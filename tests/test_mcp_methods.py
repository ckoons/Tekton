#!/usr/bin/env python3
"""
Test script for MCP methods implementation.

Tests the following MCP methods:
1. GetSpecialistConversationHistory - Queries Engram for conversation history
2. ConfigureOrchestration - Configures AI routing strategies
3. send_message_to_specialist_stream - Streaming variant of specialist messaging
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add Tekton to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Rhetor.rhetor.core.mcp.tools_integration_unified import MCPToolsIntegrationUnified


async def test_get_specialist_conversation_history():
    """Test GetSpecialistConversationHistory method."""
    print("\n=== Testing GetSpecialistConversationHistory ===")
    
    mcp = MCPToolsIntegrationUnified()
    
    # Test 1: Get history for a specific specialist
    print("\n1. Testing conversation history for apollo-ci...")
    result = await mcp.get_specialist_conversation_history(
        specialist_id="apollo-ci",
        limit=5
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Conversations found: {result.get('conversation_count', 0)}")
    
    if result['success'] and result.get('conversations'):
        print("\nFirst conversation preview:")
        conv = result['conversations'][0]
        print(f"  Conversation ID: {conv.get('conversation_id')}")
        print(f"  Messages: {len(conv.get('messages', []))}")
        print(f"  Score: {conv['metadata'].get('score', 0.0)}")
    
    # Test 2: Get history with specific context
    print("\n2. Testing with specific context ID...")
    result = await mcp.get_specialist_conversation_history(
        specialist_id="athena-ci",
        limit=3,
        context_id="test_context_123"
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Query metadata: {json.dumps(result.get('query_metadata', {}), indent=2)}")
    
    # Test 3: Test error handling (Engram unavailable)
    print("\n3. Testing error handling...")
    # This will fail if Engram is not running
    if not result['success']:
        print(f"Expected error handled: {result.get('error')}")


async def test_configure_orchestration():
    """Test ConfigureOrchestration method."""
    print("\n\n=== Testing ConfigureOrchestration ===")
    
    mcp = MCPToolsIntegrationUnified()
    
    # Note: This will fail because routing_engine is not initialized
    # but we can test the validation logic
    
    # Test 1: Best-fit routing mode
    print("\n1. Testing best-fit routing configuration...")
    config = {
        "routing_mode": "best_fit",
        "context_weight": 0.7,
        "fallback_chain": ["apollo-ci", "athena-ci", "hermes-ci"],
        "load_threshold": 50
    }
    
    result = await mcp.configure_orchestration(config)
    print(f"Success: {result.get('success')}")
    if not result['success']:
        print(f"Expected error (no routing engine): {result.get('error')}")
    
    # Test 2: Context-aware routing with custom rules
    print("\n2. Testing context-aware routing with custom rules...")
    config = {
        "routing_mode": "context_aware",
        "context_weight": 0.9,
        "custom_rules": [
            {
                "condition": {
                    "type": "contains",
                    "value": "weather"
                },
                "action": {
                    "type": "route_to",
                    "specialist": "apollo-ci"
                },
                "priority": 10,
                "description": "Route weather queries to Apollo"
            },
            {
                "condition": {
                    "type": "capability_required",
                    "value": "data_analysis"
                },
                "action": {
                    "type": "prefer",
                    "specialists": ["athena-ci", "minerva-ci"]
                },
                "priority": 5
            }
        ]
    }
    
    result = await mcp.configure_orchestration(config)
    print(f"Success: {result.get('success')}")
    
    # Test 3: Invalid routing mode
    print("\n3. Testing invalid routing mode...")
    config = {
        "routing_mode": "invalid_mode"
    }
    
    result = await mcp.configure_orchestration(config)
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")


async def test_send_message_stream():
    """Test streaming message sending."""
    print("\n\n=== Testing send_message_to_specialist_stream ===")
    
    mcp = MCPToolsIntegrationUnified()
    
    print("\n1. Testing streaming from apollo-ci...")
    
    chunk_count = 0
    content_buffer = []
    
    try:
        async for chunk in mcp.send_message_to_specialist_stream(
            specialist_id="apollo-ci",
            message="Tell me a short fact about the sun.",
            timeout=10.0
        ):
            chunk_count += 1
            
            if chunk['type'] == 'chunk':
                content_buffer.append(chunk.get('content', ''))
                # Show progress
                if chunk_count % 5 == 0:
                    print(f"  Received {chunk_count} chunks...")
            
            elif chunk['type'] == 'complete':
                print(f"\nStream completed!")
                print(f"  Total chunks: {chunk_count}")
                print(f"  Specialist: {chunk.get('specialist_id')}")
                if 'metadata' in chunk:
                    print(f"  Total tokens: {chunk['metadata'].get('total_tokens', 'unknown')}")
            
            elif chunk['type'] == 'error':
                print(f"\nError: {chunk.get('error')}")
                break
        
        if content_buffer:
            full_response = ''.join(content_buffer)
            print(f"\nFull response ({len(full_response)} chars):")
            print(f"{full_response[:200]}..." if len(full_response) > 200 else full_response)
    
    except Exception as e:
        print(f"Streaming error: {e}")
    
    # Test 2: Test with non-existent specialist
    print("\n\n2. Testing with non-existent specialist...")
    
    async for chunk in mcp.send_message_to_specialist_stream(
        specialist_id="non-existent-ci",
        message="Hello"
    ):
        if chunk['type'] == 'error':
            print(f"Expected error: {chunk.get('error')}")
        break


async def test_live_mcp_integration():
    """Test MCP methods with live system."""
    print("\n\n=== Testing Live MCP Integration ===")
    
    mcp = MCPToolsIntegrationUnified()
    
    # First, check if we can list specialists
    print("\n1. Listing available specialists...")
    specialists = await mcp.list_specialists()
    print(f"Found {len(specialists)} specialists")
    
    if specialists:
        # Show first few
        for i, spec in enumerate(specialists[:3]):
            print(f"  - {spec['id']}: {spec.get('name', 'Unknown')} "
                  f"(port {spec.get('connection', {}).get('port', 'N/A')})")
    
    # Test team orchestration
    print("\n2. Testing team orchestration...")
    result = await mcp.orchestrate_team_chat(
        topic="The future of AI",
        specialists=[],  # Use all available
        initial_prompt="What's one exciting possibility for AI in the next 5 years?",
        max_rounds=1,
        orchestration_style="collaborative",
        timeout=5.0
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Response count: {result.get('response_count')}")
    print(f"Error count: {result.get('error_count')}")
    
    if result['success'] and result.get('responses'):
        print("\nSample responses:")
        for ai_id, response in list(result['responses'].items())[:3]:
            content = response.get('response', '')
            print(f"\n{ai_id}:")
            print(f"  {content[:150]}..." if len(content) > 150 else f"  {content}")


async def main():
    """Run all tests."""
    print("MCP Methods Test Suite")
    print("=" * 50)
    
    # Test individual methods
    await test_get_specialist_conversation_history()
    await test_configure_orchestration()
    await test_send_message_stream()
    
    # Test live integration
    await test_live_mcp_integration()
    
    print("\n\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())