"""
LLM adapter for Hermes.

This module provides a client for interacting with LLMs through the Tekton LLM Adapter.
Enhanced with standardized tekton-llm-client integration for consistent LLM access
across Tekton components.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union, AsyncGenerator, Callable

import aiohttp

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from hermes.core.llm_client import LLMClient

logger = logging.getLogger(__name__)

class LLMAdapter:
    """
    Client for interacting with LLMs through the Tekton LLM Adapter.
    
    This adapter maintains backward compatibility with existing code while
    using the enhanced LLMClient based on tekton-llm-client internally.
    """
    
    def __init__(self, adapter_url: Optional[str] = None):
        """
        Initialize the LLM adapter.
        
        Args:
            adapter_url: URL for the LLM adapter service
        """
        # Default to the environment variable or standard port from the Single Port Architecture
        config = get_component_config()
        rhetor_port = config.rhetor.port if hasattr(config, 'rhetor') else int(os.environ.get("RHETOR_PORT"))
        default_adapter_url = f"http://localhost:{rhetor_port}"
        
        self.adapter_url = adapter_url or os.environ.get("LLM_ADAPTER_URL", default_adapter_url)
        self.default_provider = os.environ.get("LLM_PROVIDER", "anthropic")
        self.default_model = os.environ.get("LLM_MODEL", "claude-3-haiku-20240307")
        
        # Create enhanced LLM client
        self.llm_client = LLMClient(
            adapter_url=self.adapter_url,
            model=self.default_model,
            provider=self.default_provider
        )
        
    async def get_available_providers(self) -> Dict[str, Any]:
        """
        Get available LLM providers.
        
        Returns:
            Dict of available providers and their models
        """
        # Use the enhanced client to get provider information
        return await self.llm_client.get_available_providers()
    
    def get_current_provider_and_model(self) -> Tuple[str, str]:
        """
        Get the current provider and model.
        
        Returns:
            Tuple of (provider_id, model_id)
        """
        return self.llm_client.get_current_provider_and_model()
    
    def set_provider_and_model(self, provider_id: str, model_id: str) -> None:
        """
        Set the provider and model to use.
        
        Args:
            provider_id: Provider ID
            model_id: Model ID
        """
        self.default_provider = provider_id
        self.default_model = model_id
        
        # Update the client's provider and model
        self.llm_client.set_provider_and_model(provider_id, model_id)
    
    async def analyze_message(self, message_content: str, message_type: str = "standard") -> Dict[str, Any]:
        """
        Analyze a message using LLM.
        
        Args:
            message_content: Message content
            message_type: Type of message (standard, log, registration, etc.)
            
        Returns:
            Analysis results
        """
        # Forward to the enhanced client
        return await self.llm_client.analyze_message(
            message_content=message_content,
            message_type=message_type
        )
    
    async def analyze_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a service registration using LLM.
        
        Args:
            service_data: Service registration data
            
        Returns:
            Analysis results
        """
        # Forward to the enhanced client
        return await self.llm_client.analyze_service(service_data)
    
    async def chat(self, message: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Send a chat message to the LLM.
        
        Args:
            message: User message
            chat_history: Optional chat history for context
            
        Returns:
            LLM response
        """
        # Forward to the enhanced client
        return await self.llm_client.chat(
            message=message,
            chat_history=chat_history,
            system_prompt=None,  # Will use the default system prompt
            model=self.default_model,
            provider=self.default_provider
        )
    
    async def streaming_chat(self, 
                            message: str, 
                            callback: Any,
                            chat_history: Optional[List[Dict[str, str]]] = None):
        """
        Send a chat message to the LLM with streaming response.
        
        Args:
            message: User message
            callback: Callback function to receive streaming chunks
            chat_history: Optional chat history for context
        """
        # Forward to the enhanced client
        await self.llm_client.streaming_chat(
            message=message,
            callback=callback,
            chat_history=chat_history,
            system_prompt=None,  # Will use the default system prompt
            model=self.default_model,
            provider=self.default_provider
        )
    
    # Removed the _parse_analysis_response and _parse_service_analysis_response methods
    # as they are now handled by the enhanced LLMClient