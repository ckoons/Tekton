"""
FastAPI application for the Rhetor API that provides both HTTP and WebSocket interfaces.

This module provides a single-port API for LLM interactions, template management,
and prompt engineering capabilities.
"""

import os
from shared.env import TektonEnviron
import sys
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import Field
from tekton.models import TektonBaseModel
from landmarks import api_contract, integration_point

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.urls import hermes_url
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

from ..core.rhetor_component import RhetorComponent
from ..templates import system_prompts

# Set up logging
logger = setup_component_logging("rhetor")

# Component configuration
COMPONENT_NAME = "rhetor"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "LLM orchestration and management service"

# Create component instance (singleton)
component = RhetorComponent()




# Request/Response models
class ChatRequest(TektonBaseModel):
    """Chat request model"""
    messages: List[Dict[str, str]]
    model: Optional[str] = Field(None, description="Model to use (defaults to routing logic)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    stream: Optional[bool] = Field(False, description="Enable streaming response")
    context_id: Optional[str] = Field(None, description="Context ID for conversation history")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tools available for the model")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice configuration")
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format configuration")
    request_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional request metadata")
    component: Optional[str] = Field(None, description="Component making the request")
    capability: Optional[str] = Field("chat", description="Capability type")


class ChatResponse(TektonBaseModel):
    """Chat response model"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    context_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    response: Optional[str] = None  # Alias for content for backward compatibility


class TemplateRequest(TektonBaseModel):
    """Template request model"""
    name: str
    content: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PromptRequest(TektonBaseModel):
    """Prompt request model"""
    template_name: str
    variables: Optional[Dict[str, Any]] = None
    context_id: Optional[str] = None


class GenerateRequest(TektonBaseModel):
    """Generate request model for simple text generation"""
    prompt: str
    model: Optional[str] = Field(None, description="Model to use")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2000, gt=0)
    system_prompt: Optional[str] = Field(None, description="System prompt")
    component: Optional[str] = Field(None, description="Component making the request")
    capability: Optional[str] = Field("reasoning", description="Capability type")


class GenerateResponse(TektonBaseModel):
    """Generate response model"""
    response: str
    model: str
    usage: Optional[Dict[str, Any]] = None


class PromptRegistryRequest(TektonBaseModel):
    """Prompt registry request model"""
    name: str
    template: str
    description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class BudgetPolicyRequest(TektonBaseModel):
    """Budget policy request model"""
    name: str
    max_cost: float
    period: str  # hourly, daily, weekly, monthly
    description: Optional[str] = None


class ContextRequest(TektonBaseModel):
    """Context request model"""
    context_id: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    max_tokens: Optional[int] = Field(None, description="Maximum context size in tokens")
    metadata: Optional[Dict[str, Any]] = None


# Startup callback for component initialization
async def startup_callback():
    """Component startup callback."""
    global component
    try:
        
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        
        # Initialize MCP components after component startup
        await component.initialize_mcp_components()
        
        # Initialize simplified MCP tools integration for team chat
        from rhetor.core.mcp.tools_integration_simple import MCPToolsIntegrationSimple, set_mcp_tools_integration
        integration = MCPToolsIntegrationSimple()
        set_mcp_tools_integration(integration)
        logger.info("Initialized simplified MCP tools integration")
        
        logger.info(f"Rhetor API server started successfully")
    except Exception as e:
        logger.error(f"Failed to start Rhetor: {e}")
        raise


# Initialize FastAPI app with standard configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    ),
    on_startup=[startup_callback]
)

# Add FastMCP endpoints
try:
    from .fastmcp_endpoints import mcp_router
    app.include_router(mcp_router)
    logger.info("FastMCP endpoints added to Rhetor API")
except ImportError as e:
    logger.warning(f"FastMCP endpoints not available: {e}")

# Add simplified CI Specialist endpoints
try:
    from .ai_specialist_endpoints_simple import router as ai_router
    app.include_router(ai_router)
    logger.info("Simplified CI Specialist endpoints added to Rhetor API")
except ImportError as e:
    logger.warning(f"CI Specialist endpoints not available: {e}")

# Add Team Chat endpoints
try:
    from .team_chat_endpoints import router as team_chat_router
    app.include_router(team_chat_router)
    
    # Include new streaming team chat
    from .team_chat_streaming import router as team_chat_streaming_router
    app.include_router(team_chat_streaming_router)
    logger.info("Team Chat endpoints added to Rhetor API")
except ImportError as e:
    logger.warning(f"Team Chat endpoints not available: {e}")

# Add simplified Specialist Streaming endpoints
try:
    from .specialist_streaming_endpoints_simple import router as streaming_router
    app.include_router(streaming_router)
    logger.info("Simplified Specialist Streaming endpoints added to Rhetor API")
except ImportError as e:
    logger.warning(f"Specialist Streaming endpoints not available: {e}")

# Add Model Management endpoints
try:
    from .model_endpoints import router as model_router
    app.include_router(model_router)
    logger.info("Model Management endpoints added to Rhetor API")
except ImportError as e:
    logger.warning(f"Model Management endpoints not available: {e}")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers(COMPONENT_NAME)

# Root endpoint
@routers.root.get("/")
async def root():
    """Root endpoint for the Rhetor API."""
    global_config = GlobalConfig.get_instance()
    port = global_config.config.rhetor.port
    
    return {
        "name": f"{COMPONENT_NAME} LLM Orchestration API",
        "version": COMPONENT_VERSION,
        "status": "running",
        "description": COMPONENT_DESCRIPTION,
        "documentation": "/api/v1/docs"
    }

# Health check endpoint
@routers.root.get("/health")
async def health():
    """Check the health of the Rhetor component following Tekton standards."""
    global_config = GlobalConfig.get_instance()
    port = global_config.config.rhetor.port
    
    # Get component status
    if component:
        component_status = component.get_component_status()
        health_status = "healthy" if component.initialized else "degraded"
    else:
        component_status = {}
        health_status = "degraded"
    
    return create_health_response(
        component_name=COMPONENT_NAME,
        port=port,
        version=COMPONENT_VERSION,
        status=health_status,
        registered=component.global_config.is_registered_with_hermes if component else False,
        details=component_status
    )

# Ready endpoint
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    ready_check = create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=time.time(),
        readiness_check=lambda: component and component.initialized
    )
    return await ready_check()

# Discovery endpoint
@routers.v1.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    discovery_check = create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(path="/api/v1/chat", method="POST", description="Send chat messages"),
            EndpointInfo(path="/api/v1/chat/stream", method="POST", description="Stream chat responses"),
            EndpointInfo(path="/api/v1/templates", method="*", description="Template management"),
            EndpointInfo(path="/api/v1/prompts", method="*", description="Prompt operations"),
            EndpointInfo(path="/api/v1/registry", method="*", description="Prompt registry"),
            EndpointInfo(path="/api/v1/context", method="*", description="Context management"),
            EndpointInfo(path="/api/v1/models", method="GET", description="List available models"),
            EndpointInfo(path="/api/v1/budget", method="*", description="Budget management"),
            EndpointInfo(path="/api/v1/specialists", method="*", description="CI specialist management"),
            EndpointInfo(path="/api/team-chat", method="POST", description="Team chat with multiple CIs"),
            EndpointInfo(path="/api/team-chat/stream", method="GET", description="Stream team chat responses"),
            EndpointInfo(path="/api/team-chat/sockets", method="GET", description="List team chat sockets"),
            EndpointInfo(path="/api/chat/{specialist_id}/stream", method="POST", description="Stream from individual specialist"),
            EndpointInfo(path="/api/chat/{specialist_id}/stream", method="GET", description="Stream from specialist (GET)"),
            EndpointInfo(path="/api/chat/team/stream", method="POST", description="Stream from all specialists"),
            EndpointInfo(path="/ws", method="WEBSOCKET", description="WebSocket for streaming")
        ],
        capabilities=component.get_capabilities() if component else [],
        dependencies={
            "hermes": hermes_url("")
        },
        metadata=component.get_metadata() if component else {}
    )
    return await discovery_check()


# Generate endpoint (simple text generation)
@routers.v1.post("/generate", response_model=GenerateResponse)
@api_contract(
    title="Text Generation API",
    endpoint="/api/v1/generate",
    method="POST",
    request_schema={"prompt": "string", "model": "string", "temperature": "float", "max_tokens": "int"}
)
async def generate(request: GenerateRequest):
    """Generate text from a prompt."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        # Create a unique context ID for this request
        import uuid
        context_id = str(uuid.uuid4())
        
        # Route the request
        result = await component.model_router.route_request(
            message=request.prompt,
            context_id=context_id,
            task_type=request.capability or "reasoning",
            component=request.component,
            system_prompt=request.system_prompt,
            streaming=False,
            override_config={
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "model": request.model
            } if request.model else None
        )
        
        # Extract response from result - it may have 'content' or 'message' key
        response_text = result.get("content") or result.get("message", "")
        
        return GenerateResponse(
            response=response_text,
            model=result.get("model", "unknown"),
            usage=result.get("usage")
        )
        
    except Exception as e:
        logger.error(f"Error processing generate request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Chat endpoints
@routers.v1.post("/chat", response_model=ChatResponse)
@api_contract(
    title="LLM Chat API",
    endpoint="/api/v1/chat",
    method="POST",
    request_schema={"messages": "list", "model": "string", "temperature": "float", "max_tokens": "int", "tools": "list"}
)
@integration_point(
    title="LLM Provider Integration",
    target_component="Multiple LLM providers (OpenAI, Anthropic, etc)",
    protocol="HTTP REST API",
    data_flow="Request -> Model Router -> Provider -> Response"
)
async def chat(request: ChatRequest):
    """Send a chat message to the LLM."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        # Get or create context
        context = None
        if request.context_id:
            context = await component.context_manager.get_context(request.context_id)
            if not context:
                raise HTTPException(status_code=404, detail=f"Context not found: {request.context_id}")
        
        # Extract the last user message for routing
        user_message = ""
        system_prompt = None
        for msg in request.messages:
            if msg["role"] == "user":
                user_message = msg["content"]
            elif msg["role"] == "system":
                system_prompt = msg["content"]
        
        # Create context ID if not provided
        import uuid
        context_id = request.context_id or str(uuid.uuid4())
        
        # Route the request
        result = await component.model_router.route_request(
            message=user_message,
            context_id=context_id,
            task_type=request.capability or "chat",
            component=request.component,
            system_prompt=system_prompt,
            streaming=False,
            override_config={
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "model": request.model
            } if request.model else None
        )
        
        # Update context if provided
        if context:
            await component.context_manager.add_messages(
                request.context_id,
                request.messages + [{"role": "assistant", "content": result["content"]}]
            )
        
        # Extract response from result - it may have 'content' or 'message' key
        response_content = result.get("content") or result.get("message", "")
        
        return ChatResponse(
            content=response_content,
            response=response_content,  # Include for backward compatibility
            model=result.get("model", "unknown"),
            usage=result.get("usage"),
            context_id=context_id,
            metadata=result.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@routers.v1.post("/chat/stream")
@api_contract(
    title="LLM Streaming Chat API",
    endpoint="/api/v1/chat/stream",
    method="POST",
    request_schema={"messages": "list", "model": "string", "stream": "bool"}
)
async def chat_stream(request: ChatRequest):
    """Stream a chat response from the LLM."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    async def generate():
        try:
            # Route the request with streaming
            async for chunk in component.model_router.route_request_stream(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=request.tools,
                tool_choice=request.tool_choice,
                response_format=request.response_format,
                request_metadata=request.request_metadata
            ):
                yield {"data": json.dumps(chunk)}
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield {"data": json.dumps({"error": str(e)})}
    
    return EventSourceResponse(generate())


# Template management endpoints
@routers.v1.get("/templates")
@api_contract(
    title="Template List API",
    endpoint="/api/v1/templates",
    method="GET",
    request_schema={"category": "string (optional)"}
)
async def list_templates(category: Optional[str] = None):
    """List all available templates."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    templates = await component.template_manager.list_templates(category=category)
    return {"templates": templates}


@routers.v1.get("/templates/{name}")
async def get_template(name: str):
    """Get a specific template by name."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    template = await component.template_manager.get_template(name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template not found: {name}")
    return template


@routers.v1.post("/templates")
async def create_template(request: TemplateRequest):
    """Create a new template."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        await component.template_manager.save_template(
            name=request.name,
            content=request.content,
            description=request.description,
            category=request.category,
            tags=request.tags,
            metadata=request.metadata
        )
        return {"message": f"Template '{request.name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@routers.v1.put("/templates/{name}")
async def update_template(name: str, request: TemplateRequest):
    """Update an existing template."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        await component.template_manager.update_template(
            name=name,
            content=request.content,
            description=request.description,
            category=request.category,
            tags=request.tags,
            metadata=request.metadata
        )
        return {"message": f"Template '{name}' updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@routers.v1.delete("/templates/{name}")
async def delete_template(name: str):
    """Delete a template."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        await component.template_manager.delete_template(name)
        return {"message": f"Template '{name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Prompt operations
@routers.v1.post("/prompts/render")
async def render_prompt(request: PromptRequest):
    """Render a prompt using a template."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        result = await component.prompt_engine.render_prompt(
            template_name=request.template_name,
            variables=request.variables or {},
            context_id=request.context_id
        )
        return {"prompt": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Prompt registry endpoints
@routers.v1.get("/registry")
async def list_registry_prompts(category: Optional[str] = None):
    """List all prompts in the registry."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    prompts = component.prompt_registry.list_prompts(category=category)
    return {"prompts": prompts}


@routers.v1.get("/registry/{name}")
async def get_registry_prompt(name: str, version: Optional[str] = None):
    """Get a specific prompt from the registry."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    prompt = component.prompt_registry.get_prompt(name, version=version)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {name}")
    return prompt


@routers.v1.post("/registry")
async def register_prompt(request: PromptRegistryRequest):
    """Register a new prompt."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        component.prompt_registry.register_prompt(
            name=request.name,
            template=request.template,
            description=request.description,
            category=request.category,
            version=request.version,
            tags=request.tags,
            examples=request.examples,
            metadata=request.metadata
        )
        return {"message": f"Prompt '{request.name}' registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Context management endpoints
@routers.v1.post("/context", response_model=Dict[str, str])
async def create_context(request: ContextRequest):
    """Create a new context."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    context_id = await component.context_manager.create_context(
        context_id=request.context_id,
        messages=request.messages,
        max_tokens=request.max_tokens,
        metadata=request.metadata
    )
    return {"context_id": context_id}


@routers.v1.get("/context/{context_id}")
async def get_context(context_id: str):
    """Get context information."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    context = await component.context_manager.get_context(context_id)
    if not context:
        raise HTTPException(status_code=404, detail=f"Context not found: {context_id}")
    return context


@routers.v1.delete("/context/{context_id}")
async def delete_context(context_id: str):
    """Delete a context."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    await component.context_manager.delete_context(context_id)
    return {"message": f"Context '{context_id}' deleted successfully"}


# Model management endpoints
@routers.v1.get("/models")
async def list_models():
    """List available models."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    models = await component.llm_client.list_models()
    return {"models": models}


# Budget management endpoints
@routers.v1.get("/budget/usage")
async def get_budget_usage():
    """Get current budget usage."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    usage = component.budget_manager.get_usage_summary()
    return usage


@routers.v1.post("/budget/policies")
async def create_budget_policy(request: BudgetPolicyRequest):
    """Create a new budget policy."""
    if not component or not component.initialized:
        raise HTTPException(status_code=503, detail="Rhetor not initialized")
    
    try:
        policy_id = component.budget_manager.create_policy(
            name=request.name,
            max_cost=request.max_cost,
            period=request.period,
            description=request.description
        )
        return {"policy_id": policy_id, "message": "Budget policy created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# CI Specialist endpoints are now handled by the unified endpoints in ai_specialist_endpoints_unified.py
# The old internal specialist system has been removed in favor of the CI Registry


# WebSocket endpoint for streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming LLM responses."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if not component or not component.initialized:
                await websocket.send_json({
                    "error": "Rhetor not initialized",
                    "type": "error"
                })
                continue
            
            # Process the request
            try:
                # Validate messages
                messages = data.get("messages", [])
                if not messages:
                    await websocket.send_json({
                        "error": "No messages provided. At least one message is required.",
                        "type": "error"
                    })
                    continue
                
                # Stream the response
                async for chunk in await component.model_router.route_chat_request(
                    messages=messages,
                    context_id=data.get("context_id", "websocket-default"),
                    task_type=data.get("task_type", "chat"),
                    component=data.get("component"),
                    system_prompt=data.get("system_prompt"),
                    streaming=True,
                    override_config={
                        "model": data.get("model"),
                        "options": {
                            "temperature": data.get("temperature"),
                            "max_tokens": data.get("max_tokens")
                        }
                    } if data.get("model") else None
                ):
                    await websocket.send_json(chunk)
                
                # Send completion marker
                await websocket.send_json({
                    "type": "stream_complete"
                })
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({
                    "error": str(e),
                    "type": "error"
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# Mount standard routers
mount_standard_routers(app, routers)


if __name__ == "__main__":
    import uvicorn
    
    global_config = GlobalConfig.get_instance()
    port = global_config.config.rhetor.port
    
    uvicorn.run(app, host="0.0.0.0", port=port)