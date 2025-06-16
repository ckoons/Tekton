#!/usr/bin/env python3
"""
Latent Memory Space

Provides classes and functionality for latent space reasoning within Engram.
This module has been refactored into the latent/ directory for better organization.
This file now serves as a compatibility layer for backward compatibility.
"""

from typing import Dict, List, Any, Optional, Union, Tuple

from .latent.states import ThoughtState
from .latent.space import LatentMemorySpace
from .latent.manager import LatentSpaceManager

# Re-export for backward compatibility
__all__ = [
    'ThoughtState',
    'LatentMemorySpace',
    'LatentSpaceManager'
]