"""
Mail Service for Ergon.

This module provides a high-level mail service that uses provider
adapters to interact with various email services.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
import json
from pathlib import Path
import webbrowser
import asyncio

from ergon.utils.config.settings import settings
from ergon.core.agents.mail.providers import get_mail_provider, MailProvider
# Import for proper typing, avoid circular imports at runtime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ergon.core.agents.mail.imap_provider import ImapSmtpProvider

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class MailService:
    """
    High-level mail service for Ergon.
    
    This service provides a unified interface for mail operations,
    handling the details of provider authentication and API differences.
    """
    
    def __init__(self, provider_type: str = "gmail"):
        """
        Initialize the mail service.
        
        Args:
            provider_type: Type of mail provider to use (gmail, outlook, etc.)
        """
        self.provider_type = provider_type
        self.provider = None
        self.config_path = os.path.join(settings.config_path, "mail")
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_path, exist_ok=True)
        
        # Try to load config
        self.config = self._load_config()
        
        # Initialize provider
        self._init_provider()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load mail configuration from disk."""
        config_file = os.path.join(self.config_path, "config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading mail config: {str(e)}")
        
        # Default config
        return {
            "default_provider": self.provider_type,
            "providers": {}
        }
    
    def _save_config(self) -> bool:
        """Save mail configuration to disk."""
        config_file = os.path.join(self.config_path, "config.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving mail config: {str(e)}")
            return False
    
    def _init_provider(self) -> None:
        """Initialize the mail provider based on configuration."""
        provider_config = self.config.get("providers", {}).get(self.provider_type, {})
        
        self.provider = get_mail_provider(
            provider_type=self.provider_type,
            **provider_config
        )
    
    async def setup(self) -> bool:
        """
        Set up the mail service with user authentication.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Create provider if not initialized
            if not self.provider:
                self._init_provider()
            
            # Authenticate
            success = await self.provider.authenticate()
            
            if success:
                # Update config with any provider-specific settings
                if self.provider_type not in self.config["providers"]:
                    self.config["providers"][self.provider_type] = {}
                
                # For Gmail, we don't need to store credentials in our config
                # as they're already stored in token files
                
                # Save config
                self._save_config()
                
                return True
            else:
                logger.error(f"Failed to authenticate with {self.provider_type}")
                return False
            
        except Exception as e:
            logger.error(f"Error during mail setup: {str(e)}")
            return False
    
    async def get_inbox(self, limit: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        """
        Get inbox messages.
        
        Args:
            limit: Maximum number of messages
            page: Page number (1-based)
            
        Returns:
            List of message metadata
        """
        if not self.provider:
            logger.error("Mail provider not initialized")
            return []
        
        try:
            return await self.provider.get_inbox(limit=limit, page=page)
        except Exception as e:
            logger.error(f"Error getting inbox: {str(e)}")
            return []
    
    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get a specific message by ID.
        
        Args:
            message_id: Message ID
            
        Returns:
            Message data
        """
        if not self.provider:
            logger.error("Mail provider not initialized")
            return {}
        
        try:
            return await self.provider.get_message(message_id)
        except Exception as e:
            logger.error(f"Error getting message {message_id}: {str(e)}")
            return {}
    
    async def send_message(self, to: Union[str, List[str]], subject: str, body: str,
                           html_content: bool = False,
                           cc: Optional[Union[str, List[str]]] = None,
                           bcc: Optional[Union[str, List[str]]] = None) -> bool:
        """
        Send a new email message.
        
        Args:
            to: Recipient(s) email address(es)
            subject: Email subject
            body: Email body
            html_content: Whether to send as HTML email (True for HTML, False for plain text)
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.provider:
            logger.error("Mail provider not initialized")
            return False
        
        try:
            # Convert string arguments to lists if needed
            to_list = [to] if isinstance(to, str) else to
            cc_list = [cc] if isinstance(cc, str) and cc else None if cc is None else cc
            bcc_list = [bcc] if isinstance(bcc, str) and bcc else None if bcc is None else bcc
            
            # For Gmail, we need to modify the content type in the message
            if isinstance(self.provider, GmailProvider) and hasattr(self.provider, 'send_message'):
                # We need this import inside the method to avoid circular imports
                from .providers import GmailProvider
                
                # Call Gmail provider directly with content type override
                return await self.provider.send_message(
                    to=to_list,
                    subject=subject,
                    body=body,
                    content_type="text/html" if html_content else "text/plain",
                    cc=cc_list,
                    bcc=bcc_list
                )
            else:
                # For other providers, we'll need to make them handle html_content parameter
                return await self.provider.send_message(
                    to=to_list,
                    subject=subject,
                    body=body,
                    cc=cc_list,
                    bcc=bcc_list
                )
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def reply_to_message(self, message_id: str, body: str, html_content: bool = False) -> bool:
        """
        Reply to a specific message.
        
        Args:
            message_id: Message ID to reply to
            body: Reply body
            html_content: Whether to send as HTML email (True for HTML, False for plain text)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.provider:
            logger.error("Mail provider not initialized")
            return False
        
        try:
            # For Gmail, we need to modify the content type in the message
            if isinstance(self.provider, GmailProvider) and hasattr(self.provider, 'reply_to_message'):
                # We need this import inside the method to avoid circular imports
                from .providers import GmailProvider
                
                # Call Gmail provider directly with content type override
                return await self.provider.reply_to_message(
                    message_id=message_id,
                    body=body,
                    content_type="text/html" if html_content else "text/plain"
                )
            else:
                # For other providers, we'll need to make them handle html_content parameter
                return await self.provider.reply_to_message(message_id, body)
        except Exception as e:
            logger.error(f"Error replying to message {message_id}: {str(e)}")
            return False
    
    async def search_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for messages.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        if not self.provider:
            logger.error("Mail provider not initialized")
            return []
        
        try:
            return await self.provider.search_messages(query, limit)
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    async def get_folders(self) -> List[Dict[str, Any]]:
        """
        Get available folders/labels.
        
        Returns:
            List of folder metadata
        """
        if not self.provider:
            logger.error("Mail provider not initialized")
            return []
        
        try:
            return await self.provider.get_folders()
        except Exception as e:
            logger.error(f"Error getting folders: {str(e)}")
            return []


# Singleton instance
_mail_service_instance = None

def get_mail_service(provider_type: str = None) -> MailService:
    """
    Get the mail service singleton instance.
    
    Args:
        provider_type: Optional provider type to override default
        
    Returns:
        Mail service instance
    """
    global _mail_service_instance
    
    if _mail_service_instance is None or provider_type is not None:
        # Load config to determine default provider if not specified
        config_path = os.path.join(settings.config_path, "mail", "config.json")
        
        if provider_type is None and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    provider_type = config.get("default_provider", "gmail")
            except Exception:
                provider_type = "gmail"  # Fallback to Gmail
        elif provider_type is None:
            provider_type = "gmail"  # Default to Gmail
            
        _mail_service_instance = MailService(provider_type=provider_type)
    
    return _mail_service_instance


async def setup_mail_provider(provider_type: str = "gmail") -> bool:
    """
    Set up a mail provider with user authentication.
    
    Args:
        provider_type: Type of mail provider
        
    Returns:
        True if setup successful, False otherwise
    """
    mail_service = get_mail_service(provider_type)
    return await mail_service.setup()