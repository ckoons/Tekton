#!/usr/bin/env python3
"""
Shared socket client for AI communication.

This module provides a robust async socket client for communicating with
Greek Chorus AI specialists using newline-delimited JSON protocol.

Features:
- Async/await support with streaming
- Configurable timeouts
- Robust error handling
- Connection pooling
- Automatic retry logic
- Native streaming support

Used by both Tekton components and aish for consistent AI communication.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Tuple, Callable, AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from landmarks import (
    architecture_decision,
    performance_boundary,
    integration_point,
    state_checkpoint,
    danger_zone
)

# Import connection pool if available
try:
    from .connection_pool import get_connection_pool
    HAS_CONNECTION_POOL = True
except ImportError:
    HAS_CONNECTION_POOL = False

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Supported message types"""
    CHAT = "chat"  # For Greek Chorus AIs
    MESSAGE = "message"  # For team chat
    PING = "ping"
    STREAM = "stream"
    CHUNK = "chunk"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class StreamChunk:
    """Represents a streaming chunk"""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    is_final: bool = False


@architecture_decision(
    title="Unified AI Socket Client Architecture",
    rationale="Centralize all AI socket communication to ensure consistent protocol handling and error management",
    alternatives_considered=["Individual socket implementations per component", "REST API only", "gRPC"],
    impacts=["reliability", "performance", "maintainability"],
    decided_by="Casey"
)
@integration_point(
    title="Greek Chorus AI Integration",
    target_component="Greek Chorus AIs (ports 45000-50000)",
    protocol="Socket/NDJSON",
    data_flow="Bidirectional message exchange with streaming support"
)
class AISocketClient:
    """
    Async socket client for AI specialist communication.
    
    Features:
    - Async/await support
    - Native streaming
    - Configurable timeouts
    - Robust error handling
    - Connection pooling
    - Automatic retry logic
    """
    
    def __init__(self, 
                 default_timeout: float = 30.0,
                 connection_timeout: float = 2.0,
                 max_retries: int = 1,
                 debug: bool = False):
        """
        Initialize AI socket client.
        
        Args:
            default_timeout: Default response timeout in seconds
            connection_timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            debug: Enable debug logging
        """
        self.default_timeout = default_timeout
        self.connection_timeout = connection_timeout
        self.max_retries = max_retries
        self.debug = debug
        # Use global connection pool instead of local one
        self._global_pool = None
        self._pool_initialized = False
    
    async def _ensure_pool_initialized(self):
        """Ensure connection pool is initialized (lazy init)"""
        if not self._pool_initialized and HAS_CONNECTION_POOL:
            try:
                self._global_pool = await get_connection_pool()
                self._pool_initialized = True
                if self.debug:
                    logger.debug("Initialized global connection pool")
            except Exception as e:
                if self.debug:
                    logger.debug(f"Failed to initialize connection pool: {e}")
                self._global_pool = None
                self._pool_initialized = True  # Don't retry
        
    @performance_boundary(
        title="AI Socket Message Exchange",
        sla="<30s timeout per message",
        optimization_notes="Uses connection pooling and exponential backoff retry",
        metrics={"default_timeout": "30s", "max_retries": 3}
    )
    async def send_message(self,
                          host: str,
                          port: int,
                          message: str,
                          context: Optional[Dict[str, Any]] = None,
                          timeout: Optional[float] = None,
                          temperature: Optional[float] = None,
                          max_tokens: Optional[int] = None,
                          _internal_health_check: bool = False) -> Dict[str, Any]:
        """
        Send a message to an AI specialist and get response.
        
        Args:
            host: Host address (usually localhost)
            port: Port number (45000-50000 for Greek Chorus)
            message: The message content
            context: Optional context dictionary
            timeout: Response timeout (uses default if not specified)
            temperature: Optional temperature for response
            max_tokens: Optional max tokens for response
            _internal_health_check: Internal flag for health checks
            
        Returns:
            Dict containing response with success status
            
        Example response:
            {
                "success": True,
                "response": "AI response text",
                "ai_id": "athena-ai",
                "model": "llama3.3:70b",
                "elapsed_time": 2.5
            }
        """
        # Ensure pool is initialized (lazy init)
        await self._ensure_pool_initialized()
        
        # Use global connection pool if available
        if self._global_pool and not _internal_health_check:
            try:
                # Find AI ID from registry if possible
                ai_id = f"{host}:{port}"
                
                result = await self._global_pool.send_message(
                    ai_id=ai_id,
                    host=host,
                    port=port,
                    message=message,
                    context=context,
                    timeout=timeout or self.default_timeout
                )
                
                # Make response format consistent with existing code
                if result.get('success'):
                    return {
                        "success": True,
                        "response": result.get('response', ''),
                        "ai_id": result.get('ai_id', ai_id),
                        "model": result.get('model', 'unknown'),
                        "elapsed_time": result.get('elapsed_time', 0),
                        "connection_reused": result.get('connection_reused', False)
                    }
                else:
                    # Fall through to direct connection on failure
                    if self.debug:
                        logger.debug(f"Pool failed for {ai_id}: {result.get('error')}, using direct connection")
            except Exception as e:
                if self.debug:
                    logger.debug(f"Connection pool error: {e}, falling back to direct connection")
                # Fall through to direct connection
        
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        # Prepare request
        request = {
            "type": "chat",  # Greek Chorus AIs expect "chat" not "message"
            "content": message
        }
        
        if context:
            request["context"] = context
        if temperature is not None:
            request["temperature"] = temperature
        if max_tokens is not None:
            request["max_tokens"] = max_tokens
        if _internal_health_check:
            request["_health_check"] = True
            
        # Try to send with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.connection_timeout
                )
                
                # Send request
                request_data = json.dumps(request).encode('utf-8') + b'\n'
                writer.write(request_data)
                await writer.drain()
                
                # Read response
                response_data = await asyncio.wait_for(
                    reader.readline(),
                    timeout=timeout
                )
                
                writer.close()
                await writer.wait_closed()
                
                if not response_data:
                    raise ConnectionError("No response received")
                
                response = json.loads(response_data.decode('utf-8').strip())
                elapsed_time = time.time() - start_time
                
                # Process response
                if response.get('type') == 'error':
                    return {
                        "success": False,
                        "error": response.get('message', 'Unknown error'),
                        "elapsed_time": elapsed_time
                    }
                
                # Extract content
                content = response.get('content', response.get('response', ''))
                
                return {
                    "success": True,
                    "response": content,
                    "ai_id": response.get('ai_id', f"{host}:{port}"),
                    "model": response.get('model', 'unknown'),
                    "elapsed_time": elapsed_time,
                    "raw_response": response
                }
                
            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout}s"
                if self.debug:
                    logger.debug(f"Attempt {attempt + 1} failed: {last_error}")
            except ConnectionRefusedError:
                last_error = f"Connection refused to {host}:{port}"
                if self.debug:
                    logger.debug(f"Attempt {attempt + 1} failed: {last_error}")
            except Exception as e:
                last_error = str(e)
                if self.debug:
                    logger.debug(f"Attempt {attempt + 1} failed: {last_error}")
                
            if attempt < self.max_retries:
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                
        return {
            "success": False,
            "error": last_error or "Unknown error",
            "elapsed_time": time.time() - start_time
        }
    
    @architecture_decision(
        title="Native Streaming Support",
        rationale="Support real-time streaming responses for better UX and reduced latency",
        alternatives_considered=["Polling", "Long polling", "WebSockets"],
        impacts=["user_experience", "memory_usage", "complexity"],
        decided_by="Casey"
    )
    @performance_boundary(
        title="Streaming Response Handler",
        sla="<100ms first token latency",
        optimization_notes="Yields chunks immediately without buffering",
        metrics={"chunk_size": "4KB", "protocol": "NDJSON"}
    )
    @integration_point(
        title="Streaming Protocol for Greek Chorus AIs",
        target_component="AI Specialists",
        protocol="Socket/NDJSON streaming",
        data_flow="Request with stream=True → Chunks via NDJSON → Complete signal"
    )
    async def send_message_stream(self,
                                 host: str,
                                 port: int,
                                 message: str,
                                 context: Optional[Dict[str, Any]] = None,
                                 timeout: Optional[float] = None,
                                 temperature: Optional[float] = None,
                                 max_tokens: Optional[int] = None) -> AsyncIterator[StreamChunk]:
        """
        Send a message and stream the response.
        
        Args:
            host: Host address
            port: Port number
            message: The message content
            context: Optional context dictionary
            timeout: Response timeout
            temperature: Optional temperature
            max_tokens: Optional max tokens
            
        Yields:
            StreamChunk objects containing response chunks
            
        Example usage:
            async for chunk in client.send_message_stream(host, port, "Hello"):
                print(chunk.content, end='', flush=True)
                if chunk.is_final:
                    print(f"\nModel: {chunk.metadata.get('model')}")
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        # Prepare request
        request = {
            "type": "chat",  # Greek Chorus AIs expect "chat" not "message"
            "content": message,
            "stream": True,  # Request streaming if supported
            "request_id": str(time.time())  # Unique request ID
        }
        
        if context:
            request["context"] = context
        if temperature is not None:
            request["temperature"] = temperature
        if max_tokens is not None:
            request["max_tokens"] = max_tokens
            
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.connection_timeout
            )
            
            # Send request
            request_data = json.dumps(request).encode('utf-8') + b'\n'
            writer.write(request_data)
            await writer.drain()
            
            # Process streaming response
            buffer = b""
            total_content = []
            
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        reader.read(4096),
                        timeout=timeout
                    )
                    
                    if not chunk:
                        break
                        
                    buffer += chunk
                    
                    # Process complete messages
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        if not line:
                            continue
                            
                        try:
                            response = json.loads(line.decode('utf-8'))
                            
                            if response.get("type") == "stream_start":
                                # AI acknowledged streaming request
                                logger.debug(f"Stream started: {response.get('request_id')}")
                                continue
                                
                            elif response.get("type") == "stream_chunk":
                                # Native streaming chunk from enhanced AI
                                content = response.get("content", "")
                                metadata = response.get("metadata", {})
                                
                                yield StreamChunk(
                                    content=content,
                                    metadata=metadata,
                                    is_final=False
                                )
                                
                            elif response.get("type") == "stream_end":
                                # Stream completion from enhanced AI
                                yield StreamChunk(
                                    content="",
                                    metadata=response.get("metadata", {}),
                                    is_final=True
                                )
                                writer.close()
                                await writer.wait_closed()
                                return
                                
                            elif response.get("type") == "stream_error":
                                # Streaming error
                                raise Exception(response.get("error", "Stream error"))
                                
                            elif response.get("type") == "chat_response":
                                # Greek Chorus AIs don't support streaming yet
                                # Simulate streaming by yielding the full response
                                content = response.get("content", "")
                                total_content.append(content)
                                
                                # Yield as chunks
                                chunk_size = 50  # Characters per chunk
                                for i in range(0, len(content), chunk_size):
                                    chunk_content = content[i:i+chunk_size]
                                    yield StreamChunk(
                                        content=chunk_content,
                                        metadata={
                                            "ai_id": response.get("ai_id"),
                                            "simulated_streaming": True
                                        },
                                        is_final=False
                                    )
                                    await asyncio.sleep(0.05)  # Small delay for effect
                                
                                # Final chunk
                                yield StreamChunk(
                                    content="",
                                    metadata={
                                        "model": response.get("model", "llama3.3:70b"),
                                        "ai_id": response.get("ai_id"),
                                        "elapsed_time": time.time() - start_time,
                                        "total_content": "".join(total_content)
                                    },
                                    is_final=True
                                )
                                writer.close()
                                await writer.wait_closed()
                                return
                                
                            elif response.get("type") == MessageType.CHUNK.value:
                                content = response.get("content", "")
                                total_content.append(content)
                                yield StreamChunk(
                                    content=content,
                                    metadata=response.get("metadata", {}),
                                    is_final=False
                                )
                                
                            elif response.get("type") == MessageType.COMPLETE.value:
                                # Final chunk with metadata
                                yield StreamChunk(
                                    content="",
                                    metadata={
                                        "model": response.get("model", "unknown"),
                                        "elapsed_time": time.time() - start_time,
                                        "total_tokens": response.get("total_tokens"),
                                        "ai_id": response.get("ai_id", f"{host}:{port}")
                                    },
                                    is_final=True
                                )
                                writer.close()
                                await writer.wait_closed()
                                return
                                
                            elif response.get("type") == MessageType.ERROR.value:
                                raise Exception(response.get("message", "Stream error"))
                                
                        except json.JSONDecodeError:
                            if self.debug:
                                logger.debug(f"Failed to parse JSON: {line}")
                            continue
                            
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Stream timeout after {timeout}s")
                    
            # If we got here, stream ended without complete message
            yield StreamChunk(
                content="",
                metadata={
                    "elapsed_time": time.time() - start_time,
                    "warning": "Stream ended without completion signal"
                },
                is_final=True
            )
            
        except Exception as e:
            # Yield error as final chunk
            yield StreamChunk(
                content="",
                metadata={
                    "error": str(e),
                    "elapsed_time": time.time() - start_time
                },
                is_final=True
            )
            
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def ping(self, host: str, port: int, timeout: float = 5.0) -> Dict[str, Any]:
        """
        Send a ping to check if AI is responsive.
        
        Args:
            host: Host address
            port: Port number
            timeout: Ping timeout
            
        Returns:
            Dict with success status and response time
        """
        return await self.send_message(
            host, port, "ping", 
            timeout=timeout,
            _internal_health_check=True
        )
    
    @asynccontextmanager
    async def persistent_connection(self, host: str, port: int):
        """
        Create a persistent connection for multiple messages.
        
        Example:
            async with client.persistent_connection(host, port) as conn:
                response1 = await conn.send("First message")
                response2 = await conn.send("Second message")
        """
        reader, writer = await asyncio.open_connection(host, port)
        
        class Connection:
            async def send(self, message: str, **kwargs) -> Dict[str, Any]:
                request = {
                    "type": MessageType.MESSAGE.value,
                    "content": message,
                    **kwargs
                }
                
                writer.write(json.dumps(request).encode('utf-8') + b'\n')
                await writer.drain()
                
                response_data = await reader.readline()
                if not response_data:
                    raise ConnectionError("Connection closed")
                    
                return json.loads(response_data.decode('utf-8').strip())
                
            async def stream(self, message: str, **kwargs):
                """Stream from persistent connection"""
                # Implementation similar to send_message_stream but reusing connection
                pass
        
        try:
            yield Connection()
        finally:
            writer.close()
            await writer.wait_closed()


# Backward compatibility for sync usage in aish
def create_sync_client(timeout: float = 30.0) -> 'SyncAISocketClient':
    """Create a synchronous wrapper for the async client."""
    return SyncAISocketClient(AISocketClient(default_timeout=timeout))


class SyncAISocketClient:
    """Synchronous wrapper for AISocketClient."""
    
    def __init__(self, async_client: AISocketClient):
        self.async_client = async_client
        
    def send_message(self, host: str, port: int, message: str, **kwargs) -> Dict[str, Any]:
        """Sync version of send_message."""
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop running
            return asyncio.run(self.async_client.send_message(host, port, message, **kwargs))
        else:
            # Loop already running, we're in async context
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, 
                    self.async_client.send_message(host, port, message, **kwargs)
                )
                return future.result()
    
    def ping(self, host: str, port: int, timeout: float = 5.0) -> Dict[str, Any]:
        """Sync version of ping."""
        return self.send_message(host, port, "ping", timeout=timeout, _internal_health_check=True)