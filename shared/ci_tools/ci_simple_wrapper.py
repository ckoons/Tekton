#!/usr/bin/env python3
"""
Simple CI wrapper that controls stdin for message injection
"""

import sys
import os
import subprocess
import threading
import socket
import json
import select
from datetime import datetime

class SimpleWrapper:
    def __init__(self, name, command):
        self.name = name
        self.command = command
        self.socket_path = f"/tmp/ci_{name}.sock"
        self.process = None
        self.running = True
        
    def setup_socket(self):
        """Set up Unix socket for receiving messages"""
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.socket_path)
        self.sock.listen(5)
        os.chmod(self.socket_path, 0o666)
        print(f"[Wrapper] Listening on {self.socket_path}", file=sys.stderr)
    
    def socket_listener(self):
        """Listen for messages and inject to child's stdin"""
        while self.running:
            try:
                # Accept with timeout
                self.sock.settimeout(0.5)
                try:
                    conn, _ = self.sock.accept()
                except socket.timeout:
                    continue
                
                data = conn.recv(4096).decode('utf-8')
                conn.close()
                
                if data and self.process:
                    message = json.loads(data)
                    from_ci = message.get('from', 'Unknown')
                    content = message.get('content', '')
                    
                    # Format and inject to child's stdin
                    injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                    self.process.stdin.write(injection.encode('utf-8'))
                    self.process.stdin.flush()
                    print(f"[Wrapper] Injected message from {from_ci}", file=sys.stderr)
                    
            except Exception as e:
                if self.running:
                    print(f"[Wrapper] Socket error: {e}", file=sys.stderr)
    
    def run(self):
        """Run the wrapped command with stdin control"""
        # Set up socket
        self.setup_socket()
        
        # Start socket listener thread
        listener = threading.Thread(target=self.socket_listener, daemon=True)
        listener.start()
        
        # Start the child process with stdin as PIPE
        print(f"[Wrapper] Starting: {' '.join(self.command)}", file=sys.stderr)
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
            bufsize=0  # Unbuffered
        )
        
        # Pass through user input to child
        try:
            while self.process.poll() is None:
                # Check for user input (non-blocking)
                readable, _, _ = select.select([sys.stdin], [], [], 0.1)
                if sys.stdin in readable:
                    # Read from user and pass to child
                    user_input = sys.stdin.buffer.read1(1024)
                    if user_input:
                        self.process.stdin.write(user_input)
                        self.process.stdin.flush()
        except KeyboardInterrupt:
            print("\n[Wrapper] Interrupted", file=sys.stderr)
        except Exception as e:
            print(f"[Wrapper] Error: {e}", file=sys.stderr)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        # Terminate child if still running
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
        
        # Clean up socket
        if hasattr(self, 'sock'):
            self.sock.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        print(f"[Wrapper] Cleaned up", file=sys.stderr)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple CI wrapper with stdin injection')
    parser.add_argument('--name', required=True, help='CI name for socket')
    parser.add_argument('command', nargs='+', help='Command to wrap')
    
    args = parser.parse_args()
    
    wrapper = SimpleWrapper(args.name, args.command)
    wrapper.run()

if __name__ == "__main__":
    main()