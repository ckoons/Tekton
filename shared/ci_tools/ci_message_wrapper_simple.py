#!/usr/bin/env python3
"""
Simple CI Message Wrapper using line-based interception
"""

import sys
import os
import re
import json
import socket
import select
import threading
import pty
import termios
import tty
import queue
import signal
import time
from datetime import datetime
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.env import TektonEnviron
from shared.aish.src.registry.ci_registry import get_registry as CIRegistry

class CIMessageWrapper:
    """Simple line-based CI wrapper"""
    
    def __init__(self, name, ci_hint=None, working_dir=None):
        self.name = name
        self.ci_hint = ci_hint
        self.working_dir = working_dir or os.getcwd()
        
        # Message handling
        self.message_queue = queue.Queue()
        self.socket_path = f"/tmp/ci_msg_{self.name}.sock"
        
        # PTY handling
        self.master_fd = None
        self.child_pid = None
        
        # Set up socket listener
        self.setup_socket()
        
        # Register in CI registry
        self.register_ci()
        
        # Start message listener thread
        self.listener_thread = threading.Thread(target=self.socket_listener, daemon=True)
        self.listener_thread.start()
    
    def setup_socket(self):
        """Set up Unix socket for receiving messages"""
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.socket_path)
        self.socket.listen(5)
        os.chmod(self.socket_path, 0o666)
    
    def register_ci(self):
        """Register this CI in the registry"""
        registry = CIRegistry()
        entry = {
            'name': self.name,
            'type': 'wrapped_ci',
            'socket': self.socket_path,
            'working_directory': self.working_dir,
            'capabilities': ['messaging']
        }
        
        if self.ci_hint:
            entry['ci_hint'] = self.ci_hint
        
        registry.register_wrapped_ci(entry)
    
    def socket_listener(self):
        """Background thread listening for messages"""
        while True:
            try:
                conn, _ = self.socket.accept()
                data = conn.recv(4096).decode('utf-8')
                conn.close()
                
                if data:
                    message = json.loads(data)
                    self.message_queue.put(message)
            except Exception as e:
                break
    
    def check_aish_command(self, line):
        """Check if line is an aish CI command"""
        # Pattern: aish <ci-name> "message"
        if not line.startswith('aish '):
            return None
            
        pattern = r'^aish\s+([^\s"]+)\s+"([^"]*)"'
        match = re.match(pattern, line.strip())
        
        if match:
            target = match.group(1)
            message = match.group(2)
            
            # Check if target is a registered CI
            registry = CIRegistry()
            target_info = registry.get_ci(target)
            
            if target_info and target_info.get('type') == 'wrapped_ci':
                return {'target': target, 'message': message}
        
        return None
    
    def send_message(self, target, content):
        """Send a message to another CI"""
        registry = CIRegistry()
        target_info = registry.get_ci(target)
        
        if not target_info:
            return f"[Error: Unknown CI '{target}']\n"
        
        message = {
            'type': 'message',
            'from': self.name,
            'to': target,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        target_socket = target_info.get('socket')
        if target_socket and os.path.exists(target_socket):
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(target_socket)
                sock.send(json.dumps(message).encode('utf-8'))
                sock.close()
                return f"[Sent to {target}]\n"
            except Exception as e:
                return f"[Failed to send to {target}: {e}]\n"
        return f"[CI {target} not reachable]\n"
    
    def run_simple(self, command):
        """Run command with simple line-based interception"""
        # Create PTY
        self.child_pid, self.master_fd = pty.fork()
        
        if self.child_pid == 0:
            # Child process
            os.chdir(self.working_dir)
            os.execvp(command[0], command)
        
        # Parent process
        # Save terminal settings
        old_tty = None
        if sys.stdin.isatty():
            old_tty = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        
        try:
            # Simple I/O loop
            input_line = ""
            
            while True:
                # Check what's ready
                rfds, _, _ = select.select([sys.stdin, self.master_fd], [], [], 0.1)
                
                # Handle user input
                if sys.stdin in rfds:
                    char = os.read(sys.stdin.fileno(), 1)
                    if not char:
                        break
                    
                    # Build line
                    input_line += char.decode('utf-8', errors='ignore')
                    
                    # On Enter, check if it's an aish command
                    if char in b'\n\r':
                        line = input_line.strip()
                        cmd_info = self.check_aish_command(line)
                        
                        if cmd_info:
                            # It's a CI command - handle it
                            response = self.send_message(cmd_info['target'], cmd_info['message'])
                            # Inject response to terminal
                            os.write(self.master_fd, response.encode('utf-8'))
                            input_line = ""
                        else:
                            # Normal input - pass through
                            os.write(self.master_fd, input_line.encode('utf-8'))
                            input_line = ""
                    else:
                        # Not Enter - pass through immediately
                        os.write(self.master_fd, char)
                
                # Handle program output
                if self.master_fd in rfds:
                    try:
                        data = os.read(self.master_fd, 1024)
                        if not data:
                            break
                        os.write(sys.stdout.fileno(), data)
                    except OSError:
                        break
                
                # Check for incoming messages
                try:
                    message = self.message_queue.get_nowait()
                    # Format and inject
                    timestamp = datetime.now().strftime('%H:%M')
                    from_ci = message.get('from', 'Unknown')
                    content = message.get('content', '')
                    display = f"\n[{timestamp}] Message from {from_ci}: {content}\n"
                    os.write(self.master_fd, display.encode('utf-8'))
                except queue.Empty:
                    pass
                
                # Check if child exited
                pid, status = os.waitpid(self.child_pid, os.WNOHANG)
                if pid != 0:
                    break
            
        finally:
            # Restore terminal
            if old_tty:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            
            # Cleanup
            if self.master_fd:
                os.close(self.master_fd)
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'socket'):
            self.socket.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        # Remove from registry
        try:
            wrapped_file = os.path.join(TektonEnviron.get('TEKTON_ROOT'), '.tekton', 'aish', 'ci-registry', 'wrapped_cis.json')
            if os.path.exists(wrapped_file):
                with open(wrapped_file, 'r') as f:
                    wrapped_cis = json.load(f)
                if self.name in wrapped_cis:
                    del wrapped_cis[self.name]
                    with open(wrapped_file, 'w') as f:
                        json.dump(wrapped_cis, f, indent=2)
        except:
            pass


def main():
    """Main entry point"""
    from shared.env import TektonEnvironLock
    TektonEnvironLock.load()
    
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='ci-tool',
        description='CI Tool - Simple line-based aish messaging'
    )
    parser.add_argument('--name', required=True, help='Registry name')
    parser.add_argument('--ci', help='Optional CI/model hint')
    parser.add_argument('--dir', default=os.getcwd(), help='Working directory')
    parser.add_argument('command', nargs='+', help='Command to run')
    
    args = parser.parse_args()
    
    # Create wrapper
    wrapper = CIMessageWrapper(
        name=args.name,
        ci_hint=args.ci,
        working_dir=args.dir
    )
    
    # Display startup info
    sys.stderr.write(f"[CI Tool: {args.name} ready]\n")
    sys.stderr.write(f"[Socket: {wrapper.socket_path}]\n")
    sys.stderr.write(f"[Messaging: aish <ci-name> \"message\"]\n")
    sys.stderr.write(f"[Running: {' '.join(args.command)}]\n\n")
    
    # Run with simple line handling
    try:
        wrapper.run_simple(args.command)
    except KeyboardInterrupt:
        sys.stderr.write("\n[CI Tool: Interrupted]\n")
    
    sys.exit(0)


if __name__ == "__main__":
    main()