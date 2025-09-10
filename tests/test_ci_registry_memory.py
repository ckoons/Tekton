#!/usr/bin/env python3
"""
Test CI Registry Memory Integration.

Tests the integration between CI Registry and ESR memory system.
"""

import asyncio
import json
import pytest
import httpx
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.aish.src.registry.ci_registry import CIRegistry


class TestCIRegistryMemory:
    """Test CI Registry memory integration."""
    
    @pytest.fixture
    def registry(self):
        """Create a test registry instance."""
        with patch('shared.aish.src.registry.file_registry.FileRegistry'):
            registry = CIRegistry()
            registry._esr_client = AsyncMock()
            registry._memory_metadata = {}
            registry._context_state = {}
            registry._registry = {}
            return registry
    
    @pytest.fixture
    def mock_esr_response(self):
        """Mock ESR API responses."""
        return {
            "store": {
                "status": "success",
                "memory_id": "test_memory_123"
            },
            "search": {
                "status": "success",
                "results": [
                    {"content": "Memory 1", "confidence": 0.9},
                    {"content": "Memory 2", "confidence": 0.8},
                    {"content": "Memory 3", "confidence": 0.7}
                ],
                "count": 3
            },
            "reflect": {
                "status": "success",
                "action": "reflection_triggered"
            },
            "context": {
                "status": "success",
                "context": {
                    "primary": ["thought1", "thought2"],
                    "associated": ["related1", "related2"]
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_store_ci_memory(self, registry, mock_esr_response):
        """Test storing a CI memory."""
        # Mock the ESR client response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_esr_response["store"]
        
        registry._esr_client.post = AsyncMock(return_value=mock_response)
        
        # Store a memory
        memory_id = await registry.store_ci_memory(
            ci_name="apollo",
            content="Test memory content",
            thought_type="IDEA",
            confidence=0.95
        )
        
        # Verify the memory was stored
        assert memory_id == "test_memory_123"
        
        # Check metadata was updated
        assert "apollo" in registry._memory_metadata
        assert registry._memory_metadata["apollo"]["memory_count"] == 1
        assert registry._memory_metadata["apollo"]["last_stored"] is not None
    
    @pytest.mark.asyncio
    async def test_recall_ci_memories(self, registry, mock_esr_response):
        """Test recalling CI memories."""
        # Mock the ESR client response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_esr_response["search"]
        
        registry._esr_client.post = AsyncMock(return_value=mock_response)
        
        # Recall memories
        memories = await registry.recall_ci_memories(
            ci_name="apollo",
            query="test query",
            limit=10
        )
        
        # Verify memories were recalled
        assert len(memories) == 3
        assert memories[0]["content"] == "Memory 1"
        assert memories[0]["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_trigger_ci_reflection(self, registry, mock_esr_response):
        """Test triggering CI reflection."""
        # Mock the ESR client response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_esr_response["reflect"]
        
        registry._esr_client.post = AsyncMock(return_value=mock_response)
        
        # Trigger reflection
        success = await registry.trigger_ci_reflection(
            ci_name="apollo",
            reason="test_trigger"
        )
        
        # Verify reflection was triggered
        assert success is True
        
        # Check metadata was updated
        assert "apollo" in registry._memory_metadata
        assert registry._memory_metadata["apollo"]["last_reflection"] is not None
    
    @pytest.mark.asyncio
    async def test_get_ci_memory_context(self, registry, mock_esr_response):
        """Test getting memory context."""
        # Mock the ESR client response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_esr_response["context"]
        
        registry._esr_client.post = AsyncMock(return_value=mock_response)
        
        # Get context
        context = await registry.get_ci_memory_context(
            ci_name="apollo",
            topic="test topic",
            depth=3
        )
        
        # Verify context was retrieved
        assert context is not None
        assert "primary" in context
        assert len(context["primary"]) == 2
    
    def test_should_trigger_reflection_no_history(self, registry):
        """Test reflection trigger with no history."""
        # No metadata yet
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is False
        
        # Add some memories but no reflection yet
        registry._memory_metadata["apollo"] = {
            "memory_count": 10,
            "last_stored": datetime.now().isoformat(),
            "last_reflection": None
        }
        
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is True
    
    def test_should_trigger_reflection_time_based(self, registry):
        """Test time-based reflection trigger."""
        # Recent reflection
        registry._memory_metadata["apollo"] = {
            "memory_count": 10,
            "last_stored": datetime.now().isoformat(),
            "last_reflection": datetime.now().isoformat()
        }
        
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is False
        
        # Old reflection (2 hours ago)
        old_time = datetime.now() - timedelta(hours=2)
        registry._memory_metadata["apollo"]["last_reflection"] = old_time.isoformat()
        
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is False  # Still under threshold
    
    def test_should_trigger_reflection_count_based(self, registry):
        """Test count-based reflection trigger."""
        # Exactly at threshold with old reflection (to pass time check)
        old_time = datetime.now() - timedelta(hours=2)
        registry._memory_metadata["apollo"] = {
            "memory_count": 50,
            "last_stored": datetime.now().isoformat(),
            "last_reflection": old_time.isoformat()
        }
        
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is True  # 50 is divisible by 50
        
        # Multiple of threshold
        registry._memory_metadata["apollo"]["memory_count"] = 100
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is True
        
        # Not at threshold
        registry._memory_metadata["apollo"]["memory_count"] = 49
        should_trigger = registry.should_trigger_reflection("apollo")
        assert should_trigger is False
    
    def test_update_ci_last_output_with_memory(self, registry):
        """Test that update_ci_last_output stores memories."""
        # Mock async operations
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.is_running.return_value = True
            
            # Register a CI first
            registry._registry["apollo"] = {
                "name": "apollo",
                "type": "greek"
            }
            
            # Update output
            success = registry.update_ci_last_output("apollo", {
                "user_message": "Test question",
                "content": "Test response"
            })
            
            assert success is True
            assert "apollo" in registry._context_state
            assert registry._context_state["apollo"]["last_output"]["content"] == "Test response"
    
    def test_sunset_detection_triggers_reflection(self, registry):
        """Test that sunset detection triggers reflection."""
        # Mock async operations
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.is_running.return_value = True
            
            # Register a CI
            registry._registry["apollo"] = {
                "name": "apollo",
                "type": "greek"
            }
            
            # Create sunset response
            sunset_output = {
                "user_message": "SUNSET_PROTOCOL",
                "content": """
                Current context: Working on ESR implementation
                Key decisions: Using universal encoding
                Next steps: Test the system
                Current approach: Store everywhere, synthesize on recall
                Task trajectory: Implementation complete
                """
            }
            
            # Update with sunset output
            success = registry.update_ci_last_output("apollo", sunset_output)
            
            assert success is True
            # Check that sunrise_context was set
            assert "apollo" in registry._context_state
            assert registry._context_state["apollo"]["sunrise_context"] is not None
    
    def test_get_sunrise_context_with_memories(self, registry, mock_esr_response):
        """Test that sunrise context includes memories."""
        # Set base sunrise context
        registry._context_state["apollo"] = {
            "sunrise_context": "Base context from sunset"
        }
        
        # Mock the recall_ci_memories method to return test memories
        async def mock_recall(*args, **kwargs):
            return mock_esr_response["search"]["results"]
        
        registry.recall_ci_memories = mock_recall
        
        # Mock event loop
        with patch('asyncio.new_event_loop') as mock_new_loop:
            mock_loop = MagicMock()
            mock_new_loop.return_value = mock_loop
            
            # Make run_until_complete return the memories
            mock_loop.run_until_complete.return_value = mock_esr_response["search"]["results"]
            mock_loop.close = MagicMock()
            
            # Get enriched context
            context = registry.get_sunrise_context("apollo")
            
            # Verify context includes memories
            assert "Base context from sunset" in context
            assert "Recent memories:" in context
            assert "Memory 1" in context


class TestMemoryIntegration:
    """Integration tests for memory system."""
    
    @pytest.mark.asyncio
    async def test_full_memory_lifecycle(self):
        """Test complete memory lifecycle."""
        # This test requires Engram to be running
        try:
            async with httpx.AsyncClient() as client:
                # Check if Engram is running
                response = await client.get("http://localhost:8100/api/esr/status")
                if response.status_code != 200:
                    pytest.skip("Engram not running")
                
                # Store a memory
                store_response = await client.post(
                    "http://localhost:8100/api/esr/store",
                    json={
                        "content": "Test memory for lifecycle",
                        "thought_type": "MEMORY",
                        "ci_id": "test_ci",
                        "confidence": 0.9
                    }
                )
                assert store_response.status_code == 200
                memory_id = store_response.json()["memory_id"]
                
                # Recall the memory
                recall_response = await client.get(
                    f"http://localhost:8100/api/esr/recall/{memory_id}?ci_id=test_ci"
                )
                assert recall_response.status_code == 200
                recalled = recall_response.json()
                assert recalled["memory"]["content"] == "Test memory for lifecycle"
                
                # Search for similar
                search_response = await client.post(
                    "http://localhost:8100/api/esr/search",
                    json={
                        "query": "lifecycle",
                        "ci_id": "test_ci",
                        "limit": 5
                    }
                )
                assert search_response.status_code == 200
                
                # Build context
                context_response = await client.post(
                    "http://localhost:8100/api/esr/context",
                    json={
                        "topic": "testing",
                        "depth": 2,
                        "ci_id": "test_ci"
                    }
                )
                assert context_response.status_code == 200
                
                # Trigger reflection
                reflect_response = await client.post(
                    "http://localhost:8100/api/esr/reflect",
                    json={
                        "ci_id": "test_ci",
                        "reason": "test_complete"
                    }
                )
                assert reflect_response.status_code == 200
                
        except httpx.ConnectError:
            pytest.skip("Cannot connect to Engram")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])