"""
Budget WebSocket Server

This module provides real-time budget updates via WebSocket connections.
It includes a connection manager, event handlers, and message schemas.
"""

import os
import sys
import json
import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import budget models
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType,
    Budget, BudgetPolicy, BudgetAllocation, Alert
)

# WebSocket Message Types
class MessageType(str, Enum):
    """
    Types of messages that can be sent through WebSockets.
    """
    BUDGET_UPDATE = "budget_update"           # Budget status update
    ALLOCATION_UPDATE = "allocation_update"   # Allocation status update
    POLICY_UPDATE = "policy_update"           # Policy created or updated
    ALERT = "alert"                           # Budget alert
    PRICE_UPDATE = "price_update"             # Price information updated
    SUBSCRIPTION = "subscription"             # Client subscription request
    UNSUBSCRIPTION = "unsubscription"         # Client unsubscription request
    AUTHENTICATION = "authentication"         # Authentication message
    ERROR = "error"                           # Error message
    HEARTBEAT = "heartbeat"                   # Keep-alive heartbeat

# WebSocket Message Schema
class WebSocketMessage(BaseModel):
    """
    Schema for messages sent over WebSockets.
    """
    type: MessageType
    topic: str
    payload: Dict[str, Any]
    timestamp: str = None

class ConnectionManager:
    """
    WebSocket connection manager for real-time budget updates.
    Handles connections, disconnections, and message broadcasting.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.client_topics: Dict[WebSocket, List[str]] = {}
        self.authenticated_clients: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Background task for periodic updates
        self.background_task = None
    
    async def connect(self, websocket: WebSocket, topic: str = "budget_events"):
        """
        Connect a client to a topic.
        
        Args:
            websocket: The WebSocket connection
            topic: The topic to subscribe to
        """
        await websocket.accept()
        
        # Initialize client tracking
        if topic not in self.active_connections:
            self.active_connections[topic] = []
        self.active_connections[topic].append(websocket)
        
        if websocket not in self.client_topics:
            self.client_topics[websocket] = []
        self.client_topics[websocket].append(topic)
        
        debug_log.info("budget_websocket", f"New WebSocket connection: {topic}")
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            type=MessageType.BUDGET_UPDATE,
            topic=topic,
            payload={"message": "Connected to Budget WebSocket Server"},
            timestamp=datetime.now().isoformat()
        )
        await websocket.send_text(welcome_message.json())
    
    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a client from all topics.
        
        Args:
            websocket: The WebSocket connection to disconnect
        """
        # Remove from all topics
        if websocket in self.client_topics:
            for topic in self.client_topics[websocket]:
                if topic in self.active_connections and websocket in self.active_connections[topic]:
                    self.active_connections[topic].remove(websocket)
                    debug_log.info("budget_websocket", f"WebSocket disconnected from topic: {topic}")
            
            # Clean up client tracking
            del self.client_topics[websocket]
        
        # Remove authentication if present
        if websocket in self.authenticated_clients:
            del self.authenticated_clients[websocket]
    
    async def broadcast(self, message: WebSocketMessage):
        """
        Broadcast a message to all connected clients for a topic.
        
        Args:
            message: The message to broadcast
        """
        topic = message.topic
        if topic in self.active_connections:
            dead_connections = []
            
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_text(message.json())
                except Exception as e:
                    dead_connections.append(connection)
                    debug_log.error("budget_websocket", f"Error sending message: {str(e)}")
            
            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(dead)
    
    async def broadcast_raw(self, message: str, topic: str = "budget_events"):
        """
        Broadcast a raw string message to all connected clients for a topic.
        
        Args:
            message: The raw message to broadcast
            topic: The topic to broadcast to
        """
        if topic in self.active_connections:
            dead_connections = []
            
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    dead_connections.append(connection)
                    debug_log.error("budget_websocket", f"Error sending raw message: {str(e)}")
            
            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(dead)
    
    async def authenticate_client(self, websocket: WebSocket, auth_data: Dict[str, Any]):
        """
        Authenticate a WebSocket client.
        
        Args:
            websocket: The WebSocket connection
            auth_data: Authentication data
        
        Returns:
            bool: True if authentication succeeded, False otherwise
        """
        # Simple auth for now - could be enhanced with actual validation
        if "api_key" in auth_data:
            self.authenticated_clients[websocket] = {
                "api_key": auth_data["api_key"],
                "client_id": auth_data.get("client_id", "unknown"),
                "authenticated_at": datetime.now().isoformat()
            }
            return True
        return False
    
    async def subscribe_client(self, websocket: WebSocket, topic: str):
        """
        Subscribe a client to a topic.
        
        Args:
            websocket: The WebSocket connection
            topic: The topic to subscribe to
        """
        if topic not in self.active_connections:
            self.active_connections[topic] = []
        
        if websocket not in self.active_connections[topic]:
            self.active_connections[topic].append(websocket)
        
        if websocket not in self.client_topics:
            self.client_topics[websocket] = []
        
        if topic not in self.client_topics[websocket]:
            self.client_topics[websocket].append(topic)
        
        debug_log.info("budget_websocket", f"Client subscribed to topic: {topic}")
    
    async def unsubscribe_client(self, websocket: WebSocket, topic: str):
        """
        Unsubscribe a client from a topic.
        
        Args:
            websocket: The WebSocket connection
            topic: The topic to unsubscribe from
        """
        if topic in self.active_connections and websocket in self.active_connections[topic]:
            self.active_connections[topic].remove(websocket)
        
        if websocket in self.client_topics and topic in self.client_topics[websocket]:
            self.client_topics[websocket].remove(topic)
        
        debug_log.info("budget_websocket", f"Client unsubscribed from topic: {topic}")
    
    async def process_message(self, websocket: WebSocket, message_text: str):
        """
        Process an incoming WebSocket message.
        
        Args:
            websocket: The WebSocket connection
            message_text: The raw message text
            
        Returns:
            WebSocketMessage: The response message if any
        """
        try:
            # Parse message
            message_data = json.loads(message_text)
            message = WebSocketMessage(**message_data)
            
            # Handle different message types
            if message.type == MessageType.AUTHENTICATION:
                success = await self.authenticate_client(websocket, message.payload)
                return WebSocketMessage(
                    type=MessageType.AUTHENTICATION,
                    topic=message.topic,
                    payload={"success": success},
                    timestamp=datetime.now().isoformat()
                )
            
            elif message.type == MessageType.SUBSCRIPTION:
                topic = message.payload.get("topic", "budget_events")
                await self.subscribe_client(websocket, topic)
                return WebSocketMessage(
                    type=MessageType.SUBSCRIPTION,
                    topic=topic,
                    payload={"success": True, "topic": topic},
                    timestamp=datetime.now().isoformat()
                )
            
            elif message.type == MessageType.UNSUBSCRIPTION:
                topic = message.payload.get("topic", "budget_events")
                await self.unsubscribe_client(websocket, topic)
                return WebSocketMessage(
                    type=MessageType.UNSUBSCRIPTION,
                    topic=topic,
                    payload={"success": True, "topic": topic},
                    timestamp=datetime.now().isoformat()
                )
            
            elif message.type == MessageType.HEARTBEAT:
                return WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    topic=message.topic,
                    payload={"timestamp": datetime.now().isoformat()},
                    timestamp=datetime.now().isoformat()
                )
            
            # For other message types, we don't need to respond
            return None
            
        except Exception as e:
            debug_log.error("budget_websocket", f"Error processing message: {str(e)}")
            return WebSocketMessage(
                type=MessageType.ERROR,
                topic="error",
                payload={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    async def start_periodic_updates(self, engine, interval_seconds: int = 60):
        """
        Start periodic budget status updates.
        
        Args:
            engine: The budget engine to get updates from
            interval_seconds: How often to send updates
        """
        self.background_task = asyncio.create_task(self._periodic_updates(engine, interval_seconds))
    
    async def _periodic_updates(self, engine, interval_seconds: int):
        """
        Send periodic budget status updates to all clients.
        
        Args:
            engine: The budget engine to get updates from
            interval_seconds: How often to send updates
        """
        while True:
            try:
                # Get budget summaries for each period
                for period in [BudgetPeriod.DAILY, BudgetPeriod.WEEKLY, BudgetPeriod.MONTHLY]:
                    summaries = await engine.get_budget_summaries(period=period)
                    
                    # Create update message
                    message = WebSocketMessage(
                        type=MessageType.BUDGET_UPDATE,
                        topic=f"budget_update_{period}",
                        payload={
                            "period": period,
                            "summaries": [summary.dict() for summary in summaries]
                        },
                        timestamp=datetime.now().isoformat()
                    )
                    
                    # Broadcast to clients
                    await self.broadcast(message)
                
                # Check for alerts
                alerts = await engine.get_recent_alerts()
                if alerts:
                    alert_message = WebSocketMessage(
                        type=MessageType.ALERT,
                        topic="budget_alerts",
                        payload={
                            "alerts": [alert.dict() for alert in alerts]
                        },
                        timestamp=datetime.now().isoformat()
                    )
                    await self.broadcast(alert_message)
                
            except Exception as e:
                debug_log.error("budget_websocket", f"Error in periodic update: {str(e)}")
            
            # Wait for next update
            await asyncio.sleep(interval_seconds)
    
    def cleanup(self):
        """
        Stop all background tasks and clean up resources.
        """
        if self.background_task:
            self.background_task.cancel()

# Functions to add WebSocket routes to the FastAPI app
def add_websocket_routes(app: FastAPI, manager: ConnectionManager, engine):
    """
    Add WebSocket routes to the FastAPI app.
    
    Args:
        app: The FastAPI app
        manager: The WebSocket connection manager
        engine: The budget engine
    """
    
    @app.websocket("/ws/budget/updates")
    @log_function()
    async def budget_updates(websocket: WebSocket):
        """
        WebSocket endpoint for general budget updates.
        """
        await manager.connect(websocket, "budget_events")
        try:
            while True:
                data = await websocket.receive_text()
                response = await manager.process_message(websocket, data)
                if response:
                    await websocket.send_text(response.json())
        except WebSocketDisconnect:
            debug_log.info("budget_websocket", "Client disconnected normally")
        except Exception as e:
            debug_log.error("budget_websocket", f"WebSocket error: {str(e)}")
        finally:
            manager.disconnect(websocket)
    
    @app.websocket("/ws/budget/alerts")
    @log_function()
    async def budget_alerts(websocket: WebSocket):
        """
        WebSocket endpoint for budget alerts.
        """
        await manager.connect(websocket, "budget_alerts")
        try:
            while True:
                data = await websocket.receive_text()
                response = await manager.process_message(websocket, data)
                if response:
                    await websocket.send_text(response.json())
        except WebSocketDisconnect:
            debug_log.info("budget_websocket", "Client disconnected normally")
        except Exception as e:
            debug_log.error("budget_websocket", f"WebSocket error: {str(e)}")
        finally:
            manager.disconnect(websocket)
    
    @app.websocket("/ws/budget/allocations")
    @log_function()
    async def allocation_updates(websocket: WebSocket):
        """
        WebSocket endpoint for allocation updates.
        """
        await manager.connect(websocket, "allocation_updates")
        try:
            while True:
                data = await websocket.receive_text()
                response = await manager.process_message(websocket, data)
                if response:
                    await websocket.send_text(response.json())
        except WebSocketDisconnect:
            debug_log.info("budget_websocket", "Client disconnected normally")
        except Exception as e:
            debug_log.error("budget_websocket", f"WebSocket error: {str(e)}")
        finally:
            manager.disconnect(websocket)
    
    @app.websocket("/ws/budget/prices")
    @log_function()
    async def price_updates(websocket: WebSocket):
        """
        WebSocket endpoint for price updates.
        """
        await manager.connect(websocket, "price_updates")
        try:
            while True:
                data = await websocket.receive_text()
                response = await manager.process_message(websocket, data)
                if response:
                    await websocket.send_text(response.json())
        except WebSocketDisconnect:
            debug_log.info("budget_websocket", "Client disconnected normally")
        except Exception as e:
            debug_log.error("budget_websocket", f"WebSocket error: {str(e)}")
        finally:
            manager.disconnect(websocket)
    
    # Start periodic updates
    app.add_event_handler("startup", lambda: asyncio.create_task(manager.start_periodic_updates(engine)))
    app.add_event_handler("shutdown", manager.cleanup)

# Function to create WebSocket message
def create_ws_message(
    type: MessageType, 
    topic: str, 
    payload: Dict[str, Any]
) -> WebSocketMessage:
    """
    Create a WebSocket message.
    
    Args:
        type: The message type
        topic: The message topic
        payload: The message payload
        
    Returns:
        WebSocketMessage: The formatted message
    """
    return WebSocketMessage(
        type=type,
        topic=topic,
        payload=payload,
        timestamp=datetime.now().isoformat()
    )

# Event handlers for budget events - to be used by the budget engine
async def notify_budget_update(
    manager: ConnectionManager, 
    budget_id: str, 
    summary: Dict[str, Any]
):
    """
    Notify clients of a budget update.
    
    Args:
        manager: The WebSocket connection manager
        budget_id: The budget ID
        summary: The budget summary
    """
    message = create_ws_message(
        type=MessageType.BUDGET_UPDATE,
        topic="budget_events",
        payload={
            "budget_id": budget_id,
            "summary": summary
        }
    )
    await manager.broadcast(message)

async def notify_allocation_update(
    manager: ConnectionManager, 
    allocation_id: str, 
    allocation: Dict[str, Any]
):
    """
    Notify clients of an allocation update.
    
    Args:
        manager: The WebSocket connection manager
        allocation_id: The allocation ID
        allocation: The allocation data
    """
    message = create_ws_message(
        type=MessageType.ALLOCATION_UPDATE,
        topic="allocation_updates",
        payload={
            "allocation_id": allocation_id,
            "allocation": allocation
        }
    )
    await manager.broadcast(message)

async def notify_alert(
    manager: ConnectionManager, 
    alert: Dict[str, Any]
):
    """
    Notify clients of a budget alert.
    
    Args:
        manager: The WebSocket connection manager
        alert: The alert data
    """
    message = create_ws_message(
        type=MessageType.ALERT,
        topic="budget_alerts",
        payload=alert
    )
    await manager.broadcast(message)

async def notify_price_update(
    manager: ConnectionManager, 
    provider: str, 
    model: str, 
    update: Dict[str, Any]
):
    """
    Notify clients of a price update.
    
    Args:
        manager: The WebSocket connection manager
        provider: The provider name
        model: The model name
        update: The price update data
    """
    message = create_ws_message(
        type=MessageType.PRICE_UPDATE,
        topic="price_updates",
        payload={
            "provider": provider,
            "model": model,
            "update": update
        }
    )
    await manager.broadcast(message)