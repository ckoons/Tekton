"""
Context Manager - System for managing context in MCP.

This module provides a context management system for MCP,
allowing components to create, enhance, and share context.
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union

logger = logging.getLogger(__name__)

class ContextMetadata:
    """
    Metadata for MCP contexts.
    
    This class represents metadata about an MCP context,
    including creation information, history, and tracking.
    """
    
    def __init__(
        self,
        context_id: Optional[str] = None,
        source: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize context metadata.
        
        Args:
            context_id: Unique identifier for the context
            source: Information about the context source
            category: Context category (e.g., conversation, session)
            metadata: Additional metadata
        """
        self.context_id = context_id or f"ctx-{uuid.uuid4()}"
        self.source = source or {}
        self.category = category or "general"
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.updated_at = time.time()
        self.history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metadata to a dictionary.
        
        Returns:
            Dictionary representation of the metadata
        """
        return {
            "context_id": self.context_id,
            "source": self.source,
            "category": self.category,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextMetadata":
        """
        Create metadata from a dictionary.
        
        Args:
            data: Dictionary representation of metadata
            
        Returns:
            ContextMetadata instance
        """
        metadata = cls(
            context_id=data.get("context_id"),
            source=data.get("source"),
            category=data.get("category"),
            metadata=data.get("metadata")
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            metadata.created_at = data["created_at"]
        if "updated_at" in data:
            metadata.updated_at = data["updated_at"]
        if "history" in data:
            metadata.history = data["history"]
            
        return metadata
    
    def add_history_entry(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """
        Add an entry to the context history.
        
        Args:
            operation: Operation performed on the context
            details: Optional operation details
        """
        self.history.append({
            "operation": operation,
            "timestamp": time.time(),
            "details": details or {}
        })
        self.updated_at = time.time()


class ContextManager:
    """
    Manager for MCP contexts.
    
    This class provides methods for creating, enhancing, and managing
    contexts for multimodal information processing.
    """
    
    def __init__(self):
        """Initialize the context manager."""
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, ContextMetadata] = {}
        self._callbacks: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {
            "context_created": [],
            "context_updated": []
        }
        
        logger.info("Context manager initialized")
    
    async def create_context(
        self,
        data: Optional[Dict[str, Any]] = None,
        source: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context_id: Optional[str] = None
    ) -> str:
        """
        Create a new context.
        
        Args:
            data: Initial context data
            source: Information about the context source
            category: Context category
            metadata: Additional metadata
            context_id: Optional ID for the context
            
        Returns:
            Context ID
        """
        # Create context metadata
        ctx_metadata = ContextMetadata(
            context_id=context_id,
            source=source,
            category=category,
            metadata=metadata
        )
        
        # Store context and metadata
        self.contexts[ctx_metadata.context_id] = data or {}
        self.metadata[ctx_metadata.context_id] = ctx_metadata
        
        # Add history entry
        ctx_metadata.add_history_entry("created", {
            "source": source,
            "category": category
        })
        
        logger.info(f"Created context: {ctx_metadata.context_id}")
        
        # Trigger context created callbacks
        for callback in self._callbacks["context_created"]:
            try:
                callback(ctx_metadata.context_id, self.contexts[ctx_metadata.context_id])
            except Exception as e:
                logger.error(f"Error in context created callback: {e}")
        
        return ctx_metadata.context_id
    
    async def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a context by ID.
        
        Args:
            context_id: Context ID to retrieve
            
        Returns:
            Context data or None if not found
        """
        return self.contexts.get(context_id)
    
    async def get_context_metadata(self, context_id: str) -> Optional[ContextMetadata]:
        """
        Get context metadata by ID.
        
        Args:
            context_id: Context ID to retrieve metadata for
            
        Returns:
            ContextMetadata or None if not found
        """
        return self.metadata.get(context_id)
    
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any],
        operation: str = "update"
    ) -> bool:
        """
        Update a context with new or modified data.
        
        Args:
            context_id: ID of the context to update
            updates: New or updated context data
            operation: Type of update operation
            
        Returns:
            True if update successful
        """
        if context_id not in self.contexts:
            logger.warning(f"Context not found: {context_id}")
            return False
            
        # Update context data (recursive merge)
        self.contexts[context_id] = self._deep_merge(self.contexts[context_id], updates)
        
        # Update metadata
        if context_id in self.metadata:
            self.metadata[context_id].add_history_entry(operation, {
                "keys": list(updates.keys())
            })
            
        logger.debug(f"Updated context {context_id}")
        
        # Trigger context updated callbacks
        for callback in self._callbacks["context_updated"]:
            try:
                callback(context_id, self.contexts[context_id])
            except Exception as e:
                logger.error(f"Error in context updated callback: {e}")
                
        return True
    
    async def merge_contexts(
        self,
        context_ids: List[str],
        new_context_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Merge multiple contexts into a new context.
        
        Args:
            context_ids: List of context IDs to merge
            new_context_id: Optional ID for the new context
            
        Returns:
            New context ID or None if any context is not found
        """
        # Check if all contexts exist
        merged_data = {}
        sources = []
        categories = set()
        
        for context_id in context_ids:
            if context_id not in self.contexts:
                logger.warning(f"Context not found: {context_id}")
                return None
                
            # Merge data
            merged_data = self._deep_merge(merged_data, self.contexts[context_id])
            
            # Collect sources and categories
            if context_id in self.metadata:
                sources.append(self.metadata[context_id].source)
                categories.add(self.metadata[context_id].category)
                
        # Determine category based on merged contexts
        merged_category = next(iter(categories)) if len(categories) == 1 else "merged"
                
        # Create new context
        return await self.create_context(
            data=merged_data,
            source={"merged_from": [ctx_id for ctx_id in context_ids]},
            category=merged_category,
            metadata={"merged_sources": sources},
            context_id=new_context_id
        )
    
    async def enhance_context(
        self,
        context_id: str,
        enhancements: Dict[str, Any]
    ) -> bool:
        """
        Enhance a context with additional information.
        
        This is similar to update_context but specifically for
        adding computed or derived information.
        
        Args:
            context_id: ID of the context to enhance
            enhancements: Additional context information
            
        Returns:
            True if enhancement successful
        """
        return await self.update_context(
            context_id=context_id,
            updates=enhancements,
            operation="enhance"
        )
    
    async def delete_context(self, context_id: str) -> bool:
        """
        Delete a context.
        
        Args:
            context_id: ID of the context to delete
            
        Returns:
            True if deletion successful
        """
        if context_id not in self.contexts:
            logger.warning(f"Context not found: {context_id}")
            return False
            
        # Remove context and metadata
        del self.contexts[context_id]
        if context_id in self.metadata:
            del self.metadata[context_id]
            
        logger.info(f"Deleted context: {context_id}")
        return True
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            updates: Updates to apply
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Replace or add value
                result[key] = value
                
        return result
    
    def on_context_created(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for context creation events.
        
        Args:
            callback: Function to call when a context is created
        """
        self._callbacks["context_created"].append(callback)
    
    def on_context_updated(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for context update events.
        
        Args:
            callback: Function to call when a context is updated
        """
        self._callbacks["context_updated"].append(callback)


# Global context manager instance for convenience functions
_global_context_manager: Optional[ContextManager] = None

def get_context_manager() -> ContextManager:
    """
    Get the global context manager, creating it if needed.
    
    Returns:
        Global ContextManager instance
    """
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = ContextManager()
    return _global_context_manager

async def create_context(
    data: Optional[Dict[str, Any]] = None,
    source: Optional[Dict[str, Any]] = None,
    category: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new context using the global context manager.
    
    Args:
        data: Initial context data
        source: Information about the context source
        category: Context category
        metadata: Additional metadata
        
    Returns:
        Context ID
    """
    manager = get_context_manager()
    return await manager.create_context(data, source, category, metadata)

async def merge_contexts(context_ids: List[str]) -> Optional[str]:
    """
    Merge multiple contexts using the global context manager.
    
    Args:
        context_ids: List of context IDs to merge
        
    Returns:
        New context ID or None if any context is not found
    """
    manager = get_context_manager()
    return await manager.merge_contexts(context_ids)

async def enhance_context(context_id: str, enhancements: Dict[str, Any]) -> bool:
    """
    Enhance a context using the global context manager.
    
    Args:
        context_id: ID of the context to enhance
        enhancements: Additional context information
        
    Returns:
        True if enhancement successful
    """
    manager = get_context_manager()
    return await manager.enhance_context(context_id, enhancements)