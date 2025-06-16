"""
Latent Memory Space Queries

Implements query functionality for the latent memory space.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union

from .states import ThoughtState

logger = logging.getLogger("engram.memory.latent.queries")

async def get_thought(space, thought_id: str, iteration: Optional[int] = None):
    """
    Retrieve a specific thought.
    
    Args:
        space: The latent memory space
        thought_id: ID of the thought to retrieve
        iteration: Specific iteration to retrieve (None for latest)
        
    Returns:
        Thought content or None if not found
    """
    # Check if thought exists
    if thought_id not in space.thoughts:
        logger.error(f"Thought {thought_id} not found in space {space.space_id}")
        return None
    
    # Get thought metadata
    thought_metadata = space.thoughts[thought_id]
    
    # Determine which iteration to retrieve
    target_iteration = iteration
    if target_iteration is None:
        target_iteration = thought_metadata["iteration"]
    
    # Check if iteration exists
    if target_iteration not in thought_metadata["iterations"]:
        logger.warning(f"Iteration {target_iteration} not found for thought {thought_id}")
        # Fall back to the latest iteration
        target_iteration = thought_metadata["iteration"]
    
    # Search for the thought
    search_results = await space.memory_service.search(
        query=f"thought_id:{thought_id} iteration:{target_iteration}",
        namespace=space.namespace,
        limit=1
    )
    
    if not search_results["results"]:
        logger.error(f"Failed to retrieve thought {thought_id} iteration {target_iteration}")
        return None
    
    # Parse content
    try:
        content = json.loads(search_results["results"][0]["content"])
        return {
            "thought_id": thought_id,
            "content": content["thought"],
            "iteration": target_iteration,
            "state": content["state"],
            "metadata": thought_metadata
        }
    except Exception as e:
        logger.error(f"Failed to parse thought content: {e}")
        return None

async def get_reasoning_trace(space, thought_id: str, include_iterations: bool = True):
    """
    Retrieve reasoning chain with optional intermediate steps.
    
    Args:
        space: The latent memory space
        thought_id: ID of the thought to trace
        include_iterations: Whether to include all available iterations
        
    Returns:
        Dictionary with reasoning trace or None if not found
    """
    # Check if thought exists
    if thought_id not in space.thoughts:
        logger.error(f"Thought {thought_id} not found in space {space.space_id}")
        return None
    
    # Get thought metadata
    thought_metadata = space.thoughts[thought_id]
    
    # Prepare result
    result = {
        "thought_id": thought_id,
        "metadata": {
            "created_at": thought_metadata["created_at"],
            "updated_at": thought_metadata["updated_at"],
            "state": thought_metadata["state"],
            "iterations": len(thought_metadata["iterations"]),
            "component_id": thought_metadata["component_id"]
        }
    }
    
    # Get initial thought
    initial_thought = await get_thought(space, thought_id, iteration=0)
    if not initial_thought:
        logger.error(f"Failed to retrieve initial thought {thought_id}")
        return None
    
    result["initial_thought"] = initial_thought["content"]
    
    # Get final thought if finalized
    if thought_metadata["state"] == ThoughtState.FINALIZED:
        final_thought = await get_thought(space, thought_id, iteration=thought_metadata["iteration"])
        if final_thought:
            result["final_thought"] = final_thought["content"]
    
    # Include iterations if requested
    if include_iterations:
        iterations = []
        
        for iter_num in thought_metadata["iterations"]:
            if iter_num == 0:
                # Skip initial thought (already included)
                continue
                
            iteration_thought = await get_thought(space, thought_id, iteration=iter_num)
            if iteration_thought:
                iterations.append({
                    "iteration": iter_num,
                    "content": iteration_thought["content"]
                })
        
        result["iterations"] = iterations
    
    return result

async def list_thoughts(space, state: Optional[str] = None, component_id: Optional[str] = None):
    """
    List thoughts in a latent space with optional filtering.
    
    Args:
        space: The latent memory space
        state: Filter by thought state
        component_id: Filter by component ID
        
    Returns:
        List of thought metadata
    """
    result = []
    
    for thought_id, metadata in space.thoughts.items():
        # Apply filters
        if state and metadata["state"] != state:
            continue
        
        if component_id and metadata["component_id"] != component_id:
            continue
        
        # Add to result
        result.append({
            "thought_id": thought_id,
            **metadata
        })
    
    return result

async def abandon_thought(space, thought_id: str, reason: Optional[str] = None):
    """
    Mark a thought as abandoned.
    
    Args:
        space: The latent memory space
        thought_id: ID of the thought to abandon
        reason: Optional reason for abandonment
        
    Returns:
        Boolean indicating success
    """
    # Check if thought exists
    if thought_id not in space.thoughts:
        logger.error(f"Thought {thought_id} not found in space {space.space_id}")
        return False
    
    # Get thought metadata
    thought_metadata = space.thoughts[thought_id]
    
    # Update thought state
    thought_metadata["state"] = ThoughtState.ABANDONED
    thought_metadata["updated_at"] = space._get_timestamp()
    thought_metadata["abandoned_at"] = space._get_timestamp()
    
    if reason:
        thought_metadata["abandon_reason"] = reason
    
    # Save updated thought registry
    space._save_thoughts()
    
    logger.info(f"Abandoned thought {thought_id} in space {space.space_id}")
    return True