"""
Rhetor LLM Adapter for Ergon.

This module provides an adapter to use Rhetor's LLM capabilities in Ergon,
replacing the direct LLM provider implementations.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable, AsyncGenerator
import uuid
from ergon.utils.tekton_integration import get_component_api_url

logger = logging.getLogger(__name__)

class RhetorLLMAdapter:
    """
    Adapter for integrating Rhetor's LLM capabilities into Ergon.
    
    This class provides a compatible interface with Ergon's existing
    LLMClient, but delegates all LLM requests to Rhetor.
    """
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        rhetor_url: Optional[str] = None
    ):
        """
        Initialize the Rhetor LLM adapter.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
            rhetor_url: URL for the Rhetor API (default: environment variable or localhost)
        """
        self.model_name = model_name or os.environ.get("RHETOR_DEFAULT_MODEL", "claude-3-sonnet-20240229")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.rhetor_url = rhetor_url or os.environ.get("RHETOR_API_URL", get_component_api_url("rhetor"))
        self.client = None
        self.rhetor_client = None
    
    async def initialize(self):
        """Initialize the Rhetor LLM client."""
        try:
            from rhetor.core.llm_client import LLMClient
            if not self.client:
                self.client = LLMClient()
                await self.client.initialize()
            logger.info("Successfully initialized Rhetor LLM client")
            return True
        except ImportError:
            logger.warning("Direct Rhetor LLM client not available, trying component client")
            try:
                from rhetor.client import get_rhetor_prompt_client
                if not self.rhetor_client:
                    self.rhetor_client = await get_rhetor_prompt_client()
                logger.info("Successfully initialized Rhetor prompt client")
                return True
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize Rhetor clients: {e}")
                return False
    
    async def _ensure_initialized(self):
        """Ensure the client is initialized."""
        if not self.client and not self.rhetor_client:
            success = await self.initialize()
            if not success:
                raise RuntimeError("Failed to initialize Rhetor LLM adapter")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages to Rhetor's expected format."""
        # Rhetor's LLM client already uses the standard format
        return messages
    
    def _extract_provider_from_model(self) -> str:
        """Extract the provider from the model name."""
        model = self.model_name.lower()
        if "gpt" in model or model.startswith("openai/"):
            return "openai"
        elif "claude" in model or model.startswith("anthropic/"):
            return "anthropic"
        elif "ollama" in model or "/" in model:
            return "ollama"
        else:
            return None
    
    async def complete(self, messages: List[Dict[str, str]]) -> str:
        """
        Complete a conversation with the LLM through Rhetor.
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Generated text response
        """
        await self._ensure_initialized()
        
        formatted_messages = self._format_messages(messages)
        context_id = str(uuid.uuid4())
        provider_id = self._extract_provider_from_model()
        
        if self.client:
            # Use direct LLM client
            response = await self.client.chat_complete(
                messages=formatted_messages,
                context_id=context_id,
                model_id=self.model_name,
                provider_id=provider_id,
                options={
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
            )
            
            if "error" in response:
                logger.error(f"Error from Rhetor: {response['error']}")
                raise RuntimeError(f"Rhetor LLM error: {response['error']}")
            
            return response.get("content", "")
        
        elif self.rhetor_client:
            # Use Rhetor prompt client
            response = await self.rhetor_client.invoke_capability(
                "generate_completion",
                {
                    "messages": formatted_messages,
                    "model": self.model_name,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
            )
            
            if isinstance(response, dict) and "content" in response:
                return response["content"]
            elif isinstance(response, dict) and "error" in response:
                logger.error(f"Error from Rhetor: {response['error']}")
                raise RuntimeError(f"Rhetor LLM error: {response['error']}")
            else:
                return str(response)
        
        raise RuntimeError("No Rhetor client available")
    
    async def acomplete(self, messages: List[Dict[str, str]]) -> str:
        """
        Complete a conversation with the LLM through Rhetor (async).
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Generated text response
        """
        # Just use the same implementation as complete, which is already async
        return await self.complete(messages)
    
    async def acomplete_stream(
        self, 
        messages: List[Dict[str, str]], 
        callback: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM through Rhetor (async).
        
        Args:
            messages: List of message dictionaries
            callback: Optional callback function to receive chunks
        
        Yields:
            Generated text chunks
        """
        await self._ensure_initialized()
        
        formatted_messages = self._format_messages(messages)
        context_id = str(uuid.uuid4())
        provider_id = self._extract_provider_from_model()
        
        if self.client:
            # Use direct LLM client
            try:
                async for chunk_data in self.client.chat_stream(
                    messages=formatted_messages,
                    context_id=context_id,
                    model_id=self.model_name,
                    provider_id=provider_id,
                    options={
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                    }
                ):
                    if "error" in chunk_data:
                        logger.error(f"Error from Rhetor: {chunk_data['error']}")
                        raise RuntimeError(f"Rhetor LLM error: {chunk_data['error']}")
                    
                    content = chunk_data.get("chunk", "")
                    if content and not chunk_data.get("done", False):
                        if callback:
                            callback(content)
                        yield content
            except Exception as e:
                logger.error(f"Error streaming from Rhetor: {e}")
                if callback:
                    callback(f"Error: {str(e)}")
                yield f"Error: {str(e)}"
        
        elif self.rhetor_client:
            # Use Rhetor prompt client with streaming capability
            try:
                stream_response = await self.rhetor_client.invoke_capability(
                    "generate_completion_stream",
                    {
                        "messages": formatted_messages,
                        "model": self.model_name,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                    }
                )
                
                # Handle different possible response formats
                if isinstance(stream_response, AsyncGenerator):
                    async for chunk in stream_response:
                        if isinstance(chunk, dict) and "content" in chunk:
                            content = chunk["content"]
                        elif isinstance(chunk, str):
                            content = chunk
                        else:
                            content = str(chunk)
                        
                        if callback:
                            callback(content)
                        yield content
                elif isinstance(stream_response, dict) and "error" in stream_response:
                    error_msg = f"Rhetor LLM error: {stream_response['error']}"
                    logger.error(error_msg)
                    if callback:
                        callback(error_msg)
                    yield error_msg
                else:
                    # Not a streaming response, yield as a single chunk
                    content = str(stream_response)
                    if callback:
                        callback(content)
                    yield content
            except Exception as e:
                logger.error(f"Error streaming from Rhetor: {e}")
                error_msg = f"Error: {str(e)}"
                if callback:
                    callback(error_msg)
                yield error_msg
        
        else:
            error_msg = "No Rhetor client available"
            logger.error(error_msg)
            if callback:
                callback(error_msg)
            yield error_msg