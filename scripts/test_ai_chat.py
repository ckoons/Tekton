#!/usr/bin/env python3
"""
Test Multi-AI Chat Functionality

Tests the AI specialists' ability to respond to chat messages via their socket interface.
"""
import asyncio
import json
import sys
import os
from typing import Dict, Any, Optional

# Add Tekton root to path
sys.path.insert(0, os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'))

from shared.ai.registry_client import AIRegistryClient


async def send_ai_message(ai_id: str, message: str) -> Optional[Dict[str, Any]]:
    """Send a chat message to an AI specialist and get response."""
    registry_client = AIRegistryClient()
    
    # Get AI socket info
    socket_info = registry_client.get_ai_socket(ai_id)
    if not socket_info:
        print(f"✗ {ai_id} not found in registry")
        return None
    
    host, port = socket_info
    
    try:
        # Connect to AI
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=5.0
        )
        
        # Send chat message
        chat_msg = {
            'type': 'chat',
            'content': message
        }
        
        writer.write(json.dumps(chat_msg).encode() + b'\n')
        await writer.drain()
        
        # Read response
        response_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        response = json.loads(response_data.decode())
        
        writer.close()
        await writer.wait_closed()
        
        return response
        
    except asyncio.TimeoutError:
        print(f"✗ {ai_id} timeout")
        return None
    except Exception as e:
        print(f"✗ {ai_id} error: {e}")
        return None


async def test_all_ais():
    """Test all registered AIs with sample messages."""
    registry_client = AIRegistryClient()
    ai_registry = registry_client.list_platform_ais()
    
    if not ai_registry:
        print("No AIs registered!")
        return
    
    print(f"Testing {len(ai_registry)} AI specialists...\n")
    
    # Test messages for different components
    test_messages = {
        'hermes-ai': "What is your role in service orchestration?",
        'engram-ai': "How do you manage memory storage?",
        'rhetor-ai': "What makes a good prompt?",
        'athena-ai': "How do you build knowledge graphs?",
        'prometheus-ai': "What's important in project planning?",
        'numa-ai': "How do you coordinate other AIs?",
        'ergon-ai': "How do you manage agents?",
        'default': "What is your primary expertise?"
    }
    
    # Test each AI
    results = []
    for ai_id in sorted(ai_registry.keys()):
        ai_info = ai_registry[ai_id]
        component = ai_info['component']
        
        # Get appropriate test message
        message = test_messages.get(ai_id, test_messages['default'])
        
        print(f"Testing {ai_id} ({component})...")
        print(f"  Message: {message}")
        
        # Send message and get response
        response = await send_ai_message(ai_id, message)
        
        if response:
            if response.get('type') == 'chat_response':
                content = response.get('content', 'No content')
                # Truncate long responses
                if len(content) > 200:
                    content = content[:197] + "..."
                print(f"  ✓ Response: {content}")
                results.append((ai_id, True, "Success"))
            else:
                print(f"  ✗ Unexpected response type: {response.get('type')}")
                results.append((ai_id, False, f"Wrong type: {response.get('type')}"))
        else:
            results.append((ai_id, False, "No response"))
        
        print()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(1 for _, success, _ in results if success)
    print(f"Total AIs tested: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    if len(results) - success_count > 0:
        print("\nFailed AIs:")
        for ai_id, success, reason in results:
            if not success:
                print(f"  - {ai_id}: {reason}")


async def test_specific_ai(ai_id: str, message: str):
    """Test a specific AI with a custom message."""
    print(f"Testing {ai_id}...")
    print(f"Message: {message}")
    
    response = await send_ai_message(ai_id, message)
    
    if response:
        print(f"\nResponse type: {response.get('type')}")
        print(f"Response content: {response.get('content', 'No content')}")
    else:
        print("\nNo response received")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Tekton AI specialists')
    parser.add_argument('--ai', help='Test specific AI (e.g., hermes-ai)')
    parser.add_argument('--message', help='Custom message to send')
    parser.add_argument('--all', action='store_true', help='Test all registered AIs')
    
    args = parser.parse_args()
    
    if args.ai and args.message:
        await test_specific_ai(args.ai, args.message)
    elif args.all or (not args.ai and not args.message):
        await test_all_ais()
    else:
        parser.error("Use --all to test all AIs, or --ai and --message for specific test")


if __name__ == '__main__':
    asyncio.run(main())