"""
Message Bus - Core functionality for inter-component messaging.

This module provides the main interface for message passing, publishing,
and subscribing to events across Tekton components.
"""

import logging
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Union, Callable, Set

from landmarks import architecture_decision, performance_boundary, integration_point

# Configure logger
logger = logging.getLogger(__name__)


@architecture_decision(
    title="Pub/Sub messaging pattern",
    rationale="Enable loose coupling between components with asynchronous event-driven communication",
    alternatives_considered=["Direct RPC calls", "REST webhooks", "Message queues (RabbitMQ/Kafka)"],
    impacts=["scalability", "complexity", "latency"],
    decided_by="team",
    date="2024-01-20"
)
@integration_point(
    title="Central message bus",
    target_component="All Tekton components",
    protocol="In-memory pub/sub (future: WebSocket)",
    data_flow="Components publish events -> MessageBus routes -> Subscribers receive"
)
class MessageBus:
    """
    Main interface for inter-component messaging.
    
    This class provides methods for publishing and subscribing to messages,
    enabling asynchronous communication between Tekton components.
    """
    
    def __init__(self, 
                host: str = "localhost",
                port: int = 5555,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the message bus.
        
        Args:
            host: Hostname for the message bus
            port: Port for the message bus
            config: Additional configuration options
        """
        self.host = host
        self.port = port
        self.config = config or {}
        
        # Dictionary to store topic subscriptions
        self.subscriptions: Dict[str, Set[Callable]] = {}
        
        # Message history for replay (optional, configurable size)
        self.history: Dict[str, List[Dict[str, Any]]] = {}
        self.history_size = self.config.get("history_size", 100)
        
        # Placeholder for connection
        self.connection = None
        
        logger.info(f"Message bus initialized at {host}:{port}")
    
    def connect(self) -> bool:
        """
        Connect to the message broker.
        
        Returns:
            True if connection successful
        """
        # TODO: Implement actual connection to message broker
        logger.info(f"Connecting to message broker at {self.host}:{self.port}")
        return True
    
    @performance_boundary(
        title="Message publication",
        sla="<10ms for local delivery",
        optimization_notes="In-memory routing, async delivery to subscribers",
        metrics={"avg_latency": "2ms", "p99_latency": "8ms"}
    )
    def publish(self, 
               topic: str, 
               message: Any,
               headers: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            message: Message to publish (will be serialized)
            headers: Optional message headers
            
        Returns:
            True if publication successful
        """
        # Create message envelope
        headers = headers or {}
        headers["timestamp"] = time.time()
        headers["topic"] = topic
        
        envelope = {
            "headers": headers,
            "payload": message
        }
        
        # Serialize to JSON
        try:
            message_json = json.dumps(envelope)
        except TypeError:
            logger.error(f"Cannot serialize message for topic {topic}")
            return False
        
        # TODO: Implement actual message publication
        logger.info(f"Publishing message to topic {topic}")
        
        # Store in history if enabled
        if self.history_size > 0:
            if topic not in self.history:
                self.history[topic] = []
            
            self.history[topic].append(envelope)
            
            # Trim history if needed
            if len(self.history[topic]) > self.history_size:
                self.history[topic] = self.history[topic][-self.history_size:]
        
        # Deliver to local subscribers
        self._deliver_to_subscribers(topic, envelope)
        
        return True
    
    def subscribe(self,
                 topic: str,
                 callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to a topic.
        Automatically handles both sync and async callbacks.

        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received (sync or async)

        Returns:
            True if subscription successful
        """
        # Initialize topic if not exists
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        
        # Add callback
        self.subscriptions[topic].add(callback)
        
        logger.info(f"Subscribed to topic {topic}")
        return True
    
    def unsubscribe(self, 
                   topic: str, 
                   callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if unsubscription successful
        """
        if topic in self.subscriptions and callback in self.subscriptions[topic]:
            self.subscriptions[topic].remove(callback)
            logger.info(f"Unsubscribed from topic {topic}")
            return True
            
        logger.warning(f"No subscription found for topic {topic}")
        return False
    
    def _deliver_to_subscribers(self, topic: str, message: Dict[str, Any]) -> None:
        """
        Deliver a message to all subscribers of a topic.
        Handles both sync and async callbacks properly.

        Args:
            topic: Topic the message was published to
            message: Message envelope
        """
        import asyncio
        import inspect

        # Check for exact topic match
        if topic in self.subscriptions:
            for callback in self.subscriptions[topic]:
                try:
                    # Check if callback is async and handle appropriately
                    if inspect.iscoroutinefunction(callback):
                        # Schedule async callback as a task to avoid blocking
                        # Use create_task to ensure it runs even if we're not in async context
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.create_task(callback(message))
                            else:
                                # If no loop is running, run it synchronously (fallback)
                                asyncio.run(callback(message))
                        except RuntimeError:
                            # Fallback if no event loop available
                            logger.warning(f"Cannot execute async callback for topic {topic}, no event loop available")
                    else:
                        # Sync callback - call directly
                        callback(message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback for topic {topic}: {e}")
                    # Continue processing other callbacks even if one fails
        
        # Check for wildcard subscriptions
        # For example, "events.*" would match "events.user" and "events.system"
        for subscription_topic, callbacks in self.subscriptions.items():
            if "*" in subscription_topic:
                pattern = subscription_topic.replace("*", "")
                if topic.startswith(pattern) or topic.endswith(pattern):
                    for callback in callbacks:
                        try:
                            # Check if callback is async and handle appropriately
                            if inspect.iscoroutinefunction(callback):
                                # Schedule async callback as a task to avoid blocking
                                try:
                                    loop = asyncio.get_event_loop()
                                    if loop.is_running():
                                        asyncio.create_task(callback(message))
                                    else:
                                        # If no loop is running, run it synchronously (fallback)
                                        asyncio.run(callback(message))
                                except RuntimeError:
                                    # Fallback if no event loop available
                                    logger.warning(f"Cannot execute async callback for wildcard topic {topic}, no event loop available")
                            else:
                                # Sync callback - call directly
                                callback(message)
                        except Exception as e:
                            logger.error(f"Error in wildcard subscriber callback for topic {topic}: {e}")
    
    def get_history(self, 
                   topic: str, 
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get message history for a topic.
        
        Args:
            topic: Topic to get history for
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        if topic not in self.history:
            return []
            
        if limit is None or limit >= len(self.history[topic]):
            return self.history[topic]
        else:
            return self.history[topic][-limit:]
    
    def close(self) -> None:
        """
        Close the connection to the message broker.
        """
        logger.info("Closing message bus connection")
        # TODO: Implement actual connection closing
        
    async def create_channel(self, channel_name: str, description: str = "") -> bool:
        """
        Create a new channel for message exchange.
        
        Args:
            channel_name: Name of the channel to create
            description: Optional description of the channel
            
        Returns:
            True if channel creation successful
        """
        logger.info(f"Creating channel: {channel_name} - {description}")
        
        # For now, this is a stub implementation that just logs the request
        # and returns success. In a real implementation, this would create
        # the channel in the message broker.
        
        # Add a subscription entry for this channel if it doesn't exist
        if channel_name not in self.subscriptions:
            self.subscriptions[channel_name] = set()
            
        return True
        
    async def subscribe_async(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to a topic (async version).
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received
            
        Returns:
            True if subscription successful
        """
        # This is the async version of the subscribe method
        # Avoid recursion by implementing directly
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        
        # Add callback
        self.subscriptions[topic].add(callback)
        
        logger.info(f"Subscribed to topic {topic} (async)")
        return True
        
    async def publish_async(self, 
                    topic: str, 
                    message: Any,
                    headers: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a message to a topic (async version).
        
        Args:
            topic: Topic to publish to
            message: Message to publish (will be serialized)
            headers: Optional message headers
            
        Returns:
            True if publication successful
        """
        # Create message envelope
        headers = headers or {}
        headers["timestamp"] = time.time()
        headers["topic"] = topic
        
        envelope = {
            "headers": headers,
            "payload": message
        }
        
        # Serialize to JSON
        try:
            message_json = json.dumps(envelope)
        except TypeError:
            logger.error(f"Cannot serialize message for topic {topic}")
            return False
        
        # TODO: Implement actual message publication
        logger.info(f"Publishing message to topic {topic} (async)")
        
        # Store in history if enabled
        if self.history_size > 0:
            if topic not in self.history:
                self.history[topic] = []
            
            self.history[topic].append(envelope)
            
            # Trim history if needed
            if len(self.history[topic]) > self.history_size:
                self.history[topic] = self.history[topic][-self.history_size:]
        
        # Deliver to local subscribers
        await self._deliver_to_subscribers_async(topic, envelope)
        
        return True
        
    async def _deliver_to_subscribers_async(self, topic: str, message: Dict[str, Any]) -> None:
        """
        Deliver a message to all subscribers of a topic (async version).
        
        Args:
            topic: Topic the message was published to
            message: Message envelope
        """
        # Check for exact topic match
        if topic in self.subscriptions:
            for callback in self.subscriptions[topic]:
                try:
                    # Check if callback is a coroutine function
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        # Call synchronously for regular functions
                        callback(message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback for topic {topic}: {e}")
        
        # Check for wildcard subscriptions
        for subscription_topic, callbacks in self.subscriptions.items():
            if "*" in subscription_topic:
                pattern = subscription_topic.replace("*", "")
                if topic.startswith(pattern) or topic.endswith(pattern):
                    for callback in callbacks:
                        try:
                            # Check if callback is a coroutine function
                            if asyncio.iscoroutinefunction(callback):
                                await callback(message)
                            else:
                                # Call synchronously for regular functions
                                callback(message)
                        except Exception as e:
                            logger.error(f"Error in wildcard subscriber callback for topic {topic}: {e}")