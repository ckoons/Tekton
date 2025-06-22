"""
State Manager - Workflow state persistence and management.

This module provides functionality for storing and retrieving workflow state,
enabling persistence, recovery, and observability.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime
import pickle
from landmarks import architecture_decision, performance_boundary, state_checkpoint

# Configure logger
logger = logging.getLogger(__name__)


@architecture_decision(
    title="Hybrid state storage",
    rationale="Support both file-based (pickle) and database storage for workflow state with in-memory caching",
    alternatives_considered=["Database only", "Memory only", "File only"])
@state_checkpoint(
    title="Workflow state cache",
    state_type="hybrid",
    persistence=True,
    consistency_requirements="Cache coherency with persistent storage",
    recovery_strategy="Reload from disk/database on cache miss"
)
class StateManager:
    """
    Manages workflow state persistence and retrieval.
    
    This class provides methods for saving and loading workflow state,
    enabling workflow persistence, recovery, and inspection.
    """
    
    def __init__(self, 
                storage_dir: Optional[str] = None,
                use_database: bool = False,
                max_history: int = 100):
        """
        Initialize the state manager.
        
        Args:
            storage_dir: Directory for storing state files
            use_database: Whether to use a database for state storage
            max_history: Maximum number of historical states to keep
        """
        self.storage_dir = storage_dir or os.path.join(os.path.expanduser("~"), ".harmonia", "state")
        self.use_database = use_database
        self.max_history = max_history
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # In-memory cache of recent states
        self.state_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"State manager initialized with storage directory: {self.storage_dir}")
    
    async def save_workflow_state(self, 
                               execution_id: str, 
                               state: Dict[str, Any]) -> bool:
        """
        Save workflow state.
        
        Args:
            execution_id: Workflow execution ID
            state: Workflow state to save
            
        Returns:
            True if save was successful
        """
        # Update cache
        self.state_cache[execution_id] = state.copy()
        
        # Save to disk
        if not self.use_database:
            try:
                state_file = os.path.join(self.storage_dir, f"{execution_id}.pickle")
                
                # Create a copy with serializable workflow
                state_copy = state.copy()
                state_copy["workflow"] = state_copy["workflow"].to_dict()
                
                with open(state_file, "wb") as f:
                    pickle.dump(state_copy, f)
                
                logger.debug(f"Saved workflow state for execution {execution_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error saving workflow state for execution {execution_id}: {e}")
                return False
        else:
            # Database storage would be implemented here
            logger.warning("Database storage not yet implemented")
            return True
    
    async def load_workflow_state(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Load workflow state.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Workflow state or None if not found
        """
        # Check cache first
        if execution_id in self.state_cache:
            logger.debug(f"Loaded workflow state for execution {execution_id} from cache")
            return self.state_cache[execution_id]
        
        # Load from disk
        if not self.use_database:
            try:
                state_file = os.path.join(self.storage_dir, f"{execution_id}.pickle")
                
                if not os.path.exists(state_file):
                    logger.warning(f"Workflow state file not found: {state_file}")
                    return None
                
                with open(state_file, "rb") as f:
                    state = pickle.load(f)
                
                # Reconstruct Workflow object
                from harmonia.core.workflow import Workflow
                workflow_dict = state["workflow"]
                state["workflow"] = Workflow.from_dict(workflow_dict)
                
                # Update cache
                self.state_cache[execution_id] = state
                
                logger.debug(f"Loaded workflow state for execution {execution_id} from disk")
                return state
                
            except Exception as e:
                logger.error(f"Error loading workflow state for execution {execution_id}: {e}")
                return None
        else:
            # Database loading would be implemented here
            logger.warning("Database loading not yet implemented")
            return None
    
    async def delete_workflow_state(self, execution_id: str) -> bool:
        """
        Delete workflow state.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            True if deletion was successful
        """
        # Remove from cache
        if execution_id in self.state_cache:
            del self.state_cache[execution_id]
        
        # Remove from disk
        if not self.use_database:
            try:
                state_file = os.path.join(self.storage_dir, f"{execution_id}.pickle")
                
                if os.path.exists(state_file):
                    os.remove(state_file)
                    logger.debug(f"Deleted workflow state for execution {execution_id}")
                    return True
                else:
                    logger.warning(f"Workflow state file not found: {state_file}")
                    return False
                
            except Exception as e:
                logger.error(f"Error deleting workflow state for execution {execution_id}: {e}")
                return False
        else:
            # Database deletion would be implemented here
            logger.warning("Database deletion not yet implemented")
            return True
    
    async def list_workflow_states(self) -> List[str]:
        """
        List all workflow execution IDs.
        
        Returns:
            List of workflow execution IDs
        """
        if not self.use_database:
            try:
                state_files = [f for f in os.listdir(self.storage_dir) if f.endswith(".pickle")]
                execution_ids = [f.replace(".pickle", "") for f in state_files]
                return execution_ids
                
            except Exception as e:
                logger.error(f"Error listing workflow states: {e}")
                return []
        else:
            # Database listing would be implemented here
            logger.warning("Database listing not yet implemented")
            return []
    
    async def create_checkpoint(self, execution_id: str) -> str:
        """
        Create a checkpoint of the current workflow state.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Checkpoint ID
        """
        # Load current state
        state = await self.load_workflow_state(execution_id)
        
        if not state:
            raise ValueError(f"Workflow execution {execution_id} not found")
        
        # Create checkpoint ID
        checkpoint_id = f"{execution_id}_checkpoint_{int(datetime.now().timestamp())}"
        
        # Save state with checkpoint ID
        await self.save_workflow_state(checkpoint_id, state)
        
        logger.info(f"Created checkpoint {checkpoint_id} for workflow execution {execution_id}")
        return checkpoint_id
    
    async def restore_checkpoint(self, checkpoint_id: str) -> str:
        """
        Restore a workflow from a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            New execution ID for the restored workflow
        """
        # Load checkpoint state
        state = await self.load_workflow_state(checkpoint_id)
        
        if not state:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        # Create new execution ID
        original_id = checkpoint_id.split("_checkpoint_")[0]
        new_execution_id = f"{original_id}_restored_{int(datetime.now().timestamp())}"
        
        # Update execution ID in state
        state["id"] = new_execution_id
        
        # Save with new execution ID
        await self.save_workflow_state(new_execution_id, state)
        
        logger.info(f"Restored workflow from checkpoint {checkpoint_id} to execution {new_execution_id}")
        return new_execution_id