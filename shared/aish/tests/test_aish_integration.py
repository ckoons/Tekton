#!/usr/bin/env python3
"""
Integration tests for aish functionality
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path

# Add aish to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_aish(args, input_data=None):
    """Run aish command and return output."""
    cmd = ['./aish'] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=input_data,
        cwd=Path(__file__).parent.parent
    )
    return result.returncode, result.stdout, result.stderr

def test_direct_message_syntax():
    """Test that direct message syntax works."""
    print("Testing direct message syntax...")
    
    # Test 1: Single word message
    code, stdout, stderr = run_aish(['numa', 'hello'])
    assert 'No message provided' not in stderr, f"Single word failed: {stderr}"
    print("✓ Single word message")
    
    # Test 2: Quoted message
    code, stdout, stderr = run_aish(['numa', 'hello world'])
    assert 'No message provided' not in stderr, f"Multi-word failed: {stderr}"
    print("✓ Multi-word message")
    
    # Test 3: Empty message should fail
    code, stdout, stderr = run_aish(['numa'])
    assert code != 0, "Empty message should fail"
    assert 'No message provided' in stderr or 'interactive mode' in stdout
    print("✓ Empty message handling")

def test_pipe_syntax():
    """Test piped input."""
    print("\nTesting pipe syntax...")
    
    code, stdout, stderr = run_aish(['numa'], input_data='hello from pipe')
    assert 'No message provided' not in stderr, f"Pipe failed: {stderr}"
    print("✓ Piped input")

def test_terma_commands():
    """Test terma functionality."""
    print("\nTesting terma commands...")
    
    # Test list
    code, stdout, stderr = run_aish(['terma', 'list'])
    assert code == 0, f"List failed: {stderr}"
    assert 'Active Terminals' in stdout or 'No active terminals' in stdout
    print("✓ Terminal list")
    
    # Test help
    code, stdout, stderr = run_aish(['terma', 'help'])
    assert code == 0, f"Help failed: {stderr}"
    assert 'Usage:' in stdout
    print("✓ Help command")

def test_help_system():
    """Test help functionality."""
    print("\nTesting help system...")
    
    # General help
    code, stdout, stderr = run_aish(['help'])
    assert code == 0, f"Help failed: {stderr}"
    assert 'CI Training:' in stdout
    print("✓ General help")
    
    # Component help
    code, stdout, stderr = run_aish(['numa', 'help'])
    assert code == 0, f"Component help failed: {stderr}"
    assert 'CI Training:' in stdout
    assert 'numa' in stdout
    print("✓ Component help")

def test_inbox_commands():
    """Test inbox functionality (syntax only)."""
    print("\nTesting inbox command syntax...")
    
    # These should not error with "command not found"
    commands = [
        ['terma', 'inbox'],
        ['terma', 'inbox', 'new', 'pop'],
        ['terma', 'inbox', 'keep', 'push', 'test'],
        ['terma', 'inbox', 'keep', 'write', 'test'],
        ['terma', 'inbox', 'keep', 'read']
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_aish(cmd)
        # We don't check success, just that command is recognized
        assert 'Usage:' not in stderr or code == 0, f"Command not recognized: {cmd}"
        print(f"✓ Command recognized: {' '.join(cmd)}")

def run_all_tests():
    """Run all integration tests."""
    print("Running aish integration tests")
    print("==============================\n")
    
    try:
        test_direct_message_syntax()
        test_pipe_syntax()
        test_terma_commands()
        test_help_system()
        test_inbox_commands()
        
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 2

if __name__ == '__main__':
    sys.exit(run_all_tests())