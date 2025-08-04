#!/usr/bin/env python3
"""Simple echo tool for testing CI tools integration."""

import sys
import json
import time
import os
import signal

# Log file for debugging
log_file = "/tmp/echo_tool.log"

def log(msg):
    """Log to file for debugging."""
    with open(log_file, 'a') as f:
        f.write(f"{time.time()}: {msg}\n")
        f.flush()

def handle_signal(signum, frame):
    """Handle termination signals."""
    log(f"Received signal {signum}")
    sys.exit(0)

def main():
    # Set up signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    log(f"Echo tool starting, PID: {os.getpid()}")
    
    # Send startup message
    startup = {
        'type': 'status',
        'content': 'Echo tool started',
        'timestamp': time.time()
    }
    print(json.dumps(startup))
    sys.stdout.flush()
    log("Sent startup message")
    
    while True:
        try:
            log("Waiting for input...")
            line = sys.stdin.readline()
            log(f"Received: {repr(line)}")
            
            if not line:
                log("EOF received, exiting")
                break
                
            # Try to parse as JSON
            try:
                data = json.loads(line)
                response = {
                    'type': 'response',
                    'content': f"Echo: {data.get('message', data.get('content', str(data)))}",
                    'timestamp': time.time()
                }
                log(f"Sending JSON response: {response}")
            except json.JSONDecodeError:
                # Plain text
                response = {
                    'type': 'response', 
                    'content': f"Echo: {line.strip()}",
                    'timestamp': time.time()
                }
                log(f"Sending text response: {response}")
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            log("KeyboardInterrupt received")
            break
        except Exception as e:
            log(f"Error: {e}")
            error = {'type': 'error', 'message': str(e)}
            print(json.dumps(error))
            sys.stdout.flush()
    
    log("Echo tool exiting")

if __name__ == '__main__':
    main()