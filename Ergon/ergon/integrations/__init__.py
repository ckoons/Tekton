"""
Ergon Integrations Module.

Handles integration with external Tekton components.
"""

from .tekton_core import (
    monitor_completed_projects,
    extract_sprint_metadata,
    prepare_registry_entry,
    TektonCoreMonitor
)

__all__ = [
    'monitor_completed_projects',
    'extract_sprint_metadata',
    'prepare_registry_entry',
    'TektonCoreMonitor'
]