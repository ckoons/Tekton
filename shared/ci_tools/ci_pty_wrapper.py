#!/usr/bin/env python3
"""
PTY-based CI wrapper for terminal programs with message injection
"""

import sys
import os
import pty
import termios
import tty
import threading
import socket
import json
import select
import signal
from datetime import datetime

class PTYWrapper:
    def __init__(self, name, command):
        self.name = name
        self.command = command
        self.socket_path = f"/tmp/ci_msg_{name}.sock"
        self.master_fd = None
        self.child_pid = None
        self.running = True
        
    def setup_socket(self):
        """Set up Unix socket for receiving messages"""
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.socket_path)
        self.sock.listen(5)
        os.chmod(self.socket_path, 0o666)
        print(f"[PTY Wrapper] Listening on {self.socket_path}", file=sys.stderr)
        
        # Register with CI registry
        self.register_ci()
    
    def register_ci(self):
        """Register this CI terminal with the registry."""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from shared.aish.src.registry.ci_registry import get_registry
            
            registry = get_registry()
            ci_info = {
                'name': self.name,
                'type': 'ci_terminal',
                'socket': self.socket_path,
                'working_directory': os.getcwd(),
                'capabilities': ['messaging', 'pty_injection'],
                'pid': os.getpid()
            }
            registry.register_wrapped_ci(ci_info)
            print(f"[PTY Wrapper] Registered {self.name} as ci_terminal", file=sys.stderr)
        except Exception as e:
            print(f"[PTY Wrapper] Failed to register: {e}", file=sys.stderr)
    
    def unregister_ci(self):
        """Unregister this CI terminal from the registry."""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from shared.aish.src.registry.ci_registry import get_registry
            
            registry = get_registry()
            registry.unregister_wrapped_ci(self.name)
            print(f"[PTY Wrapper] Unregistered {self.name}", file=sys.stderr)
        except Exception as e:
            print(f"[PTY Wrapper] Failed to unregister: {e}", file=sys.stderr)
    
    def socket_listener(self):
        """Listen for messages and inject to PTY"""
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
                
                if data and self.master_fd:
                    message = json.loads(data)
                    from_ci = message.get('from', 'Unknown')
                    content = message.get('content', '')
                    
                    # Format and inject to PTY
                    injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                    os.write(self.master_fd, injection.encode('utf-8'))
                    print(f"[PTY Wrapper] Injected message from {from_ci}", file=sys.stderr)
                    
            except Exception as e:
                if self.running:
                    print(f"[PTY Wrapper] Socket error: {e}", file=sys.stderr)
    
    def run(self):
        """Run the wrapped command in a PTY"""
        # Set up socket
        self.setup_socket()
        
        # Start socket listener thread
        listener = threading.Thread(target=self.socket_listener, daemon=True)
        listener.start()
        
        # Create PTY
        self.child_pid, self.master_fd = pty.fork()
        
        if self.child_pid == 0:
            # Child process - execute the command
            os.execvp(self.command[0], self.command)
        
        # Parent process - handle I/O
        print(f"[PTY Wrapper] Started child PID {self.child_pid}", file=sys.stderr)
        
        # Save terminal settings
        old_tty = None
        if sys.stdin.isatty():
            old_tty = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        
        try:
            while self.running:
                # Select on stdin and master_fd
                rfds, _, _ = select.select([sys.stdin, self.master_fd], [], [], 0.1)
                
                # Pass user input to PTY
                if sys.stdin in rfds:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    os.write(self.master_fd, data)
                
                # Pass PTY output to stdout
                if self.master_fd in rfds:
                    try:
                        data = os.read(self.master_fd, 1024)
                        if not data:
                            break
                        os.write(sys.stdout.fileno(), data)
                    except OSError:
                        break
                
                # Check if child exited
                pid, status = os.waitpid(self.child_pid, os.WNOHANG)
                if pid != 0:
                    print(f"\n[PTY Wrapper] Child exited with status {status}", file=sys.stderr)
                    break
                    
        except KeyboardInterrupt:
            print("\n[PTY Wrapper] Interrupted", file=sys.stderr)
        finally:
            # Restore terminal
            if old_tty:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        # Unregister from CI registry
        self.unregister_ci()
        
        # Close master FD
        if self.master_fd:
            os.close(self.master_fd)
        
        # Clean up socket
        if hasattr(self, 'sock'):
            self.sock.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        print(f"[PTY Wrapper] Cleaned up", file=sys.stderr)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='PTY wrapper with message injection')
    parser.add_argument('--name', required=True, help='CI name for socket')
    parser.add_argument('command', nargs='+', help='Command to wrap')
    
    args = parser.parse_args()
    
    # Check for name uniqueness
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from shared.aish.src.registry.ci_registry import get_registry
    
    registry = get_registry()
    if registry.get_by_name(args.name):
        print(f"Error: '{args.name}' already exists in CI registry", file=sys.stderr)
        print("Please use a unique name", file=sys.stderr)
        sys.exit(1)
    
    wrapper = PTYWrapper(args.name, args.command)
    wrapper.run()

if __name__ == "__main__":
    main()