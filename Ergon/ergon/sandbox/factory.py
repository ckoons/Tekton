"""
Sandbox factory for selecting appropriate providers.

Intelligently chooses between sandbox-exec, Docker, or other providers
based on system capabilities and solution requirements.
"""

import platform
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base import SandboxProvider
from .providers.sandbox_exec import SandboxExecProvider
from .providers.docker import DockerProvider

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        performance_boundary,
        integration_point
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Provider Selection Strategy",
    description="Smart factory pattern for choosing optimal sandbox provider",
    rationale="Different solutions need different isolation levels. Start lightweight with sandbox-exec, escalate to Docker when needed.",
    alternatives_considered=["Always Docker", "Always sandbox-exec", "Manual selection"],
    impacts=["performance", "resource_usage", "compatibility"],
    decided_by="Casey, Ani",
    decision_date="2025-08-22"
)
class SandboxFactory:
    """
    Factory for creating appropriate sandbox providers.
    
    Selects provider based on:
    - System capabilities (macOS, Linux, Docker availability)
    - Solution requirements (network, GPU, persistence)
    - User preferences (force specific provider)
    """
    
    def __init__(self):
        self._providers = {}
        self._default_provider = None
        self._register_providers()
    
    def _register_providers(self):
        """Register available providers"""
        
        # Register sandbox-exec for macOS
        if platform.system() == "Darwin":
            provider = SandboxExecProvider()
            self._providers["sandbox-exec"] = provider
            self._default_provider = provider
            logger.info("Registered sandbox-exec provider (macOS)")
        
        # Register Docker if available
        docker = DockerProvider()
        self._providers["docker"] = docker
        logger.info("Registered Docker provider")
        
        # Set Docker as default if no other default
        if not self._default_provider:
            self._default_provider = docker
    
    @performance_boundary(
        title="Provider Selection",
        description="Choose optimal sandbox provider for solution",
        sla="<100ms decision time",
        optimization_notes="Cache provider availability checks"
    )
    async def get_provider(
        self, 
        solution_requirements: Dict[str, Any],
        user_preference: Optional[str] = None
    ) -> SandboxProvider:
        """
        Get the best provider for given requirements.
        
        Args:
            solution_requirements: Dict with keys like:
                - needs_network: bool
                - needs_gpu: bool  
                - needs_persistence: bool
                - max_memory: str (e.g., "4G")
                - platform: str (e.g., "linux", "darwin", "any")
            user_preference: Force specific provider ("sandbox-exec", "docker")
            
        Returns:
            SandboxProvider instance ready to use
        """
        
        # Honor user preference if valid
        if user_preference and user_preference in self._providers:
            provider = self._providers[user_preference]
            if await provider.is_available():
                logger.info(f"Using user-preferred provider: {user_preference}")
                return provider
            else:
                logger.warning(f"Preferred provider {user_preference} not available")
        
        # Check requirements and capabilities
        needs_gpu = solution_requirements.get("needs_gpu", False)
        needs_persistence = solution_requirements.get("needs_persistence", False)
        platform_req = solution_requirements.get("platform", "any")
        
        # Decision logic
        if platform.system() == "Darwin" and not needs_gpu and not needs_persistence:
            # Prefer lightweight sandbox-exec on macOS for simple cases
            if "sandbox-exec" in self._providers:
                provider = self._providers["sandbox-exec"]
                if await provider.is_available():
                    logger.info("Selected sandbox-exec for lightweight macOS isolation")
                    return provider
        
        # Fall back to Docker for complex requirements
        if "docker" in self._providers:
            provider = self._providers["docker"]
            if await provider.is_available():
                logger.info("Selected Docker for full isolation")
                return provider
        
        # Use default if nothing else works
        if self._default_provider and await self._default_provider.is_available():
            logger.info(f"Using default provider: {self._default_provider.get_name()}")
            return self._default_provider
        
        # No provider available
        raise RuntimeError("No sandbox provider available on this system")
    
    async def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered providers and their status.
        
        Returns:
            Dict mapping provider name to info dict
        """
        result = {}
        
        for name, provider in self._providers.items():
            result[name] = {
                "available": await provider.is_available(),
                "capabilities": provider.get_capabilities(),
                "is_default": provider == self._default_provider
            }
        
        return result
    
    @integration_point(
        title="Provider Health Check",
        description="Verify all providers are functional",
        target_component="sandbox-providers",
        protocol="health-check",
        systems=["sandbox-exec", "Docker"],
        data_flow="Check each provider's availability and report status"
    )
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all providers.
        
        Returns:
            Dict mapping provider name to availability
        """
        health = {}
        
        for name, provider in self._providers.items():
            try:
                health[name] = await provider.is_available()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                health[name] = False
        
        return health