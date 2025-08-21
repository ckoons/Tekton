"""
Main client interface for interacting with Tekton LLM services.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Callable
from urllib.parse import urljoin

import aiohttp
import requests

from .exceptions import (
    TektonLLMError, ConnectionError, TimeoutError, 
    AuthenticationError, ServiceUnavailableError, 
    RateLimitError, InvalidRequestError, FallbackError
)
from .models import (
    Message, CompletionOptions, CompletionResponse, 
    StreamingChunk, AvailableProviders
)
from .adapters.rhetor import RhetorAdapter
from .adapters.fallback import LocalFallbackAdapter

logger = logging.getLogger(__name__)

class TektonLLMClient:
    """Client for interacting with Tekton LLM services."""
    
    def __init__(
        self,
        component_id: str,
        rhetor_url: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        use_fallback: bool = True,
        auth_token: Optional[str] = None
    ):
        """
        Initialize the Tekton LLM client.
        
        Args:
            component_id: ID of the component using the client (used for tracking)
            rhetor_url: URL for the Rhetor API (defaults to RHETOR_URL env var or http://localhost:8003)
            provider_id: Default provider ID to use (defaults to RHETOR_DEFAULT_PROVIDER env var or "anthropic")
            model_id: Default model ID to use (provider-specific, defaults to RHETOR_DEFAULT_MODEL env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            use_fallback: Whether to use local fallback when Rhetor is unavailable
            auth_token: Optional authentication token for Rhetor API
        """
        # Load settings from environment variables with defaults
        self.component_id = component_id
        self.rhetor_url = rhetor_url or TektonEnviron.get("RHETOR_URL", "http://localhost:8003")
        self.provider_id = provider_id or TektonEnviron.get("RHETOR_DEFAULT_PROVIDER", "anthropic")
        self.model_id = model_id or TektonEnviron.get("RHETOR_DEFAULT_MODEL", None)  # Will use provider's default if None
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_fallback = use_fallback
        self.auth_token = auth_token or TektonEnviron.get("RHETOR_AUTH_TOKEN")
        
        # Create HTTP session for reuse
        self.session = None
        
        # Initialize adapters
        self.primary_adapter = RhetorAdapter(
            base_url=self.rhetor_url,
            auth_token=self.auth_token,
            timeout=self.timeout
        )
        
        # Initialize fallback adapter if enabled
        self.fallback_adapter = None
        if self.use_fallback:
            self.fallback_adapter = LocalFallbackAdapter(component_id=self.component_id)
        
        logger.info(
            f"Initialized TektonLLMClient for component '{component_id}' "
            f"with Rhetor URL: {self.rhetor_url}, "
            f"Provider: {self.provider_id}, "
            f"Model: {self.model_id or 'default'}"
        )
    
    async def initialize(self):
        """
        Initialize the client and verify connection to Rhetor.
        
        This method should be called after creating the client to ensure
        the connection to Rhetor is working and to fetch available models.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Initialize session if not already done
            if self.session is None:
                self.session = aiohttp.ClientSession()
                
            # Initialize the primary adapter
            await self.primary_adapter.initialize()
            
            # If no model is specified, use the default from the adapter
            if not self.model_id:
                provider_info = await self.primary_adapter.get_provider_info(self.provider_id)
                if provider_info:
                    self.model_id = provider_info.get("default_model", "")
                    logger.info(f"Using default model: {self.model_id}")
            
            # Initialize the fallback adapter if enabled
            if self.fallback_adapter:
                await self.fallback_adapter.initialize()
                
            return True
        except Exception as e:
            logger.error(f"Error initializing TektonLLMClient: {str(e)}")
            if self.fallback_adapter:
                logger.info("Initialization failed, will use fallback adapter if needed")
            return False
    
    async def shutdown(self):
        """
        Shutdown the client and clean up resources.
        
        Should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        if self.session:
            await self.session.close()
            self.session = None
            
        # Shutdown adapters
        await self.primary_adapter.shutdown()
        if self.fallback_adapter:
            await self.fallback_adapter.shutdown()
            
        logger.info(f"TektonLLMClient for component '{self.component_id}' has been shutdown")
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        streaming: bool = False,
        callback: Optional[Callable[[StreamingChunk], None]] = None,
        context_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[CompletionResponse, AsyncGenerator[StreamingChunk, None]]:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            streaming: Whether to stream the response
            callback: Optional callback function for streaming response chunks
            context_id: Context ID for tracking conversation (defaults to component_id)
            options: Additional options for the LLM
            
        Returns:
            If streaming=False, returns a CompletionResponse
            If streaming=True, returns an AsyncGenerator yielding StreamingChunk objects
        """
        options = options or {}
        context_id = context_id or self.component_id
        
        # Convert the prompt to a message
        message = Message(role="user", content=prompt)
        
        # Create a list with a single message
        messages = [message]
        
        # If system prompt is provided, add it as a system message
        if system_prompt:
            messages.insert(0, Message(role="system", content=system_prompt))
        
        # Use the chat completion method with a single message
        return await self.generate_chat_response(
            messages=messages,
            streaming=streaming,
            callback=callback,
            context_id=context_id,
            options=options
        )
    
    async def generate_chat_response(
        self,
        messages: List[Union[Dict[str, str], Message]],
        streaming: bool = False,
        callback: Optional[Callable[[StreamingChunk], None]] = None,
        context_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[CompletionResponse, AsyncGenerator[StreamingChunk, None]]:
        """
        Generate a chat response using the LLM.
        
        Args:
            messages: List of message dictionaries or Message objects
            streaming: Whether to stream the response
            callback: Optional callback function for streaming response chunks
            context_id: Context ID for tracking conversation (defaults to component_id)
            options: Additional options for the LLM
            
        Returns:
            If streaming=False, returns a CompletionResponse
            If streaming=True, returns an AsyncGenerator yielding StreamingChunk objects
        """
        options = options or {}
        context_id = context_id or self.component_id
        
        # Ensure all messages are Message objects
        processed_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                processed_messages.append(Message(**msg))
            elif isinstance(msg, Message):
                processed_messages.append(msg)
            else:
                raise InvalidRequestError(f"Invalid message format: {msg}")
        
        # Extract system_prompt from the first message if it's a system message
        system_prompt = None
        if processed_messages and processed_messages[0].role == "system":
            system_prompt = processed_messages[0].content
            processed_messages = processed_messages[1:]
        
        # Create options object
        completion_options = CompletionOptions(
            temperature=options.get("temperature", 0.7),
            max_tokens=options.get("max_tokens"),
            stop_sequences=options.get("stop_sequences"),
            top_p=options.get("top_p"),
            top_k=options.get("top_k"),
            presence_penalty=options.get("presence_penalty"),
            frequency_penalty=options.get("frequency_penalty"),
            fallback_provider=options.get("fallback_provider"),
            fallback_model=options.get("fallback_model"),
            timeout=options.get("timeout", self.timeout),
            retry_count=options.get("retry_count", self.max_retries),
            retry_delay=options.get("retry_delay", 1000)
        )
        
        provider_id = options.get("provider", self.provider_id)
        model_id = options.get("model", self.model_id)
        
        if streaming:
            return self._stream_chat_response(
                messages=processed_messages,
                system_prompt=system_prompt,
                context_id=context_id,
                provider_id=provider_id,
                model_id=model_id,
                options=completion_options,
                callback=callback
            )
        else:
            return await self._complete_chat_response(
                messages=processed_messages,
                system_prompt=system_prompt,
                context_id=context_id,
                provider_id=provider_id,
                model_id=model_id,
                options=completion_options
            )
    
    async def _complete_chat_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        context_id: str,
        provider_id: str,
        model_id: Optional[str],
        options: CompletionOptions
    ) -> CompletionResponse:
        """
        Complete a chat response (non-streaming).
        
        This is an internal method used by generate_chat_response.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Completion options
            
        Returns:
            CompletionResponse object
        """
        start_time = time.time()
        
        try:
            # Try the primary adapter first
            response = await self.primary_adapter.complete_chat(
                messages=messages,
                system_prompt=system_prompt,
                context_id=context_id,
                provider_id=provider_id,
                model_id=model_id,
                options=options
            )
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Create the response object
            return CompletionResponse(
                content=response.get("content", ""),
                model=response.get("model", model_id),
                provider=response.get("provider", provider_id),
                finish_reason=response.get("finish_reason"),
                usage=response.get("usage"),
                context_id=context_id,
                fallback=False,
                timestamp=response.get("timestamp", ""),
                latency=latency,
                error=response.get("error")
            )
            
        except Exception as e:
            logger.error(f"Error using primary adapter: {str(e)}")
            
            # If fallback is disabled or there's no fallback adapter, raise the exception
            if not self.use_fallback or not self.fallback_adapter:
                raise
            
            # Try the fallback adapter
            try:
                logger.info(f"Using fallback adapter for {context_id}")
                
                fallback_response = await self.fallback_adapter.complete_chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    context_id=context_id,
                    provider_id=provider_id,
                    model_id=model_id,
                    options=options
                )
                
                # Calculate latency
                latency = time.time() - start_time
                
                # Create the response object
                return CompletionResponse(
                    content=fallback_response.get("content", ""),
                    model=fallback_response.get("model", "fallback"),
                    provider=fallback_response.get("provider", "fallback"),
                    finish_reason=fallback_response.get("finish_reason", "fallback"),
                    usage=fallback_response.get("usage"),
                    context_id=context_id,
                    fallback=True,
                    timestamp=fallback_response.get("timestamp", ""),
                    latency=latency,
                    error=fallback_response.get("error")
                )
                
            except Exception as fallback_error:
                logger.error(f"Fallback adapter also failed: {str(fallback_error)}")
                raise FallbackError(f"Primary error: {str(e)}. Fallback error: {str(fallback_error)}")
    
    async def _stream_chat_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        context_id: str,
        provider_id: str,
        model_id: Optional[str],
        options: CompletionOptions,
        callback: Optional[Callable[[StreamingChunk], None]] = None
    ) -> AsyncGenerator[StreamingChunk, None]:
        """
        Stream a chat response.
        
        This is an internal method used by generate_chat_response.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Completion options
            callback: Optional callback function for each chunk
            
        Yields:
            StreamingChunk objects with response chunks
        """
        try:
            # Try the primary adapter first
            async for chunk in self.primary_adapter.stream_chat(
                messages=messages,
                system_prompt=system_prompt,
                context_id=context_id,
                provider_id=provider_id,
                model_id=model_id,
                options=options
            ):
                streaming_chunk = StreamingChunk(
                    chunk=chunk.get("chunk", ""),
                    context_id=context_id,
                    model=chunk.get("model", model_id),
                    provider=chunk.get("provider", provider_id),
                    timestamp=chunk.get("timestamp", ""),
                    done=chunk.get("done", False),
                    fallback=False,
                    error=chunk.get("error")
                )
                
                # Call the callback if provided
                if callback:
                    callback(streaming_chunk)
                
                yield streaming_chunk
                
        except Exception as e:
            logger.error(f"Error streaming from primary adapter: {str(e)}")
            
            # If fallback is disabled or there's no fallback adapter, raise the exception
            if not self.use_fallback or not self.fallback_adapter:
                # Return an error chunk
                error_chunk = StreamingChunk(
                    chunk="",
                    context_id=context_id,
                    model=model_id or "",
                    provider=provider_id,
                    timestamp="",
                    done=True,
                    fallback=False,
                    error=str(e)
                )
                
                if callback:
                    callback(error_chunk)
                
                yield error_chunk
                return
            
            # Try the fallback adapter
            try:
                logger.info(f"Using fallback adapter for streaming {context_id}")
                
                async for chunk in self.fallback_adapter.stream_chat(
                    messages=messages,
                    system_prompt=system_prompt,
                    context_id=context_id,
                    provider_id=provider_id,
                    model_id=model_id,
                    options=options
                ):
                    streaming_chunk = StreamingChunk(
                        chunk=chunk.get("chunk", ""),
                        context_id=context_id,
                        model=chunk.get("model", "fallback"),
                        provider=chunk.get("provider", "fallback"),
                        timestamp=chunk.get("timestamp", ""),
                        done=chunk.get("done", False),
                        fallback=True,
                        error=chunk.get("error")
                    )
                    
                    # Call the callback if provided
                    if callback:
                        callback(streaming_chunk)
                    
                    yield streaming_chunk
                    
            except Exception as fallback_error:
                logger.error(f"Fallback adapter streaming also failed: {str(fallback_error)}")
                
                # Return an error chunk
                error_chunk = StreamingChunk(
                    chunk="",
                    context_id=context_id,
                    model=model_id or "",
                    provider=provider_id,
                    timestamp="",
                    done=True,
                    fallback=True,
                    error=f"Primary error: {str(e)}. Fallback error: {str(fallback_error)}"
                )
                
                if callback:
                    callback(error_chunk)
                
                yield error_chunk
    
    async def get_providers(self) -> AvailableProviders:
        """
        Get information about all available LLM providers.
        
        Returns:
            AvailableProviders object with provider information
        """
        try:
            # Get provider information from primary adapter
            response = await self.primary_adapter.get_providers()
            
            return AvailableProviders(
                providers=response.get("providers", {}),
                default_provider=response.get("default_provider", self.provider_id),
                default_model=response.get("default_model", self.model_id)
            )
            
        except Exception as e:
            logger.error(f"Error getting providers: {str(e)}")
            
            if not self.use_fallback or not self.fallback_adapter:
                raise
                
            # Try the fallback adapter
            try:
                fallback_response = await self.fallback_adapter.get_providers()
                
                return AvailableProviders(
                    providers=fallback_response.get("providers", {}),
                    default_provider=fallback_response.get("default_provider", "fallback"),
                    default_model=fallback_response.get("default_model", "fallback")
                )
                
            except Exception as fallback_error:
                logger.error(f"Fallback adapter also failed for providers: {str(fallback_error)}")
                raise FallbackError(f"Primary error: {str(e)}. Fallback error: {str(fallback_error)}")