"""FastAPI application for Terma"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint, performance_boundary
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(name, description, sla, rationale=""):
        def decorator(func):
            return func
        return decorator

# Add parent directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Add Tekton root to path for shared imports
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import uvicorn

# Import native terminal launcher
from ..core.terminal_launcher import TerminalLauncher, TerminalConfig, TerminalTemplates
# from ..integrations.hermes_integration import HermesIntegration  # Replaced with shared registration
from .fastmcp_endpoints import mcp_router

# Use shared logging setup
from shared.utils.logging_setup import setup_component_logging
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop

logger = setup_component_logging("terma")

# Models for native terminal launching
class LaunchTerminalRequest(BaseModel):
    """Request to launch a new terminal."""
    template: Optional[str] = Field(None, description="Template name to use")
    app: Optional[str] = Field(None, description="Terminal application to use")
    working_dir: Optional[str] = Field(None, description="Working directory")
    purpose: Optional[str] = Field(None, description="Purpose/context for AI")
    env: Optional[Dict[str, str]] = Field(default_factory=dict, description="Environment variables")
    name: Optional[str] = Field(None, description="Terminal name")

class TerminalInfo(BaseModel):
    """Information about a terminal."""
    pid: int
    app: str
    status: str
    launched_at: datetime
    purpose: Optional[str] = None
    working_dir: Optional[str] = None
    name: Optional[str] = None

class TerminalListResponse(BaseModel):
    """Response for listing terminals."""
    terminals: List[TerminalInfo]
    count: int

class TerminalTypeInfo(BaseModel):
    """Information about a terminal type."""
    id: str
    name: str
    available: bool
    path: Optional[str] = None

class TemplateInfo(BaseModel):
    """Information about a terminal template."""
    name: str
    description: str
    app: Optional[str] = None
    shell: Optional[str] = None
    purpose: Optional[str] = None

class HealthResponse(BaseModel):
    """Model for health response"""
    status: str
    uptime: float
    version: str
    active_sessions: int

class StatusResponse(BaseModel):
    """Model for status response"""
    status: str

class HermesMessage(BaseModel):
    """Model for Hermes message"""
    id: str
    source: str
    target: str
    command: str
    timestamp: float
    payload: Dict[str, Any]

class HermesEvent(BaseModel):
    """Model for Hermes event"""
    event: str
    source: str
    timestamp: float
    payload: Dict[str, Any]

# Lifespan handler for startup and shutdown
@architecture_decision(
    title="Terma Lifespan Management",
    decision="Use FastAPI lifespan for service registration and cleanup",
    rationale="Ensures proper service registration and cleanup, maintains health status with Hermes",
    alternatives_considered=["Manual startup/shutdown", "Separate service manager"],
    decision_date="2025-07-09"
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    global launcher, hermes_registration
    
    # Startup
    launcher = TerminalLauncher()
    logger.info("Terminal launcher initialized")
    
    # Register with Hermes
    hermes_url = os.environ.get("HERMES_URL", "http://localhost:8001")
    hermes_registration = HermesRegistration(hermes_url)
    
    from tekton.utils.port_config import get_terma_port
    port = get_terma_port()
    
    registration_success = await hermes_registration.register_component(
        component_name="terma",
        port=port,
        version=VERSION,
        capabilities=[
            "terminal_launch",
            "terminal_management", 
            "native_terminals",
            "aish_integration"
        ],
        metadata={
            "description": "Terminal Orchestrator",
            "type": "terminal_manager",
            "responsibilities": [
                "Launch native terminal applications",
                "Integrate with aish AI-enhanced shell",
                "Manage terminal sessions and lifecycle"
            ]
        }
    )
    
    if registration_success:
        logger.info("✅ Terma registered with Hermes")
        # Start heartbeat loop
        asyncio.create_task(heartbeat_loop(hermes_registration, "terma"))
    else:
        logger.warning("⚠️ Failed to register with Hermes")
    
    yield
    
    # Shutdown
    if launcher:
        launcher.cleanup_stopped()
        logger.info("Terminal launcher cleaned up")
    if hermes_registration:
        await hermes_registration.deregister("terma")

# Application
app = FastAPI(
    title="Terma Terminal API", 
    description="API for Terma terminal services",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include MCP router
app.include_router(mcp_router, tags=["mcp"])

# Application startup time
START_TIME = time.time()
VERSION = "0.1.0"

# Global instances
launcher: Optional[TerminalLauncher] = None
hermes_registration: Optional[HermesRegistration] = None



@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Terma Terminal API", "version": VERSION}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - START_TIME
    
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": VERSION,
        "active_sessions": 0
    }

# Native Terminal Management Endpoints

@app.get("/api/terminals/types", response_model=List[TerminalTypeInfo])
async def list_terminal_types():
    """List available terminal types on this platform."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    terminals = []
    default_terminal = launcher.get_default_terminal()
    
    for app_id, display_name, _ in launcher.available_terminals:
        terminals.append(TerminalTypeInfo(
            id=app_id,
            name=display_name,
            available=True,
            path=None
        ))
    
    return terminals


@app.get("/api/terminals/templates", response_model=Dict[str, TemplateInfo])
async def list_templates():
    """List available terminal configuration templates."""
    templates = {}
    
    for name, template in TerminalTemplates.DEFAULT_TEMPLATES.items():
        templates[name] = TemplateInfo(
            name=template.name,
            description=f"Template: {name}",
            app=template.app,
            shell=template.shell,
            purpose=template.purpose
        )
    
    return templates


@app.post("/api/terminals/launch", response_model=TerminalInfo)
@integration_point(
    title="Terminal Launch Bridge", 
    target_component="terminal_launcher_impl",
    protocol="HTTP POST to native process launch",
    data_flow="API request → TerminalConfig → Native terminal with aish-proxy",
    integration_date="2025-07-09"
)
async def launch_terminal(request: LaunchTerminalRequest):
    """Launch a new native terminal with specified configuration."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    try:
        # Create configuration
        if request.template:
            config = TerminalTemplates.get_template(request.template)
            if not config:
                raise HTTPException(
                    status_code=400,
                    detail=f"Template '{request.template}' not found"
                )
        else:
            config = TerminalConfig()
        
        # Apply request parameters
        if request.name:
            config.name = request.name
        if request.app:
            config.app = request.app
        if request.working_dir:
            config.working_dir = request.working_dir
        if request.purpose:
            config.purpose = request.purpose
        if request.env:
            config.env.update(request.env)
        
        # Launch terminal
        logger.info(f"Launching terminal: {config.app or launcher.get_default_terminal()}")
        pid = launcher.launch_terminal(config)
        
        # Get terminal info
        terminal_info = launcher.terminals.get(pid)
        if not terminal_info:
            raise HTTPException(status_code=500, detail="Terminal launched but not tracked")
        
        logger.info(f"✅ Terminal launched with PID: {pid}")
        
        # Add note about aish-proxy status
        status_msg = terminal_info.status
        if not launcher.aish_path:
            status_msg = "running (without aish-proxy)"
        
        return TerminalInfo(
            pid=pid,
            app=terminal_info.terminal_app,
            status=status_msg,
            launched_at=terminal_info.launched_at,
            purpose=terminal_info.config.purpose,
            working_dir=terminal_info.config.working_dir,
            name=terminal_info.config.name
        )
        
    except Exception as e:
        logger.error(f"Failed to launch terminal: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to launch terminal: {str(e)}"
        )


@app.get("/api/terminals", response_model=List[TerminalInfo])
async def list_terminals():
    """List all tracked terminals."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    terminals = launcher.list_terminals()
    
    return [
        TerminalInfo(
            pid=info.pid,
            app=info.terminal_app,
            status=info.status,
            launched_at=info.launched_at,
            purpose=info.config.purpose,
            working_dir=info.config.working_dir,
            name=info.config.name
        )
        for info in terminals
    ]


# Hermes message handling endpoints
@app.post("/api/hermes/message", response_model=Dict[str, Any])
@integration_point(
    title="Hermes Message Handler",
    target_component="hermes",
    protocol="HTTP POST /api/hermes/message",
    data_flow="Hermes → Terma message processing",
    integration_date="2025-07-09"
)
async def hermes_message(message: HermesMessage):
    """Handle message from Hermes"""
    logger.info(f"Received message from Hermes: {message.command}")
    # For now, just acknowledge - TODO: implement actual message handling
    return {"status": "received", "command": message.command}

@app.post("/api/events", response_model=StatusResponse)
async def handle_event(event: HermesEvent):
    """Handle event from Hermes"""
    logger.info(f"Received event from Hermes: {event.event}")
    # Just acknowledge the event for now
    return {"status": "success"}

# LLM Model API Endpoints
class LLMProvidersResponse(BaseModel):
    """Model for LLM providers response"""
    providers: Dict[str, Any]
    current_provider: str
    current_model: str

class LLMModelsResponse(BaseModel):
    """Model for LLM models response"""
    models: List[Dict[str, str]]
    current_model: str

class LLMSetRequest(BaseModel):
    """Model for setting LLM provider and model"""
    provider: str
    model: str

@app.get("/api/llm/providers", response_model=LLMProvidersResponse)
async def get_llm_providers():
    """Get available LLM providers and models"""
    from ..core.llm_adapter import LLMAdapter
    import aiohttp

    # Create LLM adapter
    llm_adapter = LLMAdapter()
    
    try:
        # Check if LLM Adapter service is available
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{llm_adapter.adapter_url}/health", timeout=2.0) as response:
                if response.status == 200:
                    # Get providers from LLM Adapter
                    providers = await llm_adapter.get_available_providers()
                    current_provider, current_model = llm_adapter.get_current_provider_and_model()
                    
                    return {
                        "providers": providers,
                        "current_provider": current_provider,
                        "current_model": current_model
                    }
    except Exception as e:
        logger.warning(f"Error connecting to LLM Adapter service: {e}")
    
    # Fallback to default values if LLM Adapter is not available
    providers = await llm_adapter.get_available_providers() # This will fallback to config
    current_provider, current_model = llm_adapter.get_current_provider_and_model()
    
    return {
        "providers": providers,
        "current_provider": current_provider,
        "current_model": current_model
    }

@app.get("/api/llm/models/{provider_id}", response_model=LLMModelsResponse)
async def get_llm_models(provider_id: str):
    """Get models for a specific LLM provider"""
    from ..core.llm_adapter import LLMAdapter
    from ..utils.config import LLM_PROVIDERS
    
    # Check if the provider exists
    if provider_id not in LLM_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
    
    llm_adapter = LLMAdapter()
    current_provider, current_model = llm_adapter.get_current_provider_and_model()
    models = LLM_PROVIDERS[provider_id]["models"]
    
    return {
        "models": models,
        "current_model": current_model if current_provider == provider_id else ""
    }

@app.post("/api/llm/set", response_model=StatusResponse)
async def set_llm_provider_model(request: LLMSetRequest):
    """Set the LLM provider and model"""
    from ..core.llm_adapter import LLMAdapter
    from ..utils.config import LLM_PROVIDERS
    
    # Check if the provider exists
    if request.provider not in LLM_PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider {request.provider} not found")
    
    # Check if the model exists for this provider
    provider_models = [m["id"] for m in LLM_PROVIDERS[request.provider]["models"]]
    if request.model not in provider_models:
        raise HTTPException(status_code=404, detail=f"Model {request.model} not found for provider {request.provider}")
    
    # Set the provider and model
    llm_adapter = LLMAdapter()
    llm_adapter.set_provider_and_model(request.provider, request.model)
    
    return {"status": "success"}


# Server startup function
async def start_server(host: str = "0.0.0.0", port: int = None):
    """Start the Terma Terminal Orchestrator API server
    
    Args:
        host: Host to bind to
        port: Port to bind the API server to (defaults to Terma's standard port)
    """
    import uvicorn
    
    # Set default port using centralized config
    if port is None:
        from tekton.utils.port_config import get_terma_port
        port = get_terma_port()
        logger.info(f"Using Terma port: {port}")
    
    logger.info(f"Starting Terma Terminal Orchestrator API on {host}:{port}")
    
    # Start the FastAPI server
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    """Run the server when executed directly"""
    import sys
    
    # Get port from command line if provided
    port = None
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    
    # Run the server
    asyncio.run(start_server(port=port))