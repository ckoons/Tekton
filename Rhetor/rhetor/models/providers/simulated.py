"""
Simulated provider implementation for Rhetor.

This module provides a simulated LLM provider for testing and when no API keys are available.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from .base import LLMProvider

logger = logging.getLogger(__name__)

class SimulatedProvider(LLMProvider):
    """Simulated provider for testing and fallback"""
    
    def __init__(self):
        """Initialize the simulated provider"""
        super().__init__("simulated", "Simulated LLM")
        self.default_model = "simulated-standard"
        self.available = True
        self.initialized = True
        
    async def _initialize(self) -> bool:
        """
        Initialize the simulated provider - always succeeds.
        
        Returns:
            True always
        """
        return True
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get available simulated models.
        
        Returns:
            List of dictionaries with model info
        """
        return [
            {"id": "simulated-fast", "name": "Fast Simulation"},
            {"id": "simulated-standard", "name": "Standard Simulation"},
            {"id": "simulated-advanced", "name": "Advanced Simulation"}
        ]
    
    async def complete(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a message with the simulated provider.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        model = model or self.default_model
        
        # If streaming is requested, just return a placeholder
        if streaming:
            return {
                "message": "",
                "model": model,
                "provider": "simulated",
                "finished": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Simulate processing time based on model
        if model == "simulated-fast":
            await asyncio.sleep(0.5)
        elif model == "simulated-advanced":
            await asyncio.sleep(2.0)
        else:  # standard
            await asyncio.sleep(1.0)
        
        # Generate a response that includes the original message and prompt info
        response = f"I received your message: \"{message}\". "
        response += "This is a simulated response as no real LLM is available. "
        response += "Please configure Rhetor with valid API keys for Anthropic, OpenAI, "
        response += "or ensure Ollama is running for local LLM access."
        
        # Add context from system prompt if provided
        if system_prompt:
            prompt_preview = system_prompt[:50] + "..." if len(system_prompt) > 50 else system_prompt
            response += f"\n\nThe system prompt was: \"{prompt_preview}\""
        
        # Add model-specific responses
        if model == "simulated-advanced":
            response += "\n\nAs the advanced simulation model, I would typically provide more detailed and nuanced responses with better reasoning capabilities."
        elif model == "simulated-fast":
            response += "\n\nAs the fast simulation model, I would typically provide quicker but potentially less detailed responses."
        
        return {
            "message": response,
            "model": model,
            "provider": "simulated",
            "finished": True,
            "simulated": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the simulated provider.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            options: Additional options for the LLM
            
        Yields:
            Completion chunks as they are generated
        """
        model = model or self.default_model
        
        # Generate the full response first
        response = f"I received your message: \"{message}\". "
        response += "This is a simulated response as no real LLM is available. "
        response += "Please configure Rhetor with valid API keys for Anthropic, OpenAI, "
        response += "or ensure Ollama is running for local LLM access."
        
        # Add context from system prompt if provided
        if system_prompt:
            prompt_preview = system_prompt[:50] + "..." if len(system_prompt) > 50 else system_prompt
            response += f"\n\nThe system prompt was: \"{prompt_preview}\""
        
        # Add model-specific responses
        if model == "simulated-advanced":
            response += "\n\nAs the advanced simulation model, I would typically provide more detailed and nuanced responses with better reasoning capabilities."
        elif model == "simulated-fast":
            response += "\n\nAs the fast simulation model, I would typically provide quicker but potentially less detailed responses."
        
        # Stream the response with different delay based on model
        chunk_size = 5  # Characters per chunk for standard model
        delay = 0.05  # Seconds per chunk for standard model
        
        if model == "simulated-fast":
            chunk_size = 10
            delay = 0.02
        elif model == "simulated-advanced":
            chunk_size = 3
            delay = 0.08
        
        # Break the response into chunks and yield with delays
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i+chunk_size]
            yield chunk
            await asyncio.sleep(delay)
    
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a chat conversation with the simulated provider.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        model = model or self.default_model
        
        # If streaming is requested, just return a placeholder
        if streaming:
            return {
                "message": "",
                "model": model,
                "provider": "simulated",
                "finished": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Simulate processing time based on model
        if model == "simulated-fast":
            await asyncio.sleep(0.5)
        elif model == "simulated-advanced":
            await asyncio.sleep(2.0)
        else:  # standard
            await asyncio.sleep(1.0)
        
        # Extract the last user message
        last_user_message = "No message found"
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        # Generate a response
        response = f"I received your message: \"{last_user_message}\". "
        response += f"I see a conversation with {len(messages)} messages. "
        response += "This is a simulated chat response as no real LLM is available. "
        
        # Add context from system prompt if provided
        if system_prompt:
            prompt_preview = system_prompt[:50] + "..." if len(system_prompt) > 50 else system_prompt
            response += f"\n\nThe system prompt was: \"{prompt_preview}\""
        
        # Add model-specific responses
        if model == "simulated-advanced":
            response += "\n\nAs the advanced simulation model, I would typically maintain better context across a conversation thread."
        elif model == "simulated-fast":
            response += "\n\nAs the fast simulation model, I would typically provide quicker responses with less context retention."
        
        return {
            "message": response,
            "model": model,
            "provider": "simulated",
            "finished": True,
            "simulated": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion from the simulated provider.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            options: Additional options for the LLM
            
        Yields:
            Completion chunks as they are generated
        """
        model = model or self.default_model
        
        # Extract the last user message
        last_user_message = "No message found"
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        
        # Generate the full response first
        response = f"I received your message: \"{last_user_message}\". "
        response += f"I see a conversation with {len(messages)} messages. "
        response += "This is a simulated chat response as no real LLM is available. "
        
        # Add context from system prompt if provided
        if system_prompt:
            prompt_preview = system_prompt[:50] + "..." if len(system_prompt) > 50 else system_prompt
            response += f"\n\nThe system prompt was: \"{prompt_preview}\""
        
        # Add model-specific responses
        if model == "simulated-advanced":
            response += "\n\nAs the advanced simulation model, I would typically maintain better context across a conversation thread."
        elif model == "simulated-fast":
            response += "\n\nAs the fast simulation model, I would typically provide quicker responses with less context retention."
        
        # Stream the response with different delay based on model
        chunk_size = 5  # Characters per chunk for standard model
        delay = 0.05  # Seconds per chunk for standard model
        
        if model == "simulated-fast":
            chunk_size = 10
            delay = 0.02
        elif model == "simulated-advanced":
            chunk_size = 3
            delay = 0.08
        
        # Break the response into chunks and yield with delays
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i+chunk_size]
            yield chunk
            await asyncio.sleep(delay)