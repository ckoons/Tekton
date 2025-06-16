#!/usr/bin/env python3
"""
Hermes Full Integration Example for Engram

This script demonstrates how to use all Hermes integration features with Engram,
including memory service, message bus, and logging system.
"""

import asyncio
import os
import time
from typing import Dict, Any

# Import Hermes integration components
from engram.integrations.hermes.memory_adapter import HermesMemoryService
from engram.integrations.hermes.message_bus_adapter import MessageBusAdapter
from engram.integrations.hermes.logging_adapter import LoggingAdapter


async def demonstrate_full_integration():
    """Demonstrate the full Hermes integration with Engram."""
    print("\n=== Demonstrating Full Hermes Integration with Engram ===\n")
    
    # Initialize the client ID
    client_id = f"demo-{int(time.time()) % 10000}"
    print(f"Using client ID: {client_id}")
    
    # Initialize the logging adapter
    logging = LoggingAdapter(client_id=client_id)
    logging.info("Starting Hermes integration demo", 
                component="demo", 
                context={"phase": "initialization"})
    
    # Initialize the memory service
    memory = HermesMemoryService(client_id=client_id)
    logging.info(f"Memory service initialized with Hermes {'available' if memory.hermes_available else 'unavailable'}")
    
    # Initialize the message bus
    message_bus = MessageBusAdapter(client_id=client_id)
    await message_bus.start()
    logging.info(f"Message bus initialized with Hermes {'available' if message_bus.hermes_available else 'unavailable'}")
    
    # Define a message handler
    async def handle_message(message):
        content = message.get("content", "")
        logging.info(f"Received message: {content}", 
                    component="message_handler",
                    context={"topic": message.get("topic", "unknown")})
        
        # Store the message in memory
        await memory.add(
            content=f"Received message: {content}",
            namespace="conversations",
            metadata={"source": "message_bus", "topic": message.get("topic", "unknown")}
        )
        
        print(f"Received message on topic {message.get('topic', 'unknown')}: {content}")
    
    # Subscribe to a topic
    topic = f"engram.demo.{client_id}"
    await message_bus.subscribe(topic, handle_message)
    logging.info(f"Subscribed to topic: {topic}")
    
    # Add some memories
    logging.info("Adding memories")
    
    await memory.add(
        content="Hermes is the messenger of the gods in Greek mythology.",
        namespace="longterm",
        metadata={"category": "mythology"}
    )
    
    await memory.add(
        content="Hermes provides centralized services like databases, messaging, and logging.",
        namespace="longterm",
        metadata={"category": "technology"}
    )
    
    # Create a test compartment
    compartment_id = await memory.create_compartment(
        name="Integration Demo",
        description="Testing the full Hermes integration"
    )
    
    if compartment_id:
        logging.info(f"Created compartment: {compartment_id}")
        
        # Activate the compartment
        await memory.activate_compartment(compartment_id)
        
        # Add memory to the compartment
        await memory.add(
            content="This memory is stored in a specific compartment.",
            namespace=f"compartment-{compartment_id}",
            metadata={"test": True}
        )
    
    # Publish a message
    logging.info("Publishing message")
    await message_bus.publish(
        topic=topic,
        message="Hello from the integration demo!",
        metadata={"demo": True}
    )
    
    # Wait for the message to be processed
    await asyncio.sleep(1)
    
    # Search for memories
    logging.info("Searching memories")
    results = await memory.search(query="Hermes", limit=5)
    
    print(f"\nFound {results['count']} results:")
    for i, result in enumerate(results["results"]):
        print(f"{i+1}. {result['content']}")
        print(f"   Relevance: {result['relevance']:.4f}")
        print()
    
    # Get relevant context
    context = await memory.get_relevant_context(query="integration")
    print("\nContext for 'integration':")
    print(context)
    
    # Publish a structured message
    logging.info("Publishing structured message")
    await message_bus.publish(
        topic=topic,
        message={
            "command": "status_update",
            "status": "complete",
            "results": {
                "memories_added": 3,
                "messages_sent": 2
            }
        }
    )
    
    # Wait for the message to be processed
    await asyncio.sleep(1)
    
    # Get recent logs
    logs = logging.get_logs(level="INFO", limit=5)
    
    print("\nRecent logs:")
    for log in logs[:5]:  # Show just the 5 most recent
        print(f"{log['timestamp']} - {log['level']} - {log['message']}")
    
    # Clean up
    logging.info("Cleaning up resources", component="demo", context={"phase": "shutdown"})
    await memory.close()
    await message_bus.close()
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(demonstrate_full_integration())