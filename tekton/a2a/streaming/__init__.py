"""
Streaming support for A2A Protocol v0.2.1

This module provides Server-Sent Events (SSE) and WebSocket support for
real-time streaming in the A2A protocol.
"""

from .sse import SSEManager, SSEEvent, SSEConnection, create_sse_response
from .events import EventType, StreamEvent, TaskEvent, AgentEvent, ChannelEvent, ConversationEvent
from .subscription import SubscriptionManager, Subscription
from .websocket import (
    WebSocketManager, 
    WebSocketConnection, 
    ConnectionState,
    websocket_manager,
    handle_websocket
)
from .channels import Channel, ChannelBridge

__all__ = [
    # SSE
    'SSEManager',
    'SSEEvent', 
    'SSEConnection',
    'create_sse_response',
    
    # Events
    'EventType',
    'StreamEvent',
    'TaskEvent',
    'AgentEvent',
    'ChannelEvent',
    'ConversationEvent',
    
    # Subscriptions
    'SubscriptionManager',
    'Subscription',
    
    # WebSocket
    'WebSocketManager',
    'WebSocketConnection',
    'ConnectionState',
    'websocket_manager',
    'handle_websocket',
    
    # Channels
    'Channel',
    'ChannelBridge'
]