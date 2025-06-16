#!/usr/bin/env python3
"""
Component Registry Monitoring Module

This module provides functions for monitoring component health and recovery.
"""

import time
import logging
from typing import Dict, List, Any

from ...lifecycle import ComponentState

logger = logging.getLogger("tekton.component_lifecycle.registry.monitoring")


async def check_for_automatic_recovery(components: Dict[str, Any], instances: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Check for components that should be automatically recovered.
    
    Args:
        components: Component registrations
        instances: Component instances
        
    Returns:
        List of component IDs that are candidates for recovery
    """
    recovery_candidates = []
    
    for component_id, component in components.items():
        # Check if component is in recoverable state
        if ComponentState.is_degraded(component.state):
            # Check if it's been degraded long enough to try recovery
            degradation_time = instances[component_id].get("metadata", {}).get("degradation_time", 0)
            if degradation_time > 0 and time.time() - degradation_time > 30:  # 30 seconds in degraded state
                # Check if recoverable
                if component.recovery_attempts < 3:  # Limit attempts
                    recovery_candidates.append(component_id)
    
    return recovery_candidates