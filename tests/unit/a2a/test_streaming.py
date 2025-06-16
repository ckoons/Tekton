"""
Unit tests for A2A streaming functionality
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from tekton.a2a.streaming import (
    SSEManager, SSEEvent, SSEConnection,
    EventType, StreamEvent, TaskEvent, AgentEvent,
    SubscriptionManager, Subscription
)


class TestSSEEvent:
    """Test SSE event formatting"""
    
    def test_simple_event(self):
        """Test formatting a simple SSE event"""
        event = SSEEvent(data="hello world")
        formatted = event.format()
        
        assert "data: hello world\n\n" in formatted
        assert "id: " in formatted  # Should have auto-generated ID
    
    def test_event_with_type(self):
        """Test event with event type"""
        event = SSEEvent(data="test", event="message", id="123")
        formatted = event.format()
        
        assert "id: 123\n" in formatted
        assert "event: message\n" in formatted
        assert "data: test\n\n" in formatted
    
    def test_json_data(self):
        """Test event with JSON data"""
        data = {"message": "hello", "count": 42}
        event = SSEEvent(data=data)
        formatted = event.format()
        
        assert 'data: {"message": "hello", "count": 42}\n\n' in formatted
    
    def test_multiline_data(self):
        """Test event with multiline data"""
        data = "line1\nline2\nline3"
        event = SSEEvent(data=data)
        formatted = event.format()
        
        assert "data: line1\ndata: line2\ndata: line3\n\n" in formatted
    
    def test_retry_field(self):
        """Test event with retry field"""
        event = SSEEvent(data="test", retry=5000)
        formatted = event.format()
        
        assert "retry: 5000\n" in formatted


class TestSSEConnection:
    """Test SSE connection filtering"""
    
    def test_no_filters(self):
        """Test connection with no filters matches all events"""
        conn = SSEConnection("test-1")
        event = StreamEvent.create(EventType.TASK_CREATED, "test", {})
        
        assert conn.matches_filters(event) is True
    
    def test_event_type_filter(self):
        """Test filtering by event type"""
        conn = SSEConnection("test-2", {"event_types": [EventType.TASK_CREATED]})
        
        matching_event = StreamEvent.create(EventType.TASK_CREATED, "test", {})
        non_matching_event = StreamEvent.create(EventType.TASK_COMPLETED, "test", {})
        
        assert conn.matches_filters(matching_event) is True
        assert conn.matches_filters(non_matching_event) is False
    
    def test_task_id_filter(self):
        """Test filtering by task ID"""
        conn = SSEConnection("test-3", {"task_id": "task-123"})
        
        matching_event = TaskEvent(
            id="evt-1",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.utcnow(),
            source="test",
            task_id="task-123",
            data={}
        )
        
        non_matching_event = TaskEvent(
            id="evt-2",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.utcnow(),
            source="test",
            task_id="task-456",
            data={}
        )
        
        assert conn.matches_filters(matching_event) is True
        assert conn.matches_filters(non_matching_event) is False
    
    @pytest.mark.asyncio
    async def test_send_event(self):
        """Test sending event to connection"""
        conn = SSEConnection("test-4")
        event = StreamEvent.create(EventType.TASK_CREATED, "test", {"name": "Test"})
        
        await conn.send_event(event)
        
        # Event should be in queue
        assert conn.queue.qsize() == 1
        queued_event = await conn.queue.get()
        assert queued_event == event
    
    def test_close_connection(self):
        """Test closing connection"""
        conn = SSEConnection("test-5")
        assert conn.active is True
        
        conn.close()
        assert conn.active is False


class TestSSEManager:
    """Test SSE manager functionality"""
    
    @pytest.mark.asyncio
    async def test_create_connection(self):
        """Test creating a new connection"""
        manager = SSEManager()
        conn = await manager.create_connection({"task_id": "task-123"})
        
        assert conn.id.startswith("sse-")
        assert conn.filters["task_id"] == "task-123"
        assert conn.active is True
        
        # Should have received connection established event
        assert conn.queue.qsize() == 1
        event = await conn.queue.get()
        assert event.type == EventType.CONNECTION_ESTABLISHED
    
    @pytest.mark.asyncio
    async def test_close_connection(self):
        """Test closing a connection"""
        manager = SSEManager()
        conn = await manager.create_connection()
        conn_id = conn.id
        
        await manager.close_connection(conn_id)
        
        # Connection should be removed
        connections = await manager.get_active_connections()
        assert conn_id not in connections
    
    @pytest.mark.asyncio
    async def test_broadcast_event(self):
        """Test broadcasting event to multiple connections"""
        manager = SSEManager()
        
        # Create connections with different filters
        conn1 = await manager.create_connection({"task_id": "task-123"})
        conn2 = await manager.create_connection({"task_id": "task-456"})
        conn3 = await manager.create_connection()  # No filters
        
        # Clear initial connection events
        await conn1.queue.get()
        await conn2.queue.get()
        await conn3.queue.get()
        
        # Broadcast a task event
        event = TaskEvent(
            id="evt-1",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.utcnow(),
            source="test",
            task_id="task-123",
            data={}
        )
        
        await manager.broadcast_event(event)
        
        # Only conn1 and conn3 should receive the event
        assert conn1.queue.qsize() == 1
        assert conn2.queue.qsize() == 0  # Filtered out
        assert conn3.queue.qsize() == 1  # No filters, gets all
    
    @pytest.mark.asyncio
    async def test_stream_events(self):
        """Test streaming events"""
        manager = SSEManager()
        conn = await manager.create_connection()
        
        # Add an event to the queue
        event = StreamEvent.create(
            EventType.TASK_CREATED,
            "test",
            {"message": "Hello SSE"}
        )
        await conn.send_event(event)
        
        # Stream events
        stream_gen = manager.stream_events(conn, keepalive_interval=0.1)
        
        # Get first event (connection established)
        first = await stream_gen.__anext__()
        assert "event: connection.established" in first
        
        # Get second event (our test event)
        second = await stream_gen.__anext__()
        assert "event: task.created" in second
        assert "Hello SSE" in second
        
        # Close the generator
        await stream_gen.aclose()


class TestStreamEvents:
    """Test stream event creation"""
    
    def test_create_task_state_change_event(self):
        """Test creating task state change event"""
        event = TaskEvent.create_state_change(
            task_id="task-123",
            old_state="pending",
            new_state="running",
            source="test-agent",
            message="Task started"
        )
        
        assert event.type == EventType.TASK_STATE_CHANGED
        assert event.task_id == "task-123"
        assert event.data["old_state"] == "pending"
        assert event.data["new_state"] == "running"
        assert event.data["message"] == "Task started"
    
    def test_create_task_progress_event(self):
        """Test creating task progress event"""
        event = TaskEvent.create_progress(
            task_id="task-456",
            progress=0.75,
            source="worker",
            message="Processing..."
        )
        
        assert event.type == EventType.TASK_PROGRESS
        assert event.task_id == "task-456"
        assert event.data["progress"] == 0.75
        assert event.data["message"] == "Processing..."
    
    def test_create_agent_status_change_event(self):
        """Test creating agent status change event"""
        event = AgentEvent.create_status_change(
            agent_id="agent-789",
            old_status="idle",
            new_status="busy",
            source="system"
        )
        
        assert event.type == EventType.AGENT_STATUS_CHANGED
        assert event.agent_id == "agent-789"
        assert event.data["old_status"] == "idle"
        assert event.data["new_status"] == "busy"


class TestSubscription:
    """Test subscription filtering"""
    
    def test_task_subscription(self):
        """Test task subscription creation and matching"""
        sub = Subscription.create_task_subscription(
            subscriber_id="agent-1",
            task_id="task-123"
        )
        
        # Should match task events for the specific task
        matching_event = TaskEvent(
            id="evt-1",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.utcnow(),
            source="test",
            task_id="task-123",
            data={}
        )
        
        non_matching_event = TaskEvent(
            id="evt-2",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.utcnow(),
            source="test",
            task_id="task-456",
            data={}
        )
        
        assert sub.matches_event(matching_event) is True
        assert sub.matches_event(non_matching_event) is False
    
    def test_channel_subscription(self):
        """Test channel subscription with custom filters"""
        sub = Subscription.create_channel_subscription(
            subscriber_id="agent-2",
            channel="updates",
            filters={"priority": "high"}
        )
        
        # For this test, we'd need a ChannelEvent class
        # which we haven't implemented yet
        assert sub.subscription_type == "channel"
        assert sub.target == "updates"
        assert sub.filters["priority"] == "high"


class TestSubscriptionManager:
    """Test subscription manager"""
    
    @pytest.mark.asyncio
    async def test_add_subscription(self):
        """Test adding a subscription"""
        manager = SubscriptionManager()
        
        sub = Subscription.create_task_subscription(
            subscriber_id="agent-1",
            task_id="task-123"
        )
        
        sub_id = await manager.add_subscription(sub)
        
        assert sub_id == sub.id
        retrieved = await manager.get_subscription(sub_id)
        assert retrieved == sub
    
    @pytest.mark.asyncio
    async def test_remove_subscription(self):
        """Test removing a subscription"""
        manager = SubscriptionManager()
        
        sub = Subscription.create_task_subscription(
            subscriber_id="agent-1",
            task_id="task-123"
        )
        
        sub_id = await manager.add_subscription(sub)
        removed = await manager.remove_subscription(sub_id)
        
        assert removed is True
        assert await manager.get_subscription(sub_id) is None
    
    @pytest.mark.asyncio
    async def test_route_event(self):
        """Test routing events to subscriptions"""
        manager = SubscriptionManager()
        
        # Track callback invocations
        callback_invocations = []
        
        async def callback(event):
            callback_invocations.append(event)
        
        # Add subscriptions
        sub1 = Subscription.create_task_subscription(
            subscriber_id="agent-1",
            task_id="task-123"
        )
        await manager.add_subscription(sub1, callback)
        
        sub2 = Subscription.create_task_subscription(
            subscriber_id="agent-2",
            task_id="task-456"
        )
        await manager.add_subscription(sub2, callback)
        
        # Route an event
        event = TaskEvent(
            id="evt-1",
            type=EventType.TASK_STATE_CHANGED,
            timestamp=datetime.utcnow(),
            source="test",
            task_id="task-123",
            data={}
        )
        
        routed = await manager.route_event(event)
        
        # Should have routed to 1 subscription
        assert routed == 1
        assert len(callback_invocations) == 1
        assert callback_invocations[0] == event
    
    @pytest.mark.asyncio
    async def test_remove_subscriber_subscriptions(self):
        """Test removing all subscriptions for a subscriber"""
        manager = SubscriptionManager()
        
        # Add multiple subscriptions for same subscriber
        sub1 = Subscription.create_task_subscription(
            subscriber_id="agent-1",
            task_id="task-123"
        )
        sub2 = Subscription.create_task_subscription(
            subscriber_id="agent-1",
            task_id="task-456"
        )
        sub3 = Subscription.create_task_subscription(
            subscriber_id="agent-2",
            task_id="task-789"
        )
        
        await manager.add_subscription(sub1)
        await manager.add_subscription(sub2)
        await manager.add_subscription(sub3)
        
        # Remove all subscriptions for agent-1
        removed = await manager.remove_subscriber_subscriptions("agent-1")
        
        assert removed == 2
        
        # agent-1 subscriptions should be gone
        subs = await manager.get_subscriber_subscriptions("agent-1")
        assert len(subs) == 0
        
        # agent-2 subscription should remain
        subs = await manager.get_subscriber_subscriptions("agent-2")
        assert len(subs) == 1