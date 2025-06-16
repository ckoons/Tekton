"""
Local fallback adapter for when Rhetor is unavailable.
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from datetime import datetime

from .base import BaseAdapter
from ..models import Message, CompletionOptions

logger = logging.getLogger(__name__)

class LocalFallbackAdapter(BaseAdapter):
    """Local fallback adapter for when Rhetor is unavailable."""
    
    def __init__(self, component_id: str):
        """
        Initialize the local fallback adapter.
        
        Args:
            component_id: ID of the component using the adapter
        """
        self.component_id = component_id
        self.available = True
        
        logger.info(f"Initialized LocalFallbackAdapter for component '{component_id}'")
    
    async def initialize(self) -> bool:
        """
        Initialize the adapter.
        
        Returns:
            True (always available)
        """
        return True
    
    async def shutdown(self) -> None:
        """Shutdown the adapter and clean up resources."""
        pass
    
    def is_available(self) -> bool:
        """
        Check if the adapter is available.
        
        Returns:
            True (always available)
        """
        return True
    
    async def complete_chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        context_id: str,
        provider_id: str,
        model_id: Optional[str],
        options: CompletionOptions
    ) -> Dict[str, Any]:
        """
        Generate a simulated response for fallback purposes.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID that was requested
            model_id: Model ID that was requested
            options: Completion options
            
        Returns:
            Dictionary with simulated response
        """
        # Get the last user message
        last_message = messages[-1] if messages else None
        message_content = last_message.content if last_message else ""
        
        # Wait to simulate processing
        await asyncio.sleep(0.5)
        
        # Generate a simulated response
        timestamp = datetime.utcnow().isoformat()
        
        response = (
            f"This is a simulated response from the fallback adapter. The Rhetor LLM service "
            f"is currently unavailable. Your component '{self.component_id}' attempted to use "
            f"the '{provider_id}' provider with model '{model_id or 'default'}'.\n\n"
            f"Your message was: \"{message_content[:100]}{'...' if len(message_content) > 100 else ''}\"\n\n"
            f"To resolve this issue, please ensure that:\n"
            f"1. The Rhetor service is running on the configured URL\n"
            f"2. Network connectivity to Rhetor is available\n"
            f"3. Any authentication requirements are properly configured\n\n"
            f"This is a temporary fallback response. Please try again later."
        )
        
        return {
            "content": response,
            "model": "fallback",
            "provider": "fallback",
            "finish_reason": "fallback",
            "usage": {"prompt_tokens": 0, "completion_tokens": len(response) // 4, "total_tokens": len(response) // 4},
            "context_id": context_id,
            "timestamp": timestamp
        }
    
    async def stream_chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str],
        context_id: str,
        provider_id: str,
        model_id: Optional[str],
        options: CompletionOptions
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a simulated response for fallback purposes.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID that was requested
            model_id: Model ID that was requested
            options: Completion options
            
        Yields:
            Dictionaries with simulated response chunks
        """
        # Get the last user message
        last_message = messages[-1] if messages else None
        message_content = last_message.content if last_message else ""
        
        # Generate a simulated response
        response = (
            f"This is a simulated response from the fallback adapter. The Rhetor LLM service "
            f"is currently unavailable. Your component '{self.component_id}' attempted to use "
            f"the '{provider_id}' provider with model '{model_id or 'default'}'.\n\n"
            f"Your message was: \"{message_content[:100]}{'...' if len(message_content) > 100 else ''}\"\n\n"
            f"To resolve this issue, please ensure that:\n"
            f"1. The Rhetor service is running on the configured URL\n"
            f"2. Network connectivity to Rhetor is available\n"
            f"3. Any authentication requirements are properly configured\n\n"
            f"This is a temporary fallback response. Please try again later."
        )
        
        # Break into small chunks to simulate streaming
        chunk_size = 5  # Characters per chunk
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i+chunk_size]
            
            # Yield the chunk
            yield {
                "chunk": chunk,
                "context_id": context_id,
                "model": "fallback",
                "provider": "fallback",
                "timestamp": datetime.utcnow().isoformat(),
                "done": False
            }
            
            # Add a slight delay for realism
            await asyncio.sleep(0.05)
        
        # Yield the final chunk
        yield {
            "chunk": "",
            "context_id": context_id,
            "model": "fallback",
            "provider": "fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "done": True
        }
    
    async def get_providers(self) -> Dict[str, Any]:
        """
        Get a simulated list of providers.
        
        Returns:
            Dictionary with simulated provider information
        """
        return {
            "providers": {
                "fallback": {
                    "name": "Fallback Provider",
                    "available": True,
                    "models": [
                        {"id": "fallback", "name": "Fallback Model"}
                    ]
                }
            },
            "default_provider": "fallback",
            "default_model": "fallback"
        }
    
    async def get_provider_info(self, provider_id: str) -> Dict[str, Any]:
        """
        Get simulated information about a specific provider.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Dictionary with simulated provider information
        """
        return {
            "name": "Fallback Provider",
            "available": True,
            "models": [
                {"id": "fallback", "name": "Fallback Model"}
            ],
            "default_model": "fallback"
        }