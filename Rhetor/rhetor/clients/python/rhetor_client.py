"""
Python client for Rhetor LLM Management System.

This is a high-level client library that Tekton components can use to interact
with the Rhetor LLM Management System.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StreamingResponse:
    """Data class for streaming response chunks."""
    chunk: str
    done: bool
    model: Optional[str] = None
    provider: Optional[str] = None
    context: Optional[str] = None
    error: Optional[str] = None

@dataclass
class CompletionResponse:
    """Data class for completion responses."""
    message: str
    model: Optional[str] = None
    provider: Optional[str] = None
    context: Optional[str] = None
    error: Optional[str] = None

class RhetorClient:
    """Client for interacting with the Rhetor LLM Management System."""
    
    def __init__(
        self,
        rhetor_url: Optional[str] = None,
        component_id: Optional[str] = None,
        default_context: Optional[str] = None,
        auto_reconnect: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialize Rhetor client.
        
        Args:
            rhetor_url: URL for Rhetor API (defaults to http://localhost:8003)
            component_id: ID of the component using the client
            default_context: Default context ID for messages
            auto_reconnect: Whether to automatically attempt reconnection
            max_retries: Maximum number of retry attempts for operations
            retry_delay: Delay between retry attempts in seconds
        """
        self.rhetor_url = rhetor_url or TektonEnviron.get("RHETOR_URL", "http://localhost:8003")
        self.component_id = component_id or TektonEnviron.get("COMPONENT_ID", "component")
        self.default_context = default_context or f"{self.component_id}:default"
        self.auto_reconnect = auto_reconnect
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Internal state
        self.session = None
        self.ws = None
        self.ws_connected = False
        self.reconnecting = False
        self.ws_task = None
        self.message_queue = asyncio.Queue()
        self.pending_requests = {}
        self.event_handlers = {
            "message": [],
            "error": [],
            "connection": []
        }
    
    async def connect(self) -> bool:
        """Connect to the Rhetor service.
        
        Returns:
            Connection success
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
        
        try:
            # Check if Rhetor is available
            async with self.session.get(f"{self.rhetor_url}/health") as response:
                if response.status != 200:
                    logger.warning(f"Rhetor service is not available: {response.status}")
                    return False
            
            # Connect via WebSocket for streaming
            if self.ws_task is None:
                self.ws_task = asyncio.create_task(self._maintain_ws_connection())
            
            return True
        
        except Exception as e:
            logger.warning(f"Error connecting to Rhetor: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the Rhetor service."""
        # Close WebSocket
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.ws_connected = False
        
        # Cancel WebSocket task
        if self.ws_task:
            self.ws_task.cancel()
            try:
                await self.ws_task
            except asyncio.CancelledError:
                pass
            self.ws_task = None
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
    
    async def ensure_connected(self) -> bool:
        """Ensure client is connected to Rhetor.
        
        Returns:
            Connection status
        """
        if self.session is None:
            return await self.connect()
        return True
    
    async def _maintain_ws_connection(self) -> None:
        """Maintain WebSocket connection with automatic reconnection."""
        while True:
            try:
                if not self.ws_connected and not self.reconnecting:
                    self.reconnecting = True
                    
                    # Connect to WebSocket
                    self.ws = await self.session.ws_connect(f"{self.rhetor_url}/ws")
                    self.ws_connected = True
                    self.reconnecting = False
                    
                    # Call connection handlers
                    for handler in self.event_handlers["connection"]:
                        try:
                            await handler(True)
                        except Exception as e:
                            logger.error(f"Error in connection handler: {e}")
                    
                    # Start message handling task
                    asyncio.create_task(self._handle_ws_messages())
                    
                    # Register with server
                    await self.ws.send_json({
                        "type": "REGISTER",
                        "source": self.component_id,
                        "timestamp": self._get_timestamp(),
                        "payload": {
                            "component_id": self.component_id
                        }
                    })
                
                # Process outgoing messages
                try:
                    # Non-blocking get with timeout
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                    if self.ws_connected:
                        await self.ws.send_json(message)
                    self.message_queue.task_done()
                except asyncio.TimeoutError:
                    # No messages to send, continue
                    pass
            
            except Exception as e:
                logger.warning(f"WebSocket connection error: {e}")
                
                # Mark as disconnected
                self.ws_connected = False
                
                # Call connection handlers
                for handler in self.event_handlers["connection"]:
                    try:
                        await handler(False)
                    except Exception as e:
                        logger.error(f"Error in connection handler: {e}")
                
                # Retry connecting after delay
                if self.auto_reconnect:
                    await asyncio.sleep(self.retry_delay)
                else:
                    break
    
    async def _handle_ws_messages(self) -> None:
        """Handle incoming WebSocket messages."""
        if not self.ws:
            return
        
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    message_type = data.get("type")
                    
                    # Handle response
                    if message_type == "RESPONSE":
                        request_id = data.get("req_id")
                        if request_id and request_id in self.pending_requests:
                            future = self.pending_requests.pop(request_id)
                            future.set_result(data.get("payload", {}))
                        
                        # Call message handlers
                        for handler in self.event_handlers["message"]:
                            try:
                                await handler(data)
                            except Exception as e:
                                logger.error(f"Error in message handler: {e}")
                    
                    # Handle error
                    elif message_type == "ERROR":
                        request_id = data.get("req_id")
                        if request_id and request_id in self.pending_requests:
                            future = self.pending_requests.pop(request_id)
                            future.set_exception(Exception(data.get("payload", {}).get("error", "Unknown error")))
                        
                        # Call error handlers
                        for handler in self.event_handlers["error"]:
                            try:
                                await handler(data.get("payload", {}))
                            except Exception as e:
                                logger.error(f"Error in error handler: {e}")
                
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    logger.warning("WebSocket closed or error")
                    self.ws_connected = False
                    break
        
        except Exception as e:
            logger.error(f"Error handling WebSocket messages: {e}")
            self.ws_connected = False
    
    def _get_timestamp(self) -> str:
        """Get ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def on_message(self, handler: Callable) -> None:
        """Register message event handler.
        
        Args:
            handler: Async function to call when a message is received
        """
        self.event_handlers["message"].append(handler)
    
    def on_error(self, handler: Callable) -> None:
        """Register error event handler.
        
        Args:
            handler: Async function to call when an error occurs
        """
        self.event_handlers["error"].append(handler)
    
    def on_connection(self, handler: Callable) -> None:
        """Register connection event handler.
        
        Args:
            handler: Async function to call when connection status changes
        """
        self.event_handlers["connection"].append(handler)
    
    async def complete(
        self,
        message: str,
        context_id: Optional[str] = None,
        task_type: str = "default",
        options: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> CompletionResponse:
        """Send a message to Rhetor and get a completion.
        
        Args:
            message: The message to send
            context_id: The context ID (defaults to component's default context)
            task_type: The task type (e.g., "chat", "code", "planning")
            options: Additional options for the LLM
            timeout: Request timeout in seconds
            
        Returns:
            CompletionResponse with message and metadata
            
        Raises:
            Exception: If the request fails
        """
        # Ensure connected
        if not await self.ensure_connected():
            raise Exception("Not connected to Rhetor")
        
        context = context_id or self.default_context
        
        for retry in range(self.max_retries):
            try:
                async with self.session.post(
                    f"{self.rhetor_url}/message",
                    json={
                        "message": message,
                        "context_id": context,
                        "task_type": task_type,
                        "component": self.component_id,
                        "streaming": False,
                        "options": options or {}
                    },
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "error" in data and data["error"]:
                            return CompletionResponse(
                                message="",
                                error=data["error"],
                                context=context
                            )
                        
                        return CompletionResponse(
                            message=data.get("message", ""),
                            model=data.get("model"),
                            provider=data.get("provider"),
                            context=context,
                            error=None
                        )
                    else:
                        error_text = await response.text()
                        if retry == self.max_retries - 1:
                            raise Exception(f"HTTP error {response.status}: {error_text}")
                        
                        # Wait before retrying
                        await asyncio.sleep(self.retry_delay)
            
            except asyncio.TimeoutError:
                if retry == self.max_retries - 1:
                    raise Exception(f"Request timed out after {timeout} seconds")
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
            
            except Exception as e:
                if retry == self.max_retries - 1:
                    raise
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
        
        # Should never reach here
        raise Exception("Unexpected error in complete()")
    
    async def stream(
        self,
        message: str,
        context_id: Optional[str] = None,
        task_type: str = "default",
        options: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
        use_sse: bool = True
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Stream a completion from Rhetor.
        
        Args:
            message: The message to send
            context_id: The context ID (defaults to component's default context)
            task_type: The task type (e.g., "chat", "code", "planning")
            options: Additional options for the LLM
            timeout: Request timeout in seconds
            use_sse: Whether to use server-sent events (SSE) or WebSocket
            
        Yields:
            StreamingResponse chunks as they arrive
            
        Raises:
            Exception: If the request fails
        """
        # Ensure connected
        if not await self.ensure_connected():
            raise Exception("Not connected to Rhetor")
        
        context = context_id or self.default_context
        
        # Prefer WebSocket if available, otherwise fallback to SSE
        if self.ws_connected and not use_sse:
            # Use WebSocket for streaming
            request_id = f"{self.component_id}:{self._get_timestamp()}"
            
            # Create future for first response
            future = asyncio.Future()
            self.pending_requests[request_id] = future
            
            # Send request
            await self.message_queue.put({
                "type": "LLM_REQUEST",
                "source": self.component_id,
                "req_id": request_id,
                "timestamp": self._get_timestamp(),
                "payload": {
                    "message": message,
                    "context": context,
                    "task_type": task_type,
                    "component": self.component_id,
                    "streaming": True,
                    "options": options or {}
                }
            })
            
            # Create queue for streaming chunks
            queue = asyncio.Queue()
            
            # Register one-time handler for streaming
            async def stream_handler(data):
                if data.get("req_id") == request_id:
                    payload = data.get("payload", {})
                    
                    if data.get("type") == "UPDATE":
                        # Put chunk in queue
                        await queue.put(StreamingResponse(
                            chunk=payload.get("chunk", ""),
                            done=payload.get("done", False),
                            model=payload.get("model"),
                            provider=payload.get("provider"),
                            context=context,
                            error=payload.get("error")
                        ))
                        
                        # Remove handler if done
                        if payload.get("done", False):
                            if stream_handler in self.event_handlers["message"]:
                                self.event_handlers["message"].remove(stream_handler)
                    
                    elif data.get("type") == "ERROR":
                        # Put error in queue
                        await queue.put(StreamingResponse(
                            chunk="",
                            done=True,
                            context=context,
                            error=payload.get("error", "Unknown error")
                        ))
                        
                        # Remove handler
                        if stream_handler in self.event_handlers["message"]:
                            self.event_handlers["message"].remove(stream_handler)
            
            # Add handler
            self.on_message(stream_handler)
            
            # Wait for first response or timeout
            try:
                await asyncio.wait_for(future, timeout)
                
                # Start yielding chunks
                while True:
                    try:
                        chunk = await asyncio.wait_for(queue.get(), timeout)
                        yield chunk
                        queue.task_done()
                        
                        if chunk.done:
                            break
                    except asyncio.TimeoutError:
                        raise Exception(f"Streaming response timed out after {timeout} seconds")
            
            except asyncio.TimeoutError:
                # Remove handler
                if stream_handler in self.event_handlers["message"]:
                    self.event_handlers["message"].remove(stream_handler)
                
                raise Exception(f"Streaming request timed out after {timeout} seconds")
            
            except Exception as e:
                # Remove handler
                if stream_handler in self.event_handlers["message"]:
                    self.event_handlers["message"].remove(stream_handler)
                
                raise
        
        else:
            # Use SSE for streaming
            for retry in range(self.max_retries):
                try:
                    async with self.session.post(
                        f"{self.rhetor_url}/stream",
                        json={
                            "message": message,
                            "context_id": context,
                            "task_type": task_type,
                            "component": self.component_id,
                            "options": options or {}
                        },
                        timeout=timeout
                    ) as response:
                        if response.status == 200:
                            # Parse the SSE stream
                            full_text = ""
                            
                            async for line in response.content:
                                line = line.decode('utf-8').strip()
                                
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])
                                        
                                        # Create response
                                        chunk = data.get("chunk", "")
                                        full_text += chunk
                                        
                                        yield StreamingResponse(
                                            chunk=chunk,
                                            done=data.get("done", False),
                                            model=data.get("model"),
                                            provider=data.get("provider"),
                                            context=context,
                                            error=data.get("error")
                                        )
                                        
                                        if data.get("done", False):
                                            break
                                    
                                    except json.JSONDecodeError:
                                        logger.warning(f"Invalid JSON in SSE stream: {line[6:]}")
                            
                            return
                        else:
                            error_text = await response.text()
                            if retry == self.max_retries - 1:
                                raise Exception(f"HTTP error {response.status}: {error_text}")
                            
                            # Wait before retrying
                            await asyncio.sleep(self.retry_delay)
                
                except asyncio.TimeoutError:
                    if retry == self.max_retries - 1:
                        raise Exception(f"Streaming request timed out after {timeout} seconds")
                    
                    # Wait before retrying
                    await asyncio.sleep(self.retry_delay)
                
                except Exception as e:
                    if retry == self.max_retries - 1:
                        raise
                    
                    # Wait before retrying
                    await asyncio.sleep(self.retry_delay)
    
    async def get_providers(self) -> Dict[str, Any]:
        """Get available LLM providers.
        
        Returns:
            Dictionary of available providers and models
            
        Raises:
            Exception: If the request fails
        """
        # Ensure connected
        if not await self.ensure_connected():
            raise Exception("Not connected to Rhetor")
        
        for retry in range(self.max_retries):
            try:
                async with self.session.get(
                    f"{self.rhetor_url}/providers"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        if retry == self.max_retries - 1:
                            raise Exception(f"HTTP error {response.status}: {error_text}")
                        
                        # Wait before retrying
                        await asyncio.sleep(self.retry_delay)
            
            except Exception as e:
                if retry == self.max_retries - 1:
                    raise
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
        
        # Should never reach here
        raise Exception("Unexpected error in get_providers()")
    
    async def set_provider(
        self,
        provider_id: str,
        model_id: str
    ) -> bool:
        """Set the active provider and model.
        
        Args:
            provider_id: Provider ID
            model_id: Model ID
            
        Returns:
            Success status
            
        Raises:
            Exception: If the request fails
        """
        # Ensure connected
        if not await self.ensure_connected():
            raise Exception("Not connected to Rhetor")
        
        for retry in range(self.max_retries):
            try:
                async with self.session.post(
                    f"{self.rhetor_url}/provider",
                    json={
                        "provider_id": provider_id,
                        "model_id": model_id
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("success", False)
                    else:
                        error_text = await response.text()
                        if retry == self.max_retries - 1:
                            raise Exception(f"HTTP error {response.status}: {error_text}")
                        
                        # Wait before retrying
                        await asyncio.sleep(self.retry_delay)
            
            except Exception as e:
                if retry == self.max_retries - 1:
                    raise
                
                # Wait before retrying
                await asyncio.sleep(self.retry_delay)
        
        # Should never reach here
        raise Exception("Unexpected error in set_provider()")
    
    # Simple easy-to-use methods for common tasks
    
    async def ask(
        self,
        question: str,
        context_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Ask a question and get a response.
        
        Args:
            question: The question to ask
            context_id: Optional context ID
            options: Additional options for the LLM
            stream: Whether to stream the response
            
        Returns:
            String response or streaming generator
            
        Raises:
            Exception: If the request fails
        """
        if stream:
            # Return a generator that yields text chunks
            async def text_generator():
                async for chunk in self.stream(
                    message=question,
                    context_id=context_id,
                    task_type="chat",
                    options=options
                ):
                    if chunk.error:
                        raise Exception(chunk.error)
                    yield chunk.chunk
            
            return text_generator()
        else:
            # Return the complete response
            response = await self.complete(
                message=question,
                context_id=context_id,
                task_type="chat",
                options=options
            )
            
            if response.error:
                raise Exception(response.error)
            
            return response.message
    
    async def code(
        self,
        task: str,
        context_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """Generate code for a task.
        
        Args:
            task: The coding task description
            context_id: Optional context ID
            options: Additional options for the LLM
            stream: Whether to stream the response
            
        Returns:
            String response or streaming generator
            
        Raises:
            Exception: If the request fails
        """
        # Set default options for code generation
        code_options = {
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        # Merge with user options
        if options:
            code_options.update(options)
        
        if stream:
            # Return a generator that yields text chunks
            async def text_generator():
                async for chunk in self.stream(
                    message=task,
                    context_id=context_id,
                    task_type="code",
                    options=code_options
                ):
                    if chunk.error:
                        raise Exception(chunk.error)
                    yield chunk.chunk
            
            return text_generator()
        else:
            # Return the complete response
            response = await self.complete(
                message=task,
                context_id=context_id,
                task_type="code",
                options=code_options
            )
            
            if response.error:
                raise Exception(response.error)
            
            return response.message


# Singleton client instance for simple imports
_client_instance = None

async def get_client(
    component_id: Optional[str] = None,
    rhetor_url: Optional[str] = None
) -> RhetorClient:
    """Get a configured Rhetor client instance.
    
    Args:
        component_id: ID of the component using the client
        rhetor_url: URL for Rhetor API
        
    Returns:
        Configured RhetorClient
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = RhetorClient(
            rhetor_url=rhetor_url,
            component_id=component_id
        )
        await _client_instance.connect()
    
    return _client_instance