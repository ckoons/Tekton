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

# Add TEKTON_ROOT to path if needed
tekton_root = os.environ.get('TEKTON_ROOT')
if tekton_root and tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import and load TektonEnviron for configuration
from shared.env import TektonEnviron, TektonEnvironLock
# Load environment if running standalone
if __name__ == "__main__":
    TektonEnvironLock.load()

# Import the MCP router
sys.path.insert(0, str(Path(__file__).parent.parent))
from mcp.server import mcp_router

# Setup logging
logger = logging.getLogger(__name__)


@asynccontextmanager
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
async def root():
    """Root endpoint - provides basic service information"""
    return {
        "service": "aish-mcp",
        "version": "1.0.0",
        "description": "aish Model Context Protocol server",
        "mcp_endpoint": "/api/mcp/v2/capabilities"
    }


def start_mcp_server():
    """
    Start the MCP server - designed to be run in a thread
    """
    import sys
    import os
    print(f"[MCP] Thread starting...", file=sys.stderr)
    
    # Ensure we have the right paths
    if os.environ.get('TEKTON_ROOT') and os.environ['TEKTON_ROOT'] not in sys.path:
        sys.path.insert(0, os.environ['TEKTON_ROOT'])
    
    # Ensure environment is loaded when running in thread
    try:
        from shared.env import TektonEnvironLock, TektonEnviron
        TektonEnvironLock.load()
    except Exception as e:
        print(f"[MCP] TektonEnvironLock.load() error: {e}", file=sys.stderr)
    
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
    if os.environ.get('AISH_NO_MCP'):
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