#!/usr/bin/env python3
"""
Base Model Adapter Module

This module provides the base class for all model adapters and defines
common capabilities and health status.
"""

import time
import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union

# Configure logger
logger = logging.getLogger("tekton.models.adapters.base")


class ModelCapability(Enum):
    """Enum for model capabilities."""
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    VISION = "vision"
    EMBEDDINGS = "embeddings"
    FUNCTION_CALLING = "function_calling"


class AdapterHealthStatus(Enum):
    """Enum for adapter health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ModelAdapter:
    """Base class for external model adapters."""

    def __init__(self, config=None):
        """
        Initialize the model adapter.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics = {}
        self.health_status = AdapterHealthStatus.UNKNOWN.value
        self.last_failure_time = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.backoff_factor = 1.5
        self.initial_retry_delay = 1.0  # seconds
        self.max_retry_delay = 60.0  # seconds
        
    async def initialize(self) -> bool:
        """
        Initialize the model adapter.
        
        Returns:
            True if initialization was successful
        """
        raise NotImplementedError("Subclasses must implement initialize")

    async def generate(self, prompt, options=None) -> Dict[str, Any]:
        """
        Generate a response from the model.
        
        Args:
            prompt: The prompt to send to the model
            options: Optional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        raise NotImplementedError("Subclasses must implement generate")

    async def embed(self, text, options=None) -> Dict[str, Any]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            options: Optional embedding parameters
            
        Returns:
            Dictionary with embedding and metadata
        """
        raise NotImplementedError("Subclasses must implement embed")
        
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get usage metrics for this adapter.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics
        
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get capabilities of this model adapter.
        
        Returns:
            Dictionary of capabilities
        """
        return {
            "max_tokens": self.config.get("max_tokens", 4096),
            "supports_streaming": self.config.get("supports_streaming", False),
            "supports_json_mode": self.config.get("supports_json_mode", False),
            "supports_vision": self.config.get("supports_vision", False),
            "supports_embeddings": self.config.get("supports_embeddings", False),
            "supports_function_calling": self.config.get("supports_function_calling", False),
            "context_window": self.config.get("context_window", 4096)
        }
        
    def get_health_status(self) -> str:
        """
        Get health status of this model adapter.
        
        Returns:
            Status string: "healthy", "degraded", or "unhealthy"
        """
        return self.health_status
        
    def _update_health_status(self, success: bool):
        """
        Update health status based on request success.
        
        Args:
            success: Whether the request was successful
        """
        if success:
            # Reset consecutive failures
            self.consecutive_failures = 0
            self.health_status = AdapterHealthStatus.HEALTHY.value
        else:
            # Increment consecutive failures
            self.consecutive_failures += 1
            self.last_failure_time = time.time()
            
            # Update health status
            if self.consecutive_failures >= self.max_consecutive_failures:
                self.health_status = AdapterHealthStatus.UNHEALTHY.value
            elif self.consecutive_failures > 0:
                self.health_status = AdapterHealthStatus.DEGRADED.value
                
    async def _handle_rate_limit(self, retry_attempt: int) -> None:
        """
        Handle rate limiting with exponential backoff.
        
        Args:
            retry_attempt: Current retry attempt number
        """
        delay = min(
            self.initial_retry_delay * (self.backoff_factor ** retry_attempt),
            self.max_retry_delay
        )
        
        logger.warning(f"Rate limited, retrying after {delay:.1f}s (attempt {retry_attempt+1})")
        await asyncio.sleep(delay)