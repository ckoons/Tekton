#!/usr/bin/env python3
"""
OpenAI Model Adapter

This module provides the adapter for OpenAI models.
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from .base import ModelAdapter, AdapterHealthStatus

# Configure logger
logger = logging.getLogger("tekton.models.adapters.openai")


class OpenAIAdapter(ModelAdapter):
    """Adapter for OpenAI models."""

    def __init__(self, config=None):
        """
        Initialize OpenAI adapter.
        
        Args:
            config: Configuration dictionary with at least 'api_key'
        """
        super().__init__(config)
        from shared.env import TektonEnviron
        self.api_key = config.get("api_key") or TektonEnviron.get("OPENAI_API_KEY")
        self.model = config.get("model", "gpt-4o")
        self.embedding_model = config.get("embedding_model", "text-embedding-3-large")
        self.client = None
        
        # Set capabilities
        model_capabilities = {
            "gpt-4o": {
                "max_tokens": 4096,
                "context_window": 128000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True,
                "supports_function_calling": True
            },
            "gpt-4-turbo": {
                "max_tokens": 4096,
                "context_window": 128000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True,
                "supports_function_calling": True
            },
            "gpt-4": {
                "max_tokens": 4096,
                "context_window": 8192,
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": False,
                "supports_json_mode": True,
                "supports_function_calling": True
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "context_window": 16385,
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": False,
                "supports_json_mode": True,
                "supports_function_calling": True
            }
        }
        
        if self.model in model_capabilities:
            self.config.update(model_capabilities[self.model])

    async def initialize(self) -> bool:
        """
        Initialize the OpenAI client.
        
        Returns:
            True if initialization was successful
        """
        try:
            # Check if API key is available
            if not self.api_key:
                logger.error("OpenAI API key not provided")
                return False
                
            # Import the OpenAI library
            from openai import AsyncOpenAI
            
            # Initialize client
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # Set health status to healthy
            self.health_status = AdapterHealthStatus.HEALTHY.value
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False

    async def generate(self, prompt, options=None) -> Dict[str, Any]:
        """
        Generate a response from OpenAI.
        
        Args:
            prompt: The prompt to send to the model
            options: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        options = options or {}
        
        # Try up to 3 times for transient errors
        for attempt in range(3):
            try:
                # Prepare messages
                if isinstance(prompt, list):
                    messages = prompt
                else:
                    messages = [{"role": "user", "content": prompt}]
                
                # Add system message if provided
                if options.get("system_prompt") and not any(m.get("role") == "system" for m in messages):
                    messages.insert(0, {"role": "system", "content": options["system_prompt"]})
                
                # Prepare parameters
                params = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": options.get("max_tokens", 1000),
                    "temperature": options.get("temperature", 0.7)
                }
                
                # Add response format if specified
                if options.get("response_format") == "json":
                    params["response_format"] = {"type": "json_object"}
                    
                # Add functions if specified
                if options.get("functions") and self.config.get("supports_function_calling", False):
                    params["tools"] = [
                        {
                            "type": "function",
                            "function": func
                        }
                        for func in options["functions"]
                    ]
                    
                # Generate response
                start_time = time.time()
                
                # Handle streaming if requested
                if options.get("stream", False) and self.config.get("supports_streaming", False):
                    if options.get("stream_handler"):
                        stream_handler = options["stream_handler"]
                        
                        # Generate streaming response
                        text_chunks = []
                        async for chunk in await self.client.chat.completions.create(
                            **params,
                            stream=True
                        ):
                            if chunk.choices and chunk.choices[0].delta.content:
                                text_chunk = chunk.choices[0].delta.content
                                text_chunks.append(text_chunk)
                                stream_handler(text_chunk)
                        
                        full_text = "".join(text_chunks)
                        duration = time.time() - start_time
                        
                        # Estimate token count (very rough)
                        token_count = len(full_text.split()) * 1.5
                        input_tokens = sum(len(m.get("content", "").split()) for m in messages) * 1.5
                    else:
                        # Without handler just use non-streaming mode
                        params.pop("stream", None)
                        response = await self.client.chat.completions.create(**params)
                        duration = time.time() - start_time
                        full_text = response.choices[0].message.content
                        token_count = response.usage.completion_tokens
                        input_tokens = response.usage.prompt_tokens
                else:
                    # Generate non-streaming response
                    response = await self.client.chat.completions.create(**params)
                    duration = time.time() - start_time
                    
                    # Extract response text
                    full_text = response.choices[0].message.content
                    token_count = response.usage.completion_tokens
                    input_tokens = response.usage.prompt_tokens
                    
                    # Handle function calls
                    function_call = None
                    if (response.choices[0].message.tool_calls and 
                        response.choices[0].message.tool_calls[0].function):
                        func_call = response.choices[0].message.tool_calls[0].function
                        function_call = {
                            "name": func_call.name,
                            "arguments": json.loads(func_call.arguments)
                        }
                
                # Update metrics
                self.metrics["total_requests"] = self.metrics.get("total_requests", 0) + 1
                self.metrics["total_tokens"] = self.metrics.get("total_tokens", 0) + token_count
                self.metrics["total_input_tokens"] = self.metrics.get("total_input_tokens", 0) + input_tokens
                self.metrics["average_latency"] = (
                    (self.metrics.get("average_latency", 0) * (self.metrics["total_requests"] - 1)) 
                    + duration
                ) / self.metrics["total_requests"]
                
                # Update health status
                self._update_health_status(True)
                
                result = {
                    "text": full_text,
                    "model": self.model,
                    "tokens": token_count,
                    "latency": duration,
                    "provider": "openai"
                }
                
                # Add function call if present
                if function_call:
                    result["function_call"] = function_call
                
                return result
                
            except Exception as e:
                # Check for rate limiting
                error_message = str(e).lower()
                is_rate_limit = "rate limit" in error_message or "too many requests" in error_message
                
                # Update error metrics
                self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
                if is_rate_limit:
                    self.metrics["rate_limit_errors"] = self.metrics.get("rate_limit_errors", 0) + 1
                    await self._handle_rate_limit(attempt)
                    continue
                
                self._update_health_status(False)
                
                logger.error(f"OpenAI generation error: {str(e)}")
                
                if attempt == 2:  # Last attempt
                    raise Exception(f"OpenAI generation error: {str(e)}")
                
                # Wait before retrying
                await asyncio.sleep(1)
        
        # Should never reach here due to exceptions
        return {"error": "Max retries exceeded"}

    async def embed(self, text, options=None) -> Dict[str, Any]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed (string or list of strings)
            options: Optional embedding parameters
            
        Returns:
            Dictionary with embedding and metadata
        """
        options = options or {}
        
        # Try up to 3 times for transient errors
        for attempt in range(3):
            try:
                # Prepare text input
                if isinstance(text, list):
                    input_texts = text
                else:
                    input_texts = [text]
                
                # Prepare parameters
                params = {
                    "model": options.get("model", self.embedding_model),
                    "input": input_texts,
                    "dimensions": options.get("dimensions")
                }
                
                # Generate embeddings
                start_time = time.time()
                response = await self.client.embeddings.create(**params)
                duration = time.time() - start_time
                
                # Extract embeddings
                embeddings = [data.embedding for data in response.data]
                
                # Update metrics
                self.metrics["total_embed_requests"] = self.metrics.get("total_embed_requests", 0) + 1
                self.metrics["total_embed_tokens"] = self.metrics.get("total_embed_tokens", 0) + response.usage.total_tokens
                self.metrics["average_embed_latency"] = (
                    (self.metrics.get("average_embed_latency", 0) * (self.metrics["total_embed_requests"] - 1)) 
                    + duration
                ) / self.metrics["total_embed_requests"]
                
                # Update health status
                self._update_health_status(True)
                
                return {
                    "embeddings": embeddings[0] if len(embeddings) == 1 else embeddings,
                    "model": params["model"],
                    "dimensions": len(embeddings[0]),
                    "tokens": response.usage.total_tokens,
                    "latency": duration,
                    "provider": "openai"
                }
                
            except Exception as e:
                # Check for rate limiting
                error_message = str(e).lower()
                is_rate_limit = "rate limit" in error_message or "too many requests" in error_message
                
                # Update error metrics
                self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
                if is_rate_limit:
                    self.metrics["rate_limit_errors"] = self.metrics.get("rate_limit_errors", 0) + 1
                    await self._handle_rate_limit(attempt)
                    continue
                
                self._update_health_status(False)
                
                logger.error(f"OpenAI embedding error: {str(e)}")
                
                if attempt == 2:  # Last attempt
                    raise Exception(f"OpenAI embedding error: {str(e)}")
                
                # Wait before retrying
                await asyncio.sleep(1)
        
        # Should never reach here due to exceptions
        return {"error": "Max retries exceeded"}