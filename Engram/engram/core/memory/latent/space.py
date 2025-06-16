"""
Latent Memory Space Implementation

Provides the core LatentMemorySpace class for latent space reasoning.
"""

import logging
import uuid
import time
from datetime import datetime

# Import queries
from .queries import get_thought, get_reasoning_trace, list_thoughts, abandon_thought 
from typing import Dict, List, Any, Optional, Union, Tuple
import json

from engram.core.memory.base import MemoryService
from .states import ThoughtState
from .operations import (
    refine_thought,
    finalize_thought,
    transition_thought_state,
    merge_thoughts
)
from .persistence import (
    save_thoughts,
    load_thoughts,
    initialize_space,
    initialize_thought
)

logger = logging.getLogger("engram.memory.latent.space")

class LatentMemorySpace:
    """
    Specialized memory structure for latent space reasoning.
    
    Enables components to store, iteratively refine, and finalize thoughts
    in a dedicated latent reasoning space.
    """
    
    def __init__(self, 
                memory_service: MemoryService,
                space_id: Optional[str] = None,
                owner_component: Optional[str] = None,
                shared: bool = False,
                max_history_length: int = 10):
        """
        Initialize a latent memory space.
        
        Args:
            memory_service: The underlying memory service for storage
            space_id: Unique identifier for this latent space (generated if None)
            owner_component: Component that owns this space (if not shared)
            shared: Whether this is a shared latent space
            max_history_length: Maximum number of refinement iterations to store
        """
        self.memory_service = memory_service
        self.space_id = space_id or f"latent-{uuid.uuid4()}"
        self.owner_component = owner_component
        self.shared = shared
        self.max_history_length = max_history_length
        
        # Namespace for this latent space
        self.namespace = f"latent-{self.space_id}"
        
        # Thought registry - maps thought IDs to metadata
        self.thoughts: Dict[str, Dict[str, Any]] = {}
        
        # Initialize namespace in memory service
        initialize_space(self.memory_service, self.namespace)
        
        # Load existing thoughts if any
        self.thoughts = load_thoughts(self.memory_service, self.namespace)
        
        logger.info(f"Initialized latent memory space {self.space_id} (shared: {self.shared})")
    
    def _save_thoughts(self):
        """Save thought registry to storage."""
        save_thoughts(self.thoughts, self.memory_service, self.namespace)
    
    async def initialize_thought(self, 
                               thought_seed: str, 
                               component_id: Optional[str] = None, 
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create initial thought entry in latent space.
        
        Args:
            thought_seed: Initial thought content
            component_id: ID of component initializing the thought
            metadata: Optional metadata for the thought
            
        Returns:
            Unique thought ID
        """
        # Use the component ID from constructor if not provided
        effective_component_id = component_id or self.owner_component
        
        # Initialize the thought
        thought_id, thought_metadata = await initialize_thought(
            self.memory_service,
            self.namespace,
            thought_seed,
            effective_component_id,
            metadata
        )
        
        if thought_id and thought_metadata:
            # Add to thought registry
            self.thoughts[thought_id] = thought_metadata
            self._save_thoughts()
            return thought_id
        else:
            return None
    
    async def refine_thought(self, 
                           thought_id: str, 
                           refinement: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, int]:
        """
        Process thought through additional reasoning cycle.
        
        Args:
            thought_id: ID of the thought to refine
            refinement: Refinement content
            metadata: Optional metadata for this refinement
            
        Returns:
            Tuple of (success, iteration_number)
        """
        success, iteration = await refine_thought(
            self.memory_service,
            self.namespace,
            thought_id,
            refinement,
            self.thoughts,
            metadata,
            self.max_history_length
        )
        
        if success:
            self._save_thoughts()
        
        return success, iteration
    
    async def finalize_thought(self, 
                            thought_id: str, 
                            final_content: Optional[str] = None,
                            persist: bool = True,
                            persist_namespace: Optional[str] = None) -> bool:
        """
        Complete reasoning process and optionally persist insights.
        
        Args:
            thought_id: ID of the thought to finalize
            final_content: Optional final content (if None, uses last refinement)
            persist: Whether to persist the final thought to another namespace
            persist_namespace: Namespace to persist the thought to (defaults to longterm)
            
        Returns:
            Boolean indicating success
        """
        success = await finalize_thought(
            self.memory_service,
            self.namespace,
            thought_id,
            self.thoughts,
            final_content,
            persist,
            persist_namespace
        )
        
        if success:
            self._save_thoughts()
        
        return success
    
    async def pause_thought(self, thought_id: str, reason: Optional[str] = None) -> bool:
        """
        Pause active work on a thought without abandoning it.
        
        Args:
            thought_id: ID of the thought to pause
            reason: Optional reason for pausing
            
        Returns:
            Boolean indicating success
        """
        success = await transition_thought_state(
            self.memory_service,
            self.namespace,
            thought_id,
            self.thoughts,
            ThoughtState.PAUSED,
            reason
        )
        
        if success:
            self._save_thoughts()
        
        return success
    
    async def reject_thought(self, thought_id: str, reason: str) -> bool:
        """
        Explicitly reject a thought as invalid or incorrect.
        
        Args:
            thought_id: ID of the thought to reject
            reason: Reason for rejection (required)
            
        Returns:
            Boolean indicating success
        """
        # Require a reason for rejection
        if not reason:
            logger.error("A reason is required to reject a thought")
            return False
        
        success = await transition_thought_state(
            self.memory_service,
            self.namespace,
            thought_id,
            self.thoughts,
            ThoughtState.REJECTED,
            reason
        )
        
        if success:
            self._save_thoughts()
        
        return success
    
    async def reconsider_thought(self, 
                             thought_id: str, 
                             reason: str,
                             new_context: Optional[str] = None) -> bool:
        """
        Start reconsidering a previously finalized, abandoned, or rejected thought.
        
        Args:
            thought_id: ID of the thought to reconsider
            reason: Reason for reconsidering
            new_context: Optional new context or evidence
            
        Returns:
            Boolean indicating success
        """
        # Require a reason for reconsidering
        if not reason:
            logger.error("A reason is required to reconsider a thought")
            return False
        
        additional_metadata = {}
        if new_context:
            additional_metadata["new_context"] = new_context
        
        success = await transition_thought_state(
            self.memory_service,
            self.namespace,
            thought_id,
            self.thoughts,
            ThoughtState.RECONSIDERING,
            reason,
            additional_metadata
        )
        
        if success:
            self._save_thoughts()
        
        return success
    
    async def supersede_thought(self,
                            old_thought_id: str,
                            new_thought_id: str,
                            reason: str) -> bool:
        """
        Mark a thought as superseded by a newer, better thought.
        
        Args:
            old_thought_id: ID of the thought being superseded
            new_thought_id: ID of the thought that supersedes it
            reason: Reason for superseding
            
        Returns:
            Boolean indicating success
        """
        # Check if thoughts exist
        if old_thought_id not in self.thoughts:
            logger.error(f"Old thought {old_thought_id} not found in space {self.space_id}")
            return False
            
        if new_thought_id not in self.thoughts:
            logger.error(f"New thought {new_thought_id} not found in space {self.space_id}")
            return False
        
        # Require a reason
        if not reason:
            logger.error("A reason is required to supersede a thought")
            return False
        
        # Set additional metadata for the supersede operation
        additional_metadata = {
            "superseded_by": new_thought_id
        }
        
        success = await transition_thought_state(
            self.memory_service,
            self.namespace,
            old_thought_id,
            self.thoughts,
            ThoughtState.SUPERSEDED,
            reason,
            additional_metadata
        )
        
        if success:
            # Update new thought to reference the superseded thought
            new_metadata = self.thoughts[new_thought_id]
            if "supersedes" not in new_metadata:
                new_metadata["supersedes"] = []
            new_metadata["supersedes"].append(old_thought_id)
            
            self._save_thoughts()
        
        return success
    
    async def merge_thoughts(self,
                         thought_ids: List[str],
                         merged_content: str,
                         reason: str) -> Optional[str]:
        """
        Merge multiple thoughts into a new combined thought.
        
        Args:
            thought_ids: List of thought IDs to merge
            merged_content: Content for the merged thought
            reason: Reason for merging
            
        Returns:
            ID of the new merged thought or None if failed
        """
        merged_thought_id = await merge_thoughts(
            self.memory_service,
            self.namespace,
            thought_ids,
            self.thoughts,
            merged_content,
            reason,
            self.owner_component
        )
        
        if merged_thought_id:
            self._save_thoughts()
        
        return merged_thought_id