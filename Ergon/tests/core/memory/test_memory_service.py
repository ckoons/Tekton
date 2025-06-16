"""
Tests for the memory service.

These tests verify functionality of the Ergon memory system.
"""

import os
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

from ergon.core.memory.service import MemoryService
from ergon.core.memory.utils.categories import MemoryCategory

# Pytest fixture for the memory service
@pytest.fixture
def memory_service():
    """Create a memory service for testing."""
    # Mock the get_db_session function
    with patch('ergon.core.memory.service.get_db_session') as mock_db:
        # Create a mock db session that returns a mock agent
        mock_session = MagicMock()
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        
        # Set up the mock query chain
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_first = MagicMock(return_value=mock_agent)
        
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_first
        mock_session.query.return_value = mock_query
        
        # Set up the context manager
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_session
        mock_db.return_value = mock_cm
        
        # Mock the vector store
        with patch('ergon.core.memory.service.MemoryVectorService') as mock_vector_store:
            # Create a mock vector store instance
            mock_vs_instance = MagicMock()
            mock_vector_store.return_value = mock_vs_instance
            
            # Mock the add_memory method
            async def mock_add_memory(*args, **kwargs):
                return "mock_memory_id"
            mock_vs_instance.add_memory = mock_add_memory
            
            # Mock the search method
            async def mock_search(*args, **kwargs):
                return [
                    {
                        "id": "mock_memory_id_1",
                        "content": "Test memory content 1",
                        "metadata": {
                            "category": "factual",
                            "importance": 3,
                            "timestamp": datetime.now().timestamp()
                        },
                        "score": 0.95
                    }
                ]
            mock_vs_instance.search = mock_search
            
            # Create the memory service
            service = MemoryService(agent_id=999)
            
            # Mock the embedding service
            with patch('ergon.core.memory.service.embedding_service') as mock_embedding:
                async def mock_embed_text(*args, **kwargs):
                    return [0.1] * 384  # Mock embedding
                mock_embedding.embed_text = mock_embed_text
                
                yield service

# Test adding a memory
@pytest.mark.asyncio
async def test_add_memory(memory_service):
    """Test adding a memory."""
    # Call the add_memory method
    memory_id = await memory_service.add_memory(
        content="This is a test memory",
        category=MemoryCategory.FACTUAL,
        importance=4
    )
    
    # Assert that we got a memory ID back
    assert memory_id == "mock_memory_id"

# Test searching for memories
@pytest.mark.asyncio
async def test_search_memories(memory_service):
    """Test searching for memories."""
    # Call the search method
    memories = await memory_service.search(
        query="test query",
        categories=[MemoryCategory.FACTUAL],
        min_importance=3
    )
    
    # Assert that we got memories back
    assert len(memories) == 1
    assert memories[0]["content"] == "Test memory content 1"
    assert memories[0]["category"] == "factual"
    assert memories[0]["importance"] == 3

# Test getting relevant context
@pytest.mark.asyncio
async def test_get_relevant_context(memory_service):
    """Test getting relevant context."""
    # Call the get_relevant_context method
    context = await memory_service.get_relevant_context(
        query="test query",
        categories=[MemoryCategory.FACTUAL],
        min_importance=3
    )
    
    # Assert that we got context back
    assert "relevant memories" in context
    assert "Test memory content 1" in context