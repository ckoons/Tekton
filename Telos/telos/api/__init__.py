"""
Telos API for requirements management.

This module provides a REST API and WebSocket interface for managing requirements,
tracing, and validation with support for the Single Port Architecture pattern.
"""

from .app import app

__all__ = ['app']