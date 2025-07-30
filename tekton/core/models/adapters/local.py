#!/usr/bin/env python3
"""
Local Model Adapter

This module provides the adapter for local models via Ollama or OpenAI-compatible APIs.
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

from .base import ModelAdapter, AdapterHealthStatus

# Configure logger
logger = logging.getLogger("tekton.models.adapters.local")


class LocalModelAdapter(ModelAdapter):
    """Adapter for local models (Ollama, LM Studio, etc.)."""

    def __init__(self, config=None):
        """
        Initialize local model adapter.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.endpoint = config.get("endpoint", "http://localhost:11434")
        self.model = config.get("model", "llama3")
        
        # Set capabilities based on model
        model_capabilities = {
            "llama3": {
                "max_tokens": 4096,
                "context_window": 8192,
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": True,
                "supports_json_mode": False
            },
            "llama3.3": {
                "max_tokens": 8192,
                "context_window": 131072,  # 128K context
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": True,
                "supports_json_mode": False
            },
            "mixtral": {
                "max_tokens": 4096,
                "context_window": 32768,
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": True,
                "supports_json_mode": False
            },
            "codellama": {
                "max_tokens": 4096,
                "context_window": 16384,
                "supports_streaming": True,
                "supports_vision": False,
                "supports_embeddings": True,
                "supports_json_mode": False
            }
        }
        
        # Extract model base name (without tags)
        model_base = self.model.split(":")[0]
        
        if model_base in model_capabilities:
            self.config.update(model_capabilities[model_base])

    async def initialize(self) -> bool:
        """
        Initialize the local model client.
        
        Returns:
            True if initialization was successful
        """
        try:
            # Simple validation of endpoint
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Try to ping the server
                try:
                    # For Ollama - use api/version or api/tags endpoint
                    async with session.get(f"{self.endpoint}/api/version") as response:
                        if response.status == 200:
                            self.health_status = AdapterHealthStatus.HEALTHY.value
                            return True
                except:
                    # For LM Studio
                    try:
                        async with session.get(f"{self.endpoint}/v1/models") as response:
                            if response.status == 200:
                                self.health_status = AdapterHealthStatus.HEALTHY.value
                                return True
                    except:
                        pass
            
            logger.warning(f"Local model endpoint {self.endpoint} not reachable")
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize local model adapter: {e}")
            return False

    async def generate(self, prompt, options=None) -> Dict[str, Any]:
        """
        Generate a response from local model.
        
        Args:
            prompt: The prompt to send to the model
            options: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        options = options or {}
        
        try:
            import aiohttp
            
            # Determine if this is Ollama or OpenAI-compatible API
            is_ollama = "ollama" in self.endpoint or self.endpoint.endswith(":11434")
            
            # Prepare request based on API type
            if is_ollama:
                # Prepare Ollama chat-style request
                if isinstance(prompt, list):
                    messages = prompt
                else:
                    messages = [{"role": "user", "content": prompt}]
                
                # Add system message if provided in options
                if options.get("system_prompt") and not any(m.get("role") == "system" for m in messages):
                    messages.insert(0, {"role": "system", "content": options["system_prompt"]})
                
                request_data = {
                    "model": self.model,
                    "messages": messages,
                    "stream": options.get("stream", False),
                    "options": {
                        "temperature": options.get("temperature", 0.7),
                        "top_p": options.get("top_p", 0.95),
                        "top_k": options.get("top_k", 40),
                        "num_ctx": self.config.get("context_window", 8192)
                    }
                }
                
                # Set max tokens if specified
                if options.get("max_tokens"):
                    request_data["options"]["num_predict"] = options["max_tokens"]
                
                api_url = f"{self.endpoint}/api/chat"
            else:
                # Prepare OpenAI-compatible request
                if isinstance(prompt, list):
                    messages = prompt
                else:
                    messages = [{"role": "user", "content": prompt}]
                
                # Add system message if provided
                if options.get("system_prompt") and not any(m.get("role") == "system" for m in messages):
                    messages.insert(0, {"role": "system", "content": options["system_prompt"]})
                
                request_data = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": options.get("max_tokens", 1000),
                    "temperature": options.get("temperature", 0.7),
                    "stream": options.get("stream", False)
                }
                
                api_url = f"{self.endpoint}/v1/chat/completions"
            
            # Generate response
            start_time = time.time()
            
            # Handle streaming if requested
            if options.get("stream", False) and self.config.get("supports_streaming", False):
                if options.get("stream_handler"):
                    stream_handler = options["stream_handler"]
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api_url, json=request_data) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                raise Exception(f"HTTP error {response.status}: {error_text}")
                            
                            text_chunks = []
                            
                            if is_ollama:
                                # Process Ollama streaming format
                                async for line in response.content:
                                    try:
                                        chunk = json.loads(line)
                                        if "response" in chunk:
                                            text_chunk = chunk["response"]
                                            text_chunks.append(text_chunk)
                                            stream_handler(text_chunk)
                                    except json.JSONDecodeError:
                                        continue
                            else:
                                # Process OpenAI-compatible streaming format
                                async for line in response.content:
                                    try:
                                        line_text = line.decode('utf-8').strip()
                                        if line_text.startswith('data: '):
                                            data_str = line_text[6:]
                                            if data_str == "[DONE]":
                                                break
                                                
                                            try:
                                                chunk = json.loads(data_str)
                                                if chunk["choices"][0]["delta"].get("content"):
                                                    text_chunk = chunk["choices"][0]["delta"]["content"]
                                                    text_chunks.append(text_chunk)
                                                    stream_handler(text_chunk)
                                            except (json.JSONDecodeError, KeyError, IndexError):
                                                continue
                                    except Exception:
                                        continue
                    
                    full_text = "".join(text_chunks)
                    duration = time.time() - start_time
                    
                    # Estimate token count (very rough)
                    token_count = len(full_text.split()) * 1.5
                else:
                    # Without handler just use non-streaming mode
                    request_data["stream"] = False
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(api_url, json=request_data) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                raise Exception(f"HTTP error {response.status}: {error_text}")
                            
                            result = await response.json()
                    
                    duration = time.time() - start_time
                    
                    if is_ollama:
                        # For chat API, response is in message.content
                        full_text = result.get("message", {}).get("content", "")
                        token_count = result.get("eval_count", 0)
                    else:
                        full_text = result["choices"][0]["message"]["content"]
                        token_count = result.get("usage", {}).get("completion_tokens", 0)
            else:
                # Non-streaming request
                async with aiohttp.ClientSession() as session:
                    async with session.post(api_url, json=request_data) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"HTTP error {response.status}: {error_text}")
                        
                        result = await response.json()
                
                duration = time.time() - start_time
                
                if is_ollama:
                    # For chat API, response is in message.content
                    full_text = result.get("message", {}).get("content", "")
                    token_count = result.get("eval_count", 0)
                else:
                    full_text = result["choices"][0]["message"]["content"]
                    token_count = result.get("usage", {}).get("completion_tokens", 0)
            
            # Update metrics
            self.metrics["total_requests"] = self.metrics.get("total_requests", 0) + 1
            self.metrics["total_tokens"] = self.metrics.get("total_tokens", 0) + token_count
            self.metrics["average_latency"] = (
                (self.metrics.get("average_latency", 0) * (self.metrics["total_requests"] - 1)) 
                + duration
            ) / self.metrics["total_requests"]
            
            # Update health status
            self._update_health_status(True)
            
            return {
                "content": full_text,
                "model": self.model,
                "usage": {
                    "total_tokens": token_count
                },
                "latency": duration,
                "provider": "local"
            }
            
        except Exception as e:
            # Update error metrics
            self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
            self._update_health_status(False)
            
            logger.error(f"Local model generation error: {str(e)}")
            raise Exception(f"Local model generation error: {str(e)}")

    async def embed(self, text, options=None) -> Dict[str, Any]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            options: Optional embedding parameters
            
        Returns:
            Dictionary with embedding and metadata
        """
        options = options or {}
        
        try:
            import aiohttp
            
            # Determine if this is Ollama or OpenAI-compatible API
            is_ollama = "ollama" in self.endpoint or self.endpoint.endswith(":11434")
            
            # Prepare text input
            if isinstance(text, list):
                input_texts = text
            else:
                input_texts = [text]
            
            # Prepare request based on API type
            if is_ollama:
                # Prepare Ollama-style request for the first text
                # (Ollama doesn't support batch embeddings)
                request_data = {
                    "model": self.model,
                    "prompt": input_texts[0]
                }
                
                api_url = f"{self.endpoint}/api/embeddings"
            else:
                # Prepare OpenAI-compatible request
                request_data = {
                    "model": self.model,
                    "input": input_texts,
                    "dimensions": options.get("dimensions")
                }
                
                api_url = f"{self.endpoint}/v1/embeddings"
            
            # Generate embeddings
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=request_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP error {response.status}: {error_text}")
                    
                    result = await response.json()
            
            duration = time.time() - start_time
            
            # Extract embeddings based on API type
            if is_ollama:
                embeddings = [result.get("embedding", [])]
                dimensions = len(embeddings[0])
                tokens = len(input_texts[0].split())  # Estimate
            else:
                embeddings = [item["embedding"] for item in result["data"]]
                dimensions = len(embeddings[0])
                tokens = result.get("usage", {}).get("total_tokens", 0)
            
            # Update metrics
            self.metrics["total_embed_requests"] = self.metrics.get("total_embed_requests", 0) + 1
            self.metrics["total_embed_tokens"] = self.metrics.get("total_embed_tokens", 0) + tokens
            self.metrics["average_embed_latency"] = (
                (self.metrics.get("average_embed_latency", 0) * (self.metrics["total_embed_requests"] - 1)) 
                + duration
            ) / self.metrics["total_embed_requests"]
            
            # Update health status
            self._update_health_status(True)
            
            return {
                "embeddings": embeddings[0] if len(embeddings) == 1 else embeddings,
                "model": self.model,
                "dimensions": dimensions,
                "latency": duration,
                "provider": "local"
            }
            
        except Exception as e:
            # Update error metrics
            self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
            self._update_health_status(False)
            
            logger.error(f"Local model embedding error: {str(e)}")
            raise Exception(f"Local model embedding error: {str(e)}")