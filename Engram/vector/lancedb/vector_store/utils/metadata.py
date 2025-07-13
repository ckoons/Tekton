"""
Metadata cache utilities for the LanceDB vector store.

This module provides utilities for managing metadata caches for vector store compartments.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

# Get logger
logger = logging.getLogger("lancedb_vector_store.metadata")


class MetadataCache:
    """
    Manager for metadata caches associated with vector store compartments.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the metadata cache manager.
        
        Args:
            data_path: Base path for storing metadata cache files
        """
        self.data_path = data_path
        self.cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_metadata_path(self, compartment: str) -> str:
        """
        Get the path for a compartment's metadata cache file.
        
        Args:
            compartment: Compartment name
            
        Returns:
            Path to the metadata cache file
        """
        return os.path.join(self.data_path, f"{compartment}_metadata.json")
    
    def load(self, compartment: str) -> List[Dict[str, Any]]:
        """
        Load metadata cache for a compartment.
        
        Args:
            compartment: Compartment name
            
        Returns:
            List of metadata entries
        """
        # If already loaded, return from memory
        if compartment in self.cache:
            return self.cache[compartment]
        
        # Check if file exists
        metadata_path = self.get_metadata_path(compartment)
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    self.cache[compartment] = json.load(f)
                logger.info(f"Loaded metadata cache for '{compartment}' with {len(self.cache[compartment])} items")
            except Exception as e:
                logger.error(f"Failed to load metadata cache for '{compartment}': {e}")
                self.cache[compartment] = []
        else:
            self.cache[compartment] = []
        
        return self.cache[compartment]
    
    def save(self, compartment: str) -> bool:
        """
        Save metadata cache for a compartment.
        
        Args:
            compartment: Compartment name
            
        Returns:
            True if successful, False otherwise
        """
        if compartment not in self.cache:
            logger.warning(f"No metadata cache to save for '{compartment}'")
            return False
        
        metadata_path = self.get_metadata_path(compartment)
        try:
            with open(metadata_path, 'w') as f:
                json.dump(self.cache[compartment], f)
            logger.info(f"Saved metadata cache for '{compartment}'")
            return True
        except Exception as e:
            logger.error(f"Failed to save metadata cache for '{compartment}': {e}")
            return False
    
    def add_entries(self, compartment: str, texts: List[str], 
                   ids: List[int], timestamp: float,
                   metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add entries to the metadata cache.
        
        Args:
            compartment: Compartment name
            texts: List of text entries
            ids: List of IDs for the entries
            timestamp: Timestamp for the entries
            metadatas: Optional list of metadata dicts for the entries
        """
        # Initialize cache for this compartment if needed
        if compartment not in self.cache:
            self.load(compartment)
        
        # Use empty dict if no metadata
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Add entries
        for i, (text, meta) in enumerate(zip(texts, metadatas)):
            entry = {
                "id": ids[i],
                "text": text,
                "timestamp": timestamp,
                **meta
            }
            self.cache[compartment].append(entry)
        
        # Save after adding entries
        self.save(compartment)
    
    def delete_compartment(self, compartment: str) -> bool:
        """
        Delete metadata cache for a compartment.
        
        Args:
            compartment: Compartment name
            
        Returns:
            True if successful, False otherwise
        """
        # Remove from memory cache
        if compartment in self.cache:
            del self.cache[compartment]
        
        # Delete cache file
        metadata_path = self.get_metadata_path(compartment)
        if os.path.exists(metadata_path):
            try:
                os.remove(metadata_path)
                logger.info(f"Deleted metadata cache file for '{compartment}'")
                return True
            except Exception as e:
                logger.error(f"Failed to delete metadata cache file for '{compartment}': {e}")
                return False
        
        return True