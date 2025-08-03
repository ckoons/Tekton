#!/usr/bin/env python3
"""Simple echo tool that stays running."""

import sys
import json
import time
import select

# Send startup message
startup = {
    'type': 'status',
    'content': 'Echo tool started',
    'timestamp': time.time()
}
print(json.dumps(startup))
sys.stdout.flush()

# Main loop - use select to check for input without blocking
while True:
    # Check if stdin has data available
    if sys.platform == 'win32':
        # Windows doesn't support select on stdin
        time.sleep(0.1)
    else:
        # Unix/Linux/Mac
        readable, _, _ = select.select([sys.stdin], [], [], 0.1)
        if readable:
            try:
                line = sys.stdin.readline()
                if line:
                    # Process the input
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
                            'content': f"Echo: {line.strip()}",
                            'timestamp': time.time()
                        }
                    
                    print(json.dumps(response))
                    sys.stdout.flush()
            except Exception as e:
                error = {'type': 'error', 'message': str(e)}
                print(json.dumps(error))
                sys.stdout.flush()
    
    # Small sleep to prevent CPU spinning
    time.sleep(0.01)