#!/usr/bin/env python3
"""
Memory compartment management functionality
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.compartments")

async def create_compartment(
    memory_service,
    name: str, 
    description: str = None, 
    parent: str = None
) -> Optional[str]:
    """
    Create a new memory compartment.
    
    Args:
        memory_service: The memory service instance
        name: Name of the compartment
        description: Optional description
        parent: Optional parent compartment ID for hierarchical organization
        
    Returns:
        Compartment ID if successful, None otherwise
    """
    try:
        # Generate a unique ID for the compartment
        compartment_id = f"{int(time.time())}-{name.lower().replace(' ', '-')}"
        
        # Create compartment data
        compartment_data = {
            "id": compartment_id,
            "name": name,
            "description": description,
            "parent": parent,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "expiration": None  # No expiration by default
        }
        
        # Store in compartments
        memory_service.compartments[compartment_id] = compartment_data
        
        # Save to file
        memory_service._save_compartments()
        
        # Ensure storage exists for this compartment
        memory_service._ensure_compartment_collection(compartment_id)
        
        # Store the compartment info in the compartments namespace
        await memory_service.add(
            content=f"Compartment: {name} (ID: {compartment_id})\nDescription: {description or 'N/A'}\nParent: {parent or 'None'}",
            namespace="compartments",
            metadata={"compartment_id": compartment_id}
        )
        
        return compartment_id
    except Exception as e:
        logger.error(f"Error creating compartment: {e}")
        return None

async def activate_compartment(
    memory_service,
    compartment_id_or_name: str
) -> bool:
    """
    Activate a compartment to include in automatic context retrieval.
    
    Args:
        memory_service: The memory service instance
        compartment_id_or_name: ID or name of compartment to activate
        
    Returns:
        Boolean indicating success
    """
    try:
        # Check if the input is a compartment ID
        if compartment_id_or_name in memory_service.compartments:
            compartment_id = compartment_id_or_name
        else:
            # Look for a compartment with matching name
            for c_id, c_data in memory_service.compartments.items():
                if c_data.get("name", "").lower() == compartment_id_or_name.lower():
                    compartment_id = c_id
                    break
            else:
                logger.warning(f"No compartment found matching '{compartment_id_or_name}'")
                return False
        
        # Update last accessed time
        memory_service.compartments[compartment_id]["last_accessed"] = datetime.now().isoformat()
        memory_service._save_compartments()
        
        # Add to active compartments if not already active
        if compartment_id not in memory_service.active_compartments:
            memory_service.active_compartments.append(compartment_id)
            
        return True
    except Exception as e:
        logger.error(f"Error activating compartment: {e}")
        return False

async def deactivate_compartment(
    memory_service,
    compartment_id_or_name: str
) -> bool:
    """
    Deactivate a compartment to exclude from automatic context retrieval.
    
    Args:
        memory_service: The memory service instance
        compartment_id_or_name: ID or name of compartment to deactivate
        
    Returns:
        Boolean indicating success
    """
    try:
        # Check if the input is a compartment ID
        if compartment_id_or_name in memory_service.compartments:
            compartment_id = compartment_id_or_name
        else:
            # Look for a compartment with matching name
            for c_id, c_data in memory_service.compartments.items():
                if c_data.get("name", "").lower() == compartment_id_or_name.lower():
                    compartment_id = c_id
                    break
            else:
                logger.warning(f"No compartment found matching '{compartment_id_or_name}'")
                return False
        
        # Remove from active compartments
        if compartment_id in memory_service.active_compartments:
            memory_service.active_compartments.remove(compartment_id)
            
        return True
    except Exception as e:
        logger.error(f"Error deactivating compartment: {e}")
        return False

async def list_compartments(
    memory_service,
    include_expired: bool = False
) -> List[Dict[str, Any]]:
    """
    List all compartments.
    
    Args:
        memory_service: The memory service instance
        include_expired: Whether to include expired compartments
        
    Returns:
        List of compartment information dictionaries
    """
    try:
        result = []
        now = datetime.now()
        
        for compartment_id, data in memory_service.compartments.items():
            # Check expiration if needed
            if not include_expired and data.get("expiration"):
                try:
                    expiration_date = datetime.fromisoformat(data["expiration"])
                    if expiration_date < now:
                        # Skip expired compartments
                        continue
                except Exception as e:
                    logger.error(f"Error parsing expiration date: {e}")
            
            # Add active status
            compartment_info = data.copy()
            compartment_info["active"] = compartment_id in memory_service.active_compartments
            
            result.append(compartment_info)
        
        return result
    except Exception as e:
        logger.error(f"Error listing compartments: {e}")
        return []