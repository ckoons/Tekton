#!/usr/bin/env python3
"""
Latent Space Memory System for Engram

This module implements a specialized memory framework for continuous latent space reasoning,
allowing components to iteratively refine their thinking processes.

Note: This is the original implementation of the latent space system.
The updated implementation using LatentMemorySpace and LatentSpaceManager classes can be found
in the memory/latent_space.py module. New development should use those classes instead.
"""

import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Union
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.core.latent_space")


class LatentMemorySpace:
    """
    Specialized memory structure for iterative thought refinement in latent space.
    
    This class provides methods for initializing, refining, and finalizing thoughts,
    supporting the continuous reasoning process inspired by Coconut research.
    """
    
    def __init__(self, 
                component_id: str, 
                namespace: str = "default", 
                max_history: int = 20,
                data_dir: Optional[str] = None):
        """
        Initialize a latent memory space.
        
        Args:
            component_id: Unique identifier for the component using this space
            namespace: Namespace for organizing thoughts (default: "default")
            max_history: Maximum number of iterations to store per thought
            data_dir: Directory to store persisted thoughts (default: ~/.engram/latent)
        """
        self.component_id = component_id
        self.namespace = namespace
        self.thoughts = {}  # Thought storage
        self.iterations = {}  # Track iterations per thought
        self.max_history = max_history
        
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            import os
            self.data_dir = os.path.expanduser("~/.engram/latent")
            
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load any previously persisted thoughts
        self._load_persisted_thoughts()
        
        logger.info(f"Initialized latent memory space for {component_id} in namespace {namespace}")
        
    async def initialize_thought(self, 
                               thought_seed: str, 
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create initial thought entry in latent space.
        
        Args:
            thought_seed: Initial thought content
            metadata: Optional metadata for the thought
            
        Returns:
            Unique thought identifier
        """
        thought_id = f"thought_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "component_id": self.component_id,
            "created_at": time.time(),
            "iteration": 0,
            "namespace": self.namespace,
            "finalized": False
        })
        
        self.thoughts[thought_id] = {
            "content": thought_seed,
            "metadata": metadata,
            "iterations": [{
                "content": thought_seed,
                "timestamp": time.time(),
                "iteration": 0
            }]
        }
        
        self.iterations[thought_id] = 0
        logger.debug(f"Initialized thought {thought_id} in latent space")
        return thought_id
        
    async def refine_thought(self, 
                           thought_id: str, 
                           refinement: str, 
                           iteration: Optional[int] = None,
                           metadata_updates: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process thought through additional reasoning cycle.
        
        Args:
            thought_id: Identifier for the thought to refine
            refinement: Updated thought content
            iteration: Optional iteration number (auto-increments if not provided)
            metadata_updates: Optional updates to thought metadata
            
        Returns:
            Updated thought data
        """
        if thought_id not in self.thoughts:
            raise ValueError(f"Thought {thought_id} not found")
            
        if self.thoughts[thought_id]["metadata"].get("finalized", False):
            raise ValueError(f"Cannot refine finalized thought {thought_id}")
            
        if iteration is None:
            iteration = self.iterations[thought_id] + 1
            
        # Update the thought with new refinement
        self.thoughts[thought_id]["content"] = refinement
        self.thoughts[thought_id]["metadata"]["iteration"] = iteration
        self.thoughts[thought_id]["metadata"]["updated_at"] = time.time()
        
        # Apply metadata updates if provided
        if metadata_updates:
            self.thoughts[thought_id]["metadata"].update(metadata_updates)
        
        # Add to iterations history
        self.thoughts[thought_id]["iterations"].append({
            "content": refinement,
            "timestamp": time.time(),
            "iteration": iteration,
            "metadata": metadata_updates or {}
        })
        
        # Prune history if needed
        if len(self.thoughts[thought_id]["iterations"]) > self.max_history:
            # Keep first and last few iterations, remove middle ones
            keep_count = self.max_history // 2
            self.thoughts[thought_id]["iterations"] = (
                self.thoughts[thought_id]["iterations"][:keep_count] + 
                self.thoughts[thought_id]["iterations"][-keep_count:]
            )
        
        self.iterations[thought_id] = iteration
        logger.debug(f"Refined thought {thought_id} to iteration {iteration}")
        return self.thoughts[thought_id]
        
    async def finalize_thought(self, 
                             thought_id: str, 
                             final_content: Optional[str] = None, 
                             persist: bool = True,
                             metadata_updates: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete reasoning process and optionally persist insights.
        
        Args:
            thought_id: Identifier for the thought to finalize
            final_content: Optional final content (uses last iteration if not provided)
            persist: Whether to persist the thought to disk
            metadata_updates: Optional updates to thought metadata
            
        Returns:
            Finalized thought data
        """
        if thought_id not in self.thoughts:
            raise ValueError(f"Thought {thought_id} not found")
            
        if final_content is not None:
            self.thoughts[thought_id]["content"] = final_content
            # Add as final iteration
            self.thoughts[thought_id]["iterations"].append({
                "content": final_content,
                "timestamp": time.time(),
                "iteration": self.iterations[thought_id] + 1,
                "is_final": True
            })
            self.iterations[thought_id] += 1
            
        # Update metadata
        self.thoughts[thought_id]["metadata"]["finalized"] = True
        self.thoughts[thought_id]["metadata"]["finalized_at"] = time.time()
        
        if metadata_updates:
            self.thoughts[thought_id]["metadata"].update(metadata_updates)
            
        if persist:
            # Persist to disk
            await self._persist_thought(thought_id)
            
        logger.info(f"Finalized thought {thought_id} after {self.iterations[thought_id]} iterations")
        return self.thoughts[thought_id]
        
    async def get_reasoning_trace(self, 
                                thought_id: str, 
                                include_iterations: bool = False) -> Dict[str, Any]:
        """
        Retrieve reasoning chain with optional intermediate steps.
        
        Args:
            thought_id: Identifier for the thought to retrieve
            include_iterations: Whether to include detailed iteration history
            
        Returns:
            Thought data including reasoning trace
        """
        if thought_id not in self.thoughts:
            raise ValueError(f"Thought {thought_id} not found")
            
        result = self.thoughts[thought_id].copy()
        
        if not include_iterations:
            # Exclude detailed iteration history, keep only first and last
            iterations = result["iterations"]
            if len(iterations) > 1:
                result["iterations"] = [iterations[0], iterations[-1]]
            else:
                result["iterations"] = iterations.copy()
                
        return result
        
    async def get_all_thoughts(self, 
                             include_iterations: bool = False, 
                             only_finalized: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve all thoughts in this latent space.
        
        Args:
            include_iterations: Whether to include detailed iteration history
            only_finalized: Whether to include only finalized thoughts
            
        Returns:
            List of thought data
        """
        results = []
        
        for thought_id, thought in self.thoughts.items():
            # Filter for finalized thoughts if requested
            if only_finalized and not thought["metadata"].get("finalized", False):
                continue
                
            result = thought.copy()
            
            if not include_iterations:
                # Exclude detailed iteration history, keep only first and last
                iterations = result["iterations"]
                if len(iterations) > 1:
                    result["iterations"] = [iterations[0], iterations[-1]]
                else:
                    result["iterations"] = iterations.copy()
                    
            results.append(result)
            
        return results
        
    async def delete_thought(self, thought_id: str) -> bool:
        """
        Delete a thought from latent space.
        
        Args:
            thought_id: Identifier for the thought to delete
            
        Returns:
            Boolean indicating success
        """
        if thought_id not in self.thoughts:
            raise ValueError(f"Thought {thought_id} not found")
            
        # Remove from memory
        del self.thoughts[thought_id]
        del self.iterations[thought_id]
        
        # Remove persisted file if it exists
        try:
            import os
            file_path = os.path.join(self.data_dir, f"{thought_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error removing persisted thought file: {e}")
            return False
            
        logger.info(f"Deleted thought {thought_id} from latent space")
        return True
        
    async def clear_namespace(self) -> int:
        """
        Clear all thoughts in this namespace.
        
        Returns:
            Number of thoughts cleared
        """
        count = len(self.thoughts)
        
        # Get list of thought IDs to avoid modifying during iteration
        thought_ids = list(self.thoughts.keys())
        
        for thought_id in thought_ids:
            await self.delete_thought(thought_id)
            
        logger.info(f"Cleared {count} thoughts from namespace {self.namespace}")
        return count
        
    async def _persist_thought(self, thought_id: str) -> bool:
        """Persist a thought to disk."""
        if thought_id not in self.thoughts:
            return False
            
        try:
            file_path = f"{self.data_dir}/{thought_id}.json"
            
            with open(file_path, "w") as f:
                json.dump(self.thoughts[thought_id], f, indent=2)
                
            logger.debug(f"Persisted thought {thought_id} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error persisting thought {thought_id}: {e}")
            return False
            
    def _load_persisted_thoughts(self) -> int:
        """
        Load previously persisted thoughts.
        
        Returns:
            Number of thoughts loaded
        """
        try:
            import os
            import glob
            
            # Get all JSON files in data directory
            pattern = os.path.join(self.data_dir, "thought_*.json")
            files = glob.glob(pattern)
            
            count = 0
            for file_path in files:
                try:
                    with open(file_path, "r") as f:
                        thought_data = json.load(f)
                        
                    # Check if this thought belongs to this namespace and component
                    metadata = thought_data.get("metadata", {})
                    if (metadata.get("namespace") == self.namespace and 
                        metadata.get("component_id") == self.component_id):
                        
                        # Extract thought ID from filename
                        thought_id = os.path.basename(file_path).replace(".json", "")
                        
                        # Load into memory
                        self.thoughts[thought_id] = thought_data
                        self.iterations[thought_id] = metadata.get("iteration", 0)
                        count += 1
                except Exception as e:
                    logger.error(f"Error loading thought from {file_path}: {e}")
                    continue
                    
            logger.info(f"Loaded {count} persisted thoughts for {self.component_id} in namespace {self.namespace}")
            return count
        except Exception as e:
            logger.error(f"Error loading persisted thoughts: {e}")
            return 0


class ConvergenceDetector:
    """
    Utility for detecting convergence in iterative thought refinement.
    
    This class provides methods to determine when additional iterations are not
    producing significant improvements in thought quality.
    """
    
    @staticmethod
    async def text_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two text passages.
        
        This is a simple implementation using Jaccard similarity on word sets.
        For production, consider using a more sophisticated approach with embeddings.
        
        Args:
            text1: First text passage
            text2: Second text passage
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
            
        # Tokenize to words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
            
        return intersection / union
        
    @staticmethod
    async def detect_convergence(iterations: List[Dict[str, Any]], 
                               threshold: float = 0.85, 
                               window_size: int = 2) -> bool:
        """
        Detect if thought refinement has converged.
        
        Args:
            iterations: List of iteration data
            threshold: Similarity threshold for convergence
            window_size: Number of consecutive iterations to check
            
        Returns:
            Boolean indicating whether convergence has occurred
        """
        if len(iterations) < window_size + 1:
            return False
            
        # Check similarity between recent iterations
        recent_iterations = iterations[-window_size-1:]
        
        for i in range(len(recent_iterations) - 1):
            text1 = recent_iterations[i].get("content", "")
            text2 = recent_iterations[i+1].get("content", "")
            
            similarity = await ConvergenceDetector.text_similarity(text1, text2)
            
            # If any pair is below threshold, not converged
            if similarity < threshold:
                return False
                
        return True