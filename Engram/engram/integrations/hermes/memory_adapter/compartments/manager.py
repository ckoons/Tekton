"""
Compartment management for the Hermes Memory Adapter.

This module provides functionality for managing memory compartments,
including creation, activation, and expiration.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.imports import logger


class CompartmentManager:
    """
    Manager for memory compartments.
    """
    
    def __init__(self, client_id: str, data_dir: Path):
        """
        Initialize the compartment manager.
        
        Args:
            client_id: Client identifier
            data_dir: Data directory for storage
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
            Dictionary of compartment definitions
        """
        if self.compartment_file.exists():
            try:
                with open(self.compartment_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading compartments: {e}")
        
        # Initialize with empty compartments dict if none exists
        return {}
    
    def _save_compartments(self) -> bool:
        """
        Save compartment definitions to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.compartment_file, "w") as f:
                json.dump(self.compartments, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving compartments: {e}")
            return False
    
    async def create_compartment(self, name: str, description: str = None, 
                                parent: str = None) -> Optional[str]:
        """
        Create a new compartment.
        
        Args:
            name: Name of the compartment
            description: Optional description
            parent: Optional parent compartment ID
            
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
        Activate a compartment.
        
        Args:
            compartment_id_or_name: ID or name of compartment to activate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the input is a compartment ID
            if compartment_id_or_name in self.compartments:
                compartment_id = compartment_id_or_name
            else:
                # Look for a compartment with matching name
                for c_id, c_data in self.compartments.items():
                    if c_data.get("name", "").lower() == compartment_id_or_name.lower():
                        compartment_id = c_id
                        break
                else:
                    logger.warning(f"No compartment found matching '{compartment_id_or_name}'")
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
        Deactivate a compartment.
        
        Args:
            compartment_id_or_name: ID or name of compartment to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the input is a compartment ID
            if compartment_id_or_name in self.compartments:
                compartment_id = compartment_id_or_name
            else:
                # Look for a compartment with matching name
                for c_id, c_data in self.compartments.items():
                    if c_data.get("name", "").lower() == compartment_id_or_name.lower():
                        compartment_id = c_id
                        break
                else:
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
        Set expiration for a compartment.
        
        Args:
            compartment_id: ID of the compartment
            days: Number of days until expiration, or None to remove expiration
            
        Returns:
            True if successful, False otherwise
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
            self._save_compartments()
            return True
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
                compartment_info["active"] = compartment_id in self.active_compartments
                
                result.append(compartment_info)
            
            return result
        except Exception as e:
            logger.error(f"Error listing compartments: {e}")
            return []
    
    def get_active_compartments(self) -> List[str]:
        """
        Get IDs of currently active compartments.
        
        Returns:
            List of active compartment IDs
        """
        return self.active_compartments[:]  # Return a copy
    
    def get_compartment_data(self, compartment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific compartment.
        
        Args:
            compartment_id: ID of the compartment
            
        Returns:
            Compartment data dictionary or None if not found
        """
        return self.compartments.get(compartment_id)