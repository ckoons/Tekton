"""
Base adapter interface for LLM providers.
"""

from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from abc import ABC, abstractmethod

from ..models import Message, CompletionOptions


class BaseAdapter(ABC):
    """Base adapter interface for LLM providers."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the adapter.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the adapter and clean up resources."""
        pass
    
    @abstractmethod
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
        Complete a chat request.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Completion options
            
        Returns:
            Dictionary with the complete response
        """
        pass
    
    @abstractmethod
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
        Stream a chat response.
        
        Args:
            messages: List of Message objects
            system_prompt: Optional system instructions
            context_id: Context ID for tracking conversation
            provider_id: Provider ID to use
            model_id: Model ID to use
            options: Completion options
            
        Yields:
            Dictionaries with response chunks
        """
        pass
    
    @abstractmethod
    async def get_providers(self) -> Dict[str, Any]:
        """
        Get information about all available LLM providers.
        
        Returns:
            Dictionary with provider information
        """
        pass
    
    @abstractmethod
    async def get_provider_info(self, provider_id: str) -> Dict[str, Any]:
        """
        Get information about a specific provider.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Dictionary with provider information
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the adapter is available.
        
        Returns:
            True if the adapter is available, False otherwise
        """
        pass