"""
Tool loading functionality for agent runner.
"""

import os
import sys
import logging
import importlib.util
from typing import Dict, Any, List, Optional, Callable

# Configure logger
logger = logging.getLogger(__name__)

def load_agent_tools(agent_id: int, working_dir: str) -> Dict[str, Callable]:
    """
    Load tool functions from agent files.
    
    Args:
        agent_id: ID of the agent
        working_dir: Path to the agent's working directory
        
    Returns:
        Dictionary mapping tool names to callable functions
    """
    tools = {}
    
    try:
        # Check if agent_tools.py exists
        tools_path = os.path.join(working_dir, "agent_tools.py")
        if not os.path.exists(tools_path):
            logger.info(f"No agent_tools.py found in {working_dir}")
            return tools
        
        # Load the module
        spec = importlib.util.spec_from_file_location("agent_tools", tools_path)
        if spec is None or spec.loader is None:
            logger.error(f"Failed to create module spec for {tools_path}")
            return tools
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all callable functions in the module
        for name in dir(module):
            if name.startswith("_"):
                continue
            
            func = getattr(module, name)
            if callable(func):
                tools[name] = func
                logger.debug(f"Loaded tool function: {name}")
        
        return tools
    except Exception as e:
        logger.error(f"Error loading tool functions: {str(e)}")
        return {}