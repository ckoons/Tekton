"""
Tekton Landmark System
A persistent memory layer for Companion Intelligences
"""

from .core.landmark import Landmark
from .core.decorators import (
    landmark,
    architecture_decision,
    performance_boundary,
    api_contract,
    danger_zone,
    integration_point,
    state_checkpoint
)
from .core.registry import LandmarkRegistry

__all__ = [
    'Landmark',
    'LandmarkRegistry',
    'landmark',
    'architecture_decision',
    'performance_boundary',
    'api_contract',
    'danger_zone',
    'integration_point',
    'state_checkpoint'
]

__version__ = '0.1.0'