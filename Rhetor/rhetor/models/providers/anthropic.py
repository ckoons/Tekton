"""
Anthropic (Claude) provider implementation for Rhetor.

This module provides the implementation for the Anthropic Claude provider.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from .base import LLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models"""
    
    def __init__(self):
        """Initialize the Anthropic provider"""
        super().__init__("anthropic", "Anthropic Claude")
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = None
        self.default_model = "claude-3-sonnet-20240229"
        self.default_max_tokens = 4000
        self.default_temperature = 0.7
        self.available = False
        
    async def _initialize(self) -> bool:
        """
        Initialize the Anthropic client.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Only import if we have an API key
            if not self.api_key:
                logger.warning("ANTHROPIC_API_KEY not set. Claude integration is disabled.")
                self.available = False
                return False
                
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            # Test connection by getting model list
            await asyncio.to_thread(lambda: self.client.models.list())
            self.available = True
            logger.info(f"Anthropic Claude provider initialized with default model {self.default_model}")
            return True
        except ImportError:
            logger.error("anthropic package not installed. Claude integration is disabled.")
            self.available = False
            return False
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {e}")
            self.available = False
            return False
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get available Claude models.
        
        Returns:
            List of dictionaries with model info
        """
        # Claude models (3rd generation)
        models = [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
            {"id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet"}
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
        Complete a message with Claude.
        
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
                "error": "Anthropic Claude is not available.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If streaming is requested, just return a placeholder
            # The actual streaming happens in the stream method
            if streaming:
                return {
                    "message": "",
                    "model": model,
                    "provider": "anthropic",
                    "finished": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Non-streaming completion
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=model,
                max_tokens=options.get("max_tokens", self.default_max_tokens),
                temperature=options.get("temperature", self.default_temperature),
                system=system_prompt,
                messages=[{"role": "user", "content": message}]
            )
            
            return {
                "message": response.content[0].text,
                "model": model,
                "provider": "anthropic",
                "finished": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error completing message with Claude: {e}")
            return {
                "error": str(e),
                "model": model,
                "provider": "anthropic",
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
        Stream a completion from Claude.
        
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
            # Create a streaming request to Claude
            kwargs = {
                "model": model,
                "max_tokens": options.get("max_tokens", self.default_max_tokens),
                "temperature": options.get("temperature", self.default_temperature),
                "messages": [{"role": "user", "content": message}]
            }
            
            # Only add system if it's a non-empty string
            if system_prompt and isinstance(system_prompt, str):
                kwargs["system"] = system_prompt
                
            stream = self.client.messages.stream(**kwargs)
            
            # Process the stream
            with stream as s:
                for text in s.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Error streaming from Claude: {e}")
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
        Complete a chat conversation with Claude.
        
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
                "error": "Anthropic Claude is not available.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If streaming is requested, just return a placeholder
            if streaming:
                return {
                    "message": "",
                    "model": model,
                    "provider": "anthropic",
                    "finished": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Convert messages to Anthropic format if needed
            anthropic_messages = []
            for msg in messages:
                role = msg["role"]
                # Anthropic only supports "user" and "assistant" roles
                if role not in ["user", "assistant"]:
                    role = "user"
                anthropic_messages.append({"role": role, "content": msg["content"]})
            
            # Non-streaming completion
            kwargs = {
                "model": model,
                "max_tokens": options.get("max_tokens", self.default_max_tokens),
                "temperature": options.get("temperature", self.default_temperature),
                "messages": anthropic_messages
            }
            
            # Only add system if it's a non-empty string
            if system_prompt and isinstance(system_prompt, str):
                kwargs["system"] = system_prompt
                
            response = await asyncio.to_thread(
                self.client.messages.create,
                **kwargs
            )
            
            return {
                "message": response.content[0].text,
                "model": model,
                "provider": "anthropic",
                "finished": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error completing chat with Claude: {e}")
            return {
                "error": str(e),
                "model": model,
                "provider": "anthropic",
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
        Stream a chat completion from Claude.
        
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
            # Convert messages to Anthropic format if needed
            anthropic_messages = []
            for msg in messages:
                role = msg["role"]
                # Anthropic only supports "user" and "assistant" roles
                if role not in ["user", "assistant"]:
                    role = "user"
                anthropic_messages.append({"role": role, "content": msg["content"]})
            
            # Create a streaming request to Claude
            kwargs = {
                "model": model,
                "max_tokens": options.get("max_tokens", self.default_max_tokens),
                "temperature": options.get("temperature", self.default_temperature),
                "messages": anthropic_messages
            }
            
            # Only add system if it's a non-empty string
            if system_prompt and isinstance(system_prompt, str):
                kwargs["system"] = system_prompt
                
            stream = self.client.messages.stream(**kwargs)
            
            # Process the stream
            with stream as s:
                for text in s.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Error streaming chat from Claude: {e}")
            yield ""