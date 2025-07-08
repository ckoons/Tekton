#!/usr/bin/env python3
"""
Test inbox functionality directly
"""

import json
import os
import time
from pathlib import Path
from collections import deque

# Test the inbox operations
def test_inbox():
    print("Testing inbox operations...")
    print("==========================")
    
    # Setup test data
    tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    inbox_dir = Path(tekton_root) / '.tekton' / 'terma'
    inbox_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test inbox
    test_inbox = {
        'new': [
            {
                'id': 1,
                'timestamp': '2025-01-04T14:00:00',
                'from': 'TestSender',
                'message': 'Test message 1',
                'routing': 'direct'
            },
            {
                'id': 2,
                'timestamp': '2025-01-04T14:01:00',
                'from': 'TestSender',
                'message': 'Test message 2',
                'routing': 'direct'
            }
        ],
        'keep': [],
        'session_id': 'test-session',
        'timestamp': '2025-01-04T14:00:00'
    }
    
    # Write test inbox
    snapshot_file = inbox_dir / '.inbox_snapshot'
    with open(snapshot_file, 'w') as f:
        json.dump(test_inbox, f, indent=2)
    
    print("✓ Created test inbox with 2 messages")
    
    # Test 1: Pop command
    print("\nTest 1: Testing pop command")
    cmd_dir = inbox_dir / 'commands'
    cmd_dir.mkdir(exist_ok=True)
    
    pop_cmd = {
        'action': 'pop',
        'timestamp': time.time()
    }
    cmd_file = cmd_dir / f'test_pop_{int(time.time()*1000)}.json'
    with open(cmd_file, 'w') as f:
        json.dump(pop_cmd, f)
    
    print(f"✓ Created pop command: {cmd_file.name}")
    
    # Simulate processing
    from aish_proxy import process_inbox_commands, message_inbox
    
    # Initialize the in-memory inbox
    message_inbox['new'] = deque(test_inbox['new'])
    message_inbox['keep'] = deque(test_inbox['keep'])
    
    print(f"Before: {len(message_inbox['new'])} new messages")
    
    # Process commands
    process_inbox_commands()
    
    print(f"After: {len(message_inbox['new'])} new messages")
    
    # Verify
    if len(message_inbox['new']) == 1:
        print("✅ Pop worked - removed 1 message")
    else:
        print("❌ Pop failed - message count unchanged")
    
    # Test 2: Keep push
    print("\nTest 2: Testing keep push")
    push_cmd = {
        'action': 'keep_push',
        'message': 'Important note',
        'timestamp': time.time()
    }
    cmd_file = cmd_dir / f'test_push_{int(time.time()*1000)}.json'
    with open(cmd_file, 'w') as f:
        json.dump(push_cmd, f)
    
    print(f"Before: {len(message_inbox['keep'])} keep messages")
    
    process_inbox_commands()
    
    print(f"After: {len(message_inbox['keep'])} keep messages")
    
    if len(message_inbox['keep']) == 1:
        print("✅ Push worked - added 1 message")
    else:
        print("❌ Push failed - keep unchanged")
    
    # Check snapshot was updated
    with open(snapshot_file, 'r') as f:
        updated = json.load(f)
    
    print(f"\nSnapshot has {len(updated['new'])} new, {len(updated['keep'])} keep messages")
    
    # Cleanup
    for f in cmd_dir.glob('test_*.json'):
        f.unlink()
    
    print("\n✓ Test complete!")

if __name__ == '__main__':
    # Add aish-proxy to path
    import sys
    sys.path.insert(0, '/Users/cskoons/projects/github/Tekton/shared/aish')
    
    test_inbox()