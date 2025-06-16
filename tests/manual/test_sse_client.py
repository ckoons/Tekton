#!/usr/bin/env python3
"""
Test SSE streaming with proper SSE client
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_sse_stream():
    """Test SSE streaming with proper event parsing"""
    base_url = "http://localhost:8001/api/a2a/v1"
    
    async with aiohttp.ClientSession() as session:
        # Create a task
        print("Creating task...")
        request = {
            "jsonrpc": "2.0",
            "method": "task.create",
            "params": {
                "name": "SSE Test Task",
                "description": "Testing SSE streaming"
            },
            "id": 1
        }
        
        async with session.post(f"{base_url}/", json=request) as response:
            result = await response.json()
            task_id = result["result"]["task_id"]
            print(f"Created task: {task_id}\n")
        
        # Start task updater in background
        async def update_task():
            await asyncio.sleep(2)
            
            # Update to running
            print("[Updater] Changing state to running...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.update_state",
                "params": {
                    "task_id": task_id,
                    "state": "running"
                },
                "id": 2
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
            
            # Update progress
            await asyncio.sleep(1)
            print("[Updater] Updating progress...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.update_progress",
                "params": {
                    "task_id": task_id,
                    "progress": 0.5,
                    "message": "Halfway done"
                },
                "id": 3
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
            
            # Complete task
            await asyncio.sleep(1)
            print("[Updater] Completing task...")
            request = {
                "jsonrpc": "2.0",
                "method": "task.complete",
                "params": {
                    "task_id": task_id,
                    "output_data": {"result": "success"}
                },
                "id": 4
            }
            async with session.post(f"{base_url}/", json=request) as response:
                await response.json()
        
        # Start updater
        updater = asyncio.create_task(update_task())
        
        # Connect to SSE stream
        print("Connecting to SSE stream...")
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.get(
                f"{base_url}/stream/events",
                params={"task_id": task_id},
                timeout=timeout
            ) as response:
                print(f"Connected! Status: {response.status}")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print("\nWaiting for events...\n")
                
                # Read SSE stream
                buffer = ""
                event_count = 0
                
                async for chunk in response.content.iter_chunked(1024):
                    text = chunk.decode('utf-8')
                    buffer += text
                    
                    # Process complete events
                    while '\n\n' in buffer:
                        event_data, buffer = buffer.split('\n\n', 1)
                        
                        # Skip empty events
                        if not event_data.strip():
                            continue
                        
                        # Parse SSE event
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
                                # Comment/keepalive
                                print("[Keepalive]")
                        
                        if data_lines:
                            # Join multiline data
                            data_str = '\n'.join(data_lines)
                            try:
                                event['data'] = json.loads(data_str)
                            except:
                                event['data'] = data_str
                            
                            # Display event
                            event_count += 1
                            print(f"Event #{event_count}:")
                            print(f"  Type: {event.get('event', 'unknown')}")
                            print(f"  ID: {event.get('id', 'none')}")
                            if isinstance(event.get('data'), dict):
                                print(f"  Data: {json.dumps(event['data'], indent=4)}")
                            else:
                                print(f"  Data: {event.get('data')}")
                            print()
                            
                            # Stop after task completes
                            if event.get('event') == 'task.completed':
                                print("Task completed! Stopping stream.")
                                break
                
        except asyncio.TimeoutError:
            print("Stream timeout reached")
        except Exception as e:
            print(f"Stream error: {type(e).__name__}: {e}")
        
        # Wait for updater
        await updater
        print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_sse_stream())