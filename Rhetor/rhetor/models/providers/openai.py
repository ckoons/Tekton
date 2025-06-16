"""
OpenAI provider implementation for Rhetor.

This module provides the implementation for the OpenAI provider.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from .base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI models"""
    
    def __init__(self):
        """Initialize the OpenAI provider"""
        super().__init__("openai", "OpenAI")
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.client = None
        self.default_model = "gpt-4o"
        self.default_max_tokens = 2048
        self.default_temperature = 0.7
        self.available = False
        
    async def _initialize(self) -> bool:
        """
        Initialize the OpenAI client.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Only import if we have an API key
            if not self.api_key:
                logger.warning("OPENAI_API_KEY not set. OpenAI integration is disabled.")
                self.available = False
                return False
                
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # Test connection by listing models
            await self.client.models.list()
            
            self.available = True
            logger.info(f"OpenAI provider initialized with default model {self.default_model}")
            return True
        except ImportError:
            logger.error("openai package not installed. OpenAI integration is disabled.")
            self.available = False
            return False
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.available = False
            return False
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get available OpenAI models.
        
        Returns:
            List of dictionaries with model info
        """
        models = [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
        ]
        
        return models
    
    async def complete(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a message with OpenAI.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        model = model or self.default_model
        
        if not self.available or not self.client:
            return {
                "error": "OpenAI is not available.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If streaming is requested, just return a placeholder
            # The actual streaming happens in the stream method
            if streaming:
                return {
                    "message": "",
                    "model": model,
                    "provider": "openai",
                    "finished": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Create the messages list
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            # Non-streaming completion
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=options.get("max_tokens", self.default_max_tokens),
                temperature=options.get("temperature", self.default_temperature)
            )
            
            return {
                "message": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "finished": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error completing message with OpenAI: {e}")
            return {
                "error": str(e),
                "model": model,
                "provider": "openai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from OpenAI.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            options: Additional options for the LLM
            
        Yields:
            Completion chunks as they are generated
        """
        options = options or {}
        model = model or self.default_model
        
        if not self.available or not self.client:
            yield ""
            return
        
        try:
            # Create the messages list
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            # Create a streaming request
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=options.get("max_tokens", self.default_max_tokens),
                temperature=options.get("temperature", self.default_temperature),
                stream=True
            )
            
            # Process the stream
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming from OpenAI: {e}")
            yield ""
    
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a chat conversation with OpenAI.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        model = model or self.default_model
        
        if not self.available or not self.client:
            return {
                "error": "OpenAI is not available.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If streaming is requested, just return a placeholder
            if streaming:
                return {
                    "message": "",
                    "model": model,
                    "provider": "openai",
                    "finished": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Create the messages list with system prompt if provided
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            # Add the conversation messages
            for msg in messages:
                openai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Non-streaming completion
            response = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=options.get("max_tokens", self.default_max_tokens),
                temperature=options.get("temperature", self.default_temperature)
            )
            
            return {
                "message": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "finished": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error completing chat with OpenAI: {e}")
            return {
                "error": str(e),
                "model": model,
                "provider": "openai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion from OpenAI.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            options: Additional options for the LLM
            
        Yields:
            Completion chunks as they are generated
        """
        options = options or {}
        model = model or self.default_model
        
        if not self.available or not self.client:
            yield ""
            return
        
        try:
            # Create the messages list with system prompt if provided
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            
            # Add the conversation messages
            for msg in messages:
                openai_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Create a streaming request
            stream = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=options.get("max_tokens", self.default_max_tokens),
                temperature=options.get("temperature", self.default_temperature),
                stream=True
            )
            
            # Process the stream
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming chat from OpenAI: {e}")
            yield ""