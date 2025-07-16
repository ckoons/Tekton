"""
Harmonia API Server - Implements workflow orchestration APIs.

This module provides a FastAPI application that implements the Harmonia
API following the Single Port Architecture, including:
- HTTP REST endpoints for workflow management (/api/*)
- WebSocket endpoint for real-time events (/ws/*)
- Event streaming endpoint for workflow events (/events/*)
"""

import os
import sys
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Set, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter, Depends, HTTPException, WebSocket, BackgroundTasks, Query, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field
from tekton.models import TektonBaseModel

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown

# Import shared API utilities
from shared.api.documentation import get_openapi_configuration
from shared.api.endpoints import create_ready_endpoint, create_discovery_endpoint, EndpointInfo
from shared.api.routers import create_standard_routers, mount_standard_routers

from harmonia.core.engine import WorkflowEngine
from harmonia.core.state import StateManager
from harmonia.core.component import ComponentRegistry
from harmonia.core.workflow_startup import WorkflowEngineStartup
from harmonia.core.startup_instructions import StartUpInstructions
from harmonia.models.workflow import (
    TaskStatus,
    WorkflowStatus,
    RetryPolicy,
    TaskDefinition,
    WorkflowDefinition,
    TaskExecution,
    WorkflowExecution,
)
from harmonia.models.execution import (
    EventType, 
    ExecutionEvent,
    ExecutionMetrics, 
    Checkpoint,
    ExecutionHistory,
    ExecutionSummary
)
from harmonia.models.template import (
    Template,
    TemplateVersion,
    TemplateInstantiation,
    ParameterDefinition
)
from harmonia.models.webhook import (
    WebhookDefinition,
    WebhookEvent
)
from tekton.utils.tekton_errors import TektonNotFoundError as NotFoundError, DataValidationError as ValidationError, AuthorizationError

# Import FastMCP endpoints - will be used in lifespan
from .fastmcp_endpoints import fastmcp_router, fastmcp_startup, fastmcp_shutdown, set_workflow_engine

# Import Harmonia component
from harmonia.core.harmonia_component import HarmoniaComponent

# Create component singleton
harmonia_component = HarmoniaComponent()

# Configure logger
logger = setup_component_logging("harmonia")

async def startup_callback():
    """Initialize Harmonia component (includes Hermes registration)."""
    # Initialize component (includes Hermes registration and workflow engine setup)
    await harmonia_component.initialize(
        capabilities=harmonia_component.get_capabilities(),
        metadata=harmonia_component.get_metadata()
    )
    
    # Get the workflow engine from component
    workflow_engine = harmonia_component.workflow_engine
    
    # Component-specific initialization AFTER component init
    
    # Register event handlers for WebSocket broadcasting
    workflow_engine.register_event_handler(
        EventType.WORKFLOW_STARTED,
        lambda event: asyncio.create_task(
            connection_manager.broadcast_event(event.execution_id, event)
        )
    )
    
    workflow_engine.register_event_handler(
        EventType.WORKFLOW_COMPLETED,
        lambda event: asyncio.create_task(
            connection_manager.broadcast_event(event.execution_id, event)
        )
    )
    
    workflow_engine.register_event_handler(
        EventType.WORKFLOW_FAILED,
        lambda event: asyncio.create_task(
            connection_manager.broadcast_event(event.execution_id, event)
        )
    )
    
    workflow_engine.register_event_handler(
        EventType.TASK_STARTED,
        lambda event: asyncio.create_task(
            connection_manager.broadcast_event(event.execution_id, event)
        )
    )
    
    workflow_engine.register_event_handler(
        EventType.TASK_COMPLETED,
        lambda event: asyncio.create_task(
            connection_manager.broadcast_event(event.execution_id, event)
        )
    )
    
    workflow_engine.register_event_handler(
        EventType.TASK_FAILED,
        lambda event: asyncio.create_task(
            connection_manager.broadcast_event(event.execution_id, event)
        )
    )
    
    # Register event handler for SSE
    for event_type in EventType:
        workflow_engine.register_event_handler(
            event_type,
            lambda event: asyncio.create_task(
                event_manager.add_event(event.execution_id, event)
            )
        )
    
    logger.info("Event handlers registered successfully")
    
    # Set workflow engine for FastMCP and initialize
    set_workflow_engine(workflow_engine)
    await fastmcp_startup()
    
    # Initialize Hermes MCP Bridge
    try:
        from harmonia.core.mcp.hermes_bridge import HarmoniaMCPBridge
        harmonia_component.mcp_bridge = HarmoniaMCPBridge(workflow_engine)
        await harmonia_component.mcp_bridge.initialize()
        logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
    except Exception as e:
        logger.warning(f"Failed to initialize MCP Bridge: {e}")
    
    # Store connection managers in component for cleanup
    harmonia_component.connection_manager = connection_manager
    harmonia_component.event_manager = event_manager

# Create FastAPI app using component
app = harmonia_component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name="harmonia",
        component_version="0.1.0",
        component_description="Workflow orchestration and state management service for Tekton ecosystem"
    )
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers("harmonia")

# Create specialized routers for WebSocket and SSE
websocket_router = APIRouter(prefix="/ws")
events_router = APIRouter(prefix="/events")

# Connection manager for WebSockets
class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[UUID, WebSocket] = {}
        self.subscriptions: Dict[UUID, Set[UUID]] = {}  # Client ID -> Set of workflow execution IDs
    
    async def connect(self, websocket: WebSocket) -> UUID:
        """
        Accept a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            Client ID
        """
        await websocket.accept()
        client_id = uuid4()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")
        return client_id
    
    def disconnect(self, client_id: UUID):
        """
        Remove a WebSocket connection.
        
        Args:
            client_id: Client ID
        """
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)
        logger.info(f"Client {client_id} disconnected")
    
    def subscribe(self, client_id: UUID, execution_id: UUID):
        """
        Subscribe a client to workflow execution events.
        
        Args:
            client_id: Client ID
            execution_id: Workflow execution ID
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].add(execution_id)
            logger.info(f"Client {client_id} subscribed to execution {execution_id}")
    
    def unsubscribe(self, client_id: UUID, execution_id: UUID):
        """
        Unsubscribe a client from workflow execution events.
        
        Args:
            client_id: Client ID
            execution_id: Workflow execution ID
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(execution_id)
            logger.info(f"Client {client_id} unsubscribed from execution {execution_id}")
    
    async def broadcast_event(self, execution_id: UUID, event: ExecutionEvent):
        """
        Broadcast an event to all subscribed clients.
        
        Args:
            execution_id: Workflow execution ID
            event: Execution event
        """
        # Find all clients subscribed to this execution
        subscribers = [
            client_id for client_id, subscriptions in self.subscriptions.items()
            if execution_id in subscriptions
        ]
        
        if not subscribers:
            return
        
        # Prepare the message
        message = {
            "event_type": event.event_type.value,
            "execution_id": str(execution_id),
            "task_id": event.task_id,
            "details": event.details,
            "message": event.message,
            "timestamp": event.timestamp.isoformat()
        }
        
        # Send to all subscribers
        for client_id in subscribers:
            websocket = self.active_connections.get(client_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending event to client {client_id}: {e}")
                    self.disconnect(client_id)

# Event manager for SSE
class EventManager:
    """Manages event streams for Server-Sent Events."""
    
    def __init__(self):
        """Initialize the event manager."""
        self.event_queues: Dict[UUID, asyncio.Queue] = {}
    
    def create_queue(self, execution_id: UUID) -> asyncio.Queue:
        """
        Create an event queue for a workflow execution.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Event queue
        """
        queue = asyncio.Queue()
        self.event_queues[execution_id] = queue
        return queue
    
    def get_queue(self, execution_id: UUID) -> Optional[asyncio.Queue]:
        """
        Get the event queue for a workflow execution.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Event queue if it exists
        """
        return self.event_queues.get(execution_id)
    
    def remove_queue(self, execution_id: UUID):
        """
        Remove the event queue for a workflow execution.
        
        Args:
            execution_id: Workflow execution ID
        """
        self.event_queues.pop(execution_id, None)
    
    async def add_event(self, execution_id: UUID, event: ExecutionEvent):
        """
        Add an event to the queue.
        
        Args:
            execution_id: Workflow execution ID
            event: Execution event
        """
        queue = self.get_queue(execution_id)
        if queue:
            # Format event as SSE
            event_data = {
                "event_type": event.event_type.value,
                "execution_id": str(execution_id),
                "task_id": event.task_id,
                "details": event.details,
                "message": event.message,
                "timestamp": event.timestamp.isoformat()
            }
            
            await queue.put(f"event: {event.event_type.value}\ndata: {json.dumps(event_data)}\n\n")

# Create managers
connection_manager = ConnectionManager()
event_manager = EventManager()


# Dependency to get the workflow engine
async def get_workflow_engine() -> WorkflowEngine:
    """
    Get the workflow engine.
    
    Raises:
        HTTPException: If the engine is not initialized
    """
    if harmonia_component.workflow_engine is None:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")
    return harmonia_component.workflow_engine


# --- API Request/Response Models ---

class WorkflowDefinitionCreate(TektonBaseModel):
    """Request model for creating a workflow definition."""
    name: str
    description: str = ""
    tasks: Dict[str, TaskDefinition]
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionCreate(TektonBaseModel):
    """Request model for creating a workflow execution."""
    workflow_id: UUID
    input: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateCreate(TektonBaseModel):
    """Request model for creating a template."""
    name: str
    description: str = ""
    workflow_definition_id: UUID
    parameters: Dict[str, ParameterDefinition] = Field(default_factory=dict)
    category_ids: List[UUID] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    is_public: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateInstantiateRequest(TektonBaseModel):
    """Request model for instantiating a template."""
    template_id: UUID
    parameter_values: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WebhookDefinitionCreate(TektonBaseModel):
    """Request model for creating a webhook definition."""
    name: str
    description: str = ""
    trigger_type: str
    url: str
    auth_type: Optional[str] = None
    auth_config: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    payload_template: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIResponse(TektonBaseModel):
    """Standard API response model."""
    status: str
    message: str
    data: Optional[Any] = None


# Add infrastructure endpoints
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name="harmonia",
        component_version="0.1.0",
        start_time=harmonia_component.global_config._start_time,
        readiness_check=lambda: harmonia_component.workflow_engine is not None
    )
    return await ready_check()


@routers.root.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    discovery_check = create_discovery_endpoint(
        component_name="harmonia",
        component_version="0.1.0",
        component_description="Workflow orchestration and state management service for Tekton ecosystem",
        endpoints=[
            EndpointInfo(path="/health", method="GET", description="Health check"),
            EndpointInfo(path="/ready", method="GET", description="Readiness check"),
            EndpointInfo(path="/discovery", method="GET", description="Service discovery"),
            EndpointInfo(path="/api/v1/workflows", method="GET", description="List workflows"),
            EndpointInfo(path="/api/v1/workflows", method="POST", description="Create workflow"),
            EndpointInfo(path="/api/v1/executions", method="GET", description="List executions"),
            EndpointInfo(path="/api/v1/executions", method="POST", description="Create execution"),
            EndpointInfo(path="/api/v1/templates", method="GET", description="List templates"),
            EndpointInfo(path="/api/v1/components", method="GET", description="List components"),
            EndpointInfo(path="/ws/executions/{id}", method="WS", description="Execution WebSocket"),
            EndpointInfo(path="/events/executions/{id}", method="GET", description="Execution events (SSE)")
        ],
        capabilities=[
            "workflow_orchestration",
            "state_management",
            "event_streaming",
            "component_coordination"
        ],
        metadata={
            "category": "workflow",
            "event_types": [e.value for e in EventType]
        }
    )
    return await discovery_check()


# --- HTTP API Endpoints ---

# Workflow Definition Endpoints

@routers.v1.post("/workflows", response_model=APIResponse, status_code=201)
async def create_workflow(
    definition: WorkflowDefinitionCreate,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create a new workflow definition.
    
    Args:
        definition: Workflow definition to create
        engine: Workflow engine
        
    Returns:
        Created workflow definition
    """
    try:
        # Convert to WorkflowDefinition
        workflow_def = WorkflowDefinition(
            name=definition.name,
            description=definition.description,
            tasks=definition.tasks,
            input=definition.input,
            output=definition.output,
            version=definition.version,
            metadata=definition.metadata
        )
        
        # Save to state manager
        await engine.state_manager.save_workflow_definition(workflow_def)
        
        return APIResponse(
            status="success",
            message=f"Workflow definition '{workflow_def.name}' created",
            data=workflow_def.dict()
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creating workflow definition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/workflows", response_model=APIResponse)
async def list_workflows(
    engine: WorkflowEngine = Depends(get_workflow_engine),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    List workflow definitions.
    
    Args:
        engine: Workflow engine
        limit: Maximum number of results
        offset: Result offset
        
    Returns:
        List of workflow definitions
    """
    try:
        # Get workflow definitions from state manager
        workflows = await engine.state_manager.list_workflow_definitions(limit, offset)
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(workflows)} workflow definitions",
            data=[w.dict() for w in workflows]
        )
    
    except Exception as e:
        logger.error(f"Error listing workflow definitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/workflows/{workflow_id}", response_model=APIResponse)
async def get_workflow(
    workflow_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get a workflow definition by ID.
    
    Args:
        workflow_id: Workflow definition ID
        engine: Workflow engine
        
    Returns:
        Workflow definition
    """
    try:
        # Get workflow definition from state manager
        workflow = await engine.state_manager.load_workflow_definition(workflow_id)
        
        if not workflow:
            raise NotFoundError(f"Workflow definition {workflow_id} not found")
        
        return APIResponse(
            status="success",
            message=f"Retrieved workflow definition '{workflow.name}'",
            data=workflow.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting workflow definition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.put("/workflows/{workflow_id}", response_model=APIResponse)
async def update_workflow(
    workflow_id: UUID,
    definition: WorkflowDefinitionCreate,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Update a workflow definition.
    
    Args:
        workflow_id: Workflow definition ID
        definition: Updated workflow definition
        engine: Workflow engine
        
    Returns:
        Updated workflow definition
    """
    try:
        # Check if workflow exists
        existing = await engine.state_manager.load_workflow_definition(workflow_id)
        
        if not existing:
            raise NotFoundError(f"Workflow definition {workflow_id} not found")
        
        # Update workflow definition
        workflow_def = WorkflowDefinition(
            id=workflow_id,
            name=definition.name,
            description=definition.description,
            tasks=definition.tasks,
            input=definition.input,
            output=definition.output,
            version=definition.version,
            metadata=definition.metadata
        )
        
        # Save to state manager
        await engine.state_manager.save_workflow_definition(workflow_def)
        
        return APIResponse(
            status="success",
            message=f"Updated workflow definition '{workflow_def.name}'",
            data=workflow_def.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error updating workflow definition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.delete("/workflows/{workflow_id}", response_model=APIResponse)
async def delete_workflow(
    workflow_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Delete a workflow definition.
    
    Args:
        workflow_id: Workflow definition ID
        engine: Workflow engine
        
    Returns:
        Deletion confirmation
    """
    try:
        # Check if workflow exists
        existing = await engine.state_manager.load_workflow_definition(workflow_id)
        
        if not existing:
            raise NotFoundError(f"Workflow definition {workflow_id} not found")
        
        # Delete workflow definition
        await engine.state_manager.delete_workflow_definition(workflow_id)
        
        return APIResponse(
            status="success",
            message=f"Deleted workflow definition '{existing.name}'",
            data=None
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error deleting workflow definition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow Execution Endpoints

@routers.v1.post("/executions", response_model=APIResponse, status_code=201)
async def create_execution(
    execution: WorkflowExecutionCreate,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create a new workflow execution.
    
    Args:
        execution: Workflow execution to create
        engine: Workflow engine
        
    Returns:
        Created workflow execution
    """
    try:
        # Get workflow definition
        workflow_def = await engine.state_manager.load_workflow_definition(execution.workflow_id)
        
        if not workflow_def:
            raise NotFoundError(f"Workflow definition {execution.workflow_id} not found")
        
        # Execute workflow
        workflow_execution = await engine.execute_workflow(
            workflow_def=workflow_def,
            input_data=execution.input,
            metadata=execution.metadata
        )
        
        return APIResponse(
            status="success",
            message=f"Started workflow execution for '{workflow_def.name}'",
            data=workflow_execution.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creating workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/executions", response_model=APIResponse)
async def list_executions(
    engine: WorkflowEngine = Depends(get_workflow_engine),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None)
):
    """
    List workflow executions.
    
    Args:
        engine: Workflow engine
        limit: Maximum number of results
        offset: Result offset
        status: Filter by execution status
        
    Returns:
        List of workflow executions
    """
    try:
        # Get workflow executions from state manager
        workflow_status = WorkflowStatus(status) if status else None
        executions = await engine.state_manager.list_workflow_executions(limit, offset, workflow_status)
        
        # Get execution summaries
        summaries = []
        for execution in executions:
            summary = await engine.get_workflow_status(execution.id)
            if summary:
                summaries.append(summary)
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(summaries)} workflow executions",
            data=[s.dict() for s in summaries]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status value: {e}")
    
    except Exception as e:
        logger.error(f"Error listing workflow executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/executions/{execution_id}", response_model=APIResponse)
async def get_execution(
    execution_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get a workflow execution by ID.
    
    Args:
        execution_id: Workflow execution ID
        engine: Workflow engine
        
    Returns:
        Workflow execution
    """
    try:
        # Get workflow execution from state manager
        execution = await engine.state_manager.load_workflow_execution(execution_id)
        
        if not execution:
            raise NotFoundError(f"Workflow execution {execution_id} not found")
        
        # Get workflow definition
        workflow_def = await engine.state_manager.load_workflow_definition(execution.workflow_id)
        
        # Get execution summary
        summary = await engine.get_workflow_status(execution_id)
        
        return APIResponse(
            status="success",
            message=f"Retrieved workflow execution {execution_id}",
            data={
                "execution": execution.dict(),
                "workflow_definition": workflow_def.dict() if workflow_def else None,
                "summary": summary.dict() if summary else None
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/executions/{execution_id}/cancel", response_model=APIResponse)
async def cancel_execution(
    execution_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Cancel a workflow execution.
    
    Args:
        execution_id: Workflow execution ID
        engine: Workflow engine
        
    Returns:
        Cancellation confirmation
    """
    try:
        # Cancel workflow execution
        cancelled = await engine.cancel_workflow(execution_id)
        
        if not cancelled:
            raise NotFoundError(f"Workflow execution {execution_id} not found or not running")
        
        return APIResponse(
            status="success",
            message=f"Cancelled workflow execution {execution_id}",
            data=None
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error cancelling workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/executions/{execution_id}/pause", response_model=APIResponse)
async def pause_execution(
    execution_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Pause a workflow execution.
    
    Args:
        execution_id: Workflow execution ID
        engine: Workflow engine
        
    Returns:
        Pause confirmation
    """
    try:
        # Pause workflow execution
        paused = await engine.pause_workflow(execution_id)
        
        if not paused:
            raise NotFoundError(f"Workflow execution {execution_id} not found or not running")
        
        return APIResponse(
            status="success",
            message=f"Paused workflow execution {execution_id}",
            data=None
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error pausing workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/executions/{execution_id}/resume", response_model=APIResponse)
async def resume_execution(
    execution_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Resume a paused workflow execution.
    
    Args:
        execution_id: Workflow execution ID
        engine: Workflow engine
        
    Returns:
        Resume confirmation
    """
    try:
        # Resume workflow execution
        resumed = await engine.resume_workflow(execution_id)
        
        if not resumed:
            raise NotFoundError(f"Workflow execution {execution_id} not found or not paused")
        
        return APIResponse(
            status="success",
            message=f"Resumed workflow execution {execution_id}",
            data=None
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error resuming workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/executions/{execution_id}/checkpoint", response_model=APIResponse)
async def create_execution_checkpoint(
    execution_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create a checkpoint for a workflow execution.
    
    Args:
        execution_id: Workflow execution ID
        engine: Workflow engine
        
    Returns:
        Created checkpoint
    """
    try:
        # Create checkpoint
        checkpoint = await engine.create_checkpoint(execution_id)
        
        if not checkpoint:
            raise NotFoundError(f"Workflow execution {execution_id} not found")
        
        return APIResponse(
            status="success",
            message=f"Created checkpoint for workflow execution {execution_id}",
            data=checkpoint.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creating checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/checkpoints/{checkpoint_id}/restore", response_model=APIResponse)
async def restore_from_checkpoint(
    checkpoint_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Restore a workflow execution from a checkpoint.
    
    Args:
        checkpoint_id: Checkpoint ID
        engine: Workflow engine
        
    Returns:
        New execution ID
    """
    try:
        # Restore from checkpoint
        new_execution_id = await engine.restore_from_checkpoint(checkpoint_id)
        
        if not new_execution_id:
            raise NotFoundError(f"Checkpoint {checkpoint_id} not found")
        
        return APIResponse(
            status="success",
            message=f"Restored workflow execution from checkpoint {checkpoint_id}",
            data={"execution_id": str(new_execution_id)}
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error restoring from checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Template Endpoints

@routers.v1.post("/templates", response_model=APIResponse, status_code=201)
async def create_template(
    template: TemplateCreate,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create a new template.
    
    Args:
        template: Template to create
        engine: Workflow engine
        
    Returns:
        Created template
    """
    try:
        # Get workflow definition
        workflow_def = await engine.state_manager.load_workflow_definition(template.workflow_definition_id)
        
        if not workflow_def:
            raise NotFoundError(f"Workflow definition {template.workflow_definition_id} not found")
        
        # Create template
        template_manager = engine.template_manager
        if not template_manager:
            raise HTTPException(status_code=503, detail="Template manager not initialized")
        
        created_template = template_manager.create_template(
            name=template.name,
            description=template.description,
            workflow_definition=workflow_def,
            parameters=template.parameters,
            category_ids=template.category_ids,
            tags=template.tags,
            is_public=template.is_public,
            metadata=template.metadata
        )
        
        return APIResponse(
            status="success",
            message=f"Created template '{template.name}'",
            data=created_template.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/templates", response_model=APIResponse)
async def list_templates(
    engine: WorkflowEngine = Depends(get_workflow_engine),
    category_id: Optional[UUID] = Query(None),
    tags: List[str] = Query([])
):
    """
    List templates.
    
    Args:
        engine: Workflow engine
        category_id: Filter by category ID
        tags: Filter by tags
        
    Returns:
        List of templates
    """
    try:
        # Get templates from template manager
        template_manager = engine.template_manager
        if not template_manager:
            raise HTTPException(status_code=503, detail="Template manager not initialized")
        
        templates = template_manager.get_templates(category_id, tags)
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(templates)} templates",
            data=[t.dict() for t in templates]
        )
    
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/templates/{template_id}", response_model=APIResponse)
async def get_template(
    template_id: UUID,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get a template by ID.
    
    Args:
        template_id: Template ID
        engine: Workflow engine
        
    Returns:
        Template
    """
    try:
        # Get template from template manager
        template_manager = engine.template_manager
        if not template_manager:
            raise HTTPException(status_code=503, detail="Template manager not initialized")
        
        template = template_manager.get_template(template_id)
        
        if not template:
            raise NotFoundError(f"Template {template_id} not found")
        
        return APIResponse(
            status="success",
            message=f"Retrieved template '{template.name}'",
            data=template.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/templates/{template_id}/instantiate", response_model=APIResponse)
async def instantiate_template(
    template_id: UUID,
    instantiation: TemplateInstantiateRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Instantiate a template.
    
    Args:
        template_id: Template ID
        instantiation: Template instantiation request
        engine: Workflow engine
        
    Returns:
        Template instantiation and created workflow definition
    """
    try:
        # Get template manager
        template_manager = engine.template_manager
        if not template_manager:
            raise HTTPException(status_code=503, detail="Template manager not initialized")
        
        # Instantiate template
        instantiation_result = await template_manager.instantiate_template(
            template_id=template_id,
            parameter_values=instantiation.parameter_values
        )
        
        if not instantiation_result:
            raise NotFoundError(f"Template {template_id} not found")
        
        template_instantiation, workflow_def = instantiation_result
        
        return APIResponse(
            status="success",
            message=f"Instantiated template {template_id}",
            data={
                "instantiation": template_instantiation.dict(),
                "workflow_definition": workflow_def.dict()
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error instantiating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Webhook Endpoints

@routers.v1.post("/webhooks", response_model=APIResponse, status_code=201)
async def create_webhook(
    webhook: WebhookDefinitionCreate,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Create a new webhook definition.
    
    Args:
        webhook: Webhook definition to create
        engine: Workflow engine
        
    Returns:
        Created webhook definition
    """
    try:
        # Create webhook definition
        webhook_def = WebhookDefinition(
            name=webhook.name,
            description=webhook.description,
            trigger_type=webhook.trigger_type,
            url=webhook.url,
            auth_type=webhook.auth_type,
            auth_config=webhook.auth_config,
            headers=webhook.headers,
            payload_template=webhook.payload_template,
            metadata=webhook.metadata
        )
        
        # Save to state manager
        await engine.state_manager.save_webhook_definition(webhook_def)
        
        return APIResponse(
            status="success",
            message=f"Created webhook definition '{webhook.name}'",
            data=webhook_def.dict()
        )
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creating webhook definition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/webhooks", response_model=APIResponse)
async def list_webhooks(
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    List webhook definitions.
    
    Args:
        engine: Workflow engine
        
    Returns:
        List of webhook definitions
    """
    try:
        # Get webhook definitions from state manager
        webhooks = await engine.state_manager.list_webhook_definitions()
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(webhooks)} webhook definitions",
            data=[w.dict() for w in webhooks]
        )
    
    except Exception as e:
        logger.error(f"Error listing webhook definitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/webhooks/{webhook_id}/deliver", response_model=APIResponse)
async def trigger_webhook(
    webhook_id: UUID,
    payload: Dict[str, Any],
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Manually trigger a webhook.
    
    Args:
        webhook_id: Webhook definition ID
        payload: Webhook payload
        engine: Workflow engine
        
    Returns:
        Webhook delivery result
    """
    try:
        # Get webhook definition
        webhook_def = await engine.state_manager.load_webhook_definition(webhook_id)
        
        if not webhook_def:
            raise NotFoundError(f"Webhook definition {webhook_id} not found")
        
        # Create webhook event
        webhook_event = WebhookEvent(
            webhook_id=webhook_id,
            payload=payload
        )
        
        # Deliver webhook
        delivery = await engine.webhook_manager.deliver_webhook(webhook_def, webhook_event)
        
        return APIResponse(
            status="success",
            message=f"Triggered webhook '{webhook_def.name}'",
            data=delivery.dict()
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error triggering webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Component Endpoints

@routers.v1.get("/components", response_model=APIResponse)
async def list_components(
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    List registered components.
    
    Args:
        engine: Workflow engine
        
    Returns:
        List of component names
    """
    try:
        # Get components from component registry
        components = engine.component_registry.get_components()
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(components)} components",
            data=components
        )
    
    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/components/{component_name}/actions", response_model=APIResponse)
async def list_component_actions(
    component_name: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    List available actions for a component.
    
    Args:
        component_name: Component name
        engine: Workflow engine
        
    Returns:
        List of action names
    """
    try:
        # Get component from registry
        if not engine.component_registry.has_component(component_name):
            raise NotFoundError(f"Component {component_name} not found")
        
        component = engine.component_registry.get_component(component_name)
        
        # Get actions
        actions = await component.get_actions()
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(actions)} actions for component {component_name}",
            data=actions
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error listing component actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/components/{component_name}/actions/{action}", response_model=APIResponse)
async def get_action_schema(
    component_name: str,
    action: str,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Get schema for a component action.
    
    Args:
        component_name: Component name
        action: Action name
        engine: Workflow engine
        
    Returns:
        Action schema
    """
    try:
        # Get component from registry
        if not engine.component_registry.has_component(component_name):
            raise NotFoundError(f"Component {component_name} not found")
        
        component = engine.component_registry.get_component(component_name)
        
        # Get action schema
        schema = await component.get_action_schema(action)
        
        if not schema:
            raise NotFoundError(f"Action {action} not found for component {component_name}")
        
        return APIResponse(
            status="success",
            message=f"Retrieved schema for action {action} of component {component_name}",
            data=schema
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error getting action schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/components/{component_name}/actions/{action}", response_model=APIResponse)
async def execute_component_action(
    component_name: str,
    action: str,
    params: Dict[str, Any],
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Execute an action on a component.
    
    Args:
        component_name: Component name
        action: Action name
        params: Action parameters
        engine: Workflow engine
        
    Returns:
        Action result
    """
    try:
        # Execute action using component registry
        result = await engine.component_registry.execute_action(
            component_name=component_name,
            action=action,
            params=params
        )
        
        return APIResponse(
            status="success",
            message=f"Executed action {action} on component {component_name}",
            data=result
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error executing component action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- WebSocket Endpoints ---

@websocket_router.websocket("/executions/{execution_id}")
async def execution_websocket(
    websocket: WebSocket,
    execution_id: UUID
):
    """
    WebSocket endpoint for real-time workflow execution events.
    
    Args:
        websocket: WebSocket connection
        execution_id: Workflow execution ID
    """
    client_id = None
    try:
        # Accept connection
        client_id = await connection_manager.connect(websocket)
        
        # Subscribe to execution events
        connection_manager.subscribe(client_id, execution_id)
        
        # Send initial message
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected to execution {execution_id}",
            "client_id": str(client_id),
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection open and handle client messages
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle message types
            message_type = message.get("type")
            
            if message_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "unsubscribe":
                # Unsubscribe from execution
                connection_manager.unsubscribe(client_id, execution_id)
                await websocket.send_json({
                    "type": "unsubscribed",
                    "message": f"Unsubscribed from execution {execution_id}",
                    "timestamp": datetime.now().isoformat()
                })
                break
    
    except Exception as e:
        logger.error(f"Error in execution WebSocket: {e}")
    
    finally:
        # Clean up connection
        if client_id:
            connection_manager.disconnect(client_id)


# --- Event Stream Endpoints ---

@events_router.get("/executions/{execution_id}")
async def execution_events(
    execution_id: UUID,
    request: Request,
    engine: WorkflowEngine = Depends(get_workflow_engine)
):
    """
    Server-Sent Events endpoint for workflow execution events.
    
    Args:
        execution_id: Workflow execution ID
        request: HTTP request
        engine: Workflow engine
        
    Returns:
        Event stream response
    """
    try:
        # Check if execution exists
        execution = await engine.state_manager.load_workflow_execution(execution_id)
        
        if not execution:
            raise NotFoundError(f"Workflow execution {execution_id} not found")
        
        # Create event queue
        queue = event_manager.create_queue(execution_id)
        
        # Send initial event
        await queue.put(f"event: connected\ndata: {json.dumps({'execution_id': str(execution_id)})}\n\n")
        
        # Add connection indicator to the queue
        queue.put_nowait("event: keepalive\ndata: {}\n\n")
        
        # Send current execution state
        state = {
            "execution_id": str(execution_id),
            "status": execution.status.value,
            "tasks": {
                task_id: task.status.value
                for task_id, task in execution.task_executions.items()
            }
        }
        await queue.put(f"event: state\ndata: {json.dumps(state)}\n\n")
        
        async def event_generator():
            try:
                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break
                    
                    # Get event from queue with timeout
                    try:
                        event = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield event
                    except asyncio.TimeoutError:
                        # Send keepalive event to prevent connection timeout
                        yield "event: keepalive\ndata: {}\n\n"
            
            finally:
                # Clean up queue when client disconnects
                event_manager.remove_queue(execution_id)
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error in execution events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Status Endpoint ---

@routers.v1.get("/status", response_model=APIResponse)
async def get_status():
    """
    Get the status of the Harmonia service.
    
    Returns:
        Service status information
    """
    # Check if workflow engine is initialized
    workflow_engine = harmonia_component.workflow_engine
    engine_status = "running" if workflow_engine else "not_initialized"
    
    return APIResponse(
        status="success",
        message="Harmonia service status",
        data={
            "status": engine_status,
            "version": "0.1.0",
            "uptime": "Unknown",  # Would be calculated in a real implementation
            "active_executions": len(workflow_engine.active_executions) if workflow_engine else 0,
            "components": workflow_engine.component_registry.get_components() if workflow_engine else []
        }
    )

# --- Health Check Endpoint (Standard Single Port Architecture) ---

@app.get("/health")
async def health_check():
    """
    Health check endpoint for the Harmonia service.
    Following the Tekton Single Port Architecture standard.
    
    Returns:
        Health status information
    """
    config = get_component_config()
    port = config.harmonia.port if hasattr(config, 'harmonia') else int(os.environ.get("HARMONIA_PORT"))
    
    # Check if workflow engine is initialized
    workflow_engine = harmonia_component.workflow_engine
    engine_status = "running" if workflow_engine else "not_initialized"
    
    # Check if registered with Hermes
    registered = harmonia_component.global_config.is_registered_with_hermes
    
    return {
        "status": "healthy" if engine_status == "running" else "degraded",
        "component": "harmonia",
        "version": "0.1.0",
        "port": port,
        "registered": registered,
        "message": "Harmonia is running normally" if engine_status == "running" else "Harmonia workflow engine not initialized"
    }


@app.get("/")
async def root():
    """
    Root endpoint - provides basic information about Harmonia.
    
    Returns:
        Basic service information
    """
    workflow_engine = harmonia_component.workflow_engine
    return {
        "name": "Harmonia Workflow System",
        "version": "0.1.0",
        "status": "running" if workflow_engine else "initializing",
        "endpoints": [
            "/health",
            "/api/workflows",
            "/api/templates", 
            "/api/components",
            "/ws",
            "/events"
        ],
        "message": "Harmonia workflow orchestration service"
    }


# Mount standard routers
mount_standard_routers(app, routers)

# Include specialized routers
app.include_router(websocket_router)
app.include_router(events_router)

# Mount FastMCP router under versioned API
routers.v1.include_router(fastmcp_router, prefix="/mcp/v2", tags=["MCP"])

# Add shutdown endpoint for proper port cleanup

# Store component in app state for access by endpoints
app.state.component = harmonia_component

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    config = get_component_config()
    port = config.harmonia.port if hasattr(config, 'harmonia') else int(os.environ.get("HARMONIA_PORT"))
    
    uvicorn.run(app, host="0.0.0.0", port=port)