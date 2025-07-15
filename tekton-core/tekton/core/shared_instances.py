"""
Shared instances for TektonCore components.

This module provides singleton instances to ensure consistency across
the application without circular imports.
"""

from tekton.core.project_manager_v2 import ProjectManager

# Singleton project manager instance
_project_manager_v2 = None

def get_project_manager():
    """Get the shared ProjectManager V2 instance"""
    global _project_manager_v2
    if _project_manager_v2 is None:
        _project_manager_v2 = ProjectManager()
    return _project_manager_v2