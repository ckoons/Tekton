"""
Unit tests for A2A channel-based pub/sub system
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, call
from uuid import uuid4

from tekton.a2a.streaming.channels import Channel, ChannelBridge
from tekton.a2a.streaming.events import ChannelEvent, EventType
from tekton.a2a.streaming.subscription import SubscriptionManager, SubscriptionType


class TestChannel:
    """Test the Channel dataclass"""
    
    def test_channel_creation(self):
        """Test creating a channel with all fields"""
        channel = Channel(
            name="test.channel",
            owner_id="agent-123",
            created_at=datetime.utcnow(),
            description="Test channel",
            metadata={"key": "value"},
            public=True,
            message_count=5,
            last_message_at=datetime.utcnow()
        )
        
        assert channel.name == "test.channel"
        assert channel.owner_id == "agent-123"
        assert channel.description == "Test channel"
        assert channel.metadata == {"key": "value"}
        assert channel.public is True
        assert channel.message_count == 5
        assert channel.last_message_at is not None
    
    def test_channel_defaults(self):
        """Test channel creation with defaults"""
        channel = Channel(
            name="test.channel",
            owner_id="agent-123",
            created_at=datetime.utcnow()
        )
        
        assert channel.description is None
        assert channel.metadata == {}
        assert channel.public is True
        assert channel.message_count == 0
        assert channel.last_message_at is None


class TestChannelBridge:
    """Test the ChannelBridge class"""
    
    @pytest.fixture
    def mock_message_bus(self):
        """Create a mock message bus"""
        bus = AsyncMock()
        bus.subscribe = AsyncMock()
        bus.publish = AsyncMock()
        bus.create_channel = AsyncMock()
        return bus
    
    @pytest.fixture
    def mock_subscription_manager(self):
        """Create a mock subscription manager"""
        manager = AsyncMock()
        manager.route_event = AsyncMock()
        manager.create_subscription = AsyncMock()
        return manager
    
    @pytest.fixture
    def channel_bridge(self, mock_message_bus, mock_subscription_manager):
        """Create a channel bridge instance"""
        return ChannelBridge(mock_message_bus, mock_subscription_manager)
    
    @pytest.mark.asyncio
    async def test_initialize(self, channel_bridge, mock_message_bus):
        """Test bridge initialization"""
        await channel_bridge.initialize()
        
        # Should subscribe to wildcard patterns
        assert mock_message_bus.subscribe.call_count == 2
        mock_message_bus.subscribe.assert_any_call("*", channel_bridge._bridge_hermes_message)
        mock_message_bus.subscribe.assert_any_call("**", channel_bridge._bridge_hermes_message)
    
    def test_should_bridge_topic(self, channel_bridge):
        """Test topic bridging rules"""
        # Should bridge regular channels
        assert channel_bridge._should_bridge_topic("metrics.cpu") is True
        assert channel_bridge._should_bridge_topic("tasks.updates") is True
        assert channel_bridge._should_bridge_topic("custom.channel") is True
        
        # Should not bridge system topics
        assert channel_bridge._should_bridge_topic("system.health") is False
        assert channel_bridge._should_bridge_topic("internal.events") is False
        assert channel_bridge._should_bridge_topic("component.status") is False
    
    @pytest.mark.asyncio
    async def test_bridge_hermes_message(self, channel_bridge, mock_subscription_manager):
        """Test bridging Hermes messages to A2A events"""
        # Test bridging a regular channel message
        await channel_bridge._bridge_hermes_message(
            "metrics.cpu",
            {"value": 45.2},
            {"sender_id": "agent-123"}
        )
        
        # Should create and route a channel event
        mock_subscription_manager.route_event.assert_called_once()
        event = mock_subscription_manager.route_event.call_args[0][0]
        assert isinstance(event, ChannelEvent)
        assert event.channel == "metrics.cpu"
        assert event.sender_id == "agent-123"
        assert event.data == {"value": 45.2}
        
        # Reset mock
        mock_subscription_manager.route_event.reset_mock()
        
        # Test system topic (should not bridge)
        await channel_bridge._bridge_hermes_message(
            "system.health",
            {"status": "ok"},
            {}
        )
        
        # Should not route event
        mock_subscription_manager.route_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_enhance_channel(self, channel_bridge, mock_subscription_manager):
        """Test enhancing a channel with metadata"""
        # Create new channel
        channel = await channel_bridge.enhance_channel(
            "test.channel",
            "agent-123",
            description="Test channel"
        )
        
        assert channel.name == "test.channel"
        assert channel.owner_id == "agent-123"
        assert channel.description == "Test channel"
        assert channel in channel_bridge.channels.values()
        
        # Should emit channel created event
        mock_subscription_manager.route_event.assert_called_once()
        event = mock_subscription_manager.route_event.call_args[0][0]
        assert event.type == EventType.CHANNEL_CREATED
        assert event.channel == "test.channel"
        
        # Enhance existing channel (should not create duplicate)
        mock_subscription_manager.route_event.reset_mock()
        channel2 = await channel_bridge.enhance_channel("test.channel", "agent-456")
        
        assert channel2 == channel
        assert len(channel_bridge.channels) == 1
        mock_subscription_manager.route_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_publish_with_metadata(self, channel_bridge, mock_message_bus, mock_subscription_manager):
        """Test publishing to both Hermes and A2A"""
        result = await channel_bridge.publish_with_metadata(
            "test.channel",
            "agent-123",
            {"message": "hello"},
            {"priority": "high"}
        )
        
        # Check result
        assert result["success"] is True
        assert result["channel"] == "test.channel"
        assert "message_id" in result
        assert "timestamp" in result
        
        # Should create channel if it doesn't exist
        assert "test.channel" in channel_bridge.channels
        channel = channel_bridge.channels["test.channel"]
        assert channel.message_count == 1
        assert channel.last_message_at is not None
        
        # Should route through A2A subscriptions
        mock_subscription_manager.route_event.assert_called()
        event = mock_subscription_manager.route_event.call_args[0][0]
        assert event.type == EventType.CHANNEL_MESSAGE
        assert event.channel == "test.channel"
        assert event.sender_id == "agent-123"
        assert event.data == {"message": "hello"}
        assert event.metadata == {"priority": "high"}
        
        # Should publish to Hermes message bus
        mock_message_bus.publish.assert_called_once_with(
            "test.channel",
            {"message": "hello"},
            {"sender_id": "agent-123", "priority": "high"}
        )
    
    def test_matches_pattern(self, channel_bridge):
        """Test pattern matching with wildcards"""
        # Exact match
        assert channel_bridge.matches_pattern("metrics.cpu", "metrics.cpu") is True
        assert channel_bridge.matches_pattern("metrics.cpu", "metrics.memory") is False
        
        # Single wildcard (*)
        assert channel_bridge.matches_pattern("metrics.cpu", "metrics.*") is True
        assert channel_bridge.matches_pattern("metrics.system.cpu", "metrics.*") is False
        assert channel_bridge.matches_pattern("tasks.created", "tasks.*") is True
        
        # Multi-wildcard (**)
        assert channel_bridge.matches_pattern("metrics.cpu", "metrics.**") is True
        assert channel_bridge.matches_pattern("metrics.system.cpu", "metrics.**") is True
        assert channel_bridge.matches_pattern("tasks.updates.progress", "tasks.**") is True
        assert channel_bridge.matches_pattern("other.channel", "tasks.**") is False
        
        # Complex patterns
        assert channel_bridge.matches_pattern("a.b.c.d", "a.*.c.*") is True
        assert channel_bridge.matches_pattern("a.b.c.d", "a.**.d") is True
        assert channel_bridge.matches_pattern("test.channel.sub", "test.*.**") is True
    
    @pytest.mark.asyncio
    async def test_create_pattern_subscription(self, channel_bridge, mock_subscription_manager, mock_message_bus):
        """Test creating subscriptions with patterns"""
        # Mock subscription creation
        mock_sub = Mock()
        mock_sub.id = "sub-123"
        mock_subscription_manager.create_subscription.return_value = mock_sub
        
        # Create pattern subscription
        sub_id = await channel_bridge.create_pattern_subscription("agent-123", "metrics.*")
        
        assert sub_id == "sub-123"
        
        # Should create A2A subscription with pattern filter
        mock_subscription_manager.create_subscription.assert_called_once_with(
            subscriber_id="agent-123",
            subscription_type=SubscriptionType.CHANNEL,
            filters={"channel_pattern": "metrics.*"}
        )
        
        # Should subscribe to Hermes pattern
        mock_message_bus.subscribe.assert_called()
        # Last call should be the pattern subscription
        pattern_call = mock_message_bus.subscribe.call_args_list[-1]
        assert pattern_call[0][0] == "metrics.*"  # Hermes pattern
    
    @pytest.mark.asyncio
    async def test_list_channels(self, channel_bridge):
        """Test listing channels with pattern filter"""
        # Add some test channels
        await channel_bridge.enhance_channel("metrics.cpu", "agent-1")
        await channel_bridge.enhance_channel("metrics.memory", "agent-1")
        await channel_bridge.enhance_channel("tasks.created", "agent-2")
        await channel_bridge.enhance_channel("custom.channel", "agent-3")
        
        # List all channels
        all_channels = await channel_bridge.list_channels()
        assert len(all_channels) == 4
        
        # List with pattern
        metrics_channels = await channel_bridge.list_channels("metrics.*")
        assert len(metrics_channels) == 2
        assert all(ch["name"].startswith("metrics.") for ch in metrics_channels)
        
        # List with different pattern
        task_channels = await channel_bridge.list_channels("tasks.**")
        assert len(task_channels) == 1
        assert task_channels[0]["name"] == "tasks.created"
    
    @pytest.mark.asyncio
    async def test_get_channel_info(self, channel_bridge):
        """Test getting channel information"""
        # Channel doesn't exist
        info = await channel_bridge.get_channel_info("nonexistent")
        assert info is None
        
        # Add channel
        await channel_bridge.enhance_channel(
            "test.channel",
            "agent-123",
            description="Test channel",
            metadata={"key": "value"}
        )
        
        # Get channel info
        info = await channel_bridge.get_channel_info("test.channel")
        assert info is not None
        assert info["name"] == "test.channel"
        assert info["owner_id"] == "agent-123"
        assert info["description"] == "Test channel"
        assert info["metadata"] == {"key": "value"}
        assert info["public"] is True
        assert info["message_count"] == 0
        assert info["last_message_at"] is None
    
    @pytest.mark.asyncio
    async def test_delete_channel(self, channel_bridge, mock_subscription_manager):
        """Test deleting a channel"""
        # Add channel
        await channel_bridge.enhance_channel("test.channel", "agent-123")
        assert "test.channel" in channel_bridge.channels
        
        # Try to delete as non-owner (should fail)
        result = await channel_bridge.delete_channel("test.channel", "agent-456")
        assert result is False
        assert "test.channel" in channel_bridge.channels
        
        # Delete as owner (should succeed)
        mock_subscription_manager.route_event.reset_mock()
        result = await channel_bridge.delete_channel("test.channel", "agent-123")
        assert result is True
        assert "test.channel" not in channel_bridge.channels
        
        # Should emit channel deleted event
        mock_subscription_manager.route_event.assert_called_once()
        event = mock_subscription_manager.route_event.call_args[0][0]
        assert event.type == EventType.CHANNEL_DELETED
        assert event.channel == "test.channel"
        assert event.data["deleted_by"] == "agent-123"
        
        # Try to delete non-existent channel
        result = await channel_bridge.delete_channel("nonexistent", "agent-123")
        assert result is False
    
    def test_channel_to_dict(self, channel_bridge):
        """Test converting channel to dict"""
        now = datetime.utcnow()
        channel = Channel(
            name="test.channel",
            owner_id="agent-123",
            created_at=now,
            description="Test channel",
            metadata={"key": "value"},
            public=False,
            message_count=10,
            last_message_at=now
        )
        
        channel_dict = channel_bridge._channel_to_dict(channel)
        
        assert channel_dict["name"] == "test.channel"
        assert channel_dict["owner_id"] == "agent-123"
        assert channel_dict["created_at"] == now.isoformat()
        assert channel_dict["description"] == "Test channel"
        assert channel_dict["metadata"] == {"key": "value"}
        assert channel_dict["public"] is False
        assert channel_dict["message_count"] == 10
        assert channel_dict["last_message_at"] == now.isoformat()
    
    @pytest.mark.asyncio
    async def test_pattern_caching(self, channel_bridge):
        """Test that pattern compilation is cached"""
        # First call compiles pattern
        assert len(channel_bridge._pattern_cache) == 0
        result1 = channel_bridge.matches_pattern("metrics.cpu", "metrics.*")
        assert len(channel_bridge._pattern_cache) == 1
        
        # Second call uses cached pattern
        result2 = channel_bridge.matches_pattern("metrics.memory", "metrics.*")
        assert len(channel_bridge._pattern_cache) == 1
        
        # Different pattern creates new cache entry
        result3 = channel_bridge.matches_pattern("tasks.created", "tasks.**")
        assert len(channel_bridge._pattern_cache) == 2
        
        assert result1 is True
        assert result2 is True
        assert result3 is True