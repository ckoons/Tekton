"""
Ergon Sandbox Module.

Provides isolated testing environments for Registry solutions.
Supports multiple providers (sandbox-exec, Docker, etc.) through
a pluggable architecture.
"""

from .runner import SandboxRunner
from .factory import SandboxFactory
from .base import SandboxProvider, SandboxResult

__all__ = [
    'SandboxRunner',
    'SandboxFactory', 
    'SandboxProvider',
    'SandboxResult'
]