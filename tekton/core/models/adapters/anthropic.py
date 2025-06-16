#!/usr/bin/env python3
"""
Anthropic Model Adapter

This module provides the adapter for Anthropic Claude models.
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from .base import ModelAdapter, AdapterHealthStatus

# Configure logger
logger = logging.getLogger("tekton.models.adapters.anthropic")


class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic Claude models."""

    def __init__(self, config=None):
        """
        Initialize Anthropic adapter.
        
        Args:
            config: Configuration dictionary with at least 'api_key'
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        self.model = config.get("model", "claude-3-opus-20240229")
        self.client = None
        
        # Set capabilities
        model_capabilities = {
            "claude-3-opus-20240229": {
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True
            },
            "claude-3-sonnet-20240229": {
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 4096, 
                "context_window": 200000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True
            },
            "claude-3-5-sonnet-20240620": {
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True
            },
            "claude-3-7-sonnet-20240620": {
                "max_tokens": 4096,
                "context_window": 200000,
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": False,
                "supports_json_mode": True
            }
        }
        
        if self.model in model_capabilities:
            self.config.update(model_capabilities[self.model])

    async def initialize(self) -> bool:
        """
        Initialize the Anthropic client.
        
        Returns:
            True if initialization was successful
        """
        try:
            # Check if API key is available
            if not self.api_key:
                logger.error("Anthropic API key not provided")
                return False
                
            # Import the Anthropic library
            import anthropic
            
            # Initialize client
            self.client = anthropic.Client(api_key=self.api_key)
            
            # Set health status to healthy
            self.health_status = AdapterHealthStatus.HEALTHY.value
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            return False

    async def generate(self, prompt, options=None) -> Dict[str, Any]:
        """
        Generate a response from Claude.
        
        Args:
            prompt: The prompt to send to Claude
            options: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        options = options or {}
        
        # Try up to 3 times for transient errors
        for attempt in range(3):
            try:
                # Prepare message
                if isinstance(prompt, list):
                    messages = prompt
                else:
                    messages = [{"role": "user", "content": prompt}]
                
                # Prepare parameters
                params = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": options.get("max_tokens", 1000),
                    "temperature": options.get("temperature", 0.7),
                }
                
                # Add system prompt if provided
                if options.get("system_prompt"):
                    params["system"] = options["system_prompt"]
                    
                # Add response format if specified
                if options.get("response_format") == "json":
                    params["response_format"] = {"type": "json"}
                    
                # Add streaming parameter if specified
                if options.get("stream", False) and self.config.get("supports_streaming", False):
                    if options.get("stream_handler"):
                        stream_handler = options["stream_handler"]
                        
                        # Generate streaming response
                        start_time = time.time()
                        with self.client.messages.stream(**params) as stream:
                            text_chunks = []
                            for chunk in stream:
                                if chunk.type == "content_block_delta" and hasattr(chunk.delta, "text"):
                                    text_chunk = chunk.delta.text
                                    text_chunks.append(text_chunk)
                                    stream_handler(text_chunk)
                        
                        full_text = "".join(text_chunks)
                        duration = time.time() - start_time
                        
                        # Estimate token count (very rough)
                        token_count = len(full_text.split()) * 1.5
                    else:
                        # Without handler just use non-streaming mode
                        params.pop("stream", None)
                        response = self.client.messages.create(**params)
                        duration = time.time() - start_time
                        full_text = response.content[0].text
                        token_count = response.usage.output_tokens
                else:
                    # Generate non-streaming response
                    start_time = time.time()
                    response = self.client.messages.create(**params)
                    duration = time.time() - start_time
                    
                    # Extract response text
                    full_text = response.content[0].text
                    token_count = response.usage.output_tokens
                    
                # Update metrics
                self.metrics["total_requests"] = self.metrics.get("total_requests", 0) + 1
                self.metrics["total_tokens"] = self.metrics.get("total_tokens", 0) + token_count
                self.metrics["total_input_tokens"] = self.metrics.get("total_input_tokens", 0) + (
                    response.usage.input_tokens if hasattr(response, "usage") else 0
                )
                self.metrics["average_latency"] = (
                    (self.metrics.get("average_latency", 0) * (self.metrics["total_requests"] - 1)) 
                    + duration
                ) / self.metrics["total_requests"]
                
                # Update health status
                self._update_health_status(True)
                
                return {
                    "text": full_text,
                    "model": self.model,
                    "tokens": token_count,
                    "latency": duration,
                    "provider": "anthropic"
                }
                
            except Exception as e:
                # Check if this is a rate limit error
                if hasattr(e, "__module__") and e.__module__ == "anthropic.error":
                    if e.__class__.__name__ == "RateLimitError":
                        self.metrics["rate_limit_errors"] = self.metrics.get("rate_limit_errors", 0) + 1
                        await self._handle_rate_limit(attempt)
                        continue
                
                # Update error metrics
                self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
                self._update_health_status(False)
                
                logger.error(f"Anthropic generation error: {str(e)}")
                
                if attempt == 2:  # Last attempt
                    raise Exception(f"Anthropic generation error: {str(e)}")
                
                # Wait before retrying
                await asyncio.sleep(1)
        
        # Should never reach here due to exceptions
        return {"error": "Max retries exceeded"}

    async def embed(self, text, options=None) -> Dict[str, Any]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            options: Optional embedding parameters
            
        Returns:
            Dictionary with embedding and metadata
        """
        # Claude doesn't support embeddings yet
        raise NotImplementedError("Claude doesn't support embeddings yet")