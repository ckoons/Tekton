"""
Agent runner for executing AI agents.

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import os
import sys
import json
import importlib.util
import tempfile
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import logging
import asyncio

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent, AgentExecution, AgentMessage, AgentTool
from ergon.core.llm.client import LLMClient
from ergon.utils.config.settings import settings

# Import from refactored structure
from ergon.core.agents.runner.base.runner import AgentRunner
from ergon.core.agents.runner.base.exceptions import AgentException

# Import memory service if available
HAS_MEMORY = False
try:
    from ergon.core.memory.service import MemoryService
    HAS_MEMORY = True
except ImportError:
    HAS_MEMORY = False

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))

# Re-export for backward compatibility
__all__ = ["AgentRunner", "AgentException"]