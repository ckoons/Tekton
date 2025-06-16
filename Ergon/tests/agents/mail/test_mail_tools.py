"""
Tests for Mail Agent tools.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from ergon.core.agents.mail.tools import MailTools, mail_tool_definitions, register_mail_tools


def test_mail_tool_definitions():
    """Test mail tool definitions."""
    # Verify mail tool definitions structure
    tool_defs = mail_tool_definitions()
    
    # Check if we have all expected tools
    expected_tools = [
        "setup_mail", "get_inbox", "get_message", "send_message", 
        "reply_to_message", "search_messages", "get_folders"
    ]
    
    actual_tools = [tool["name"] for tool in tool_defs]
    
    for tool in expected_tools:
        assert tool in actual_tools, f"Missing tool definition: {tool}"
    
    # Verify specific tool structure
    send_message_tool = [t for t in tool_defs if t["name"] == "send_message"][0]
    assert "function_def" in send_message_tool
    assert "parameters" in send_message_tool["function_def"]


@pytest.mark.asyncio
async def test_get_inbox_tool():
    """Test get_inbox mail tool."""
    # Mock the mail service
    with patch('ergon.core.agents.mail.tools.get_mail_service') as mock_get_service:
        # Set up the mock service
        mock_service = MagicMock()
        mock_inbox = [
            {"id": "msg1", "subject": "Test Email 1", "from": "user1@example.com"},
            {"id": "msg2", "subject": "Test Email 2", "from": "user2@example.com"}
        ]
        
        # Make get_inbox return a coroutine that returns the test data
        async def mock_get_inbox(*args, **kwargs):
            return mock_inbox
            
        mock_service.get_inbox = mock_get_inbox
        mock_get_service.return_value = mock_service
        
        # Call the get_inbox tool
        result = await MailTools.get_inbox(limit=10, page=1)
        
        # Verify the result
        assert result["success"] is True
        assert len(result["messages"]) == 2
        assert "Test Email 1" in result["messages"][0]["subject"]


@pytest.mark.asyncio
async def test_send_message_tool():
    """Test send_message mail tool."""
    # Mock the mail service
    with patch('ergon.core.agents.mail.tools.get_mail_service') as mock_get_service:
        # Set up the mock service
        mock_service = MagicMock()
        
        # Make send_message return a coroutine that returns True
        async def mock_send_message(*args, **kwargs):
            # Store the args for verification
            mock_send_message.called_with = kwargs
            return True
            
        mock_service.send_message = mock_send_message
        mock_get_service.return_value = mock_service
        
        # Call the send_message tool
        result = await MailTools.send_message(
            to="user@example.com", 
            subject="Test Subject", 
            body="Test Body"
        )
        
        # Verify the result
        assert result["success"] is True
        
        # Verify the service was called with correct parameters
        assert mock_send_message.called_with["to"] == ["user@example.com"]
        assert mock_send_message.called_with["subject"] == "Test Subject"
        assert mock_send_message.called_with["body"] == "Test Body"


def test_register_mail_tools():
    """Test registering mail tools."""
    # Create a mock tool registry
    tool_registry = {}
    
    # Register mail tools
    register_mail_tools(tool_registry)
    
    # Verify tools were registered
    expected_tools = [
        "setup_mail", "get_inbox", "get_message", "send_message", 
        "reply_to_message", "search_messages", "get_folders"
    ]
    
    for tool in expected_tools:
        assert tool in tool_registry
        assert callable(tool_registry[tool])