#!/usr/bin/env python3
"""
Google Gemini Model Adapter

This module provides the adapter for Google's Gemini models.
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from .base import ModelAdapter, AdapterHealthStatus

# Configure logger
logger = logging.getLogger("tekton.models.adapters.gemini")


class GeminiAdapter(ModelAdapter):
    """Adapter for Google Gemini models."""

    def __init__(self, config=None):
        """
        Initialize Gemini adapter.
        
        Args:
            config: Configuration dictionary with at least 'api_key'
        """
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model = config.get("model", "gemini-1.5-pro")
        self.endpoint = config.get("endpoint", "https://generativelanguage.googleapis.com/v1beta")
        self.client = None
        
        # Set capabilities based on available Gemini models
        model_capabilities = {
            "gemini-1.5-pro": {
                "max_tokens": 8192,
                "context_window": 2097152,  # 2M context window
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": True,
                "supports_json_mode": True,
                "supports_function_calling": True
            },
            "gemini-1.5-flash": {
                "max_tokens": 8192,
                "context_window": 1048576,  # 1M context window
                "supports_streaming": True,
                "supports_vision": True,
                "supports_embeddings": True,
                "supports_json_mode": True,
                "supports_function_calling": True
            },
            "gemini-1.0-pro": {
                "max_tokens": 8192,
                "context_window": 32768,
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": True,
                "supports_json_mode": False,
                "supports_function_calling": True
            }
        }
        
        self.capabilities = model_capabilities.get(self.model, model_capabilities["gemini-1.5-pro"])
        
    async def initialize(self) -> bool:
        """
        Initialize the Gemini client.
        
        Returns:
            True if initialization was successful
        """
        if not self.api_key:
            logger.error("Gemini API key not found")
            self.health_status = AdapterHealthStatus.UNHEALTHY.value
            return False
            
        try:
            # Initialize client
            import httpx
            self.client = httpx.AsyncClient(
                base_url=self.endpoint,
                headers={
                    "Content-Type": "application/json"
                },
                params={
                    "key": self.api_key
                },
                timeout=httpx.Timeout(60.0)
            )
            
            # Test connection
            test_successful = await self.health_check()
            if test_successful:
                self.health_status = AdapterHealthStatus.HEALTHY.value
                logger.info(f"Gemini adapter initialized successfully with model {self.model}")
                return True
            else:
                self.health_status = AdapterHealthStatus.UNHEALTHY.value
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini adapter: {e}")
            self.health_status = AdapterHealthStatus.UNHEALTHY.value
            return False
            
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generate a response from Gemini.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Response dictionary
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
            
        try:
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                if msg["role"] == "system":
                    # Gemini handles system prompts differently - prepend to first user message
                    continue
                    
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Handle system prompt
            system_prompts = [msg["content"] for msg in messages if msg["role"] == "system"]
            if system_prompts and contents:
                # Prepend system prompt to first user message
                if contents[0]["role"] == "user":
                    contents[0]["parts"][0]["text"] = "\n".join(system_prompts) + "\n\n" + contents[0]["parts"][0]["text"]
            
            # Prepare request
            request_data = {
                "contents": contents,
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "maxOutputTokens": kwargs.get("max_tokens", self.capabilities["max_tokens"]),
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 40)
                }
            }
            
            # Add JSON mode if requested
            if kwargs.get("response_format", {}).get("type") == "json_object":
                request_data["generationConfig"]["responseMimeType"] = "application/json"
            
            start_time = time.time()
            
            # Make request
            response = await self.client.post(
                f"/models/{self.model}:generateContent",
                json=request_data
            )
            response.raise_for_status()
            
            elapsed_time = time.time() - start_time
            
            # Parse response
            result = response.json()
            
            # Extract content
            content = ""
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    content = " ".join(part.get("text", "") for part in candidate["content"]["parts"])
            
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
                "content": content,
                "model": self.model,
                "usage": result.get("usageMetadata", {}),
                "latency": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response from Gemini: {e}")
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
        Stream a response from Gemini.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
            
        try:
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                if msg["role"] == "system":
                    continue
                    
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Handle system prompt
            system_prompts = [msg["content"] for msg in messages if msg["role"] == "system"]
            if system_prompts and contents:
                if contents[0]["role"] == "user":
                    contents[0]["parts"][0]["text"] = "\n".join(system_prompts) + "\n\n" + contents[0]["parts"][0]["text"]
            
            # Prepare request
            request_data = {
                "contents": contents,
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "maxOutputTokens": kwargs.get("max_tokens", self.capabilities["max_tokens"]),
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 40)
                }
            }
            
            # Make streaming request
            async with self.client.stream(
                "POST",
                f"/models/{self.model}:streamGenerateContent",
                json=request_data
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            # Parse JSON response
                            chunk = json.loads(line)
                            
                            if "candidates" in chunk and chunk["candidates"]:
                                candidate = chunk["candidates"][0]
                                if "content" in candidate and "parts" in candidate["content"]:
                                    for part in candidate["content"]["parts"]:
                                        if "text" in part:
                                            yield {
                                                "content": part["text"],
                                                "done": False
                                            }
                        except json.JSONDecodeError:
                            continue
                            
            yield {"content": "", "done": True}
            
        except Exception as e:
            logger.error(f"Failed to stream from Gemini: {e}")
            raise
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings using Gemini.
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        if not self.capabilities.get("supports_embeddings"):
            raise NotImplementedError(f"Model {self.model} does not support embeddings")
            
        try:
            embeddings = []
            
            # Gemini embedding model
            embedding_model = "models/text-embedding-004"
            
            for text in texts:
                request_data = {
                    "model": embedding_model,
                    "content": {
                        "parts": [{"text": text}]
                    }
                }
                
                response = await self.client.post(
                    f"/{embedding_model}:embedContent",
                    json=request_data
                )
                response.raise_for_status()
                
                result = response.json()
                if "embedding" in result:
                    embeddings.append(result["embedding"]["values"])
                else:
                    raise ValueError("No embedding in response")
                    
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
            
    async def health_check(self) -> bool:
        """
        Check the health of the Gemini adapter.
        
        Returns:
            True if healthy
        """
        try:
            # List available models to verify connectivity
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
            
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
            self.client = None