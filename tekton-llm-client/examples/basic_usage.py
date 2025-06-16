#!/usr/bin/env python3
"""
Basic usage example for Tekton LLM Client.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add the package to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import Message, MessageRole, StreamingChunk
from tekton_llm_client.exceptions import TektonLLMError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("example")

async def basic_example():
    """Basic usage example."""
    # Initialize the client
    client = TektonLLMClient(
        component_id="example-client",
        rhetor_url=os.environ.get("RHETOR_URL", "http://localhost:8003")
    )
    
    try:
        # Initialize connection to Rhetor
        await client.initialize()
        
        # Generate text
        logger.info("Generating text...")
        response = await client.generate_text(
            prompt="What is the capital of France?",
            system_prompt="You are a helpful assistant that provides concise answers."
        )
        
        logger.info(f"Response: {response.content}")
        logger.info(f"Provider: {response.provider}, Model: {response.model}")
        
        # Generate chat response
        logger.info("\nGenerating chat response...")
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.USER, content="Hello! Who are you?"),
            Message(role=MessageRole.ASSISTANT, content="I'm an AI assistant. How can I help you today?"),
            Message(role=MessageRole.USER, content="Explain what makes a good API design in one paragraph.")
        ]
        
        chat_response = await client.generate_chat_response(messages=messages)
        logger.info(f"Chat response: {chat_response.content}")
        
        # Get available providers
        logger.info("\nGetting available providers...")
        providers = await client.get_providers()
        logger.info(f"Default provider: {providers.default_provider}")
        logger.info(f"Default model: {providers.default_model}")
        logger.info(f"Available providers: {', '.join(providers.providers.keys())}")
        
        # Streaming example
        logger.info("\nStreaming example...")
        print("Streaming response: ", end="", flush=True)
        
        async for chunk in client.generate_text(
            prompt="Write a haiku about programming.",
            system_prompt="You are a creative assistant that writes beautiful poetry.",
            streaming=True
        ):
            print(chunk.chunk, end="", flush=True)
            if chunk.error:
                print(f"\nError: {chunk.error}")
                break
        
        print("\n")
    except TektonLLMError as e:
        logger.error(f"LLM error: {e}")
    finally:
        # Clean up
        await client.shutdown()

async def streaming_with_callback():
    """Example with streaming and callback."""
    client = TektonLLMClient(component_id="example-client")
    await client.initialize()
    
    try:
        # Define callback
        def handle_chunk(chunk: StreamingChunk):
            print(chunk.chunk, end="", flush=True)
            if chunk.done:
                print("\n--- Streaming complete ---")
        
        print("Streaming with callback: ", end="", flush=True)
        
        # Stream with callback
        response = await client.generate_text(
            prompt="Write a short story about a robot learning to code.",
            system_prompt="You are a creative storyteller.",
            streaming=True,
            callback=handle_chunk
        )
        
    except TektonLLMError as e:
        logger.error(f"LLM error: {e}")
    finally:
        await client.shutdown()

async def main():
    """Run all examples."""
    await basic_example()
    # Uncomment to run streaming example with callback
    # await streaming_with_callback()

if __name__ == "__main__":
    asyncio.run(main())