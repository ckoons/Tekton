"""
Mail agent handler.
"""

import logging
from typing import Dict, Any, Optional, Callable

# Configure logger
logger = logging.getLogger(__name__)

def setup_mail_agent(agent_name: str) -> bool:
    """
    Check if agent is a mail agent and perform any necessary setup.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        True if agent is a mail agent, False otherwise
    """
    if "mail" not in agent_name.lower() and "email" not in agent_name.lower():
        return False
    
    try:
        # Import mail module to ensure it's available
        from ergon.core.agents.mail import tools
        logger.info("Mail agent detected, mail module is available")
        return True
    except ImportError as e:
        logger.error(f"Mail agent detected but mail module not available: {str(e)}")
        return False