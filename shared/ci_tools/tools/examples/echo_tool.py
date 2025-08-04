#!/usr/bin/env python3
"""Simple echo tool for testing CI tools integration."""

import sys
import json
import time
import os

def main():
    # Log startup to stderr for debugging
    sys.stderr.write(f"Echo tool starting, PID: {os.getpid()}\n")
    sys.stderr.flush()
    # Send startup message
    startup = {
        'type': 'status',
        'content': 'Echo tool started',
        'timestamp': time.time()
    }
    print(json.dumps(startup))
    sys.stdout.flush()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            # Try to parse as JSON
            try:
                data = json.loads(line)
                response = {
                    'type': 'response',
                    'content': f"Echo: {data.get('message', data.get('content', str(data)))}",
                    'timestamp': time.time()
                }
            except json.JSONDecodeError:
                # Plain text
                response = {
                    'type': 'response', 
                    'content': f"Echo: {line.strip()}",
                    'timestamp': time.time()
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            error = {'type': 'error', 'message': str(e)}
            print(json.dumps(error))
            sys.stdout.flush()

if __name__ == '__main__':
    main()