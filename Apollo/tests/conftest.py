"""
Pytest configuration file for Apollo tests.
"""

import os
import tempfile
import asyncio
import pytest
from unittest.mock import AsyncMock

# Set event loop policy for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create and yield an event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Create a temporary directory for tests
@pytest.fixture(scope="function")
def temp_test_dir():
    """Create and yield a temporary directory for tests."""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    import shutil
    shutil.rmtree(test_dir)

# Mock Rhetor interface
@pytest.fixture
def mock_rhetor():
    """Create and yield a mock RhetorInterface."""
    mock = AsyncMock()
    mock.get_active_sessions.return_value = []
    return mock

# Mock Hermes client
@pytest.fixture
def mock_hermes():
    """Create and yield a mock HermesClient."""
    mock = AsyncMock()
    mock.send_message.return_value = True
    mock.send_batch.return_value = True
    mock.subscribe.return_value = "test-subscription-id"
    mock.unsubscribe.return_value = True
    return mock