"""
Subscription management for A2A streaming

Handles subscriptions to channels, tasks, and agents for real-time updates.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Set, List, Optional, Any, Callable
from uuid import uuid4

from tekton.models import TektonBaseModel
from .events import StreamEvent, EventType

logger = logging.getLogger(__name__)


class SubscriptionType(str):
    """Types of subscriptions"""
    TASK = "task"
    AGENT = "agent" 
    CHANNEL = "channel"
    BROADCAST = "broadcast"
    EVENT_TYPE = "event_type"


class Subscription(TektonBaseModel):
    """Represents a subscription to events"""
    
    id: str
    subscriber_id: str  # Agent or client ID
    subscription_type: str
    target: Optional[str] = None  # task_id, agent_id, channel name, etc.
    event_types: List[EventType] = []
    filters: Dict[str, Any] = {}
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    @classmethod
    def create_task_subscription(
        cls,
        subscriber_id: str,
        task_id: str,
        event_types: Optional[List[EventType]] = None
    ) -> 'Subscription':
        """Create a subscription to task events"""
        return cls(
            id=f"sub-{uuid4()}",
            subscriber_id=subscriber_id,
            subscription_type=SubscriptionType.TASK,
            target=task_id,
            event_types=event_types or [
                EventType.TASK_STATE_CHANGED,
                EventType.TASK_PROGRESS,
                EventType.TASK_COMPLETED,
                EventType.TASK_FAILED,
                EventType.TASK_CANCELLED
            ],
            created_at=datetime.utcnow()
        )
    
    @classmethod
    def create_agent_subscription(
        cls,
        subscriber_id: str,
        agent_id: str,
        event_types: Optional[List[EventType]] = None
    ) -> 'Subscription':
        """Create a subscription to agent events"""
        return cls(
            id=f"sub-{uuid4()}",
            subscriber_id=subscriber_id,
            subscription_type=SubscriptionType.AGENT,
            target=agent_id,
            event_types=event_types or [
                EventType.AGENT_STATUS_CHANGED,
                EventType.AGENT_HEARTBEAT
            ],
            created_at=datetime.utcnow()
        )
    
    @classmethod
    def create_channel_subscription(
        cls,
        subscriber_id: str,
        channel: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> 'Subscription':
        """Create a subscription to a channel"""
        return cls(
            id=f"sub-{uuid4()}",
            subscriber_id=subscriber_id,
            subscription_type=SubscriptionType.CHANNEL,
            target=channel,
            event_types=[EventType.CHANNEL_MESSAGE],
            filters=filters or {},
            created_at=datetime.utcnow()
        )
    
    def matches_event(self, event: StreamEvent) -> bool:
        """Check if an event matches this subscription"""
        # Check event type
        if self.event_types and event.type not in self.event_types:
            return False
        
        # Check subscription type specific matching
        if self.subscription_type == SubscriptionType.TASK:
            if not hasattr(event, "task_id") or event.task_id != self.target:
                return False
                
        elif self.subscription_type == SubscriptionType.AGENT:
            if not hasattr(event, "agent_id") or event.agent_id != self.target:
                return False
                
        elif self.subscription_type == SubscriptionType.CHANNEL:
            if not hasattr(event, "channel"):
                return False
            # Check for pattern matching in filters
            if "channel_pattern" in self.filters:
                from .channels import ChannelBridge
                # Use static pattern matching method
                if not self._matches_channel_pattern(event.channel, self.filters["channel_pattern"]):
                    return False
            elif event.channel != self.target:
                return False
        
        # Check custom filters
        for key, value in self.filters.items():
            if not hasattr(event, key) or getattr(event, key) != value:
                return False
        
        # Check expiration
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def _matches_channel_pattern(self, channel: str, pattern: str) -> bool:
        """Check if channel matches pattern with wildcards"""
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
        return bool(re.match(regex_pattern, channel))


class SubscriptionManager:
    """
    Manages event subscriptions and routing
    """
    
    def __init__(self):
        self._subscriptions: Dict[str, Subscription] = {}
        self._subscriber_index: Dict[str, Set[str]] = {}  # subscriber_id -> subscription_ids
        self._target_index: Dict[str, Set[str]] = {}  # target -> subscription_ids
        self._callbacks: Dict[str, Callable[[StreamEvent], None]] = {}
        self._lock = asyncio.Lock()
    
    async def add_subscription(
        self,
        subscription: Subscription,
        callback: Optional[Callable[[StreamEvent], None]] = None
    ) -> str:
        """
        Add a subscription
        
        Args:
            subscription: The subscription to add
            callback: Optional callback for events matching this subscription
            
        Returns:
            Subscription ID
        """
        async with self._lock:
            # Store subscription
            self._subscriptions[subscription.id] = subscription
            
            # Update indexes
            if subscription.subscriber_id not in self._subscriber_index:
                self._subscriber_index[subscription.subscriber_id] = set()
            self._subscriber_index[subscription.subscriber_id].add(subscription.id)
            
            if subscription.target:
                if subscription.target not in self._target_index:
                    self._target_index[subscription.target] = set()
                self._target_index[subscription.target].add(subscription.id)
            
            # Store callback if provided
            if callback:
                self._callbacks[subscription.id] = callback
            
            logger.info(
                f"Added subscription {subscription.id} for subscriber "
                f"{subscription.subscriber_id} to {subscription.subscription_type} "
                f"{subscription.target}"
            )
        
        return subscription.id
    
    async def remove_subscription(self, subscription_id: str) -> bool:
        """Remove a subscription"""
        async with self._lock:
            if subscription_id not in self._subscriptions:
                return False
            
            subscription = self._subscriptions[subscription_id]
            
            # Remove from indexes
            if subscription.subscriber_id in self._subscriber_index:
                self._subscriber_index[subscription.subscriber_id].discard(subscription_id)
                if not self._subscriber_index[subscription.subscriber_id]:
                    del self._subscriber_index[subscription.subscriber_id]
            
            if subscription.target and subscription.target in self._target_index:
                self._target_index[subscription.target].discard(subscription_id)
                if not self._target_index[subscription.target]:
                    del self._target_index[subscription.target]
            
            # Remove subscription and callback
            del self._subscriptions[subscription_id]
            self._callbacks.pop(subscription_id, None)
            
            logger.info(f"Removed subscription {subscription_id}")
            return True
    
    async def remove_subscriber_subscriptions(self, subscriber_id: str) -> int:
        """Remove all subscriptions for a subscriber"""
        async with self._lock:
            if subscriber_id not in self._subscriber_index:
                return 0
            
            subscription_ids = list(self._subscriber_index[subscriber_id])
        
        # Remove subscriptions outside the lock to avoid deadlock
        removed = 0
        for sub_id in subscription_ids:
            if await self.remove_subscription(sub_id):
                removed += 1
        
        return removed
    
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get a subscription by ID"""
        async with self._lock:
            return self._subscriptions.get(subscription_id)
    
    async def get_subscriber_subscriptions(
        self,
        subscriber_id: str
    ) -> List[Subscription]:
        """Get all subscriptions for a subscriber"""
        async with self._lock:
            sub_ids = self._subscriber_index.get(subscriber_id, set())
            return [
                self._subscriptions[sub_id]
                for sub_id in sub_ids
                if sub_id in self._subscriptions
            ]
    
    async def route_event(self, event: StreamEvent) -> int:
        """
        Route an event to matching subscriptions
        
        Returns:
            Number of subscriptions that received the event
        """
        async with self._lock:
            # Find all potentially matching subscriptions
            potential_subs = set()
            
            # Check target-based subscriptions
            if hasattr(event, "task_id") and event.task_id in self._target_index:
                potential_subs.update(self._target_index[event.task_id])
            
            if hasattr(event, "agent_id") and event.agent_id in self._target_index:
                potential_subs.update(self._target_index[event.agent_id])
            
            if hasattr(event, "channel") and event.channel in self._target_index:
                potential_subs.update(self._target_index[event.channel])
            
            # Also check broadcast subscriptions
            if None in self._target_index:
                potential_subs.update(self._target_index[None])
            
            # Filter to matching subscriptions
            matching_subs = []
            for sub_id in potential_subs:
                if sub_id in self._subscriptions:
                    subscription = self._subscriptions[sub_id]
                    if subscription.matches_event(event):
                        matching_subs.append((sub_id, subscription))
            
            # Get callbacks
            callbacks = [
                self._callbacks.get(sub_id)
                for sub_id, _ in matching_subs
                if sub_id in self._callbacks
            ]
        
        # Execute callbacks outside the lock
        if callbacks:
            await asyncio.gather(
                *[callback(event) for callback in callbacks if callback],
                return_exceptions=True
            )
        
        logger.debug(
            f"Routed event {event.type} to {len(matching_subs)} subscriptions"
        )
        
        return len(matching_subs)
    
    async def cleanup_expired(self) -> int:
        """Remove expired subscriptions"""
        now = datetime.utcnow()
        async with self._lock:
            expired = [
                sub_id
                for sub_id, sub in self._subscriptions.items()
                if sub.expires_at and sub.expires_at < now
            ]
        
        removed = 0
        for sub_id in expired:
            if await self.remove_subscription(sub_id):
                removed += 1
        
        if removed:
            logger.info(f"Cleaned up {removed} expired subscriptions")
        
        return removed