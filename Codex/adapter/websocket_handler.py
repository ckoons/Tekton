import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("websocket_handler")

class WebSocketHandler:
    """
    Handler for WebSocket communication between Aider and the Tekton UI.
    """
    
    def __init__(self, websocket):
        """
        Initialize the WebSocket handler.
        
        Args:
            websocket: The WebSocket connection to the UI
        """
        self.websocket = websocket
        self.input_requested = False
    
    async def send_message(self, message_type: str, content: Any) -> None:
        """
        Send a message to the UI.
        
        Args:
            message_type: Type of message (output, error, warning, etc.)
            content: Message content
        """
        try:
            await self.websocket.send_json({
                'type': message_type,
                'content': content
            })
        except Exception as e:
            logger.error(f"Error sending message to UI: {e}")
    
    async def send_output(self, message: str) -> None:
        """
        Send output message to the UI.
        
        Args:
            message: The output message
        """
        logger.debug(f"Sending output: {message[:100]}...")
        await self.send_message('output', message)
    
    async def send_error(self, message: str) -> None:
        """
        Send error message to the UI.
        
        Args:
            message: The error message
        """
        logger.warning(f"Sending error: {message}")
        await self.send_message('error', message)
    
    async def send_warning(self, message: str) -> None:
        """
        Send warning message to the UI.
        
        Args:
            message: The warning message
        """
        logger.info(f"Sending warning: {message}")
        await self.send_message('warning', message)
    
    async def send_active_files(self, files: List[str]) -> None:
        """
        Send list of active files to the UI.
        
        Args:
            files: List of active file paths
        """
        logger.debug(f"Sending active files: {files}")
        await self.send_message('active_files', files)
    
    async def request_input(self) -> None:
        """
        Signal to the UI that input is requested.
        """
        logger.debug("Requesting input from UI")
        self.input_requested = True
        await self.send_message('input_request', {
            'prompt': 'Type a message to Aider...'
        })
    
    async def send_input_received(self, text: str) -> None:
        """
        Send confirmation that input was received to provide visual feedback.
        
        Args:
            text: The input text that was received
        """
        logger.debug(f"Confirming input received: {text[:50]}...")
        await self.send_message('input_received', {
            'text': text,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    async def send_session_status(self, is_active: bool, session_id: str = None) -> None:
        """
        Send session status update to the UI.
        
        Args:
            is_active: Whether the session is active
            session_id: Optional session identifier
        """
        logger.debug(f"Sending session status: {'active' if is_active else 'inactive'}, session_id: {session_id}")
        await self.send_message('session_status', {
            'active': is_active,
            'session_id': session_id,
            'timestamp': asyncio.get_event_loop().time()
        })