"""
Shared instances for TektonCore components.

This module provides singleton instances to ensure consistency across
the application without circular imports.
"""

from tekton.core.project_manager import ProjectManager

# Singleton project manager instance
_project_manager = None

def get_project_manager():
    """Get the shared ProjectManager instance"""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager