"""
Mail Agent Tools for Ergon.

This module defines the tools that can be used by agents to interact
with email services.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable

from ergon.utils.config.settings import settings
from ergon.core.agents.mail.service import get_mail_service, setup_mail_provider

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


def mail_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get the mail tool definitions for agent use.
    
    Returns:
        List of tool definition objects
    """
    return [
        {
            "name": "setup_mail",
            "description": "Set up mail service with user authentication",
            "function_def": {
                "name": "setup_mail",
                "description": "Set up mail service with user authentication",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "Email provider (gmail, outlook, imap)",
                            "enum": ["gmail", "outlook", "imap"]
                        }
                    },
                    "required": ["provider"]
                }
            }
        },
        {
            "name": "get_inbox",
            "description": "Get messages from the user's inbox",
            "function_def": {
                "name": "get_inbox",
                "description": "Get messages from the user's inbox",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of messages to retrieve",
                            "default": 10
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number (1-based)",
                            "default": 1
                        }
                    }
                }
            }
        },
        {
            "name": "get_message",
            "description": "Get a specific email message by ID",
            "function_def": {
                "name": "get_message",
                "description": "Get a specific email message by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "ID of the message to retrieve"
                        }
                    },
                    "required": ["message_id"]
                }
            }
        },
        {
            "name": "send_message",
            "description": "Send a new email message",
            "function_def": {
                "name": "send_message",
                "description": "Send a new email message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address(es), comma-separated for multiple"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body text"
                        },
                        "html": {
                            "type": "boolean",
                            "description": "Whether to send as HTML email",
                            "default": False
                        },
                        "cc": {
                            "type": "string",
                            "description": "CC recipient(s), comma-separated for multiple"
                        },
                        "bcc": {
                            "type": "string",
                            "description": "BCC recipient(s), comma-separated for multiple"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        },
        {
            "name": "reply_to_message",
            "description": "Reply to an existing email message",
            "function_def": {
                "name": "reply_to_message",
                "description": "Reply to an existing email message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "ID of the message to reply to"
                        },
                        "body": {
                            "type": "string",
                            "description": "Reply body text"
                        },
                        "html": {
                            "type": "boolean",
                            "description": "Whether to send as HTML email",
                            "default": False
                        }
                    },
                    "required": ["message_id", "body"]
                }
            }
        },
        {
            "name": "search_messages",
            "description": "Search for email messages",
            "function_def": {
                "name": "search_messages",
                "description": "Search for email messages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (provider-specific syntax)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "name": "get_folders",
            "description": "Get available email folders/labels",
            "function_def": {
                "name": "get_folders",
                "description": "Get available email folders/labels",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]


class MailTools:
    """Mail tools for agent use."""
    
    @staticmethod
    async def setup_mail(provider: str = "gmail") -> Dict[str, Any]:
        """
        Set up mail service with user authentication.
        
        Args:
            provider: Email provider (gmail, outlook, etc.)
            
        Returns:
            Result object
        """
        try:
            success = await setup_mail_provider(provider_type=provider)
            
            if success:
                return {
                    "success": True,
                    "message": f"Successfully set up {provider} mail service."
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to set up {provider} mail service. Please check logs."
                }
        except Exception as e:
            logger.error(f"Error setting up mail: {str(e)}")
            return {
                "success": False,
                "message": f"Error setting up mail: {str(e)}"
            }
    
    @staticmethod
    async def get_inbox(limit: int = 10, page: int = 1) -> Dict[str, Any]:
        """
        Get messages from the user's inbox.
        
        Args:
            limit: Maximum number of messages
            page: Page number (1-based)
            
        Returns:
            Result with messages
        """
        try:
            mail_service = get_mail_service()
            messages = await mail_service.get_inbox(limit=limit, page=page)
            
            return {
                "success": True,
                "message": f"Retrieved {len(messages)} messages from inbox.",
                "messages": messages
            }
        except Exception as e:
            logger.error(f"Error getting inbox: {str(e)}")
            return {
                "success": False,
                "message": f"Error getting inbox: {str(e)}",
                "messages": []
            }
    
    @staticmethod
    async def get_message(message_id: str) -> Dict[str, Any]:
        """
        Get a specific email message by ID.
        
        Args:
            message_id: ID of the message
            
        Returns:
            Result with message
        """
        try:
            mail_service = get_mail_service()
            message = await mail_service.get_message(message_id)
            
            if message:
                return {
                    "success": True,
                    "message": "Successfully retrieved message.",
                    "email": message
                }
            else:
                return {
                    "success": False,
                    "message": f"Message {message_id} not found.",
                    "email": {}
                }
        except Exception as e:
            logger.error(f"Error getting message {message_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error getting message: {str(e)}",
                "email": {}
            }
    
    @staticmethod
    async def send_message(to: str, subject: str, body: str,
                           html: bool = False,
                           cc: Optional[str] = None,
                           bcc: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a new email message.
        
        Args:
            to: Recipient(s), comma-separated
            subject: Email subject
            body: Email body
            html: Whether to send as HTML email
            cc: CC recipient(s), comma-separated
            bcc: BCC recipient(s), comma-separated
            
        Returns:
            Result object
        """
        try:
            mail_service = get_mail_service()
            
            # Parse recipients
            to_list = [addr.strip() for addr in to.split(",") if addr.strip()]
            cc_list = [addr.strip() for addr in cc.split(",")] if cc else None
            bcc_list = [addr.strip() for addr in bcc.split(",")] if bcc else None
            
            # Validate email addresses
            if not to_list:
                return {
                    "success": False,
                    "message": "No valid recipient addresses provided."
                }
                
            # Send message
            success = await mail_service.send_message(
                to=to_list,
                subject=subject,
                body=body,
                html_content=html,  # Pass HTML flag to service
                cc=cc_list,
                bcc=bcc_list
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Message sent successfully to {', '.join(to_list)}."
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to send message. Please check logs."
                }
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                "success": False,
                "message": f"Error sending message: {str(e)}"
            }
    
    @staticmethod
    async def reply_to_message(message_id: str, body: str, html: bool = False) -> Dict[str, Any]:
        """
        Reply to an existing email message.
        
        Args:
            message_id: ID of the message to reply to
            body: Reply body
            html: Whether to send as HTML email
            
        Returns:
            Result object
        """
        try:
            mail_service = get_mail_service()
            success = await mail_service.reply_to_message(message_id, body, html_content=html)
            
            if success:
                return {
                    "success": True,
                    "message": "Reply sent successfully."
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to send reply. Please check logs."
                }
        except Exception as e:
            logger.error(f"Error replying to message {message_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error replying to message: {str(e)}"
            }
    
    @staticmethod
    async def search_messages(query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for email messages.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Result with matching messages
        """
        try:
            mail_service = get_mail_service()
            messages = await mail_service.search_messages(query, limit)
            
            return {
                "success": True,
                "message": f"Found {len(messages)} matching messages.",
                "messages": messages
            }
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return {
                "success": False,
                "message": f"Error searching messages: {str(e)}",
                "messages": []
            }
    
    @staticmethod
    async def get_folders() -> Dict[str, Any]:
        """
        Get available email folders/labels.
        
        Returns:
            Result with folders
        """
        try:
            mail_service = get_mail_service()
            folders = await mail_service.get_folders()
            
            return {
                "success": True,
                "message": f"Retrieved {len(folders)} folders/labels.",
                "folders": folders
            }
        except Exception as e:
            logger.error(f"Error getting folders: {str(e)}")
            return {
                "success": False,
                "message": f"Error getting folders: {str(e)}",
                "folders": []
            }


def register_mail_tools(tool_registry: Dict[str, Callable]) -> None:
    """
    Register mail tools with the agent tool registry.
    
    Args:
        tool_registry: Tool registry to update
    """
    # Create async tool wrappers
    for tool_def in mail_tool_definitions():
        tool_name = tool_def["name"]
        
        # Get the corresponding method from MailTools
        method = getattr(MailTools, tool_name)
        
        # Register the tool
        tool_registry[tool_name] = method