"""
Logging utilities for agent runner.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ergon.utils.config.settings import settings

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))

def log_agent_start(agent_name: str, agent_id: int, timeout: Optional[int] = None) -> None:
    """
    Log agent execution start.
    
    Args:
        agent_name: Name of the agent
        agent_id: ID of the agent
        timeout: Optional timeout in seconds
    """
    if timeout:
        logger.info(f"Running agent '{agent_name}' (ID: {agent_id}) with {timeout}s timeout")
    else:
        logger.info(f"Running agent '{agent_name}' (ID: {agent_id})")


def log_agent_success(agent_name: str, agent_id: int, elapsed_time: float) -> None:
    """
    Log agent execution success.
    
    Args:
        agent_name: Name of the agent
        agent_id: ID of the agent
        elapsed_time: Execution time in seconds
    """
    logger.info(f"Agent '{agent_name}' (ID: {agent_id}) completed successfully in {elapsed_time:.2f} seconds")


def log_agent_error(agent_name: str, agent_id: int, error: str, elapsed_time: float) -> None:
    """
    Log agent execution error.
    
    Args:
        agent_name: Name of the agent
        agent_id: ID of the agent
        error: Error message
        elapsed_time: Execution time in seconds
    """
    logger.error(f"Error in agent '{agent_name}' (ID: {agent_id}) after {elapsed_time:.2f} seconds: {error}")


def log_agent_timeout(agent_name: str, agent_id: int, timeout: int, elapsed_time: float) -> None:
    """
    Log agent execution timeout.
    
    Args:
        agent_name: Name of the agent
        agent_id: ID of the agent
        timeout: Timeout in seconds
        elapsed_time: Execution time in seconds
    """
    logger.warning(f"Agent '{agent_name}' (ID: {agent_id}) execution timed out after {elapsed_time:.2f} seconds (timeout: {timeout}s)")


def format_timeout_message(agent_name: str, timeout: int, elapsed_time: float, action: str) -> str:
    """
    Format timeout message based on action.
    
    Args:
        agent_name: Name of the agent
        timeout: Timeout in seconds
        elapsed_time: Execution time in seconds
        action: Timeout action ('log', 'alarm', or 'kill')
        
    Returns:
        Formatted timeout message
    """
    error_msg = f"Agent '{agent_name}' execution timed out after {elapsed_time:.2f} seconds (timeout: {timeout}s)"
    
    if action == "alarm":
        return f"⚠️ TIMEOUT ALARM: {error_msg}"
    elif action == "kill":
        return f"❌ EXECUTION TERMINATED: {error_msg}"
    else:  # "log"
        return f"I wasn't able to complete the task in the allowed time. {error_msg}"