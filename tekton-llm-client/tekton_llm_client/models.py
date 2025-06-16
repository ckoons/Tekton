"""
Data models for the Tekton LLM Client.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator

# Temporary fix - create dummy functions if import fails
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Fallback implementations
    def debug_log(message, level="info"):
        import logging
        getattr(logging, level)(f"[DEBUG] {message}")
    
    def log_function(operation=None):
        def decorator(func):
            return func
        return decorator


class MessageRole(str, Enum):
    """Message role in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """A message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        """Validates the role and converts string to enum."""
        if isinstance(v, str):
            try:
                return MessageRole(v.lower())
            except ValueError:
                raise ValueError(f"Invalid role: {v}")
        return v


class CompletionOptions(BaseModel):
    """Options for text completion requests."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    timeout: int = 120
    retry_count: int = 3
    retry_delay: int = 1000  # milliseconds


class CompletionResponse(BaseModel):
    """Response from a text completion request."""
    content: str
    model: str
    provider: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    context_id: str
    fallback: bool = False
    timestamp: str
    latency: Optional[float] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Returns whether the request was successful."""
        return self.error is None


class StreamingChunk(BaseModel):
    """A chunk of a streaming response."""
    chunk: str
    context_id: str
    model: str
    provider: str
    timestamp: str
    done: bool = False
    fallback: bool = False
    error: Optional[str] = None


class ProviderModel(BaseModel):
    """Information about an LLM model."""
    id: str
    name: str
    context_length: Optional[int] = None
    description: Optional[str] = None
    pricing: Optional[Dict[str, float]] = None
    capabilities: Optional[List[str]] = None


class Provider(BaseModel):
    """Information about an LLM provider."""
    name: str
    available: bool
    models: List[ProviderModel]
    description: Optional[str] = None


class AvailableProviders(BaseModel):
    """Information about all available LLM providers."""
    providers: Dict[str, Provider]
    default_provider: str
    default_model: str


class ChatCompletionOptions(BaseModel):
    """Options for chat completion requests."""
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None
    stream: bool = False
    timeout: int = 120
    retry_count: int = 3
    retry_delay: int = 1000  # milliseconds
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    system_message: Optional[str] = None
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v):
        """Validates that there is at least one message in the list."""
        if not v or len(v) == 0:
            raise ValueError("At least one message is required for chat completion")
        return v
    
    def add_system_message(self, content: str) -> None:
        """Adds a system message at the beginning of the messages list."""
        if content:
            # Check if there's already a system message at the beginning
            if self.messages and self.messages[0].role == MessageRole.SYSTEM:
                self.messages[0].content = content
                debug_log.debug("tekton_llm_client", "Updated existing system message")
            else:
                self.messages.insert(0, Message(role=MessageRole.SYSTEM, content=content))
                debug_log.debug("tekton_llm_client", "Added new system message")


# Alias for backward compatibility
ChatMessage = Message