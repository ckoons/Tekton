"""
Integration module for Noesis
Handles integration with other Tekton components
"""

from .sophia_bridge import SophiaBridge, TheoryExperimentProtocol, CollaborationProtocol

__all__ = [
    'SophiaBridge',
    'TheoryExperimentProtocol',
    'CollaborationProtocol'
]