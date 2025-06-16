"""
Pytest configuration for Metis tests.

This module provides fixtures and setup/teardown functionality for Metis tests.
"""

import pytest
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Async event loop fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an asyncio event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Temp file fixture
@pytest.fixture
def temp_file():
    """Create a temporary file for tests."""
    with tempfile.NamedTemporaryFile() as f:
        yield f.name