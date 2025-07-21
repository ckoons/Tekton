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
from landmarks import architecture_decision, performance_boundary, state_checkpoint, integration_point

# Import Hermes database client
try:
    from hermes.utils.database_helper import DatabaseClient
    from hermes.core.database_manager import DatabaseBackend
    HAS_HERMES = True
except ImportError:
    HAS_HERMES = False
    DatabaseClient = None

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
                use_database: bool = True,
                max_history: int = 100):
        """
        Initialize the state manager.
        
        Args:
            storage_dir: Directory for storing state files
            use_database: Whether to use a database for state storage
            max_history: Maximum number of historical states to keep
        """
        self.storage_dir = storage_dir or os.path.join(os.path.expanduser("~"), ".harmonia", "state")
        self.use_database = use_database and HAS_HERMES
        self.max_history = max_history
        
        # Initialize database client if available
        if self.use_database:
            self.db_client = DatabaseClient(
                component_id="harmonia",
                data_path=self.storage_dir
            )
            logger.info("Using Hermes database services for state persistence")
        else:
            self.db_client = None
            os.makedirs(self.storage_dir, exist_ok=True)
            logger.info("Using file-based storage for state persistence")
        
        # In-memory cache of recent states
        self.state_cache: Dict[str, Dict[str, Any]] = {}
        
        # Database connections (initialized on first use)
        self._doc_db = None
        self._kv_db = None
    
    @integration_point(
        title="Hermes document database connection",
        target_component="Hermes",
        protocol="MCP",
        data_flow="Connect to Hermes document database for workflow state persistence"
    )
    async def _get_doc_db(self):
        """Get document database connection."""
        if self._doc_db is None and self.db_client:
            self._doc_db = await self.db_client.get_document_db(
                namespace="workflow_states"
            )
        return self._doc_db
    
    async def _get_kv_db(self):
        """Get key-value database connection."""
        if self._kv_db is None and self.db_client:
            self._kv_db = await self.db_client.get_key_value_db(
                namespace="workflow_metadata"
            )
        return self._kv_db
    
    async def _save_to_file(self, execution_id: str, state: Dict[str, Any]) -> bool:
        """Save state to file (fallback method)."""
        try:
            state_file = os.path.join(self.storage_dir, f"{execution_id}.pickle")
            
            # Create a copy with serializable workflow
            state_copy = state.copy()
            state_copy["workflow"] = state_copy["workflow"].to_dict()
            
            with open(state_file, "wb") as f:
                pickle.dump(state_copy, f)
            
            logger.debug(f"Saved workflow state for execution {execution_id} to file")
            return True
            
        except Exception as e:
            logger.error(f"Error saving workflow state for execution {execution_id}: {e}")
            return False
    
    @performance_boundary(
        title="Workflow state persistence",
        sla="<200ms storage latency",
        optimization_notes="Uses caching and async I/O"
    )
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
        
        if self.use_database:
            try:
                doc_db = await self._get_doc_db()
                
                # Prepare state document
                state_doc = {
                    "execution_id": execution_id,
                    "workflow": state["workflow"].to_dict(),
                    "status": state.get("status"),
                    "current_task": state.get("current_task"),
                    "completed_tasks": state.get("completed_tasks", []),
                    "context": state.get("context", {}),
                    "timestamp": datetime.now().isoformat(),
                    "version": state.get("version", 1)
                }
                
                # Store in document database
                await doc_db.upsert(
                    {"execution_id": execution_id},
                    state_doc
                )
                
                # Store metadata in key-value store for fast lookup
                kv_db = await self._get_kv_db()
                await kv_db.set(
                    f"workflow:{execution_id}:metadata",
                    {
                        "status": state.get("status"),
                        "created_at": state.get("created_at"),
                        "updated_at": datetime.now().isoformat()
                    }
                )
                
                logger.debug(f"Saved workflow state for {execution_id} to Hermes")
                return True
                
            except Exception as e:
                logger.error(f"Error saving to Hermes: {e}")
                # Fall back to file storage
                return await self._save_to_file(execution_id, state)
        else:
            # Use file storage
            return await self._save_to_file(execution_id, state)
    
    async def _load_from_file(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Load state from file (fallback method)."""
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
            
            logger.debug(f"Loaded workflow state for execution {execution_id} from file")
            return state
            
        except Exception as e:
            logger.error(f"Error loading workflow state for execution {execution_id}: {e}")
            return None
    
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
        
        if self.use_database:
            try:
                doc_db = await self._get_doc_db()
                
                # Load from document database
                state_doc = await doc_db.find_one(
                    {"execution_id": execution_id}
                )
                
                if state_doc:
                    # Reconstruct workflow object
                    from harmonia.core.workflow import Workflow
                    workflow = Workflow.from_dict(state_doc["workflow"])
                    
                    # Reconstruct state
                    state = {
                        "id": execution_id,
                        "workflow": workflow,
                        "status": state_doc.get("status"),
                        "current_task": state_doc.get("current_task"),
                        "completed_tasks": state_doc.get("completed_tasks", []),
                        "context": state_doc.get("context", {})
                    }
                    
                    # Update cache
                    self.state_cache[execution_id] = state
                    
                    logger.debug(f"Loaded workflow state for {execution_id} from Hermes")
                    return state
                    
            except Exception as e:
                logger.error(f"Error loading from Hermes: {e}")
                # Fall back to file storage
                
        # Fallback to file storage
        return await self._load_from_file(execution_id)
    
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