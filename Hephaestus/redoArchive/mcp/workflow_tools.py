"""
UI Workflow Tools - Smart composite operations that eliminate confusion
Created after experiencing the pain of area vs component confusion!

Version 2 improvements based on real testing feedback
"""
# Import the improved v2 implementation
from .workflow_tools_v2 import ui_workflow_v2 as ui_workflow, WorkflowType

# Re-export for backward compatibility
__all__ = ['ui_workflow', 'WorkflowType']