#!/usr/bin/env python3
"""
Migration example showing how to replace a custom LLM adapter with the Tekton LLM Client.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional

# Add the package to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("migration-example")

#
# BEFORE: Custom LLM Adapter Implementation
#

class CustomLLMAdapter:
    """Example of a custom LLM adapter that would be replaced."""
    
    def __init__(self, api_key=None, model=None):
        """Initialize the adapter."""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model or "claude-3-haiku-20240307"
        self.base_url = "https://api.anthropic.com/v1"
        
        logger.info(f"Initialized CustomLLMAdapter with model: {self.model}")
    
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the LLM."""
        logger.info(f"Generating text with prompt: {prompt[:30]}...")
        
        # In a real implementation, this would make an API call
        # For this example, we'll just simulate a response
        await asyncio.sleep(1)  # Simulate API call
        
        return f"This is a simulated response to: '{prompt[:20]}...'"
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a chat response."""
        logger.info(f"Generating chat response with {len(messages)} messages")
        
        # Simulate API call
        await asyncio.sleep(1)
        
        last_message = messages[-1]["content"] if messages else ""
        return f"This is a simulated chat response to: '{last_message[:20]}...'"

#
# AFTER: Using Tekton LLM Client
#

from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import Message, MessageRole
from tekton_llm_client.exceptions import TektonLLMError

class MigratedComponent:
    """Example of a component that has migrated to the Tekton LLM Client."""
    
    def __init__(self):
        """Initialize the component."""
        self.llm_client = TektonLLMClient(
            component_id="migrated-component",
            rhetor_url=os.environ.get("RHETOR_URL", "http://localhost:8003"),
            provider_id="anthropic",
            model_id="claude-3-haiku-20240307"
        )
        
        logger.info("Initialized MigratedComponent with TektonLLMClient")
    
    async def initialize(self):
        """Initialize the component and its dependencies."""
        await self.llm_client.initialize()
    
    async def shutdown(self):
        """Shut down the component and its dependencies."""
        await self.llm_client.shutdown()
    
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the LLM."""
        logger.info(f"Generating text with prompt: {prompt[:30]}...")
        
        try:
            response = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )
            return response.content
        except TektonLLMError as e:
            logger.error(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate a chat response."""
        logger.info(f"Generating chat response with {len(messages)} messages")
        
        try:
            response = await self.llm_client.generate_chat_response(messages=messages)
            return response.content
        except TektonLLMError as e:
            logger.error(f"Error generating chat response: {e}")
            return f"Error: {str(e)}"

async def demonstrate_before():
    """Demonstrate the before implementation."""
    logger.info("=== BEFORE: Using Custom LLM Adapter ===")
    
    adapter = CustomLLMAdapter()
    
    # Generate text
    text_response = await adapter.generate_text(
        prompt="What is the capital of France?",
        system_prompt="You are a helpful assistant."
    )
    logger.info(f"Text response: {text_response}")
    
    # Generate chat response
    chat_response = await adapter.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
        {"role": "user", "content": "What's the weather like in Paris?"}
    ])
    logger.info(f"Chat response: {chat_response}")

async def demonstrate_after():
    """Demonstrate the after implementation."""
    logger.info("\n=== AFTER: Using Tekton LLM Client ===")
    
    component = MigratedComponent()
    await component.initialize()
    
    try:
        # Generate text
        text_response = await component.generate_text(
            prompt="What is the capital of France?",
            system_prompt="You are a helpful assistant."
        )
        logger.info(f"Text response: {text_response}")
        
        # Generate chat response
        chat_response = await component.chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
            {"role": "user", "content": "What's the weather like in Paris?"}
        ])
        logger.info(f"Chat response: {chat_response}")
    finally:
        await component.shutdown()

async def main():
    """Run the migration example."""
    await demonstrate_before()
    await demonstrate_after()

if __name__ == "__main__":
    asyncio.run(main())