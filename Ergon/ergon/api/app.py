"""
Ergon API server.

This module provides a FastAPI-based REST API for Ergon,
allowing external systems to interact with the agent builder.
"""

import os
import sys
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio
import time
import json
from enum import Enum
import logging

# Import shared workflow endpoint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
from workflow.endpoint_template import create_workflow_endpoint

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Path, Body
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from tekton.models.base import TektonBaseModel
from contextlib import asynccontextmanager
from landmarks import api_contract, integration_point, danger_zone

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utils
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.utils.env_config import get_component_config
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.utils.health_check import create_health_response
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)

from ergon.core.database.engine import get_db_session, init_db
from ergon.core.database.models import Agent, AgentFile, AgentTool, AgentExecution, AgentMessage, DocumentationPage
from ergon.core.agents.generator import AgentGenerator
from ergon.core.agents.runner import AgentRunner
from ergon.core.docs.crawler import crawl_all_docs, crawl_pydantic_ai_docs, crawl_langchain_docs, crawl_anthropic_docs
from ergon.core.llm.client import LLMClient
from ergon.core.vector_store.faiss_store import FAISSDocumentStore
from ergon.core.memory.service import MemoryService
from ergon.utils.config.settings import settings
from ergon.utils.tekton_integration import get_component_port, configure_for_single_port

# Import A2A and MCP endpoints
from .a2a_endpoints import router as a2a_router
from .mcp_endpoints import router as mcp_router
from .fastmcp_endpoints import fastmcp_router, fastmcp_startup, fastmcp_shutdown
from .registry import router as registry_router
from .sandbox import router as sandbox_router
from .construct import router as construct_router

# Import ergon component
from ..core.ergon_component import ErgonComponent

# Create component singleton
ergon_component = ErgonComponent()

# Use shared logger
logger = setup_component_logging("ergon")

# Get port configuration
port_config = configure_for_single_port()
logger.info(f"Ergon API configured with port {port_config['port']}")

async def startup_callback():
    """Initialize Ergon component (includes Hermes registration)."""
    # Initialize component (includes Hermes registration)
    await ergon_component.initialize(
        capabilities=ergon_component.get_capabilities(),
        metadata=ergon_component.get_metadata()
    )
    
    # Component-specific FastMCP initialization (after component init)
    try:
        # Initialize FastMCP
        await fastmcp_startup()
        logger.info("FastMCP initialized")
        
        # Initialize Hermes MCP Bridge
        from ergon.core.mcp.hermes_bridge import ErgonMCPBridge
        
        # Use component's A2A client
        ergon_component.mcp_bridge = ErgonMCPBridge(ergon_component.a2a_client)
        await ergon_component.mcp_bridge.initialize()
        logger.info("Initialized Hermes MCP Bridge for FastMCP tools")
    except ImportError:
        logger.warning("FastMCP or MCP Bridge not available, continuing without")
    except Exception as e:
        logger.warning(f"Failed to initialize FastMCP/MCP Bridge: {e}")

# Create FastAPI app using component
app = ergon_component.create_app(
    startup_callback=startup_callback,
    **get_openapi_configuration(
        component_name="ergon",
        component_version="0.2.0",
        component_description="Agent system for specialized task execution"
    )
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers("ergon")

# Add exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"General error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# ----- Models -----

class AgentCreate(TektonBaseModel):
    """Model for creating a new agent."""
    name: str = Field(..., description="Name of the agent")
    description: str = Field(..., description="Description of the agent")
    model_name: Optional[str] = Field(None, description="Model to use (defaults to settings)")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="List of tools for the agent")
    temperature: float = Field(0.7, description="Temperature for generation (0-1)")

class AgentResponse(TektonBaseModel):
    """Model for agent response."""
    id: int
    name: str
    description: Optional[str] = None
    model_name: str
    system_prompt: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MessageCreate(TektonBaseModel):
    """Model for creating a new message."""
    content: str = Field(..., description="Content of the message")
    stream: bool = Field(False, description="Whether to stream the response")

class MessageResponse(TektonBaseModel):
    """Model for message response."""
    role: str
    content: str
    timestamp: datetime

class StatusResponse(TektonBaseModel):
    """Model for status response."""
    status: str
    version: str
    database: bool
    models: List[str]
    doc_count: int
    port: int
    single_port_enabled: bool

class DocCrawlRequest(TektonBaseModel):
    """Model for doc crawl request."""
    source: str = Field(..., description="Source to crawl ('all', 'pydantic', 'langchain', 'anthropic')")
    max_pages: int = Field(100, description="Maximum number of pages to crawl")

class DocCrawlResponse(TektonBaseModel):
    """Model for doc crawl response."""
    status: str
    pages_crawled: int
    source: str
    
class TerminalMessageRequest(TektonBaseModel):
    """Model for terminal message request."""
    message: str = Field(..., description="Message content")
    context_id: str = Field("ergon", description="Context ID (e.g., 'ergon', 'awt-team')")
    model: Optional[str] = Field(None, description="LLM model to use (defaults to settings)")
    temperature: Optional[float] = Field(None, description="Temperature for generation (0-1)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    streaming: bool = Field(True, description="Whether to stream the response")
    save_to_memory: bool = Field(True, description="Whether to save message to memory")
    
class TerminalMessageResponse(TektonBaseModel):
    """Model for terminal message response."""
    status: str
    message: Optional[str] = None
    error: Optional[str] = None
    context_id: str

# ----- Standard Routes -----

# Health check endpoint
@routers.root.get("/health")
async def health_check():
    """Get API health status following Tekton standards."""
    from tekton.utils.port_config import get_ergon_port
    port = get_ergon_port()
    
    # Use standardized health response
    return create_health_response(
        component_name="ergon",
        port=port,
        version="0.1.0",
        status="healthy",
        registered=ergon_component.global_config.is_registered_with_hermes,
        details={
            "services": ["agent_creation", "agent_execution", "memory_integration"]
        }
    )

# Root endpoint
@routers.root.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "component": "ergon",
        "description": "Agent system for specialized task execution",
        "version": "0.1.0",
        "status": "active"
    }

# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name="ergon",
        component_version="0.1.0",
        start_time=ergon_component.global_config._start_time,
        readiness_check=lambda: ergon_component.global_config.is_registered_with_hermes
    ),
    methods=["GET"]
)

# Add discovery endpoint
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name="ergon",
        component_version="0.1.0",
        component_description="Agent system for specialized task execution",
        endpoints=[
            EndpointInfo(path="/api/v1/agents", method="*", description="Agent management"),
            EndpointInfo(path="/api/v1/agents/{agent_id}", method="*", description="Agent operations"),
            EndpointInfo(path="/api/v1/agents/{agent_id}/run", method="POST", description="Run agent"),
            EndpointInfo(path="/api/v1/docs/crawl", method="POST", description="Crawl documentation"),
            EndpointInfo(path="/api/v1/docs/search", method="GET", description="Search documentation"),
            EndpointInfo(path="/api/v1/terminal/message", method="POST", description="Terminal message"),
            EndpointInfo(path="/api/v1/terminal/stream", method="POST", description="Terminal streaming")
        ],
        capabilities=ergon_component.get_capabilities(),
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata=ergon_component.get_metadata()
    ),
    methods=["GET"]
)

# Legacy status endpoint for backward compatibility
@routers.v1.get("/status", response_model=StatusResponse)
async def get_status():
    """Get API status."""
    with get_db_session() as db:
        doc_count = db.query(DocumentationPage).count()
        
    return {
        "status": "ok",
        "version": "0.1.0",
        "database": os.path.exists(str(ergon_component.db_path)) if ergon_component.db_path else False,
        "models": settings.available_models,
        "doc_count": doc_count,
        "port": port_config["port"],
        "single_port_enabled": True
    }

# ----- Business Routes -----

@routers.v1.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(0, description="Number of agents to skip"),
    limit: int = Query(100, description="Maximum number of agents to return")
):
    """List all agents."""
    with get_db_session() as db:
        agents = db.query(Agent).offset(skip).limit(limit).all()
        return [agent.__dict__ for agent in agents]

@routers.v1.post("/agents", response_model=AgentResponse)
@api_contract(
    title="Agent Creation API",
    endpoint="/api/v1/agents",
    method="POST",
    request_schema={"name": "string", "description": "string", "model_name": "string", "tools": "list"}
)
@integration_point(
    title="Agent Generator Integration",
    target_component="Agent Generator, LLM Client",
    protocol="Internal Python API",
    data_flow="Request -> Agent Generator -> LLM -> Agent Definition -> Database"
)
@danger_zone(
    title="Agent Code Generation",
    risk_level="high",
    risks=["Code injection", "Resource exhaustion", "Malicious agent creation"],
    mitigations=["Code validation", "Resource limits", "Sandboxing", "User authorization"],
    review_required=True
)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent."""
    try:
        # Initialize agent generator
        generator = AgentGenerator(
            model_name=agent_data.model_name,
            temperature=agent_data.temperature
        )
        
        # Generate agent
        agent_result = await generator.generate(
            name=agent_data.name,
            description=agent_data.description,
            tools=agent_data.tools
        )
        
        # Save agent to database
        with get_db_session() as db:
            agent = Agent(
                name=agent_result["name"],
                description=agent_result["description"],
                model_name=agent_result["model_name"],
                system_prompt=agent_result["system_prompt"]
            )
            db.add(agent)
            db.commit()
            db.refresh(agent)
            
            # Save agent files
            for file_data in agent_result["files"]:
                file = AgentFile(
                    agent_id=agent.id,
                    filename=file_data["filename"],
                    file_type=file_data["file_type"],
                    content=file_data["content"]
                )
                db.add(file)
            
            # Save agent tools
            for tool_data in agent_result.get("tools", []):
                tool = AgentTool(
                    agent_id=agent.id,
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    function_def=json.dumps(tool_data)
                )
                db.add(tool)
            
            db.commit()
            db.refresh(agent)
            
            return agent.__dict__
            
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@routers.v1.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int = Path(..., description="ID of the agent")):
    """Get agent by ID."""
    with get_db_session() as db:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
        
        return agent.__dict__

@routers.v1.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int = Path(..., description="ID of the agent")):
    """Delete agent by ID."""
    with get_db_session() as db:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
        
        db.delete(agent)
        db.commit()
        
        return {"status": "deleted", "id": agent_id}

@routers.v1.post("/agents/{agent_id}/run", response_model=MessageResponse)
async def run_agent(
    message: MessageCreate,
    agent_id: int = Path(..., description="ID of the agent")
):
    """Run an agent with the given input."""
    try:
        with get_db_session() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found")
            
            # Create execution record
            execution = AgentExecution(agent_id=agent.id)
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Record user message
            user_message = AgentMessage(
                execution_id=execution.id,
                role="user",
                content=message.content
            )
            db.add(user_message)
            db.commit()
        
        # Initialize runner
        runner = AgentRunner(agent=agent, execution_id=execution.id)
        
        if message.stream:
            async def generate():
                async for chunk in runner.arun_stream(message.content):
                    yield f"data: {chunk}\n\n"
                
                # Mark execution as completed
                with get_db_session() as db:
                    execution = db.query(AgentExecution).filter(AgentExecution.id == execution.id).first()
                    if execution:
                        execution.completed_at = datetime.now()
                        execution.success = True
                        db.commit()
                
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Run agent
            response = await runner.arun(message.content)
            
            # Mark execution as completed
            with get_db_session() as db:
                execution = db.query(AgentExecution).filter(AgentExecution.id == execution.id).first()
                if execution:
                    execution.completed_at = datetime.now()
                    execution.success = True
                    db.commit()
                
                # Get assistant message
                assistant_message = db.query(AgentMessage).filter(
                    AgentMessage.execution_id == execution.id,
                    AgentMessage.role == "assistant"
                ).order_by(AgentMessage.id.desc()).first()
                
                if assistant_message:
                    return {
                        "role": assistant_message.role,
                        "content": assistant_message.content,
                        "timestamp": assistant_message.timestamp
                    }
                else:
                    # If no message found, create one
                    return {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now()
                    }
            
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")

@routers.v1.post("/docs/crawl", response_model=DocCrawlResponse)
async def crawl_docs(request: DocCrawlRequest):
    """Crawl documentation from specified source."""
    try:
        pages_crawled = 0
        
        if request.source.lower() == "all":
            pages_crawled = await crawl_all_docs()
            source = "all"
        elif request.source.lower() == "pydantic":
            pages_crawled = await crawl_pydantic_ai_docs()
            source = "pydantic"
        elif request.source.lower() == "langchain":
            pages_crawled = await crawl_langchain_docs()
            source = "langchain"
        elif request.source.lower() == "anthropic":
            pages_crawled = await crawl_anthropic_docs()
            source = "anthropic"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown source: {request.source}")
        
        return {
            "status": "ok",
            "pages_crawled": pages_crawled,
            "source": source
        }
        
    except Exception as e:
        logger.error(f"Error crawling docs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error crawling docs: {str(e)}")

@routers.v1.get("/docs/search")
async def search_docs(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Maximum number of results to return")
):
    """Search documentation."""
    try:
        vector_store = FAISSDocumentStore()
        results = vector_store.search(query, top_k=limit)
        
        # Clean up results
        cleaned_results = []
        for result in results:
            # Truncate content if too long
            content = result["content"]
            if len(content) > 500:
                content = content[:500] + "..."
            
            cleaned_results.append({
                "id": result["id"],
                "title": result["metadata"].get("title", "Untitled"),
                "url": result["metadata"].get("url", ""),
                "source": result["metadata"].get("source", ""),
                "content": content,
                "score": result["score"]
            })
        
        return cleaned_results
        
    except Exception as e:
        logger.error(f"Error searching docs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching docs: {str(e)}")

@routers.v1.post("/terminal/message", response_model=TerminalMessageResponse)
async def terminal_message(
    request: TerminalMessageRequest,
    background_tasks: BackgroundTasks
):
    """Handle terminal message from UI."""
    try:
        # Get appropriate LLM client based on settings
        llm_client = LLMClient(
            model_name=request.model,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens
        )
        
        # Prepare messages
        messages = []
        
        # Add a system message based on the context
        system_message = "You are a helpful assistant."
        if request.context_id == "ergon":
            system_message = "You are the Ergon CI assistant, specialized in agent creation, automation, and tool configuration for the Tekton system. Be concise and helpful."
        elif request.context_id == "awt-team":
            system_message = "You are the Advanced Workflow Team assistant for Tekton. You specialize in workflow automation, process design, and team collaboration. Be concise and helpful."
        elif request.context_id == "agora":
            system_message = "You are Agora, a multi-component CI assistant for Tekton. You coordinate between different CI systems to solve complex problems. Be concise and helpful."
        
        messages.append({"role": "system", "content": system_message})
        
        # Get previous messages from memory if applicable
        if request.save_to_memory:
            prev_messages = ergon_component.terminal_memory.get_recent_messages(request.context_id, limit=10)
            messages.extend(prev_messages)
        
        # Add the current user message
        messages.append({"role": "user", "content": request.message})
        
        # If streaming is requested, handle streaming response
        if request.streaming:
            return await terminal_stream(request, background_tasks)
        
        # Otherwise, handle regular response
        # Call LLM with the message
        response = await llm_client.acomplete(messages)
        
        # Save to memory if needed
        if request.save_to_memory:
            background_tasks.add_task(
                terminal_memory.add_message,
                context_id=request.context_id,
                message=request.message,
                role="user"
            )
            background_tasks.add_task(
                terminal_memory.add_message,
                context_id=request.context_id,
                message=response,
                role="assistant"
            )
        
        return {
            "status": "success",
            "message": response,
            "context_id": request.context_id
        }
    except Exception as e:
        logger.error(f"Error handling terminal message: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "context_id": request.context_id
        }

@routers.v1.post("/terminal/stream")
async def terminal_stream(
    request: TerminalMessageRequest,
    background_tasks: BackgroundTasks
):
    """Stream response from LLM for terminal."""
    try:
        # Get appropriate LLM client based on settings
        llm_client = LLMClient(
            model_name=request.model,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens
        )
        
        # Prepare messages
        messages = []
        
        # Add a system message based on the context
        system_message = "You are a helpful assistant."
        if request.context_id == "ergon":
            system_message = "You are the Ergon CI assistant, specialized in agent creation, automation, and tool configuration for the Tekton system. Be concise and helpful."
        elif request.context_id == "awt-team":
            system_message = "You are the Advanced Workflow Team assistant for Tekton. You specialize in workflow automation, process design, and team collaboration. Be concise and helpful."
        elif request.context_id == "agora":
            system_message = "You are Agora, a multi-component CI assistant for Tekton. You coordinate between different CI systems to solve complex problems. Be concise and helpful."
        
        messages.append({"role": "system", "content": system_message})
        
        # Get previous messages from memory if applicable
        if request.save_to_memory:
            prev_messages = ergon_component.terminal_memory.get_recent_messages(request.context_id, limit=10)
            messages.extend(prev_messages)
        
        # Add the current user message
        messages.append({"role": "user", "content": request.message})
        
        # Save user message to memory
        if request.save_to_memory:
            background_tasks.add_task(
                terminal_memory.add_message,
                context_id=request.context_id,
                message=request.message,
                role="user"
            )
        
        # Create string buffer to collect full response
        response_buffer = []
        
        # Define callback to save complete response to memory
        async def on_complete():
            if request.save_to_memory:
                full_response = "".join(response_buffer)
                await terminal_memory.add_message(
                    context_id=request.context_id,
                    message=full_response,
                    role="assistant"
                )
        
        # Stream generator function
        async def generate():
            async for chunk in llm_client.acomplete_stream(messages):
                # Add to buffer for saving later
                response_buffer.append(chunk)
                
                # Format as server-sent event
                yield f"data: {json.dumps({'chunk': chunk, 'context_id': request.context_id})}\n\n"
            
            # Complete streaming
            await on_complete()
            yield f"data: {json.dumps({'done': True, 'context_id': request.context_id})}\n\n"
        
        # Return streaming response
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Error streaming terminal response: {str(e)}")
        # Return error as SSE
        async def error_response():
            yield f"data: {json.dumps({'error': str(e), 'context_id': request.context_id})}\n\n"
        
        return StreamingResponse(
            error_response(),
            media_type="text/event-stream"
        )

# Mount standard routers
mount_standard_routers(app, routers)

# Include business routers (already included in v1 router)
# The business endpoints are already defined with @routers.v1 decorators

# Include A2A and MCP routers under v1
routers.v1.include_router(a2a_router, prefix="/a2a", tags=["A2A"])
routers.v1.include_router(mcp_router, prefix="/mcp", tags=["MCP"])

# Include Registry router (note: registry has its own /api/ergon/registry prefix)
app.include_router(registry_router)

# Include Sandbox router (note: sandbox has its own /api/ergon/sandbox prefix)
app.include_router(sandbox_router)

# Include Construct router (note: construct has its own /api/ergon/construct prefix)
app.include_router(construct_router)

# Include FastMCP router at its special path
app.include_router(fastmcp_router, prefix="/api/mcp/v2")  # Mount FastMCP router under /api/mcp/v2

# Include standardized workflow endpoint
workflow_router = create_workflow_endpoint("ergon")
app.include_router(workflow_router)

# ==================== Ergon V2 Endpoints ====================

# Autonomy Management Endpoints
@routers.v1.get("/autonomy/level")
async def get_autonomy_level():
    """Get current autonomy level."""
    return {
        "current_level": ergon_component.current_autonomy_level.value,
        "available_levels": ["advisory", "assisted", "guided", "autonomous"]
    }


class SetAutonomyRequest(TektonBaseModel):
    """Request to set autonomy level."""
    level: str = Field(..., description="Autonomy level to set")
    reason: Optional[str] = Field(None, description="Reason for change")


@routers.v1.post("/autonomy/level")
async def set_autonomy_level(request: SetAutonomyRequest):
    """Set autonomy level for Ergon operations."""
    try:
        from ergon.core.ergon_component import AutonomyLevel
        autonomy_level = AutonomyLevel(request.level)
        await ergon_component.set_autonomy_level(autonomy_level, request.reason)
        return {"status": "success", "new_level": request.level}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid autonomy level: {request.level}")


# Solution Registry Endpoints (Phase 1)
@routers.v1.get("/solutions")
async def list_solutions(
    type: Optional[str] = Query(None, description="Filter by solution type"),
    capability: Optional[str] = Query(None, description="Filter by capability"),
    search: Optional[str] = Query(None, description="Search term"),
    limit: int = Query(100, description="Maximum results"),
    offset: int = Query(0, description="Offset for pagination")
):
    """List solutions in the registry."""
    if not ergon_component.solution_registry:
        return {
            "status": "error",
            "message": "Solution registry not initialized",
            "solutions": [],
            "total": 0
        }
    
    try:
        from ergon.core.database.v2_models import SolutionType
        
        # Convert type string to enum if provided
        solution_type = SolutionType(type) if type else None
        
        # Get solutions from repository
        solutions, total = await ergon_component.solution_registry.list_solutions(
            solution_type=solution_type,
            search=search,
            capability=capability,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "solutions": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.type.value,
                    "description": s.description,
                    "version": s.version,
                    "author": s.author,
                    "tags": s.tags,
                    "capabilities": s.capabilities,
                    "usage_count": s.usage_count,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in solutions
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error listing solutions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Create Solution Model
class CreateSolutionRequest(TektonBaseModel):
    """Request to create a new solution."""
    name: str = Field(..., description="Solution name")
    type: str = Field(..., description="Solution type")
    description: str = Field("", description="Solution description")
    version: str = Field("1.0.0", description="Solution version")
    source_url: Optional[str] = Field(None, description="Source repository URL")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    author: str = Field("unknown", description="Solution author")
    license: str = Field("unknown", description="Solution license")
    tags: List[str] = Field([], description="Solution tags")
    capabilities: Dict[str, Any] = Field({}, description="Solution capabilities")
    dependencies: Dict[str, Any] = Field({}, description="Solution dependencies")
    configuration_template: Dict[str, Any] = Field({}, description="Configuration template")
    usage_examples: List[str] = Field([], description="Usage examples")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")


@routers.v1.post("/solutions")
async def create_solution(request: CreateSolutionRequest):
    """Create a new solution in the registry."""
    if not ergon_component.solution_registry:
        raise HTTPException(status_code=503, detail="Solution registry not initialized")
    
    try:
        solution = await ergon_component.solution_registry.create_solution(request.dict())
        
        return {
            "status": "success",
            "solution": {
                "id": solution.id,
                "name": solution.name,
                "type": solution.type.value,
                "description": solution.description,
                "version": solution.version,
                "created_at": solution.created_at.isoformat() if solution.created_at else None
            }
        }
    except Exception as e:
        logger.error(f"Error creating solution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.get("/solutions/{solution_id}")
async def get_solution(solution_id: int = Path(..., description="Solution ID")):
    """Get a specific solution by ID."""
    if not ergon_component.solution_registry:
        raise HTTPException(status_code=503, detail="Solution registry not initialized")
    
    solution = await ergon_component.solution_registry.get_solution(solution_id)
    
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return {
        "status": "success",
        "solution": {
            "id": solution.id,
            "name": solution.name,
            "type": solution.type.value,
            "description": solution.description,
            "version": solution.version,
            "source_url": solution.source_url,
            "documentation_url": solution.documentation_url,
            "author": solution.author,
            "license": solution.license,
            "tags": solution.tags,
            "capabilities": solution.capabilities,
            "dependencies": solution.dependencies,
            "configuration_template": solution.configuration_template,
            "usage_examples": solution.usage_examples,
            "metadata": solution.extra_metadata,
            "usage_count": solution.usage_count,
            "created_at": solution.created_at.isoformat() if solution.created_at else None,
            "updated_at": solution.updated_at.isoformat() if solution.updated_at else None,
            "last_accessed": solution.last_accessed.isoformat() if solution.last_accessed else None
        }
    }


@routers.v1.put("/solutions/{solution_id}")
async def update_solution(
    solution_id: int = Path(..., description="Solution ID"),
    update_data: Dict[str, Any] = Body(..., description="Fields to update")
):
    """Update a solution."""
    if not ergon_component.solution_registry:
        raise HTTPException(status_code=503, detail="Solution registry not initialized")
    
    solution = await ergon_component.solution_registry.update_solution(solution_id, update_data)
    
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return {
        "status": "success",
        "solution": {
            "id": solution.id,
            "name": solution.name,
            "type": solution.type.value,
            "updated_at": solution.updated_at.isoformat() if solution.updated_at else None
        }
    }


@routers.v1.delete("/solutions/{solution_id}")
async def delete_solution(solution_id: int = Path(..., description="Solution ID")):
    """Delete a solution."""
    if not ergon_component.solution_registry:
        raise HTTPException(status_code=503, detail="Solution registry not initialized")
    
    deleted = await ergon_component.solution_registry.delete_solution(solution_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return {"status": "success", "message": "Solution deleted"}


@routers.v1.get("/solutions/popular")
async def get_popular_solutions(limit: int = Query(10, description="Maximum results")):
    """Get most popular solutions by usage count."""
    if not ergon_component.solution_registry:
        raise HTTPException(status_code=503, detail="Solution registry not initialized")
    
    solutions = await ergon_component.solution_registry.get_popular_solutions(limit)
    
    return {
        "status": "success",
        "solutions": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type.value,
                "description": s.description,
                "usage_count": s.usage_count
            }
            for s in solutions
        ]
    }


@routers.v1.get("/solutions/recent")
async def get_recent_solutions(limit: int = Query(10, description="Maximum results")):
    """Get recently added solutions."""
    if not ergon_component.solution_registry:
        raise HTTPException(status_code=503, detail="Solution registry not initialized")
    
    solutions = await ergon_component.solution_registry.get_recent_solutions(limit)
    
    return {
        "status": "success",
        "solutions": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type.value,
                "description": s.description,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in solutions
        ]
    }


# MCP Tool Discovery Endpoints
@routers.v1.get("/tools/discover")
async def discover_tools():
    """Get discovered MCP tools."""
    if not ergon_component.tool_discovery:
        return {
            "status": "error",
            "message": "Tool discovery not initialized",
            "tools": []
        }
    
    return {
        "status": "success",
        "tools": [
            {
                "name": f"{tool.provider}.{tool.name}",
                "description": tool.description,
                "provider": tool.provider,
                "version": tool.version,
                "capabilities": tool.capabilities,
                "parameters": tool.parameters,
                "available": tool.available
            }
            for tool in ergon_component.tool_discovery.tools.values()
        ],
        "total": len(ergon_component.tool_discovery.tools)
    }


@routers.v1.get("/tools/search")
async def search_tools(
    query: str = Query(..., description="Search query"),
    capability: Optional[str] = Query(None, description="Filter by capability")
):
    """Search for MCP tools."""
    if not ergon_component.tool_discovery:
        raise HTTPException(status_code=503, detail="Tool discovery not initialized")
    
    # Search by query
    results = ergon_component.tool_discovery.search_tools(query)
    
    # Filter by capability if provided
    if capability:
        results = [t for t in results if capability in t.capabilities]
    
    return {
        "query": query,
        "capability": capability,
        "results": [
            {
                "name": f"{tool.provider}.{tool.name}",
                "description": tool.description,
                "provider": tool.provider,
                "capabilities": tool.capabilities
            }
            for tool in results
        ],
        "count": len(results)
    }


@routers.v1.get("/tools/recommend")
async def recommend_tools(
    task_type: str = Query(..., description="Type of task (file_operations, code_execution, etc)")
):
    """Get tool recommendations for a task type."""
    if not ergon_component.tool_discovery:
        raise HTTPException(status_code=503, detail="Tool discovery not initialized")
    
    recommendations = ergon_component.tool_discovery.get_tool_recommendations(task_type)
    
    return {
        "task_type": task_type,
        "recommendations": [
            {
                "name": f"{tool.provider}.{tool.name}",
                "description": tool.description,
                "provider": tool.provider,
                "capabilities": tool.capabilities,
                "reason": f"Recommended for {task_type} tasks"
            }
            for tool in recommendations
        ],
        "count": len(recommendations)
    }


@routers.v1.get("/tools/status")
async def tool_discovery_status():
    """Get tool discovery status."""
    if not ergon_component.tool_discovery:
        return {
            "status": "error",
            "message": "Tool discovery not initialized"
        }
    
    status = ergon_component.tool_discovery.get_discovery_status()
    return {
        "status": "success",
        **status
    }


# GitHub Analysis Endpoints (Phase 2)
class AnalyzeRequest(TektonBaseModel):
    """Request to analyze a repository."""
    repository_url: Optional[str] = Field(None, description="GitHub repository URL")
    deep_scan: bool = Field(False, description="Perform deep architecture analysis")
    analysis_type: Optional[str] = Field("full", description="Type of analysis to perform")
    local_path: Optional[str] = Field(None, description="Local path to repository")


@routers.v1.post("/analyze")
async def analyze_repository(request: AnalyzeRequest):
    """Analyze a GitHub repository for reusable components."""
    # For now, return placeholder data based on analysis type
    analysis_type = request.analysis_type or 'full'
    repo_path = request.repository_url or request.local_path or "unknown"
    
    base_result = {
        "status": "success",
        "repository_url": repo_path,
        "analysis_id": f"analysis-{analysis_type}-{abs(hash(repo_path)) % 10000}"
    }
    
    if analysis_type == 'basic':
        return {
            **base_result,
            "type": "Basic Analysis",
            "summary": "Repository structure and basic information analyzed.",
            "components": {
                "languages": ["Python", "JavaScript", "HTML"],
                "frameworks": ["FastAPI", "Vue.js"],
                "dependencies": 42,
                "files": 156
            }
        }
    elif analysis_type == 'architecture':
        return {
            **base_result,
            "type": "Architecture Analysis", 
            "summary": "System architecture and design patterns identified.",
            "architecture": {
                "pattern": "Microservices",
                "components": ["API Gateway", "Service Registry", "Message Bus"],
                "integrations": ["REST APIs", "WebSocket", "GraphQL"],
                "data_flow": "Event-driven with CQRS"
            }
        }
    elif analysis_type == 'companion':
        return {
            **base_result,
            "type": "Companion Intelligence Analysis",
            "summary": "Evaluating how CI integration could transform development workflow.",
            "companion_benefits": {
                "automation": [
                    "Automated code reviews with context awareness",
                    "Intelligent refactoring suggestions",
                    "Real-time bug detection and fixes"
                ],
                "training": [
                    "Interactive code explanations",
                    "Best practices enforcement",
                    "Team knowledge sharing"
                ],
                "enhancement": [
                    "Performance optimization recommendations",
                    "Security vulnerability detection",
                    "Architecture evolution guidance"
                ],
                "integration_approach": "Embedded CI with MCP tools and Hermes messaging"
            }
        }
    elif analysis_type == 'tekton':
        return {
            **base_result,
            "type": "Tekton Integration Analysis",
            "summary": "Tekton compatibility and integration points assessed.",
            "tekton_compatibility": {
                "score": 0.85,
                "integration_points": ["Hermes messaging", "A2A sockets", "MCP tools"],
                "recommended_approach": "Service wrapper with Hermes integration",
                "effort_estimate": "2-3 days"
            }
        }
    else:  # full
        return {
            **base_result,
            "type": "Full Analysis",
            "summary": "Comprehensive analysis completed across all dimensions.",
            "results": {
                "basic": "Complete",
                "architecture": "Complete", 
                "tekton": "Complete",
                "reusability_score": 0.78,
                "recommendations": [
                    "Extract authentication module as standalone service",
                    "Implement Hermes message bus integration",
                    "Add MCP tool discovery for API endpoints"
                ]
            }
        }


# Configuration Generation Endpoints (Phase 2)
class ConfigureRequest(TektonBaseModel):
    """Request to generate configuration."""
    solution_id: str = Field(..., description="Solution ID to configure")
    config_type: str = Field(..., description="Type of configuration to generate")
    parameters: Dict[str, Any] = Field({}, description="Configuration parameters")


@routers.v1.post("/configure")
async def configure_solution(request: ConfigureRequest):
    """Generate configuration for a solution."""
    return {
        "status": "not_implemented",
        "message": "Configuration generation coming in Phase 2",
        "solution_id": request.solution_id,
        "config_type": request.config_type,
        "configuration_id": None
    }


# Workflow Memory Endpoints
class StartWorkflowCaptureRequest(TektonBaseModel):
    """Request to start workflow capture."""
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    context: Dict[str, Any] = Field({}, description="Initial context")


@routers.v1.post("/workflows/capture/start")
async def start_workflow_capture(request: StartWorkflowCaptureRequest):
    """Start capturing a new workflow."""
    if not ergon_component.workflow_memory:
        raise HTTPException(status_code=503, detail="Workflow memory not initialized")
    
    workflow_id = await ergon_component.workflow_memory.start_capture(
        name=request.name,
        description=request.description,
        context=request.context
    )
    
    return {
        "status": "success",
        "workflow_id": workflow_id,
        "message": "Workflow capture started"
    }


class CaptureStepRequest(TektonBaseModel):
    """Request to capture a workflow step."""
    workflow_id: str = Field(..., description="Workflow ID")
    step_type: str = Field(..., description="Step type")
    action: str = Field(..., description="Action performed")
    parameters: Dict[str, Any] = Field({}, description="Step parameters")
    result: Optional[Dict[str, Any]] = Field(None, description="Step result")


@routers.v1.post("/workflows/capture/step")
async def capture_workflow_step(request: CaptureStepRequest):
    """Capture a workflow step."""
    if not ergon_component.workflow_memory:
        raise HTTPException(status_code=503, detail="Workflow memory not initialized")
    
    from ergon.core.database.v2_models import StepType
    
    try:
        step_type = StepType(request.step_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid step type: {request.step_type}")
    
    await ergon_component.workflow_memory.capture_step(
        workflow_id=request.workflow_id,
        step_type=step_type,
        action=request.action,
        parameters=request.parameters,
        result=request.result
    )
    
    return {"status": "success", "message": "Step captured"}


class EndWorkflowCaptureRequest(TektonBaseModel):
    """Request to end workflow capture."""
    workflow_id: str = Field(..., description="Workflow ID")
    success: bool = Field(True, description="Whether workflow succeeded")
    metrics: Dict[str, Any] = Field({}, description="Performance metrics")


@routers.v1.post("/workflows/capture/end")
async def end_workflow_capture(request: EndWorkflowCaptureRequest):
    """End workflow capture."""
    if not ergon_component.workflow_memory:
        raise HTTPException(status_code=503, detail="Workflow memory not initialized")
    
    await ergon_component.workflow_memory.end_capture(
        workflow_id=request.workflow_id,
        success=request.success,
        metrics=request.metrics
    )
    
    return {"status": "success", "message": "Workflow capture ended"}


@routers.v1.get("/workflows/similar")
async def find_similar_workflows(
    description: str = Query(..., description="Description to match"),
    limit: int = Query(5, description="Maximum results")
):
    """Find workflows similar to the description."""
    if not ergon_component.workflow_memory:
        raise HTTPException(status_code=503, detail="Workflow memory not initialized")
    
    workflows = await ergon_component.workflow_memory.find_similar_workflows(
        description=description,
        limit=limit
    )
    
    return {
        "description": description,
        "workflows": [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "success_rate": w.success_rate,
                "execution_count": w.execution_count,
                "pattern_type": w.pattern_type
            }
            for w in workflows
        ],
        "count": len(workflows)
    }


@routers.v1.post("/workflows/{workflow_id}/replay")
async def replay_workflow(
    workflow_id: int = Path(..., description="Workflow ID"),
    context: Dict[str, Any] = Body({}, description="Override context"),
    dry_run: bool = Query(False, description="Don't execute, just plan")
):
    """Replay a captured workflow."""
    if not ergon_component.workflow_memory:
        raise HTTPException(status_code=503, detail="Workflow memory not initialized")
    
    result = await ergon_component.workflow_memory.replay_workflow(
        workflow_id=workflow_id,
        context=context if context else None,
        dry_run=dry_run
    )
    
    return result


@routers.v1.get("/workflows/patterns/suggest")
async def suggest_workflow_patterns(
    task_description: str = Query(..., description="Task description")
):
    """Get workflow pattern suggestions for a task."""
    if not ergon_component.workflow_memory:
        raise HTTPException(status_code=503, detail="Workflow memory not initialized")
    
    suggestions = ergon_component.workflow_memory.get_pattern_suggestions(task_description)
    
    return {
        "task_description": task_description,
        "suggestions": suggestions,
        "count": len(suggestions)
    }


# Workflow Automation Endpoints (Phase 3)
@routers.v1.get("/workflows")
async def list_workflows():
    """List available workflows."""
    return {
        "status": "not_implemented",
        "message": "Full workflow listing coming in Phase 3",
        "workflows": []
    }


# The Ultimate Endpoint - Automate Casey
class AutomateRequest(TektonBaseModel):
    """Request to automate development."""
    project_description: str = Field(..., description="What to build")
    autonomy_level: Optional[str] = Field(None, description="Override autonomy level")
    sprint_name: Optional[str] = Field(None, description="Dev sprint name")


@routers.v1.post("/automate")
async def automate_development(request: AutomateRequest):
    """The ultimate endpoint - automate Casey's expertise."""
    from ergon.core.ergon_component import AutonomyLevel
    
    level = None
    if request.autonomy_level:
        try:
            level = AutonomyLevel(request.autonomy_level)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid autonomy level: {request.autonomy_level}"
            )
    
    result = await ergon_component.automate_casey(
        request.project_description, 
        level
    )
    return result


# Add WebSocket endpoint for A2A and MCP (at root level)
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for A2A and MCP communication."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message based on its type
            if "protocol" in message:
                if message["protocol"] == "a2a":
                    # Handle A2A message
                    await websocket.send_text(json.dumps({
                        "type": "a2a_ack",
                        "status": "received",
                        "timestamp": time.time()
                    }))
                elif message["protocol"] == "mcp":
                    # Handle MCP message
                    await websocket.send_text(json.dumps({
                        "type": "mcp_ack",
                        "status": "received",
                        "timestamp": time.time()
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Unknown protocol: {message.get('protocol')}"
                    }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Missing protocol field"
                }))
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()


# Run with: uvicorn ergon.api.app:app --host 0.0.0.0 --port $ERGON_PORT (default: 8002)

# Store component in app state for access by endpoints
app.state.component = ergon_component

if __name__ == "__main__":
    import uvicorn
    from shared.utils.global_config import GlobalConfig
    
    global_config = GlobalConfig.get_instance()
    default_port = global_config.config.ergon.port
    
    uvicorn.run(app, host="0.0.0.0", port=default_port)