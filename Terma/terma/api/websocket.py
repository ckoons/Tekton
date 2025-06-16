"""WebSocket server for terminal communication"""

import asyncio
import json
import logging
import os
import sys
import re
import uuid
from typing import Dict, Any, Set, Optional, Callable, List

import websockets
from websockets.server import WebSocketServerProtocol

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

from ..core.session_manager import SessionManager
from ..utils.logging import setup_logging

logger = setup_logging()

class TerminalWebSocketHandler:
    """Handles WebSocket connections for a single terminal session"""
    
    def __init__(self, session_id: str, session_manager: SessionManager):
        """Initialize the WebSocket handler
        
        Args:
            session_id: The ID of the session
            session_manager: SessionManager instance to manage terminal sessions
        """
        self.session_id = session_id
        self.session_manager = session_manager
        self.websockets: Set[WebSocketServerProtocol] = set()
        self.output_buffer = ""
        self.buffer_lock = asyncio.Lock()
        
    async def add_websocket(self, websocket: WebSocketServerProtocol):
        """Add a WebSocket connection
        
        Args:
            websocket: The WebSocket connection
        """
        self.websockets.add(websocket)
        
        # Register the output callback
        self.session_manager.register_output_callback(
            self.session_id, 
            lambda data: asyncio.create_task(self._handle_terminal_output(data))
        )
        
        logger.info(f"WebSocket connected to session {self.session_id}")
        
        # Send initial terminal content if available
        if self.output_buffer:
            async with self.buffer_lock:
                await self._send_output(self.output_buffer)
    
    async def remove_websocket(self, websocket: WebSocketServerProtocol):
        """Remove a WebSocket connection
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.websockets:
            self.websockets.remove(websocket)
            logger.info(f"WebSocket disconnected from session {self.session_id}")
            
        # If no more websockets, unregister the output callback
        if not self.websockets:
            self.session_manager.unregister_output_callback(
                self.session_id,
                lambda data: asyncio.create_task(self._handle_terminal_output(data))
            )
    
    async def _handle_terminal_output(self, data: str):
        """Handle output from the terminal and send to all WebSocket clients
        
        Args:
            data: The terminal output data
        """
        async with self.buffer_lock:
            # Add to buffer
            self.output_buffer += data
            
            # Limit buffer size
            if len(self.output_buffer) > 50000:
                self.output_buffer = self.output_buffer[-50000:]
            
            # Send to all websockets
            await self._send_output(data)
    
    async def _send_output(self, data: str):
        """Send output data to all connected WebSockets
        
        Args:
            data: The data to send
        """
        message = json.dumps({
            "type": "output",
            "data": data
        })
        
        # Send to all connected websockets
        for websocket in list(self.websockets):
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                # This will be handled by the event handler
                pass
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle a message from a WebSocket client
        
        Args:
            websocket: The WebSocket connection
            message: The message received
        """
        try:
            # Parse the message
            data = json.loads(message)
            message_type = data.get("type", "")
            
            if message_type == "input":
                # Write input to the terminal
                input_data = data.get("data", "")
                self.session_manager.write_to_session(self.session_id, input_data)
                
            elif message_type == "resize":
                # Resize the terminal
                rows = data.get("rows", 24)
                cols = data.get("cols", 80)
                self.session_manager.resize_session(self.session_id, rows, cols)
                
            elif message_type == "llm_assist":
                # Request LLM assistance
                command = data.get("command", "")
                is_output_analysis = data.get("is_output_analysis", False)
                await self._handle_llm_request(websocket, command, is_output_analysis)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling websocket message: {e}")
    
    async def _handle_llm_request(self, websocket: WebSocketServerProtocol, command: str, is_output_analysis: bool = False):
        """Handle a request for LLM assistance
        
        Args:
            websocket: The WebSocket connection
            command: The command to analyze
            is_output_analysis: Whether this is an output analysis request
        """
        try:
            # Get the session from the handler
            session_id = self.session_id
            session = self.session_manager.get_session(session_id)
            
            if not session:
                logger.error(f"Session {session_id} not found for LLM request")
                response = {
                    "type": "llm_response",
                    "content": f"Error: Terminal session not found. Please refresh the page.",
                    "error": True
                }
                await websocket.send(json.dumps(response))
                return
            
            # Send a loading message
            loading_response = {
                "type": "llm_response",
                "content": "Analyzing command and generating response...",
                "loading": True
            }
            await websocket.send(json.dumps(loading_response))
            
            # Use the LLM adapter to analyze the command
            from ..core.llm_adapter import LLMAdapter
            llm_adapter = LLMAdapter()
            
            # Process based on whether this is command help or output analysis
            if is_output_analysis:
                # Get command and output from the provided text
                if '\nOutput:\n' in command:
                    # Command includes output
                    parts = command.split('\nOutput:\n', 1)
                    cmd = parts[0].strip()
                    output = parts[1] if len(parts) > 1 else ""
                    
                    # Analyze the command output
                    logger.info(f"Analyzing output for command: {cmd}")
                    llm_response = await llm_adapter.analyze_output(session_id, cmd, output)
                else:
                    # Just a command without output
                    logger.info(f"Analyzing command output: {command}")
                    llm_response = await llm_adapter.analyze_output(session_id, command, "")
            else:
                # Command explanation request
                clean_command = command.strip()
                if clean_command.startswith("?"):
                    clean_command = clean_command[1:].strip()
                
                if not clean_command:
                    llm_response = "Please provide a command to explain."
                else:
                    logger.info(f"Analyzing command: {clean_command}")
                    llm_response = await llm_adapter.analyze_command(session_id, clean_command)
            
            # Send the response
            response = {
                "type": "llm_response",
                "content": llm_response,
                "loading": False
            }
            
            await websocket.send(json.dumps(response))
        except Exception as e:
            logger.error(f"Error handling LLM request: {e}")
            response = {
                "type": "llm_response",
                "content": f"Error processing LLM request: {str(e)}",
                "loading": False,
                "error": True
            }
            try:
                await websocket.send(json.dumps(response))
            except Exception as send_error:
                logger.error(f"Error sending LLM error response: {send_error}")

class TerminalWebSocketServer:
    """WebSocket server for terminal I/O"""
    
    def __init__(self, session_manager: SessionManager):
        """Initialize the WebSocket server
        
        Args:
            session_manager: SessionManager instance to manage terminal sessions
        """
        self.session_manager = session_manager
        self.handlers: Dict[str, TerminalWebSocketHandler] = {}
        self.server = None
        
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new WebSocket connection
        
        Args:
            websocket: The WebSocket connection
            path: The connection path
        """
        # Extract session ID from path
        session_id = self._extract_session_id(path)
        if not session_id:
            # Invalid path
            await websocket.close(1008, "Invalid path")
            return
            
        # Check if the session exists
        session = self.session_manager.get_session(session_id)
        if not session:
            # Session doesn't exist, try to create it
            session_id = self.session_manager.create_session(session_id)
            if not session_id:
                # Failed to create session
                await websocket.close(1011, "Failed to create session")
                return
                
        # Get or create handler for this session
        handler = self._get_or_create_handler(session_id)
        
        # Add this websocket to the handler
        await handler.add_websocket(websocket)
        
        try:
            # Handle messages from this websocket
            async for message in websocket:
                await handler.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Remove this websocket from the handler
            await handler.remove_websocket(websocket)
    
    def _extract_session_id(self, path: str) -> Optional[str]:
        """Extract session ID from WebSocket path
        
        Args:
            path: The WebSocket path
            
        Returns:
            str: The session ID, or None if invalid
        """
        # Path pattern: /ws/{session_id}
        pattern = r"^/ws/([a-zA-Z0-9-]+)$"
        match = re.match(pattern, path)
        if match:
            return match.group(1)
        return None
    
    def _get_or_create_handler(self, session_id: str) -> TerminalWebSocketHandler:
        """Get or create a handler for the session
        
        Args:
            session_id: The session ID
            
        Returns:
            TerminalWebSocketHandler: The handler
        """
        if session_id not in self.handlers:
            self.handlers[session_id] = TerminalWebSocketHandler(session_id, self.session_manager)
        return self.handlers[session_id]
    
    async def start_server(self, host: str = None, port: int = None):
        """Start the WebSocket server
        
        Args:
            host: Host to bind to (defaults to TERMA_WS_HOST env var or "0.0.0.0")
            port: Port to bind to (defaults to TERMA_WS_PORT env var or 8767)
        """
        import os
        
        # Read from environment variables as the source of truth
        if host is None:
            host = os.environ.get("TERMA_WS_HOST", "0.0.0.0")
        
        if port is None:
            # Use TERMA_WS_PORT as the default
            config = get_component_config()
            port = config.terma.ws_port if hasattr(config, 'terma') else int(os.environ.get("TERMA_WS_PORT"))
            logger.info(f"Using port {port} from configuration")
        # Debug port availability
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((host, port))
        if result == 0:
            logger.warning(f"WebSocket port {port} is already in use!")
            # Check what process is using the port
            import subprocess
            try:
                process_info = subprocess.run(['lsof', '-i', f':{port}'], 
                                           capture_output=True, text=True)
                logger.debug(f"WebSocket port {port} lsof output:\n{process_info.stdout}")
            except Exception as e:
                logger.debug(f"Failed to run lsof for WebSocket port: {e}")
        else:
            logger.debug(f"WebSocket port {port} is available")
        s.close()
        
        try:
            import os
            logger.debug(f"WebSocket server process PID: {os.getpid()}")
            
            # Use more explicit server settings
            # Only use parameters that are supported by the installed websockets version
            self.server = await websockets.serve(
                self.handle_connection,
                host,
                port,
                ping_interval=30,      # Send ping every 30 seconds
                ping_timeout=10,       # Wait 10 seconds for pong
                max_size=1024*1024,    # 1MB max message size
            )
            
            logger.info(f"Terminal WebSocket server started on {host}:{port}")
            
            # Keep the server running
            await self.server.wait_closed()
        except Exception as e:
            logger.error(f"Failed to start WebSocket server on port {port}: {e}")
            import traceback
            logger.debug(f"WebSocket server error details: {traceback.format_exc()}")
    
    def stop_server(self):
        """Stop the WebSocket server"""
        if self.server:
            self.server.close()
            logger.info("Terminal WebSocket server stopped")