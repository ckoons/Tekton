#!/usr/bin/env python3
"""
Test ESR MCP Tools.

Tests the ESR MCP tool implementations.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from engram.core.mcp.esr_tools import (
    esr_store_thought,
    esr_recall_thought,
    esr_search_similar,
    esr_build_context,
    esr_create_association,
    esr_get_metabolism_status,
    esr_trigger_reflection,
    esr_get_namespaces,
    get_esr_system
)
from engram.core.storage.cognitive_workflows import ThoughtType, Thought


class TestESRTools:
    """Test ESR MCP tools."""
    
    @pytest.fixture
    def mock_esr_system(self):
        """Create mock ESR system and cognitive workflows."""
        mock_system = AsyncMock()
        mock_workflows = AsyncMock()
        
        # Mock the cache and encoder attributes
        mock_system.cache = AsyncMock()
        mock_system.encoder = AsyncMock()
        
        return mock_system, mock_workflows
    
    @pytest.mark.asyncio
    async def test_store_thought(self, mock_esr_system):
        """Test storing a thought."""
        mock_system, mock_workflows = mock_esr_system
        
        # Mock the store_thought method
        mock_workflows.store_thought = AsyncMock(return_value="memory_id_123")
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_store_thought(
                content="Test thought",
                thought_type="IDEA",
                context={"test": True},
                confidence=0.9,
                ci_id="test_ci"
            )
        
        assert result["status"] == "success"
        assert result["memory_id"] == "memory_id_123"
        assert "timestamp" in result
        
        # Verify the method was called correctly
        mock_workflows.store_thought.assert_called_once()
        call_args = mock_workflows.store_thought.call_args[1]
        assert call_args["content"] == "Test thought"
        assert call_args["thought_type"] == ThoughtType.IDEA
        assert call_args["confidence"] == 0.9
        assert call_args["ci_id"] == "test_ci"
    
    @pytest.mark.asyncio
    async def test_recall_thought_found(self, mock_esr_system):
        """Test recalling an existing thought."""
        mock_system, mock_workflows = mock_esr_system
        
        # Mock thought object
        mock_thought = Mock(spec=Thought)
        mock_thought.to_dict.return_value = {
            "content": "Recalled thought",
            "type": "MEMORY",
            "confidence": 0.8
        }
        
        mock_workflows.recall_thought = AsyncMock(return_value=mock_thought)
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_recall_thought(
                memory_id="memory_123",
                ci_id="test_ci"
            )
        
        assert result["status"] == "success"
        assert result["memory"]["content"] == "Recalled thought"
        assert result["memory"]["type"] == "MEMORY"
    
    @pytest.mark.asyncio
    async def test_recall_thought_not_found(self, mock_esr_system):
        """Test recalling a non-existent thought."""
        mock_system, mock_workflows = mock_esr_system
        
        mock_workflows.recall_thought = AsyncMock(return_value=None)
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_recall_thought(
                memory_id="nonexistent",
                ci_id="test_ci"
            )
        
        assert result["status"] == "not_found"
        assert result["memory_id"] == "nonexistent"
    
    @pytest.mark.asyncio
    async def test_search_similar(self, mock_esr_system):
        """Test searching for similar thoughts."""
        mock_system, mock_workflows = mock_esr_system
        
        # Mock thought objects
        mock_thoughts = []
        for i in range(3):
            thought = Mock(spec=Thought)
            # Mock the ThoughtType enum properly
            mock_type = Mock()
            mock_type.value = "MEMORY"
            thought.thought_type = mock_type
            thought.confidence = 0.9 - (i * 0.1)
            thought.to_dict.return_value = {
                "content": f"Thought {i}",
                "type": "MEMORY",
                "confidence": thought.confidence
            }
            mock_thoughts.append(thought)
        
        mock_workflows.recall_similar = AsyncMock(return_value=mock_thoughts)
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_search_similar(
                query="test query",
                limit=10,
                thought_type="MEMORY",
                min_confidence=0.7,
                ci_id="test_ci"
            )
        
        assert result["status"] == "success"
        assert result["count"] == 3  # All 3 thoughts meet min_confidence (0.9, 0.8, 0.7)
        assert len(result["results"]) == 3
        assert result["results"][0]["confidence"] == 0.9
        assert result["results"][1]["confidence"] == 0.8
    
    @pytest.mark.asyncio
    async def test_build_context(self, mock_esr_system):
        """Test building context around a topic."""
        mock_system, mock_workflows = mock_esr_system
        
        mock_context = {
            "primary": ["thought1", "thought2"],
            "associated": ["related1", "related2"],
            "depth": 3
        }
        
        mock_workflows.build_context = AsyncMock(return_value=mock_context)
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_build_context(
                topic="test topic",
                depth=3,
                max_items=10,
                ci_id="test_ci"
            )
        
        assert result["status"] == "success"
        assert result["context"] == mock_context
        assert result["topic"] == "test topic"
        assert result["depth"] == 3
    
    @pytest.mark.asyncio
    async def test_create_association(self, mock_esr_system):
        """Test creating association between memories."""
        mock_system, mock_workflows = mock_esr_system
        
        mock_workflows.create_association = AsyncMock(return_value=True)
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_create_association(
                from_memory="memory1",
                to_memory="memory2",
                association_type="related",
                strength=0.8,
                ci_id="test_ci"
            )
        
        assert result["status"] == "success"
        assert result["from"] == "memory1"
        assert result["to"] == "memory2"
        assert result["type"] == "related"
    
    @pytest.mark.asyncio
    async def test_get_metabolism_status(self, mock_esr_system):
        """Test getting metabolism status."""
        mock_system, mock_workflows = mock_esr_system
        
        mock_status = {
            "total_memories": 100,
            "promoted": 20,
            "forgotten": 5,
            "reflection_count": 3
        }
        
        mock_workflows.metabolism_stats = mock_status
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_get_metabolism_status(ci_id="test_ci")
        
        assert result["status"] == "success"
        assert result["metabolism"] == mock_status
        assert result["ci_id"] == "test_ci"
    
    @pytest.mark.asyncio
    async def test_trigger_reflection(self, mock_esr_system):
        """Test triggering memory reflection."""
        mock_system, mock_workflows = mock_esr_system
        
        mock_workflows.trigger_reflection = AsyncMock(return_value={
            "reflected": 50,
            "promoted": 10,
            "forgotten": 3
        })
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_trigger_reflection(
                ci_id="test_ci",
                reason="test_trigger"
            )
        
        assert result["status"] == "success"
        assert result["action"] == "reflection_triggered"
        assert result["ci_id"] == "test_ci"
        assert result["reason"] == "test_trigger"
    
    @pytest.mark.asyncio
    async def test_get_namespaces(self, mock_esr_system):
        """Test getting active namespaces."""
        mock_system, mock_workflows = mock_esr_system
        
        # Mock backends with namespaces
        mock_backend1 = Mock()
        mock_backend1.namespace = "apollo"
        mock_backend2 = Mock()
        mock_backend2.namespace = "athena"
        
        mock_system.backends = {
            "backend1": mock_backend1,
            "backend2": mock_backend2
        }
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_get_namespaces()
        
        assert result["status"] == "success"
        assert set(result["namespaces"]) == {"apollo", "athena"}
        assert result["count"] == 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_esr_system):
        """Test error handling in ESR tools."""
        mock_system, mock_workflows = mock_esr_system
        
        # Simulate an error
        mock_workflows.store_thought = AsyncMock(side_effect=Exception("Test error"))
        
        with patch('engram.core.mcp.esr_tools.get_esr_system', AsyncMock(return_value=(mock_system, mock_workflows))):
            result = await esr_store_thought(
                content="Test",
                ci_id="test_ci"
            )
        
        assert result["status"] == "error"
        assert "Test error" in result["error"]


class TestESRSystemInitialization:
    """Test ESR system initialization."""
    
    @pytest.mark.asyncio
    async def test_get_esr_system_initialization(self):
        """Test ESR system initialization."""
        with patch('engram.core.mcp.esr_tools.ESRMemorySystem') as MockESR:
            with patch('engram.core.mcp.esr_tools.CognitiveWorkflows') as MockWorkflows:
                # Setup mocks
                mock_system = AsyncMock()
                mock_system.cache = Mock()
                mock_system.encoder = Mock()
                mock_system.start = AsyncMock()
                
                MockESR.return_value = mock_system
                MockWorkflows.return_value = Mock()
                
                # Reset global state
                import engram.core.mcp.esr_tools as esr_tools
                esr_tools._esr_system = None
                esr_tools._cognitive_workflows = None
                
                # Initialize system
                system, workflows = await get_esr_system()
                
                # Verify initialization
                assert system is not None
                assert workflows is not None
                MockESR.assert_called_once()
                MockWorkflows.assert_called_once_with(
                    cache=mock_system.cache,
                    encoder=mock_system.encoder
                )
                mock_system.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_esr_system_singleton(self):
        """Test that ESR system is a singleton."""
        with patch('engram.core.mcp.esr_tools.ESRMemorySystem') as MockESR:
            with patch('engram.core.mcp.esr_tools.CognitiveWorkflows') as MockWorkflows:
                # Setup mocks
                mock_system = AsyncMock()
                mock_system.cache = Mock()
                mock_system.encoder = Mock()
                mock_system.start = AsyncMock()
                
                MockESR.return_value = mock_system
                MockWorkflows.return_value = Mock()
                
                # Reset global state
                import engram.core.mcp.esr_tools as esr_tools
                esr_tools._esr_system = None
                esr_tools._cognitive_workflows = None
                
                # Get system twice
                system1, workflows1 = await get_esr_system()
                system2, workflows2 = await get_esr_system()
                
                # Should be the same instances
                assert system1 is system2
                assert workflows1 is workflows2
                
                # Should only initialize once
                MockESR.assert_called_once()
                MockWorkflows.assert_called_once()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])