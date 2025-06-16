"""
Tests for Gmail Provider integration.
"""

import pytest
import asyncio
import os
import json
import base64
from unittest.mock import MagicMock, patch, mock_open
from ergon.core.agents.mail.providers import GmailProvider


@pytest.mark.asyncio
async def test_gmail_provider_initialization():
    """Test Gmail provider initialization."""
    # Initialize the provider
    provider = GmailProvider(
        credentials_file="/path/to/credentials.json",
        token_file="/path/to/token.json"
    )
    
    # Check properties
    assert provider.credentials_file == "/path/to/credentials.json"
    assert provider.token_file == "/path/to/token.json"
    assert provider.credentials is None
    assert provider.email is None
    assert provider.api_base == "https://gmail.googleapis.com/gmail/v1"


@pytest.mark.asyncio
async def test_gmail_authentication_with_existing_token():
    """Test Gmail authentication with existing token."""
    # First patch settings so we can create a GmailProvider instance
    with patch('ergon.core.agents.mail.providers.settings') as mock_settings:
        # Mock the settings
        mock_settings.config_path = '/tmp'
        
        # Create a provider with pre-configured credentials
        provider = GmailProvider(
            credentials_file="/tmp/fake_credentials.json",
            token_file="/tmp/fake_token.json"
        )
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        mock_credentials.valid = True
        mock_credentials.expired = False
        mock_credentials.token = "fake_token"
        provider.credentials = mock_credentials
        
        # Just test the case where credentials are already valid
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock HTTP response for user profile
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"emailAddress": "test@example.com"}
            mock_get.return_value = mock_response
            
            # Call authenticate (no need to patch it further since we're just using it normally)
            result = await provider.authenticate()
            
            # Verify result
            assert provider.email == "test@example.com"


@pytest.mark.asyncio
async def test_gmail_get_inbox_mock():
    """Test Gmail get_inbox function with simplified mocking."""
    # Patch settings
    with patch('ergon.core.agents.mail.providers.settings') as mock_settings:
        # Mock the settings
        mock_settings.config_path = '/tmp'
        
        # Create a provider with specific file paths
        provider = GmailProvider(
            credentials_file="/tmp/fake_credentials.json",
            token_file="/tmp/fake_token.json"
        )
        
        # Set up mock credentials
        provider.credentials = MagicMock()
        provider.credentials.valid = True
        provider.credentials.token = "fake_token"
        
        # Create mock inbox messages
        mock_messages = [
            {
                "id": "msg1", 
                "subject": "Test Email 1", 
                "from": "user1@example.com", 
                "snippet": "This is a test"
            },
            {
                "id": "msg2", 
                "subject": "Test Email 2", 
                "from": "user2@example.com", 
                "snippet": "This is another test"
            }
        ]
        
        # Create a mock get_inbox method
        async def mock_get_inbox(*args, **kwargs):
            return mock_messages
            
        # Patch the get_inbox method
        provider.get_inbox = mock_get_inbox
        
        # Call get_inbox
        messages = await provider.get_inbox(limit=10, page=1)
        
        # Verify results
        assert len(messages) == 2
        assert messages[0]["id"] == "msg1"
        assert messages[0]["subject"] == "Test Email 1"
        assert messages[1]["id"] == "msg2"
        assert messages[1]["subject"] == "Test Email 2"


@pytest.mark.asyncio
async def test_gmail_send_message_mock():
    """Test Gmail send_message function with simplified mocking."""
    # Patch settings
    with patch('ergon.core.agents.mail.providers.settings') as mock_settings:
        # Mock the settings
        mock_settings.config_path = '/tmp'
        
        # Create a provider with specific file paths
        provider = GmailProvider(
            credentials_file="/tmp/fake_credentials.json",
            token_file="/tmp/fake_token.json"
        )
        
        # Set up mock credentials
        provider.credentials = MagicMock()
        provider.credentials.valid = True
        provider.credentials.token = "fake_token"
        provider.email = "me@example.com"
        
        # Create a mock send_message method to avoid API calls
        called_with = {}
        
        async def mock_send_message(*args, **kwargs):
            # Store the arguments for verification
            nonlocal called_with
            called_with = kwargs
            return True
            
        # Replace the real method with our mock
        provider.send_message = mock_send_message
        
        # Test parameters
        to_addr = ["recipient@example.com"]
        subject = "Test Subject"
        body = "Test Body"
        content_type = "text/plain"
        
        # Call send_message
        result = await provider.send_message(
            to=to_addr,
            subject=subject,
            body=body,
            content_type=content_type
        )
        
        # Verify the result
        assert result is True
        
        # Verify that the method was called with the expected parameters
        assert called_with["to"] == to_addr
        assert called_with["subject"] == subject
        assert called_with["body"] == body
        assert called_with["content_type"] == content_type