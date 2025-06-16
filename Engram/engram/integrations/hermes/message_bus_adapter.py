#!/usr/bin/env python3
"""
Hermes Message Bus Adapter for Engram

This module provides integration between Engram and Hermes's message bus service,
enabling asynchronous communication between Tekton components.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.integrations.hermes.message_bus")

# Import Hermes message bus client
try:
    from hermes.core.message_bus import MessageBus, MessageHandler, Message
    HAS_HERMES_MESSAGE_BUS = True
except ImportError:
    logger.warning("Hermes message bus not found, using fallback implementation")
    HAS_HERMES_MESSAGE_BUS = False


class MessageBusAdapter:
    """
    Message bus adapter for Engram using Hermes's message bus service.
    
    This class provides asynchronous communication capabilities between
    Engram instances and other Tekton components.
    """
    
    def __init__(self, client_id: str = "default"):
        """
        Initialize the message bus adapter.
        
        Args:
            client_id: Unique identifier for this client
        """
        self.client_id = client_id
        
        # Initialize message bus client if available
        self.hermes_available = HAS_HERMES_MESSAGE_BUS
        self.message_bus = None
        
        if self.hermes_available:
            try:
                # Initialize the MessageBus
                self.message_bus = MessageBus(
                    component_id=f"engram.{client_id}",
                    description=f"Engram memory service ({client_id})"
                )
                logger.info(f"Initialized Hermes message bus client for Engram ({client_id})")
            except Exception as e:
                logger.error(f"Error initializing Hermes message bus: {e}")
                self.hermes_available = False
        
        # Initialize fallback message storage
        if not self.hermes_available:
            logger.info(f"Using fallback in-memory message queue for client {client_id}")
            self.fallback_queue = asyncio.Queue()
            self.fallback_handlers = {}
            self.fallback_task = None
    
    async def start(self) -> bool:
        """
        Start the message bus service.
        
        Returns:
            Boolean indicating success
        """
        if self.hermes_available:
            try:
                # Start the message bus client
                await self.message_bus.connect()
                logger.info(f"Started Hermes message bus client for {self.client_id}")
                return True
            except Exception as e:
                logger.error(f"Error starting Hermes message bus: {e}")
                self.hermes_available = False
        
        # Start fallback message processor
        if not self.hermes_available:
            try:
                self.fallback_task = asyncio.create_task(self._process_fallback_messages())
                logger.info("Started fallback message processor")
                return True
            except Exception as e:
                logger.error(f"Error starting fallback message processor: {e}")
                return False
    
    async def publish(self, 
                     topic: str, 
                     message: Union[str, Dict[str, Any]],
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a message to a topic.
        
        Args:
            topic: The topic to publish to
            message: The message content (string or dict)
            metadata: Optional metadata for the message
            
        Returns:
            Boolean indicating success
        """
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        timestamp = datetime.now().isoformat()
        metadata["timestamp"] = timestamp
        metadata["source"] = f"engram.{self.client_id}"
        
        # Convert message to string if it's a dict
        if isinstance(message, dict):
            try:
                message_str = json.dumps(message)
            except Exception as e:
                logger.error(f"Error serializing message: {e}")
                message_str = str(message)
        else:
            message_str = str(message)
        
        # Publish via Hermes if available
        if self.hermes_available:
            try:
                # Create a message object
                msg = Message(
                    topic=topic,
                    content=message_str,
                    metadata=metadata
                )
                
                # Publish the message
                result = await self.message_bus.publish(msg)
                
                logger.debug(f"Published message to topic {topic}")
                return result
            except Exception as e:
                logger.error(f"Error publishing message to Hermes: {e}")
                # Fallback to local implementation
        
        # Use fallback message queue
        try:
            # Create a simple message structure
            fallback_msg = {
                "topic": topic,
                "content": message_str,
                "metadata": metadata,
                "id": f"{topic}-{int(time.time())}-{hash(message_str) % 10000}"
            }
            
            # Put in fallback queue
            await self.fallback_queue.put(fallback_msg)
            
            logger.debug(f"Published message to fallback queue topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Error publishing to fallback queue: {e}")
            return False
    
    async def subscribe(self, 
                       topic: str, 
                       handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> bool:
        """
        Subscribe to a topic and register a handler.
        
        Args:
            topic: The topic to subscribe to
            handler: Async callback function to handle received messages
            
        Returns:
            Boolean indicating success
        """
        # Subscribe via Hermes if available
        if self.hermes_available:
            try:
                # Create a message handler
                async def message_handler(message: Message) -> None:
                    try:
                        # Extract the message content
                        msg_data = {
                            "topic": message.topic,
                            "content": message.content,
                            "metadata": message.metadata,
                            "id": message.id
                        }
                        
                        # Call the user's handler
                        await handler(msg_data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
                
                # Register the handler with Hermes
                await self.message_bus.subscribe(
                    topic=topic,
                    handler=MessageHandler(callback=message_handler)
                )
                
                logger.info(f"Subscribed to topic {topic}")
                return True
            except Exception as e:
                logger.error(f"Error subscribing to Hermes topic: {e}")
                # Fallback to local implementation
        
        # Use fallback subscription
        try:
            # Store the handler in the fallback handlers
            if topic not in self.fallback_handlers:
                self.fallback_handlers[topic] = []
                
            self.fallback_handlers[topic].append(handler)
            
            logger.info(f"Subscribed to fallback topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Error subscribing to fallback topic: {e}")
            return False
    
    async def unsubscribe(self, topic: str, handler: Optional[Callable] = None) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: The topic to unsubscribe from
            handler: Specific handler to unsubscribe, or None to unsubscribe all
            
        Returns:
            Boolean indicating success
        """
        # Unsubscribe via Hermes if available
        if self.hermes_available:
            try:
                # Unsubscribe from the topic
                await self.message_bus.unsubscribe(topic)
                
                logger.info(f"Unsubscribed from topic {topic}")
                return True
            except Exception as e:
                logger.error(f"Error unsubscribing from Hermes topic: {e}")
                # Fallback to local implementation
        
        # Use fallback unsubscription
        try:
            if topic in self.fallback_handlers:
                if handler is None:
                    # Remove all handlers for this topic
                    self.fallback_handlers[topic] = []
                else:
                    # Remove specific handler
                    self.fallback_handlers[topic] = [
                        h for h in self.fallback_handlers[topic] if h != handler
                    ]
                
                logger.info(f"Unsubscribed from fallback topic {topic}")
                return True
            else:
                logger.warning(f"No handlers found for topic {topic}")
                return False
        except Exception as e:
            logger.error(f"Error unsubscribing from fallback topic: {e}")
            return False
    
    async def _process_fallback_messages(self) -> None:
        """Process messages in the fallback queue."""
        try:
            while True:
                # Get the next message from the queue
                message = await self.fallback_queue.get()
                
                # Get the topic
                topic = message["topic"]
                
                # Find handlers for this topic
                handlers = self.fallback_handlers.get(topic, [])
                
                # Call each handler
                for handler in handlers:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Error in fallback message handler: {e}")
                
                # Mark task as done
                self.fallback_queue.task_done()
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            logger.info("Fallback message processor was cancelled")
        except Exception as e:
            # Unexpected error
            logger.error(f"Error in fallback message processor: {e}")
            # Restart the task
            await asyncio.sleep(1)
            self.fallback_task = asyncio.create_task(self._process_fallback_messages())
    
    async def close(self) -> None:
        """Close connections and clean up resources."""
        if self.hermes_available and self.message_bus:
            try:
                await self.message_bus.disconnect()
                logger.debug("Closed Hermes message bus connection")
            except Exception as e:
                logger.error(f"Error closing Hermes message bus: {e}")
                
        # Clean up fallback resources
        if self.fallback_task and not self.fallback_task.done():
            try:
                self.fallback_task.cancel()
                await asyncio.wait_for(self.fallback_task, timeout=1.0)
            except Exception as e:
                logger.error(f"Error cancelling fallback task: {e}")


# For integration testing
async def main():
    """Main function for testing the message bus adapter."""
    # Initialize the message bus adapter
    adapter = MessageBusAdapter(client_id="test")
    
    # Start the adapter
    await adapter.start()
    
    # Define a message handler
    async def handle_message(message):
        print(f"Received message on topic {message['topic']}:")
        print(f"Content: {message['content']}")
        print(f"Metadata: {message['metadata']}")
        print()
    
    # Subscribe to a topic
    await adapter.subscribe("test.topic", handle_message)
    
    # Publish a message
    await adapter.publish(
        topic="test.topic",
        message="Hello, world!",
        metadata={"priority": "high"}
    )
    
    # Wait a moment for the message to be processed
    await asyncio.sleep(1)
    
    # Publish a JSON message
    await adapter.publish(
        topic="test.topic",
        message={"greeting": "Hello", "target": "world"},
        metadata={"format": "json"}
    )
    
    # Wait a moment for the message to be processed
    await asyncio.sleep(1)
    
    # Close the adapter
    await adapter.close()


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())