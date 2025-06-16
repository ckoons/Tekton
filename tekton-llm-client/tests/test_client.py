import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock

from tekton_llm_client import TektonLLMClient
from tekton_llm_client.models import Message, MessageRole, CompletionOptions, CompletionResponse
from tekton_llm_client.exceptions import ServiceUnavailableError, ConnectionError

@pytest.fixture
def client():
    """Create a TektonLLMClient instance for testing."""
    client = TektonLLMClient(
        component_id="test-component",
        rhetor_url="http://localhost:8003"
    )
    return client

@pytest.fixture
def mock_response():
    """Create a mock response for testing."""
    return {
        "content": "This is a test response",
        "model": "test-model",
        "provider": "test-provider",
        "finish_reason": "stop",
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        "context_id": "test-context",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@pytest.mark.asyncio
async def test_initialize(client):
    """Test client initialization."""
    with patch.object(client.primary_adapter, 'initialize', return_value=AsyncMock(return_value=True)):
        with patch.object(client.primary_adapter, 'get_provider_info', return_value=AsyncMock(return_value={"default_model": "test-model"})):
            result = await client.initialize()
            assert result is True
            assert client.primary_adapter.initialize.called

@pytest.mark.asyncio
async def test_generate_text(client, mock_response):
    """Test text generation."""
    with patch.object(client, '_complete_chat_response', return_value=AsyncMock(return_value=CompletionResponse(**mock_response))):
        response = await client.generate_text("Test prompt", system_prompt="Test system prompt")
        assert response.content == "This is a test response"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert client._complete_chat_response.called

@pytest.mark.asyncio
async def test_generate_chat_response(client, mock_response):
    """Test chat response generation."""
    messages = [
        Message(role=MessageRole.USER, content="Hello"),
        Message(role=MessageRole.ASSISTANT, content="Hi there"),
        Message(role=MessageRole.USER, content="How are you?")
    ]
    
    with patch.object(client, '_complete_chat_response', return_value=AsyncMock(return_value=CompletionResponse(**mock_response))):
        response = await client.generate_chat_response(messages)
        assert response.content == "This is a test response"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert client._complete_chat_response.called
        
        # Check that the messages were passed correctly
        args, kwargs = client._complete_chat_response.call_args
        assert len(kwargs['messages']) == 3
        assert kwargs['messages'][0].role == MessageRole.USER
        assert kwargs['messages'][1].role == MessageRole.ASSISTANT
        assert kwargs['messages'][2].role == MessageRole.USER

@pytest.mark.asyncio
async def test_fallback_on_error(client, mock_response):
    """Test fallback behavior when primary adapter fails."""
    # Configure the test client to use fallback
    client.use_fallback = True
    client.fallback_adapter = MagicMock()
    client.fallback_adapter.complete_chat = AsyncMock(return_value=mock_response)
    
    # Make primary adapter fail
    with patch.object(client.primary_adapter, 'complete_chat', side_effect=ConnectionError("Connection failed")):
        response = await client.generate_text("Test prompt")
        
        # Verify fallback was used
        assert client.fallback_adapter.complete_chat.called
        assert response.content == "This is a test response"

@pytest.mark.asyncio
async def test_error_without_fallback(client):
    """Test error handling when fallback is disabled."""
    # Configure the test client to not use fallback
    client.use_fallback = False
    
    # Make primary adapter fail
    with patch.object(client.primary_adapter, 'complete_chat', side_effect=ServiceUnavailableError("Service unavailable")):
        with pytest.raises(ServiceUnavailableError):
            await client.generate_text("Test prompt")

@pytest.mark.asyncio
async def test_get_providers(client):
    """Test getting available providers."""
    mock_providers = {
        "providers": {
            "anthropic": {
                "name": "Anthropic Claude",
                "available": True,
                "models": [
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"}
                ]
            }
        },
        "default_provider": "anthropic",
        "default_model": "claude-3-opus-20240229"
    }
    
    with patch.object(client.primary_adapter, 'get_providers', return_value=AsyncMock(return_value=mock_providers)):
        providers = await client.get_providers()
        assert providers.providers["anthropic"].name == "Anthropic Claude"
        assert providers.default_provider == "anthropic"
        assert providers.default_model == "claude-3-opus-20240229"

@pytest.mark.asyncio
async def test_streaming(client):
    """Test streaming responses."""
    async def mock_stream():
        for i in range(3):
            yield {
                "chunk": f"Chunk {i} ",
                "context_id": "test-context",
                "model": "test-model",
                "provider": "test-provider",
                "timestamp": "2024-01-01T00:00:00Z",
                "done": i == 2
            }
    
    with patch.object(client, '_stream_chat_response', return_value=mock_stream()):
        chunks = []
        async for chunk in client.generate_text("Test prompt", streaming=True):
            chunks.append(chunk)
        
        assert len(chunks) == 3
        assert chunks[0].chunk == "Chunk 0 "
        assert chunks[1].chunk == "Chunk 1 "
        assert chunks[2].chunk == "Chunk 2 "
        assert chunks[2].done == True

if __name__ == "__main__":
    pytest.main(["-xvs", "test_client.py"])