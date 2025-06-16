"""
GitHub agent handler.
"""

import logging
from typing import Dict, Any, Optional, Callable

# Configure logger
logger = logging.getLogger(__name__)

def handle_github_agent(
    input_text: str,
    tool_funcs: Dict[str, Callable]
) -> Optional[str]:
    """
    Handle GitHub agent request directly.
    
    Args:
        input_text: User input text
        tool_funcs: Dictionary of tool functions
        
    Returns:
        Response if handled directly, None otherwise
    """
    if "process_request" not in tool_funcs:
        return None
    
    try:
        # Direct call to the agent's process_request function
        return tool_funcs["process_request"](input_text)
    except Exception as e:
        logger.error(f"Error calling GitHub agent: {str(e)}")
        return f"Error calling GitHub agent: {str(e)}"