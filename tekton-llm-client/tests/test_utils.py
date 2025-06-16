import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from tekton_llm_client.utils import (
    count_tokens, count_message_tokens, 
    truncate_text_to_token_limit, optimize_messages_for_token_limit,
    StreamProcessor, StreamBuffer,
    RetryConfig, retry_async
)
from tekton_llm_client.models import StreamingChunk
from tekton_llm_client.exceptions import ConnectionError, TimeoutError, ServiceUnavailableError

#
# Token Counting Tests
#

def test_count_tokens():
    """Test token counting."""
    # Basic token counting
    text = "This is a test sentence."
    count = count_tokens(text)
    assert count >= 5  # Rough estimate
    
    # Empty string
    assert count_tokens("") == 1
    
    # Long text
    long_text = "This is a much longer text that should have many more tokens. " * 10
    long_count = count_tokens(long_text)
    assert long_count > count

def test_count_message_tokens():
    """Test message token counting."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thanks for asking!"}
    ]
    
    count = count_message_tokens(messages)
    
    # Basic validation
    assert count["prompt_tokens"] > 0
    assert count["total_tokens"] > 0

def test_truncate_text_to_token_limit():
    """Test text truncation by token limit."""
    text = "This is a test sentence. " * 100
    truncated = truncate_text_to_token_limit(text, max_tokens=10)
    
    # The truncated text should be shorter
    assert len(truncated) < len(text)
    
    # Text already under the limit should not be truncated
    short_text = "Short text."
    assert truncate_text_to_token_limit(short_text, max_tokens=10) == short_text

def test_optimize_messages_for_token_limit():
    """Test message optimization for token limits."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
        {"role": "user", "content": "Tell me about AI." + " This is a long text." * 100}
    ]
    
    # Optimize with a small token limit
    optimized = optimize_messages_for_token_limit(messages, max_tokens=50)
    
    # Should keep system prompt but reduce messages
    assert len(optimized) < len(messages)
    assert optimized[0]["role"] == "system"
    
    # With a very small limit, might only keep system prompt
    very_optimized = optimize_messages_for_token_limit(messages, max_tokens=10)
    assert len(very_optimized) < len(optimized)

#
# Streaming Tests
#

def test_stream_processor():
    """Test StreamProcessor functionality."""
    processor = StreamProcessor()
    
    # Process some chunks
    chunks = [
        StreamingChunk(
            chunk="Hello, ",
            context_id="test",
            model="test-model",
            provider="test-provider",
            timestamp="2024-01-01T00:00:00Z",
            done=False
        ),
        StreamingChunk(
            chunk="world!",
            context_id="test",
            model="test-model",
            provider="test-provider",
            timestamp="2024-01-01T00:00:00Z",
            done=True
        )
    ]
    
    for chunk in chunks:
        processor.process_chunk(chunk)
    
    # Check results
    assert processor.get_result() == "Hello, world!"
    assert len(processor.get_chunks()) == 2
    assert processor.is_complete is True
    assert processor.has_error is False

def test_stream_processor_with_error():
    """Test StreamProcessor with error handling."""
    processor = StreamProcessor()
    
    # Process a chunk with an error
    error_chunk = StreamingChunk(
        chunk="",
        context_id="test",
        model="test-model",
        provider="test-provider",
        timestamp="2024-01-01T00:00:00Z",
        done=True,
        error="Test error"
    )
    
    processor.process_chunk(error_chunk)
    
    # Check error state
    assert processor.is_complete is True
    assert processor.has_error is True
    assert processor.error == "Test error"

@pytest.mark.asyncio
async def test_stream_processor_with_stream():
    """Test StreamProcessor with async stream."""
    async def mock_stream():
        chunks = [
            StreamingChunk(
                chunk="Hello, ",
                context_id="test",
                model="test-model",
                provider="test-provider",
                timestamp="2024-01-01T00:00:00Z",
                done=False
            ),
            StreamingChunk(
                chunk="world!",
                context_id="test",
                model="test-model",
                provider="test-provider",
                timestamp="2024-01-01T00:00:00Z",
                done=True
            )
        ]
        for chunk in chunks:
            yield chunk
    
    processor = StreamProcessor()
    result = await processor.process_stream(mock_stream())
    
    assert result == "Hello, world!"
    assert len(processor.get_chunks()) == 2
    assert processor.is_complete is True

@pytest.mark.asyncio
async def test_stream_buffer():
    """Test StreamBuffer functionality."""
    buffer = StreamBuffer()
    
    # Add some chunks
    chunks = [
        StreamingChunk(
            chunk="Hello, ",
            context_id="test",
            model="test-model",
            provider="test-provider",
            timestamp="2024-01-01T00:00:00Z",
            done=False
        ),
        StreamingChunk(
            chunk="world!",
            context_id="test",
            model="test-model",
            provider="test-provider",
            timestamp="2024-01-01T00:00:00Z",
            done=True
        )
    ]
    
    for chunk in chunks:
        await buffer.add_chunk(chunk)
    
    # Get chunks
    received_chunks = []
    async for chunk in buffer.get_chunks():
        received_chunks.append(chunk)
    
    # Check results
    assert len(received_chunks) == 2
    assert buffer.get_combined_text() == "Hello, world!"
    assert buffer.is_done() is True
    assert buffer.has_error() is False

#
# Retry Tests
#

def test_retry_config():
    """Test RetryConfig functionality."""
    config = RetryConfig(
        max_retries=3,
        base_delay=100,
        max_delay=1000,
        jitter=True
    )
    
    # Test retry decision
    assert config.should_retry(ConnectionError("Test"), 0) is True
    assert config.should_retry(ConnectionError("Test"), 1) is True
    assert config.should_retry(ConnectionError("Test"), 2) is True
    assert config.should_retry(ConnectionError("Test"), 3) is False  # Exceeded max
    
    # Test delay calculation
    delay_1 = config.get_delay(0)
    delay_2 = config.get_delay(1)
    delay_3 = config.get_delay(2)
    
    assert delay_1 < delay_2 < delay_3  # Exponential backoff
    assert 0.08 <= delay_1 <= 0.12  # ~100ms with jitter
    assert 0.16 <= delay_2 <= 0.24  # ~200ms with jitter
    assert 0.32 <= delay_3 <= 0.48  # ~400ms with jitter

@pytest.mark.asyncio
async def test_retry_async():
    """Test retry_async functionality."""
    # Mock operation that fails twice then succeeds
    counter = 0
    async def mock_operation():
        nonlocal counter
        counter += 1
        if counter < 3:
            raise ConnectionError("Test error")
        return "Success"
    
    # Configure retry
    config = RetryConfig(max_retries=3, base_delay=10)
    
    # Test retry
    result = await retry_async(mock_operation, config)
    
    assert result == "Success"
    assert counter == 3  # Called 3 times (2 failures, 1 success)

@pytest.mark.asyncio
async def test_retry_async_max_retries_exceeded():
    """Test retry_async when max retries is exceeded."""
    # Mock operation that always fails
    async def mock_operation():
        raise ConnectionError("Test error")
    
    # Configure retry
    config = RetryConfig(max_retries=2, base_delay=10)
    
    # Test retry
    with pytest.raises(ConnectionError):
        await retry_async(mock_operation, config)

@pytest.mark.asyncio
async def test_retry_async_non_retryable_error():
    """Test retry_async with non-retryable error."""
    # Mock operation that fails with non-retryable error
    async def mock_operation():
        raise ValueError("Non-retryable error")
    
    # Configure retry
    config = RetryConfig(max_retries=3, base_delay=10)
    
    # Test retry
    with pytest.raises(ValueError):
        await retry_async(mock_operation, config)

if __name__ == "__main__":
    pytest.main(["-xvs", "test_utils.py"])