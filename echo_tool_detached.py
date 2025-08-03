#!/usr/bin/env python3
"""Echo tool that can run in detached mode without stdin."""

import sys
import json
import time
import signal
import socket
import threading
import os

running = True
port = int(os.environ.get('TEKTON_CI_PORT', '0'))

def signal_handler(signum, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def socket_listener():
    """Listen on socket for messages when stdin is not available."""
    global running
    
    if port == 0:
        return
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', port))
        server.listen(5)
        server.settimeout(1.0)  # Non-blocking with timeout
        
        print(json.dumps({
            'type': 'status',
            'content': f'Echo tool listening on port {port}',
            'timestamp': time.time()
        }))
        sys.stdout.flush()
        
        while running:
            try:
                client, addr = server.accept()
                # Handle client in same thread for simplicity
                data = client.recv(4096).decode('utf-8')
                if data:
                    # Process message
                    try:
                        msg = json.loads(data)
                        response = {
                            'type': 'response',
                            'content': f"Echo: {msg.get('message', str(msg))}",
                            'timestamp': time.time()
                        }
                    except json.JSONDecodeError:
                        response = {
                            'type': 'response',
                            'content': f"Echo: {data}",
                            'timestamp': time.time()
                        }
                    
                    client.send(json.dumps(response).encode('utf-8'))
                client.close()
            except socket.timeout:
                continue
            except Exception as e:
                if running:
                    print(json.dumps({
                        'type': 'error',
                        'message': f'Socket error: {str(e)}',
                        'timestamp': time.time()
                    }))
                    sys.stdout.flush()
        
        server.close()
    except Exception as e:
        print(json.dumps({
            'type': 'error',
            'message': f'Failed to start socket listener: {str(e)}',
            'timestamp': time.time()
        }))
        sys.stdout.flush()

# Send startup message
print(json.dumps({
    'type': 'status',
    'content': 'Echo tool started',
    'timestamp': time.time()
}))
sys.stdout.flush()

# Check if stdin is available
stdin_available = True
try:
    # Try to check if stdin is a terminal or pipe
    if not sys.stdin.isatty():
        # Not a terminal, might be a pipe or file
        # Check if we can select on it
        import select
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if not r:
            # No data immediately available, might be closed
            stdin_available = False
except:
    stdin_available = False

if not stdin_available or port > 0:
    # Run in socket mode
    print(json.dumps({
        'type': 'status',
        'content': 'Running in socket mode (no stdin)',
        'timestamp': time.time()
    }))
    sys.stdout.flush()
    
    # Start socket listener
    socket_listener()
else:
    # Run in stdin mode
    print(json.dumps({
        'type': 'status',
        'content': 'Running in stdin mode',
        'timestamp': time.time()
    }))
    sys.stdout.flush()
    
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