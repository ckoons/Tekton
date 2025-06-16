"""
Latent Space Manager

Manages multiple latent memory spaces across different components.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union

from engram.core.memory.base import MemoryService
from .space import LatentMemorySpace

logger = logging.getLogger("engram.memory.latent.manager")

class LatentSpaceManager:
    """
    Manager for all latent memory spaces.
    
    Creates, tracks, and manages latent spaces for different components.
    """
    
    def __init__(self, memory_service: MemoryService):
        """
        Initialize the latent space manager.
        
        Args:
            memory_service: The underlying memory service
        """
        self.memory_service = memory_service
        self.spaces: Dict[str, LatentMemorySpace] = {}
        self.component_spaces: Dict[str, List[str]] = {}
        
        self.shared_space_id = f"shared-latent-{uuid.uuid4()}"
        self.shared_space = None
        
        # Initialize shared space
        self._initialize_shared_space()
        
        logger.info("Initialized latent space manager")
    
    def _initialize_shared_space(self):
        """Initialize the shared latent space."""
        self.shared_space = LatentMemorySpace(
            memory_service=self.memory_service,
            space_id=self.shared_space_id,
            shared=True
        )
        
        self.spaces[self.shared_space_id] = self.shared_space
        logger.info(f"Initialized shared latent space {self.shared_space_id}")
    
    async def create_component_space(self, 
                                  component_id: str, 
                                  space_id: Optional[str] = None,
                                  max_history_length: int = 10) -> str:
        """
        Create a latent space for a component.
        
        Args:
            component_id: ID of the component
            space_id: Optional space ID (generated if None)
            max_history_length: Maximum history length for this space
            
        Returns:
            Space ID
        """
        # Generate space ID if not provided
        if not space_id:
            space_id = f"latent-{component_id}-{uuid.uuid4()}"
        
        # Create latent space
        space = LatentMemorySpace(
            memory_service=self.memory_service,
            space_id=space_id,
            owner_component=component_id,
            shared=False,
            max_history_length=max_history_length
        )
        
        # Add to registry
        self.spaces[space_id] = space
        
        # Track component spaces
        if component_id not in self.component_spaces:
            self.component_spaces[component_id] = []
        
        self.component_spaces[component_id].append(space_id)
        
        logger.info(f"Created latent space {space_id} for component {component_id}")
        return space_id
    
    def get_space(self, space_id: str) -> Optional[LatentMemorySpace]:
        """
        Get a latent space by ID.
        
        Args:
            space_id: ID of the space to retrieve
            
        Returns:
            LatentMemorySpace or None if not found
        """
        return self.spaces.get(space_id)
    
    def get_shared_space(self) -> LatentMemorySpace:
        """Get the shared latent space."""
        return self.shared_space
    
    def get_component_spaces(self, component_id: str) -> List[LatentMemorySpace]:
        """
        Get all latent spaces for a component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            List of latent spaces
        """
        space_ids = self.component_spaces.get(component_id, [])
        return [self.spaces[space_id] for space_id in space_ids if space_id in self.spaces]
    
    async def delete_space(self, space_id: str) -> bool:
        """
        Delete a latent space.
        
        Args:
            space_id: ID of the space to delete
            
        Returns:
            Boolean indicating success
        """
        # Check if space exists
        if space_id not in self.spaces:
            logger.warning(f"Space {space_id} not found")
            return False
        
        # Clear space contents
        space = self.spaces[space_id]
        await space.clear_space()
        
        # Remove from registry
        del self.spaces[space_id]
        
        # Update component spaces
        for component_id, space_ids in self.component_spaces.items():
            if space_id in space_ids:
                self.component_spaces[component_id].remove(space_id)
        
        logger.info(f"Deleted latent space {space_id}")
        return True
    
    async def list_spaces(self) -> List[Dict[str, Any]]:
        """
        List all latent spaces.
        
        Returns:
            List of space information dictionaries
        """
        result = []
        
        for space_id, space in self.spaces.items():
            # Get thought counts
            thoughts = await space.list_thoughts()
            active_thoughts = [t for t in thoughts if t["state"] in ["initial", "refining"]]
            
            result.append({
                "space_id": space_id,
                "shared": space.shared,
                "owner_component": space.owner_component,
                "total_thoughts": len(thoughts),
                "active_thoughts": len(active_thoughts)
            })
        
        return result