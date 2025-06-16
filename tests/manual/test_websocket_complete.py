#!/usr/bin/env python3
"""
Manual test for A2A WebSocket streaming

This script demonstrates WebSocket connectivity with the A2A protocol,
including bidirectional JSON-RPC communication and event streaming.

Usage:
    python test_websocket_complete.py [--url URL] [--agent-id AGENT_ID]
"""

import asyncio
import json
import sys
import argparse
import signal
from datetime import datetime
from typing import Optional, Dict, Any

import websockets
from websockets.exceptions import WebSocketException


class WebSocketTestClient:
    """Test client for A2A WebSocket streaming"""
    
    def __init__(self, url: str, agent_id: Optional[str] = None):
        self.url = url
        self.agent_id = agent_id
        self.websocket = None
        self.running = True
        self.message_count = 0
        self.request_id = 0
    
    async def connect(self):
        """Connect to WebSocket endpoint"""
        # Build URL with query parameters
        params = []
        if self.agent_id:
            params.append(f"agent_id={self.agent_id}")
        
        full_url = self.url
        if params:
            full_url += "?" + "&".join(params)
        
        print(f"🔌 Connecting to: {full_url}")
        self.websocket = await websockets.connect(full_url)
        print(f"✅ Connected to WebSocket")
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Send a JSON-RPC request"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": str(self.request_id)
        }
        
        print(f"\n📤 Sending request: {method}")
        print(f"   ID: {request['id']}")
        print(f"   Params: {json.dumps(params, indent=2)}")
        
        await self.websocket.send(json.dumps(request))
    
    async def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Send a JSON-RPC notification"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        print(f"\n📢 Sending notification: {method}")
        print(f"   Params: {json.dumps(params, indent=2)}")
        
        await self.websocket.send(json.dumps(notification))
    
    async def receive_messages(self):
        """Receive and display messages"""
        try:
            async for message in self.websocket:
                self.message_count += 1
                
                try:
                    data = json.loads(message)
                    
                    # Determine message type
                    if "method" in data and "id" not in data:
                        # Notification (including events)
                        print(f"\n📨 [{self.message_count}] Notification received:")
                        print(f"   Method: {data['method']}")
                        if data['method'] == 'event.publish' and 'params' in data:
                            event = data['params']
                            print(f"   Event Type: {event.get('type', 'unknown')}")
                            print(f"   Event Data: {json.dumps(event.get('data', {}), indent=2)}")
                        else:
                            print(f"   Params: {json.dumps(data.get('params', {}), indent=2)}")
                    
                    elif "result" in data:
                        # Response
                        print(f"\n✅ [{self.message_count}] Response received:")
                        print(f"   ID: {data.get('id')}")
                        print(f"   Result: {json.dumps(data['result'], indent=2)}")
                    
                    elif "error" in data:
                        # Error response
                        print(f"\n❌ [{self.message_count}] Error received:")
                        print(f"   ID: {data.get('id')}")
                        print(f"   Error: {json.dumps(data['error'], indent=2)}")
                    
                    else:
                        # Unknown format
                        print(f"\n❓ [{self.message_count}] Unknown message:")
                        print(f"   {json.dumps(data, indent=2)}")
                
                except json.JSONDecodeError:
                    print(f"\n⚠️  [{self.message_count}] Invalid JSON received: {message}")
                
                if not self.running:
                    break
                    
        except WebSocketException as e:
            print(f"\n❌ WebSocket error: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
    
    async def test_basic_methods(self):
        """Test basic A2A methods"""
        # Test agent.list
        await self.send_request("agent.list")
        await asyncio.sleep(1)
        
        # Test task.list (without state parameter)
        await self.send_request("task.list")
        await asyncio.sleep(1)
        
        # Test creating a task
        await self.send_request("task.create", {
            "name": "WebSocket Test Task",
            "description": "Testing WebSocket bidirectional communication",
            "metadata": {"source": "websocket_test"}
        })
        await asyncio.sleep(1)
        
        # Send a test notification
        await self.send_notification("test.heartbeat", {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy"
        })
    
    async def run_interactive(self):
        """Run interactive mode"""
        print("\n🎮 Interactive Mode - Commands:")
        print("  list agents     - List all agents")
        print("  list tasks      - List all tasks")
        print("  create task     - Create a test task")
        print("  test echo       - Test echo method")
        print("  notify <text>   - Send a notification")
        print("  quit            - Exit")
        
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        while self.running:
            print("\n> ", end="", flush=True)
            
            # Read input with timeout
            try:
                line = await asyncio.wait_for(reader.readline(), timeout=1.0)
                if not line:
                    continue
                    
                command = line.decode().strip().lower()
                
                if command == "quit":
                    self.running = False
                    break
                elif command == "list agents":
                    await self.send_request("agent.list")
                elif command == "list tasks":
                    await self.send_request("task.list", {"state": "all"})
                elif command == "create task":
                    await self.send_request("task.create", {
                        "name": f"Interactive Task {datetime.now().strftime('%H:%M:%S')}",
                        "description": "Created via WebSocket interactive mode"
                    })
                elif command == "test echo":
                    await self.send_request("echo", {"message": "Hello from WebSocket!"})
                elif command.startswith("notify "):
                    text = command[7:]
                    await self.send_notification("user.message", {"text": text})
                else:
                    print(f"Unknown command: {command}")
                    
            except asyncio.TimeoutError:
                # No input, continue
                pass
            except Exception as e:
                print(f"Error: {e}")
    
    async def run(self, interactive: bool = False):
        """Run the test client"""
        try:
            await self.connect()
            
            # Start receiving messages
            receive_task = asyncio.create_task(self.receive_messages())
            
            if interactive:
                # Interactive mode
                await self.run_interactive()
            else:
                # Automated test mode
                print("\n🧪 Running automated tests...")
                await self.test_basic_methods()
                
                # Wait for responses
                print("\n⏳ Waiting for messages (10 seconds)...")
                await asyncio.sleep(10)
                print("\n✅ Test completed!")
            
            # Clean shutdown
            self.running = False
            await self.websocket.close()
            await receive_task
            
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
            print(f"\n📊 Total messages received: {self.message_count}")


def main():
    parser = argparse.ArgumentParser(description="Test A2A WebSocket streaming")
    parser.add_argument(
        "--url",
        default="ws://localhost:8001/api/a2a/v1/stream/ws",
        help="WebSocket URL (default: ws://localhost:8001/api/a2a/v1/stream/ws)"
    )
    parser.add_argument(
        "--agent-id",
        help="Agent ID to use for the connection"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    print("🚀 A2A WebSocket Test Client")
    print("=" * 40)
    print(f"URL: {args.url}")
    print(f"Agent ID: {args.agent_id or 'None'}")
    print(f"Mode: {'Interactive' if args.interactive else 'Automated'}")
    print("=" * 40)
    
    client = WebSocketTestClient(args.url, args.agent_id)
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        client.running = False
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the client
    asyncio.run(client.run(interactive=args.interactive))


if __name__ == "__main__":
    main()