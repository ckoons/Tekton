"""
Tests for the MCP client in Ergon.

This module contains unit tests for the MCP client.
"""

import os
import base64
import pytest
import logging
import unittest.mock as mock
from typing import Dict, Any

import aiohttp
from aiohttp import ClientSession
from ergon.utils.tekton_integration import get_component_api_url

from ergon.core.mcp_client import MCPClient
from ergon.utils.mcp_adapter import (
    prepare_text_content,
    prepare_code_content,
    prepare_structured_content,
    extract_text_from_mcp_result
)

# Configure logging
logging.basicConfig(level=logging.INFO)

@pytest.fixture
def mcp_client():
    """Create an MCP client for testing."""
    client = MCPClient(
        client_id="test-client",
        client_name="Test MCP Client",
        hermes_url=get_component_api_url("hermes")
    )
    return client

@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = mock.AsyncMock(spec=ClientSession)
    return session

@pytest.mark.asyncio
async def test_initialize(mcp_client, mock_session):
    """Test client initialization."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Test initialization
    result = await mcp_client.initialize()
    
    # Assert result
    assert result is True
    
@pytest.mark.asyncio
async def test_close(mcp_client, mock_session):
    """Test client close."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Test close
    await mcp_client.close()
    
    # Assert session was closed
    mock_session.close.assert_called_once()
    
@pytest.mark.asyncio
async def test_process_content_text(mcp_client, mock_session):
    """Test processing text content."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={
        "result": {
            "content": {
                "text": "Processed text content"
            }
        }
    })
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Process text content
    result = await mcp_client.process_content(
        content="Test content",
        content_type="text"
    )
    
    # Assert result
    assert "result" in result
    assert "content" in result["result"]
    assert "text" in result["result"]["content"]
    assert result["result"]["content"]["text"] == "Processed text content"
    
    # Assert session.post was called with the right arguments
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args[0]
    assert call_args[0].endswith("/mcp/process")
    
@pytest.mark.asyncio
async def test_process_content_code(mcp_client, mock_session):
    """Test processing code content."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={
        "result": {
            "content": {
                "text": "Processed code content"
            }
        }
    })
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Process code content
    result = await mcp_client.process_content(
        content="def test(): pass",
        content_type="code",
        processing_options={"language": "python"}
    )
    
    # Assert result
    assert "result" in result
    assert "content" in result["result"]
    assert "text" in result["result"]["content"]
    assert result["result"]["content"]["text"] == "Processed code content"
    
@pytest.mark.asyncio
async def test_process_content_structured(mcp_client, mock_session):
    """Test processing structured content."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={
        "result": {
            "content": {
                "data": {"key": "value"}
            }
        }
    })
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Process structured content
    result = await mcp_client.process_content(
        content={"test": "data"},
        content_type="structured"
    )
    
    # Assert result
    assert "result" in result
    assert "content" in result["result"]
    assert "data" in result["result"]["content"]
    assert result["result"]["content"]["data"] == {"key": "value"}
    
@pytest.mark.asyncio
async def test_register_tool(mcp_client, mock_session):
    """Test registering a tool."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={"success": True})
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Define a mock handler
    async def mock_handler(params, context):
        return "Tool result"
    
    # Register tool
    result = await mcp_client.register_tool(
        tool_id="test-tool",
        name="Test Tool",
        description="A test tool",
        parameters={"type": "object"},
        returns={"type": "string"},
        handler=mock_handler
    )
    
    # Assert result
    assert result is True
    
    # Assert tool was stored
    assert "test-tool" in mcp_client.tools
    assert "test-tool" in mcp_client.tool_handlers
    
    # Assert session.post was called with the right arguments
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args[0]
    assert call_args[0].endswith("/mcp/tools/register")
    
@pytest.mark.asyncio
async def test_unregister_tool(mcp_client, mock_session):
    """Test unregistering a tool."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={"success": True})
    mock_session.delete.return_value.__aenter__.return_value = mock_response
    
    # Register a tool first
    async def mock_handler(params, context):
        return "Tool result"
    
    mcp_client.tools["test-tool"] = {
        "name": "Test Tool",
        "description": "A test tool",
        "parameters": {"type": "object"},
        "returns": {"type": "string"},
        "metadata": {}
    }
    mcp_client.tool_handlers["test-tool"] = mock_handler
    
    # Unregister tool
    result = await mcp_client.unregister_tool("test-tool")
    
    # Assert result
    assert result is True
    
    # Assert tool was removed
    assert "test-tool" not in mcp_client.tools
    assert "test-tool" not in mcp_client.tool_handlers
    
    # Assert session.delete was called with the right arguments
    mock_session.delete.assert_called_once()
    call_args = mock_session.delete.call_args[0]
    assert call_args[0].endswith("/mcp/tools/unregister")
    
@pytest.mark.asyncio
async def test_execute_tool_local(mcp_client):
    """Test executing a tool locally."""
    # Define a mock handler
    async def mock_handler(params, context):
        return params["a"] + params["b"]
    
    # Register the tool
    mcp_client.tool_handlers["calculator"] = mock_handler
    
    # Execute the tool
    result = await mcp_client.execute_tool(
        tool_id="calculator",
        parameters={"a": 5, "b": 3}
    )
    
    # Assert result
    assert result["success"] is True
    assert result["result"] == 8
    
@pytest.mark.asyncio
async def test_execute_tool_remote(mcp_client, mock_session):
    """Test executing a tool remotely."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={
        "success": True,
        "result": 8
    })
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Execute the tool
    result = await mcp_client.execute_tool(
        tool_id="remote-calculator",
        parameters={"a": 5, "b": 3}
    )
    
    # Assert result
    assert result["success"] is True
    assert result["result"] == 8
    
    # Assert session.post was called with the right arguments
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args[0]
    assert call_args[0].endswith("/mcp/tools/execute")
    
@pytest.mark.asyncio
async def test_create_context(mcp_client, mock_session):
    """Test creating a context."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={
        "context_id": "test-context-123"
    })
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Create context
    result = await mcp_client.create_context(
        context_type="conversation",
        content={"messages": [{"role": "user", "content": "Hello"}]}
    )
    
    # Assert result
    assert result == "test-context-123"
    
    # Assert session.post was called with the right arguments
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args[0]
    assert call_args[0].endswith("/mcp/contexts")
    
@pytest.mark.asyncio
async def test_enhance_context(mcp_client, mock_session):
    """Test enhancing a context."""
    # Mock the client session
    mcp_client.session = mock_session
    
    # Setup mock response
    mock_response = mock.AsyncMock()
    mock_response.raise_for_status = mock.AsyncMock()
    mock_response.json = mock.AsyncMock(return_value={"success": True})
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    # Enhance context
    result = await mcp_client.enhance_context(
        context_id="test-context-123",
        content={"messages": [{"role": "assistant", "content": "Hello there!"}]},
        operation="add"
    )
    
    # Assert result
    assert result is True
    
    # Assert session.post was called with the right arguments
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args[0]
    assert call_args[0].endswith("/mcp/contexts/test-context-123/enhance")
    
@pytest.mark.parametrize("content,content_type,expected", [
    ("text content", "text", {"text": "text content"}),
    ("code content", "code", {"text": "code content"}),
    ({"data": "value"}, "structured", {"data": {"data": "value"}}),
    (b"image data", "image", {"image": mock.ANY, "format": "base64"})
])
def test_prepare_content(mcp_client, content, content_type, expected):
    """Test preparing content for different types."""
    result = mcp_client._prepare_content(content, content_type)
    
    # For text and code, check exact match
    if content_type in ["text", "code"]:
        assert result == expected
    
    # For structured, check data is included
    elif content_type == "structured":
        assert "data" in result
        assert result["data"] == expected["data"]
    
    # For image, check base64 encoding
    elif content_type == "image":
        assert "image" in result
        assert "format" in result
        assert result["format"] == "base64"
        
        # Decode the base64 to verify it's valid
        try:
            decoded = base64.b64decode(result["image"])
            assert decoded == content
        except Exception:
            pytest.fail("Invalid base64 encoding")

def test_prepare_content_invalid():
    """Test preparing content with invalid types."""
    client = MCPClient()
    
    # Test invalid text content
    with pytest.raises(ValueError):
        client._prepare_content(123, "text")
    
    # Test invalid structured content
    with pytest.raises(ValueError):
        client._prepare_content("not a dict", "structured")
    
    # Test invalid image content
    with pytest.raises(ValueError):
        client._prepare_content("not bytes", "image")

# Test the MCP adapter functions
def test_extract_text_from_mcp_result():
    """Test extracting text from MCP result."""
    # Test with direct text in content
    result = {
        "result": {
            "content": {
                "text": "Extracted text"
            }
        }
    }
    assert extract_text_from_mcp_result(result) == "Extracted text"
    
    # Test with content as string
    result = {
        "result": {
            "content": "Extracted text"
        }
    }
    assert extract_text_from_mcp_result(result) == "Extracted text"
    
    # Test with result as string
    result = {
        "result": "Extracted text"
    }
    assert extract_text_from_mcp_result(result) == "Extracted text"
    
    # Test with error
    result = {
        "error": "Something went wrong"
    }
    assert extract_text_from_mcp_result(result) is None
    
    # Test with empty result
    assert extract_text_from_mcp_result({}) is None
    assert extract_text_from_mcp_result(None) is None