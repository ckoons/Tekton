#!/usr/bin/env python3
"""
Test script for aish MCP server endpoints

Usage:
    python test_mcp.py              # Run all tests
    python test_mcp.py capabilities  # Test specific endpoint
"""

import sys
import requests
import json
import time
import os
from pathlib import Path

# Add TEKTON_ROOT to path
sys.path.insert(0, TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Coder-A'))
from shared.env import TektonEnviron, TektonEnvironLock
# Load environment to get correct port
TektonEnvironLock.load()

# Get MCP port
MCP_PORT = int(TektonEnviron.get("AISH_MCP_PORT", "3100"))
BASE_URL = f"http://localhost:{MCP_PORT}/api/mcp/v2"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_capabilities():
    """Test capabilities discovery"""
    print("\n=== Testing Capabilities Endpoint ===")
    try:
        resp = requests.get(f"{BASE_URL}/capabilities")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Server: {data.get('server_name')}")
        print(f"Version: {data.get('mcp_version')}")
        print(f"Tools: {len(data.get('capabilities', {}).get('tools', {}))}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_ais():
    """Test list CIs endpoint"""
    print("\n=== Testing List CIs ===")
    try:
        resp = requests.post(f"{BASE_URL}/tools/list-ais", json={})
        print(f"Status: {resp.status_code}")
        data = resp.json()
        ais = data.get('ais', [])
        print(f"Found {len(ais)} CIs:")
        for ai in ais[:5]:  # Show first 5
            print(f"  - {ai['name']} ({ai['status']})")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_send_message():
    """Test sending message to AI"""
    print("\n=== Testing Send Message (non-streaming) ===")
    try:
        payload = {
            "ai_name": "numa",
            "message": "Hello from MCP test",
            "stream": False
        }
        resp = requests.post(f"{BASE_URL}/tools/send-message", json=payload)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"Error: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_send_message_streaming():
    """Test streaming message to AI"""
    print("\n=== Testing Send Message (streaming) ===")
    try:
        payload = {
            "ai_name": "numa",
            "message": "Hello from MCP streaming test",
            "stream": True
        }
        resp = requests.post(f"{BASE_URL}/tools/send-message", json=payload, stream=True)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Streaming response:")
            for line in resp.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data = json.loads(line_str[6:])
                        if data.get('chunk'):
                            print(f"  Chunk: {data['chunk'][:50]}...")
                        if data.get('done'):
                            print("  Stream complete")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_forwarding():
    """Test forwarding management"""
    print("\n=== Testing Forwarding ===")
    try:
        # List current forwards
        resp = requests.post(f"{BASE_URL}/tools/forward", json={"action": "list"})
        print(f"List forwards - Status: {resp.status_code}")
        if resp.status_code == 200:
            forwards = resp.json().get('forwards', [])
            print(f"Current forwards: {forwards}")
        
        # Add a forward
        resp = requests.post(f"{BASE_URL}/tools/forward", json={
            "action": "add",
            "ai_name": "test-ai",
            "terminal": "test-terminal"
        })
        print(f"\nAdd forward - Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Message: {resp.json().get('message')}")
        
        # Remove the forward
        resp = requests.post(f"{BASE_URL}/tools/forward", json={
            "action": "remove",
            "ai_name": "test-ai"
        })
        print(f"\nRemove forward - Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Message: {resp.json().get('message')}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_terma_inbox():
    """Test terminal inbox"""
    print("\n=== Testing Terminal Inbox ===")
    try:
        resp = requests.get(f"{BASE_URL}/tools/terma-inbox")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Prompt messages: {len(data.get('prompt', []))}")
            print(f"New messages: {len(data.get('new', []))}")
            print(f"Keep messages: {len(data.get('keep', []))}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_purpose():
    """Test purpose management"""
    print("\n=== Testing Purpose ===")
    try:
        # Get current purpose
        resp = requests.post(f"{BASE_URL}/tools/purpose", json={})
        print(f"Get purpose - Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Current purpose: {data.get('purpose', 'none')}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests or specific test"""
    print(f"Testing aish MCP server on port {MCP_PORT}")
    print(f"Base URL: {BASE_URL}")
    
    # Give server a moment to start if just launched
    time.sleep(1)
    
    # Check if server is running
    try:
        requests.get(f"http://localhost:{MCP_PORT}/", timeout=2)
    except:
        print(f"\nERROR: Cannot connect to MCP server on port {MCP_PORT}")
        print("Make sure aish MCP server is running:")
        print("  1. Export AISH_MCP_PORT=3100 (or your preferred port)")
        print("  2. Run: aish list  (this will start the MCP server)")
        print("  3. In another terminal, run this test")
        return 1
    
    if len(sys.argv) > 1:
        # Test specific endpoint
        test_name = sys.argv[1]
        test_func = globals().get(f"test_{test_name}")
        if test_func:
            success = test_func()
            return 0 if success else 1
        else:
            print(f"Unknown test: {test_name}")
            return 1
    
    # Run all tests
    tests = [
        test_health,
        test_capabilities,
        test_list_ais,
        test_send_message,
        test_send_message_streaming,
        test_forwarding,
        test_terma_inbox,
        test_purpose
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\nTest {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())