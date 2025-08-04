#!/usr/bin/env python3
"""Echo tool for testing with C launcher - stays alive properly."""

import sys
import json
import time
import signal

running = True

def signal_handler(signum, frame):
    global running
    running = False
    print(json.dumps({
        'type': 'status',
        'content': f'Received signal {signum}, shutting down',
        'timestamp': time.time()
    }))
    sys.stdout.flush()

# Set up signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Send startup message
startup = {
    'type': 'status',
    'content': 'Echo tool started (C launcher version)',
    'timestamp': time.time()
}
print(json.dumps(startup))
sys.stdout.flush()

# Main loop - read from stdin
while running:
    try:
        line = sys.stdin.readline()
        if not line:  # EOF
            break
            
        line = line.strip()
        if not line:  # Empty line
            continue
            
        # Try to parse as JSON
        try:
            data = json.loads(line)
            response = {
                'type': 'response',
                'content': f"Echo: {data.get('message', data.get('content', str(data)))}",
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
        running = False
    except Exception as e:
        error = {'type': 'error', 'message': str(e)}
        print(json.dumps(error))
        sys.stdout.flush()

# Final message
print(json.dumps({
    'type': 'status',
    'content': 'Echo tool exiting normally',
    'timestamp': time.time()
}))
sys.stdout.flush()