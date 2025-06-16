#!/usr/bin/env python3
"""
Manual test client for A2A channel-based pub/sub functionality.

This script demonstrates the channel features including:
- Creating and listing channels
- Subscribing to channels with patterns
- Publishing messages to channels
- Receiving channel events via WebSocket

Usage:
    python test_channels_complete.py [--host HOST] [--port PORT]
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import websockets
from uuid import uuid4


class ChannelTestClient:
    """Test client for A2A channel functionality"""
    
    def __init__(self, host: str = "localhost", port: int = 5001):
        self.host = host
        self.port = port
        self.ws_url = f"ws://{host}:{port}/a2a/v1/stream/websocket"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.agent_id = f"test-agent-{uuid4().hex[:8]}"
        self.request_id = 0
        
    def next_request_id(self) -> str:
        """Generate next request ID"""
        self.request_id += 1
        return f"req-{self.request_id}"
        
    async def connect(self):
        """Connect to WebSocket endpoint"""
        print(f"\n🔌 Connecting to {self.ws_url} as {self.agent_id}...")
        self.websocket = await websockets.connect(
            f"{self.ws_url}?agent_id={self.agent_id}"
        )
        print("✅ Connected successfully!")
        
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            print("\n🔌 Disconnected from WebSocket")
            
    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request and wait for response"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.next_request_id()
        }
        
        print(f"\n📤 Sending: {method}")
        print(f"   Params: {json.dumps(params, indent=2)}")
        
        await self.websocket.send(json.dumps(request))
        
        # Wait for response
        while True:
            message = await self.websocket.recv()
            data = json.loads(message)
            
            # Check if it's our response
            if data.get("id") == request["id"]:
                if "result" in data:
                    print(f"📥 Response: {json.dumps(data['result'], indent=2)}")
                    return data["result"]
                elif "error" in data:
                    print(f"❌ Error: {data['error']}")
                    return None
            else:
                # It's an event/notification
                print(f"📨 Event: {data.get('method', 'unknown')} - {json.dumps(data.get('params', {}), indent=2)}")
                
    async def listen_for_events(self, duration: int = 10):
        """Listen for events for specified duration"""
        print(f"\n👂 Listening for events for {duration} seconds...")
        end_time = asyncio.get_event_loop().time() + duration
        
        try:
            while asyncio.get_event_loop().time() < end_time:
                remaining = int(end_time - asyncio.get_event_loop().time())
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=1.0
                    )
                    data = json.loads(message)
                    
                    if "method" in data:  # It's an event
                        event_type = data["method"]
                        params = data.get("params", {})
                        
                        # Pretty print based on event type
                        if event_type == "event":
                            event_data = params.get("event", {})
                            print(f"\n📨 {event_data.get('type', 'unknown')} event:")
                            print(f"   Channel: {event_data.get('channel', 'N/A')}")
                            print(f"   Sender: {event_data.get('sender_id', 'N/A')}")
                            print(f"   Data: {json.dumps(event_data.get('data', {}), indent=2)}")
                        else:
                            print(f"\n📨 {event_type}: {json.dumps(params, indent=2)}")
                            
                except asyncio.TimeoutError:
                    print(f"\r⏱️  {remaining}s remaining...", end="", flush=True)
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped listening")
            
    async def run_channel_demo(self):
        """Run channel functionality demonstration"""
        try:
            await self.connect()
            
            print("\n" + "="*60)
            print("A2A CHANNEL PUB/SUB DEMONSTRATION")
            print("="*60)
            
            # 1. List existing channels
            print("\n1️⃣  LISTING EXISTING CHANNELS")
            await self.send_request("channel.list", {})
            
            # 2. Create channels
            print("\n2️⃣  CREATING CHANNELS")
            
            # Create metrics channels
            await self.send_request("channel.subscribe", {
                "agent_id": self.agent_id,
                "channel": "metrics.cpu"
            })
            
            await self.send_request("channel.subscribe", {
                "agent_id": self.agent_id,
                "channel": "metrics.memory"
            })
            
            # Create task channels
            await self.send_request("channel.subscribe", {
                "agent_id": self.agent_id,
                "channel": "tasks.created"
            })
            
            # 3. Subscribe to patterns
            print("\n3️⃣  SUBSCRIBING TO CHANNEL PATTERNS")
            
            # Subscribe to all metrics
            await self.send_request("channel.subscribe_pattern", {
                "agent_id": self.agent_id,
                "pattern": "metrics.*"
            })
            
            # Subscribe to all task events
            await self.send_request("channel.subscribe_pattern", {
                "agent_id": self.agent_id,
                "pattern": "tasks.**"
            })
            
            # 4. List channels with pattern
            print("\n4️⃣  LISTING CHANNELS WITH PATTERN")
            await self.send_request("channel.list", {
                "pattern": "metrics.*"
            })
            
            # 5. Get channel info
            print("\n5️⃣  GETTING CHANNEL INFORMATION")
            await self.send_request("channel.info", {
                "channel": "metrics.cpu"
            })
            
            # 6. Publish messages
            print("\n6️⃣  PUBLISHING MESSAGES TO CHANNELS")
            
            # Start listening task
            listen_task = asyncio.create_task(self.listen_for_events(15))
            
            # Give listener time to start
            await asyncio.sleep(1)
            
            # Publish to metrics.cpu
            await self.send_request("channel.publish", {
                "channel": "metrics.cpu",
                "message": {
                    "sender_id": self.agent_id,
                    "value": 45.2,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            await asyncio.sleep(1)
            
            # Publish to metrics.memory
            await self.send_request("channel.publish", {
                "channel": "metrics.memory",
                "message": {
                    "sender_id": self.agent_id,
                    "used": 1024,
                    "total": 2048,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            await asyncio.sleep(1)
            
            # Publish to tasks.created
            await self.send_request("channel.publish", {
                "channel": "tasks.created",
                "message": {
                    "sender_id": self.agent_id,
                    "task_id": f"task-{uuid4().hex[:8]}",
                    "name": "Process data",
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            await asyncio.sleep(1)
            
            # Publish to a sub-channel (should match tasks.**)
            await self.send_request("channel.publish", {
                "channel": "tasks.updates.progress",
                "message": {
                    "sender_id": self.agent_id,
                    "task_id": "task-12345",
                    "progress": 50,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
            
            # Wait for listener to complete
            await listen_task
            
            # 7. Unsubscribe
            print("\n7️⃣  UNSUBSCRIBING FROM CHANNEL")
            await self.send_request("channel.unsubscribe", {
                "agent_id": self.agent_id,
                "channel": "metrics.cpu"
            })
            
            print("\n" + "="*60)
            print("DEMONSTRATION COMPLETE!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            await self.disconnect()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test A2A channel pub/sub functionality"
    )
    parser.add_argument(
        "--host", 
        default="localhost", 
        help="Hermes host (default: localhost)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5001, 
        help="Hermes port (default: 5001)"
    )
    
    args = parser.parse_args()
    
    # Create and run test client
    client = ChannelTestClient(args.host, args.port)
    await client.run_channel_demo()


if __name__ == "__main__":
    print("\n🚀 A2A Channel Test Client")
    print("="*40)
    print("Make sure Hermes is running:")
    print("  tekton-launch -c hermes")
    print("="*40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")