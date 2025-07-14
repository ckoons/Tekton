"""
CRUD operations for the LanceDB vector store.

This module provides create, read, update, and delete operations for vector store compartments.
"""

import os
import time
import logging
import pyarrow as pa
from typing import Dict, List, Any, Optional, Tuple

# Get logger
logger = logging.getLogger("lancedb_vector_store.operations")


def create_compartment(db, metadata_cache, compartment: str, dimension: int) -> bool:
    """
    Create a new compartment (table in LanceDB).
    
    Args:
        db: LanceDB connection
        metadata_cache: Metadata cache manager
        compartment: Name of the compartment to create
        dimension: Dimension of the vectors to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if table already exists
        try:
            table_names = db.table_names()
            if compartment in table_names:
                logger.info(f"Compartment '{compartment}' already exists")
                # Load metadata cache if not already loaded
                metadata_cache.load(compartment)
                return True
        except Exception as e:
            logger.warning(f"Error checking existing tables: {e}")
            # Proceed with creation attempt
            
        # Create a minimal table with required fields
        empty_table = pa.Table.from_pydict(
            {
                "id": [0],
                "text": ["initialization placeholder"],
                "vector": [[0.0] * dimension],
                "timestamp": [time.time()]
            }
        )
        
        # First try to open the table to see if it exists
        try:
            db.open_table(compartment)
            logger.info(f"Table '{compartment}' exists but wasn't listed")
            exists = True
        except:
            exists = False
            
        if not exists:
            # Create the table
            try:
                db.create_table(compartment, empty_table)
                logger.info(f"Created new compartment '{compartment}'")
            except Exception as create_err:
                logger.error(f"Error creating table: {create_err}")
                # If table creation failed due to existing table, we can still proceed
                if "already exists" not in str(create_err):
                    raise
        
        # Initialize metadata cache with the placeholder
        cache = metadata_cache.load(compartment)
        if not cache:  # If cache is empty
            cache_entry = {
                "id": 0,
                "text": "initialization placeholder",
                "timestamp": time.time(),
                "placeholder": True
            }
            metadata_cache.cache[compartment] = [cache_entry]
            metadata_cache.save(compartment)
        
        return True
    except Exception as e:
        logger.error(f"Failed to create compartment '{compartment}': {e}")
        return False


def add_to_compartment(db, metadata_cache, compartment: str, 
                      texts: List[str], embeddings: List[List[float]],
                      metadatas: Optional[List[Dict[str, Any]]] = None) -> List[int]:
    """
    Add texts and their embeddings to a compartment.
    
    Args:
        db: LanceDB connection
        metadata_cache: Metadata cache manager
        compartment: Name of the compartment to add to
        texts: List of texts to add
        embeddings: List of embedding vectors for the texts
        metadatas: Optional list of metadata dicts for the texts
        
    Returns:
        List of IDs assigned to the added texts
    """
    if not texts:
        return []
        
    # Ensure metadata is provided for each text
    if metadatas is None:
        metadatas = [{} for _ in texts]
    elif len(metadatas) != len(texts):
        raise ValueError(f"Number of texts ({len(texts)}) and metadata ({len(metadatas)}) must match")
        
    try:
        # Ensure compartment exists
        try:
            if compartment not in db.table_names():
                create_compartment(db, metadata_cache, compartment, len(embeddings[0]))
        except Exception as e:
            logger.warning(f"Error checking compartments: {e}")
            # Try to create it anyway
            create_compartment(db, metadata_cache, compartment, len(embeddings[0]))
            
        # Load metadata cache
        cache = metadata_cache.load(compartment)
        
        # Current count in the index
        start_id = 1  # Start from 1 since 0 is the placeholder
        if cache:
            start_id = max(item.get("id", 0) for item in cache) + 1
            
        # Generate IDs
        ids = list(range(start_id, start_id + len(texts)))
        
        # Prepare data for LanceDB
        timestamp = time.time()
        data = {
            "id": ids,
            "text": texts,
            "vector": embeddings,
            "timestamp": [timestamp] * len(texts)
        }
        
        # Add metadata fields - create empty fields for all possible metadata keys
        all_keys = set()
        for meta in metadatas:
            all_keys.update(meta.keys())
            
        # Add each metadata field with appropriate values for each record
        for key in all_keys:
            data[key] = [meta.get(key, None) for meta in metadatas]
            
        # Create Arrow table
        table = pa.Table.from_pydict(data)
        
        # Add to LanceDB
        try:
            db_table = db.open_table(compartment)
            db_table.add(table)
            logger.info(f"Added {len(texts)} texts to table '{compartment}'")
        except Exception as table_err:
            logger.error(f"Failed to add to table: {table_err}")
            # Try to create the table first if it doesn't exist or has schema issues
            if "Table does not exist" in str(table_err) or "schema mismatch" in str(table_err).lower():
                logger.info(f"Creating table '{compartment}' with new schema")
                try:
                    db.create_table(compartment, table)
                    logger.info(f"Created table '{compartment}' with data")
                except Exception as create_err:
                    logger.error(f"Failed to create table: {create_err}")
                    # Still keep track in metadata cache even if DB operation failed
            else:
                raise
        
        # Add to metadata cache
        metadata_cache.add_entries(compartment, texts, ids, timestamp, metadatas)
        
        return ids
        
    except Exception as e:
        logger.error(f"Failed to add texts to compartment '{compartment}': {e}")
        # Fallback to metadata-only operation if database failed
        try:
            # Generate IDs
            start_id = 1
            cache = metadata_cache.load(compartment)
            if cache:
                start_id = max(item.get("id", 0) for item in cache) + 1
            ids = list(range(start_id, start_id + len(texts)))
            
            # Add to metadata cache
            timestamp = time.time()
            metadata_cache.add_entries(compartment, texts, ids, timestamp, metadatas)
            
            logger.warning(f"Added {len(texts)} texts to metadata cache only (DB operation failed)")
            return ids
        except Exception as fallback_err:
            logger.error(f"Fallback metadata-only operation also failed: {fallback_err}")
            return []


def save_compartment(db, metadata_cache, compartment: str) -> bool:
    """
    Save a compartment explicitly (forcing cache save and optionally compacting).
    
    Args:
        db: LanceDB connection
        metadata_cache: Metadata cache manager
        compartment: Name of the compartment to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Save metadata cache
        metadata_cache.save(compartment)
        
        # Compact the table if possible
        try:
            db_table = db.open_table(compartment)
            db_table.compact()
            logger.info(f"Compacted compartment '{compartment}'")
        except Exception as e:
            logger.warning(f"Failed to compact compartment '{compartment}': {e}")
            
        logger.info(f"Saved compartment '{compartment}'")
        return True
    except Exception as e:
        logger.error(f"Failed to save compartment '{compartment}': {e}")
        return False


def delete_compartment(db, metadata_cache, compartment: str) -> bool:
    """
    Delete a compartment and its metadata.
    
    Args:
        db: LanceDB connection
        metadata_cache: Metadata cache manager
        compartment: Name of the compartment to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Delete from LanceDB
        try:
            db.drop_table(compartment)
            logger.info(f"Deleted table '{compartment}'")
        except Exception as e:
            logger.warning(f"Failed to drop table '{compartment}': {e}")
        
        # Delete metadata cache
        metadata_success = metadata_cache.delete_compartment(compartment)
        
        return metadata_success
    except Exception as e:
        logger.error(f"Failed to delete compartment '{compartment}': {e}")
        return False