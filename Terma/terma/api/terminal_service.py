#!/usr/bin/env python3
"""
Terma Service - Native Terminal Orchestrator for Tekton

Complete replacement for old Terma. Launches and manages native terminal 
applications with aish-proxy. No web terminals, no PTY sessions.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import our terminal launcher
from core.terminal_launcher import TerminalLauncher, TerminalConfig, TerminalTemplates

# Use shared logging if available
try:
    from shared.utils.logging_setup import setup_component_logging
    logger = setup_component_logging("terma")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("terma")


# Pydantic models
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
    """Response with list of terminals."""
    terminals: List[TerminalInfo]
    count: int


class TerminalTypeInfo(BaseModel):
    """Information about available terminal type."""
    id: str
    display_name: str
    is_default: bool


class TemplateInfo(BaseModel):
    """Terminal template information."""
    name: str
    description: str
    purpose: Optional[str] = None
    env: Dict[str, str]


class AITerminalRequest(BaseModel):
    """Request from AI component to launch a terminal."""
    requester_id: str = Field(..., description="ID of requesting AI component")
    purpose: str = Field(..., description="Purpose of terminal request")
    context: Optional[str] = Field(None, description="Additional context")
    working_dir: Optional[str] = Field(None, description="Working directory")
    terminal_app: Optional[str] = Field(None, description="Preferred terminal app")
    initial_commands: Optional[List[str]] = Field(None, description="Commands to run on startup")


# Create FastAPI app
app = FastAPI(
    title="Terma Terminal Orchestrator",
    description="Native terminal launcher for Tekton - manages Terminal.app, iTerm2, Warp, etc. with aish-proxy",
    version="2.0.0"
)

# Add CORS middleware for Hephaestus UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global terminal launcher instance
launcher: Optional[TerminalLauncher] = None


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    global launcher
    
    logger.info("🚀 Starting Terma Terminal Orchestrator v2.0.0")
    
    # Initialize terminal launcher
    try:
        launcher = TerminalLauncher()
        logger.info(f"✅ Terminal launcher initialized")
        logger.info(f"   Platform: {launcher.platform}")
        logger.info(f"   Default terminal: {launcher.get_default_terminal()}")
        logger.info(f"   Available terminals: {len(launcher.available_terminals)}")
        
        # Log available terminals
        for app_id, display_name in launcher.available_terminals:
            logger.info(f"   - {app_id}: {display_name}")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize terminal launcher: {e}")
        raise
    
    # Register with Hermes if enabled
    if os.environ.get("REGISTER_WITH_HERMES", "true").lower() == "true":
        await register_with_hermes()


async def register_with_hermes():
    """Register this service with Hermes for discovery."""
    try:
        import httpx
        
        # Get configuration
        hermes_url = os.environ.get("HERMES_URL", "http://localhost:8001")
        service_port = int(os.environ.get("TERMA_PORT", "8004"))
        
        registration = {
            "name": "terma",
            "url": f"http://localhost:{service_port}",
            "port": service_port,
            "version": "2.0.0",
            "description": "Native terminal orchestrator with aish integration",
            "capabilities": [
                "terminal-launch",
                "terminal-management",
                "aish-integration",
                "multi-platform",
                "pid-tracking"
            ],
            "health_check_path": "/health",
            "metadata": {
                "platform": launcher.platform if launcher else "unknown",
                "terminals": len(launcher.available_terminals) if launcher else 0,
                "default_terminal": launcher.get_default_terminal() if launcher else "unknown"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{hermes_url}/api/v1/services/register",
                json=registration,
                timeout=5.0
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Registered with Hermes at {hermes_url}")
            else:
                logger.warning(f"⚠️  Hermes registration returned {response.status_code}")
                
    except Exception as e:
        logger.warning(f"⚠️  Could not register with Hermes: {e}")
        logger.info("   Running standalone (Hermes integration disabled)")


# Health and discovery endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Terma Terminal Orchestrator",
        "version": "2.0.0",
        "description": "Native terminal launcher for Tekton"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "terma",
        "version": "2.0.0",
        "launcher_ready": launcher is not None,
        "platform": launcher.platform if launcher else None,
        "terminals_available": len(launcher.available_terminals) if launcher else 0
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    if not launcher:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Terminal launcher not initialized"
        )
    return {"ready": True}


@app.get("/discovery")
async def service_discovery():
    """Service discovery endpoint for other Tekton components."""
    return {
        "name": "terma",
        "version": "2.0.0",
        "description": "Native terminal orchestrator",
        "port": int(os.environ.get("TERMA_PORT", "8004")),
        "capabilities": [
            "terminal-launch",
            "terminal-management",
            "aish-integration",
            "multi-platform"
        ],
        "api_endpoints": {
            "terminals": "/api/terminals",
            "types": "/api/terminals/types",
            "templates": "/api/terminals/templates",
            "launch": "/api/terminals/launch",
            "ai_request": "/api/terminals/ai-request"
        }
    }


# Terminal type and template endpoints
@app.get("/api/terminals/types", response_model=List[TerminalTypeInfo])
async def list_terminal_types():
    """List available terminal types on this platform."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    terminals = []
    default_terminal = launcher.get_default_terminal()
    
    for app_id, display_name in launcher.available_terminals:
        terminals.append(TerminalTypeInfo(
            id=app_id,
            display_name=display_name,
            is_default=(app_id == default_terminal)
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
            purpose=template.purpose,
            env=template.env
        )
    
    return templates


# Terminal management endpoints
@app.post("/api/terminals/launch", response_model=TerminalInfo)
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
        
        return TerminalInfo(
            pid=pid,
            app=terminal_info.terminal_app,
            status=terminal_info.status,
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


@app.get("/api/terminals", response_model=TerminalListResponse)
async def list_terminals():
    """List all tracked terminals."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    terminals = launcher.list_terminals()
    
    responses = [
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
    
    return TerminalListResponse(
        terminals=responses,
        count=len(responses)
    )


@app.get("/api/terminals/{pid}", response_model=TerminalInfo)
async def get_terminal(pid: int):
    """Get information about a specific terminal."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    terminal_info = launcher.terminals.get(pid)
    if not terminal_info:
        raise HTTPException(
            status_code=404,
            detail=f"Terminal with PID {pid} not found"
        )
    
    # Update status
    if not launcher.is_terminal_running(pid):
        terminal_info.status = "stopped"
    
    return TerminalInfo(
        pid=pid,
        app=terminal_info.terminal_app,
        status=terminal_info.status,
        launched_at=terminal_info.launched_at,
        purpose=terminal_info.config.purpose,
        working_dir=terminal_info.config.working_dir,
        name=terminal_info.config.name
    )


@app.post("/api/terminals/{pid}/show")
async def show_terminal(pid: int):
    """Bring terminal to foreground (macOS only)."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    if launcher.platform != "darwin":
        raise HTTPException(
            status_code=400,
            detail="Show terminal only supported on macOS"
        )
    
    success = launcher.show_terminal(pid)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Could not show terminal {pid}"
        )
    
    return {"status": "success", "pid": pid}


@app.delete("/api/terminals/{pid}")
async def terminate_terminal(pid: int):
    """Terminate a terminal."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    success = launcher.terminate_terminal(pid)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Could not terminate terminal {pid}"
        )
    
    logger.info(f"Terminated terminal PID: {pid}")
    
    return {"status": "terminated", "pid": pid}


@app.post("/api/terminals/cleanup")
async def cleanup_stopped_terminals():
    """Remove stopped terminals from tracking."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    before_count = len(launcher.terminals)
    launcher.cleanup_stopped()
    after_count = len(launcher.terminals)
    
    cleaned = before_count - after_count
    logger.info(f"Cleaned up {cleaned} stopped terminals")
    
    return {
        "cleaned": cleaned,
        "remaining": after_count
    }


# AI Terminal Request endpoint
@app.post("/api/terminals/ai-request", response_model=TerminalInfo)
async def ai_terminal_request(request: AITerminalRequest):
    """Handle terminal requests from AI components."""
    if not launcher:
        raise HTTPException(status_code=500, detail="Launcher not initialized")
    
    logger.info(f"AI terminal request from {request.requester_id}: {request.purpose}")
    
    # Create AI-specific configuration
    config = TerminalConfig(
        name=f"AI Terminal - {request.requester_id}",
        app=request.terminal_app,
        working_dir=request.working_dir,
        purpose=request.purpose,
        env={
            "TEKTON_AI_CONTEXT": request.context or "",
            "TEKTON_AI_PURPOSE": request.purpose,
            "TEKTON_AI_REQUESTER": request.requester_id,
            "AISH_AI_MODE": "true"
        }
    )
    
    try:
        # Launch terminal
        pid = launcher.launch_terminal(config)
        
        # TODO: Handle initial_commands injection
        # This would require enhancement to aish-proxy to accept initial commands
        
        terminal_info = launcher.terminals.get(pid)
        if not terminal_info:
            raise HTTPException(status_code=500, detail="Terminal launched but not tracked")
        
        logger.info(f"✅ AI terminal launched with PID: {pid} for {request.requester_id}")
        
        return TerminalInfo(
            pid=pid,
            app=terminal_info.terminal_app,
            status=terminal_info.status,
            launched_at=terminal_info.launched_at,
            purpose=terminal_info.config.purpose,
            working_dir=terminal_info.config.working_dir,
            name=terminal_info.config.name
        )
        
    except Exception as e:
        logger.error(f"Failed to launch AI terminal: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to launch AI terminal: {str(e)}"
        )


def main():
    """Run the Terma service."""
    # Get configuration
    port = int(os.environ.get("TERMA_PORT", "8004"))
    host = os.environ.get("TERMA_HOST", "0.0.0.0")
    
    print(f"Starting Terma Terminal Orchestrator on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()