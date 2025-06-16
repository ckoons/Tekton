import asyncio
import logging
import os
import sys
import time
import multiprocessing
from typing import Dict, List, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from Codex.adapter.aider_adapter import CodexAiderAdapter
from Codex.adapter.websocket_handler import WebSocketHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("codex_server")

# Create FastAPI app
app = FastAPI()

# Add CORS middleware to allow browser connections
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create Aider adapter
codex_adapter = None  # Will be initialized on-demand to prevent threading issues

# Active WebSocket connections
active_connections: List[WebSocket] = []

# Session status tracking
session_status = {
    "initialized": False,
    "starting": False,
    "last_activity": time.time(),
    "current_handler": None,
    "session_id": None  # Track session ID for better management
}

# Initialize the multiprocessing context - 'spawn' is more compatible across platforms
mp_context = multiprocessing.get_context('spawn')

@app.get("/api/codex/status")
async def get_status():
    """
    Get the status of the Codex component.
    
    Returns:
        dict: Status information
    """
    return JSONResponse({
        "status": "active",
        "name": "Codex Aider",
        "description": "AI pair programming tool",
        "input_destination": "right_footer",  # Signal that we use the RIGHT FOOTER for input
        "session_active": session_status["initialized"]
    })

@app.post("/api/codex/start")
async def start_session():
    """
    Start a new Aider session.
    
    Returns:
        dict: Status information
    """
    global codex_adapter
    
    try:
        # If we're already starting, return status
        if session_status["starting"]:
            return JSONResponse({
                "status": "warning",
                "message": "Session startup already in progress"
            })
        
        # Mark as starting before anything else
        session_status["starting"] = True
        
        # Log the start process
        logger.info("Starting new Aider session")
        
        # Stop existing session if running - with proper error handling
        if session_status["initialized"] and codex_adapter:
            logger.info("Stopping existing Aider session before starting new one")
            try:
                await codex_adapter.stop()
            except Exception as e:
                logger.error(f"Error stopping existing session: {e}")
            finally:
                # Even if stop fails, reset these
                session_status["initialized"] = False
                codex_adapter = None
                session_status["session_id"] = None
                # Small delay to ensure cleanup
                await asyncio.sleep(0.5)
        
        # Create a new WebSocket handler if needed
        if session_status["current_handler"] is None and active_connections:
            logger.info("Setting up new WebSocket handler")
            session_status["current_handler"] = WebSocketHandler(active_connections[0])
            
        if session_status["current_handler"] is None:
            session_status["starting"] = False
            return JSONResponse({
                "status": "error",
                "message": "No active WebSocket connection available"
            })
        
        # Send starting message to UI
        await session_status["current_handler"].send_output("Starting Aider session...")
        
        # Generate a new session ID
        session_status["session_id"] = f"session_{int(time.time())}"
        logger.info(f"Generated new session ID: {session_status['session_id']}")
        
        # Create a new adapter instance for this session
        logger.info("Creating new CodexAiderAdapter instance")
        codex_adapter = CodexAiderAdapter()
        
        # Initialize the adapter
        logger.info("Initializing the adapter with WebSocket handler")
        initialization_result = await codex_adapter.initialize(session_status["current_handler"])
        
        if not initialization_result:
            session_status["starting"] = False
            return JSONResponse({
                "status": "error",
                "message": "Failed to initialize Aider session"
            })
        
        # Update status
        session_status["initialized"] = True
        session_status["starting"] = False
        session_status["last_activity"] = time.time()
        
        # Notify all connections about the new session
        for conn in active_connections:
            handler = WebSocketHandler(conn)
            await handler.send_session_status(True, session_status["session_id"])
        
        # Success message is sent in the JSON response, no need to duplicate it here
        
        return JSONResponse({
            "status": "success",
            "message": "Aider session started successfully",
            "session_id": session_status["session_id"]
        })
    except Exception as e:
        # Reset status on error
        session_status["starting"] = False
        if codex_adapter:
            try:
                await codex_adapter.stop()
            except:
                pass
            codex_adapter = None
        logger.error(f"Error starting session: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/codex/stop")
async def stop_session():
    """
    Stop the current Aider session.
    
    Returns:
        dict: Status information
    """
    global codex_adapter
    
    try:
        if not session_status["initialized"] or not codex_adapter:
            return JSONResponse({
                "status": "warning", 
                "message": "No active session to stop"
            })
            
        # Stop the adapter
        await codex_adapter.stop()
        
        # Update status
        session_status["initialized"] = False
        session_status["session_id"] = None
        
        if session_status["current_handler"]:
            await session_status["current_handler"].send_output("Aider session stopped")
        
        # Clean up adapter
        codex_adapter = None
            
        return JSONResponse({
            "status": "success",
            "message": "Aider session stopped successfully"
        })
    except Exception as e:
        # Ensure adapter is cleaned up even on errors
        if codex_adapter:
            try:
                await codex_adapter.stop()
            except:
                pass
            codex_adapter = None
        
        # Reset session status
        session_status["initialized"] = False
        session_status["session_id"] = None
        
        logger.error(f"Error stopping session: {e}")
        return JSONResponse({"status": "error", "message": str(e)})
    
@app.post("/api/codex/input")
async def receive_input(data: dict):
    """
    Receive input from the Tekton RIGHT FOOTER.
    
    SIMPLIFIED DIRECT IMPLEMENTATION:
    This endpoint is now the primary method for sending user input to Aider.
    The complex chain of events (chat input → adapter → iframe → WebSocket → server)
    has been replaced with a direct API call.
    
    Args:
        data: A dictionary containing the input text
            
    Returns:
        dict: Status information
    """
    global codex_adapter
    
    try:
        input_text = data.get("text", "")
        if not input_text:
            logger.warning("Empty input received by API")
            return JSONResponse({"status": "error", "message": "No input text provided"})
        
        # Make received input extremely visible in logs for debugging
        log_separator = "=" * 50
        logger.info(f"\n{log_separator}\nDIRECT API INPUT: '{input_text}'\n{log_separator}")
        print(f"\n{log_separator}\n====> DIRECT API INPUT RECEIVED: '{input_text}' <====\n{log_separator}")
        
        # Auto-start if not initialized
        if (not session_status["initialized"] or not codex_adapter) and not session_status["starting"]:
            logger.info(f"Auto-starting session for input: '{input_text}'")
            # Use the first available connection
            if active_connections:
                session_status["current_handler"] = WebSocketHandler(active_connections[0])
                await start_session()
            else:
                logger.error("Cannot auto-start: No active WebSocket connection")
                return JSONResponse({
                    "status": "error",
                    "message": "No active WebSocket connection for notifications. Please refresh the page."
                })
                
        # Check again after potential auto-start
        if not session_status["initialized"] or not codex_adapter:
            logger.error(f"Session not initialized after auto-start attempt for input: '{input_text}'")
            return JSONResponse({
                "status": "error",
                "message": "Session not initialized, please try again in a moment"
            })
            
        # Update last activity timestamp
        session_status["last_activity"] = time.time()
            
        # Process input directly through adapter - CRITICAL PATH
        logger.info(f"Sending input directly to adapter: '{input_text}'")
        success = await codex_adapter.receive_input(input_text)
        
        if not success:
            logger.error(f"Adapter reported failure processing input: '{input_text}'")
            return JSONResponse({
                "status": "error", 
                "message": "Adapter failed to process input"
            })
        
        # Also forward to all active WebSocket connections to keep UI in sync
        # This is now for UI feedback only, not primary input handling
        logger.info(f"Forwarding input to {len(active_connections)} WebSocket connections for UI sync")
        for connection in active_connections:
            await connection.send_json({
                "type": "input_received",  # Changed to clearer message type
                "content": {"text": input_text, "timestamp": time.time()}
            })
            
        # Send additional visual feedback through WebSocket handler
        if session_status["current_handler"]:
            await session_status["current_handler"].send_input_received(input_text)
        
        logger.info(f"Input successfully processed: '{input_text}'")
        return JSONResponse({
            "status": "success", 
            "message": "Input received and processed",
            "session_id": session_status["session_id"]
        })
    except Exception as e:
        logger.error(f"Error processing input '{input_text if 'input_text' in locals() else '<unknown>'}': {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse({"status": "error", "message": f"Server error: {str(e)}"})

@app.websocket("/ws/codex")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle WebSocket connections from the UI.
    
    Args:
        websocket: The WebSocket connection
    """
    global codex_adapter
    
    await websocket.accept()
    active_connections.append(websocket)
    
    # Create WebSocket handler
    websocket_handler = WebSocketHandler(websocket)
    
    # Set as current handler if none exists
    if session_status["current_handler"] is None:
        session_status["current_handler"] = websocket_handler
    
    try:
        # Send current session status to new connection
        await websocket.send_json({
            "type": "session_status",
            "content": {
                "active": session_status["initialized"],
                "session_id": session_status["session_id"],
                "timestamp": time.time()
            }
        })
        
        # Notify about existing session if already running
        if session_status["initialized"] and codex_adapter:
            await websocket_handler.send_output("Connected to existing Aider session")
            
        # Handle messages from the client
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get("type", "")
            content = data.get("content", "")
            
            if message_type == "start_session":
                # Use this handler for the session
                session_status["current_handler"] = websocket_handler
                
                # Start or restart Aider session via the API endpoint
                await start_session()
                
            elif message_type == "stop_session":
                # Stop current session via the API endpoint
                await stop_session()
                
            elif message_type == "input":
                # Update the current handler if needed
                session_status["current_handler"] = websocket_handler
                
                # Auto-start if needed
                if (not session_status["initialized"] or not codex_adapter) and not session_status["starting"]:
                    await start_session()
                
                # Process input from the UI
                if session_status["initialized"] and codex_adapter:
                    # Update last activity
                    session_status["last_activity"] = time.time()
                    
                    # Send immediate visual feedback
                    await websocket_handler.send_input_received(content)
                    
                    # Forward the input to Aider
                    await codex_adapter.receive_input(content)
                else:
                    await websocket_handler.send_error("Session not initialized, please try again")
                    
            elif message_type == "ping":
                # Simple ping-pong to keep connection alive
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        # Handle disconnection
        logger.info("WebSocket client disconnected")
        if websocket in active_connections:
            active_connections.remove(websocket)
        
        # Clear current handler if this was it
        if session_status["current_handler"] and session_status["current_handler"].websocket == websocket:
            session_status["current_handler"] = None
            
            # Try to set a new handler if available
            if active_connections:
                session_status["current_handler"] = WebSocketHandler(active_connections[0])
            elif session_status["initialized"] and codex_adapter:
                # No more connections but session is running, stop it gracefully
                logger.info("No more active connections, stopping Aider session")
                await codex_adapter.stop()
                codex_adapter = None
                session_status["initialized"] = False
                session_status["session_id"] = None
    
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Error in WebSocket connection: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)
        
        # Clear current handler if this was it
        if session_status["current_handler"] and session_status["current_handler"].websocket == websocket:
            session_status["current_handler"] = None
            
            # Try to set a new handler if available
            if active_connections:
                session_status["current_handler"] = WebSocketHandler(active_connections[0])