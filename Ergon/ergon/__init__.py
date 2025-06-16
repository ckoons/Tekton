"""
Ergon: A streamlined AI agent builder with minimal configuration.
"""

__version__ = "0.1.0"
__author__ = "AI Agent Team"

from pathlib import Path

from .utils.config.settings import settings
# Define package root
from .core.database.engine import get_db_session
ROOT_DIR = Path(__file__).parent.absolute()
from .core.database.models import Agent

from .core.database.engine import init_db
from .core.llm.client import LLMClient
from .core.database.models import AgentTool
from .core.database.models import AgentExecution
from .core.memory.service import MemoryService
from .core.database.models import DocumentationPage
from .core.database.models import AgentMessage