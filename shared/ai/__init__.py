"""
Shared AI libraries for Tekton platform-wide AI integration.

This package provides:
- simple_ai: Simple AI communication interface
- CISpecialistWorker: Base class for CI specialists
"""

from .specialist_worker import CISpecialistWorker

__all__ = ['CISpecialistWorker']