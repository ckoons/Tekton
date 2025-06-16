#!/usr/bin/env python3
"""
Test script for Rhetor SSE streaming functionality.

This script demonstrates and tests the real-time streaming capabilities
added in Phase 4A of the Rhetor AI Integration Sprint.
"""

import asyncio
import aiohttp
import json
import argparse
from datetime import datetime


class StreamingClient:
    """Client for testing SSE streaming endpoints."""
    
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_basic_streaming(self):
        """Test the basic SSE streaming test endpoint."""
        print("\n=== Testing Basic SSE Streaming ===")
        url = f"{self.base_url}/api/mcp/v2/stream/test"
        
        async with self.session.get(url) as response:
            print(f"Connected to {url}")
            print(f"Status: {response.status}")
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Event: {data}")
    
    async def test_streaming_tool(self, tool_name, arguments):
        """Test a specific MCP tool with streaming."""
        print(f"\n=== Testing Streaming Tool: {tool_name} ===")
        url = f"{self.base_url}/api/mcp/v2/stream"
        
        payload = {
            "tool_name": tool_name,
            "arguments": arguments,
            "stream_options": {
                "include_progress": True,
                "chunk_size": "sentence"
            }
        }
        
        async with self.session.post(url, json=payload) as response:
            print(f"Connected to streaming endpoint")
            print(f"Status: {response.status}")
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                
                if line.startswith('event:'):
                    event_type = line[6:].strip()
                elif line.startswith('data:'):
                    try:
                        data = json.loads(line[5:])
                        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                        
                        if event_type == 'connected':
                            print(f"[{timestamp}] 🔗 Connected: {data.get('message')}")
                        elif event_type == 'progress':
                            stage = data.get('stage', '')
                            percentage = data.get('percentage', 0)
                            message = data.get('message', '')
                            print(f"[{timestamp}] 📊 Progress [{stage}] {percentage}%: {message}")
                        elif event_type == 'chunk':
                            content = data.get('content', {})
                            specialist = content.get('specialist', 'unknown')
                            chunk_text = content.get('content', '')
                            progress = content.get('progress', 0)
                            print(f"[{timestamp}] 💬 [{specialist}] ({progress}%): {chunk_text}")
                        elif event_type == 'message':
                            speaker = data.get('speaker', 'unknown')
                            content = data.get('content', '')
                            round_num = data.get('round', 0)
                            print(f"[{timestamp}] 🗣️  [{speaker}] Round {round_num}: {content}")
                        elif event_type == 'complete':
                            result = data.get('result', {})
                            exec_time = data.get('execution_time', 0)
                            print(f"[{timestamp}] ✅ Complete in {exec_time:.2f}s")
                            if result:
                                print(f"    Result: {json.dumps(result, indent=2)}")
                        elif event_type == 'error':
                            error = data.get('error', 'Unknown error')
                            print(f"[{timestamp}] ❌ Error: {error}")
                        elif event_type == 'disconnect':
                            print(f"[{timestamp}] 🔌 Disconnected: {data.get('message')}")
                        else:
                            print(f"[{timestamp}] 📨 {event_type}: {data}")
                    except json.JSONDecodeError as e:
                        print(f"[{timestamp}] ⚠️  Failed to parse data: {line}")


async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description="Test Rhetor SSE streaming functionality")
    parser.add_argument("--host", default="localhost", help="Rhetor host")
    parser.add_argument("--port", default=8003, type=int, help="Rhetor port")
    parser.add_argument("--test", choices=["basic", "specialist", "team", "all"], 
                       default="all", help="Which test to run")
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    
    async with StreamingClient(base_url) as client:
        try:
            if args.test in ["basic", "all"]:
                await client.test_basic_streaming()
                await asyncio.sleep(1)
            
            if args.test in ["specialist", "all"]:
                # Test streaming message to specialist
                await client.test_streaming_tool(
                    "SendMessageToSpecialistStream",
                    {
                        "specialist_id": "rhetor-orchestrator",
                        "message": "Please analyze the current system performance and provide optimization recommendations.",
                        "message_type": "chat"
                    }
                )
                await asyncio.sleep(1)
            
            if args.test in ["team", "all"]:
                # Test streaming team chat
                await client.test_streaming_tool(
                    "OrchestrateTeamChatStream",
                    {
                        "topic": "Optimizing Tekton Performance",
                        "specialists": ["rhetor-orchestrator", "apollo-coordinator", "engram-memory"],
                        "initial_prompt": "What are the key areas we should focus on for performance improvements?",
                        "max_rounds": 2,
                        "orchestration_style": "collaborative"
                    }
                )
        
        except aiohttp.ClientError as e:
            print(f"\n❌ Connection error: {e}")
            print("\nMake sure Rhetor is running:")
            print("  tekton-launch -c rhetor")
            print(f"  Check if service is available at {base_url}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Rhetor SSE Streaming Test Client")
    print("===================================")
    asyncio.run(main())