"""
Mail Provider Base Interface

This module defines the base interface for mail providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class MailProvider(ABC):
    """Base interface for mail providers."""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the provider."""
        pass
    
    @abstractmethod
    async def get_inbox(self, limit: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        """Retrieve inbox messages."""
        pass
    
    @abstractmethod
    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """Retrieve a specific message by ID."""
        pass
    
    @abstractmethod
    async def send_message(self, to: List[str], subject: str, body: str, 
                           cc: Optional[List[str]] = None,
                           bcc: Optional[List[str]] = None) -> bool:
        """Send a new message."""
        pass
    
    @abstractmethod
    async def reply_to_message(self, message_id: str, body: str) -> bool:
        """Reply to a specific message."""
        pass
    
    @abstractmethod
    async def search_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for messages using provider-specific query."""
        pass
    
    @abstractmethod
    async def get_folders(self) -> List[Dict[str, Any]]:
        """Get available folders/labels."""
        pass