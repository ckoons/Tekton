#!/usr/bin/env python3
"""
Memory Service - Core memory functionality for Engram using FAISS for vector storage

This module provides memory storage and retrieval with namespace support, allowing
AI to maintain different types of memories (conversations, thinking, longterm).

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.memory")

# Import from the refactored structure
from engram.core.memory_faiss import MemoryService
from engram.core.memory_faiss.compartments import (
    create_compartment,
    activate_compartment,
    deactivate_compartment,
    list_compartments,
    set_compartment_expiration,
    keep_memory
)
from engram.core.memory_faiss.search import (
    search,
    get_relevant_context
)

# Check if fallback mode is forced (set by environment variable)
USE_FALLBACK = os.environ.get('ENGRAM_USE_FALLBACK', '').lower() in ('1', 'true', 'yes')

# Try to import vector database components (optional dependencies)
HAS_VECTOR_DB = False
VECTOR_DB_NAME = None
VECTOR_DB_VERSION = None

if not USE_FALLBACK:
    # Import FAISS for vector-based memory
    try:
        import faiss
        import numpy as np
        from engram.core.vector_store import VectorStore
        from engram.core.simple_embedding import SimpleEmbedding
        
        HAS_VECTOR_DB = True
        VECTOR_DB_NAME = "faiss"
        
        # Get version if available
        try:
            VECTOR_DB_VERSION = faiss.__version__
        except AttributeError:
            VECTOR_DB_VERSION = "unknown"
        
        logger.info(f"Vector storage library found: {VECTOR_DB_NAME} {VECTOR_DB_VERSION}")
        logger.info("Using vector-based memory implementation with FAISS")
    except ImportError:
        HAS_VECTOR_DB = False
        logger.warning("FAISS not found, using fallback file-based implementation")
        logger.info("Memory will still work but without vector search capabilities")

# Forward methods for compatibility
async def create_compartment_wrapper(name: str, description: str = None, parent: str = None) -> Optional[str]:
    """Forward to create_compartment."""
    memory_service = globals().get("_memory_service_instance")
    if not memory_service:
        raise ValueError("Memory service not initialized")
    return await create_compartment(memory_service, name, description, parent)

async def activate_compartment_wrapper(compartment_id_or_name: str) -> bool:
    """Forward to activate_compartment."""
    memory_service = globals().get("_memory_service_instance")
    if not memory_service:
        raise ValueError("Memory service not initialized")
    return await activate_compartment(memory_service, compartment_id_or_name)

async def deactivate_compartment_wrapper(compartment_id_or_name: str) -> bool:
    """Forward to deactivate_compartment."""
    memory_service = globals().get("_memory_service_instance")
    if not memory_service:
        raise ValueError("Memory service not initialized")
    return await deactivate_compartment(memory_service, compartment_id_or_name)

async def set_compartment_expiration_wrapper(compartment_id: str, days: int = None) -> bool:
    """Forward to set_compartment_expiration."""
    memory_service = globals().get("_memory_service_instance")
    if not memory_service:
        raise ValueError("Memory service not initialized")
    return await set_compartment_expiration(memory_service, compartment_id, days)

async def list_compartments_wrapper(include_expired: bool = False) -> List[Dict[str, Any]]:
    """Forward to list_compartments."""
    memory_service = globals().get("_memory_service_instance")
    if not memory_service:
        raise ValueError("Memory service not initialized")
    return await list_compartments(memory_service, include_expired)

# Maintain the original interface with a global instance
_memory_service_instance = None

def get_memory_service(client_id: str = "default", data_dir: Optional[str] = None) -> MemoryService:
    """Get or create a memory service instance."""
    global _memory_service_instance
    if _memory_service_instance is None or _memory_service_instance.client_id != client_id:
        _memory_service_instance = MemoryService(client_id=client_id, data_dir=data_dir)
    return _memory_service_instance

# Create standard named exports for the Engram memory client
STANDARD_NAMESPACES = ["conversations", "thinking", "longterm", "projects", "compartments", "session"]