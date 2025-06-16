"""
Tekton WebSocket Management

This module provides standardized WebSocket client and server utilities for Tekton components.
It includes connection management, reconnection logic, message formatting, and error handling.

Usage:
    # Client Usage
    from tekton.utils.tekton_websocket import WebSocketClient
    
    client = WebSocketClient(
        ws_url="ws://localhost:8001/ws", 
        on_message=lambda msg: print(f"Received: {msg}")
    )
    
    await client.connect()
    await client.send_message({"type": "request", "id": "123", "action": "get_status"})
    await client.close()
    
    # Server Usage (with FastAPI)
    from tekton.utils.tekton_websocket import WebSocketManager, WSConnectionManager
    
    ws_manager = WebSocketManager()
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                await ws_manager.process_message(websocket, data)
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
"""

import os
import json
import asyncio
import logging
import uuid
from enum import Enum
from typing import Dict, Any, Optional, Callable, List, Union, Set, Tuple, cast
from datetime import datetime, timedelta

# Import tekton errors
from .tekton_errors import (
    WebSocketError,
    WebSocketConnectionError,
    WebSocketProtocolError,
    WebSocketClosedError
)

# Set up logger
logger = logging.getLogger(__name__)

# We'll assume common WebSocket implementations are available
try:
    # Server-side
    from fastapi import WebSocket, WebSocketDisconnect
    from starlette.websockets import WebSocketState
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    
    # Create stub classes for type checking
    class WebSocket:
        pass
    
    class WebSocketDisconnect(Exception):
        pass
    
    class WebSocketState(Enum):
        CONNECTING = 0
        CONNECTED = 1
        DISCONNECTED = 2

try:
    # Client-side
    import websockets
    from websockets.exceptions import (
        ConnectionClosed, 
        InvalidStatusCode, 
        WebSocketProtocolError as WSProtocolError
    )
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    
    # Create stub classes for type checking
    class websockets:
        class client:
            class WebSocketClientProtocol:
                pass
    
    class ConnectionClosed(Exception):
        pass
    
    class InvalidStatusCode(Exception):
        pass
    
    class WSProtocolError(Exception):
        pass


class ConnectionState(Enum):
    """WebSocket connection states."""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    RECONNECTING = 3
    CLOSING = 4


class WebSocketClient:
    """WebSocket client for Tekton components."""
    
    def __init__(
        self,
        ws_url: str,
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_connect: Optional[Callable[[], None]] = None,
        on_disconnect: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        reconnect_interval: int = 5000,
        max_reconnect_attempts: int = 10,
        auto_reconnect: bool = True,
        auth_token: Optional[str] = None,
        component_id: Optional[str] = None,
        timeout: float = 30.0,
        ping_interval: Optional[float] = 20.0,
        ping_timeout: Optional[float] = 10.0
    ):
        """
        Initialize WebSocket client.
        
        Args:
            ws_url: WebSocket server URL
            on_message: Callback for incoming messages
            on_connect: Callback for successful connection
            on_disconnect: Callback for disconnection
            on_error: Callback for errors
            reconnect_interval: Interval in ms to attempt reconnection
            max_reconnect_attempts: Maximum number of reconnection attempts
            auto_reconnect: Whether to automatically reconnect on disconnection
            auth_token: Optional authentication token
            component_id: Component identifier for logging
            timeout: Connection timeout in seconds
            ping_interval: Interval in seconds between ping messages (None to disable)
            ping_timeout: Timeout in seconds for ping responses (None to disable)
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets package is required for WebSocketClient")
            
        self.ws_url = ws_url
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_error = on_error
        self.reconnect_interval = reconnect_interval / 1000.0  # Convert to seconds
        self.max_reconnect_attempts = max_reconnect_attempts
        self.auto_reconnect = auto_reconnect
        self.auth_token = auth_token
        self.component_id = component_id or "tekton_client"
        self.timeout = timeout
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        
        # Connection state
        self.connection: Optional[websockets.client.WebSocketClientProtocol] = None
        self.state = ConnectionState.DISCONNECTED
        self.reconnect_attempts = 0
        self.reconnect_task: Optional[asyncio.Task] = None
        self.ping_task: Optional[asyncio.Task] = None
        self.receive_task: Optional[asyncio.Task] = None
        self.closing_event = asyncio.Event()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_requests: Dict[str, asyncio.Future] = {}
    
    async def connect(self) -> bool:
        """
        Connect to the WebSocket server.
        
        Returns:
            True if connection successful
        
        Raises:
            WebSocketConnectionError: If connection fails
        """
        if self.state in (ConnectionState.CONNECTED, ConnectionState.CONNECTING):
            logger.debug(f"Already connected or connecting to {self.ws_url}")
            return True
        
        self.state = ConnectionState.CONNECTING
        self.closing_event.clear()
        
        try:
            # Prepare connection headers
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Connect to server
            connection = await websockets.connect(
                self.ws_url,
                extra_headers=headers,
                open_timeout=self.timeout,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout
            )
            
            # Store connection and update state
            self.connection = connection
            self.state = ConnectionState.CONNECTED
            self.reconnect_attempts = 0
            
            # Start message processing task
            self.receive_task = asyncio.create_task(self._process_messages())
            
            # Call on_connect callback if provided
            if self.on_connect:
                try:
                    self.on_connect()
                except Exception as e:
                    logger.error(f"Error in on_connect callback: {e}")
            
            logger.info(f"Connected to WebSocket server at {self.ws_url}")
            return True
            
        except (ConnectionRefusedError, InvalidStatusCode, WebSocketError, OSError) as e:
            self.state = ConnectionState.DISCONNECTED
            logger.error(f"Failed to connect to WebSocket server at {self.ws_url}: {e}")
            
            # Call on_error callback if provided
            if self.on_error:
                try:
                    self.on_error(e)
                except Exception as callback_error:
                    logger.error(f"Error in on_error callback: {callback_error}")
            
            # Start reconnection if enabled
            if self.auto_reconnect and not self.closing_event.is_set():
                asyncio.create_task(self._reconnect())
            
            raise WebSocketConnectionError(f"Failed to connect to {self.ws_url}: {str(e)}")
    
    async def _process_messages(self) -> None:
        """
        Process incoming messages from the WebSocket connection.
        
        This method runs as a background task while connected.
        """
        if not self.connection:
            return
        
        try:
            async for message in self.connection:
                try:
                    # Parse the message as JSON
                    if isinstance(message, str):
                        data = json.loads(message)
                    elif isinstance(message, bytes):
                        data = json.loads(message.decode('utf-8'))
                    else:
                        logger.warning(f"Received message of unexpected type: {type(message)}")
                        continue
                    
                    # Handle response messages
                    if isinstance(data, dict) and "request_id" in data:
                        request_id = data["request_id"]
                        if request_id in self.pending_requests:
                            future = self.pending_requests.pop(request_id)
                            if not future.done():
                                future.set_result(data)
                    
                    # Call message callback if provided
                    if self.on_message:
                        try:
                            self.on_message(data)
                        except Exception as e:
                            logger.error(f"Error in on_message callback: {e}")
                    
                except json.JSONDecodeError:
                    logger.warning(f"Received non-JSON message: {message[:100]}...")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
        
        except (ConnectionClosed, WSProtocolError) as e:
            if not self.closing_event.is_set():
                logger.info(f"WebSocket connection closed: {e}")
                await self._handle_disconnection()
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket receive loop: {e}")
            await self._handle_disconnection()
    
    async def _handle_disconnection(self) -> None:
        """Handle WebSocket disconnection."""
        if self.state == ConnectionState.CLOSING:
            return
        
        # Update state
        prev_state = self.state
        self.state = ConnectionState.DISCONNECTED
        
        # Clean up connection
        if self.connection:
            try:
                await self.connection.close()
            except Exception:
                pass
            self.connection = None
        
        # Cancel any pending requests
        for request_id, future in self.pending_requests.items():
            if not future.done():
                future.set_exception(WebSocketClosedError("WebSocket connection closed"))
        
        # Clear pending requests
        self.pending_requests.clear()
        
        # Call on_disconnect callback if provided
        if self.on_disconnect and prev_state == ConnectionState.CONNECTED:
            try:
                self.on_disconnect()
            except Exception as e:
                logger.error(f"Error in on_disconnect callback: {e}")
        
        # Start reconnection if enabled
        if self.auto_reconnect and not self.closing_event.is_set():
            asyncio.create_task(self._reconnect())
    
    async def _reconnect(self) -> None:
        """
        Attempt to reconnect to the WebSocket server.
        
        This method implements exponential backoff for reconnection attempts.
        """
        if self.state in (ConnectionState.CONNECTING, ConnectionState.RECONNECTING):
            return
        
        self.state = ConnectionState.RECONNECTING
        
        while (
            self.reconnect_attempts < self.max_reconnect_attempts and 
            not self.closing_event.is_set()
        ):
            self.reconnect_attempts += 1
            
            # Calculate delay with exponential backoff and jitter
            delay = min(60, self.reconnect_interval * (1.5 ** (self.reconnect_attempts - 1)))
            delay_with_jitter = delay * (0.8 + 0.4 * (uuid.uuid4().int % 100) / 100.0)
            
            logger.info(
                f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} "
                f"in {delay_with_jitter:.2f} seconds"
            )
            
            # Wait before reconnecting
            try:
                await asyncio.wait_for(self.closing_event.wait(), timeout=delay_with_jitter)
                return  # Closing event was set
            except asyncio.TimeoutError:
                pass  # Continue with reconnection
            
            # Attempt to reconnect
            try:
                await self.connect()
                return  # Reconnection successful
            except WebSocketConnectionError:
                # Connection failed, will retry
                pass
        
        logger.error(
            f"Failed to reconnect after {self.reconnect_attempts} attempts"
        )
        
        # Update state if still reconnecting
        if self.state == ConnectionState.RECONNECTING:
            self.state = ConnectionState.DISCONNECTED
    
    async def send_message(
        self, 
        message: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> None:
        """
        Send a message to the WebSocket server.
        
        Args:
            message: Message to send (will be serialized to JSON)
            timeout: Optional timeout in seconds
            
        Raises:
            WebSocketError: If sending fails
            WebSocketClosedError: If connection is closed
        """
        if self.state != ConnectionState.CONNECTED:
            raise WebSocketClosedError("WebSocket is not connected")
        
        if not self.connection:
            raise WebSocketClosedError("WebSocket connection is not established")
        
        try:
            # Serialize message to JSON
            json_message = json.dumps(message)
            
            # Send with timeout if specified
            if timeout is not None:
                await asyncio.wait_for(self.connection.send(json_message), timeout=timeout)
            else:
                await self.connection.send(json_message)
                
        except asyncio.TimeoutError:
            raise WebSocketError(f"Timeout sending message after {timeout} seconds")
        except ConnectionClosed:
            self.state = ConnectionState.DISCONNECTED
            raise WebSocketClosedError("WebSocket connection closed while sending message")
        except Exception as e:
            raise WebSocketError(f"Error sending WebSocket message: {str(e)}")
    
    async def request(
        self,
        message: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Send a request and wait for a response.
        
        This method assigns a unique request_id to the message and waits
        for a response with the same request_id.
        
        Args:
            message: Request message (will be modified with request_id)
            timeout: Timeout in seconds
            
        Returns:
            Response message
            
        Raises:
            WebSocketError: If request fails
            WebSocketClosedError: If connection is closed
            asyncio.TimeoutError: If response times out
        """
        if self.state != ConnectionState.CONNECTED:
            raise WebSocketClosedError("WebSocket is not connected")
        
        # Create a copy of the message to avoid modifying the original
        request = message.copy()
        
        # Generate a unique request ID if not provided
        if "request_id" not in request:
            request["request_id"] = str(uuid.uuid4())
        
        request_id = request["request_id"]
        
        # Create a future for the response
        future: asyncio.Future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send the request
            await self.send_message(request)
            
            # Wait for the response
            return await asyncio.wait_for(future, timeout=timeout)
        
        except asyncio.TimeoutError:
            # Remove the pending request
            self.pending_requests.pop(request_id, None)
            raise asyncio.TimeoutError(f"Request timed out after {timeout} seconds")
        
        except Exception as e:
            # Remove the pending request
            self.pending_requests.pop(request_id, None)
            
            # Re-raise the exception
            if isinstance(e, (WebSocketError, WebSocketClosedError, asyncio.TimeoutError)):
                raise
            raise WebSocketError(f"Error sending request: {str(e)}")
    
    async def close(self) -> None:
        """
        Close the WebSocket connection.
        
        This method stops reconnection attempts and closes the connection.
        """
        logger.debug(f"Closing WebSocket connection to {self.ws_url}")
        
        # Set closing state and event
        self.state = ConnectionState.CLOSING
        self.closing_event.set()
        
        # Close connection
        if self.connection:
            try:
                await self.connection.close()
            except Exception as e:
                logger.debug(f"Error closing WebSocket connection: {e}")
            self.connection = None
        
        # Cancel tasks
        for task in [self.receive_task, self.reconnect_task, self.ping_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):
                    pass
        
        # Reset tasks
        self.receive_task = None
        self.reconnect_task = None
        self.ping_task = None
        
        # Update state
        self.state = ConnectionState.DISCONNECTED
        logger.debug("WebSocket connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if the WebSocket is connected."""
        return self.state == ConnectionState.CONNECTED and self.connection is not None
    
    async def __aenter__(self) -> 'WebSocketClient':
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# FastAPI WebSocket manager
if FASTAPI_AVAILABLE:
    class WSConnectionManager:
        """
        Connection manager for WebSocket connections.
        
        This is a simple connection manager that tracks active connections
        and provides methods for broadcasting messages.
        """
        
        def __init__(self):
            """Initialize the connection manager."""
            self.active_connections: List[WebSocket] = []
            self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        
        async def connect(
            self,
            websocket: WebSocket,
            client_info: Optional[Dict[str, Any]] = None
        ) -> None:
            """
            Accept a WebSocket connection and store it.
            
            Args:
                websocket: The WebSocket connection
                client_info: Optional information about the client
            """
            await websocket.accept()
            self.active_connections.append(websocket)
            self.connection_info[websocket] = client_info or {}
            logger.debug(f"WebSocket client connected: {websocket.client.host}:{websocket.client.port}")
        
        def disconnect(self, websocket: WebSocket) -> None:
            """
            Remove a disconnected WebSocket connection.
            
            Args:
                websocket: The WebSocket connection to remove
            """
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connection_info.pop(websocket, None)
                logger.debug(f"WebSocket client disconnected: {websocket.client.host}:{websocket.client.port}")
        
        def get_client_info(self, websocket: WebSocket) -> Dict[str, Any]:
            """
            Get information about a client.
            
            Args:
                websocket: The WebSocket connection
                
            Returns:
                Client information
            """
            return self.connection_info.get(websocket, {})
        
        def set_client_info(self, websocket: WebSocket, info: Dict[str, Any]) -> None:
            """
            Set information about a client.
            
            Args:
                websocket: The WebSocket connection
                info: Client information
            """
            if websocket in self.active_connections:
                self.connection_info[websocket] = info
        
        def update_client_info(self, websocket: WebSocket, info: Dict[str, Any]) -> None:
            """
            Update information about a client.
            
            Args:
                websocket: The WebSocket connection
                info: Client information to update
            """
            if websocket in self.active_connections:
                current_info = self.connection_info.get(websocket, {})
                current_info.update(info)
                self.connection_info[websocket] = current_info
        
        async def send_personal_message(
            self,
            message: Union[str, Dict[str, Any]],
            websocket: WebSocket
        ) -> bool:
            """
            Send a message to a specific client.
            
            Args:
                message: The message to send (string or dict)
                websocket: The WebSocket connection
                
            Returns:
                True if the message was sent successfully
            """
            if websocket not in self.active_connections:
                return False
            
            try:
                if isinstance(message, dict):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(message)
                return True
            except Exception as e:
                logger.error(f"Error sending personal message: {e}")
                return False
        
        async def broadcast(
            self,
            message: Union[str, Dict[str, Any]],
            exclude: Optional[Union[WebSocket, List[WebSocket]]] = None
        ) -> int:
            """
            Broadcast a message to all connected clients.
            
            Args:
                message: The message to broadcast
                exclude: Client(s) to exclude from the broadcast
                
            Returns:
                Number of clients the message was sent to
            """
            exclude_list = []
            if exclude is not None:
                if isinstance(exclude, list):
                    exclude_list = exclude
                else:
                    exclude_list = [exclude]
            
            sent_count = 0
            for connection in self.active_connections:
                if connection not in exclude_list:
                    try:
                        if isinstance(message, dict):
                            await connection.send_json(message)
                        else:
                            await connection.send_text(message)
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Error broadcasting message: {e}")
            
            return sent_count
        
        async def broadcast_filtered(
            self,
            message: Union[str, Dict[str, Any]],
            filter_func: Callable[[WebSocket, Dict[str, Any]], bool]
        ) -> int:
            """
            Broadcast a message to clients that match a filter.
            
            Args:
                message: The message to broadcast
                filter_func: Function that takes a WebSocket and client info and returns
                            True if the client should receive the message
                
            Returns:
                Number of clients the message was sent to
            """
            sent_count = 0
            for connection in self.active_connections:
                client_info = self.connection_info.get(connection, {})
                if filter_func(connection, client_info):
                    try:
                        if isinstance(message, dict):
                            await connection.send_json(message)
                        else:
                            await connection.send_text(message)
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"Error broadcasting filtered message: {e}")
            
            return sent_count
        
        def get_connection_count(self) -> int:
            """Get the number of active connections."""
            return len(self.active_connections)


    class WebSocketManager(WSConnectionManager):
        """
        Extended WebSocket manager with message handling and authentication.
        
        This manager extends the basic connection manager with message handlers,
        authentication, and more advanced features.
        """
        
        def __init__(self):
            """Initialize the WebSocket manager."""
            super().__init__()
            self.message_handlers: Dict[str, Callable] = {}
            self.default_handler: Optional[Callable] = None
            self.on_connect: Optional[Callable] = None
            self.on_disconnect: Optional[Callable] = None
            self.authenticate_func: Optional[Callable] = None
        
        def register_handler(
            self,
            message_type: str,
            handler: Callable[[WebSocket, Dict[str, Any]], Any]
        ) -> None:
            """
            Register a handler for a specific message type.
            
            Args:
                message_type: Type of message to handle
                handler: Coroutine function to handle the message
            """
            self.message_handlers[message_type] = handler
        
        def register_default_handler(
            self,
            handler: Callable[[WebSocket, Dict[str, Any]], Any]
        ) -> None:
            """
            Register a default handler for messages with no specific handler.
            
            Args:
                handler: Coroutine function to handle messages
            """
            self.default_handler = handler
        
        def register_connect_handler(
            self,
            handler: Callable[[WebSocket], Any]
        ) -> None:
            """
            Register a handler for new connections.
            
            Args:
                handler: Coroutine function to handle new connections
            """
            self.on_connect = handler
        
        def register_disconnect_handler(
            self,
            handler: Callable[[WebSocket], Any]
        ) -> None:
            """
            Register a handler for disconnections.
            
            Args:
                handler: Coroutine function to handle disconnections
            """
            self.on_disconnect = handler
        
        def register_auth_handler(
            self,
            handler: Callable[[WebSocket, Dict[str, Any]], Any]
        ) -> None:
            """
            Register an authentication handler.
            
            Args:
                handler: Coroutine function to authenticate connections
            """
            self.authenticate_func = handler
        
        async def connect(
            self,
            websocket: WebSocket,
            client_info: Optional[Dict[str, Any]] = None
        ) -> bool:
            """
            Accept a WebSocket connection and store it.
            
            Args:
                websocket: The WebSocket connection
                client_info: Optional information about the client
                
            Returns:
                True if the connection was accepted
            """
            # Accept connection
            await websocket.accept()
            
            # Initialize client info
            info = client_info or {}
            info.update({
                "connected_at": datetime.now().isoformat(),
                "client_ip": websocket.client.host,
                "client_port": websocket.client.port,
                "authenticated": False
            })
            
            # Authenticate if needed
            if self.authenticate_func:
                try:
                    auth_result = await self.authenticate_func(websocket, info)
                    if not auth_result:
                        logger.warning(f"Authentication failed for {websocket.client.host}")
                        await websocket.close(code=1008, reason="Authentication failed")
                        return False
                    info["authenticated"] = True
                except Exception as e:
                    logger.error(f"Error in authentication: {e}")
                    await websocket.close(code=1011, reason="Authentication error")
                    return False
            
            # Add to active connections
            self.active_connections.append(websocket)
            self.connection_info[websocket] = info
            
            # Call on_connect handler if registered
            if self.on_connect:
                try:
                    await self.on_connect(websocket)
                except Exception as e:
                    logger.error(f"Error in on_connect handler: {e}")
            
            return True
        
        def disconnect(self, websocket: WebSocket) -> None:
            """
            Remove a disconnected WebSocket connection.
            
            Args:
                websocket: The WebSocket connection to remove
            """
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connection_info.pop(websocket, None)
                
                # Call on_disconnect handler if registered
                if self.on_disconnect:
                    try:
                        asyncio.create_task(self.on_disconnect(websocket))
                    except Exception as e:
                        logger.error(f"Error in on_disconnect handler: {e}")
        
        async def process_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
            """
            Process an incoming message.
            
            Args:
                websocket: The WebSocket connection
                message: The message to process
            """
            if websocket not in self.active_connections:
                return
            
            # Extract message type or use default
            message_type = message.get("type", "unknown")
            
            # Check if there is a handler for this message type
            handler = self.message_handlers.get(message_type)
            
            try:
                if handler:
                    # Call the specific handler
                    await handler(websocket, message)
                elif self.default_handler:
                    # Call the default handler
                    await self.default_handler(websocket, message)
                else:
                    logger.debug(f"No handler for message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "request_id": message.get("request_id")
                    })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}",
                        "request_id": message.get("request_id")
                    })
                except Exception:
                    pass
        
        async def handle_connection(self, websocket: WebSocket) -> None:
            """
            Main handler for a WebSocket connection.
            
            This method accepts the connection, processes messages, and handles disconnection.
            
            Args:
                websocket: The WebSocket connection
            """
            connected = await self.connect(websocket)
            if not connected:
                return
            
            try:
                while True:
                    # Receive JSON data
                    try:
                        data = await websocket.receive_json()
                    except json.JSONDecodeError:
                        # Try to receive text
                        text = await websocket.receive_text()
                        try:
                            data = json.loads(text)
                        except json.JSONDecodeError:
                            logger.warning(f"Received non-JSON message: {text[:100]}...")
                            continue
                    
                    # Process the message
                    await self.process_message(websocket, data)
            
            except WebSocketDisconnect:
                # Handle normal disconnection
                self.disconnect(websocket)
            except Exception as e:
                # Handle unexpected errors
                logger.error(f"Error handling WebSocket connection: {e}")
                try:
                    if websocket.client_state != WebSocketState.DISCONNECTED:
                        await websocket.close(code=1011, reason="Internal error")
                except Exception:
                    pass
                self.disconnect(websocket)


# Utility functions

def create_websocket_url(
    host: str,
    port: int,
    path: str = "/ws",
    secure: bool = False
) -> str:
    """
    Create a WebSocket URL.
    
    Args:
        host: Host name or IP address
        port: Port number
        path: URL path
        secure: Whether to use secure WebSocket (wss)
        
    Returns:
        WebSocket URL
    """
    # Add leading slash to path if missing
    if not path.startswith("/"):
        path = f"/{path}"
    
    # Use wss for secure connections
    protocol = "wss" if secure else "ws"
    
    return f"{protocol}://{host}:{port}{path}"


def get_component_websocket_url(
    component_id: str,
    path: str = "/ws",
    secure: bool = False,
    host: Optional[str] = None
) -> str:
    """
    Get the WebSocket URL for a Tekton component.
    
    Args:
        component_id: Component identifier (e.g., "hermes", "engram")
        path: URL path
        secure: Whether to use secure WebSocket (wss)
        host: Host name or IP address (default: "localhost")
        
    Returns:
        WebSocket URL
    """
    # Get port from environment variable
    port_var = f"{component_id.upper()}_PORT"
    port_str = os.environ.get(port_var)
    
    if port_str:
        try:
            port = int(port_str)
        except ValueError:
            # Use known port assignments
            port = _get_standard_port(component_id)
    else:
        # Use known port assignments
        port = _get_standard_port(component_id)
    
    if port is None:
        raise ValueError(f"No port found for component: {component_id}")
    
    return create_websocket_url(
        host=host or "localhost",
        port=port,
        path=path,
        secure=secure
    )


def _get_standard_port(component_id: str) -> Optional[int]:
    """
    Get the standard port for a Tekton component.
    
    Args:
        component_id: Component identifier
        
    Returns:
        Port number or None if not found
    """
    # Standard port assignments
    port_assignments = {
        "engram": 8000,
        "hermes": 8001,
        "ergon": 8002,
        "rhetor": 8003,
        "terma": 8004,
        "athena": 8005,
        "prometheus": 8006,
        "harmonia": 8007,
        "telos": 8008,
        "synthesis": 8009,
        "tekton_core": 8010,
        "hephaestus": 8080
    }
    
    return port_assignments.get(component_id.lower())