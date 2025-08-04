#!/usr/bin/env python3
"""Debug echo tool with detailed logging."""

import sys
import json
import time
import select
import os
import signal

# Log file for debugging
log_file = "/tmp/echo_tool_debug.log"

def log(msg):
    """Log to file with timestamp."""
    with open(log_file, 'a') as f:
        f.write(f"{time.time():.6f}: {msg}\n")
        f.flush()

def signal_handler(signum, frame):
    """Log any signals received."""
    log(f"SIGNAL RECEIVED: {signum} ({signal.Signals(signum).name})")
    if signum in (signal.SIGTERM, signal.SIGINT):
        log("Exiting due to termination signal")
        sys.exit(0)

# Set up signal handlers for all catchable signals
for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGPIPE]:
    signal.signal(sig, signal_handler)

log(f"=== ECHO TOOL STARTING ===")
log(f"PID: {os.getpid()}")
log(f"Python: {sys.version}")
log(f"Platform: {sys.platform}")

# Check stdin status
log(f"stdin: {sys.stdin}")
log(f"stdin.isatty(): {sys.stdin.isatty()}")
log(f"stdin.fileno(): {sys.stdin.fileno()}")
try:
    log(f"stdin.closed: {sys.stdin.closed}")
except:
    log("stdin.closed: (attribute not available)")

# Send startup message
startup = {
    'type': 'status',
    'content': 'Echo tool started (debug mode)',
    'timestamp': time.time()
}
log(f"Sending startup message: {startup}")
print(json.dumps(startup))
sys.stdout.flush()
log("Startup message sent")

loop_count = 0
# Main loop
while True:
    loop_count += 1
    if loop_count % 100 == 0:  # Log every 100 iterations
        log(f"Loop iteration {loop_count}, still running...")
    
    try:
        # Check if stdin has data available
        readable, _, _ = select.select([sys.stdin], [], [], 0.1)
        
        if readable:
            log(f"select() says stdin is readable")
            
            try:
                line = sys.stdin.readline()
                log(f"readline() returned: {repr(line)} (type: {type(line)}, len: {len(line)})")
                
                if line == '':  # EOF
                    log("RECEIVED EOF (empty string from readline)")
                    log("Breaking from main loop due to EOF")
                    break
                elif line.strip() == '':  # Empty line (just newline)
                    log(f"Received empty line (just newline), ignoring")
                    continue
                elif line:
                    log(f"Processing input: {repr(line)}")
                    # Process the input
                    try:
                        data = json.loads(line)
                        response = {
                            'type': 'response',
                            'content': f"Echo: {data.get('message', data.get('content', str(data)))}",
                            'timestamp': time.time()
                        }
                        log(f"Parsed JSON, sending response: {response}")
                    except json.JSONDecodeError as e:
                        log(f"JSON decode error: {e}")
                        response = {
                            'type': 'response', 
                            'content': f"Echo: {line.strip()}",
                            'timestamp': time.time()
                        }
                        log(f"Sending plain text response: {response}")
                    
                    print(json.dumps(response))
                    sys.stdout.flush()
                    log("Response sent")
                    
            except Exception as e:
                log(f"Exception reading stdin: {type(e).__name__}: {e}")
                error = {'type': 'error', 'message': str(e)}
                print(json.dumps(error))
                sys.stdout.flush()
                
    except Exception as e:
        log(f"Exception in main loop: {type(e).__name__}: {e}")
    
    # Small sleep to prevent CPU spinning
    time.sleep(0.01)

log("=== ECHO TOOL EXITING ===")
log("Main loop ended, exiting normally")