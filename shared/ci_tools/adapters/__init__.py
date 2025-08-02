"""
CI Tool Adapters
Specific implementations for each CI tool.
"""

from .claude_code import ClaudeCodeAdapter
from .generic_adapter import GenericAdapter

__all__ = ['ClaudeCodeAdapter', 'GenericAdapter']