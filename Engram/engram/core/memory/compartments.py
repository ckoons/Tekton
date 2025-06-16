#!/usr/bin/env python3
"""
Memory Compartments

Provides compartmentalized memory organization for different contexts.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from engram.core.memory.utils import (
    load_json_file,
    save_json_file,
    parse_expiration_date,
    is_expired
)

logger = logging.getLogger("engram.memory.compartments")

class CompartmentManager:
    """
    Manages memory compartments for organizing memory contexts.
    
    Compartments provide a way to organize memories into separate
    contexts that can be activated or deactivated as needed.
    """
    
    def __init__(self, client_id: str, data_dir: Path):
        """
        Initialize compartment manager.
        
        Args:
            client_id: Unique identifier for the client
            data_dir: Directory to store compartment data
        """
        self.client_id = client_id
        self.data_dir = data_dir
        self.compartment_file = data_dir / f"{client_id}-compartments.json"
        self.compartments = self._load_compartments()
        self.active_compartments = []
        
    def _load_compartments(self) -> Dict[str, Dict[str, Any]]:
        """
        Load compartment definitions from file.
        
        Returns:
            Dictionary of compartment data by ID
        """
        return load_json_file(self.compartment_file) or {}
        
    def _save_compartments(self) -> bool:
        """
        Save compartment definitions to file.
        
        Returns:
            Boolean indicating success
        """
        return save_json_file(self.compartment_file, self.compartments)
        
    async def create_compartment(self, 
                               name: str, 
                               description: str = None, 
                               parent: str = None) -> Optional[str]:
        """
        Create a new memory compartment.
        
        Args:
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
            self.compartments[compartment_id] = compartment_data
            
            # Save to file
            self._save_compartments()
            
            return compartment_id
        except Exception as e:
            logger.error(f"Error creating compartment: {e}")
            return None
            
    async def activate_compartment(self, compartment_id_or_name: str) -> bool:
        """
        Activate a compartment to include in automatic context retrieval.
        
        Args:
            compartment_id_or_name: ID or name of compartment to activate
            
        Returns:
            Boolean indicating success
        """
        try:
            # Resolve compartment ID from name if needed
            compartment_id = self._resolve_compartment_id(compartment_id_or_name)
            if not compartment_id:
                logger.warning(f"No compartment found matching '{compartment_id_or_name}'")
                return False
                
            # Check if compartment is expired
            if self._is_compartment_expired(compartment_id):
                logger.warning(f"Cannot activate expired compartment: {compartment_id}")
                return False
                
            # Update last accessed time
            self.compartments[compartment_id]["last_accessed"] = datetime.now().isoformat()
            self._save_compartments()
            
            # Add to active compartments if not already active
            if compartment_id not in self.active_compartments:
                self.active_compartments.append(compartment_id)
                
            return True
        except Exception as e:
            logger.error(f"Error activating compartment: {e}")
            return False
            
    async def deactivate_compartment(self, compartment_id_or_name: str) -> bool:
        """
        Deactivate a compartment to exclude from automatic context retrieval.
        
        Args:
            compartment_id_or_name: ID or name of compartment to deactivate
            
        Returns:
            Boolean indicating success
        """
        try:
            # Resolve compartment ID from name if needed
            compartment_id = self._resolve_compartment_id(compartment_id_or_name)
            if not compartment_id:
                logger.warning(f"No compartment found matching '{compartment_id_or_name}'")
                return False
                
            # Remove from active compartments
            if compartment_id in self.active_compartments:
                self.active_compartments.remove(compartment_id)
                
            return True
        except Exception as e:
            logger.error(f"Error deactivating compartment: {e}")
            return False
            
    async def set_compartment_expiration(self, compartment_id: str, days: int = None) -> bool:
        """
        Set expiration for a compartment in days.
        
        Args:
            compartment_id: ID of the compartment
            days: Number of days until expiration, or None to remove expiration
            
        Returns:
            Boolean indicating success
        """
        if compartment_id not in self.compartments:
            logger.warning(f"No compartment found with ID '{compartment_id}'")
            return False
            
        try:
            if days is None:
                # Remove expiration
                self.compartments[compartment_id]["expiration"] = None
            else:
                # Calculate expiration date
                expiration_date = datetime.now() + timedelta(days=days)
                self.compartments[compartment_id]["expiration"] = expiration_date.isoformat()
                
            # Save to file
            return self._save_compartments()
        except Exception as e:
            logger.error(f"Error setting compartment expiration: {e}")
            return False
            
    async def list_compartments(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        List all compartments.
        
        Args:
            include_expired: Whether to include expired compartments
            
        Returns:
            List of compartment information dictionaries
        """
        try:
            result = []
            now = datetime.now()
            
            for compartment_id, data in self.compartments.items():
                # Check expiration if needed
                if not include_expired and self._is_compartment_expired(compartment_id):
                    # Skip expired compartments
                    continue
                    
                # Add active status
                compartment_info = data.copy()
                compartment_info["active"] = compartment_id in self.active_compartments
                
                result.append(compartment_info)
                
            return result
        except Exception as e:
            logger.error(f"Error listing compartments: {e}")
            return []
            
    def get_active_compartments(self) -> List[str]:
        """
        Get list of active compartment IDs.
        
        Returns:
            List of active compartment IDs
        """
        # Filter out any expired compartments
        active = []
        for compartment_id in self.active_compartments:
            if not self._is_compartment_expired(compartment_id):
                active.append(compartment_id)
                
        # Update active list if any were filtered out
        if len(active) != len(self.active_compartments):
            self.active_compartments = active
            
        return active
        
    def get_compartment_namespaces(self) -> List[str]:
        """
        Get list of compartment namespaces.
        
        Returns:
            List of compartment namespace strings
        """
        return [f"compartment-{c_id}" for c_id in self.compartments]
        
    def _resolve_compartment_id(self, compartment_id_or_name: str) -> Optional[str]:
        """
        Resolve compartment ID from name or ID.
        
        Args:
            compartment_id_or_name: Compartment name or ID
            
        Returns:
            Compartment ID or None if not found
        """
        # Check if the input is a compartment ID
        if compartment_id_or_name in self.compartments:
            return compartment_id_or_name
            
        # Look for a compartment with matching name
        for c_id, c_data in self.compartments.items():
            if c_data.get("name", "").lower() == compartment_id_or_name.lower():
                return c_id
                
        return None
        
    def _is_compartment_expired(self, compartment_id: str) -> bool:
        """
        Check if a compartment is expired.
        
        Args:
            compartment_id: Compartment ID
            
        Returns:
            True if expired, False otherwise
        """
        if compartment_id not in self.compartments:
            return False
            
        compartment = self.compartments[compartment_id]
        expiration_str = compartment.get("expiration")
        
        if not expiration_str:
            return False
            
        # Parse expiration date
        expiration_date = parse_expiration_date(expiration_str)
        
        # Check if expired
        return is_expired(expiration_date)

# Function wrappers for direct import
_compartment_manager = None

def _get_compartment_manager(client_id: str, data_dir: Path) -> CompartmentManager:
    """Get or create compartment manager instance."""
    global _compartment_manager
    if _compartment_manager is None:
        _compartment_manager = CompartmentManager(client_id, data_dir)
    return _compartment_manager

async def create_compartment(
    client_id: str, 
    data_dir: Path,
    name: str, 
    description: str = None, 
    parent: str = None
) -> Optional[str]:
    """Create a new memory compartment."""
    manager = _get_compartment_manager(client_id, data_dir)
    return await manager.create_compartment(name, description, parent)

async def activate_compartment(
    client_id: str,
    data_dir: Path,
    compartment_id_or_name: str
) -> bool:
    """Activate a compartment."""
    manager = _get_compartment_manager(client_id, data_dir)
    return await manager.activate_compartment(compartment_id_or_name)

async def deactivate_compartment(
    client_id: str,
    data_dir: Path,
    compartment_id_or_name: str
) -> bool:
    """Deactivate a compartment."""
    manager = _get_compartment_manager(client_id, data_dir)
    return await manager.deactivate_compartment(compartment_id_or_name)

async def set_compartment_expiration(
    client_id: str,
    data_dir: Path,
    compartment_id: str,
    days: int = None
) -> bool:
    """Set expiration for a compartment."""
    manager = _get_compartment_manager(client_id, data_dir)
    return await manager.set_compartment_expiration(compartment_id, days)

async def list_compartments(
    client_id: str,
    data_dir: Path,
    include_expired: bool = False
) -> List[Dict[str, Any]]:
    """List all compartments."""
    manager = _get_compartment_manager(client_id, data_dir)
    return await manager.list_compartments(include_expired)