#!/usr/bin/env python3
"""
Shared socket client for AI communication.

This module provides a robust async socket client for communicating with
Greek Chorus AI specialists using newline-delimited JSON protocol.

Used by both Tekton components and aish for consistent AI communication.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class AISocketClient:
    """
    Async socket client for AI specialist communication.
    
    Features:
    - Async/await support
    - Configurable timeouts
    - Robust error handling
    - Connection pooling (future)
    - Automatic retry logic
    """
    
    def __init__(self, 
                 default_timeout: float = 30.0,
                 connection_timeout: float = 2.0,
                 max_retries: int = 1):
        """
        Initialize AI socket client.
        
        Args:
            default_timeout: Default response timeout in seconds
            connection_timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.default_timeout = default_timeout
        self.connection_timeout = connection_timeout
        self.max_retries = max_retries
        
    async def send_message(self,
                          host: str,
                          port: int,
                          message: str,
                          context: Optional[Dict[str, Any]] = None,
                          timeout: Optional[float] = None,
                          temperature: Optional[float] = None,
                          max_tokens: Optional[int] = None) -> Dict[str, Any]:
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
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        # Prepare request
        request = {
            "type": "message",  # Greek Chorus AIs expect "message" not "chat"
            "content": message
        }
        
        if context:
            request["context"] = context
        if temperature is not None:
            request["temperature"] = temperature
        if max_tokens is not None:
            request["max_tokens"] = max_tokens
            
        # Try to send with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._send_single_message(
                    host, port, request, timeout
                )
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                response["elapsed_time"] = elapsed_time
                
                return response
                
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {host}:{port}: {e}, retrying..."
                    )
                    await asyncio.sleep(0.5)  # Brief delay before retry
                    
        # All attempts failed
        elapsed_time = time.time() - start_time
        error_msg = str(last_error) if last_error else "Unknown error"
        
        logger.error(f"Failed to communicate with {host}:{port} after {self.max_retries + 1} attempts: {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "response": None,
            "elapsed_time": elapsed_time
        }
    
    async def _send_single_message(self,
                                  host: str,
                                  port: int,
                                  request: Dict[str, Any],
                                  timeout: float) -> Dict[str, Any]:
        """
        Send a single message attempt (internal method).
        
        Args:
            host: Host address
            port: Port number
            request: Request dictionary
            timeout: Total timeout for operation
            
        Returns:
            Response dictionary
            
        Raises:
            Various exceptions on failure
        """
        reader = None
        writer = None
        
        try:
            # Connect with timeout
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.connection_timeout
            )
            
            logger.debug(f"Connected to {host}:{port}")
            
            # Send request as newline-delimited JSON
            request_data = json.dumps(request) + '\n'
            writer.write(request_data.encode('utf-8'))
            await writer.drain()
            
            logger.debug(f"Sent request: {request['type']} with {len(request.get('content', ''))} chars")
            
            # Read response with timeout
            remaining_timeout = timeout - self.connection_timeout
            response_data = await asyncio.wait_for(
                reader.readline(),
                timeout=remaining_timeout
            )
            
            if not response_data:
                raise ConnectionError("No response received (empty response)")
                
            # Parse response
            response_text = response_data.decode('utf-8').strip()
            if not response_text:
                raise ValueError("Empty response from AI")
                
            response = json.loads(response_text)
            
            # Extract content based on response format
            if response.get('type') == 'response' or response.get('type') == 'chat_response':
                # Expected format
                return {
                    "success": True,
                    "response": response.get('content', ''),
                    "ai_id": response.get('ai_id', f"{host}:{port}"),
                    "model": response.get('model', 'unknown')
                }
            elif response.get('type') == 'error':
                # Error response
                return {
                    "success": False,
                    "error": response.get('message', 'Unknown error'),
                    "response": None
                }
            elif 'response' in response:
                # Alternative format
                return {
                    "success": True,
                    "response": response['response'],
                    "ai_id": response.get('ai_id', f"{host}:{port}"),
                    "model": response.get('model', 'unknown')
                }
            elif 'content' in response:
                # Another alternative format
                return {
                    "success": True,
                    "response": response['content'],
                    "ai_id": response.get('ai_id', f"{host}:{port}"),
                    "model": response.get('model', 'unknown')
                }
            else:
                # Unexpected format, return as-is
                logger.warning(f"Unexpected response format: {response}")
                return {
                    "success": True,
                    "response": str(response),
                    "ai_id": f"{host}:{port}",
                    "model": 'unknown',
                    "raw_response": response
                }
                
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout after {timeout}s waiting for response")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise ConnectionError(f"Socket error: {e}")
        finally:
            # Clean up connection
            if writer:
                writer.close()
                await writer.wait_closed()
                
    async def ping(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """
        Ping an AI specialist to check if it's responsive.
        
        Args:
            host: Host address
            port: Port number
            timeout: Ping timeout
            
        Returns:
            True if responsive, False otherwise
        """
        try:
            request = {"type": "ping"}
            response = await self._send_single_message(host, port, request, timeout)
            return response.get("type") == "pong" or response.get("success", False)
        except Exception as e:
            logger.debug(f"Ping failed for {host}:{port}: {e}")
            return False
            
    async def get_health(self, host: str, port: int, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        Get health status from an AI specialist.
        
        Args:
            host: Host address
            port: Port number
            timeout: Health check timeout
            
        Returns:
            Health status dict or None if failed
        """
        try:
            request = {"type": "health"}
            response = await self._send_single_message(host, port, request, timeout)
            if response.get("success"):
                return response
            return None
        except Exception as e:
            logger.debug(f"Health check failed for {host}:{port}: {e}")
            return None


# Convenience functions for simple usage

async def send_to_ai(host: str, port: int, message: str, 
                    timeout: float = 30.0, **kwargs) -> Dict[str, Any]:
    """
    Simple function to send a message to an AI specialist.
    
    Args:
        host: Host address
        port: Port number  
        message: Message to send
        timeout: Response timeout
        **kwargs: Additional parameters (context, temperature, etc.)
        
    Returns:
        Response dictionary
    """
    client = AISocketClient(default_timeout=timeout)
    return await client.send_message(host, port, message, **kwargs)


async def test_ai_connection(host: str = "localhost", port: int = 45003):
    """
    Test function to verify AI connection.
    
    Args:
        host: Host address
        port: Port to test (default: Apollo AI)
    """
    client = AISocketClient()
    
    print(f"Testing connection to {host}:{port}...")
    
    # Test ping
    if await client.ping(host, port):
        print("✓ Ping successful")
    else:
        print("✗ Ping failed")
        return
        
    # Test health
    health = await client.get_health(host, port)
    if health:
        print(f"✓ Health check: {health}")
    else:
        print("✗ Health check failed")
        
    # Test chat
    print("Testing chat...")
    response = await client.send_message(
        host, port, 
        "Hello, this is a test message. Please respond briefly.",
        timeout=10.0
    )
    
    if response["success"]:
        print(f"✓ Chat response: {response['response'][:100]}...")
        print(f"  AI: {response.get('ai_id', 'unknown')}")
        print(f"  Model: {response.get('model', 'unknown')}")
        print(f"  Time: {response.get('elapsed_time', 0):.2f}s")
    else:
        print(f"✗ Chat failed: {response['error']}")


# For testing
if __name__ == "__main__":
    import sys
    
    # Simple test
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 45003
    asyncio.run(test_ai_connection(port=port))