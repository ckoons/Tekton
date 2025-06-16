"""
Base provider interface for LLM providers in Rhetor.

This module defines the base interface that all LLM providers must implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator, Union

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, provider_id: str, display_name: str):
        """
        Initialize the LLM provider.
        
        Args:
            provider_id: Unique identifier for the provider
            display_name: User-friendly name for the provider
        """
        self.provider_id = provider_id
        self.display_name = display_name
        self.available = False
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the provider.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.initialized = await self._initialize()
            return self.initialized
        except Exception as e:
            logger.error(f"Error initializing provider {self.provider_id}: {e}")
            self.initialized = False
            return False
    
    @abstractmethod
    async def _initialize(self) -> bool:
        """
        Provider-specific initialization.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    def is_available(self) -> bool:
        """
        Check if the provider is available.
        
        Returns:
            True if the provider is available, False otherwise
        """
        return self.available
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get available models for this provider.
        
        Returns:
            List of dictionaries with model info
        """
        pass
    
    @abstractmethod
    async def complete(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a message with the LLM.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM.
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            options: Additional options for the LLM
            
        Yields:
            Completion chunks as they are generated
        """
        pass
    
    @abstractmethod
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a chat conversation with the LLM.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion from the LLM.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            system_prompt: Optional system prompt
            model: Optional model to use (defaults to provider default)
            options: Additional options for the LLM
            
        Yields:
            Completion chunks as they are generated
        """
        pass