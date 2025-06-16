#!/usr/bin/env python3
"""
Manual test for A2A SSE streaming functionality

This script demonstrates:
1. Creating a task and monitoring its progress via SSE
2. Subscribing to task events
3. Updating task state and progress
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime


async def test_sse_streaming():
    """Test SSE streaming with task updates"""
    base_url = "http://localhost:8001/api/a2a/v1"
    
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("A2A SSE Streaming Test")
        print("=" * 60)
        
        # Step 1: Create a task
        print("\n1. Creating a task...")
        request = {
            "jsonrpc": "2.0",
            "method": "task.create",
            "params": {
                "name": "SSE Test Task",
                "description": "Task to test SSE streaming",
                "input_data": {"test": True},
                "priority": "high"
            },
            "id": 1
        }
        
        async with session.post(f"{base_url}/", json=request) as response:
            result = await response.json()
            task_id = result["result"]["task_id"]
            print(f"   Created task: {task_id}")
        
        # Step 2: Start SSE connection to monitor the task
        print(f"\n2. Starting SSE connection for task {task_id}...")
        print("   (Press Ctrl+C to stop)\n")
        
        # Create a separate task to update the task state
        async def update_task():
            await asyncio.sleep(2)
            
            # Update to running
            print("\n   [Updater] Changing task state to 'running'...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.update_state",
                "params": {
                    "task_id": task_id,
                    "state": "running",
                    "message": "Starting task execution"
                },
                "id": 2
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
            
            # Update progress
            for progress in [0.25, 0.5, 0.75, 1.0]:
                await asyncio.sleep(1)
                print(f"\n   [Updater] Setting progress to {progress:.0%}...")
                request = {
                    "jsonrpc": "2.0",
                    "method": "task.update_progress",
                    "params": {
                        "task_id": task_id,
                        "progress": progress,
                        "message": f"Processing... {progress:.0%} complete"
                    },
                    "id": 3
                }
                async with session.post(f"{base_url}/", json=request) as response:
                    await response.json()
            
            # Complete the task
            await asyncio.sleep(1)
            print("\n   [Updater] Completing task...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.complete",
                "params": {
                    "task_id": task_id,
                    "output_data": {"result": "success", "processed": 100},
                    "message": "Task completed successfully"
                },
                "id": 4
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
        
        # Start the updater task
        updater = asyncio.create_task(update_task())
        
        # Connect to SSE stream
        try:
            async with session.get(
                f"{base_url}/stream/events",
                params={"task_id": task_id}
            ) as response:
                print("   Connected to SSE stream")
                print("   Waiting for events...\n")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            event = json.loads(data)
                            timestamp = event.get('timestamp', '')
                            event_type = event.get('type', 'unknown')
                            
                            print(f"[{timestamp}] Event: {event_type}")
                            
                            if event_type == "task.state_changed":
                                old_state = event['data'].get('old_state', '?')
                                new_state = event['data'].get('new_state', '?')
                                print(f"   State: {old_state} → {new_state}")
                            
                            elif event_type == "task.progress":
                                progress = event['data'].get('progress', 0)
                                message = event['data'].get('message', '')
                                print(f"   Progress: {progress:.0%} - {message}")
                            
                            elif event_type == "task.completed":
                                print("   Task completed!")
                                print(f"   Result: {json.dumps(event.get('data', {}), indent=2)}")
                                break
                            
                            print()
                            
                        except json.JSONDecodeError:
                            if data:
                                print(f"   Non-JSON data: {data}")
                    
                    elif line.startswith('event: '):
                        # Event type line, skip
                        pass
                    
                    elif line.startswith('id: '):
                        # Event ID line, skip
                        pass
                    
                    elif line.startswith(': '):
                        # Comment/keepalive
                        print("   [Keepalive]")
        
        except asyncio.CancelledError:
            print("\n   SSE connection cancelled")
        
        # Wait for updater to finish
        await updater
        
        print("\n" + "=" * 60)
        print("Test completed!")


async def test_subscriptions():
    """Test subscription management"""
    base_url = "http://localhost:8001/api/a2a/v1"
    
    async with aiohttp.ClientSession() as session:
        print("\n" + "=" * 60)
        print("Subscription Management Test")
        print("=" * 60)
        
        # Create a subscription
        print("\n1. Creating a task subscription...")
        subscription_data = {
            "subscriber_id": "test-agent-123",
            "subscription_type": "task",
            "target": "task-*",  # Would need pattern matching
            "event_types": ["task.state_changed", "task.completed"]
        }
        
        async with session.post(
            f"{base_url}/subscriptions",
            json=subscription_data
        ) as response:
            result = await response.json()
            if response.status == 200:
                sub_id = result["subscription_id"]
                print(f"   Created subscription: {sub_id}")
            else:
                print(f"   Error: {result}")
                return
        
        # List subscriptions
        print("\n2. Listing subscriptions for subscriber...")
        async with session.get(
            f"{base_url}/subscriptions/test-agent-123"
        ) as response:
            result = await response.json()
            print(f"   Found {len(result['subscriptions'])} subscription(s)")
            for sub in result['subscriptions']:
                print(f"   - {sub['id']}: {sub['subscription_type']} on {sub['target']}")
        
        # Get active connections
        print("\n3. Checking active SSE connections...")
        async with session.get(
            f"{base_url}/stream/connections"
        ) as response:
            result = await response.json()
            print(f"   Active connections: {result['total_connections']}")
        
        # Remove subscription
        print("\n4. Removing subscription...")
        async with session.delete(
            f"{base_url}/subscriptions/{sub_id}"
        ) as response:
            if response.status == 200:
                print("   Subscription removed")
            else:
                print(f"   Error: {response.status}")


async def main():
    """Run all tests"""
    try:
        # Test SSE streaming
        await test_sse_streaming()
        
        # Test subscription management
        await test_subscriptions()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("A2A SSE Streaming Manual Test")
    print("Make sure Hermes is running on port 8001")
    print()
    
    asyncio.run(main())