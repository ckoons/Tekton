#!/usr/bin/env python3
"""
Passthrough CI Message Wrapper - everything goes to wrapped program
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
    """Passthrough wrapper - all input goes to wrapped program"""
    
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
        
        # Track what user types (for parsing after Enter)
        self.current_line = ""
        
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
    
    def find_aish_commands(self, line):
        """Find all aish CI commands in a line"""
        commands = []
        # Find all matches of: aish <ci-name> "message"
        pattern = r'aish\s+([^\s"]+)\s+"([^"]*)"'
        for match in re.finditer(pattern, line):
            target = match.group(1)
            message = match.group(2)
            
            # Check if target is a registered CI
            registry = CIRegistry()
            target_info = registry.get_ci(target)
            
            if target_info and target_info.get('type') == 'wrapped_ci':
                commands.append({'target': target, 'message': message})
        
        return commands
    
    def send_message(self, target, content):
        """Send a message to another CI"""
        registry = CIRegistry()
        target_info = registry.get_ci(target)
        
        if not target_info:
            return
        
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
            except:
                pass
    
    def run_passthrough(self, command):
        """Run command with complete passthrough"""
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
            while True:
                # Check what's ready
                rfds, _, _ = select.select([sys.stdin, self.master_fd], [], [], 0.1)
                
                # Handle user input - ALWAYS pass through immediately
                if sys.stdin in rfds:
                    char = os.read(sys.stdin.fileno(), 1)
                    if not char:
                        break
                    
                    # Pass through to wrapped program immediately
                    os.write(self.master_fd, char)
                    
                    # Track what was typed (for parsing after Enter)
                    decoded = char.decode('utf-8', errors='ignore')
                    if char in b'\n\r':
                        # User pressed Enter - check if line had any aish commands
                        commands = self.find_aish_commands(self.current_line)
                        for cmd in commands:
                            self.send_message(cmd['target'], cmd['message'])
                        self.current_line = ""
                    else:
                        self.current_line += decoded
                
                # Handle program output - pass through immediately
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
                    # Format and inject to wrapped program's stdin
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
        description='CI Tool - Passthrough wrapper with aish messaging'
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
    
    # Run with passthrough
    try:
        wrapper.run_passthrough(args.command)
    except KeyboardInterrupt:
        sys.stderr.write("\n[CI Tool: Interrupted]\n")
    
    sys.exit(0)


if __name__ == "__main__":
    main()