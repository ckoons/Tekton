"""
Shared AI libraries for Tekton platform-wide AI integration.

This package provides:
- simple_ai: Simple AI communication interface
- AISpecialistWorker: Base class for AI specialists
- AIHealthMonitor: AI-specific health monitoring
"""

from .specialist_worker import AISpecialistWorker
from .health_monitor import AIHealthMonitor

__all__ = ['AISpecialistWorker', 'AIHealthMonitor']