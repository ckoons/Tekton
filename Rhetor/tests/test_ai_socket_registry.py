"""Tests for AI Socket Registry.

Tests the core socket registry functionality including:
- Socket creation and management
- Message routing with headers
- Persistence and recovery
- Broadcast mechanisms
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from rhetor.core.ai_socket_registry import (
    AISocketRegistry,
    AISocket,
    SocketState,
    get_socket_registry
)


class TestAISocket:
    """Test the AISocket dataclass."""
    
    def test_socket_creation(self):
        """Test basic socket creation."""
        socket = AISocket(
            socket_id="test-123",
            model="claude-3",
            prompt="Be helpful",
            context={"key": "value"},
            created_at=datetime.utcnow().isoformat()
        )
        
        assert socket.socket_id == "test-123"
        assert socket.model == "claude-3"
        assert socket.prompt == "Be helpful"
        assert socket.context == {"key": "value"}
        assert socket.state == SocketState.ACTIVE
        assert socket.message_queue == []
    
    def test_socket_to_dict(self):
        """Test socket serialization."""
        socket = AISocket(
            socket_id="test-123",
            model="claude-3",
            prompt="Be helpful",
            context={"key": "value"},
            created_at="2024-01-01T00:00:00"
        )
        
        data = socket.to_dict()
        assert data["socket_id"] == "test-123"
        assert data["state"] == "active"
        assert isinstance(data["message_queue"], list)
    
    def test_socket_from_dict(self):
        """Test socket deserialization."""
        data = {
            "socket_id": "test-123",
            "model": "claude-3",
            "prompt": "Be helpful",
            "context": {"key": "value"},
            "created_at": "2024-01-01T00:00:00",
            "state": "unresponsive",
            "last_activity": "2024-01-01T01:00:00",
            "message_queue": [{"content": "test"}]
        }
        
        socket = AISocket.from_dict(data)
        assert socket.socket_id == "test-123"
        assert socket.state == SocketState.UNRESPONSIVE
        assert len(socket.message_queue) == 1


class TestAISocketRegistry:
    """Test the AI Socket Registry."""
    
    @pytest.fixture
    async def registry(self):
        """Create a test registry without persistence."""
        registry = AISocketRegistry()
        # Mock Engram client to avoid actual persistence
        registry.engram_client = None
        registry._initialized = True
        return registry
    
    @pytest.fixture
    async def mock_engram_client(self):
        """Create a mock Engram client."""
        client = AsyncMock()
        client.store_memory = AsyncMock(return_value=True)
        client.get_memory = AsyncMock(return_value=None)
        client.delete_memory = AsyncMock(return_value=True)
        client.list_memories = AsyncMock(return_value=[])
        return client
    
    @pytest.mark.asyncio
    async def test_registry_initialization(self, mock_engram_client):
        """Test registry initialization."""
        with patch('rhetor.core.ai_socket_registry.get_engram_client', return_value=mock_engram_client):
            registry = AISocketRegistry()
            await registry.initialize()
            
            assert registry._initialized
            assert "team-chat-all" in registry.sockets
            assert registry.sockets["team-chat-all"].model == "broadcast"
    
    @pytest.mark.asyncio
    async def test_create_socket(self, registry):
        """Test socket creation."""
        socket_id = await registry.create(
            model="claude-3",
            prompt="Be helpful",
            context={"test": True}
        )
        
        assert socket_id.startswith("claude_3_")
        assert socket_id in registry.sockets
        
        socket = registry.sockets[socket_id]
        assert socket.model == "claude-3"
        assert socket.prompt == "Be helpful"
        assert socket.context == {"test": True}
    
    @pytest.mark.asyncio
    async def test_create_socket_with_id(self, registry):
        """Test socket creation with specific ID."""
        socket_id = await registry.create(
            model="claude-3",
            prompt="Be helpful",
            context={},
            socket_id="custom-id"
        )
        
        assert socket_id == "custom-id"
        assert "custom-id" in registry.sockets
    
    @pytest.mark.asyncio
    async def test_write_to_socket(self, registry):
        """Test writing messages to a socket."""
        socket_id = await registry.create("claude-3", "Be helpful", {})
        
        success = await registry.write(socket_id, "Hello AI", {"meta": "data"})
        assert success
        
        socket = registry.sockets[socket_id]
        assert len(socket.message_queue) == 1
        
        message = socket.message_queue[0]
        assert message["content"] == "Hello AI"
        assert message["header"] == f"[team-chat-to-{socket_id}]"
        assert message["metadata"] == {"meta": "data"}
    
    @pytest.mark.asyncio
    async def test_read_from_socket(self, registry):
        """Test reading messages from a socket."""
        socket_id = await registry.create("claude-3", "Be helpful", {})
        
        # Write a message first
        await registry.write(socket_id, "Hello AI")
        
        # Read messages
        messages = await registry.read(socket_id)
        assert len(messages) == 1
        
        message = messages[0]
        assert message["content"] == "Hello AI"
        assert message["header"] == f"[team-chat-from-{socket_id}]"
        
        # Queue should be cleared after reading
        assert len(registry.sockets[socket_id].message_queue) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_write(self, registry):
        """Test broadcasting to all sockets."""
        # Create multiple sockets
        socket1 = await registry.create("claude-3", "Be helpful", {})
        socket2 = await registry.create("gpt-4", "Be creative", {})
        
        # Broadcast message
        success = await registry.write("team-chat-all", "Team meeting!")
        assert success
        
        # Check both sockets received the message
        assert len(registry.sockets[socket1].message_queue) == 1
        assert len(registry.sockets[socket2].message_queue) == 1
        
        # Messages should have correct headers
        msg1 = registry.sockets[socket1].message_queue[0]
        assert msg1["header"] == f"[team-chat-to-{socket1}]"
        assert msg1["content"] == "Team meeting!"
        
        msg2 = registry.sockets[socket2].message_queue[0]
        assert msg2["header"] == f"[team-chat-to-{socket2}]"
        assert msg2["content"] == "Team meeting!"
    
    @pytest.mark.asyncio
    async def test_broadcast_read(self, registry):
        """Test reading from broadcast socket."""
        # Create sockets and add messages
        socket1 = await registry.create("claude-3", "Be helpful", {})
        socket2 = await registry.create("gpt-4", "Be creative", {})
        
        registry.sockets[socket1].message_queue.append({
            "content": "Response 1",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {}
        })
        
        registry.sockets[socket2].message_queue.append({
            "content": "Response 2",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {}
        })
        
        # Read from team-chat-all
        messages = await registry.read("team-chat-all")
        assert len(messages) == 2
        
        # Check headers
        headers = [msg["header"] for msg in messages]
        assert f"[team-chat-from-{socket1}]" in headers
        assert f"[team-chat-from-{socket2}]" in headers
        
        # Queues should be cleared
        assert len(registry.sockets[socket1].message_queue) == 0
        assert len(registry.sockets[socket2].message_queue) == 0
    
    @pytest.mark.asyncio
    async def test_delete_socket(self, registry):
        """Test socket deletion."""
        socket_id = await registry.create("claude-3", "Be helpful", {})
        
        success = await registry.delete(socket_id)
        assert success
        assert socket_id not in registry.sockets
    
    @pytest.mark.asyncio
    async def test_delete_broadcast_socket_fails(self, registry):
        """Test that broadcast socket cannot be deleted."""
        success = await registry.delete("team-chat-all")
        assert not success
        assert "team-chat-all" in registry.sockets
    
    @pytest.mark.asyncio
    async def test_reset_socket(self, registry):
        """Test socket reset."""
        socket_id = await registry.create("claude-3", "Be helpful", {"key": "value"})
        
        # Add some messages
        await registry.write(socket_id, "Message 1")
        await registry.write(socket_id, "Message 2")
        
        # Reset socket
        success = await registry.reset(socket_id)
        assert success
        
        socket = registry.sockets[socket_id]
        assert len(socket.message_queue) == 0
        assert socket.context == {}
        assert socket.state == SocketState.ACTIVE
    
    @pytest.mark.asyncio
    async def test_list_sockets(self, registry):
        """Test listing all sockets."""
        # Create multiple sockets
        socket1 = await registry.create("claude-3", "Be helpful", {})
        socket2 = await registry.create("gpt-4", "Be creative", {})
        
        sockets = await registry.list_sockets()
        
        # Should include broadcast socket + 2 created
        assert len(sockets) >= 3
        
        socket_ids = [s["socket_id"] for s in sockets]
        assert socket1 in socket_ids
        assert socket2 in socket_ids
        assert "team-chat-all" in socket_ids
    
    @pytest.mark.asyncio
    async def test_get_socket_info(self, registry):
        """Test getting detailed socket information."""
        socket_id = await registry.create("claude-3", "Be helpful", {"key": "value"})
        
        info = await registry.get_socket_info(socket_id)
        assert info is not None
        assert info["socket_id"] == socket_id
        assert info["model"] == "claude-3"
        assert info["prompt"] == "Be helpful"
        assert info["context"] == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_mark_unresponsive(self, registry):
        """Test marking a socket as unresponsive."""
        socket_id = await registry.create("claude-3", "Be helpful", {})
        
        success = await registry.mark_unresponsive(socket_id)
        assert success
        
        socket = registry.sockets[socket_id]
        assert socket.state == SocketState.UNRESPONSIVE
    
    @pytest.mark.asyncio
    async def test_unresponsive_socket_no_write(self, registry):
        """Test that unresponsive sockets don't receive writes."""
        socket_id = await registry.create("claude-3", "Be helpful", {})
        await registry.mark_unresponsive(socket_id)
        
        success = await registry.write(socket_id, "Hello")
        assert not success
    
    @pytest.mark.asyncio
    async def test_persistence_integration(self, mock_engram_client):
        """Test integration with Engram persistence."""
        registry = AISocketRegistry()
        registry.engram_client = mock_engram_client
        registry._initialized = True
        
        # Create a socket
        socket_id = await registry.create("claude-3", "Be helpful", {})
        
        # Verify persistence was called
        mock_engram_client.store_memory.assert_called()
        call_args = mock_engram_client.store_memory.call_args
        assert call_args[1]["namespace"] == "rhetor_sockets"
        assert call_args[1]["key"] == socket_id
    
    @pytest.mark.asyncio
    async def test_restore_from_persistence(self, mock_engram_client):
        """Test restoring registry from persistence."""
        # Mock existing sockets in persistence
        mock_engram_client.list_memories.return_value = [
            {"key": "socket-1"},
            {"key": "socket-2"}
        ]
        
        socket_data = {
            "socket_id": "socket-1",
            "model": "claude-3",
            "prompt": "Be helpful",
            "context": {},
            "created_at": "2024-01-01T00:00:00",
            "state": "active",
            "message_queue": []
        }
        
        mock_engram_client.get_memory.return_value = socket_data
        
        with patch('rhetor.core.ai_socket_registry.get_engram_client', return_value=mock_engram_client):
            registry = AISocketRegistry()
            await registry.initialize()
            
            # Should have restored socket + broadcast socket
            assert "socket-1" in registry.sockets
            assert "team-chat-all" in registry.sockets
    
    @pytest.mark.asyncio
    async def test_singleton_instance(self, mock_engram_client):
        """Test singleton pattern for registry."""
        with patch('rhetor.core.ai_socket_registry.get_engram_client', return_value=mock_engram_client):
            registry1 = await get_socket_registry()
            registry2 = await get_socket_registry()
            
            assert registry1 is registry2


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    async def registry(self):
        """Create a test registry."""
        registry = AISocketRegistry()
        registry.engram_client = None
        registry._initialized = True
        return registry
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_socket(self, registry):
        """Test reading from non-existent socket."""
        messages = await registry.read("nonexistent")
        assert messages == []
    
    @pytest.mark.asyncio
    async def test_write_nonexistent_socket(self, registry):
        """Test writing to non-existent socket."""
        success = await registry.write("nonexistent", "Hello")
        assert not success
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_socket(self, registry):
        """Test deleting non-existent socket."""
        success = await registry.delete("nonexistent")
        assert not success
    
    @pytest.mark.asyncio
    async def test_empty_broadcast(self, registry):
        """Test broadcast with no active sockets."""
        # Only broadcast socket exists
        messages = await registry.read("team-chat-all")
        assert messages == []
    
    @pytest.mark.asyncio
    async def test_persistence_failure_handling(self):
        """Test handling of persistence failures."""
        # Mock Engram client that fails
        mock_client = AsyncMock()
        mock_client.store_memory = AsyncMock(side_effect=Exception("Storage failed"))
        
        registry = AISocketRegistry()
        registry.engram_client = mock_client
        registry._initialized = True
        
        # Should still work despite persistence failure
        socket_id = await registry.create("claude-3", "Be helpful", {})
        assert socket_id in registry.sockets