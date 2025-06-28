"""
Shared AI libraries for Tekton platform-wide AI integration.

This package provides:
- AIRegistryClient: Platform-wide AI socket registry client
- AISpecialistWorker: Base class for AI specialists
- AIHealthMonitor: AI-specific health monitoring
"""

from .registry_client import AIRegistryClient
from .specialist_worker import AISpecialistWorker
from .health_monitor import AIHealthMonitor

__all__ = ['AIRegistryClient', 'AISpecialistWorker', 'AIHealthMonitor']