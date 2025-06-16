"""
Metadata management for FAISS vector store.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

class MetadataManager:
    """
    Manages metadata for vectors and the index.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the metadata manager.
        
        Args:
            data_path: Path to the data directory
        """
        self.data_path = data_path
        self.metadata_path = os.path.join(data_path, "metadata.json")
        
    def load_index_metadata(self) -> Dict[str, Any]:
        """
        Load index metadata from disk.
        
        Returns:
            Metadata dictionary or empty dict if not found
        """
        try:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    metadata = json.load(f)
                logger.debug(f"Loaded metadata from {self.metadata_path}")
                return metadata
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading metadata from {self.metadata_path}: {e}")
            return {}
    
    def save_index_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Save index metadata to disk.
        
        Args:
            metadata: Metadata to save
            
        Returns:
            True if successful
        """
        try:
            # Update timestamp
            metadata["updated_at"] = datetime.now().isoformat()
            
            # Write to disk
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.debug(f"Saved metadata to {self.metadata_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving metadata to {self.metadata_path}: {e}")
            return False
    
    def load_vector_metadata(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata for a specific vector.
        
        Args:
            vector_id: ID of the vector
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_path = os.path.join(self.data_path, f"metadata_{vector_id}.json")
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading vector metadata for {vector_id}: {e}")
            return None
    
    def save_vector_metadata(self, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata for a specific vector.
        
        Args:
            vector_id: ID of the vector
            metadata: Metadata to save
            
        Returns:
            True if successful
        """
        metadata_path = os.path.join(self.data_path, f"metadata_{vector_id}.json")
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving vector metadata for {vector_id}: {e}")
            return False
    
    def delete_vector_metadata(self, vector_id: str) -> bool:
        """
        Delete metadata for a specific vector.
        
        Args:
            vector_id: ID of the vector
            
        Returns:
            True if successful
        """
        metadata_path = os.path.join(self.data_path, f"metadata_{vector_id}.json")
        try:
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting vector metadata for {vector_id}: {e}")
            return False