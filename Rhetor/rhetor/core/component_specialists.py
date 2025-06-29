"""
Component Specialists - DEPRECATED

This module has been replaced by the unified AI Registry system.
All AI specialist management is now handled through:
- shared/ai/registry_client.py
- shared/ai/ai_discovery_service.py

This file is kept as a stub to prevent import errors during migration.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ComponentSpecialistRegistry:
    """DEPRECATED - Stub class for backward compatibility during migration."""
    
    def __init__(self, *args, **kwargs):
        logger.warning("ComponentSpecialistRegistry is deprecated. Use AI Registry instead.")
    
    async def ensure_specialist(self, component: str) -> Optional[object]:
        """DEPRECATED - Use AI Registry instead."""
        logger.warning("ComponentSpecialistRegistry.ensure_specialist() is deprecated")
        return None