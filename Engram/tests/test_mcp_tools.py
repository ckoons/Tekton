#!/usr/bin/env python3
"""
Test suite for Engram MCP Tools.

Tests all MCP tool connections and functionality including:
- Core memory operations
- Cross-CI memory sharing
- Whisper channels
- Memory persistence
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add parent directory and project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Add Coder-C to path

# Set environment to avoid shared.env dependency
os.environ['TEKTON_ROOT'] = str(Path(__file__).parent.parent.parent)

try:
    from engram.core.mcp.tools import (
        # Core memory tools
        memory_store,
        memory_query,
        memory_recall,
        memory_search,
        get_context,
        # Shared memory tools
        shared_memory_store,
        shared_memory_recall,
        memory_gift,
        memory_broadcast,
        whisper_send,
        whisper_receive
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Attempting direct import...")
    # Try direct import path
    sys.path.insert(0, str(Path(__file__).parent.parent / "engram"))
    from core.mcp.tools import (
        memory_store,
        memory_query,
        memory_recall,
        memory_search,
        get_context,
        shared_memory_store,
        shared_memory_recall,
        memory_gift,
        memory_broadcast,
        whisper_send,
        whisper_receive
    )


class TestCoreMCPTools:
    """Test core memory MCP tools."""
    
    @pytest.mark.asyncio
    async def test_memory_store(self):
        """Test storing memory via MCP tool."""
        result = await memory_store(
            content="Test memory from MCP tool test suite",
            namespace="conversations",
            metadata={"test": True, "suite": "mcp_tools"}
        )
        
        assert result["success"] == True
        assert result["namespace"] == "conversations"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_memory_query(self):
        """Test querying memory via MCP tool."""
        # First store a memory
        await memory_store(
            content="Unique test content XYZ123",
            namespace="conversations"
        )
        
        # Then query it
        result = await memory_query(
            query="XYZ123",
            namespace="conversations",
            limit=5
        )
        
        assert "results" in result
        assert isinstance(result["results"], list)
        # Should find our test memory
        found = any("XYZ123" in r.get("content", "") for r in result["results"])
        assert found, "Should find the test memory we stored"
    
    @pytest.mark.asyncio
    async def test_memory_recall_alias(self):
        """Test that MemoryRecall is an alias for MemoryQuery."""
        # Store a test memory
        await memory_store(
            content="Recall test ABC789",
            namespace="thinking"
        )
        
        # Test recall
        result = await memory_recall(
            query="ABC789",
            namespace="thinking"
        )
        
        assert "results" in result
        assert isinstance(result["results"], list)
    
    @pytest.mark.asyncio
    async def test_memory_search_vector(self):
        """Test vector search functionality."""
        # Store semantic test data
        await memory_store(
            content="The weather is sunny and warm today",
            namespace="conversations"
        )
        
        # Search semantically similar
        result = await memory_search(
            query="bright hot day",
            namespace="conversations"
        )
        
        assert "results" in result
        assert isinstance(result["results"], list)
    
    @pytest.mark.asyncio
    async def test_get_context(self):
        """Test multi-namespace context retrieval."""
        # Store memories in different namespaces
        await memory_store("Context test in conversations", "conversations")
        await memory_store("Context test in thinking", "thinking")
        await memory_store("Context test in longterm", "longterm")
        
        # Get context across namespaces
        result = await get_context(
            query="context test",
            namespaces=["conversations", "thinking", "longterm"],
            limit=2
        )
        
        assert result["success"] == True
        assert "context" in result
        assert isinstance(result["context"], str)


class TestSharedMemoryTools:
    """Test cross-CI memory sharing tools."""
    
    @pytest.mark.asyncio
    async def test_shared_memory_store(self):
        """Test storing memory in shared space."""
        result = await shared_memory_store(
            content="Shared discovery about MCP tools",
            space="collective",
            attribution="test_suite",
            emotion="confident",
            confidence=0.9
        )
        
        assert result["success"] == True
        assert result["space"] == "collective"
        assert result["namespace"] == "shared-collective"
    
    @pytest.mark.asyncio
    async def test_shared_memory_recall(self):
        """Test recalling from shared spaces."""
        # Store in shared space
        await shared_memory_store(
            content="Test shared memory DEF456",
            space="collective",
            attribution="test_ci"
        )
        
        # Recall from shared space
        result = await shared_memory_recall(
            query="DEF456",
            space="collective"
        )
        
        assert "results" in result
        assert result["space"] == "collective"
    
    @pytest.mark.asyncio
    async def test_memory_gift(self):
        """Test gifting memory between CIs."""
        result = await memory_gift(
            content="Here's a helpful insight",
            from_ci="CI_A",
            to_ci="CI_B",
            message="Hope this helps!"
        )
        
        assert result["success"] == True
        assert result["from"] == "CI_A"
        assert result["to"] == "CI_B"
    
    @pytest.mark.asyncio
    async def test_memory_broadcast(self):
        """Test broadcasting to all CIs."""
        result = await memory_broadcast(
            content="Important discovery!",
            from_ci="test_ci",
            importance="high",
            category="breakthrough"
        )
        
        assert result["success"] == True
        assert result["importance"] == "high"
        assert result["category"] == "breakthrough"
    
    @pytest.mark.asyncio
    async def test_whisper_send(self):
        """Test private whisper between CIs."""
        result = await whisper_send(
            content="Private context for you",
            from_ci="Apollo",
            to_ci="Rhetor"
        )
        
        assert result["success"] == True
        assert result["from"] == "Apollo"
        assert result["to"] == "Rhetor"
    
    @pytest.mark.asyncio
    async def test_whisper_receive(self):
        """Test receiving whispers."""
        # First send a whisper
        await whisper_send(
            content="Test whisper GHI789",
            from_ci="Apollo",
            to_ci="Rhetor"
        )
        
        # Then receive it
        result = await whisper_receive(
            ci_name="Rhetor",
            from_ci="Apollo"
        )
        
        assert "results" in result
        assert result["whisper_channel"] == "Apollo -> Rhetor"


class TestMemoryPersistence:
    """Test memory persistence across sessions."""
    
    @pytest.mark.asyncio
    async def test_persistence_marker(self):
        """Test that memories persist (LanceDB handles this)."""
        # Store a unique persistence marker
        marker = f"PERSIST_TEST_MARKER_999"
        result = await memory_store(
            content=marker,
            namespace="longterm",
            metadata={"persistence_test": True}
        )
        
        assert result["success"] == True
        
        # Query it back immediately
        result = await memory_query(
            query=marker,
            namespace="longterm"
        )
        
        assert result.get("count", 0) > 0
        # Note: Actual restart testing would require stopping/starting the service


class TestExperientialMetadata:
    """Test experiential memory features."""
    
    @pytest.mark.asyncio
    async def test_emotion_metadata(self):
        """Test storing memories with emotional context."""
        result = await shared_memory_store(
            content="I successfully connected the MCP tools!",
            space="collective",
            attribution="Cari",
            emotion="excited",
            confidence=0.95
        )
        
        assert result["success"] == True
        # The metadata should be stored (verification would require querying)
    
    @pytest.mark.asyncio
    async def test_confidence_levels(self):
        """Test confidence levels in shared memories."""
        # Store with low confidence
        await shared_memory_store(
            content="I think this might work",
            space="collective",
            attribution="uncertain_ci",
            confidence=0.3
        )
        
        # Store with high confidence
        result = await shared_memory_store(
            content="This definitely works!",
            space="collective",
            attribution="confident_ci",
            confidence=1.0
        )
        
        assert result["success"] == True


class TestErrorHandling:
    """Test error handling in MCP tools."""
    
    @pytest.mark.asyncio
    async def test_invalid_namespace_fallback(self):
        """Test that invalid namespaces fall back gracefully."""
        # This should work even with a completely new namespace
        result = await memory_store(
            content="Test content",
            namespace="completely-new-namespace"
        )
        
        # Should either succeed or fall back to conversations
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_whisper_requires_sender(self):
        """Test that whisper receive requires a sender."""
        result = await whisper_receive(
            ci_name="Rhetor",
            from_ci=None  # Should fail
        )
        
        assert result["success"] == False
        assert "error" in result


# Simple standalone test runner
async def run_basic_tests():
    """Run basic tests without pytest."""
    print("Running basic MCP tools tests...")
    
    # Test 1: Store and retrieve
    print("\n1. Testing memory store and query...")
    store_result = await memory_store("Test memory 123", "conversations")
    print(f"   Store: {store_result['success']}")
    
    query_result = await memory_query("Test memory", "conversations")
    print(f"   Query: Found {query_result.get('count', 0)} results")
    
    # Test 2: Shared memory
    print("\n2. Testing shared memory...")
    shared_result = await shared_memory_store(
        "Shared test",
        space="collective",
        attribution="test"
    )
    print(f"   Shared store: {shared_result['success']}")
    
    # Test 3: Whisper
    print("\n3. Testing whisper...")
    whisper_result = await whisper_send(
        "Secret message",
        from_ci="A",
        to_ci="B"
    )
    print(f"   Whisper: {whisper_result['success']}")
    
    print("\nBasic tests complete!")


# Run tests
if __name__ == "__main__":
    import sys
    if "--basic" in sys.argv:
        # Run basic tests without pytest
        asyncio.run(run_basic_tests())
    else:
        # Run with pytest
        pytest.main([__file__, "-v", "--asyncio-mode=auto"])