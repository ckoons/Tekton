"""
Latent Memory Space Persistence

Provides functions for persisting and loading thoughts in latent memory space.
"""

import logging
import uuid
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import os
from pathlib import Path

logger = logging.getLogger("engram.memory.latent.persistence")


def save_thoughts(thoughts, memory_service, namespace):
    """
    Save thought registry to storage.
    
    Args:
        thoughts: Thought registry dict
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
    """
    try:
        # Ensure directory exists
        metadata_dir = memory_service.data_dir / f"{memory_service.client_id}"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Save thought registry
        metadata_file = metadata_dir / f"{namespace}-thoughts.json"
        with open(metadata_file, 'w') as f:
            json.dump(thoughts, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving thoughts to {namespace}: {e}")


def load_thoughts(memory_service, namespace) -> Dict[str, Dict[str, Any]]:
    """
    Load existing thoughts from storage.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
        
    Returns:
        Dictionary of thought ID to thought metadata
    """
    try:
        # Check if index file exists
        metadata_file = memory_service.data_dir / f"{memory_service.client_id}" / f"{namespace}-thoughts.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                thoughts = json.load(f)
            logger.info(f"Loaded {len(thoughts)} thoughts from {namespace}")
            return thoughts
        else:
            # Initialize empty thought registry
            return {}
    except Exception as e:
        logger.error(f"Error loading thoughts from {namespace}: {e}")
        return {}


def initialize_space(memory_service, namespace):
    """
    Initialize the latent space in memory service.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
    """
    # Create namespace for this latent space
    if hasattr(memory_service.storage, "initialize_namespace"):
        memory_service.storage.initialize_namespace(namespace)


async def initialize_thought(memory_service, namespace, thought_seed, 
                          component_id=None, metadata=None) -> str:
    """
    Create initial thought entry in latent space.
    
    Args:
        memory_service: Memory service for storage
        namespace: Namespace for this latent space
        thought_seed: Initial thought content
        component_id: ID of component initializing the thought
        metadata: Optional metadata for the thought
        
    Returns:
        Unique thought ID
    """
    # Generate thought ID
    thought_id = f"thought-{uuid.uuid4()}"
    
    # Create thought metadata
    thought_metadata = {
        "thought_id": thought_id,
        "component_id": component_id or "unknown",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "state": "INITIAL",
        "iteration": 0,
        "iterations": [0],  # List of available iterations
        **(metadata or {})
    }
    
    # Store initial thought
    content = {
        "thought": thought_seed,
        "iteration": 0,
        "state": "INITIAL"
    }
    
    success = await memory_service.add(
        content=json.dumps(content),
        namespace=namespace,
        metadata={
            "thought_id": thought_id,
            "iteration": 0,
            **thought_metadata
        }
    )
    
    if success:
        logger.info(f"Initialized thought {thought_id} in space {namespace}")
        return thought_id, thought_metadata
    else:
        logger.error(f"Failed to initialize thought in space {namespace}")
        return None, None