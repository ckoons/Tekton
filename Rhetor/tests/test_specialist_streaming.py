#!/usr/bin/env python3
"""
Test script for the specialist streaming endpoints.

This script tests the new SSE streaming functionality with real Greek Chorus AIs.
"""

import asyncio
import aiohttp
import json
import sys
import time
from typing import AsyncIterator, Dict, Any


async def test_individual_streaming(specialist_id: str = "apollo-ai", message: str = "Tell me a short story"):
    """Test streaming from an individual specialist."""
    print(f"\n=== Testing Individual Streaming: {specialist_id} ===")
    print(f"Message: {message}")
    print("-" * 50)
    
    url = f"http://localhost:8003/api/chat/{specialist_id}/stream"
    params = {
        "message": message,
        "include_metadata": "true",
        "temperature": "0.7",
        "max_tokens": "500"
    }
    
    start_time = time.time()
    chunks_received = 0
    total_content = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    print(await response.text())
                    return
                
                # Process SSE stream
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        try:
                            data = json.loads(data_str)
                            
                            if data['type'] == 'chunk':
                                chunks_received += 1
                                content = data.get('content', '')
                                total_content.append(content)
                                
                                # Print chunk
                                print(content, end='', flush=True)
                                
                                # Show metadata for first few chunks
                                if chunks_received <= 3 and data.get('metadata'):
                                    print(f"\n[Metadata: chunk {chunks_received}, "
                                          f"tokens: {data['metadata'].get('total_tokens_so_far', 0)}, "
                                          f"time: {data['metadata'].get('elapsed_time', 0):.2f}s]")
                            
                            elif data['type'] == 'complete':
                                print("\n\n[Stream Complete]")
                                if data.get('summary'):
                                    summary = data['summary']
                                    print(f"Total chunks: {summary.get('total_chunks', 0)}")
                                    print(f"Total tokens: {summary.get('total_tokens', 0)}")
                                    print(f"Total time: {summary.get('total_time', 0):.2f}s")
                                    print(f"Model: {summary.get('model', 'unknown')}")
                            
                            elif data['type'] == 'error':
                                print(f"\n[Error: {data.get('error', 'Unknown error')}]")
                                
                        except json.JSONDecodeError as e:
                            print(f"\n[JSON Error: {e}]")
    
    except Exception as e:
        print(f"\n[Connection Error: {e}]")
    
    elapsed = time.time() - start_time
    print(f"\n\nTest completed in {elapsed:.2f}s")
    print(f"Received {chunks_received} chunks")
    print(f"Total content length: {len(''.join(total_content))} characters")


async def test_team_streaming(message: str = "What makes a good CI assistant?"):
    """Test streaming from all specialists simultaneously."""
    print(f"\n=== Testing Team Streaming (Greek Chorus) ===")
    print(f"Message: {message}")
    print("-" * 50)
    
    url = "http://localhost:8003/api/chat/team/stream"
    json_data = {
        "message": message,
        "include_metadata": True,
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    start_time = time.time()
    specialist_responses = {}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as response:
                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    print(await response.text())
                    return
                
                # Process SSE stream
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data_str = line[6:]
                        
                        try:
                            data = json.loads(data_str)
                            
                            if data['type'] == 'team_chunk':
                                specialist_id = data['specialist_id']
                                content = data.get('content', '')
                                
                                # Initialize specialist entry if needed
                                if specialist_id not in specialist_responses:
                                    specialist_responses[specialist_id] = {
                                        'content': [],
                                        'chunks': 0
                                    }
                                
                                specialist_responses[specialist_id]['content'].append(content)
                                specialist_responses[specialist_id]['chunks'] += 1
                                
                                # Show progress
                                if not data.get('is_final'):
                                    print(f".", end='', flush=True)
                                else:
                                    print(f"\n[{specialist_id} completed]")
                            
                            elif data['type'] == 'team_complete':
                                print("\n\n[Team Stream Complete]")
                                summary = data.get('summary', {})
                                print(f"Total AIs: {summary.get('total_ais', 0)}")
                                print(f"Completed streams: {summary.get('completed_streams', 0)}")
                                print(f"Total time: {summary.get('total_time', 0):.2f}s")
                            
                            elif data['type'] == 'specialist_error':
                                print(f"\n[Error from {data['specialist_id']}: {data.get('error')}]")
                                
                        except json.JSONDecodeError as e:
                            print(f"\n[JSON Error: {e}]")
    
    except Exception as e:
        print(f"\n[Connection Error: {e}]")
    
    # Show results
    print("\n\n=== Team Responses Summary ===")
    for specialist_id, response_data in specialist_responses.items():
        content = ''.join(response_data['content'])
        print(f"\n{specialist_id} ({response_data['chunks']} chunks):")
        print(f"{content[:200]}..." if len(content) > 200 else content)
    
    elapsed = time.time() - start_time
    print(f"\n\nTest completed in {elapsed:.2f}s")
    print(f"Received responses from {len(specialist_responses)} specialists")


async def test_metadata_tracking():
    """Test enhanced metadata tracking in streams."""
    print("\n=== Testing Enhanced Metadata Tracking ===")
    
    specialist_id = "athena-ai"
    message = "Explain the concept of emergence in complex systems"
    
    url = f"http://localhost:8003/api/chat/{specialist_id}/stream"
    params = {
        "message": message,
        "include_metadata": "true",
        "reasoning_depth": "2"  # Track reasoning depth
    }
    
    metadata_samples = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    return
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data_str = line[6:]
                        
                        try:
                            data = json.loads(data_str)
                            
                            if data.get('metadata'):
                                metadata_samples.append(data['metadata'])
                                
                                # Show first few metadata samples
                                if len(metadata_samples) <= 3:
                                    print(f"\nMetadata sample {len(metadata_samples)}:")
                                    for key, value in data['metadata'].items():
                                        print(f"  {key}: {value}")
                        
                        except json.JSONDecodeError:
                            pass
    
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n\nCollected {len(metadata_samples)} metadata samples")
    
    # Analyze metadata trends
    if metadata_samples:
        avg_tokens = sum(m.get('total_tokens_so_far', 0) for m in metadata_samples) / len(metadata_samples)
        max_reasoning = max(m.get('reasoning_depth', 0) for m in metadata_samples)
        
        print(f"Average tokens per chunk: {avg_tokens:.1f}")
        print(f"Maximum reasoning depth: {max_reasoning}")


async def main():
    """Run all tests."""
    print("Starting Specialist Streaming Tests")
    print("=" * 60)
    
    # Test 1: Individual specialist streaming
    await test_individual_streaming("apollo-ai", "Write a haiku about coding")
    
    # Small delay between tests
    await asyncio.sleep(2)
    
    # Test 2: Team streaming
    await test_team_streaming("What is the meaning of consciousness?")
    
    # Small delay
    await asyncio.sleep(2)
    
    # Test 3: Metadata tracking
    await test_metadata_tracking()
    
    print("\n\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())