"""
Specialist Router - DEPRECATED

This module has been replaced by the unified AI Registry system.
Routing is now handled through:
- shared/ai/ai_discovery_service.py (find_best_ai method)
- AI Registry role-based discovery

This file is kept as a stub to prevent import errors during migration.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SpecialistRouter:
    """DEPRECATED - Stub class for backward compatibility during migration."""
    
    def __init__(self, *args, **kwargs):
        logger.warning("SpecialistRouter is deprecated. Use AI Registry discovery instead.")
        self._specialist_manager = None
    
    def set_specialist_manager(self, manager):
        """DEPRECATED - No longer needed."""
        self._specialist_manager = manager
    
    async def route_to_specialist(self, *args, **kwargs):
        """DEPRECATED - Use AI Registry discovery instead."""
        logger.warning("SpecialistRouter.route_to_specialist() is deprecated")
        return None