"""
Environment setup utilities for agent runner.
"""

import os
import tempfile
import logging
from typing import List, Dict, Any

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent, AgentFile

logger = logging.getLogger(__name__)

def setup_agent_environment(agent: Agent) -> str:
    """
    Set up the agent's execution environment.
    
    Args:
        agent: Agent to set up environment for
        
    Returns:
        Path to the agent's working directory
    """
    # Create temporary directory for agent
    working_dir = tempfile.mkdtemp(prefix=f"ergon_{agent.name}_")
    
    # Get agent files from database
    with get_db_session() as db:
        files = db.query(AgentFile).filter(AgentFile.agent_id == agent.id).all()
        
        # Write files to disk
        for file in files:
            file_path = os.path.join(working_dir, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file.content)
    
    logger.info(f"Set up environment for agent '{agent.name}' in '{working_dir}'")
    return working_dir


def cleanup_agent_environment(working_dir: str) -> None:
    """
    Clean up the agent's execution environment.
    
    Args:
        working_dir: Path to the agent's working directory
    """
    if os.path.exists(working_dir):
        import shutil
        shutil.rmtree(working_dir)
        logger.info(f"Removed working directory: {working_dir}")
    else:
        logger.warning(f"Working directory doesn't exist: {working_dir}")