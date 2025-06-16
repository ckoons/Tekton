"""
AI-driven tool generator.

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import asyncio
from typing import Dict, List, Any, Optional

# Import the main ToolGenerator class
from ergon.core.repository.generators.base import ToolGenerator

# Import the convenience function
from ergon.core.repository.generators.base import generate_tool

# Re-export the main class and function
__all__ = ["ToolGenerator", "generate_tool"]