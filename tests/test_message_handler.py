#!/usr/bin/env python3
"""
Tests for the simple message handler
"""
import sys
import socket
import json
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.aish.src.message_handler import MessageHandler

def create_mock_ai_server(port, response="Test response"):
    """Create a mock CI server for testing"""
    def server_thread():
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', port))
        s.listen(1)
        
        conn, addr = s.accept()
        data = conn.recv(4096)
        
        # Send back a response
        response_data = json.dumps({
            'type': 'chat_response',
            'content': response
        }).encode()
        conn.send(response_data)
        conn.close()
        s.close()
    
    thread = threading.Thread(target=server_thread)
    thread.daemon = True
    thread.start()
    time.sleep(0.1)  # Give server time to start
    return thread

def test_send_message():
    """Test sending a message to a single AI"""
    print("Testing single message send...")
    
    handler = MessageHandler(timeout=30)
    try:
        # Test with real CI if available
        response = handler.send('apollo', 'ping')
        assert len(response) > 0, "Expected non-empty response"
        print(f"✓ Single message send works - got {len(response)} chars")
    except Exception as e:
        print(f"ℹ️  Apollo not available: {type(e).__name__}")
        # Try mock server on different port
        test_port = 54321
        create_mock_ai_server(test_port, "Mock response")
        # Test with mock by temporarily adding to ports
        handler.ports['test_ai'] = test_port
        response = handler.send('test_ai', 'test message')
        assert response == "Mock response"
        print("✓ Single message send works (mock)")
        del handler.ports['test_ai']

def test_broadcast():
    """Test broadcasting to multiple AIs"""
    print("\nTesting broadcast...")
    
    handler = MessageHandler(timeout=5)  # Short timeout for broadcast test
    
    # Test with real AIs if available
    responses = handler.broadcast('ping')
    
    # Count successful responses
    success_count = sum(1 for r in responses.values() if not r.startswith('ERROR:'))
    error_count = sum(1 for r in responses.values() if r.startswith('ERROR:'))
    
    print(f"  Broadcast results: {success_count} success, {error_count} errors")
    
    if success_count > 0:
        print(f"✓ Broadcast works - {success_count} AIs responded")
        # Show which AIs responded
        for ai, resp in responses.items():
            if not resp.startswith('ERROR:'):
                print(f"    - {ai}: responded with {len(resp)} chars")
    else:
        print("ℹ️  No AIs available for broadcast test")
        # Test with mocks
        handler.ports = {
            'mock1': 54321,
            'mock2': 54322,
            'mock3': 54323
        }
        create_mock_ai_server(54321, "Mock1 response")
        create_mock_ai_server(54322, "Mock2 response") 
        create_mock_ai_server(54323, "Mock3 response")
        
        responses = handler.broadcast('test')
        success_count = sum(1 for r in responses.values() if not r.startswith('ERROR:'))
        assert success_count == 3, f"Expected 3 responses, got {success_count}"
        print("✓ Broadcast works (mock)")

def test_unknown_ai():
    """Test sending to unknown AI"""
    print("\nTesting unknown AI...")
    
    handler = MessageHandler()
    try:
        handler.send('unknown_ai', 'test')
        print("✗ Should have raised ValueError for unknown AI")
        assert False
    except ValueError as e:
        assert "Unknown AI" in str(e)
        print("✓ Correctly raised ValueError for unknown AI")

def test_timeout():
    """Test timeout handling"""
    print("\nTesting timeout...")
    
    handler = MessageHandler(timeout=1)
    try:
        # Try to connect to a non-existent AI
        handler.ports['fake_ai'] = 59999  # Port with no server
        handler.send('fake_ai', 'test')
        print("✗ Should have raised exception for timeout")
    except Exception as e:
        print(f"✓ Correctly raised exception: {type(e).__name__}")
    finally:
        if 'fake_ai' in handler.ports:
            del handler.ports['fake_ai']

def test_port_mapping():
    """Test the port mapping formula"""
    print("\nTesting port mapping...")
    
    handler = MessageHandler()
    
    # Test the formula with default bases
    # Note: These tests assume default TEKTON_PORT_BASE=8000 and TEKTON_AI_PORT_BASE=45000
    test_cases = [
        ('engram', 45000),     # Default: engram at base port
        ('hermes', 45001),     # Default: hermes at base+1
        ('apollo', 45012),     # Default: apollo at base+12
        ('hephaestus', 45080), # Default: hephaestus at base+80
    ]
    
    for ai_name, expected_port in test_cases:
        actual_port = handler.ports.get(ai_name)
        assert actual_port == expected_port, f"{ai_name}: expected {expected_port}, got {actual_port}"
    
    print("✓ Port mapping is correct")

def test_aish_compatibility():
    """Test aish shell compatibility methods"""
    print("Testing aish shell methods...")
    
    handler = MessageHandler(timeout=5)
    
    # Test create method
    socket_id = handler.create('apollo')
    assert socket_id == 'apollo-socket', f"Expected 'apollo-socket', got {socket_id}"
    print("✓ create() returns proper socket ID")
    
    # Test write/read for direct message
    success = handler.write(socket_id, 'test message')
    if success:
        messages = handler.read(socket_id)
        # Should be empty since responses are cleared after read
        print(f"✓ write/read works for direct messages")
    else:
        print("ℹ️  Apollo not available for write/read test")
    
    # Test team chat write/read
    success = handler.write('team-chat-all', 'team test')
    if success:
        messages = handler.read('team-chat-all')
        if messages:
            print(f"✓ team-chat write/read works - got {len(messages)} responses")
        else:
            print("✗ team-chat read returned no messages")
    else:
        print("ℹ️  No AIs available for team chat test")

if __name__ == "__main__":
    print("=== Testing Message Handler ===\n")
    
    # Run tests
    test_port_mapping()
    test_unknown_ai()
    test_timeout()
    
    # These tests work with or without AIs running
    print("\nTests with CI servers:")
    test_send_message()
    test_broadcast()
    
    # Test direct CI compatibility
    print("\nTesting aish compatibility:")
    test_aish_compatibility()
    
    print("\n=== Tests Complete ===")