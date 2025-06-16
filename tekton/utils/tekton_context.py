"""
Tekton Context Management

This module provides standardized context management for tracking conversation
contexts, request metadata, and state across interactions.

Usage:
    from tekton.utils.tekton_context import (
        ConversationContext,
        ContextManager,
        get_current_context
    )
    
    # Creating a new context
    context = ConversationContext(context_id="abc123")
    context.add_message("user", "Hello, how are you?")
    context.add_message("assistant", "I'm doing well, thank you!")
    
    # Storing and retrieving contexts
    manager = ContextManager()
    manager.store_context(context)
    retrieved = manager.get_context("abc123")
    
    # Using the context in request handlers
    @app.post("/api/chat")
    async def chat_endpoint(request: ChatRequest):
        context = get_current_context() or ConversationContext()
        context.add_message("user", request.message)
        response = await generate_response(context)
        context.add_message("assistant", response)
        return {"response": response, "context_id": context.context_id}
"""

import json
import time
import uuid
import logging
import asyncio
import threading
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Set, Tuple, TypeVar, Generic, cast, Callable

# Thread-local storage for context
_thread_local = threading.local()

# Set up logger
logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Standard message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class ConversationContext:
    """
    Represents a conversation context with message history and metadata.
    
    This class provides a standardized way to manage conversation contexts,
    including message history, metadata, and state.
    """
    
    def __init__(
        self,
        context_id: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_messages: int = 100
    ):
        """
        Initialize a conversation context.
        
        Args:
            context_id: Context identifier (auto-generated if None)
            messages: Initial messages
            metadata: Context metadata
            max_messages: Maximum number of messages to store
        """
        self.context_id = context_id or str(uuid.uuid4())
        self.messages = messages or []
        self.metadata = metadata or {}
        self.max_messages = max_messages
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def add_message(
        self,
        role: Union[str, MessageRole],
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to the context.
        
        Args:
            role: Message role (user, assistant, system, etc.)
            content: Message content
            metadata: Message metadata
            
        Returns:
            The added message
        """
        # Convert MessageRole enum to string if needed
        if isinstance(role, MessageRole):
            role = role.value
        
        # Create message object
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        
        # Add metadata if provided
        if metadata:
            message["metadata"] = metadata
        
        # Add to messages, respecting max_messages
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        # Update timestamps
        self.updated_at = time.time()
        
        return message
    
    def get_messages(
        self,
        limit: Optional[int] = None,
        roles: Optional[List[Union[str, MessageRole]]] = None,
        start_index: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages from the context.
        
        Args:
            limit: Maximum number of messages to return
            roles: Only include messages with these roles
            start_index: Start index for messages
            
        Returns:
            List of messages
        """
        # Convert MessageRole enums to strings if needed
        if roles:
            roles = [
                role.value if isinstance(role, MessageRole) else role
                for role in roles
            ]
        
        # Filter by role if specified
        if roles:
            filtered_messages = [
                msg for msg in self.messages[start_index:]
                if msg["role"] in roles
            ]
        else:
            filtered_messages = self.messages[start_index:]
        
        # Apply limit if specified
        if limit is not None:
            filtered_messages = filtered_messages[-limit:]
        
        return filtered_messages
    
    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """
        Get the last message in the context.
        
        Returns:
            Last message or None if no messages
        """
        if not self.messages:
            return None
        
        return self.messages[-1]
    
    def clear_messages(self) -> None:
        """Clear all messages from the context."""
        self.messages = []
        self.updated_at = time.time()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set a metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = time.time()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update multiple metadata values.
        
        Args:
            metadata: Metadata values to update
        """
        self.metadata.update(metadata)
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            "context_id": self.context_id,
            "messages": self.messages,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """
        Create a context from a dictionary.
        
        Args:
            data: Dictionary representation of a context
            
        Returns:
            Conversation context
        """
        context = cls(
            context_id=data.get("context_id"),
            messages=data.get("messages", []),
            metadata=data.get("metadata", {})
        )
        
        # Restore timestamps if available
        if "created_at" in data:
            context.created_at = data["created_at"]
        
        if "updated_at" in data:
            context.updated_at = data["updated_at"]
        
        return context
    
    def to_llm_context(
        self,
        include_system: bool = True,
        system_message: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Convert the context to a format suitable for LLM APIs.
        
        Args:
            include_system: Whether to include system messages
            system_message: Optional system message to prepend
            max_tokens: Maximum tokens to include (approximated by characters)
            
        Returns:
            List of messages in LLM format
        """
        # Start with system message if provided
        messages = []
        if system_message and include_system:
            messages.append({"role": "system", "content": system_message})
        
        # Get filtered messages (skipping system messages if not included)
        filtered_messages = []
        for msg in self.messages:
            if not include_system and msg["role"] == "system":
                continue
            
            filtered_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Apply token limit if specified (approximate by characters)
        if max_tokens is not None:
            # Average characters per token is about 4
            max_chars = max_tokens * 4
            
            # Add messages until limit is reached
            remaining_chars = max_chars
            trimmed_messages = []
            
            # Process in reverse to prioritize recent messages
            for msg in reversed(filtered_messages):
                content_len = len(msg["content"])
                if content_len <= remaining_chars:
                    trimmed_messages.insert(0, msg)
                    remaining_chars -= content_len
                else:
                    # Include partial message if possible
                    if remaining_chars > 20:  # Minimum length to include
                        trimmed_msg = msg.copy()
                        trimmed_msg["content"] = msg["content"][:remaining_chars] + "..."
                        trimmed_messages.insert(0, trimmed_msg)
                    break
            
            # Replace filtered messages with trimmed ones
            filtered_messages = trimmed_messages
        
        # Combine with system message
        messages.extend(filtered_messages)
        
        return messages


class ContextManager:
    """
    Manager for conversation contexts.
    
    This class provides storage, retrieval, and lifecycle management for
    conversation contexts.
    """
    
    def __init__(
        self,
        max_contexts: int = 1000,
        context_ttl: int = 86400,  # 24 hours
        cleanup_interval: int = 3600  # 1 hour
    ):
        """
        Initialize the context manager.
        
        Args:
            max_contexts: Maximum number of contexts to store
            context_ttl: Context time-to-live in seconds
            cleanup_interval: Interval for context cleanup in seconds
        """
        self.contexts: Dict[str, ConversationContext] = {}
        self.max_contexts = max_contexts
        self.context_ttl = context_ttl
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        self._lock = threading.RLock()
    
    def get_context(self, context_id: str) -> Optional[ConversationContext]:
        """
        Get a context by ID.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Conversation context or None if not found
        """
        with self._lock:
            # Maybe run cleanup
            self._maybe_cleanup()
            
            return self.contexts.get(context_id)
    
    def store_context(self, context: ConversationContext) -> None:
        """
        Store a context.
        
        Args:
            context: Conversation context to store
        """
        with self._lock:
            # Maybe run cleanup
            self._maybe_cleanup()
            
            # Check if we're at capacity
            if len(self.contexts) >= self.max_contexts and context.context_id not in self.contexts:
                # Remove oldest context
                oldest_id = None
                oldest_time = float('inf')
                
                for cid, ctx in self.contexts.items():
                    if ctx.updated_at < oldest_time:
                        oldest_id = cid
                        oldest_time = ctx.updated_at
                
                if oldest_id:
                    del self.contexts[oldest_id]
            
            # Store the context
            self.contexts[context.context_id] = context
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            True if context was deleted
        """
        with self._lock:
            if context_id in self.contexts:
                del self.contexts[context_id]
                return True
            
            return False
    
    def list_contexts(
        self,
        filter_func: Optional[Callable[[ConversationContext], bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all contexts.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of context dictionaries
        """
        with self._lock:
            # Maybe run cleanup
            self._maybe_cleanup()
            
            result = []
            
            for context in self.contexts.values():
                if filter_func is None or filter_func(context):
                    result.append({
                        "context_id": context.context_id,
                        "created_at": context.created_at,
                        "updated_at": context.updated_at,
                        "message_count": len(context.messages),
                        "metadata": context.metadata
                    })
            
            return result
    
    def _maybe_cleanup(self) -> None:
        """
        Run context cleanup if needed.
        
        This method removes expired contexts based on their TTL.
        """
        current_time = time.time()
        
        # Check if cleanup is needed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Update cleanup timestamp
        self.last_cleanup = current_time
        
        # Find expired contexts
        expired_ids = []
        for context_id, context in self.contexts.items():
            if current_time - context.updated_at > self.context_ttl:
                expired_ids.append(context_id)
        
        # Remove expired contexts
        for context_id in expired_ids:
            del self.contexts[context_id]
        
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired contexts")
    
    def create_context(self, **kwargs) -> ConversationContext:
        """
        Create and store a new context.
        
        Args:
            **kwargs: Arguments for ConversationContext constructor
            
        Returns:
            New conversation context
        """
        context = ConversationContext(**kwargs)
        self.store_context(context)
        return context


# Global context manager
_global_context_manager = ContextManager()


def get_global_context_manager() -> ContextManager:
    """
    Get the global context manager.
    
    Returns:
        Global context manager
    """
    return _global_context_manager


def set_current_context(context: Optional[ConversationContext]) -> None:
    """
    Set the current thread's context.
    
    Args:
        context: Conversation context
    """
    _thread_local.current_context = context


def get_current_context() -> Optional[ConversationContext]:
    """
    Get the current thread's context.
    
    Returns:
        Current conversation context or None
    """
    return getattr(_thread_local, "current_context", None)


class RequestContext:
    """
    Context for a single request.
    
    This class provides a way to track request-specific information
    throughout the processing of a request.
    """
    
    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a request context.
        
        Args:
            request_id: Request identifier (auto-generated if None)
            user_id: User identifier
            conversation_id: Conversation identifier
            metadata: Request metadata
        """
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.values: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the context.
        
        Args:
            key: Value key
            value: Value to store
        """
        self.values[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the context.
        
        Args:
            key: Value key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.values.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "values": self.values
        }


def set_request_context(context: Optional[RequestContext]) -> None:
    """
    Set the current thread's request context.
    
    Args:
        context: Request context
    """
    _thread_local.request_context = context


def get_request_context() -> Optional[RequestContext]:
    """
    Get the current thread's request context.
    
    Returns:
        Current request context or None
    """
    return getattr(_thread_local, "request_context", None)


class ContextMiddleware:
    """
    Middleware for managing conversation and request contexts.
    
    This class provides middleware for FastAPI or other web frameworks
    to manage contexts during request processing.
    """
    
    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        context_id_header: str = "X-Context-ID",
        request_id_header: str = "X-Request-ID",
        user_id_header: str = "X-User-ID"
    ):
        """
        Initialize the context middleware.
        
        Args:
            context_manager: Context manager to use
            context_id_header: Header for context ID
            request_id_header: Header for request ID
            user_id_header: Header for user ID
        """
        self.context_manager = context_manager or get_global_context_manager()
        self.context_id_header = context_id_header
        self.request_id_header = request_id_header
        self.user_id_header = user_id_header
    
    async def __call__(self, request, call_next):
        """
        Process a request with context management.
        
        This method is designed to work with FastAPI's middleware system,
        but can be adapted for other frameworks.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or handler
            
        Returns:
            Response
        """
        # Extract headers
        context_id = request.headers.get(self.context_id_header)
        request_id = request.headers.get(self.request_id_header, str(uuid.uuid4()))
        user_id = request.headers.get(self.user_id_header)
        
        # Create request context
        request_context = RequestContext(
            request_id=request_id,
            user_id=user_id,
            conversation_id=context_id
        )
        
        # Set request context for this thread
        set_request_context(request_context)
        
        # Get conversation context if available
        conversation_context = None
        if context_id:
            conversation_context = self.context_manager.get_context(context_id)
            
            if conversation_context:
                # Set conversation context for this thread
                set_current_context(conversation_context)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Add context ID header to response if available
            if conversation_context:
                response.headers[self.context_id_header] = conversation_context.context_id
            
            # Add request ID header to response
            response.headers[self.request_id_header] = request_id
            
            return response
        
        finally:
            # Clear thread-local contexts
            set_current_context(None)
            set_request_context(None)


# Context serialization/deserialization utilities

def serialize_context(context: ConversationContext) -> str:
    """
    Serialize a context to a JSON string.
    
    Args:
        context: Conversation context
        
    Returns:
        JSON string
    """
    return json.dumps(context.to_dict())


def deserialize_context(data: str) -> ConversationContext:
    """
    Deserialize a context from a JSON string.
    
    Args:
        data: JSON string
        
    Returns:
        Conversation context
    """
    return ConversationContext.from_dict(json.loads(data))


def save_context_to_file(context: ConversationContext, file_path: str) -> None:
    """
    Save a context to a file.
    
    Args:
        context: Conversation context
        file_path: File path
    """
    with open(file_path, 'w') as f:
        json.dump(context.to_dict(), f, indent=2)


def load_context_from_file(file_path: str) -> ConversationContext:
    """
    Load a context from a file.
    
    Args:
        file_path: File path
        
    Returns:
        Conversation context
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return ConversationContext.from_dict(data)


# Decorator for context management
def with_context(context_id: Optional[str] = None) -> Callable:
    """
    Decorator for functions to run with a specific context.
    
    Args:
        context_id: Context identifier
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @asyncio.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get context manager
            manager = get_global_context_manager()
            
            # Get or create context
            if context_id is not None:
                context = manager.get_context(context_id)
                if not context:
                    context = manager.create_context(context_id=context_id)
            else:
                context = manager.create_context()
            
            # Set current context
            previous_context = get_current_context()
            set_current_context(context)
            
            try:
                # Run the function
                result = await func(*args, **kwargs)
                
                # Store updated context
                manager.store_context(context)
                
                return result
            
            finally:
                # Restore previous context
                set_current_context(previous_context)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get context manager
            manager = get_global_context_manager()
            
            # Get or create context
            if context_id is not None:
                context = manager.get_context(context_id)
                if not context:
                    context = manager.create_context(context_id=context_id)
            else:
                context = manager.create_context()
            
            # Set current context
            previous_context = get_current_context()
            set_current_context(context)
            
            try:
                # Run the function
                result = func(*args, **kwargs)
                
                # Store updated context
                manager.store_context(context)
                
                return result
            
            finally:
                # Restore previous context
                set_current_context(previous_context)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator