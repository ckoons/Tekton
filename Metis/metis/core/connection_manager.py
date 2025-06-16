"""WebSocket connection manager for Metis."""
import json
from typing import Dict, List, Set, Any
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Connect a new WebSocket client.
        
        Args:
            websocket: WebSocket connection
            client_id: Client ID
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"WebSocket client {client_id} connected")
    
    def disconnect(self, client_id: str) -> None:
        """
        Disconnect a WebSocket client.
        
        Args:
            client_id: Client ID
        """
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)
        logger.info(f"WebSocket client {client_id} disconnected")
    
    async def disconnect_all(self) -> None:
        """Disconnect all WebSocket clients."""
        for client_id in list(self.active_connections.keys()):
            websocket = self.active_connections.get(client_id)
            if websocket:
                try:
                    await websocket.close()
                except Exception as e:
                    logger.warning(f"Error closing WebSocket for client {client_id}: {e}")
            self.disconnect(client_id)
        logger.info("All WebSocket clients disconnected")
    
    def subscribe(self, client_id: str, event_types: List[str]) -> None:
        """
        Subscribe a client to event types.
        
        Args:
            client_id: Client ID
            event_types: List of event types to subscribe to
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].update(event_types)
            logger.info(f"Client {client_id} subscribed to: {event_types}")
    
    def unsubscribe(self, client_id: str, event_types: List[str]) -> None:
        """
        Unsubscribe a client from event types.
        
        Args:
            client_id: Client ID
            event_types: List of event types to unsubscribe from
        """
        if client_id in self.subscriptions:
            for event_type in event_types:
                self.subscriptions[client_id].discard(event_type)
            logger.info(f"Client {client_id} unsubscribed from: {event_types}")
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast (should have 'event' and data fields)
        """
        if not message:
            return
            
        # Convert to JSON once
        message_json = json.dumps(message)
        
        # Send to all connected clients
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_to_subscribers(self, event_type: str, data: Any) -> None:
        """
        Broadcast an event to all subscribed clients.
        
        Args:
            event_type: Event type
            data: Event data
        """
        message = {
            "type": event_type,
            "data": data
        }
        
        # Convert to JSON once
        message_json = json.dumps(message)
        
        # Send to each subscribed client
        disconnected_clients = []
        for client_id, subscriptions in self.subscriptions.items():
            if event_type in subscriptions:
                websocket = self.active_connections.get(client_id)
                if websocket:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        logger.warning(f"Failed to send to client {client_id}: {e}")
                        disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)