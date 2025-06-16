"""
MCP (Model Context Protocol) integration for Metis.

This module provides FastMCP tools for task management operations.
"""

from .tools import *
from .capabilities import *

__all__ = [
    'task_management_tools',
    'dependency_management_tools', 
    'analytics_tools',
    'MetisTaskManager'
]