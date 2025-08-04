#!/usr/bin/env python3
"""Simple echo tool that works with C launcher."""

import sys
import json
import time
import signal

running = True

def signal_handler(signum, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Send startup message
print(json.dumps({
    'type': 'status',
    'content': 'Echo tool started',
    'timestamp': time.time()
}))
sys.stdout.flush()

# Main loop
while running:
    try:
        # Simple blocking read
        line = sys.stdin.readline()
        if not line:  # EOF
            break
        
        line = line.strip()
        if not line:  # Empty line
            continue
        
        # Process message
        try:
            data = json.loads(line)
            response = {
                'type': 'response',
                'content': f"Echo: {data.get('message', str(data))}",
                'timestamp': time.time()
            }
        except json.JSONDecodeError:
            response = {
                'type': 'response',
                'content': f"Echo: {line}",
                'timestamp': time.time()
            }
        
        print(json.dumps(response))
        sys.stdout.flush()
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(json.dumps({
            'type': 'error',
            'message': str(e),
            'timestamp': time.time()
        }))
        sys.stdout.flush()

# Exit message
print(json.dumps({
    'type': 'status',
    'content': 'Echo tool exiting',
    'timestamp': time.time()
}))
sys.stdout.flush()