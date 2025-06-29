"""
Socket Specialist Integration - DEPRECATED

This module has been replaced by the unified AI Registry system.
Socket management is now handled directly by AI specialists through the registry.

This file is kept as a stub to prevent import errors during migration.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SocketSpecialistIntegration:
    """DEPRECATED - Stub class for backward compatibility during migration."""
    
    def __init__(self, *args, **kwargs):
        logger.warning("SocketSpecialistIntegration is deprecated. Use AI Registry instead.")
    
    async def on_specialist_created(self, specialist_id: str):
        """DEPRECATED - No longer needed."""
        pass


async def get_socket_specialist_integration(*args, **kwargs) -> SocketSpecialistIntegration:
    """DEPRECATED - Return stub instance."""
    logger.warning("get_socket_specialist_integration() is deprecated")
    return SocketSpecialistIntegration()