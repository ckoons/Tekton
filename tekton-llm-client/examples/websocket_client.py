#!/usr/bin/env python3
"""
WebSocket client example for Tekton LLM Client.
"""

import os
from shared.env import TektonEnviron
import sys
import asyncio
import logging
from typing import Dict, Any

# Add the package to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tekton_llm_client import TektonLLMWebSocketClient
from tekton_llm_client.models import StreamingChunk
from tekton_llm_client.exceptions import TektonLLMError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ws-example")

async def websocket_example():
    """WebSocket client example."""
    # Define event handlers
    def on_message(message):
        logger.info(f"Message received: {message}")
    
    def on_error(error):
        logger.error(f"WebSocket error: {error}")
    
    def on_close():
        logger.info("WebSocket connection closed")
    
    # Initialize the WebSocket client
    client = TektonLLMWebSocketClient(
        component_id="ws-example-client",
        rhetor_url=TektonEnviron.get("RHETOR_URL", "http://localhost:8003"),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    try:
        # Connect to the server
        logger.info("Connecting to WebSocket server...")
        connected = await client.connect()
        
        if not connected:
            logger.error("Failed to connect to WebSocket server")
            return
            
        logger.info("Connected successfully")
        
        # Define callback for streaming
        def handle_chunk(chunk: StreamingChunk):
            print(chunk.chunk, end="", flush=True)
            if chunk.done:
                print("\n--- Streaming complete ---")
            if chunk.error:
                print(f"\nError: {chunk.error}")
        
        # Generate a response
        logger.info("Generating response...")
        print("Response: ", end="", flush=True)
        
        request_id = await client.generate(
            prompt="Write a short poem about programming.",
            context_id="poetry",
            system_prompt="You are a creative assistant that writes poetry.",
            callback=handle_chunk
        )
        
        logger.info(f"Request ID: {request_id}")
        
        # Wait for a bit to allow streaming to complete
        await asyncio.sleep(5)
        
        # Chat example
        logger.info("\nGenerating chat response...")
        print("\nChat response: ", end="", flush=True)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Who are you?"},
            {"role": "assistant", "content": "I'm an AI assistant. How can I help you today?"},
            {"role": "user", "content": "What's your favorite programming language?"}
        ]
        
        chat_request_id = await client.chat_stream(
            messages=messages,
            callback=handle_chunk,
            context_id="chat"
        )
        
        # Wait for streaming to complete
        await asyncio.sleep(5)
        
        # Cancellation example (uncomment to test)
        """
        logger.info("\nCancellation example...")
        cancel_request_id = await client.generate(
            prompt="Write a very long essay about artificial intelligence.",
            context_id="cancellation-test",
            callback=handle_chunk
        )
        
        # Wait a bit and then cancel
        await asyncio.sleep(2)
        logger.info(f"Cancelling request {cancel_request_id}...")
        cancelled = await client.cancel(cancel_request_id)
        logger.info(f"Cancellation successful: {cancelled}")
        """
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Disconnect
        logger.info("Disconnecting...")
        await client.disconnect()
        logger.info("Disconnected")

if __name__ == "__main__":
    asyncio.run(websocket_example())