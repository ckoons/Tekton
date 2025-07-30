#!/usr/bin/env python3
"""
Synthesis API Server

This module implements the API server for the Synthesis component,
following the Single Port Architecture pattern.
"""

import asyncio
import json
import os
import sys
import time
import uuid
from typing import Dict, List, Any, Optional, Union

import fastapi
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from tekton.models.base import TektonBaseModel

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.global_config import GlobalConfig
from shared.utils.logging_setup import setup_component_logging
from shared.utils.health_check import create_health_response
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
# Import landmarks with fallback pattern
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        danger_zone,
        state_checkpoint
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Import Tekton utilities
from tekton.utils.tekton_errors import (
    TektonError, 
    ConfigurationError,
    ConnectionError,
    AuthenticationError
)

# Import shared modules for URLs
from shared.urls import tekton_url

# Import Synthesis components
from synthesis.core.synthesis_component import SynthesisComponent
from synthesis.core.execution_models import (
    ExecutionStage, ExecutionStatus, ExecutionPriority,
    ExecutionResult, ExecutionPlan, ExecutionContext
)

# Set up logging
logger = setup_component_logging("synthesis")

# Component configuration
COMPONENT_NAME = "Synthesis"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Execution and integration engine for Tekton"

# Architecture Decision: Synthesis Component Design
@architecture_decision(
    title="Synthesis Execution Engine Architecture",
    description="Central execution coordinator for multi-component workflows in Tekton",
    rationale="Synthesis acts as the orchestrator that transforms high-level plans into coordinated actions across multiple Tekton components, ensuring proper sequencing, error handling, and state management",
    alternatives_considered=[
        "Direct component-to-component communication",
        "Message queue based orchestration",
        "Workflow engine integration (e.g., Airflow)"
    ],
    impacts=["component_integration", "execution_reliability", "state_consistency"],
    decided_by="Casey",
    decision_date="2024-12-01"
)
class _SynthesisArchitecture:
    """Marker class for architecture decision"""
    pass

# Create component instance (singleton)
component = SynthesisComponent()


# API Data Models
class APIResponse(TektonBaseModel):
    """Generic API response model."""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class ExecutionRequest(TektonBaseModel):
    """Execution request model."""
    plan: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(default=ExecutionPriority.NORMAL)
    wait_for_completion: Optional[bool] = Field(default=False)
    timeout: Optional[int] = Field(default=None)


class ExecutionResponse(TektonBaseModel):
    """Execution response model."""
    execution_id: str
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


class VariableRequest(TektonBaseModel):
    """Variable request model."""
    operation: str  # set, delete, increment, append, merge
    name: str
    value: Optional[Any] = None


# Startup callback for component initialization
@integration_point(
    title="Synthesis Component Initialization",
    description="Initializes Synthesis component and MCP bridge on startup",
    target_component="SynthesisComponent, MCP Bridge",
    protocol="Internal initialization",
    data_flow="Config → Component init → MCP bridge init → Ready state",
    integration_date="2024-12-01"
)
async def startup_callback():
    """Component startup callback."""
    global component
    try:
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        
        # Initialize MCP bridge after component startup
        await component.initialize_mcp_bridge()
        
        logger.info(f"Synthesis API server started successfully")
    except Exception as e:
        logger.error(f"Failed to start Synthesis: {e}")
        raise


# Create FastAPI application with standard configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    on_startup=[startup_callback]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Static files are served by Hephaestus, not by individual component APIs
# The UI files reside in /Hephaestus/ui/components/synthesis/

# Create standard routers
routers = create_standard_routers(COMPONENT_NAME)

# Create additional routers for Synthesis-specific needs
ws_router = APIRouter()

# Root endpoint
@routers.root.get("/")
@api_contract(
    title="Root API Endpoint",
    description="Provides basic component information and API documentation links",
    endpoint="/",
    method="GET",
    response_schema={
        "name": "string - Component display name",
        "version": "string - Component version",
        "status": "string - Component status",
        "description": "string - Component description",
        "documentation": "string - API documentation URL"
    }
)
async def root():
    """Root endpoint for the Synthesis API."""
    global_config = GlobalConfig.get_instance()
    port = global_config.config.synthesis.port
    
    return {
        "name": f"{COMPONENT_NAME} Execution Engine API",
        "version": COMPONENT_VERSION,
        "status": "running",
        "description": COMPONENT_DESCRIPTION,
        "documentation": "/api/v1/docs"
    }

# Import and include MCP router
from synthesis.api.fastmcp_endpoints import mcp_router

# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=time.time(),
        readiness_check=lambda: component is not None
    ),
    methods=["GET"]
)

# Add discovery endpoint to v1 router
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(
                path="/api/v1/executions",
                method="POST",
                description="Execute a synthesis plan"
            ),
            EndpointInfo(
                path="/api/v1/executions",
                method="GET",
                description="List all executions"
            ),
            EndpointInfo(
                path="/api/v1/executions/{execution_id}",
                method="GET",
                description="Get execution details"
            ),
            EndpointInfo(
                path="/api/v1/metrics",
                method="GET",
                description="Get execution metrics"
            ),
            EndpointInfo(
                path="/ws",
                method="WEBSOCKET",
                description="WebSocket connection for execution events"
            )
        ],
        capabilities=[
            "code_generation",
            "integration",
            "execution",
            "event_streaming",
            "metric_tracking"
        ],
        dependencies={
            "hermes": tekton_url("hermes"),
            "rhetor": tekton_url("rhetor")
        },
        metadata={
            "websocket_endpoint": "/ws",
            "documentation": "/api/v1/docs"
        }
    ),
    methods=["GET"]
)

# NOTE: mount_standard_routers must be called AFTER all endpoint definitions
# We'll move this to the end of the file

# Dependency to get the execution engine
@state_checkpoint(
    title="Execution Engine Access",
    description="Ensures execution engine is initialized before handling requests",
    state_type="singleton",
    persistence=False,
    consistency_requirements="Single instance per process",
    recovery_strategy="Fail fast if not initialized"
)
async def get_execution_engine():
    """Get the execution engine or raise an error if not initialized."""
    if not component:
        raise HTTPException(status_code=503, detail="Synthesis component not initialized")
    if not component.execution_engine:
        raise HTTPException(status_code=503, detail="Execution engine not initialized")
    return component.execution_engine


# Health check endpoint
@routers.root.get("/health")
@api_contract(
    title="Health Check Endpoint",
    description="Standard Tekton health check following platform conventions",
    endpoint="/health",
    method="GET",
    response_schema={
        "status": "string - healthy|degraded|error",
        "component": "string - Component name",
        "port": "int - Component port",
        "version": "string - Component version",
        "registered": "bool - Hermes registration status",
        "details": "object - Additional health information"
    }
)
async def health_check():
    """Check the health of the Synthesis component following Tekton standards."""
    # Get port from config
    global_config = GlobalConfig.get_instance()
    port = global_config.config.synthesis.port
    
    # Try to get component health info
    # Even if the component isn't fully initialized, we'll return a basic health response
    try:
        if component:
            # Component exists, get proper health info
            health_info = component.get_component_status()
            
            # Set status code based on health
            status_code = 200
            if health_info.get("status") == "error":
                status_code = 500
                health_status = "error"
            elif health_info.get("status") == "degraded":
                status_code = 429
                health_status = "degraded"
            else:
                health_status = "healthy"
                
            # Message from component health
            message = health_info.get("message", "Synthesis is running")
        else:
            # Component not initialized but app is responding
            status_code = 200
            health_status = "healthy"
            message = "Synthesis API is running (component not fully initialized)"
    except Exception as e:
        # Something went wrong in health check
        status_code = 200
        health_status = "healthy"
        message = f"Synthesis API is running (basic health check only)"
        logger.warning(f"Error in health check, using basic response: {e}")
    
    # Use standardized health response
    return create_health_response(
        component_name="synthesis",
        port=port,
        version=COMPONENT_VERSION,
        status=health_status,
        registered=component.global_config.is_registered_with_hermes if component else False,
        details={"message": message}
    )


# Metrics endpoint
@routers.v1.get("/metrics")
@api_contract(
    title="Execution Metrics API",
    description="Provides real-time metrics about execution engine performance and capacity",
    endpoint="/api/v1/metrics",
    method="GET",
    response_schema={
        "active_executions": "int - Currently running executions",
        "execution_capacity": "int - Maximum concurrent executions",
        "execution_load": "float - Percentage of capacity in use",
        "total_executions": "int - Historical execution count",
        "timestamp": "float - Metric collection time"
    },
    performance_requirements="<10ms response time"
)
async def metrics():
    """Get metrics from the Synthesis component."""
    if not component:
        return JSONResponse(
            content={"status": "unavailable", "message": "Synthesis component not initialized"},
            status_code=503
        )
    
    # Get execution engine
    execution_engine = await get_execution_engine()
    
    # Collect metrics
    metrics = {
        "active_executions": len(execution_engine.active_executions),
        "execution_capacity": execution_engine.max_concurrent_executions,
        "execution_load": len(execution_engine.active_executions) / execution_engine.max_concurrent_executions,
        "total_executions": len(execution_engine.execution_history),
        "timestamp": time.time()
    }
    
    return JSONResponse(
        content=metrics,
        status_code=200
    )


# WebSocket endpoints
@ws_router.websocket("/ws")
@integration_point(
    title="WebSocket Event Streaming",
    description="Real-time bidirectional communication channel for execution events",
    target_component="UI Components, Other Tekton Services",
    protocol="WebSocket",
    data_flow="Execution Events → WebSocket → Subscribers | Client Commands → WebSocket → Execution Engine",
    integration_date="2024-12-01"
)
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time execution updates.
    """
    # Get WebSocket manager
    if not component or not component.initialized or not component.ws_manager:
        await websocket.close(code=1011, reason="Synthesis component not initialized")
        return
    
    ws_manager = component.ws_manager
    
    # Accept connection
    await websocket.accept()
    
    # Register connection
    client_id = await ws_manager.connect(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "timestamp": time.time()
        })
        
        # Handle incoming messages
        while True:
            message = await websocket.receive_json()
            await ws_manager.process_message(websocket, message)
            
    except WebSocketDisconnect:
        # Handle client disconnect
        ws_manager.disconnect(client_id)
        
    except Exception as e:
        # Handle other errors
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(client_id)


# Execution endpoints
@routers.v1.post("/executions", response_model=ExecutionResponse)
@api_contract(
    title="Execution Creation API",
    description="Creates and optionally waits for completion of multi-component execution plans",
    endpoint="/api/v1/executions",
    method="POST",
    request_schema={
        "plan": "object - ExecutionPlan with stages and actions",
        "context": "object - ExecutionContext with variables and metadata",
        "priority": "int - ExecutionPriority enum value",
        "wait_for_completion": "bool - Block until execution completes",
        "timeout": "int - Maximum seconds to wait if blocking"
    },
    response_schema={
        "execution_id": "string - Unique execution identifier",
        "status": "string - Current execution status",
        "message": "string - Human-readable status message",
        "data": "object - Execution details and results"
    },
    performance_requirements="<100ms to queue execution, <10s for typical completion"
)
@integration_point(
    title="Cross-Component Execution Orchestration",
    description="Coordinates execution across multiple Tekton components based on execution plans",
    target_component="All Tekton Components via Hermes",
    protocol="HTTP/REST API calls, WebSocket event streams",
    data_flow="Execution Plan → Synthesis Engine → Component API calls → Result aggregation → Event notifications",
    integration_date="2024-12-01"
)
@danger_zone(
    title="Multi-Component Code Execution",
    description="Executes arbitrary plans across multiple components with potential side effects",
    risk_level="high",
    risks=[
        "Arbitrary code execution across components",
        "Resource exhaustion from parallel executions",
        "Cascading component failures",
        "Data inconsistency from partial execution",
        "Deadlocks from circular dependencies"
    ],
    mitigations=[
        "Execution sandboxing per component",
        "Resource limits and quotas",
        "Timeout controls at stage and plan level",
        "Transactional rollback capability",
        "Dependency cycle detection",
        "Circuit breakers for failing components"
    ],
    review_required=True
)
@state_checkpoint(
    title="Execution State Management",
    description="Tracks execution progress, results, and recovery information",
    state_type="execution_context",
    persistence=True,
    consistency_requirements="Atomic updates, crash recovery, result durability",
    recovery_strategy="Resume from last completed stage on restart"
)
async def create_execution(request: ExecutionRequest, execution_engine = Depends(get_execution_engine)):
    """
    Create a new execution.
    """
    try:
        # Create execution plan
        plan = ExecutionPlan.from_dict(request.plan) if isinstance(request.plan, dict) else request.plan
        
        # Create execution context if provided
        context = None
        if request.context:
            context = ExecutionContext.from_dict(request.context)
        
        # Execute plan
        execution_id = await execution_engine.execute_plan(plan, context)
        
        # Get initial status
        status = await execution_engine.get_execution_status(execution_id)
        
        # Wait for completion if requested
        if request.wait_for_completion:
            timeout = request.timeout or 600  # Default: 10 minutes
            start_time = time.time()
            
            while status["status"] in (ExecutionStatus.PENDING, ExecutionStatus.IN_PROGRESS):
                # Check timeout
                if time.time() - start_time > timeout:
                    return ExecutionResponse(
                        execution_id=execution_id,
                        status="timeout",
                        message=f"Execution timed out after {timeout} seconds",
                        data=status
                    )
                
                # Wait a bit
                await asyncio.sleep(0.5)
                
                # Update status
                status = await execution_engine.get_execution_status(execution_id)
        
        return ExecutionResponse(
            execution_id=execution_id,
            status=status["status"],
            message=f"Execution {'completed' if status['status'] == ExecutionStatus.COMPLETED else 'started'}",
            data=status
        )
        
    except Exception as e:
        logger.error(f"Error creating execution: {e}")
        return ExecutionResponse(
            execution_id=str(uuid.uuid4()),
            status="error",
            message="Error creating execution",
            errors=[str(e)]
        )


@routers.v1.get("/executions/{execution_id}", response_model=ExecutionResponse)
@api_contract(
    title="Execution Status Retrieval",
    description="Retrieves current status and details of a specific execution",
    endpoint="/api/v1/executions/{execution_id}",
    method="GET",
    request_schema={"execution_id": "string - UUID of execution"},
    response_schema={
        "execution_id": "string",
        "status": "string - pending|in_progress|completed|failed|cancelled",
        "data": "object - Full execution details including stages and results"
    }
)
async def get_execution(execution_id: str, execution_engine = Depends(get_execution_engine)):
    """
    Get execution details by ID.
    """
    try:
        # Get execution status
        status = await execution_engine.get_execution_status(execution_id)
        
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        
        return ExecutionResponse(
            execution_id=execution_id,
            status=status["status"],
            data=status
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {e}")
        return ExecutionResponse(
            execution_id=execution_id,
            status="error",
            message=f"Error getting execution {execution_id}",
            errors=[str(e)]
        )


@routers.v1.get("/executions", response_model=APIResponse)
@api_contract(
    title="Execution List API",
    description="Lists active and historical executions with optional filtering",
    endpoint="/api/v1/executions",
    method="GET",
    request_schema={
        "status": "string (optional) - Filter by execution status",
        "limit": "int - Maximum results to return (default: 100)"
    },
    response_schema={
        "executions": "array - List of execution summaries",
        "count": "int - Number of executions returned"
    }
)
async def list_executions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Maximum number of executions to return"),
    execution_engine = Depends(get_execution_engine)
):
    """
    List executions.
    """
    try:
        # Get active executions
        active_executions = execution_engine.active_executions
        
        # Get execution history
        history = execution_engine.execution_history
        
        # Combine and filter results
        all_executions = []
        
        # Add active executions
        for execution_id, execution in active_executions.items():
            if status is None or execution["status"] == status:
                all_executions.append(execution)
        
        # Add historical executions (if not already included in active)
        for execution_id, execution in history.items():
            if execution_id not in active_executions and (status is None or execution.get("status") == status):
                all_executions.append({
                    "context_id": execution_id,
                    "plan_id": execution.get("plan_id"),
                    "status": execution.get("status"),
                    "start_time": execution.get("start_time"),
                    "end_time": execution.get("end_time")
                })
        
        # Sort by start time (descending)
        all_executions.sort(key=lambda x: x.get("start_time", 0), reverse=True)
        
        # Limit results
        all_executions = all_executions[:limit]
        
        return APIResponse(
            status="success",
            data={
                "executions": all_executions,
                "count": len(all_executions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        return APIResponse(
            status="error",
            message="Error listing executions",
            errors=[str(e)]
        )


@routers.v1.post("/executions/{execution_id}/cancel", response_model=APIResponse)
@api_contract(
    title="Execution Cancellation",
    description="Cancels an in-progress execution and triggers cleanup",
    endpoint="/api/v1/executions/{execution_id}/cancel",
    method="POST",
    request_schema={"execution_id": "string - UUID of execution to cancel"},
    response_schema={
        "status": "string - success|error",
        "message": "string - Cancellation result"
    }
)
@danger_zone(
    title="Execution Cancellation",
    description="Forcefully stops execution which may leave components in inconsistent state",
    risk_level="medium",
    risks=[
        "Partial execution state",
        "Resource leaks",
        "Inconsistent component state"
    ],
    mitigations=[
        "Graceful shutdown signals",
        "Cleanup handlers per component",
        "State rollback where possible"
    ],
    review_required=False
)
async def cancel_execution(execution_id: str, execution_engine = Depends(get_execution_engine)):
    """
    Cancel an execution.
    """
    try:
        # Cancel execution
        success = await execution_engine.cancel_execution(execution_id)
        
        if not success:
            return APIResponse(
                status="error",
                message=f"Failed to cancel execution {execution_id}",
                errors=[f"Execution {execution_id} not found or already completed"]
            )
        
        return APIResponse(
            status="success",
            message=f"Execution {execution_id} cancelled successfully"
        )
        
    except Exception as e:
        logger.error(f"Error cancelling execution {execution_id}: {e}")
        return APIResponse(
            status="error",
            message=f"Error cancelling execution {execution_id}",
            errors=[str(e)]
        )


@routers.v1.get("/executions/{execution_id}/results", response_model=APIResponse)
@api_contract(
    title="Execution Results Retrieval",
    description="Retrieves detailed results from completed executions",
    endpoint="/api/v1/executions/{execution_id}/results",
    method="GET",
    request_schema={"execution_id": "string - UUID of completed execution"},
    response_schema={
        "execution_id": "string",
        "status": "string - Execution final status",
        "results": "array - Results from each execution stage"
    }
)
async def get_execution_results(execution_id: str, execution_engine = Depends(get_execution_engine)):
    """
    Get execution results.
    """
    try:
        # Get execution status
        status = await execution_engine.get_execution_status(execution_id)
        
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        
        # Get results from history
        if execution_id in execution_engine.execution_history:
            execution = execution_engine.execution_history[execution_id]
            results = execution.get("results", [])
            
            return APIResponse(
                status="success",
                data={
                    "execution_id": execution_id,
                    "status": status["status"],
                    "results": results
                }
            )
        else:
            return APIResponse(
                status="error",
                message=f"Results not found for execution {execution_id}",
                errors=[f"Results not found for execution {execution_id}"]
            )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error getting execution results {execution_id}: {e}")
        return APIResponse(
            status="error",
            message=f"Error getting execution results {execution_id}",
            errors=[str(e)]
        )


@routers.v1.post("/executions/{execution_id}/variables", response_model=APIResponse)
@api_contract(
    title="Execution Variable Management",
    description="Updates variables in active execution contexts for dynamic workflow control",
    endpoint="/api/v1/executions/{execution_id}/variables",
    method="POST",
    request_schema={
        "operation": "string - set|delete|increment|append|merge",
        "name": "string - Variable name",
        "value": "any - New value (operation dependent)"
    },
    response_schema={
        "name": "string - Variable name",
        "value": "any - Current value after operation",
        "operation": "string - Operation performed"
    }
)
@state_checkpoint(
    title="Execution Variable State",
    description="Manages mutable state within execution contexts",
    state_type="variables",
    persistence=False,
    consistency_requirements="Thread-safe updates within active execution",
    recovery_strategy="Variables lost on execution completion"
)
async def update_execution_variables(
    execution_id: str,
    request: VariableRequest,
    execution_engine = Depends(get_execution_engine)
):
    """
    Update execution variables.
    """
    try:
        # Get execution status
        status = await execution_engine.get_execution_status(execution_id)
        
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        
        # Get execution context
        if execution_id in execution_engine.active_executions:
            # Get from active executions
            for current_context in execution_engine.active_contexts:
                if current_context.context_id == execution_id:
                    context = current_context
                    break
            else:
                raise HTTPException(status_code=404, detail=f"Context not found for active execution {execution_id}")
        else:
            # Cannot update variables for completed executions
            raise HTTPException(status_code=400, detail=f"Cannot update variables for inactive execution {execution_id}")
        
        # Update variable based on operation
        if request.operation == "set":
            context.variables[request.name] = request.value
            message = f"Variable {request.name} set to {request.value}"
            
        elif request.operation == "delete":
            if request.name in context.variables:
                del context.variables[request.name]
                message = f"Variable {request.name} deleted"
            else:
                message = f"Variable {request.name} not found"
                
        elif request.operation == "increment":
            if request.name not in context.variables:
                context.variables[request.name] = 0
                
            if not isinstance(context.variables[request.name], (int, float)):
                raise HTTPException(status_code=400, detail=f"Variable {request.name} is not a number")
                
            increment = request.value if request.value is not None else 1
            context.variables[request.name] += increment
            message = f"Variable {request.name} incremented to {context.variables[request.name]}"
            
        elif request.operation == "append":
            if request.name not in context.variables:
                context.variables[request.name] = []
                
            if not isinstance(context.variables[request.name], list):
                context.variables[request.name] = [context.variables[request.name]]
                
            context.variables[request.name].append(request.value)
            message = f"Value appended to variable {request.name}"
            
        elif request.operation == "merge":
            if request.name not in context.variables:
                context.variables[request.name] = {}
                
            if not isinstance(context.variables[request.name], dict):
                raise HTTPException(status_code=400, detail=f"Variable {request.name} is not a dictionary")
                
            if not isinstance(request.value, dict):
                raise HTTPException(status_code=400, detail=f"Value must be a dictionary for merge operation")
                
            context.variables[request.name].update(request.value)
            message = f"Dictionary merged into variable {request.name}"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {request.operation}")
        
        return APIResponse(
            status="success",
            message=message,
            data={
                "name": request.name,
                "value": context.variables.get(request.name),
                "operation": request.operation
            }
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Error updating execution variables for {execution_id}: {e}")
        return APIResponse(
            status="error",
            message=f"Error updating execution variables for {execution_id}",
            errors=[str(e)]
        )


# Function registry endpoints
@routers.v1.post("/functions/{function_name}", response_model=APIResponse)
@api_contract(
    title="Function Registration (Disabled)",
    description="Would allow dynamic function registration - disabled for security",
    endpoint="/api/v1/functions/{function_name}",
    method="POST",
    request_schema={"function_name": "string", "function_code": "string"},
    response_schema={"status": "string - Always returns 501 Not Implemented"}
)
@danger_zone(
    title="Dynamic Code Registration",
    description="Disabled endpoint that would allow arbitrary code injection",
    risk_level="critical",
    risks=["Remote code execution", "System compromise", "Data exfiltration"],
    mitigations=["Endpoint disabled in production", "Would require code signing"],
    review_required=True
)
async def register_function(
    function_name: str,
    function_code: str,
    execution_engine = Depends(get_execution_engine)
):
    """
    Register a function in the execution engine.
    
    Note: This endpoint is disabled in production for security reasons.
    """
    raise HTTPException(status_code=501, detail="Function registration via API is disabled in production")


@routers.v1.get("/functions", response_model=APIResponse)
@api_contract(
    title="Function Registry Listing",
    description="Lists all registered functions available to the execution engine",
    endpoint="/api/v1/functions",
    method="GET",
    response_schema={
        "functions": "array - List of function names",
        "count": "int - Total number of functions"
    }
)
async def list_functions(execution_engine = Depends(get_execution_engine)):
    """
    List registered functions.
    """
    try:
        # Get function names from registry
        function_names = list(execution_engine.function_registry.keys())
        
        return APIResponse(
            status="success",
            data={
                "functions": function_names,
                "count": len(function_names)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing functions: {e}")
        return APIResponse(
            status="error",
            message="Error listing functions",
            errors=[str(e)]
        )


# Events endpoints
@routers.v1.get("/events", response_model=APIResponse)
@api_contract(
    title="Event Stream Query",
    description="Retrieves recent execution events for monitoring and debugging",
    endpoint="/api/v1/events",
    method="GET",
    request_schema={
        "event_type": "string (optional) - Filter by event type",
        "limit": "int - Maximum events to return (default: 100)"
    },
    response_schema={
        "events": "array - List of event objects",
        "count": "int - Number of events returned"
    }
)
async def list_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, description="Maximum number of events to return")
):
    """
    List recent events.
    """
    try:
        # Get event manager
        if not component:
            raise HTTPException(status_code=503, detail="Synthesis component not initialized")
            
        event_manager = component.event_manager
        
        # Get recent events
        events = event_manager.get_recent_events(event_type, limit)
        
        return APIResponse(
            status="success",
            data={
                "events": events,
                "count": len(events)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return APIResponse(
            status="error",
            message="Error listing events",
            errors=[str(e)]
        )


@routers.v1.post("/events", response_model=APIResponse)
@api_contract(
    title="Custom Event Emission",
    description="Allows components to emit custom events into the execution event stream",
    endpoint="/api/v1/events",
    method="POST",
    request_schema={
        "event_type": "string - Event type identifier",
        "event_data": "object - Arbitrary event payload"
    },
    response_schema={
        "event_id": "string - Unique identifier for emitted event"
    }
)
@integration_point(
    title="Event Bus Integration",
    description="Injects custom events into Synthesis event stream for component coordination",
    target_component="Event Manager, WebSocket subscribers",
    protocol="Internal event bus",
    data_flow="Component → Event API → Event Manager → WebSocket broadcast",
    integration_date="2024-12-01"
)
async def emit_event(
    event_type: str,
    event_data: Dict[str, Any]
):
    """
    Emit a custom event.
    """
    try:
        # Get event manager
        if not component:
            raise HTTPException(status_code=503, detail="Synthesis component not initialized")
            
        event_manager = component.event_manager
        
        # Emit event
        event_id = await event_manager.emit(event_type, event_data)
        
        return APIResponse(
            status="success",
            message=f"Event {event_type} emitted successfully",
            data={"event_id": event_id}
        )
        
    except Exception as e:
        logger.error(f"Error emitting event: {e}")
        return APIResponse(
            status="error",
            message="Error emitting event",
            errors=[str(e)]
        )


# Mount standard routers AFTER all endpoint definitions
mount_standard_routers(app, routers)

# Include additional routers
app.include_router(ws_router)
app.include_router(mcp_router)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    global_config = GlobalConfig.get_instance()
    port = global_config.config.synthesis.port
    
    uvicorn.run(app, host="0.0.0.0", port=port)