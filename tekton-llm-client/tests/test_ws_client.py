import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock, mock_open

from tekton_llm_client import TektonLLMWebSocketClient
from tekton_llm_client.models import StreamingChunk
from tekton_llm_client.exceptions import ConnectionError, TimeoutError

class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self, messages=None):
        self.messages = messages or []
        self.sent_messages = []
        self.closed = False
    
    async def send(self, message):
        self.sent_messages.append(message)
        
    async def recv(self):
        if not self.messages:
            # If no more messages, simulate connection closed
            raise Exception("Connection closed")
        return self.messages.pop(0)
        
    async def close(self):
        self.closed = True
        
    async def __aiter__(self):
        for message in self.messages:
            yield message
        self.closed = True

@pytest.fixture
def client():
    """Create a TektonLLMWebSocketClient instance for testing."""
    client = TektonLLMWebSocketClient(
        component_id="test-component",
        rhetor_url="http://localhost:8003"
    )
    return client

@pytest.fixture
def connected_client():
    """Create a connected TektonLLMWebSocketClient for testing."""
    client = TektonLLMWebSocketClient(
        component_id="test-component",
        rhetor_url="http://localhost:8003"
    )
    
    # Set up the client as connected
    client.ws = MockWebSocket()
    client.connected = True
    client.connecting = False
    
    return client

@pytest.mark.asyncio
async def test_connect(client):
    """Test WebSocket connection."""
    # Mock the websockets.connect function
    mock_ws = MockWebSocket([
        json.dumps({"type": "REGISTER_ACK", "status": "registered"})
    ])
    
    with patch('websockets.connect', return_value=AsyncMock(return_value=mock_ws)):
        result = await client.connect()
        assert result is True
        assert client.connected is True
        assert client.connecting is False
        
        # Verify registration message was sent
        assert len(mock_ws.sent_messages) == 1
        reg_msg = json.loads(mock_ws.sent_messages[0])
        assert reg_msg["type"] == "REGISTER"
        assert reg_msg["component_id"] == "test-component"

@pytest.mark.asyncio
async def test_disconnect(connected_client):
    """Test WebSocket disconnection."""
    await connected_client.disconnect()
    assert connected_client.ws.closed is True
    assert connected_client.connected is False
    assert connected_client.connecting is False
    assert connected_client.should_reconnect is False

@pytest.mark.asyncio
async def test_generate(connected_client):
    """Test generate method."""
    # Setup mock response
    response_future = asyncio.Future()
    response_future.set_result({
        "content": "This is a test response",
        "model": "test-model",
        "provider": "test-provider",
        "context_id": "test-context",
        "timestamp": "2024-01-01T00:00:00Z"
    })
    
    # Register the future as a handler
    request_id = None
    
    # Mock the send method to capture the request ID
    original_send = connected_client.ws.send
    async def mock_send(message):
        nonlocal request_id
        await original_send(message)
        data = json.loads(message)
        if data.get("type") == "GENERATE":
            request_id = data.get("request_id")
            # Register the handler
            connected_client.message_handlers[request_id] = response_future
    
    connected_client.ws.send = mock_send
    
    # Call generate
    response = await connected_client.generate(
        prompt="Test prompt",
        context_id="test-context",
        system_prompt="Test system prompt"
    )
    
    # Check response
    assert response["content"] == "This is a test response"
    assert response["model"] == "test-model"
    assert response["provider"] == "test-provider"
    
    # Check request was sent correctly
    assert len(connected_client.ws.sent_messages) == 1
    request = json.loads(connected_client.ws.sent_messages[0])
    assert request["type"] == "GENERATE"
    assert request["prompt"] == "Test prompt"
    assert request["context_id"] == "test-context"
    assert request["options"] == {}
    assert "system_prompt" in request

@pytest.mark.asyncio
async def test_stream(connected_client):
    """Test stream method."""
    # Create a callback for testing
    chunks = []
    def callback(chunk):
        chunks.append(chunk)
    
    # Call stream
    request_id = await connected_client.stream(
        prompt="Test prompt",
        callback=callback,
        context_id="test-context"
    )
    
    # Check request was sent
    assert len(connected_client.ws.sent_messages) == 1
    request = json.loads(connected_client.ws.sent_messages[0])
    assert request["type"] == "STREAM"
    assert request["prompt"] == "Test prompt"
    assert request["context_id"] == "test-context"
    
    # Verify the callback was registered
    assert request_id in connected_client.message_handlers
    assert connected_client.message_handlers[request_id] == callback
    
    # Simulate receiving chunks
    for i in range(3):
        chunk = StreamingChunk(
            chunk=f"Chunk {i} ",
            context_id="test-context",
            model="test-model",
            provider="test-provider",
            timestamp="2024-01-01T00:00:00Z",
            done=i == 2
        )
        await connected_client._handle_message({
            "type": "CHUNK",
            "request_id": request_id,
            "chunk": chunk.chunk,
            "context_id": chunk.context_id,
            "model": chunk.model,
            "provider": chunk.provider,
            "timestamp": chunk.timestamp,
            "done": chunk.done
        })
    
    # Check chunks were received
    assert len(chunks) == 3
    assert chunks[0].chunk == "Chunk 0 "
    assert chunks[1].chunk == "Chunk 1 "
    assert chunks[2].chunk == "Chunk 2 "
    assert chunks[2].done == True
    
    # Check handler was removed after completion
    assert request_id not in connected_client.message_handlers

@pytest.mark.asyncio
async def test_cancel(connected_client):
    """Test cancel method."""
    # Create a mock for testing
    callback = MagicMock()
    
    # Register a fake request
    request_id = "test-request-id"
    connected_client.message_handlers[request_id] = callback
    
    # Cancel the request
    result = await connected_client.cancel(request_id)
    
    # Check cancellation request was sent
    assert result is True
    assert len(connected_client.ws.sent_messages) == 1
    cancel_msg = json.loads(connected_client.ws.sent_messages[0])
    assert cancel_msg["type"] == "CANCEL"
    assert cancel_msg["request_id"] == request_id
    
    # Check handler was removed
    assert request_id not in connected_client.message_handlers

@pytest.mark.asyncio
async def test_error_handling(connected_client):
    """Test error handling in message processing."""
    # Mock process_messages to test error handling
    original_process = connected_client._process_messages
    
    # Create an error future for testing
    error_future = asyncio.Future()
    
    # Create a request ID and register handler
    request_id = "test-request-id"
    connected_client.message_handlers[request_id] = error_future
    
    # Simulate an error message
    await connected_client._handle_message({
        "type": "ERROR",
        "request_id": request_id,
        "error": "Test error message"
    })
    
    # Check that the future was rejected with the error
    assert error_future.exception() is not None
    assert "Test error message" in str(error_future.exception())
    
    # Check handler was removed
    assert request_id not in connected_client.message_handlers

if __name__ == "__main__":
    pytest.main(["-xvs", "test_ws_client.py"])