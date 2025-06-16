"""
Integration tests for A2A SSE streaming functionality

These tests verify that SSE streaming works end-to-end with Hermes.
"""

import pytest
import asyncio
import httpx
import json
import time
from datetime import datetime


class TestStreamingIntegration:
    """Test SSE streaming integration with Hermes"""
    
    base_url = "http://localhost:8001/api/a2a/v1"
    
    @pytest.mark.asyncio
    async def test_sse_connection_and_events(self):
        """Test SSE connection establishment and event streaming"""
        async with httpx.AsyncClient() as client:
            # Create a task
            response = await client.post(
                f"{self.base_url}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "task.create",
                    "params": {
                        "name": "SSE Integration Test",
                        "description": "Testing SSE integration"
                    },
                    "id": 1
                }
            )
            assert response.status_code == 200
            result = response.json()
            task_id = result["result"]["task_id"]
            
            # Collect events
            events = []
            
            # Connect to SSE stream
            async with client.stream(
                "GET",
                f"{self.base_url}/stream/events",
                params={"task_id": task_id},
                timeout=5.0
            ) as stream_response:
                assert stream_response.status_code == 200
                assert stream_response.headers.get("content-type") == "text/event-stream; charset=utf-8"
                
                # Start task updates in background
                async def update_task():
                    await asyncio.sleep(0.5)
                    
                    # Update to running
                    await client.post(
                        f"{self.base_url}/",
                        json={
                            "jsonrpc": "2.0",
                            "method": "task.update_state",
                            "params": {
                                "task_id": task_id,
                                "state": "running"
                            },
                            "id": 2
                        }
                    )
                    
                    await asyncio.sleep(0.5)
                    
                    # Update progress
                    await client.post(
                        f"{self.base_url}/",
                        json={
                            "jsonrpc": "2.0",
                            "method": "task.update_progress",
                            "params": {
                                "task_id": task_id,
                                "progress": 0.5,
                                "message": "Halfway done"
                            },
                            "id": 3
                        }
                    )
                
                # Start updater
                updater = asyncio.create_task(update_task())
                
                # Read events for a few seconds
                start_time = time.time()
                buffer = ""
                
                async for chunk in stream_response.aiter_text():
                    buffer += chunk
                    
                    # Process complete events
                    while '\n\n' in buffer:
                        event_data, buffer = buffer.split('\n\n', 1)
                        
                        if event_data.strip():
                            # Parse SSE event
                            event = {}
                            data_lines = []
                            
                            for line in event_data.strip().split('\n'):
                                if line.startswith('event: '):
                                    event['type'] = line[7:]
                                elif line.startswith('data: '):
                                    data_lines.append(line[6:])
                            
                            if data_lines:
                                try:
                                    event['data'] = json.loads('\n'.join(data_lines))
                                    events.append(event)
                                except json.JSONDecodeError:
                                    pass
                    
                    # Stop after 3 seconds
                    if time.time() - start_time > 3:
                        break
                
                await updater
            
            # Verify we got the expected events
            event_types = [e.get('type') for e in events]
            
            # Should have connection established
            assert 'connection.established' in event_types
            
            # Should have task progress
            assert 'task.progress' in event_types
            
            # Verify progress event data
            progress_events = [e for e in events if e.get('type') == 'task.progress']
            assert len(progress_events) > 0
            assert progress_events[0]['data']['data']['progress'] == 0.5
    
    @pytest.mark.asyncio
    async def test_sse_filtering(self):
        """Test SSE event filtering by task_id"""
        async with httpx.AsyncClient() as client:
            # Create two tasks
            response1 = await client.post(
                f"{self.base_url}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "task.create",
                    "params": {"name": "Task 1"},
                    "id": 1
                }
            )
            task1_id = response1.json()["result"]["task_id"]
            
            response2 = await client.post(
                f"{self.base_url}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "task.create",
                    "params": {"name": "Task 2"},
                    "id": 2
                }
            )
            task2_id = response2.json()["result"]["task_id"]
            
            # Connect to SSE stream filtered by task1
            events = []
            
            async with client.stream(
                "GET",
                f"{self.base_url}/stream/events",
                params={"task_id": task1_id},
                timeout=3.0
            ) as stream_response:
                # Update both tasks
                async def update_tasks():
                    await asyncio.sleep(0.5)
                    
                    # Update task 1
                    await client.post(
                        f"{self.base_url}/",
                        json={
                            "jsonrpc": "2.0",
                            "method": "task.update_progress",
                            "params": {
                                "task_id": task1_id,
                                "progress": 0.3,
                                "message": "Task 1 progress"
                            },
                            "id": 3
                        }
                    )
                    
                    # Update task 2
                    await client.post(
                        f"{self.base_url}/",
                        json={
                            "jsonrpc": "2.0",
                            "method": "task.update_progress",
                            "params": {
                                "task_id": task2_id,
                                "progress": 0.7,
                                "message": "Task 2 progress"
                            },
                            "id": 4
                        }
                    )
                
                updater = asyncio.create_task(update_tasks())
                
                # Collect events
                start_time = time.time()
                buffer = ""
                
                async for chunk in stream_response.aiter_text():
                    buffer += chunk
                    
                    while '\n\n' in buffer:
                        event_data, buffer = buffer.split('\n\n', 1)
                        
                        if event_data.strip():
                            # Parse event
                            for line in event_data.strip().split('\n'):
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])
                                        if data.get('task_id'):
                                            events.append(data)
                                    except:
                                        pass
                    
                    if time.time() - start_time > 2:
                        break
                
                await updater
            
            # Verify only task1 events were received
            task_ids = [e.get('task_id') for e in events if e.get('task_id')]
            assert all(tid == task1_id for tid in task_ids)
            assert len(task_ids) > 0  # Should have at least one event
    
    @pytest.mark.asyncio
    async def test_subscription_management(self):
        """Test subscription CRUD operations"""
        async with httpx.AsyncClient() as client:
            # Create a subscription
            response = await client.post(
                f"{self.base_url}/subscriptions",
                json={
                    "subscriber_id": "test-agent-integration",
                    "subscription_type": "task",
                    "target": "task-*",
                    "event_types": ["task.state_changed", "task.completed"]
                }
            )
            assert response.status_code == 200
            result = response.json()
            sub_id = result["subscription_id"]
            
            # List subscriptions
            response = await client.get(
                f"{self.base_url}/subscriptions/test-agent-integration"
            )
            assert response.status_code == 200
            subs = response.json()["subscriptions"]
            assert len(subs) == 1
            assert subs[0]["id"] == sub_id
            
            # Delete subscription
            response = await client.delete(
                f"{self.base_url}/subscriptions/{sub_id}"
            )
            assert response.status_code == 200
            
            # Verify deletion
            response = await client.get(
                f"{self.base_url}/subscriptions/test-agent-integration"
            )
            assert response.status_code == 200
            subs = response.json()["subscriptions"]
            assert len(subs) == 0
    
    @pytest.mark.asyncio
    async def test_active_connections_monitoring(self):
        """Test monitoring of active SSE connections"""
        async with httpx.AsyncClient() as client:
            # Check initial connections
            response = await client.get(f"{self.base_url}/stream/connections")
            assert response.status_code == 200
            initial_count = response.json()["total_connections"]
            
            # Create an SSE connection
            async with client.stream(
                "GET",
                f"{self.base_url}/stream/events",
                timeout=2.0
            ) as stream:
                # Give it time to register
                await asyncio.sleep(0.5)
                
                # Check connections again
                response = await client.get(f"{self.base_url}/stream/connections")
                assert response.status_code == 200
                data = response.json()
                
                # Should have one more connection
                assert data["total_connections"] == initial_count + 1
                
                # Connection details should be present
                connections = data["connections"]
                assert len(connections) > 0
                
                # Check connection has expected fields
                conn_id = list(connections.keys())[0]
                conn = connections[conn_id]
                assert "id" in conn
                assert "active" in conn
                assert "created_at" in conn