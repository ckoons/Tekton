"""
Adapter for Rhetor LLM service.
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from urllib.parse import urljoin

from .base import BaseAdapter
from ..models import Message, CompletionOptions
from ..exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    AuthenticationError, ServiceUnavailableError, 
    InvalidRequestError, AdapterError
)

logger = logging.getLogger(__name__)

class RhetorAdapter(BaseAdapter):
    """Adapter for Rhetor LLM service."""
    
    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the Rhetor adapter.
        
        Args:
            base_url: Base URL for the Rhetor API
            auth_token: Authentication token for Rhetor API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.timeout = timeout
        self.session = None
        self.available = False
        self.providers_cache = None
        self.ws_url = self._get_ws_url()
        
        logger.info(f"Initialized RhetorAdapter with URL: {self.base_url}")
    
    def _get_ws_url(self) -> str:
        """
        Get the WebSocket URL based on the HTTP URL.
        
        Returns:
            WebSocket URL
        """
        if self.base_url.startswith("https://"):
            ws_url = self.base_url.replace("https://", "wss://")
        else:
            ws_url = self.base_url.replace("http://", "ws://")
            
        return ws_url + "/ws"
    
    async def initialize(self) -> bool:
        """
        Initialize the adapter.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Create session if it doesn't exist
            if self.session is None:
                self.session = aiohttp.ClientSession(
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            # Check if Rhetor is available
            async with self.session.get(
                urljoin(self.base_url, "/api/v1/health"),
                raise_for_status=False
            ) as response:
                if response.status == 200:
                    self.available = True
                    
                    # Cache providers for future use
                    await self.get_providers()
                    
                    logger.info("Rhetor service is available")
                    return True
                else:
                    self.available = False
                    logger.warning(f"Rhetor service health check failed: {response.status}")
                    return False
                    
        except aiohttp.ClientError as e:
            self.available = False
            logger.error(f"Error connecting to Rhetor service: {str(e)}")
            return False
        except Exception as e:
            self.available = False
            logger.error(f"Unexpected error initializing Rhetor adapter: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the adapter and clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
        self.available = False
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for HTTP requests.
        
        Returns:
            Dictionary with request headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        return headers
    
    def is_available(self) -> bool:
        """
        Check if the adapter is available.
        
        Returns:
            True if the adapter is available, False otherwise
        """
        return self.available
    
    async def complete_chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        context_id: str,
        provider_id: str,
        model_id: Optional[str],
        options: CompletionOptions
    ) -> Dict[str, Any]:
        """
        Complete a chat request using Rhetor.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Completion options
            
        Returns:
            Dictionary with the complete response
        """
        if not self.available:
            raise ServiceUnavailableError("Rhetor service is not available")
            
        if not self.session:
            await self.initialize()
            if not self.available:
                raise ServiceUnavailableError("Failed to initialize Rhetor service")
        
        # Convert messages to the format expected by Rhetor
        formatted_messages = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]
        
        # Prepare the request payload
        payload = {
            "messages": formatted_messages,
            "context_id": context_id,
            "provider_id": provider_id,
            "streaming": False,
            "options": {
                "temperature": options.temperature,
                "fallback_provider": options.fallback_provider,
                "fallback_model": options.fallback_model
            }
        }
        
        if model_id:
            payload["model_id"] = model_id
            
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        if options.max_tokens:
            payload["options"]["max_tokens"] = options.max_tokens
            
        if options.stop_sequences:
            payload["options"]["stop"] = options.stop_sequences
            
        if options.top_p:
            payload["options"]["top_p"] = options.top_p
            
        if options.top_k:
            payload["options"]["top_k"] = options.top_k
            
        if options.presence_penalty:
            payload["options"]["presence_penalty"] = options.presence_penalty
            
        if options.frequency_penalty:
            payload["options"]["frequency_penalty"] = options.frequency_penalty
        
        try:
            async with self.session.post(
                urljoin(self.base_url, "/api/v1/chat"),
                json=payload,
                raise_for_status=False,
                timeout=aiohttp.ClientTimeout(total=options.timeout)
            ) as response:
                response_data = await response.json()
                
                if response.status != 200:
                    error_message = response_data.get("error", "Unknown error")
                    
                    if response.status == 401:
                        raise AuthenticationError(f"Authentication failed: {error_message}")
                    elif response.status == 400:
                        raise InvalidRequestError(f"Invalid request: {error_message}")
                    elif response.status == 429:
                        raise RateLimitError(f"Rate limit exceeded: {error_message}")
                    elif response.status == 503:
                        raise ServiceUnavailableError(f"Service unavailable: {error_message}")
                    else:
                        raise AdapterError("rhetor", f"HTTP error {response.status}: {error_message}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Error connecting to Rhetor service: {str(e)}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timed out after {options.timeout} seconds")
        except (AuthenticationError, InvalidRequestError, RateLimitError, ServiceUnavailableError, AdapterError) as e:
            raise e
        except Exception as e:
            raise TektonLLMError(f"Unexpected error: {str(e)}")
    
    async def stream_chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        context_id: str,
        provider_id: str,
        model_id: Optional[str],
        options: CompletionOptions
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a chat response using Rhetor.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Completion options
            
        Yields:
            Dictionaries with response chunks
        """
        if not self.available:
            raise ServiceUnavailableError("Rhetor service is not available")
            
        if not self.session:
            await self.initialize()
            if not self.available:
                raise ServiceUnavailableError("Failed to initialize Rhetor service")
        
        # Convert messages to the format expected by Rhetor
        formatted_messages = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]
        
        # Prepare the request payload
        payload = {
            "messages": formatted_messages,
            "context_id": context_id,
            "provider_id": provider_id,
            "streaming": True,
            "options": {
                "temperature": options.temperature,
                "fallback_provider": options.fallback_provider,
                "fallback_model": options.fallback_model
            }
        }
        
        if model_id:
            payload["model_id"] = model_id
            
        if system_prompt:
            payload["system_prompt"] = system_prompt
            
        if options.max_tokens:
            payload["options"]["max_tokens"] = options.max_tokens
            
        if options.stop_sequences:
            payload["options"]["stop"] = options.stop_sequences
            
        if options.top_p:
            payload["options"]["top_p"] = options.top_p
            
        if options.top_k:
            payload["options"]["top_k"] = options.top_k
            
        if options.presence_penalty:
            payload["options"]["presence_penalty"] = options.presence_penalty
            
        if options.frequency_penalty:
            payload["options"]["frequency_penalty"] = options.frequency_penalty
        
        try:
            async with self.session.post(
                urljoin(self.base_url, "/api/v1/chat/stream"),
                json=payload,
                raise_for_status=False,
                timeout=aiohttp.ClientTimeout(total=options.timeout)
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", "Unknown error")
                    
                    if response.status == 401:
                        raise AuthenticationError(f"Authentication failed: {error_message}")
                    elif response.status == 400:
                        raise InvalidRequestError(f"Invalid request: {error_message}")
                    elif response.status == 429:
                        raise RateLimitError(f"Rate limit exceeded: {error_message}")
                    elif response.status == 503:
                        raise ServiceUnavailableError(f"Service unavailable: {error_message}")
                    else:
                        raise AdapterError("rhetor", f"HTTP error {response.status}: {error_message}")
                
                # Process the stream
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line:
                        continue
                        
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        
                        if line == '[DONE]':
                            # End of stream
                            break
                            
                        try:
                            chunk_data = json.loads(line)
                            yield chunk_data
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing chunk data: {str(e)}, data: {line}")
                
                # Send a final chunk indicating completion
                yield {
                    "chunk": "",
                    "context_id": context_id,
                    "model": model_id or "",
                    "provider": provider_id,
                    "done": True
                }
                
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Error connecting to Rhetor service: {str(e)}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timed out after {options.timeout} seconds")
        except (AuthenticationError, InvalidRequestError, RateLimitError, ServiceUnavailableError, AdapterError) as e:
            raise e
        except Exception as e:
            raise TektonLLMError(f"Unexpected error: {str(e)}")
    
    async def get_providers(self) -> Dict[str, Any]:
        """
        Get information about all available LLM providers from Rhetor.
        
        Returns:
            Dictionary with provider information
        """
        if not self.session:
            await self.initialize()
        
        try:
            # Use cached providers if available
            if self.providers_cache is not None:
                return self.providers_cache
                
            async with self.session.get(
                urljoin(self.base_url, "/api/v1/providers"),
                raise_for_status=False
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to get providers: {response.status}")
                    return {"providers": {}, "default_provider": "", "default_model": ""}
                
                providers_data = await response.json()
                
                # Cache the providers
                self.providers_cache = providers_data
                
                return providers_data
                
        except Exception as e:
            logger.error(f"Error getting providers: {str(e)}")
            return {"providers": {}, "default_provider": "", "default_model": ""}
    
    async def get_provider_info(self, provider_id: str) -> Dict[str, Any]:
        """
        Get information about a specific provider from Rhetor.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Dictionary with provider information
        """
        providers = await self.get_providers()
        providers_dict = providers.get("providers", {})
        
        if provider_id in providers_dict:
            return providers_dict[provider_id]
        
        return {}