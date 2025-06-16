#!/usr/bin/env python3
"""
Memory compartment expiration functionality
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.compartments")

async def set_compartment_expiration(
    memory_service,
    compartment_id: str, 
    days: int = None
) -> bool:
    """
    Set expiration for a compartment in days.
    
    Args:
        memory_service: The memory service instance
        compartment_id: ID of the compartment
        days: Number of days until expiration, or None to remove expiration
        
    Returns:
        Boolean indicating success
    """
    if compartment_id not in memory_service.compartments:
        logger.warning(f"No compartment found with ID '{compartment_id}'")
        return False
    
    try:
        if days is None:
            # Remove expiration
            memory_service.compartments[compartment_id]["expiration"] = None
        else:
            # Calculate expiration date
            expiration_date = datetime.now() + timedelta(days=days)
            memory_service.compartments[compartment_id]["expiration"] = expiration_date.isoformat()
        
        # Save to file
        memory_service._save_compartments()
        return True
    except Exception as e:
        logger.error(f"Error setting compartment expiration: {e}")
        return False

async def keep_memory(
    memory_service,
    memory_id: str, 
    days: int = 30
) -> bool:
    """
    Keep a memory for a specified number of days by setting expiration.
    
    Args:
        memory_service: The memory service instance
        memory_id: The ID of the memory to keep
        days: Number of days to keep the memory
        
    Returns:
        Boolean indicating success
    """
    try:
        # Find the memory in fallback storage
        for namespace, memories in memory_service.fallback_memories.items():
            for memory in memories:
                if memory.get("id") == memory_id:
                    # Set expiration date in metadata
                    if "metadata" not in memory:
                        memory["metadata"] = {}
                    
                    expiration_date = datetime.now() + timedelta(days=days)
                    memory["metadata"]["expiration"] = expiration_date.isoformat()
                    
                    # Save to file if using fallback storage
                    if not memory_service.vector_available:
                        with open(memory_service.fallback_file, "w") as f:
                            json.dump(memory_service.fallback_memories, f, indent=2)
                    
                    return True
        
        # If using vector storage, we would need to implement a way to update metadata
        # This would require finding and updating the vector entry
        
        logger.warning(f"Memory {memory_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error keeping memory: {e}")
        return False