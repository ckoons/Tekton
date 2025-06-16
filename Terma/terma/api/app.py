"""FastAPI application for Terma"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any

# Add parent directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Add Tekton root to path for shared imports
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from fastapi import FastAPI, WebSocket, HTTPException, Depends, WebSocketDisconnect, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..core.session_manager import SessionManager
from .websocket import TerminalWebSocketServer
from ..integrations.hermes_integration import HermesIntegration
from .fastmcp_endpoints import mcp_router

# Use shared logging setup
from shared.utils.logging_setup import setup_component_logging
logger = setup_component_logging("terma")

# Models
class SessionCreate(BaseModel):
    """Model for session creation request"""
    shell_command: Optional[str] = None

class SessionResponse(BaseModel):
    """Model for session response"""
    session_id: str
    created_at: float

class SessionInfo(BaseModel):
    """Model for session information"""
    id: str
    active: bool
    created_at: float
    last_activity: float
    shell_command: str
    idle_time: float

class SessionsResponse(BaseModel):
    """Model for sessions list response"""
    sessions: List[SessionInfo]

class WriteRequest(BaseModel):
    """Model for write request"""
    data: str

class WriteResponse(BaseModel):
    """Model for write response"""
    status: str
    bytes_written: int

class ReadResponse(BaseModel):
    """Model for read response"""
    data: str

class StatusResponse(BaseModel):
    """Model for status response"""
    status: str

class HealthResponse(BaseModel):
    """Model for health response"""
    status: str
    uptime: float
    version: str
    active_sessions: int

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

# Application
app = FastAPI(title="Terma Terminal API", description="API for Terma terminal services")

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

# Dependency for session manager
def get_session_manager():
    """Get or create the session manager"""
    if not hasattr(app.state, "session_manager"):
        app.state.session_manager = SessionManager()
        app.state.session_manager.start()
    return app.state.session_manager

# Dependency for websocket server
def get_websocket_server():
    """Get or create the WebSocket server"""
    if not hasattr(app.state, "websocket_server"):
        app.state.websocket_server = TerminalWebSocketServer(get_session_manager())
    return app.state.websocket_server

# Dependency for Hermes integration
def get_hermes_integration():
    """Get or create the Hermes integration"""
    if not hasattr(app.state, "hermes_integration"):
        from tekton.utils.port_config import get_hermes_url, get_terma_port
        hermes_url = get_hermes_url()
        app.state.hermes_integration = HermesIntegration(
            api_url=hermes_url,
            session_manager=get_session_manager(),
            component_name="Terma"
        )
    return app.state.hermes_integration

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    # Start session manager
    session_manager = get_session_manager()
    logger.info("Session manager started")
    
    # Register with Hermes if REGISTER_WITH_HERMES environment variable is set
    if os.environ.get("REGISTER_WITH_HERMES", "false").lower() == "true":
        hermes_integration = get_hermes_integration()
        success = hermes_integration.register_capabilities()
        if success:
            logger.info("Registered with Hermes successfully")
        else:
            logger.warning("Failed to register with Hermes")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    # Stop session manager
    if hasattr(app.state, "session_manager"):
        app.state.session_manager.stop()
        logger.info("Session manager stopped")
        
    # Stop websocket server
    if hasattr(app.state, "websocket_server"):
        app.state.websocket_server.stop_server()
        logger.info("WebSocket server stopped")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Terma Terminal API", "version": VERSION}

@app.get("/health", response_model=HealthResponse)
async def health_check(session_manager: SessionManager = Depends(get_session_manager)):
    """Health check endpoint"""
    uptime = time.time() - START_TIME
    active_sessions = len(session_manager.sessions)
    
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": VERSION,
        "active_sessions": active_sessions
    }

# Session management endpoints
@app.get("/api/sessions", response_model=SessionsResponse)
async def list_sessions(session_manager: SessionManager = Depends(get_session_manager)):
    """List all active terminal sessions"""
    sessions = session_manager.list_sessions()
    return {"sessions": sessions}

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(
    session_create: SessionCreate = Body(...),
    session_manager: SessionManager = Depends(get_session_manager),
    hermes_integration: HermesIntegration = Depends(get_hermes_integration)
):
    """Create a new terminal session"""
    session_id = session_manager.create_session(shell_command=session_create.shell_command)
    if not session_id:
        raise HTTPException(status_code=500, detail="Failed to create session")
        
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=500, detail="Session created but not found")
    
    # Publish event to Hermes
    if hermes_integration.is_registered:
        event_payload = {
            "session_id": session_id,
            "shell_command": session_create.shell_command,
            "created_at": session.created_at
        }
        asyncio.create_task(hermes_integration.publish_event("terminal.session.created", event_payload))
        
    return {"session_id": session_id, "created_at": session.created_at}

@app.get("/api/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get information about a terminal session"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    return session.get_info()

@app.delete("/api/sessions/{session_id}", response_model=StatusResponse)
async def close_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
    hermes_integration: HermesIntegration = Depends(get_hermes_integration)
):
    """Close a terminal session"""
    success = session_manager.close_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Publish event to Hermes
    if hermes_integration.is_registered:
        event_payload = {
            "session_id": session_id,
            "closed_at": time.time()
        }
        asyncio.create_task(hermes_integration.publish_event("terminal.session.closed", event_payload))
        
    return {"status": "success"}

# Terminal I/O endpoints
@app.post("/api/sessions/{session_id}/write", response_model=WriteResponse)
async def write_to_session(
    session_id: str,
    write_request: WriteRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Write data to a terminal session"""
    success = session_manager.write_to_session(session_id, write_request.data)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    return {"status": "success", "bytes_written": len(write_request.data)}

@app.get("/api/sessions/{session_id}/read", response_model=ReadResponse)
async def read_from_session(
    session_id: str,
    size: int = Query(1024, description="Maximum size to read"),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Read data from a terminal session"""
    data = session_manager.read_from_session(session_id, size)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    return {"data": data or ""}

# Hermes integration endpoints
@app.post("/api/hermes/message", response_model=Dict[str, Any])
async def hermes_message(
    message: HermesMessage,
    hermes_integration: HermesIntegration = Depends(get_hermes_integration)
):
    """Handle message from Hermes"""
    logger.info(f"Received message from Hermes: {message.command}")
    
    # Handle the message
    response = await hermes_integration.handle_message(message.model_dump())
    return response

@app.post("/api/events", response_model=StatusResponse)
async def handle_event(
    event: HermesEvent,
    hermes_integration: HermesIntegration = Depends(get_hermes_integration)
):
    """Handle event from Hermes"""
    logger.info(f"Received event from Hermes: {event.event}")
    
    # Just acknowledge the event for now
    # In the future, we could handle specific events here
    return {"status": "success"}

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    websocket_server: TerminalWebSocketServer = Depends(get_websocket_server)
):
    """WebSocket endpoint for terminal communication"""
    await websocket_server.handle_connection(websocket, f"/ws/{session_id}")

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

# Terminal launcher endpoint
@app.get("/terminal/launch")
async def launch_terminal(
    session_id: str = Query(..., description="Session ID to connect to"),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Launch a standalone terminal for a session"""
    # Check if session exists
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Return HTML for the standalone terminal
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terma Terminal - Session {session_id}</title>
        <link rel="stylesheet" href="/ui/css/terma-terminal.css">
        <script src="https://cdn.jsdelivr.net/npm/xterm@5.1.0/lib/xterm.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.7.0/lib/xterm-addon-fit.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.8.0/lib/xterm-addon-web-links.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/xterm-addon-search@0.12.0/lib/xterm-addon-search.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.7.0/build/highlight.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.7.0/build/styles/github-dark.min.css">
        <script>
            // Session ID from server
            const SESSION_ID = "{session_id}";
            
            // Configure marked options
            document.addEventListener('DOMContentLoaded', function() {{
                if (typeof marked !== 'undefined') {{
                    marked.setOptions({{
                        highlight: function(code, lang) {{
                            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                            return hljs.highlight(code, {{ language }}).value;
                        }},
                        langPrefix: 'hljs language-',
                        gfm: true,
                        breaks: true
                    }});
                }}
            }});
        </script>
        <script src="/ui/js/terma-terminal.js"></script>
    </head>
    <body>
        <div class="terma-standalone-container">
            <div class="terma-header">
                <div class="terma-title">Terma Terminal - Session {session_id}</div>
                <div class="terma-controls">
                    <select id="terma-llm-provider" class="terma-select" title="LLM Provider">
                        <!-- To be populated by JS -->
                    </select>
                    <select id="terma-llm-model" class="terma-select" title="LLM Model">
                        <!-- To be populated by JS -->
                    </select>
                    <button id="terma-settings-btn" class="terma-btn" title="Terminal Settings">⚙</button>
                </div>
            </div>
            <div class="terma-content">
                <div id="terma-terminal" class="terma-terminal"></div>
            </div>
        </div>
        
        <!-- Terminal Settings Modal -->
        <div id="terma-settings-modal" class="terma-modal">
            <div class="terma-modal-content">
                <div class="terma-modal-header">
                    <h2>Terminal Settings</h2>
                    <button id="terma-settings-close" class="terma-modal-close">&times;</button>
                </div>
                <div class="terma-modal-body">
                    <!-- Settings content copied from terma-component.html -->
                </div>
                <div class="terma-modal-footer">
                    <button id="terma-settings-save" class="terma-btn terma-btn-primary">Save Settings</button>
                    <button id="terma-settings-reset" class="terma-btn">Reset to Defaults</button>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

# Server startup function
async def start_server(host: str = "0.0.0.0", port: int = None, ws_port: int = None):
    """Start the FastAPI server and WebSocket server
    
    Args:
        host: Host to bind to
        port: Port to bind the API server to (defaults to Terma's standard port)
        ws_port: Port to bind the WebSocket server to (defaults to None, which disables the WebSocket server)
    """
    import uvicorn
    import logging
    logger = logging.getLogger("terma")
    
    # Use environment variables for port configuration
    import os

    # Set default port using centralized config
    if port is None:
        from tekton.utils.port_config import get_terma_port
        port = get_terma_port()
        logger.info(f"Using Terma port: {port}")

    # Always check for WebSocket port in environment variables first
    if ws_port is None:
        # Use environment or disable WebSocket server
        # Add import for get_component_config
        from shared.utils.env_config import get_component_config
        config = get_component_config()
        ws_port = config.terma.ws_port if hasattr(config, 'terma') else (int(os.environ.get("TERMA_WS_PORT")) if os.environ.get("TERMA_WS_PORT") else None)
        if ws_port:
            logger.info(f"Using WebSocket port {ws_port} from environment")
        else:
            logger.info("WebSocket server disabled (no TERMA_WS_PORT configured)")
    
    # Only start the WebSocket server if a port is available
    if ws_port is not None:
        logger.debug(f"Starting WebSocket server on {host}:{ws_port}")
        websocket_server = get_websocket_server()
        
        # Check if port is already in use
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((host, ws_port))
        s.close()
        
        if result == 0:
            logger.warning(f"WebSocket port {ws_port} is already in use - WebSocket server may not start correctly")
        
        # Start the WebSocket server in a background task
        asyncio.create_task(websocket_server.start_server(host, ws_port))
    else:
        logger.debug("WebSocket server initialization skipped (ws_port not specified)")
    
    # Start the FastAPI server
    logger.debug(f"Starting FastAPI server on {host}:{port}")
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()