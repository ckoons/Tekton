#!/usr/bin/env python3
"""
Synthesis Event System

This module provides an event system for emitting and subscribing to events
across the Synthesis execution engine.
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Set, Union
from datetime import datetime

# Configure logging
logger = logging.getLogger("synthesis.core.events")


class EventManager:
    """
    Event manager for Synthesis.
    
    This class provides a singleton event manager for publishing and
    subscribing to events across the Synthesis execution engine.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'EventManager':
        """
        Get the singleton instance of the event manager.
        
        Returns:
            EventManager instance
        """
        if cls._instance is None:
            cls._instance = EventManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the event manager."""
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.subscribers_all: Set[Callable] = set()
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
    async def emit(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Emit an event to subscribers.
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            Event ID
        """
        # Create event object
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        event = {
            "id": event_id,
            "type": event_type,
            "timestamp": timestamp,
            "data": data
        }
        
        # Add to history
        self.event_history.append(event)
        
        # Prune history if needed
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
            
        # Notify subscribers for this event type
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await self._call_subscriber(callback, event)
                except Exception as e:
                    logger.error(f"Error notifying subscriber for event {event_type}: {e}")
                    
        # Notify subscribers for all events
        for callback in self.subscribers_all:
            try:
                await self._call_subscriber(callback, event)
            except Exception as e:
                logger.error(f"Error notifying subscriber for all events: {e}")
                
        return event_id
    
    async def _call_subscriber(self, callback: Callable, event: Dict[str, Any]) -> None:
        """
        Call a subscriber callback.
        
        Args:
            callback: Subscriber callback
            event: Event data
        """
        if asyncio.iscoroutinefunction(callback):
            await callback(event)
        else:
            callback(event)
    
    def subscribe(self, event_type: Optional[str], callback: Callable) -> None:
        """
        Subscribe to events.
        
        Args:
            event_type: Type of event to subscribe to, or None for all events
            callback: Callback function to call when event occurs
        """
        if event_type is None:
            # Subscribe to all events
            self.subscribers_all.add(callback)
        else:
            # Subscribe to specific event type
            if event_type not in self.subscribers:
                self.subscribers[event_type] = set()
            self.subscribers[event_type].add(callback)
            
    def unsubscribe(self, event_type: Optional[str], callback: Callable) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of event to unsubscribe from, or None for all events
            callback: Callback function to remove
        """
        if event_type is None:
            # Unsubscribe from all events
            self.subscribers_all.discard(callback)
        else:
            # Unsubscribe from specific event type
            if event_type in self.subscribers:
                self.subscribers[event_type].discard(callback)
                
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent events.
        
        Args:
            event_type: Type of event to filter by, or None for all events
            limit: Maximum number of events to return
            
        Returns:
            List of events
        """
        if event_type is None:
            # Return all events
            return self.event_history[-limit:]
        else:
            # Filter by event type
            return [event for event in self.event_history if event["type"] == event_type][-limit:]


class WebSocketManager:
    """
    WebSocket manager for event broadcasting.
    
    This class manages WebSocket connections and broadcasts events to connected clients.
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Dict[str, Any] = {}
        self.event_manager = EventManager.get_instance()
        
        # Subscribe to all events
        self.event_manager.subscribe(None, self.broadcast_event)
        
    async def connect(self, websocket) -> str:
        """
        Register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            Connection ID
        """
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket client connected: {connection_id}")
        return connection_id
        
    def disconnect(self, connection_id: str) -> None:
        """
        Unregister a WebSocket connection.
        
        Args:
            connection_id: Connection ID
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket client disconnected: {connection_id}")
            
    async def broadcast_event(self, event: Dict[str, Any]) -> None:
        """
        Broadcast an event to all connected WebSocket clients.
        
        Args:
            event: Event data to broadcast
        """
        # Create message
        message = {
            "type": "event",
            "event": event
        }
        
        # Convert to JSON string
        json_message = json.dumps(message)
        
        # Broadcast to all clients
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json_message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket {connection_id}: {e}")
                disconnected.append(connection_id)
                
        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)
            
    async def broadcast_message(self, message: Union[Dict[str, Any], str]) -> None:
        """
        Broadcast a message to all connected WebSocket clients.
        
        Args:
            message: Message to broadcast
        """
        # Convert to JSON string if not already
        if isinstance(message, dict):
            json_message = json.dumps(message)
        else:
            json_message = message
            
        # Broadcast to all clients
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json_message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket {connection_id}: {e}")
                disconnected.append(connection_id)
                
        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)
            
    async def send_message(self, connection_id: str, message: Union[Dict[str, Any], str]) -> bool:
        """
        Send a message to a specific WebSocket client.
        
        Args:
            connection_id: Connection ID
            message: Message to send
            
        Returns:
            True if message was sent, False if client not found
        """
        if connection_id not in self.active_connections:
            return False
            
        # Convert to JSON string if not already
        if isinstance(message, dict):
            json_message = json.dumps(message)
        else:
            json_message = message
            
        # Send message
        try:
            await self.active_connections[connection_id].send_text(json_message)
            return True
        except Exception as e:
            logger.error(f"Error sending to WebSocket {connection_id}: {e}")
            self.disconnect(connection_id)
            return False
            
    async def process_message(self, websocket, data: Dict[str, Any]) -> None:
        """
        Process a message from a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            data: Message data
        """
        # Get message type
        message_type = data.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "subscribe":
            # Subscribe to events
            event_types = data.get("event_types", [])
            
            # TODO: Implement topic-based subscription for WebSocket clients
            
            # Return subscription confirmation
            await websocket.send_json({
                "type": "subscribed",
                "event_types": event_types,
                "timestamp": datetime.now().isoformat()
            })
            
        elif message_type == "get_recent_events":
            # Get recent events
            event_type = data.get("event_type")
            limit = data.get("limit", 100)
            
            # Get events from event manager
            events = self.event_manager.get_recent_events(event_type, limit)
            
            # Return events
            await websocket.send_json({
                "type": "recent_events",
                "events": events,
                "count": len(events),
                "timestamp": datetime.now().isoformat()
            })