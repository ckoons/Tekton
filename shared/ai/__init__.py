"""
Shared AI libraries for Tekton platform-wide AI integration.

This package provides:
- simple_ai: Simple AI communication interface
- AISpecialistWorker: Base class for AI specialists
"""

from .specialist_worker import AISpecialistWorker

__all__ = ['AISpecialistWorker']