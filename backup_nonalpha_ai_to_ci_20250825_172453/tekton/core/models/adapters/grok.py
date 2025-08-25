#!/usr/bin/env python3
"""
Grok (X.AI) Model Adapter

This module provides the adapter for X.AI's Grok models.
"""

import os
from shared.env import TektonEnviron
import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from .base import ModelAdapter, AdapterHealthStatus

# Configure logger
logger = logging.getLogger("tekton.models.adapters.grok")


class GrokAdapter(ModelAdapter):
    """Adapter for X.AI Grok models."""

    def __init__(self, config=None):
        """
        Initialize Grok adapter.
        
        Args:
            config: Configuration dictionary with at least 'api_key'
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or TektonEnviron.get("GROK_API_KEY")
        self.model = config.get("model", "grok-beta")
        self.endpoint = config.get("endpoint", "https://api.x.ai/v1")
        self.client = None
        
        # Set capabilities based on available Grok models
        model_capabilities = {
            "grok-beta": {
                "max_tokens": 25000,
                "context_window": 131072,  # 128K context
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": False,
                "supports_json_mode": False,
                "supports_function_calling": False
            }
        }
        
        self.capabilities = model_capabilities.get(self.model, model_capabilities["grok-beta"])
        
    async def initialize(self) -> bool:
        """
        Initialize the Grok client.
        
        Returns:
            True if initialization was successful
        """
        if not self.api_key:
            logger.error("Grok API key not found")
            self.health_status = AdapterHealthStatus.UNHEALTHY.value
            return False
            
        try:
            # Initialize client (using OpenAI-compatible interface)
            import httpx
            self.client = httpx.AsyncClient(
                base_url=self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=httpx.Timeout(60.0)
            )
            
            # Test connection
            test_successful = await self.health_check()
            if test_successful:
                self.health_status = AdapterHealthStatus.HEALTHY.value
                logger.info(f"Grok adapter initialized successfully with model {self.model}")
                return True
            else:
                self.health_status = AdapterHealthStatus.UNHEALTHY.value
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Grok adapter: {e}")
            self.health_status = AdapterHealthStatus.UNHEALTHY.value
            return False
            
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generate a response from Grok.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Response dictionary
        """
        if not self.client:
            raise RuntimeError("Grok client not initialized")
            
        try:
            # Prepare request
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", self.capabilities["max_tokens"]),
                "stream": kwargs.get("stream", False)
            }
            
            # Remove None values
            request_data = {k: v for k, v in request_data.items() if v is not None}
            
            start_time = time.time()
            
            # Make request using OpenAI-compatible endpoint
            response = await self.client.post("/chat/completions", json=request_data)
            response.raise_for_status()
            
            elapsed_time = time.time() - start_time
            
            # Parse response
            result = response.json()
            
            # Update metrics
            self.metrics["requests_total"] = self.metrics.get("requests_total", 0) + 1
            self.metrics["requests_succeeded"] = self.metrics.get("requests_succeeded", 0) + 1
            self.metrics["average_latency"] = (
                (self.metrics.get("average_latency", 0) * self.metrics.get("requests_succeeded", 1) + elapsed_time) /
                (self.metrics.get("requests_succeeded", 1) + 1)
            )
            
            # Reset failure tracking on success
            self.consecutive_failures = 0
            
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": result.get("model", self.model),
                "usage": result.get("usage", {}),
                "latency": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response from Grok: {e}")
            self.consecutive_failures += 1
            self.last_failure_time = time.time()
            self.metrics["requests_total"] = self.metrics.get("requests_total", 0) + 1
            self.metrics["requests_failed"] = self.metrics.get("requests_failed", 0) + 1
            
            # Update health status
            if self.consecutive_failures >= 3:
                self.health_status = AdapterHealthStatus.UNHEALTHY.value
            elif self.consecutive_failures >= 1:
                self.health_status = AdapterHealthStatus.DEGRADED.value
                
            raise
            
    async def stream_generate(self, messages: List[Dict[str, str]], **kwargs):
        """
        Stream a response from Grok.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        if not self.client:
            raise RuntimeError("Grok client not initialized")
            
        kwargs["stream"] = True
        
        try:
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", self.capabilities["max_tokens"]),
                "stream": True
            }
            
            # Remove None values
            request_data = {k: v for k, v in request_data.items() if v is not None}
            
            # Make streaming request
            async with self.client.stream("POST", "/chat/completions", json=request_data) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                            
                        try:
                            chunk = json.loads(data)
                            if chunk["choices"][0]["delta"].get("content"):
                                yield {
                                    "content": chunk["choices"][0]["delta"]["content"],
                                    "done": False
                                }
                        except json.JSONDecodeError:
                            continue
                            
            yield {"content": "", "done": True}
            
        except Exception as e:
            logger.error(f"Failed to stream from Grok: {e}")
            raise
            
    async def health_check(self) -> bool:
        """
        Check the health of the Grok adapter.
        
        Returns:
            True if healthy
        """
        try:
            # Try a simple completion to verify connectivity
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Grok health check failed: {e}")
            return False
            
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
            self.client = None