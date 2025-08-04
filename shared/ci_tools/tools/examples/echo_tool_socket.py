#!/usr/bin/env python3
"""Echo tool that communicates via socket, not stdin/stdout."""

import sys
import json
import time
import os
import signal
import socket
import threading

# Log file for debugging
log_file = "/tmp/echo_tool_socket.log"

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
    
    log(f"Echo tool (socket mode) starting, PID: {os.getpid()}")
    
    # Get port from environment
    port = int(os.environ.get('TEKTON_CI_PORT', '0'))
    if port == 0:
        log("Error: No port specified in TEKTON_CI_PORT")
        sys.exit(1)
    
    log(f"Connecting to port {port}")
    
    # Connect to socket bridge
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', port))
        log(f"Connected to socket bridge on port {port}")
    except Exception as e:
        log(f"Failed to connect: {e}")
        sys.exit(1)
    
    # Send startup message
    startup = {
        'type': 'status',
        'content': 'Echo tool started (socket mode)',
        'timestamp': time.time()
    }
    sock.sendall((json.dumps(startup) + '\n').encode())
    log("Sent startup message")
    
    # Main loop - receive and echo messages
    buffer = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                log("Socket closed")
                break
            
            buffer += data.decode()
            
            # Process complete messages
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    log(f"Received: {repr(line)}")
                    
                    try:
                        msg = json.loads(line)
                        response = {
                            'type': 'response',
                            'content': f"Echo: {msg.get('message', msg.get('content', str(msg)))}",
                            'timestamp': time.time()
                        }
                    except json.JSONDecodeError:
                        response = {
                            'type': 'response',
                            'content': f"Echo: {line}",
                            'timestamp': time.time()
                        }
                    
                    sock.sendall((json.dumps(response) + '\n').encode())
                    log(f"Sent response: {response}")
                    
        except KeyboardInterrupt:
            log("KeyboardInterrupt")
            break
        except Exception as e:
            log(f"Error: {e}")
            error = {'type': 'error', 'message': str(e)}
            try:
                sock.sendall((json.dumps(error) + '\n').encode())
            except:
                pass
    
    log("Echo tool exiting")
    sock.close()

if __name__ == '__main__':
    main()