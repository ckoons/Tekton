"""
Tekton Core Package

This package provides core functionality for the Tekton orchestration system,
including shared models, utilities, and base classes.
"""

# Import models for easy access
from . import models

__version__ = "0.1.0"

__all__ = [
    "models",
]