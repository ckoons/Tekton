"""
FastAPI application for aish MCP server

This module creates the FastAPI application that hosts the aish MCP endpoints,
enabling external systems to interact with aish functionality via HTTP.
"""

import asyncio
import logging
import os
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point
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

# Import and load TektonEnviron for configuration first
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron, TektonEnvironLock

# Add TEKTON_ROOT to path if needed
tekton_root = TektonEnviron.get('TEKTON_ROOT')
if tekton_root and tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# Load environment if running standalone
if __name__ == "__main__":
    TektonEnvironLock.load()

# Import the MCP router
sys.path.insert(0, str(Path(__file__).parent.parent))
from mcp.server import mcp_router

# Setup logging
logger = logging.getLogger(__name__)


@asynccontextmanager
@integration_point(
    title="MCP Server Lifecycle Manager",
    description="Manages startup and graceful shutdown of MCP server",
    target_component="FastAPI",
    protocol="ASGI",
    data_flow="startup → yield app → shutdown",
    integration_date="2025-01-18"
)
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # Startup
    logger.info("Starting aish MCP server")
    yield
    # Shutdown
    logger.info("Shutting down aish MCP server")


# Create FastAPI app
app = FastAPI(
    title="aish MCP Server",
    description="Model Context Protocol server for aish shell/messaging tools",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - allow Tekton UI components to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
        # Add specific Tekton component ports if needed
        f"http://localhost:{TektonEnviron.get('HEPHAESTUS_PORT', '8080')}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the MCP router
app.include_router(mcp_router)

# Root endpoint
@app.get("/")
@api_contract(
    title="MCP Server Root",
    description="Service discovery endpoint",
    endpoint="/",
    method="GET",
    request_schema={},
    response_schema={"service": "string", "version": "string", "description": "string", "mcp_endpoint": "string"},
    performance_requirements="<10ms response time"
)
async def root():
    """Root endpoint - provides basic service information"""
    return {
        "service": "aish-mcp",
        "version": "1.0.0",
        "description": "aish Model Context Protocol server",
        "mcp_endpoint": "/api/mcp/v2/capabilities"
    }


@architecture_decision(
    title="Threaded MCP Server",
    description="Run MCP server in separate thread from main aish process",
    rationale="Allows aish shell to remain responsive while MCP server handles HTTP requests",
    alternatives_considered=["Subprocess", "Single process with async", "Separate daemon"],
    impacts=["process_management", "resource_sharing", "debugging"],
    decided_by="Casey",
    decision_date="2025-01-18"
)
def start_mcp_server():
    """
    Start the MCP server - designed to be run in a thread
    """
    import sys
    import os
    print(f"[MCP] Thread starting...", file=sys.stderr)
    
    # Ensure environment is loaded when running in thread
    try:
        from shared.env import TektonEnvironLock, TektonEnviron
        TektonEnvironLock.load()
    except Exception as e:
        print(f"[MCP] TektonEnvironLock.load() error: {e}", file=sys.stderr)
    
    # Ensure we have the right paths
    tekton_root = TektonEnviron.get('TEKTON_ROOT')
    if tekton_root and tekton_root not in sys.path:
        sys.path.insert(0, tekton_root)
    
    # Get port from environment
    port = int(TektonEnviron.get("AISH_MCP_PORT", "3100"))
    
    print(f"[MCP] Starting aish MCP server on port {port}", file=sys.stderr)
    print(f"[MCP] sys.path[0] = {sys.path[0]}", file=sys.stderr)
    
    try:
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="warning",  # Reduce logging
            # Disable access logs to avoid cluttering aish CLI output
            access_log=False
        )
    except Exception as e:
        print(f"[MCP] Server failed to start: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def start_mcp_server_thread():
    """
    Start MCP server in a background thread
    """
    if TektonEnviron.get('AISH_NO_MCP'):
        logger.info("AISH_NO_MCP set, skipping MCP server startup")
        return None
    
    def run_server():
        try:
            start_mcp_server()
        except Exception as e:
            print(f"[MCP] Thread exception: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
    mcp_thread = threading.Thread(target=run_server, daemon=True, name="aish-mcp-server")
    mcp_thread.start()
    print(f"[MCP] Started thread: {mcp_thread.name}, alive: {mcp_thread.is_alive()}", file=sys.stderr)
    return mcp_thread


if __name__ == "__main__":
    # For testing - normally started by aish main script
    # Load environment when running standalone
    TektonEnvironLock.load()
    import asyncio
    start_mcp_server()