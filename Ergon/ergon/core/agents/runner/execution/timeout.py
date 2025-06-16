"""
Timeout handling for agent runner.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable

from ..utils.logging import log_agent_timeout, format_timeout_message
from ..base.exceptions import AgentTimeoutException

# Configure logger
logger = logging.getLogger(__name__)

async def run_with_timeout(
    agent_func: Callable[[str], Awaitable[str]],
    input_text: str,
    agent_name: str,
    agent_id: int,
    timeout: int,
    timeout_action: str = "log",
    execution_id: Optional[int] = None,
    on_timeout: Optional[Callable[[int, str, float], None]] = None
) -> str:
    """
    Run a function with a timeout.
    
    Args:
        agent_func: Async function to run with timeout
        input_text: Input to pass to the function
        agent_name: Name of the agent (for logging)
        agent_id: ID of the agent
        timeout: Timeout in seconds
        timeout_action: Action to take on timeout ('log', 'alarm', or 'kill')
        execution_id: Optional execution ID for database recording
        on_timeout: Optional callback function to call on timeout
        
    Returns:
        Function result or timeout message
        
    Raises:
        asyncio.TimeoutError: If the execution exceeds the timeout and on_timeout is None
    """
    start_time = datetime.now()
    
    # Create a task for running the function
    task = asyncio.create_task(agent_func(input_text))
    
    try:
        # Wait for the task to complete or timeout
        response = await asyncio.wait_for(task, timeout=timeout)
        
        # Calculate elapsed time
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Agent '{agent_name}' (ID: {agent_id}) completed successfully within timeout period ({elapsed_time:.2f}s)")
        
        return response
    except asyncio.TimeoutError:
        # Calculate elapsed time
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        # Log the timeout
        log_agent_timeout(agent_name, agent_id, timeout, elapsed_time)
        
        # If a timeout callback is provided, call it
        if on_timeout:
            on_timeout(execution_id, agent_name, elapsed_time)
        
        # Format and return the timeout message based on the action
        return format_timeout_message(agent_name, timeout, elapsed_time, timeout_action)