#!/usr/bin/env python3
"""
Model Manager Module

This module provides a manager for multiple model adapters with intelligent routing
and fallback capabilities.
"""

import os
from shared.env import TektonEnviron
import time
import logging
from typing import Dict, List, Any, Optional, Union

from .adapters.base import ModelAdapter
from .adapters.anthropic import AnthropicAdapter
from .adapters.openai import OpenAIAdapter
from .adapters.local import LocalModelAdapter
from .routing import select_model_for_task

# Configure logger
logger = logging.getLogger("tekton.models.manager")


class ModelManager:
    """Manager for multiple model adapters with automatic routing."""

    def __init__(self):
        """Initialize the model manager."""
        self.adapters = {}
        self.default_adapter = None
        self.metrics = {}
        self.model_capabilities = {}
        
    async def register_adapter(self, name: str, adapter_class: type, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a model adapter.
        
        Args:
            name: Name to use for this adapter
            adapter_class: Adapter class
            config: Optional configuration dictionary
            
        Returns:
            True if registration was successful
        """
        try:
            # Create and initialize adapter
            adapter = adapter_class(config)
            initialized = await adapter.initialize()
            
            if initialized:
                # Store adapter
                self.adapters[name] = adapter
                
                # Set as default if first adapter
                if not self.default_adapter:
                    self.default_adapter = name
                    
                # Store capabilities
                self.model_capabilities[name] = adapter.get_capabilities()
                
                logger.info(f"Registered model adapter: {name}")
                return True
            else:
                logger.warning(f"Failed to initialize model adapter: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering model adapter {name}: {e}")
            return False
            
    async def generate(self, prompt: Union[str, List], adapter_name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response using the specified adapter.
        
        Args:
            prompt: The prompt to send to the model
            adapter_name: Optional adapter name (uses default if not specified)
            options: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        options = options or {}
        adapter_name = adapter_name or self.default_adapter
        
        if not adapter_name or adapter_name not in self.adapters:
            raise ValueError(f"Unknown adapter: {adapter_name}")
            
        adapter = self.adapters[adapter_name]
        
        try:
            # Record start time for metrics
            start_time = time.time()
            
            # Generate response
            result = await adapter.generate(prompt, options)
            
            # Record completion time for metrics
            duration = time.time() - start_time
            
            # Update metrics
            self.metrics["total_requests"] = self.metrics.get("total_requests", 0) + 1
            self.metrics["total_tokens"] = self.metrics.get("total_tokens", 0) + result.get("tokens", 0)
            self.metrics["average_latency"] = (
                (self.metrics.get("average_latency", 0) * (self.metrics["total_requests"] - 1)) 
                + duration
            ) / self.metrics["total_requests"]
            
            # Add adapter metrics by name
            adapter_metrics = self.metrics.setdefault(adapter_name, {})
            adapter_metrics["requests"] = adapter_metrics.get("requests", 0) + 1
            adapter_metrics["tokens"] = adapter_metrics.get("tokens", 0) + result.get("tokens", 0)
            
            return result
            
        except Exception as e:
            # Update error metrics
            self.metrics["error_count"] = self.metrics.get("error_count", 0) + 1
            
            # Try fallback if specified and available
            fallback = options.get("fallback")
            if fallback and fallback in self.adapters and fallback != adapter_name:
                logger.warning(f"Falling back to {fallback} after {adapter_name} error: {e}")
                
                # Update fallback metrics
                self.metrics["fallback_count"] = self.metrics.get("fallback_count", 0) + 1
                
                # Create new options without fallback to prevent infinite recursion
                fallback_options = options.copy()
                fallback_options.pop("fallback", None)
                
                # Try fallback adapter
                try:
                    return await self.generate(prompt, fallback, fallback_options)
                except Exception as fallback_error:
                    logger.error(f"Fallback to {fallback} also failed: {fallback_error}")
                    raise Exception(f"Both primary ({adapter_name}) and fallback ({fallback}) failed: {e}")
            
            # No fallback or fallback failed
            raise
            
    async def embed(self, text: Union[str, List[str]], adapter_name: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate embeddings using the specified adapter.
        
        Args:
            text: Text to embed
            adapter_name: Optional adapter name (uses default if not specified)
            options: Optional embedding parameters
            
        Returns:
            Dictionary with embedding and metadata
        """
        options = options or {}
        adapter_name = adapter_name or self.default_adapter
        
        if not adapter_name or adapter_name not in self.adapters:
            raise ValueError(f"Unknown adapter: {adapter_name}")
            
        adapter = self.adapters[adapter_name]
        
        try:
            # Check if adapter supports embeddings
            if not self.model_capabilities.get(adapter_name, {}).get("supports_embeddings", False):
                raise NotImplementedError(f"Adapter {adapter_name} does not support embeddings")
            
            # Record start time for metrics
            start_time = time.time()
            
            # Generate embeddings
            result = await adapter.embed(text, options)
            
            # Record completion time for metrics
            duration = time.time() - start_time
            
            # Update metrics
            self.metrics["total_embed_requests"] = self.metrics.get("total_embed_requests", 0) + 1
            self.metrics["average_embed_latency"] = (
                (self.metrics.get("average_embed_latency", 0) * (self.metrics["total_embed_requests"] - 1)) 
                + duration
            ) / self.metrics["total_embed_requests"]
            
            # Add adapter metrics by name
            adapter_metrics = self.metrics.setdefault(adapter_name, {})
            adapter_metrics["embed_requests"] = adapter_metrics.get("embed_requests", 0) + 1
            
            return result
            
        except Exception as e:
            # Update error metrics
            self.metrics["embed_error_count"] = self.metrics.get("embed_error_count", 0) + 1
            
            # Try fallback if specified and available
            fallback = options.get("fallback")
            if fallback and fallback in self.adapters and fallback != adapter_name:
                logger.warning(f"Falling back to {fallback} for embeddings after {adapter_name} error: {e}")
                
                # Update fallback metrics
                self.metrics["embed_fallback_count"] = self.metrics.get("embed_fallback_count", 0) + 1
                
                # Create new options without fallback to prevent infinite recursion
                fallback_options = options.copy()
                fallback_options.pop("fallback", None)
                
                # Try fallback adapter
                try:
                    return await self.embed(text, fallback, fallback_options)
                except Exception as fallback_error:
                    logger.error(f"Fallback to {fallback} for embeddings also failed: {fallback_error}")
                    raise Exception(f"Both primary ({adapter_name}) and fallback ({fallback}) failed for embeddings: {e}")
            
            # No fallback or fallback failed
            raise
            
    async def smart_route(self, prompt: Union[str, List], task_type: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route the request to the most appropriate model based on task.
        
        Args:
            prompt: Prompt to send to the model
            task_type: Type of task (code, creative, analytical, etc.)
            options: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        options = options or {}
        
        # Get available adapters
        available_adapters = []
        for name, adapter in self.adapters.items():
            if adapter.get_health_status() != "unhealthy":
                available_adapters.append(name)
        
        if not available_adapters:
            raise ValueError("No healthy adapters available")
        
        # Select the best adapter for the task
        best_adapter = select_model_for_task(
            task_type, 
            available_adapters, 
            self.model_capabilities
        )
        
        # Use the first available adapter if no match
        if not best_adapter:
            best_adapter = available_adapters[0]
        
        # Select fallback adapter
        fallback_adapter = None
        for name in available_adapters:
            if name != best_adapter:
                fallback_adapter = name
                break
        
        # Add fallback to options if available
        if fallback_adapter:
            options["fallback"] = fallback_adapter
        
        # Generate using the selected adapter
        result = await self.generate(prompt, best_adapter, options)
        
        # Add routing info
        result["routing"] = {
            "task_type": task_type,
            "selected_adapter": best_adapter,
            "fallback_adapter": fallback_adapter
        }
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get usage metrics for all adapters.
        
        Returns:
            Dictionary of metrics
        """
        metrics = self.metrics.copy()
        
        # Add adapter-specific metrics
        for name, adapter in self.adapters.items():
            if name in metrics:
                metrics[name].update(adapter.get_metrics())
            else:
                metrics[name] = adapter.get_metrics()
                
        return metrics
    
    def get_adapter_health(self) -> Dict[str, str]:
        """
        Get health status for all adapters.
        
        Returns:
            Dictionary mapping adapter names to health status
        """
        return {
            name: adapter.get_health_status()
            for name, adapter in self.adapters.items()
        }
    
    def get_adapter_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """
        Get capabilities for all adapters.
        
        Returns:
            Dictionary mapping adapter names to capabilities
        """
        return self.model_capabilities


# Singleton instance
_model_manager = None

def get_model_manager() -> ModelManager:
    """
    Get the model manager singleton.
    
    Returns:
        ModelManager instance
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


# Helper function to initialize adapters from environment variables
async def initialize_from_env() -> ModelManager:
    """
    Initialize model adapters from environment variables.
    
    Returns:
        ModelManager instance
    """
    manager = get_model_manager()
    
    # Check for Anthropic API key
    anthropic_api_key = TektonEnviron.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        await manager.register_adapter(
            "anthropic_claude",
            AnthropicAdapter,
            {
                "api_key": anthropic_api_key,
                "model": TektonEnviron.get("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            }
        )
    
    # Check for OpenAI API key
    openai_api_key = TektonEnviron.get("OPENAI_API_KEY")
    if openai_api_key:
        await manager.register_adapter(
            "openai_gpt4",
            OpenAIAdapter,
            {
                "api_key": openai_api_key,
                "model": TektonEnviron.get("OPENAI_MODEL", "gpt-4o")
            }
        )
    
    # Check for local model endpoint
    local_endpoint = TektonEnviron.get("LOCAL_MODEL_ENDPOINT")
    if local_endpoint:
        await manager.register_adapter(
            "local_model",
            LocalModelAdapter,
            {
                "endpoint": local_endpoint,
                "model": TektonEnviron.get("LOCAL_MODEL", "llama3")
            }
        )
    
    return manager