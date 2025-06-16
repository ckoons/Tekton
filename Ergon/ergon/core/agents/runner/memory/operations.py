"""
Memory operations for agent runner.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from .service import HAS_MEMORY, MemoryService

# Configure logger
logger = logging.getLogger(__name__)

async def add_memory_context_to_messages(
    agent_id: str,
    messages: List[Dict[str, str]],
    input_text: str,
    agent_type: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Add memory context to messages if agent supports memory.
    
    Args:
        agent_id: ID of the agent
        messages: List of messages to add context to
        input_text: Input text used to search for relevant memories
        agent_type: Optional agent type for special handling
        
    Returns:
        Messages with memory context added
    """
    if not HAS_MEMORY:
        return messages
    
    # Only enhance memory for Nexus agents
    if not (agent_type == "nexus" or (isinstance(agent_type, str) and "nexus" in agent_type.lower())):
        return messages
    
    try:
        memory_service = MemoryService(agent_id)
        memory_context = await memory_service.get_relevant_context(input_text)
        
        # Add memory context to system prompt
        if memory_context and len(messages) > 0 and messages[0]["role"] == "system":
            messages[0]["content"] += f"\n\n{memory_context}"
        elif len(messages) > 0 and messages[0]["role"] == "system":
            # Add a reminder about memory capabilities even if no relevant memories found
            messages[0]["content"] += "\n\nYou are a memory-enabled assistant capable of remembering past interactions."
        
        return messages
    except Exception as e:
        logger.error(f"Error adding memory context: {str(e)}")
        return messages


async def store_conversation(
    agent_id: str,
    user_input: str,
    assistant_output: str,
    agent_type: Optional[str] = None
) -> bool:
    """
    Store a conversation in memory if agent supports memory.
    
    Args:
        agent_id: ID of the agent
        user_input: User input message
        assistant_output: Assistant output message
        agent_type: Optional agent type for special handling
        
    Returns:
        True if stored successfully, False otherwise
    """
    if not HAS_MEMORY:
        return False
    
    # Only store memory for Nexus agents
    if not (agent_type == "nexus" or (isinstance(agent_type, str) and "nexus" in agent_type.lower())):
        return False
    
    try:
        memory_service = MemoryService(agent_id)
        conversation = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_output}
        ]
        await memory_service.add(conversation)
        logger.info(f"Stored interaction in memory for agent {agent_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing memory: {str(e)}")
        return False