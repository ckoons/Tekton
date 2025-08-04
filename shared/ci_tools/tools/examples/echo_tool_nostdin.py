#!/usr/bin/env python3
"""Echo tool that doesn't use stdin - just stays alive."""

import sys
import json
import time
import signal
import threading

running = True

def signal_handler(signum, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Send startup message
startup = {
    'type': 'status',
    'content': 'Echo tool started (no stdin mode)',
    'timestamp': time.time()
}
print(json.dumps(startup))
sys.stdout.flush()

# Just stay alive until terminated
counter = 0
while running:
    counter += 1
    if counter % 5 == 0:  # Every 5 seconds
        heartbeat = {
            'type': 'heartbeat',
            'content': f'Still alive after {counter} seconds',
            'timestamp': time.time()
        }
        print(json.dumps(heartbeat))
        sys.stdout.flush()
    time.sleep(1)
    
print(json.dumps({'type': 'status', 'content': 'Echo tool shutting down'}))
sys.stdout.flush()