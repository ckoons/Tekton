"""
Memory service integration for agent runner.
"""

import logging
from typing import Dict, List, Any, Optional, Union

# Configure logger
logger = logging.getLogger(__name__)

# Check if memory service is available
HAS_MEMORY = False
MemoryService = None

try:
    from ergon.core.memory.service import MemoryService as _MemoryService
    # Import successful, set flag
    HAS_MEMORY = True
    MemoryService = _MemoryService
    logger.info("Memory service available for agent runner")
except ImportError:
    # Memory service not available
    logger.warning("Memory service not available, running without memory capabilities")


async def get_memory_context(agent_id: str, input_text: str) -> Optional[str]:
    """
    Get memory context for an agent.
    
    Args:
        agent_id: ID of the agent
        input_text: Input text to get context for
        
    Returns:
        Memory context if available, None otherwise
    """
    if not HAS_MEMORY:
        return None
    
    try:
        memory_service = MemoryService(agent_id)
        memory_context = await memory_service.get_relevant_context(input_text)
        return memory_context
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        return None


async def store_memory(agent_id: str, conversation: List[Dict[str, str]]) -> bool:
    """
    Store a conversation in memory.
    
    Args:
        agent_id: ID of the agent
        conversation: Conversation to store (list of role/content dictionaries)
        
    Returns:
        True if successful, False otherwise
    """
    if not HAS_MEMORY:
        return False
    
    try:
        memory_service = MemoryService(agent_id)
        await memory_service.add(conversation)
        logger.info(f"Stored interaction in memory for agent {agent_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing memory: {str(e)}")
        return False


async def close_memory_service(agent_id: str) -> bool:
    """
    Close memory service for an agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        True if successful, False otherwise
    """
    if not HAS_MEMORY:
        return False
    
    try:
        memory_service = MemoryService(agent_id)
        await memory_service.close()
        logger.info(f"Closed memory service for agent {agent_id}")
        return True
    except Exception as e:
        logger.warning(f"Error closing memory service: {e}")
        return False