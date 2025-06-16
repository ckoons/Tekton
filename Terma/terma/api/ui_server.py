"""UI server for Terma terminal"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import logging
from ..utils.logging import setup_logging

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

# Set up logging with DEBUG level for troubleshooting
logger = setup_logging(level=logging.DEBUG)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
UI_DIR = PROJECT_ROOT / "ui"

# Create the FastAPI application
app = FastAPI(title="Terma UI Server")

# Mount the static files
app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

@app.get("/")
async def root():
    """Redirect to the terminal page"""
    return RedirectResponse(url="/terminal")

@app.get("/terminal", response_class=HTMLResponse)
async def get_terminal_ui():
    """Return the terminal UI"""
    try:
        html_path = UI_DIR / "terma-terminal.html"
        if html_path.exists():
            return FileResponse(html_path)
        else:
            logger.error(f"Terminal UI file not found: {html_path}")
            return HTMLResponse(content="<h1>Terminal UI not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving terminal UI: {e}")
        return HTMLResponse(content=f"<h1>Error serving terminal UI: {str(e)}</h1>", status_code=500)

@app.get("/terminal/launch")
async def launch_terminal(session_id: str = None, server_url: str = None, ws_url: str = None):
    """Launch a standalone terminal"""
    try:
        html_path = UI_DIR / "launcher.html"
        if html_path.exists():
            return FileResponse(html_path)
        else:
            logger.error(f"Launcher UI file not found: {html_path}")
            return HTMLResponse(content="<h1>Launcher UI not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving launcher UI: {e}")
        return HTMLResponse(content=f"<h1>Error serving launcher UI: {str(e)}</h1>", status_code=500)

@app.get("/terminal/{session_id}")
async def get_terminal_session(session_id: str):
    """Return the terminal UI for a specific session"""
    return await get_terminal_ui()

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serve images"""
    try:
        image_path = PROJECT_ROOT / "images" / filename
        if image_path.exists():
            return FileResponse(image_path)
        else:
            logger.error(f"Image not found: {image_path}")
            return HTMLResponse(content="<h1>Image not found</h1>", status_code=404)
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        return HTMLResponse(content=f"<h1>Error serving image: {str(e)}</h1>", status_code=500)

# Function to start the server - now properly async and respects environment variables
async def start_ui_server(host: str = None, port: int = None):
    """Start the UI server asynchronously
    
    Args:
        host: The host to bind to (defaults to TERMA_UI_HOST env var or "0.0.0.0")
        port: The port to bind to (defaults to TERMA_WS_PORT env var or 8767)
        
    Returns:
        The running server instance
    """
    import os
    
    # Read from environment variables as the source of truth
    if host is None:
        host = os.environ.get("TERMA_UI_HOST", "0.0.0.0")
    
    if port is None:
        # Use TERMA_WS_PORT as the default - consistent with WebSocket server
        config = get_component_config()
        port = config.terma.ws_port if hasattr(config, 'terma') else int(os.environ.get("TERMA_WS_PORT"))
        logger.info(f"Using port {port} from configuration")
    import uvicorn
    import os
    
    # Log the current process information
    logger.debug(f"UI server starting in process PID: {os.getpid()}")
    
    # Check if the port is available
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((host, port))
    if result == 0:
        logger.warning(f"UI server port {port} is already in use!")
        # Check what process is using the port
        import subprocess
        try:
            process_info = subprocess.run(['lsof', '-i', f':{port}'], 
                                      capture_output=True, text=True)
            logger.debug(f"UI server port {port} lsof output:\n{process_info.stdout}")
        except Exception as e:
            logger.debug(f"Failed to run lsof for UI server port: {e}")
    else:
        logger.debug(f"UI server port {port} is available")
    s.close()
    
    logger.info(f"Starting UI server on {host}:{port}")
    
    try:
        # Create server config
        config = uvicorn.Config(app, host=host, port=port)
        server = uvicorn.Server(config)
        
        # Start server - this returns a coroutine that can be awaited
        await server.serve()
        logger.info(f"UI server started successfully on {host}:{port}")
        return server
    except Exception as e:
        logger.error(f"Failed to start UI server on port {port}: {e}")
        return None