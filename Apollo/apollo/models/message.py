"""
Message data models for Apollo.

This module defines the data models used for message handling and communication
between Apollo and other Tekton components.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import Field
from tekton.models import TektonBaseModel


class MessageType(str, Enum):
    """Types of messages handled by Apollo."""
    # System messages
    SYSTEM_HEARTBEAT = "system.heartbeat"
    SYSTEM_STATUS = "system.status"
    SYSTEM_ERROR = "system.error"
    SYSTEM_CONFIG = "system.config"
    
    # Context messages
    CONTEXT_CREATED = "context.created"
    CONTEXT_UPDATED = "context.updated"
    CONTEXT_CLOSED = "context.closed"
    CONTEXT_HEALTH = "context.health"
    
    # Action messages
    ACTION_RECOMMENDED = "action.recommended"
    ACTION_REQUESTED = "action.requested"
    ACTION_STARTED = "action.started"
    ACTION_COMPLETED = "action.completed"
    ACTION_FAILED = "action.failed"
    
    # Budget messages
    BUDGET_ALLOCATED = "budget.allocated"
    BUDGET_UPDATED = "budget.updated"
    BUDGET_EXCEEDED = "budget.exceeded"
    BUDGET_RESET = "budget.reset"
    
    # Protocol messages
    PROTOCOL_VIOLATION = "protocol.violation"
    PROTOCOL_UPDATED = "protocol.updated"
    
    # Prediction messages
    PREDICTION_CREATED = "prediction.created"
    PREDICTION_UPDATED = "prediction.updated"
    
    # Command messages
    COMMAND_EXECUTE = "command.execute"
    COMMAND_RESPONSE = "command.response"
    
    # Query messages
    QUERY_REQUEST = "query.request"
    QUERY_RESPONSE = "query.response"


class MessagePriority(int, Enum):
    """Priority levels for messages."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class TektonMessage(TektonBaseModel):
    """
    Base message model for Tekton component communication.
    
    This is the standard message format used for communication between
    Apollo and other Tekton components.
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    context_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextMessage(TektonMessage):
    """Message related to LLM context events."""
    def __init__(self, **data):
        # Ensure type is a context type
        if "type" not in data or not str(data["type"]).startswith("context."):
            raise ValueError("ContextMessage must have a context.* message type")
        super().__init__(**data)


class ActionMessage(TektonMessage):
    """Message related to corrective actions."""
    def __init__(self, **data):
        # Ensure type is an action type
        if "type" not in data or not str(data["type"]).startswith("action."):
            raise ValueError("ActionMessage must have an action.* message type")
        super().__init__(**data)


class BudgetMessage(TektonMessage):
    """Message related to token budget management."""
    def __init__(self, **data):
        # Ensure type is a budget type
        if "type" not in data or not str(data["type"]).startswith("budget."):
            raise ValueError("BudgetMessage must have a budget.* message type")
        super().__init__(**data)


class ProtocolMessage(TektonMessage):
    """Message related to protocol enforcement."""
    def __init__(self, **data):
        # Ensure type is a protocol type
        if "type" not in data or not str(data["type"]).startswith("protocol."):
            raise ValueError("ProtocolMessage must have a protocol.* message type")
        super().__init__(**data)


class PredictionMessage(TektonMessage):
    """Message related to predictive operations."""
    def __init__(self, **data):
        # Ensure type is a prediction type
        if "type" not in data or not str(data["type"]).startswith("prediction."):
            raise ValueError("PredictionMessage must have a prediction.* message type")
        super().__init__(**data)


class CommandMessage(TektonMessage):
    """Message for commanding operations on components."""
    def __init__(self, **data):
        # Ensure type is a command type
        if "type" not in data or not str(data["type"]).startswith("command."):
            raise ValueError("CommandMessage must have a command.* message type")
        super().__init__(**data)


class QueryMessage(TektonMessage):
    """Message for querying data from components."""
    def __init__(self, **data):
        # Ensure type is a query type
        if "type" not in data or not str(data["type"]).startswith("query."):
            raise ValueError("QueryMessage must have a query.* message type")
        super().__init__(**data)


class MessageBatch(TektonBaseModel):
    """Batch of messages for efficient transmission."""
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)
    messages: List[TektonMessage]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageSubscription(TektonBaseModel):
    """Subscription for receiving messages of specific types."""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    component: str
    message_types: List[MessageType]
    filter_expression: Optional[str] = None
    callback_url: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class MessageDeliveryStatus(str, Enum):
    """Status of message delivery."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class MessageDeliveryRecord(TektonBaseModel):
    """Record of message delivery attempt."""
    message_id: str
    subscription_id: str
    status: MessageDeliveryStatus
    attempt_count: int = 0
    last_attempt: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None