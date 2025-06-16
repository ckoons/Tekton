#!/usr/bin/env python3
"""
Capability Manager Module

Manages component capabilities and dependencies.
"""

import logging
from typing import Dict, Any, Optional, Callable, Set

from ...logging_integration import LogCategory

logger = logging.getLogger(__name__)


class CapabilityManager:
    """
    Manages component capabilities and dependencies.
    """
    
    def __init__(self, logger):
        """
        Initialize capability manager.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.dependencies = set()
        self.capabilities = {}
        
    def add_dependency(self, dependency_id: str) -> None:
        """
        Add a dependency for the component.
        
        Args:
            dependency_id: Dependency component ID
        """
        self.dependencies.add(dependency_id)
        
    def register_capability(self, 
                         capability_name: str,
                         handler: Callable,
                         level: int = 100,
                         description: str = None) -> None:
        """
        Register a capability for the component.
        
        Args:
            capability_name: Capability name
            handler: Handler function
            level: Capability level (higher is better)
            description: Optional description
        """
        self.capabilities[capability_name] = {
            "handler": handler,
            "level": level,
            "description": description or f"Capability: {capability_name}"
        }
        
        # Log capability registration
        self.logger.info(
            f"Registered capability: {capability_name}",
            category=LogCategory.COMPONENT,
            context={
                "level": level,
                "description": description
            }
        )
        
    def get_capability(self, capability_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a capability by name.
        
        Args:
            capability_name: Capability name
            
        Returns:
            Capability dict or None if not found
        """
        return self.capabilities.get(capability_name)
        
    def get_dependencies(self) -> Set[str]:
        """
        Get all dependencies.
        
        Returns:
            Set of dependency IDs
        """
        return self.dependencies.copy()
