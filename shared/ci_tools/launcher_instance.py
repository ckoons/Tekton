"""
Global tool launcher instance.
This module ensures we have a single global instance.
"""

_launcher = None

def get_launcher():
    """Get the global launcher instance."""
    global _launcher
    if _launcher is None:
        from .tool_launcher import ToolLauncher
        _launcher = ToolLauncher()
    return _launcher