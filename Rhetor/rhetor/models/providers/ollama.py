"""
Ollama provider implementation for Rhetor.

This module provides the implementation for the Ollama provider for local LLMs.
"""

import os
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from .base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """Provider for Ollama local LLMs"""
    
    def __init__(self):
        """Initialize the Ollama provider"""
        super().__init__("ollama", "Ollama Local LLMs")
        self.api_base = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
        self.session = None
        self.default_model = "llama3"
        self.default_max_tokens = 2048
        self.default_temperature = 0.7
        self.available = False
        self.models_cache = []
        
    async def _initialize(self) -> bool:
        """
        Initialize the Ollama client.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create the aiohttp session
            self.session = aiohttp.ClientSession()
            
            # Test connection by listing models
            async with self.session.get(f"{self.api_base}/api/tags") as resp:
                if resp.status == 200:
                    models_data = await resp.json()
                    self.models_cache = models_data.get("models", [])
                    self.available = True
                    logger.info(f"Ollama provider initialized with API base {self.api_base}")
                    return True
                else:
                    logger.warning(f"Ollama API returned status {resp.status}")
                    self.available = False
                    return False
        except Exception as e:
            logger.error(f"Error initializing Ollama client: {e}")
            self.available = False
            return False
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get available Ollama models.
        
        Returns:
            List of dictionaries with model info
        """
        # Return cached models if available
        if self.models_cache:
            return [{"id": model["name"], "name": model["name"]} for model in self.models_cache]
        
        # Otherwise, return some common models
        return [
            {"id": "llama3", "name": "Llama 3"},
            {"id": "mixtral", "name": "Mixtral"},
            {"id": "mistral", "name": "Mistral"},
            {"id": "gemma", "name": "Gemma"},
            {"id": "phi3", "name": "Phi-3"}
        ]
    
    async def complete(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a message with Ollama.
        
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
        
        if not self.available or not self.session:
            return {
                "error": "Ollama is not available.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If streaming is requested, just return a placeholder
            # The actual streaming happens in the stream method
            if streaming:
                return {
                    "message": "",
                    "model": model,
                    "provider": "ollama",
                    "finished": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the request payload
            payload = {
                "model": model,
                "prompt": message,
                "stream": False,
                "options": {
                    "temperature": options.get("temperature", self.default_temperature),
                    "num_predict": options.get("max_tokens", self.default_max_tokens)
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            # Call the Ollama API
            async with self.session.post(f"{self.api_base}/api/generate", json=payload) as resp:
                if resp.status != 200:
                    return {
                        "error": f"Ollama API returned status {resp.status}",
                        "model": model,
                        "provider": "ollama",
                        "timestamp": datetime.now().isoformat()
                    }
                
                response = await resp.json()
                
                return {
                    "message": response.get("response", ""),
                    "model": model,
                    "provider": "ollama",
                    "finished": True,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error completing message with Ollama: {e}")
            return {
                "error": str(e),
                "model": model,
                "provider": "ollama",
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
        Stream a completion from Ollama.
        
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
        
        if not self.available or not self.session:
            yield ""
            return
        
        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "prompt": message,
                "stream": True,
                "options": {
                    "temperature": options.get("temperature", self.default_temperature),
                    "num_predict": options.get("max_tokens", self.default_max_tokens)
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            # Call the Ollama API with streaming
            async with self.session.post(f"{self.api_base}/api/generate", json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"Ollama API returned status {resp.status}")
                    yield ""
                    return
                
                # Process the streaming response
                buffer = ""
                async for line in resp.content:
                    if not line:
                        continue
                    
                    try:
                        # Each line is a JSON object
                        buffer += line.decode('utf-8')
                        if buffer.endswith('\n'):
                            lines = buffer.strip().split('\n')
                            buffer = ""
                            for line_str in lines:
                                if not line_str:
                                    continue
                                
                                import json
                                chunk = json.loads(line_str)
                                if "response" in chunk:
                                    yield chunk["response"]
                    except Exception as e:
                        logger.error(f"Error processing Ollama stream chunk: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error streaming from Ollama: {e}")
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
        Complete a chat conversation with Ollama.
        
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
        
        if not self.available or not self.session:
            return {
                "error": "Ollama is not available.",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If streaming is requested, just return a placeholder
            if streaming:
                return {
                    "message": "",
                    "model": model,
                    "provider": "ollama",
                    "finished": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Convert the chat history to Ollama's chat format
            # Ollama expects a flat array of messages
            ollama_messages = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": options.get("temperature", self.default_temperature),
                    "num_predict": options.get("max_tokens", self.default_max_tokens)
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            # Call the Ollama API
            async with self.session.post(f"{self.api_base}/api/chat", json=payload) as resp:
                if resp.status != 200:
                    return {
                        "error": f"Ollama API returned status {resp.status}",
                        "model": model,
                        "provider": "ollama",
                        "timestamp": datetime.now().isoformat()
                    }
                
                response = await resp.json()
                
                return {
                    "message": response.get("message", {}).get("content", ""),
                    "model": model,
                    "provider": "ollama",
                    "finished": True,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error completing chat with Ollama: {e}")
            return {
                "error": str(e),
                "model": model,
                "provider": "ollama",
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
        Stream a chat completion from Ollama.
        
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
        
        if not self.available or not self.session:
            yield ""
            return
        
        try:
            # Convert the chat history to Ollama's chat format
            ollama_messages = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    "temperature": options.get("temperature", self.default_temperature),
                    "num_predict": options.get("max_tokens", self.default_max_tokens)
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            # Call the Ollama API with streaming
            async with self.session.post(f"{self.api_base}/api/chat", json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"Ollama API returned status {resp.status}")
                    yield ""
                    return
                
                # Process the streaming response
                buffer = ""
                async for line in resp.content:
                    if not line:
                        continue
                    
                    try:
                        # Each line is a JSON object
                        buffer += line.decode('utf-8')
                        if buffer.endswith('\n'):
                            lines = buffer.strip().split('\n')
                            buffer = ""
                            for line_str in lines:
                                if not line_str:
                                    continue
                                
                                import json
                                chunk = json.loads(line_str)
                                if "message" in chunk and "content" in chunk["message"]:
                                    yield chunk["message"]["content"]
                    except Exception as e:
                        logger.error(f"Error processing Ollama stream chunk: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error streaming chat from Ollama: {e}")
            yield ""