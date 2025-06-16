#!/usr/bin/env python3
"""
Complete SSE test - monitor all task lifecycle events
"""

import asyncio
import aiohttp
import json

async def test_complete_sse():
    """Test complete SSE streaming with all task events"""
    base_url = "http://localhost:8001/api/a2a/v1"
    
    async with aiohttp.ClientSession() as session:
        # Create a task
        print("Creating task...")
        request = {
            "jsonrpc": "2.0",
            "method": "task.create",
            "params": {
                "name": "Complete SSE Test",
                "description": "Test all lifecycle events",
                "priority": "high"
            },
            "id": 1
        }
        
        async with session.post(f"{base_url}/", json=request) as response:
            result = await response.json()
            task_id = result["result"]["task_id"]
            print(f"Created task: {task_id}\n")
        
        # Task updater
        async def update_task():
            await asyncio.sleep(1)
            
            # Update to running
            print("\n[Updater] Starting task...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.update_state",
                "params": {
                    "task_id": task_id,
                    "state": "running",
                    "message": "Task started"
                },
                "id": 2
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
            
            # Progress updates
            for progress in [0.25, 0.5, 0.75]:
                await asyncio.sleep(0.5)
                print(f"\n[Updater] Progress: {progress:.0%}")
                request = {
                    "jsonrpc": "2.0",
                    "method": "task.update_progress",
                    "params": {
                        "task_id": task_id,
                        "progress": progress,
                        "message": f"Processing... {progress:.0%}"
                    },
                    "id": 3
                }
                async with session.post(f"{base_url}/", json=request) as response:
                    await response.json()
            
            # Complete
            await asyncio.sleep(0.5)
            print("\n[Updater] Completing task...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.complete",
                "params": {
                    "task_id": task_id,
                    "output_data": {"result": "success", "items": 100},
                    "message": "Task completed successfully"
                },
                "id": 4
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
        
        # Start updater
        updater = asyncio.create_task(update_task())
        
        # Connect to SSE
        print("Connecting to SSE stream...")
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with session.get(
                f"{base_url}/stream/events",
                params={"task_id": task_id},
                timeout=timeout
            ) as response:
                print("Connected! Monitoring events...\n")
                print("-" * 60)
                
                event_count = 0
                buffer = ""
                
                async for chunk in response.content.iter_chunked(1024):
                    text = chunk.decode('utf-8')
                    buffer += text
                    
                    # Process complete events
                    while '\n\n' in buffer:
                        event_data, buffer = buffer.split('\n\n', 1)
                        
                        if not event_data.strip():
                            continue
                        
                        # Parse event
                        lines = event_data.strip().split('\n')
                        event = {}
                        data_lines = []
                        
                        for line in lines:
                            if line.startswith('id: '):
                                event['id'] = line[4:]
                            elif line.startswith('event: '):
                                event['event'] = line[7:]
                            elif line.startswith('data: '):
                                data_lines.append(line[6:])
                            elif line.startswith(': '):
                                print("[Keepalive]")
                        
                        if data_lines:
                            data_str = '\n'.join(data_lines)
                            try:
                                event['data'] = json.loads(data_str)
                            except:
                                event['data'] = data_str
                            
                            # Display event
                            event_count += 1
                            event_type = event.get('event', 'unknown')
                            data = event.get('data', {})
                            
                            print(f"\nEvent #{event_count}: {event_type}")
                            
                            if event_type == "connection.established":
                                print(f"  Connection ID: {data.get('data', {}).get('connection_id')}")
                            
                            elif event_type == "task.state_changed":
                                print(f"  State: {data.get('data', {}).get('old_state')} → {data.get('data', {}).get('new_state')}")
                                print(f"  Message: {data.get('data', {}).get('message')}")
                            
                            elif event_type == "task.progress":
                                print(f"  Progress: {data.get('data', {}).get('progress', 0) * 100:.0f}%")
                                print(f"  Message: {data.get('data', {}).get('message')}")
                            
                            elif event_type == "task.completed":
                                print(f"  State: {data.get('data', {}).get('state')}")
                                print(f"  Output: {data.get('data', {}).get('output_data')}")
                                print(f"  Message: {data.get('data', {}).get('message')}")
                                print("\n" + "-" * 60)
                                print("Task completed! Stream ending.")
                                return
                
        except asyncio.TimeoutError:
            print("\nStream timeout")
        except Exception as e:
            print(f"\nError: {type(e).__name__}: {e}")
        finally:
            # Wait for updater
            await updater

print("Complete SSE Streaming Test")
print("=" * 60)
asyncio.run(test_complete_sse())
print("\nTest finished!")