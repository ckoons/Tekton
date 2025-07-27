"""
Shared workflow handler for Tekton components.

This module provides the WorkflowHandler base class that all components
can use to implement the standard /workflow endpoint.
"""

from .workflow_handler import WorkflowHandler, WorkflowMessage

__all__ = ['WorkflowHandler', 'WorkflowMessage']