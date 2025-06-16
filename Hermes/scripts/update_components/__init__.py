"""
Update components package for Hermes.

This package provides functionality for updating Tekton components
to use Hermes centralized services like the Centralized Logging System.
"""

from .core.args import parse_args, determine_components, determine_tekton_root
from .core.manager import UpdateManager

__all__ = [
    'parse_args',
    'determine_components',
    'determine_tekton_root',
    'UpdateManager'
]