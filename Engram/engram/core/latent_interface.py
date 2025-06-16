#!/usr/bin/env python3
"""
Latent Space Interface - High-level interface for latent space reasoning.

This module provides a simplified API for Tekton components to use latent space reasoning
leveraging the underlying LatentMemorySpace implementation.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable

from engram.core.memory import LatentMemorySpace, LatentSpaceManager, ThoughtState

logger = logging.getLogger("engram.latent_interface")

class LatentInterface:
    """
    High-level interface for latent space reasoning.
    
    This class provides a simplified, user-friendly interface for Tekton components
    to use latent space reasoning features without dealing with the underlying
    complexity of the LatentMemorySpace implementation.
    """
    
    def __init__(self, 
                memory_service=None, 
                component_id: Optional[str] = None,
                shared: bool = False):
        """
        Initialize the latent space interface.
        
        Args:
            memory_service: Engram memory service (auto-initialized if None)
            component_id: ID of the component using this latent space
            shared: Whether to use the shared latent space
        """
        self.component_id = component_id
        self.use_shared = shared
        
        # Initialize memory service if not provided
        if memory_service is None:
            from engram.core.memory.base import MemoryService
            self.memory_service = MemoryService(
                client_id=f"latent-{component_id}" if component_id else "latent-default"
            )
        else:
            self.memory_service = memory_service
        
        # Initialize latent space manager
        self.latent_manager = LatentSpaceManager(self.memory_service)
        
        # Active latent space
        self.active_space = None
        
        # Initialize active space
        self._initialize_active_space()
        
        logger.info(f"Initialized latent interface for component {component_id}")
    
    def _initialize_active_space(self):
        """Initialize the active latent space."""
        if self.use_shared:
            # Use shared space
            self.active_space = self.latent_manager.get_shared_space()
            logger.info(f"Using shared latent space: {self.active_space.space_id}")
        elif self.component_id:
            # Create component-specific space
            space_id = asyncio.run(self.latent_manager.create_component_space(self.component_id))
            self.active_space = self.latent_manager.get_space(space_id)
            logger.info(f"Created component-specific latent space: {space_id}")
        else:
            # Default to shared space
            self.active_space = self.latent_manager.get_shared_space()
            logger.info(f"Defaulting to shared latent space: {self.active_space.space_id}")
    
    async def think_iteratively(self, 
                              initial_thought: str, 
                              refinement_function: Callable[[str], Union[str, Dict[str, Any], tuple]],
                              max_iterations: int = 3,
                              confidence_threshold: float = 0.8,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform iterative thinking using latent space reasoning.
        
        Args:
            initial_thought: The initial thought to refine
            refinement_function: Function that refines thoughts (receives thought content and returns refined content)
            max_iterations: Maximum number of refinement iterations
            confidence_threshold: Threshold to stop refinement (if refinement_function returns confidence)
            metadata: Optional metadata for the thought
            
        Returns:
            Dictionary with thinking process results
        """
        # Initialize thought in latent space
        thought_id = await self.active_space.initialize_thought(
            thought_seed=initial_thought,
            component_id=self.component_id,
            metadata=metadata
        )
        
        if not thought_id:
            logger.error("Failed to initialize thought in latent space")
            return {
                "success": False,
                "final_thought": initial_thought,
                "iterations": 0,
                "message": "Failed to initialize thought"
            }
        
        # Perform refinement iterations
        iteration = 0
        current_thought = initial_thought
        refinements = []
        confidence = 0.0
        
        while iteration < max_iterations:
            # Call refinement function
            try:
                refinement_result = refinement_function(current_thought)
                
                # Handle different types of results
                if isinstance(refinement_result, tuple) and len(refinement_result) == 2:
                    # Result with confidence: (content, confidence)
                    refined_thought, confidence = refinement_result
                elif isinstance(refinement_result, dict) and "content" in refinement_result:
                    # Dictionary with content and optional confidence
                    refined_thought = refinement_result["content"]
                    confidence = refinement_result.get("confidence", 0.0)
                else:
                    # Simple string result
                    refined_thought = refinement_result
                    confidence = 0.0
            except Exception as e:
                logger.error(f"Error in refinement function: {e}")
                break
            
            # Store refinement
            success, iter_num = await self.active_space.refine_thought(
                thought_id=thought_id,
                refinement=refined_thought,
                metadata={"confidence": confidence}
            )
            
            if not success:
                logger.error(f"Failed to store refinement iteration {iteration}")
                break
            
            # Track refinement
            refinements.append({
                "iteration": iteration + 1,
                "content": refined_thought,
                "confidence": confidence
            })
            
            # Update current thought
            current_thought = refined_thought
            iteration += 1
            
            # Check if confidence threshold is reached
            if confidence >= confidence_threshold:
                logger.info(f"Stopping refinement at iteration {iteration}: confidence threshold reached")
                break
        
        # Finalize thought
        await self.active_space.finalize_thought(
            thought_id=thought_id,
            final_content=current_thought,
            persist=True
        )
        
        # Return results
        return {
            "success": True,
            "thought_id": thought_id,
            "initial_thought": initial_thought,
            "final_thought": current_thought,
            "iterations": iteration,
            "refinements": refinements,
            "confidence": confidence
        }
    
    async def recall_thinking_process(self, thought_id: str, include_iterations: bool = True) -> Dict[str, Any]:
        """
        Retrieve the complete thinking process for a thought.
        
        Args:
            thought_id: ID of the thought to retrieve
            include_iterations: Whether to include all iterations
            
        Returns:
            Dictionary with thinking process details
        """
        # Get reasoning trace
        trace = await self.active_space.get_reasoning_trace(
            thought_id=thought_id,
            include_iterations=include_iterations
        )
        
        if not trace:
            logger.error(f"Failed to retrieve reasoning trace for thought {thought_id}")
            return {
                "success": False,
                "message": "Failed to retrieve thinking process"
            }
        
        return {
            "success": True,
            "thought_id": thought_id,
            "initial_thought": trace.get("initial_thought"),
            "final_thought": trace.get("final_thought"),
            "iterations": trace.get("iterations", []),
            "metadata": trace.get("metadata", {})
        }
    
    async def list_active_thoughts(self) -> List[Dict[str, Any]]:
        """
        List all active (non-finalized) thoughts in the current space.
        
        Returns:
            List of active thought information
        """
        return await self.active_space.list_thoughts(state=ThoughtState.REFINING)
    
    async def list_all_thoughts(self) -> List[Dict[str, Any]]:
        """
        List all thoughts in the current space.
        
        Returns:
            List of all thought information
        """
        return await self.active_space.list_thoughts()
    
    async def switch_to_space(self, space_id: str) -> bool:
        """
        Switch to a different latent space.
        
        Args:
            space_id: ID of the space to switch to
            
        Returns:
            Boolean indicating success
        """
        space = self.latent_manager.get_space(space_id)
        if not space:
            logger.error(f"Latent space {space_id} not found")
            return False
        
        self.active_space = space
        logger.info(f"Switched to latent space {space_id}")
        return True
    
    async def create_dedicated_space(self, name: Optional[str] = None) -> str:
        """
        Create a new dedicated latent space for a specific task.
        
        Args:
            name: Optional name for the space (used as part of the ID)
            
        Returns:
            ID of the new space
        """
        space_id_base = name or "dedicated"
        space_id = await self.latent_manager.create_component_space(
            component_id=self.component_id or "anonymous",
            space_id=f"latent-{space_id_base}"
        )
        
        # Automatically switch to the new space
        await self.switch_to_space(space_id)
        
        return space_id