"""
Event types and models for A2A streaming
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, Union
from uuid import uuid4

from tekton.models import TektonBaseModel


class EventType(str, Enum):
    """Types of streaming events"""
    # Task events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned" 
    TASK_STATE_CHANGED = "task.state_changed"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    
    # Agent events
    AGENT_REGISTERED = "agent.registered"
    AGENT_UNREGISTERED = "agent.unregistered"
    AGENT_STATUS_CHANGED = "agent.status_changed"
    AGENT_HEARTBEAT = "agent.heartbeat"
    
    # Channel events
    CHANNEL_MESSAGE = "channel.message"
    CHANNEL_SUBSCRIBED = "channel.subscribed"
    CHANNEL_UNSUBSCRIBED = "channel.unsubscribed"
    CHANNEL_CREATED = "channel.created"
    CHANNEL_DELETED = "channel.deleted"
    
    # Conversation events
    CONVERSATION_CREATED = "conversation.created"
    CONVERSATION_PARTICIPANT_JOINED = "conversation.participant_joined"
    CONVERSATION_PARTICIPANT_LEFT = "conversation.participant_left"
    CONVERSATION_MESSAGE = "conversation.message"
    CONVERSATION_TURN_REQUESTED = "conversation.turn_requested"
    CONVERSATION_TURN_GRANTED = "conversation.turn_granted"
    CONVERSATION_TURN_ADVANCED = "conversation.turn_advanced"
    CONVERSATION_TURN_TIMEOUT = "conversation.turn_timeout"
    CONVERSATION_ENDED = "conversation.ended"
    
    # System events
    SYSTEM_ANNOUNCEMENT = "system.announcement"
    CONNECTION_ESTABLISHED = "connection.established"
    CONNECTION_CLOSED = "connection.closed"


class StreamEvent(TektonBaseModel):
    """Base class for all streaming events"""
    
    id: str
    type: EventType
    timestamp: datetime
    source: str  # Agent or component ID that generated the event
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    
    @classmethod
    def create(
        cls,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'StreamEvent':
        """Create a new stream event"""
        return cls(
            id=f"event-{uuid4()}",
            type=event_type,
            timestamp=datetime.now(timezone.utc),
            source=source,
            data=data,
            metadata=metadata or {}
        )


class TaskEvent(StreamEvent):
    """Task-specific streaming event"""
    
    task_id: str
    task_name: Optional[str] = None
    agent_id: Optional[str] = None
    
    @classmethod
    def create_state_change(
        cls,
        task_id: str,
        old_state: str,
        new_state: str,
        source: str,
        message: Optional[str] = None
    ) -> 'TaskEvent':
        """Create a task state change event"""
        return cls(
            id=f"event-{uuid4()}",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.now(timezone.utc),
            source=source,
            task_id=task_id,
            data={
                "old_state": old_state,
                "new_state": new_state,
                "message": message
            }
        )
    
    @classmethod 
    def create_progress(
        cls,
        task_id: str,
        progress: float,
        source: str,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'TaskEvent':
        """Create a task progress event"""
        return cls(
            id=f"event-{uuid4()}",
            type=EventType.TASK_PROGRESS,
            timestamp=datetime.now(timezone.utc),
            source=source,
            task_id=task_id,
            data={
                "progress": progress,
                "message": message
            },
            metadata=metadata or {}
        )


class AgentEvent(StreamEvent):
    """Agent-specific streaming event"""
    
    agent_id: str
    agent_name: Optional[str] = None
    
    @classmethod
    def create_status_change(
        cls,
        agent_id: str,
        old_status: str,
        new_status: str,
        source: str
    ) -> 'AgentEvent':
        """Create an agent status change event"""
        return cls(
            id=f"event-{uuid4()}",
            type=EventType.AGENT_STATUS_CHANGED,
            timestamp=datetime.now(timezone.utc),
            source=source,
            agent_id=agent_id,
            data={
                "old_status": old_status,
                "new_status": new_status
            }
        )


class ChannelEvent(StreamEvent):
    """Channel message event for pub/sub"""
    
    channel: str
    sender_id: str
    
    @classmethod
    def create_message(
        cls,
        channel: str,
        sender_id: str,
        message: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ChannelEvent':
        """Create a channel message event"""
        return cls(
            id=f"event-{uuid4()}",
            type=EventType.CHANNEL_MESSAGE,
            timestamp=datetime.now(timezone.utc),
            source=sender_id,
            channel=channel,
            sender_id=sender_id,
            data=message,
            metadata=metadata or {}
        )


class ConversationEvent(StreamEvent):
    """Conversation-specific event"""
    
    conversation_id: str
    participant_id: Optional[str] = None
    
    @classmethod
    def create_event(
        cls,
        event_type: EventType,
        conversation_id: str,
        source: str = "system",
        participant_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ConversationEvent':
        """Create a conversation event"""
        return cls(
            id=f"event-{uuid4()}",
            type=event_type,
            timestamp=datetime.now(timezone.utc),
            source=source,
            conversation_id=conversation_id,
            participant_id=participant_id,
            data=data or {},
            metadata=metadata or {}
        )