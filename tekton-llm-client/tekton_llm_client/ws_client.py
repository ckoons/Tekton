"""
WebSocket client for interacting with Tekton LLM services.
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Callable
from urllib.parse import urljoin

import websockets
import aiohttp

from .exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    AuthenticationError, ServiceUnavailableError
)
from .models import Message, CompletionOptions, StreamingChunk

logger = logging.getLogger(__name__)

class TektonLLMWebSocketClient:
    """WebSocket client for interacting with Tekton LLM services."""
    
    def __init__(
        self,
        component_id: str,
        rhetor_url: Optional[str] = None,
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        reconnect_interval: int = 5000,
        auth_token: Optional[str] = None
    ):
        """
        Initialize the WebSocket client.
        
        Args:
            component_id: ID of the component using the client (used for tracking)
            rhetor_url: URL for the Rhetor API (defaults to RHETOR_WS_URL env var or ws://localhost:8003/ws)
            on_message: Callback for incoming messages
            on_error: Callback for errors
            on_close: Callback for connection closures
            reconnect_interval: Interval in milliseconds to attempt reconnection
            auth_token: Optional authentication token for Rhetor API
        """
        # Load settings from environment variables with defaults
        self.component_id = component_id
        
        # Determine the WebSocket URL
        http_url = rhetor_url or os.environ.get("RHETOR_URL", "http://localhost:8003")
        ws_url = os.environ.get("RHETOR_WS_URL")
        
        if not ws_url:
            # Convert HTTP URL to WebSocket URL
            if http_url.startswith("https://"):
                ws_url = http_url.replace("https://", "wss://")
            else:
                ws_url = http_url.replace("http://", "ws://")
                
            # Append '/ws' path if it's not already there
            if not ws_url.endswith("/ws"):
                ws_url = ws_url.rstrip("/") + "/ws"
        
        self.ws_url = ws_url
        self.auth_token = auth_token or os.environ.get("RHETOR_AUTH_TOKEN")
        self.reconnect_interval = reconnect_interval
        
        # Callbacks
        self.on_message_callback = on_message
        self.on_error_callback = on_error
        self.on_close_callback = on_close
        
        # WebSocket connection state
        self.ws = None
        self.connected = False
        self.connecting = False
        self.should_reconnect = True
        self.reconnect_task = None
        
        # Message handlers for request/response tracking
        self.message_handlers = {}
        self.request_counter = 0
        
        logger.info(
            f"Initialized TektonLLMWebSocketClient for component '{component_id}' "
            f"with WebSocket URL: {self.ws_url}"
        )
    
    async def connect(self) -> bool:
        """
        Connect to the WebSocket server.
        
        Returns:
            True if connection was successful, False otherwise
        """
        if self.connected:
            return True
            
        if self.connecting:
            # Wait for existing connection attempt to complete
            for _ in range(10):  # Wait for up to 1 second
                await asyncio.sleep(0.1)
                if self.connected:
                    return True
                if not self.connecting:
                    break
            # If still connecting after waiting, consider it failed
            if self.connecting:
                return False
        
        self.connecting = True
        
        try:
            # Establish WebSocket connection
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            self.ws = await websockets.connect(
                self.ws_url,
                extra_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            # Register the client with the server
            await self._register()
            
            # Start the message processing loop
            asyncio.create_task(self._process_messages())
            
            self.connected = True
            self.connecting = False
            
            logger.info(f"WebSocket connection established for component '{self.component_id}'")
            return True
            
        except Exception as e:
            self.connected = False
            self.connecting = False
            logger.error(f"Failed to connect to WebSocket server: {str(e)}")
            
            # Trigger on_error callback if provided
            if self.on_error_callback:
                self.on_error_callback(e)
                
            # Start reconnection task if needed
            if self.should_reconnect and not self.reconnect_task:
                self.reconnect_task = asyncio.create_task(self._reconnect_loop())
                
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        self.should_reconnect = False
        
        # Cancel reconnection task if running
        if self.reconnect_task:
            self.reconnect_task.cancel()
            self.reconnect_task = None
        
        if self.ws:
            await self.ws.close()
            self.ws = None
            
        self.connected = False
        self.connecting = False
        
        logger.info(f"WebSocket connection closed for component '{self.component_id}'")
        
        # Trigger on_close callback if provided
        if self.on_close_callback:
            self.on_close_callback()
    
    async def generate(
        self,
        prompt: str,
        context_id: str = "default",
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using the LLM via WebSocket.
        
        Args:
            prompt: The user prompt
            context_id: Context ID for tracking conversation
            system_prompt: Optional system instructions
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Additional options for the LLM
            
        Returns:
            Dictionary with the complete response
        """
        if not await self.connect():
            raise ConnectionError("Failed to connect to WebSocket server")
            
        request_id = f"{self.component_id}_{int(time.time())}_{self.request_counter}"
        self.request_counter += 1
        
        # Create the request message
        request = {
            "type": "GENERATE",
            "request_id": request_id,
            "prompt": prompt,
            "context_id": context_id,
            "options": options or {}
        }
        
        if system_prompt:
            request["system_prompt"] = system_prompt
            
        if provider_id:
            request["provider_id"] = provider_id
            
        if model_id:
            request["model_id"] = model_id
        
        # Create a future for the response
        response_future = asyncio.Future()
        
        # Register the response handler
        self.message_handlers[request_id] = response_future
        
        try:
            # Send the request
            await self.ws.send(json.dumps(request))
            
            # Wait for the response with timeout
            timeout = options.get("timeout", 120) if options else 120
            response = await asyncio.wait_for(response_future, timeout=timeout)
            
            return response
            
        except asyncio.TimeoutError:
            # Remove the handler on timeout
            self.message_handlers.pop(request_id, None)
            raise TimeoutError(f"Request timed out after {timeout} seconds")
            
        except Exception as e:
            # Remove the handler on error
            self.message_handlers.pop(request_id, None)
            raise TektonLLMError(f"Error generating response: {str(e)}")
    
    async def stream(
        self,
        prompt: str,
        callback: Callable[[StreamingChunk], None],
        context_id: str = "default",
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Stream a response from the LLM via WebSocket.
        
        Args:
            prompt: The user prompt
            callback: Callback function for each chunk
            context_id: Context ID for tracking conversation
            system_prompt: Optional system instructions
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Additional options for the LLM
            
        Returns:
            Request ID that can be used to cancel the request
        """
        if not await self.connect():
            raise ConnectionError("Failed to connect to WebSocket server")
            
        request_id = f"{self.component_id}_{int(time.time())}_{self.request_counter}"
        self.request_counter += 1
        
        # Create the request message
        request = {
            "type": "STREAM",
            "request_id": request_id,
            "prompt": prompt,
            "context_id": context_id,
            "options": options or {}
        }
        
        if system_prompt:
            request["system_prompt"] = system_prompt
            
        if provider_id:
            request["provider_id"] = provider_id
            
        if model_id:
            request["model_id"] = model_id
        
        # Register the streaming handler
        self.message_handlers[request_id] = callback
        
        try:
            # Send the request
            await self.ws.send(json.dumps(request))
            
            # Return the request ID for possible cancellation
            return request_id
            
        except Exception as e:
            # Remove the handler on error
            self.message_handlers.pop(request_id, None)
            raise TektonLLMError(f"Error starting stream: {str(e)}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        context_id: str = "default",
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat request via WebSocket.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            context_id: Context ID for tracking conversation
            system_prompt: Optional system instructions
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Additional options for the LLM
            
        Returns:
            Dictionary with the complete response
        """
        if not await self.connect():
            raise ConnectionError("Failed to connect to WebSocket server")
            
        request_id = f"{self.component_id}_{int(time.time())}_{self.request_counter}"
        self.request_counter += 1
        
        # Create the request message
        request = {
            "type": "CHAT",
            "request_id": request_id,
            "messages": messages,
            "context_id": context_id,
            "options": options or {}
        }
        
        if system_prompt:
            request["system_prompt"] = system_prompt
            
        if provider_id:
            request["provider_id"] = provider_id
            
        if model_id:
            request["model_id"] = model_id
        
        # Create a future for the response
        response_future = asyncio.Future()
        
        # Register the response handler
        self.message_handlers[request_id] = response_future
        
        try:
            # Send the request
            await self.ws.send(json.dumps(request))
            
            # Wait for the response with timeout
            timeout = options.get("timeout", 120) if options else 120
            response = await asyncio.wait_for(response_future, timeout=timeout)
            
            return response
            
        except asyncio.TimeoutError:
            # Remove the handler on timeout
            self.message_handlers.pop(request_id, None)
            raise TimeoutError(f"Request timed out after {timeout} seconds")
            
        except Exception as e:
            # Remove the handler on error
            self.message_handlers.pop(request_id, None)
            raise TektonLLMError(f"Error generating chat response: {str(e)}")
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        callback: Callable[[StreamingChunk], None],
        context_id: str = "default",
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Stream a chat response via WebSocket.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            callback: Callback function for each chunk
            context_id: Context ID for tracking conversation
            system_prompt: Optional system instructions
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Additional options for the LLM
            
        Returns:
            Request ID that can be used to cancel the request
        """
        if not await self.connect():
            raise ConnectionError("Failed to connect to WebSocket server")
            
        request_id = f"{self.component_id}_{int(time.time())}_{self.request_counter}"
        self.request_counter += 1
        
        # Create the request message
        request = {
            "type": "CHAT_STREAM",
            "request_id": request_id,
            "messages": messages,
            "context_id": context_id,
            "options": options or {}
        }
        
        if system_prompt:
            request["system_prompt"] = system_prompt
            
        if provider_id:
            request["provider_id"] = provider_id
            
        if model_id:
            request["model_id"] = model_id
        
        # Register the streaming handler
        self.message_handlers[request_id] = callback
        
        try:
            # Send the request
            await self.ws.send(json.dumps(request))
            
            # Return the request ID for possible cancellation
            return request_id
            
        except Exception as e:
            # Remove the handler on error
            self.message_handlers.pop(request_id, None)
            raise TektonLLMError(f"Error starting chat stream: {str(e)}")
    
    async def cancel(self, request_id: str) -> bool:
        """
        Cancel an ongoing generation request.
        
        Args:
            request_id: The request ID to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        if not self.connected or not self.ws:
            return False
            
        if request_id not in self.message_handlers:
            return False
            
        try:
            # Send cancellation request
            await self.ws.send(json.dumps({
                "type": "CANCEL",
                "request_id": request_id
            }))
            
            # Remove the handler
            self.message_handlers.pop(request_id, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Error canceling request: {str(e)}")
            return False
    
    async def _register(self):
        """Register the client with the WebSocket server."""
        if not self.ws:
            raise ConnectionError("WebSocket connection not established")
            
        # Send registration message
        registration = {
            "type": "REGISTER",
            "component_id": self.component_id,
            "capabilities": ["chat", "stream"]
        }
        
        await self.ws.send(json.dumps(registration))
        
        # Wait for registration acknowledgment
        for _ in range(5):  # Wait for up to 5 seconds
            response = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
            try:
                data = json.loads(response)
                if data.get("type") == "REGISTER_ACK":
                    logger.info(f"Registration successful for component '{self.component_id}'")
                    return
            except json.JSONDecodeError:
                continue
                
        raise ConnectionError("Failed to receive registration acknowledgment")
    
    async def _process_messages(self):
        """Process incoming WebSocket messages."""
        if not self.ws:
            return
            
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Received invalid JSON: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connected = False
            
            # Trigger on_close callback if provided
            if self.on_close_callback:
                self.on_close_callback()
                
            # Reject all pending requests
            for request_id, handler in list(self.message_handlers.items()):
                if isinstance(handler, asyncio.Future):
                    if not handler.done():
                        handler.set_exception(ConnectionError("WebSocket connection closed"))
                elif callable(handler):
                    # For streaming handlers, send an error chunk
                    try:
                        handler(StreamingChunk(
                            chunk="",
                            context_id="",
                            model="",
                            provider="",
                            timestamp="",
                            done=True,
                            error="WebSocket connection closed"
                        ))
                    except Exception as callback_error:
                        logger.error(f"Error in streaming callback: {str(callback_error)}")
                        
            # Clear handlers
            self.message_handlers.clear()
            
            # Start reconnection task if needed
            if self.should_reconnect and not self.reconnect_task:
                self.reconnect_task = asyncio.create_task(self._reconnect_loop())
        except Exception as e:
            logger.error(f"Error in message processing loop: {str(e)}")
            
            # Trigger on_error callback if provided
            if self.on_error_callback:
                self.on_error_callback(e)
    
    async def _handle_message(self, data: Dict[str, Any]):
        """
        Handle an incoming WebSocket message.
        
        Args:
            data: The parsed message data
        """
        message_type = data.get("type", "")
        request_id = data.get("request_id", "")
        
        # Call the general message callback if provided
        if self.on_message_callback:
            self.on_message_callback(data)
        
        if message_type == "RESPONSE":
            # Handle a complete response to a non-streaming request
            if request_id in self.message_handlers:
                handler = self.message_handlers.pop(request_id)
                if isinstance(handler, asyncio.Future) and not handler.done():
                    handler.set_result(data)
                    
        elif message_type == "CHUNK":
            # Handle a chunk of a streaming response
            if request_id in self.message_handlers:
                handler = self.message_handlers[request_id]
                if callable(handler):
                    # Convert to StreamingChunk and call the handler
                    chunk = StreamingChunk(
                        chunk=data.get("chunk", ""),
                        context_id=data.get("context_id", ""),
                        model=data.get("model", ""),
                        provider=data.get("provider", ""),
                        timestamp=data.get("timestamp", ""),
                        done=data.get("done", False),
                        error=data.get("error")
                    )
                    
                    handler(chunk)
                    
                    # Remove the handler if this is the final chunk
                    if data.get("done", False):
                        self.message_handlers.pop(request_id, None)
                        
        elif message_type == "ERROR":
            # Handle an error response
            if request_id in self.message_handlers:
                handler = self.message_handlers.pop(request_id)
                error_message = data.get("error", "Unknown error")
                
                if isinstance(handler, asyncio.Future) and not handler.done():
                    handler.set_exception(TektonLLMError(error_message))
                elif callable(handler):
                    # For streaming handlers, send an error chunk
                    chunk = StreamingChunk(
                        chunk="",
                        context_id=data.get("context_id", ""),
                        model=data.get("model", ""),
                        provider=data.get("provider", ""),
                        timestamp=data.get("timestamp", ""),
                        done=True,
                        error=error_message
                    )
                    
                    handler(chunk)
            
            # Also trigger on_error callback if provided
            if self.on_error_callback:
                self.on_error_callback(TektonLLMError(data.get("error", "Unknown error")))
                
        elif message_type == "PING":
            # Respond to ping with a pong
            if self.ws:
                await self.ws.send(json.dumps({"type": "PONG"}))
    
    async def _reconnect_loop(self):
        """Reconnection loop that attempts to reestablish connection."""
        while self.should_reconnect and not self.connected:
            logger.info(f"Attempting to reconnect in {self.reconnect_interval/1000:.1f} seconds...")
            await asyncio.sleep(self.reconnect_interval / 1000)
            
            if not self.should_reconnect:
                break
                
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {str(e)}")
                
        self.reconnect_task = None