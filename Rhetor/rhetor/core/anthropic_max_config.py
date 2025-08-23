"""
Anthropic Max Configuration Handler for Rhetor.

This module handles configuration for Anthropic Max accounts,
enabling unlimited token usage for testing and development.
"""

import os
from shared.env import TektonEnviron
import logging
from typing import Dict, Any, Optional

# Standard logging - removed debug_log import

logger = logging.getLogger(__name__)

class AnthropicMaxConfig:
    """
    Manages Anthropic Max account configuration.
    
    When enabled, this allows:
    - Unlimited token usage for testing
    - Premium model access (Opus by default)
    - No budget constraints
    - Enhanced rate limits
    """
    
    def __init__(self):
        """Initialize Anthropic Max configuration."""
        self._enabled = False
        self._check_environment()
        
    def _check_environment(self):
        """Check environment for Anthropic Max configuration."""
        # Check environment variable
        max_env = TektonEnviron.get("ANTHROPIC_MAX_ACCOUNT", "false").lower()
        self._enabled = max_env in ["true", "1", "yes", "on"]
        
        if self._enabled:
            logger.info("Anthropic Max account detected - unlimited tokens enabled")
        else:
            logger.info("Standard Anthropic account - budget limits apply")
            
    @property
    def enabled(self) -> bool:
        """Check if Anthropic Max is enabled."""
        return self._enabled
        
    def enable(self):
        """Enable Anthropic Max mode."""
        self._enabled = True
        TektonEnviron.set("ANTHROPIC_MAX_ACCOUNT", "true")
        logger.info("Anthropic Max enabled via API")
        
    def disable(self):
        """Disable Anthropic Max mode."""
        self._enabled = False
        TektonEnviron.set("ANTHROPIC_MAX_ACCOUNT", "false")
        logger.info("Anthropic Max disabled via API")
        
    def get_model_override(self, requested_model: str) -> str:
        """
        Get model override for Anthropic Max accounts.
        
        Args:
            requested_model: Originally requested model
            
        Returns:
            Model to use (may be upgraded for Max accounts)
        """
        if not self._enabled:
            return requested_model
            
        # Upgrade to premium models when Max is enabled
        model_upgrades = {
            "claude-3-haiku-20240307": "claude-3-sonnet-20240229",
            "claude-3-sonnet-20240229": "claude-3-opus-20240229",
            "claude-2.1": "claude-3-opus-20240229",
            "claude-2.0": "claude-3-opus-20240229",
            "claude-instant-1.2": "claude-3-sonnet-20240229"
        }
        
        return model_upgrades.get(requested_model, requested_model)
        
    def get_budget_override(self) -> Optional[Dict[str, Any]]:
        """
        Get budget override for Anthropic Max accounts.
        
        Returns:
            Budget configuration or None
        """
        if not self._enabled:
            return None
            
        # Return unlimited budget configuration
        return {
            "total_budget": float('inf'),
            "daily_limit": float('inf'),
            "hourly_limit": float('inf'),
            "enforce_limits": False,
            "track_usage": True,  # Still track for metrics
            "alert_threshold": 1.0  # No alerts
        }
        
    def get_rate_limit_override(self) -> Optional[Dict[str, Any]]:
        """
        Get rate limit override for Anthropic Max accounts.
        
        Returns:
            Rate limit configuration or None
        """
        if not self._enabled:
            return None
            
        # Enhanced rate limits for Max accounts
        return {
            "requests_per_minute": 1000,
            "tokens_per_minute": 1000000,
            "concurrent_requests": 100
        }
        
    def get_specialist_config_override(self, specialist_type: str) -> Dict[str, Any]:
        """
        Get specialist configuration override for Max accounts.
        
        Args:
            specialist_type: Type of AI specialist
            
        Returns:
            Configuration overrides
        """
        if not self._enabled:
            return {}
            
        # Use premium models for all specialists in Max mode
        return {
            "model": "claude-3-opus-20240229" if "orchestrator" in specialist_type else "claude-3-sonnet-20240229",
            "max_tokens": 8000,  # Higher token limits
            "temperature": 0.7,
            "enable_streaming": True
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enabled": self._enabled,
            "model_upgrades_active": self._enabled,
            "budget_limits_removed": self._enabled,
            "enhanced_rate_limits": self._enabled,
            "environment_variable": TektonEnviron.get("ANTHROPIC_MAX_ACCOUNT", "false")
        }