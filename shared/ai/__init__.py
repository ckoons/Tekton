"""
Shared CI libraries for Tekton platform-wide CI integration.

This package provides:
- simple_ai: Simple CI communication interface
- CISpecialistWorker: Base class for CI specialists
"""

from .specialist_worker import CISpecialistWorker

__all__ = ['CISpecialistWorker']