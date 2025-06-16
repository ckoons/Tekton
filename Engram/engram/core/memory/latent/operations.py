"""
Latent Memory Space Operations

Provides functions for operating on thoughts in latent memory space.
"""

import logging
import uuid
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from .states import ThoughtState

logger = logging.getLogger("engram.memory.latent.operations")


async def refine_thought(memory_service, namespace, thought_id, refinement, 
                       thoughts, metadata=None, max_history_length=10) -> Tuple[bool, int]:
    """
    Process thought through additional reasoning cycle.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
        thought_id: ID of the thought to refine
        refinement: Refinement content
        thoughts: Thought registry dict
        metadata: Optional metadata for this refinement
        max_history_length: Maximum number of refinement iterations to store
        
    Returns:
        Tuple of (success, iteration_number)
    """
    # Check if thought exists
    if thought_id not in thoughts:
        logger.error(f"Thought {thought_id} not found in space {namespace}")
        return False, -1
    
    # Get thought metadata
    thought_metadata = thoughts[thought_id]
    
    # Check if thought can be refined
    if thought_metadata["state"] in [ThoughtState.FINALIZED, ThoughtState.ABANDONED]:
        logger.warning(f"Cannot refine thought {thought_id}: already in state {thought_metadata['state']}")
        return False, -1
    
    # Calculate next iteration
    next_iteration = thought_metadata["iteration"] + 1
    
    # Store refinement
    content = {
        "thought": refinement,
        "iteration": next_iteration,
        "state": ThoughtState.REFINING,
        "previous_iteration": thought_metadata["iteration"]
    }
    
    refinement_metadata = {
        "thought_id": thought_id,
        "iteration": next_iteration,
        "refined_at": datetime.now().isoformat(),
        **(metadata or {})
    }
    
    success = await memory_service.add(
        content=json.dumps(content),
        namespace=namespace,
        metadata=refinement_metadata
    )
    
    if success:
        # Update thought metadata
        thought_metadata["iteration"] = next_iteration
        thought_metadata["iterations"].append(next_iteration)
        thought_metadata["state"] = ThoughtState.REFINING
        thought_metadata["updated_at"] = datetime.now().isoformat()
        
        # Prune iterations if needed
        if len(thought_metadata["iterations"]) > max_history_length:
            # Keep first and last few iterations
            keep_first = max(1, max_history_length // 3)
            keep_last = max_history_length - keep_first
            
            iterations = thought_metadata["iterations"]
            thought_metadata["iterations"] = (
                iterations[:keep_first] + 
                iterations[-keep_last:]
            )
        
        logger.info(f"Refined thought {thought_id} to iteration {next_iteration}")
        return True, next_iteration
    else:
        logger.error(f"Failed to refine thought {thought_id}")
        return False, -1


async def finalize_thought(memory_service, namespace, thought_id, thoughts, 
                         final_content=None, persist=True, persist_namespace=None) -> bool:
    """
    Complete reasoning process and optionally persist insights.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
        thought_id: ID of the thought to finalize
        thoughts: Thought registry dict
        final_content: Optional final content (if None, uses last refinement)
        persist: Whether to persist the final thought to another namespace
        persist_namespace: Namespace to persist the thought to (defaults to longterm)
        
    Returns:
        Boolean indicating success
    """
    # Check if thought exists
    if thought_id not in thoughts:
        logger.error(f"Thought {thought_id} not found in space {namespace}")
        return False
    
    # Get thought metadata
    thought_metadata = thoughts[thought_id]
    current_state = thought_metadata["state"]
    
    # Validate state transition
    if not ThoughtState.can_transition(current_state, ThoughtState.FINALIZED):
        logger.warning(f"Cannot transition from {current_state} to {ThoughtState.FINALIZED}")
        return False
    
    # Get final content
    if final_content is None:
        # Retrieve the latest refinement
        search_results = await memory_service.search(
            query=thought_id,
            namespace=namespace,
            limit=1
        )
        
        if not search_results["results"]:
            logger.error(f"Failed to retrieve latest refinement for thought {thought_id}")
            return False
        
        # Parse content
        try:
            content_obj = json.loads(search_results["results"][0]["content"])
            final_content = content_obj["thought"]
        except Exception as e:
            logger.error(f"Failed to parse thought content: {e}")
            return False
    
    # Store finalized thought
    content = {
        "thought": final_content,
        "iteration": thought_metadata["iteration"] + 1 if final_content else thought_metadata["iteration"],
        "state": ThoughtState.FINALIZED,
        "previous_state": current_state,
        "previous_iteration": thought_metadata["iteration"]
    }
    
    finalized_metadata = {
        "thought_id": thought_id,
        "iteration": content["iteration"],
        "finalized_at": datetime.now().isoformat(),
        "from_iterations": thought_metadata["iterations"],
        "previous_state": current_state
    }
    
    success = await memory_service.add(
        content=json.dumps(content),
        namespace=namespace,
        metadata=finalized_metadata
    )
    
    if success:
        # Update thought metadata
        thought_metadata["state"] = ThoughtState.FINALIZED
        thought_metadata["updated_at"] = datetime.now().isoformat()
        thought_metadata["finalized_at"] = datetime.now().isoformat()
        thought_metadata["previous_state"] = current_state
        
        if final_content:
            thought_metadata["iteration"] += 1
            thought_metadata["iterations"].append(thought_metadata["iteration"])
        
        # Persist to another namespace if requested
        if persist:
            target_namespace = persist_namespace or "longterm"
            
            # Format for persistence
            persistence_content = (
                f"Finalized thought from latent space {namespace}:\n\n"
                f"{final_content}\n\n"
                f"[Final version after {len(thought_metadata['iterations'])} refinement iterations]"
            )
            
            await memory_service.add(
                content=persistence_content,
                namespace=target_namespace,
                metadata={
                    "thought_id": thought_id,
                    "latent_space_id": namespace,
                    "source": "latent_space",
                    "iterations": len(thought_metadata["iterations"])
                }
            )
        
        logger.info(f"Finalized thought {thought_id} in space {namespace}")
        return True
    else:
        logger.error(f"Failed to finalize thought {thought_id}")
        return False


async def transition_thought_state(memory_service, namespace, thought_id, thoughts, target_state, 
                                 reason=None, metadata=None) -> bool:
    """
    Transition a thought to a different state with validation.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
        thought_id: ID of the thought to transition
        thoughts: Thought registry dict
        target_state: Target state to transition to
        reason: Optional reason for the transition
        metadata: Optional additional metadata
        
    Returns:
        Boolean indicating success
    """
    # Check if thought exists
    if thought_id not in thoughts:
        logger.error(f"Thought {thought_id} not found in space {namespace}")
        return False
    
    # Get thought metadata
    thought_metadata = thoughts[thought_id]
    current_state = thought_metadata["state"]
    
    # Validate state transition
    if not ThoughtState.can_transition(current_state, target_state):
        logger.warning(f"Cannot transition from {current_state} to {target_state}")
        return False
    
    # Build additional metadata
    operation_metadata = {
        "thought_id": thought_id,
        "previous_state": current_state,
        **(metadata or {})
    }
    
    # Add state-specific metadata
    timestamp_field = f"{target_state.lower()}_at"
    operation_metadata[timestamp_field] = datetime.now().isoformat()
    
    if reason:
        reason_field = f"{target_state.lower()}_reason"
        operation_metadata["reason"] = reason
    
    # Store operation
    content = {
        "thought_id": thought_id,
        "state": target_state,
        "previous_state": current_state,
        "reason": reason or "No reason provided"
    }
    
    success = await memory_service.add(
        content=json.dumps(content),
        namespace=namespace,
        metadata=operation_metadata
    )
    
    if success:
        # Update thought metadata
        thought_metadata["state"] = target_state
        thought_metadata["updated_at"] = datetime.now().isoformat()
        thought_metadata[timestamp_field] = datetime.now().isoformat()
        
        if reason:
            thought_metadata[reason_field] = reason
            
        # Add any additional metadata
        if metadata:
            thought_metadata.update(metadata)
        
        logger.info(f"Transitioned thought {thought_id} from {current_state} to {target_state}")
        return True
    else:
        logger.error(f"Failed to transition thought {thought_id} to {target_state}")
        return False


async def merge_thoughts(memory_service, namespace, thought_ids, thoughts,
                       merged_content, reason, component_id=None) -> Optional[str]:
    """
    Merge multiple thoughts into a new combined thought.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space  
        thought_ids: List of thought IDs to merge
        thoughts: Thought registry dict
        merged_content: Content for the merged thought
        reason: Reason for merging
        component_id: Optional component ID for the new thought
        
    Returns:
        ID of the new merged thought or None if failed
    """
    # Check if all thoughts exist
    for thought_id in thought_ids:
        if thought_id not in thoughts:
            logger.error(f"Thought {thought_id} not found in space {namespace}")
            return None
    
    # Require a reason
    if not reason:
        logger.error("A reason is required to merge thoughts")
        return None
    
    # Check if all thoughts can transition to MERGED state
    for thought_id in thought_ids:
        current_state = thoughts[thought_id]["state"]
        if not ThoughtState.can_transition(current_state, ThoughtState.MERGED):
            logger.warning(f"Thought {thought_id} cannot transition from {current_state} to {ThoughtState.MERGED}")
            return None
    
    # Create new thought for the merged result
    merged_thought_id = f"thought-{uuid.uuid4()}"
    
    # Create thought metadata
    thought_metadata = {
        "thought_id": merged_thought_id,
        "component_id": component_id or thoughts[thought_ids[0]].get("component_id", "unknown"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "state": ThoughtState.INITIAL,
        "iteration": 0,
        "iterations": [0],  # List of available iterations
        "merged_from": thought_ids,
        "merge_reason": reason
    }
    
    # Store initial merged thought
    content = {
        "thought": merged_content,
        "iteration": 0,
        "state": ThoughtState.INITIAL
    }
    
    success = await memory_service.add(
        content=json.dumps(content),
        namespace=namespace,
        metadata={
            "thought_id": merged_thought_id,
            "iteration": 0,
            **thought_metadata
        }
    )
    
    if not success:
        logger.error("Failed to create merged thought")
        return None
    
    # Mark all source thoughts as merged
    for thought_id in thought_ids:
        # Get thought metadata
        thought_metadata = thoughts[thought_id]
        current_state = thought_metadata["state"]
        
        # Store merge operation
        content = {
            "thought_id": thought_id,
            "state": ThoughtState.MERGED,
            "previous_state": current_state,
            "merged_into": merged_thought_id,
            "reason": reason
        }
        
        merge_metadata = {
            "thought_id": thought_id,
            "merged_at": datetime.now().isoformat(),
            "previous_state": current_state,
            "merged_into": merged_thought_id,
            "reason": reason
        }
        
        success = await memory_service.add(
            content=json.dumps(content),
            namespace=namespace,
            metadata=merge_metadata
        )
        
        if success:
            # Update thought metadata
            thought_metadata["state"] = ThoughtState.MERGED
            thought_metadata["updated_at"] = datetime.now().isoformat()
            thought_metadata["merged_at"] = datetime.now().isoformat()
            thought_metadata["merged_into"] = merged_thought_id
            thought_metadata["merge_reason"] = reason
        else:
            logger.error(f"Failed to update merge state for thought {thought_id}")
    
    # Add new thought to registry
    thoughts[merged_thought_id] = thought_metadata
    
    logger.info(f"Merged thoughts {thought_ids} into {merged_thought_id} in space {namespace}")
    return merged_thought_id