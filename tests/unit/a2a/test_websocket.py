"""
Unit tests for A2A WebSocket implementation
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from tekton.a2a.streaming.websocket import (
    WebSocketConnection,
    WebSocketManager,
    ConnectionState,
    websocket_manager,
    handle_websocket
)
from tekton.a2a.streaming.events import StreamEvent, EventType, TaskEvent
from tekton.a2a import (
    JSONRPCRequest,
    JSONRPCResponse
)


class TestWebSocketConnection:
    """Test WebSocketConnection class"""
    
    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock()
        ws.close = AsyncMock()
        ws.state = WebSocketState.CONNECTED  # Add state attribute
        return ws
    
    @pytest.fixture
    def connection(self, mock_websocket):
        """Create a WebSocketConnection instance"""
        return WebSocketConnection(
            connection_id="test-conn-1",
            websocket=mock_websocket,
            agent_id="agent-1",
            filters={"task_id": "task-1"}
        )
    
    @pytest.mark.asyncio
    async def test_connection_initialization(self, connection):
        """Test WebSocket connection is initialized correctly"""
        assert connection.id == "test-conn-1"
        assert connection.agent_id == "agent-1"
        assert connection.filters == {"task_id": "task-1"}
        assert connection.state == ConnectionState.CONNECTING
        assert connection.message_count == 0
        assert connection.error_count == 0
    
    @pytest.mark.asyncio
    async def test_accept_connection(self, connection, mock_websocket):
        """Test accepting WebSocket connection"""
        await connection.accept()
        
        mock_websocket.accept.assert_called_once()
        assert connection.state == ConnectionState.CONNECTED
    
    @pytest.mark.asyncio
    async def test_send_message_dict(self, connection, mock_websocket):
        """Test sending a dictionary message"""
        connection.state = ConnectionState.CONNECTED
        message = {"test": "data"}
        
        result = await connection.send_message(message)
        
        assert result is True
        mock_websocket.send_text.assert_called_once_with('{"test": "data"}')
        assert connection.message_count == 1
    
    @pytest.mark.asyncio
    async def test_send_message_string(self, connection, mock_websocket):
        """Test sending a string message"""
        connection.state = ConnectionState.CONNECTED
        message = '{"test": "data"}'
        
        result = await connection.send_message(message)
        
        assert result is True
        mock_websocket.send_text.assert_called_once_with(message)
        assert connection.message_count == 1
    
    @pytest.mark.asyncio
    async def test_send_message_not_connected(self, connection):
        """Test sending message when not connected"""
        connection.state = ConnectionState.DISCONNECTED
        
        result = await connection.send_message({"test": "data"})
        
        assert result is False
        assert connection.message_count == 0
    
    @pytest.mark.asyncio
    async def test_send_request(self, connection, mock_websocket):
        """Test sending a JSON-RPC request"""
        connection.state = ConnectionState.CONNECTED
        
        # Mock the response handling
        async def mock_send(text):
            # Parse the request
            request = json.loads(text)
            # Simulate receiving a response
            if request["method"] == "test.method":
                response = JSONRPCResponse(
                    id=request["id"],
                    result={"success": True}
                )
                # Set the future result
                future = connection.pending_requests.get(request["id"])
                if future:
                    future.set_result(response.result)
        
        mock_websocket.send_text.side_effect = mock_send
        
        # Send request
        result = await connection.send_request("test.method", {"param": "value"})
        
        assert result == {"success": True}
        assert len(connection.pending_requests) == 0
    
    @pytest.mark.asyncio
    async def test_send_request_timeout(self, connection, mock_websocket):
        """Test request timeout"""
        connection.state = ConnectionState.CONNECTED
        
        with pytest.raises(asyncio.TimeoutError):
            await connection.send_request("test.method", timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_send_notification(self, connection, mock_websocket):
        """Test sending a JSON-RPC notification"""
        connection.state = ConnectionState.CONNECTED
        
        result = await connection.send_notification("test.notify", {"data": "value"})
        
        assert result is True
        call_args = mock_websocket.send_text.call_args[0][0]
        message = json.loads(call_args)
        assert message["method"] == "test.notify"
        assert message["params"] == {"data": "value"}
        assert "id" not in message
    
    @pytest.mark.asyncio
    async def test_send_event(self, connection, mock_websocket):
        """Test sending a stream event"""
        connection.state = ConnectionState.CONNECTED
        event = StreamEvent(
            id=str(uuid4()),
            type=EventType.TASK_CREATED,
            timestamp=datetime.now(timezone.utc),
            source="test",
            data={"task_id": "task-1"}
        )
        
        result = await connection.send_event(event)
        
        assert result is True
        call_args = mock_websocket.send_text.call_args[0][0]
        message = json.loads(call_args)
        assert message["method"] == "event.publish"
        assert "params" in message
    
    @pytest.mark.asyncio
    async def test_close_connection(self, connection, mock_websocket):
        """Test closing connection"""
        connection.state = ConnectionState.CONNECTED
        
        await connection.close()
        
        mock_websocket.close.assert_called_once_with(code=1000, reason="Normal closure")
        assert connection.state == ConnectionState.DISCONNECTED
        assert len(connection.pending_requests) == 0
    
    def test_matches_filters_task_id(self, connection):
        """Test event filtering by task_id"""
        event1 = TaskEvent(
            id=str(uuid4()),
            type=EventType.TASK_CREATED,
            timestamp=datetime.now(timezone.utc),
            source="test",
            task_id="task-1",
            task_name="Test Task 1",
            data={}
        )
        event2 = TaskEvent(
            id=str(uuid4()),
            type=EventType.TASK_CREATED,
            timestamp=datetime.now(timezone.utc),
            source="test",
            task_id="task-2",
            task_name="Test Task 2",
            data={}
        )
        
        assert connection.matches_filters(event1) is True
        assert connection.matches_filters(event2) is False
    
    def test_matches_filters_event_types(self):
        """Test event filtering by event types"""
        connection = WebSocketConnection(
            connection_id="test",
            websocket=MagicMock(),
            filters={"event_types": ["task.created", "task.completed"]}
        )
        
        event1 = StreamEvent(
            id=str(uuid4()),
            type=EventType.TASK_CREATED,
            timestamp=datetime.now(timezone.utc),
            source="test",
            data={}
        )
        event2 = StreamEvent(
            id=str(uuid4()),
            type=EventType.TASK_PROGRESS,
            timestamp=datetime.now(timezone.utc),
            source="test",
            data={}
        )
        
        assert connection.matches_filters(event1) is True
        assert connection.matches_filters(event2) is False


class TestWebSocketManager:
    """Test WebSocketManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create a WebSocketManager instance"""
        return WebSocketManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock()
        ws.close = AsyncMock()
        ws.state = WebSocketState.CONNECTED  # Add state attribute
        return ws
    
    @pytest.mark.asyncio
    async def test_connect(self, manager, mock_websocket):
        """Test connecting a new WebSocket"""
        connection = await manager.connect(
            websocket=mock_websocket,
            agent_id="agent-1",
            filters={"task_id": "task-1"}
        )
        
        assert connection.id in manager.connections
        assert connection.agent_id == "agent-1"
        assert connection.state == ConnectionState.CONNECTED
        mock_websocket.accept.assert_called_once()
        
        # Check initial connection event was sent
        mock_websocket.send_text.assert_called()
        call_args = mock_websocket.send_text.call_args[0][0]
        message = json.loads(call_args)
        assert message["method"] == "event.publish"
    
    @pytest.mark.asyncio
    async def test_disconnect(self, manager, mock_websocket):
        """Test disconnecting a WebSocket"""
        # Connect first
        connection = await manager.connect(mock_websocket)
        connection_id = connection.id
        
        # Disconnect
        await manager.disconnect(connection_id)
        
        assert connection_id not in manager.connections
        mock_websocket.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_event(self, manager, mock_websocket):
        """Test broadcasting event to connections"""
        # Create multiple connections
        ws1 = AsyncMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws1.state = WebSocketState.CONNECTED
        ws1.close = AsyncMock()
        
        ws2 = AsyncMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        ws2.state = WebSocketState.CONNECTED
        ws2.close = AsyncMock()
        
        conn1 = await manager.connect(ws1, filters={"task_id": "task-1"})
        conn2 = await manager.connect(ws2, filters={"task_id": "task-2"})
        
        # Broadcast event
        event = TaskEvent(
            id=str(uuid4()),
            type=EventType.TASK_CREATED,
            timestamp=datetime.now(timezone.utc),
            source="test",
            task_id="task-1",
            task_name="Test Task",
            data={}
        )
        
        await manager.broadcast_event(event)
        
        # Only conn1 should receive the event (matching filter)
        assert ws1.send_text.call_count >= 2  # Initial + broadcast
        assert ws2.send_text.call_count == 1  # Only initial
    
    @pytest.mark.asyncio
    async def test_send_to_agent(self, manager, mock_websocket):
        """Test sending notification to specific agent"""
        # Create connections
        ws1 = AsyncMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws1.state = WebSocketState.CONNECTED
        ws1.close = AsyncMock()
        
        ws2 = AsyncMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        ws2.state = WebSocketState.CONNECTED
        ws2.close = AsyncMock()
        
        await manager.connect(ws1, agent_id="agent-1")
        await manager.connect(ws2, agent_id="agent-2")
        
        # Send to agent-1
        count = await manager.send_to_agent("agent-1", "test.method", {"data": "value"})
        
        assert count == 1
        assert ws1.send_text.call_count >= 2  # Initial + notification
        assert ws2.send_text.call_count == 1  # Only initial
    
    def test_get_connection(self, manager):
        """Test getting connection by ID"""
        connection = WebSocketConnection(
            connection_id="test-id",
            websocket=MagicMock()
        )
        manager.connections["test-id"] = connection
        
        result = manager.get_connection("test-id")
        assert result is connection
        
        result = manager.get_connection("non-existent")
        assert result is None
    
    def test_get_connections_for_agent(self, manager):
        """Test getting connections for specific agent"""
        conn1 = WebSocketConnection("c1", MagicMock(), agent_id="agent-1")
        conn2 = WebSocketConnection("c2", MagicMock(), agent_id="agent-1")
        conn3 = WebSocketConnection("c3", MagicMock(), agent_id="agent-2")
        
        manager.connections = {"c1": conn1, "c2": conn2, "c3": conn3}
        
        connections = manager.get_connections_for_agent("agent-1")
        assert len(connections) == 2
        assert conn1 in connections
        assert conn2 in connections
        assert conn3 not in connections
    
    @pytest.mark.asyncio
    async def test_handle_request(self, manager, mock_websocket):
        """Test handling incoming JSON-RPC request"""
        connection = await manager.connect(mock_websocket)
        
        # Set up request handler
        async def handler(conn, request):
            if request.method == "test.echo":
                return request.params
        
        manager.on_request = handler
        
        # Simulate receiving a request
        request = JSONRPCRequest(
            id="req-1",
            method="test.echo",
            params={"message": "hello"}
        )
        
        await manager._handle_request(connection, request)
        
        # Check response was sent
        mock_websocket.send_text.assert_called()
        response_text = mock_websocket.send_text.call_args_list[-1][0][0]
        response = json.loads(response_text)
        assert response["id"] == "req-1"
        assert response["result"] == {"message": "hello"}
    
    @pytest.mark.asyncio
    async def test_handle_notification(self, manager, mock_websocket):
        """Test handling incoming JSON-RPC notification"""
        connection = await manager.connect(mock_websocket)
        
        # Set up notification handler
        handler_called = False
        async def handler(conn, notification):
            nonlocal handler_called
            handler_called = True
        
        manager.on_notification = handler
        
        # Simulate receiving a notification (request without ID)
        notification = JSONRPCRequest(
            method="test.notify",
            params={"data": "value"},
            id=None
        )
        
        await manager._handle_notification(connection, notification)
        
        assert handler_called is True
    
    @pytest.mark.asyncio
    async def test_close_all(self, manager):
        """Test closing all connections"""
        # Create multiple connections
        ws1 = AsyncMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.close = AsyncMock()
        ws1.state = WebSocketState.CONNECTED
        
        ws2 = AsyncMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.close = AsyncMock()
        ws2.state = WebSocketState.CONNECTED
        
        await manager.connect(ws1)
        await manager.connect(ws2)
        
        # Close all
        await manager.close_all()
        
        assert len(manager.connections) == 0
        ws1.close.assert_called_once()
        ws2.close.assert_called_once()


class TestWebSocketIntegration:
    """Test WebSocket integration functions"""
    
    @pytest.mark.asyncio
    async def test_handle_websocket(self):
        """Test handle_websocket function"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()
        mock_ws.receive_text = AsyncMock(side_effect=Exception("Disconnect"))
        mock_ws.close = AsyncMock()
        
        # Mock handlers
        request_handler = AsyncMock()
        notification_handler = AsyncMock()
        
        # Clear existing connections
        websocket_manager.connections.clear()
        
        # Handle connection
        await handle_websocket(
            websocket=mock_ws,
            agent_id="test-agent",
            filters={"task_id": "test-task"},
            on_request=request_handler,
            on_notification=notification_handler
        )
        
        # Connection should be cleaned up after error
        assert len(websocket_manager.connections) == 0