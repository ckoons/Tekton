#!/usr/bin/env python3
"""Echo tool that properly waits for socket bridge connection."""

import sys
import json
import time
import signal
import os
import socket

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
    'content': 'Echo tool started (socket-aware version)',
    'timestamp': time.time()
}
print(json.dumps(startup))
sys.stdout.flush()

# Check if we have a port - if so, we're in socket mode
port = os.environ.get('TEKTON_CI_PORT')
if port:
    # Socket mode - the C launcher will handle the connection
    # We just need to read/write normally
    sys.stderr.write(f"Running in socket mode on port {port}\n")
    sys.stderr.flush()
    
    # Keep the stdin check simple
    while running:
        try:
            # Non-blocking read with timeout
            import select
            readable, _, _ = select.select([sys.stdin], [], [], 0.1)
            
            if readable:
                line = sys.stdin.readline()
                if not line:  # EOF only when socket closes
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Process the message
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
else:
    # Direct mode - stdin/stdout
    sys.stderr.write("Running in direct mode\n")
    sys.stderr.flush()
    
    while running:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            # Process the message
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