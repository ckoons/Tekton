#!/usr/bin/env python3
"""
Test script for chat command processing
Demonstrates the full flow of bracket commands
"""

import asyncio
import sys
from pathlib import Path

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent))

from shared.aish.src.handlers.chat_command_handler import handle_chat_command
from shared.aish.src.registry.ci_registry import get_registry
from shared.ai.claude_handler import get_claude_handler


async def test_commands():
    """Test various chat commands"""
    
    print("=" * 60)
    print("CHAT COMMAND SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: aish command
    print("\n1. Testing [aish status] command:")
    result = await handle_chat_command('aish', 'status', {'component': 'test'})
    print(f"   Result: {result['output'][:100]}...")
    
    # Test 2: Shell command
    print("\n2. Testing [ls] command:")
    result = await handle_chat_command('shell', 'ls -la | head -5', {'component': 'test'})
    print(f"   Result: {result['output'][:200]}...")
    
    # Test 3: Forward command
    print("\n3. Testing forward to Claude:")
    registry = get_registry()
    
    # Set forward state
    registry.set_forward_state('test-ci', 'claude', 'claude --print')
    print("   Forward set: test-ci → claude")
    
    # Check forward state
    state = registry.get_forward_state('test-ci')
    print(f"   State: {state}")
    
    # Test 4: Check if Claude is available
    print("\n4. Checking Claude availability:")
    handler = get_claude_handler()
    available = await handler.check_claude_available()
    print(f"   Claude CLI available: {available}")
    
    if available:
        print("\n5. Testing Claude execution:")
        response = await handler.execute_claude(
            'claude --print', 
            'Say "Hello from Tekton" in exactly 5 words',
            'test-ci'
        )
        print(f"   Claude response: {response}")
    
    # Test 5: List all forwards
    print("\n6. Listing all forward states:")
    forwards = registry.list_forward_states()
    for ci_name, state in forwards.items():
        print(f"   {ci_name} → {state['model']}")
    
    # Clean up
    registry.clear_forward_state('test-ci')
    print("\n7. Cleared forward state for test-ci")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


async def test_full_flow():
    """Test the full chat flow with parsing"""
    print("\n" + "=" * 60)
    print("FULL CHAT FLOW TEST")
    print("=" * 60)
    
    # Simulate what happens when user types in chat
    test_messages = [
        "[aish status] Show me the system status",
        "[ls -la] What files are here?",
        "[claude] Explain quantum computing in one sentence",
        "Normal message without commands"
    ]
    
    for msg in test_messages:
        print(f"\nInput: {msg}")
        
        # This would normally go through ChatCommandParser.parse()
        # Then ChatCore.processChatInput()
        # Then execute commands
        
        # Extract command (simplified)
        if msg.startswith('['):
            end = msg.index(']')
            command = msg[1:end]
            remaining = msg[end+1:].strip()
            
            print(f"   Command: {command}")
            print(f"   Message: {remaining}")
            
            # Determine command type
            if command.startswith('aish '):
                cmd_type = 'aish'
                cmd = command[5:]
            elif command in ['ls', 'pwd', 'date'] or command.startswith('ls '):
                cmd_type = 'shell'
                cmd = command
            elif command.startswith('claude'):
                cmd_type = 'escalate'
                cmd = command
            else:
                cmd_type = 'unknown'
                cmd = command
            
            print(f"   Type: {cmd_type}")
        else:
            print("   No command, normal message")


if __name__ == "__main__":
    print("Testing Tekton Chat Command System\n")
    
    # Run tests
    asyncio.run(test_commands())
    asyncio.run(test_full_flow())
    
    print("\nTo test in Hephaestus UI:")
    print("1. Refresh the UI (Cmd+Shift+R)")
    print("2. Open browser console")
    print("3. Try these in any chat:")
    print("   [aish status]")
    print("   [ls -la]")
    print("   [claude] Hello")
    print("\nCommands will be intercepted by ChatCore")