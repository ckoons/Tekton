"""
Channel-based pub/sub system for A2A Protocol.

This module provides a bridge between Hermes message bus channels and 
A2A streaming channels, enhancing existing functionality without breaking 
compatibility.
"""

from typing import Dict, List, Optional, Set, Any, Pattern
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import re
from uuid import uuid4

from .events import ChannelEvent, EventType
from .subscription import SubscriptionManager, Subscription, SubscriptionType


@dataclass
class Channel:
    """Enhanced channel with metadata and access control"""
    name: str
    owner_id: str
    created_at: datetime
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    public: bool = True
    message_count: int = 0
    last_message_at: Optional[datetime] = None


class ChannelBridge:
    """
    Bridges Hermes message bus channels with A2A streaming channels.
    Enhances existing functionality without breaking compatibility.
    """
    
    def __init__(self, message_bus, subscription_manager: SubscriptionManager):
        """
        Initialize the channel bridge.
        
        Args:
            message_bus: Hermes message bus instance
            subscription_manager: A2A subscription manager
        """
        self.message_bus = message_bus
        self.subscription_manager = subscription_manager
        self.channels: Dict[str, Channel] = {}
        self._pattern_cache: Dict[str, Pattern] = {}
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Set up bridge subscriptions to Hermes channels"""
        # Subscribe to all Hermes channels to bridge messages
        self.message_bus.subscribe("*", self._bridge_hermes_message)
        self.message_bus.subscribe("**", self._bridge_hermes_message)
        
    async def _bridge_hermes_message(self, envelope: Dict[str, Any]):
        """Bridge Hermes message bus messages to A2A channel events"""
        # Extract topic, message, and headers from envelope
        headers = envelope.get("headers", {})
        topic = headers.get("topic", "")
        message = envelope.get("payload", {})
        
        # Only bridge messages from actual channels (not system topics)
        if not self._should_bridge_topic(topic):
            return
            
        # Create A2A channel event
        event = ChannelEvent(
            id=str(uuid4()),
            type=EventType.CHANNEL_MESSAGE,
            timestamp=datetime.utcnow(),
            source=headers.get("sender_id", "hermes"),
            channel=topic,
            sender_id=headers.get("sender_id", "hermes"),
            data=message,
            metadata=headers
        )
        
        # Route through A2A subscription system
        await self.subscription_manager.route_event(event)
    
    def _should_bridge_topic(self, topic: str) -> bool:
        """Determine if a Hermes topic should be bridged to A2A"""
        # Don't bridge internal system topics
        system_prefixes = ["system.", "internal.", "component."]
        return not any(topic.startswith(prefix) for prefix in system_prefixes)
    
    async def enhance_channel(self, name: str, owner_id: str, **kwargs) -> Channel:
        """
        Enhance a Hermes channel with A2A metadata.
        Called when channel is first created or accessed.
        
        Args:
            name: Channel name
            owner_id: ID of the agent creating/owning the channel
            **kwargs: Additional channel attributes
            
        Returns:
            Enhanced Channel object
        """
        async with self._lock:
            if name not in self.channels:
                channel = Channel(
                    name=name,
                    owner_id=owner_id,
                    created_at=datetime.utcnow(),
                    **kwargs
                )
                self.channels[name] = channel
                
                # Emit channel created event
                event = ChannelEvent(
                    id=str(uuid4()),
                    type=EventType.CHANNEL_CREATED,
                    timestamp=datetime.utcnow(),
                    source=owner_id,
                    channel=name,
                    sender_id=owner_id,
                    data={"channel_info": self._channel_to_dict(channel)},
                    metadata={}
                )
                await self.subscription_manager.route_event(event)
                
            return self.channels[name]
    
    async def publish_with_metadata(self, channel: str, sender_id: str, 
                                   content: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Publish to both Hermes message bus and A2A streaming.
        Enhances the basic Hermes publish with A2A features.
        
        Args:
            channel: Channel name to publish to
            sender_id: ID of the sending agent
            content: Message content
            metadata: Optional metadata dict
            
        Returns:
            Result dict with success status and details
        """
        # Ensure channel exists in our registry
        if channel not in self.channels:
            await self.enhance_channel(channel, sender_id)
        
        # Update channel stats
        channel_obj = self.channels[channel]
        channel_obj.message_count += 1
        channel_obj.last_message_at = datetime.utcnow()
        
        # Create channel event for A2A streaming
        event = ChannelEvent(
            id=str(uuid4()),
            type=EventType.CHANNEL_MESSAGE,
            timestamp=datetime.utcnow(),
            source=sender_id,
            channel=channel,
            sender_id=sender_id,
            data=content,
            metadata=metadata or {}
        )
        
        # Route through A2A subscriptions (WebSocket/SSE)
        await self.subscription_manager.route_event(event)
        
        # Also publish to Hermes message bus for backward compatibility
        headers = {"sender_id": sender_id, **(metadata or {})}
        await self.message_bus.publish(channel, content, headers)
        
        return {
            "success": True,
            "channel": channel,
            "message_id": event.id,
            "timestamp": event.timestamp.isoformat()
        }
    
    async def create_pattern_subscription(self, agent_id: str, pattern: str) -> str:
        """
        Create a subscription that supports wildcards.
        Enhances Hermes's basic channel subscription.
        
        Args:
            agent_id: Subscribing agent ID
            pattern: Channel pattern (supports * and ** wildcards)
            
        Returns:
            Subscription ID
        """
        # Create A2A subscription with pattern support
        subscription = await self.subscription_manager.create_subscription(
            subscriber_id=agent_id,
            subscription_type=SubscriptionType.CHANNEL,
            filters={"channel_pattern": pattern}
        )
        
        # Also subscribe to Hermes channels matching pattern
        # This ensures backward compatibility
        await self._subscribe_hermes_pattern(agent_id, pattern)
        
        return subscription.id
    
    async def _subscribe_hermes_pattern(self, agent_id: str, pattern: str):
        """Subscribe to Hermes channels matching pattern"""
        # Convert A2A pattern to Hermes wildcard format
        hermes_pattern = pattern.replace("**", "*")
        
        # Create callback that converts to A2A events
        async def pattern_callback(topic: str, message: Dict[str, Any], headers: Dict[str, Any]):
            if self.matches_pattern(topic, pattern):
                await self._bridge_hermes_message(topic, message, headers)
        
        await self.message_bus.subscribe(hermes_pattern, pattern_callback)
    
    def matches_pattern(self, channel: str, pattern: str) -> bool:
        """
        Check if channel matches pattern with wildcards.
        
        * matches one segment (e.g., metrics.* matches metrics.cpu but not metrics.system.cpu)
        ** matches multiple segments (e.g., metrics.** matches both)
        
        Args:
            channel: Channel name to test
            pattern: Pattern with wildcards
            
        Returns:
            True if channel matches pattern
        """
        if pattern not in self._pattern_cache:
            # Convert pattern to regex
            # First escape dots
            regex_pattern = pattern.replace(".", r"\.")
            # Replace ** with a placeholder to avoid conflict with *
            regex_pattern = regex_pattern.replace("**", "__DOUBLE_STAR__")
            # Replace single * with pattern for one segment
            regex_pattern = regex_pattern.replace("*", "[^.]+")
            # Replace placeholder with pattern for multiple segments
            regex_pattern = regex_pattern.replace("__DOUBLE_STAR__", ".*")
            regex_pattern = f"^{regex_pattern}$"
            self._pattern_cache[pattern] = re.compile(regex_pattern)
        
        return bool(self._pattern_cache[pattern].match(channel))
    
    async def list_channels(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List channels with optional pattern filter.
        
        Args:
            pattern: Optional pattern to filter channels
            
        Returns:
            List of channel info dicts
        """
        channels = []
        for name, channel in self.channels.items():
            if pattern is None or self.matches_pattern(name, pattern):
                channels.append(self._channel_to_dict(channel))
        return channels
    
    async def get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed channel information.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Channel info dict or None if not found
        """
        if channel_name in self.channels:
            return self._channel_to_dict(self.channels[channel_name])
        return None
    
    async def delete_channel(self, channel_name: str, agent_id: str) -> bool:
        """
        Delete a channel (only owner can delete).
        
        Args:
            channel_name: Name of the channel to delete
            agent_id: ID of the agent requesting deletion
            
        Returns:
            True if deleted, False if not authorized or not found
        """
        async with self._lock:
            if channel_name not in self.channels:
                return False
                
            channel = self.channels[channel_name]
            if channel.owner_id != agent_id:
                return False
                
            # Remove channel
            del self.channels[channel_name]
            
            # Emit channel deleted event
            event = ChannelEvent(
                id=str(uuid4()),
                type=EventType.CHANNEL_DELETED,
                timestamp=datetime.utcnow(),
                source=agent_id,
                channel=channel_name,
                sender_id=agent_id,
                data={"deleted_by": agent_id},
                metadata={}
            )
            await self.subscription_manager.route_event(event)
            
            return True
    
    def _channel_to_dict(self, channel: Channel) -> Dict[str, Any]:
        """Convert channel to dict representation"""
        return {
            "name": channel.name,
            "owner_id": channel.owner_id,
            "created_at": channel.created_at.isoformat(),
            "description": channel.description,
            "metadata": channel.metadata,
            "public": channel.public,
            "message_count": channel.message_count,
            "last_message_at": channel.last_message_at.isoformat() if channel.last_message_at else None
        }