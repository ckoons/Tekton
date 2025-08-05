#!/usr/bin/env python3
"""
CI Message Wrapper using aish commands
Transparent message interception for aish CI communication
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
    """Transparent CI wrapper that intercepts aish commands"""
    
    def __init__(self, name, ci_hint=None, working_dir=None):
        self.name = name
        self.ci_hint = ci_hint
        self.working_dir = working_dir or os.getcwd()
        
        # Message handling
        self.message_queue = queue.Queue()
        self.socket_path = f"/tmp/ci_msg_{self.name}.sock"
        self.recent_messages = []
        
        # PTY handling
        self.master_fd = None
        self.child_pid = None
        
        # Input buffering
        self.stdin_buffer = ""
        self.intercepted_line = None
        
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
        
        # Use the proper registration method
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
                if self.master_fd:  # Only print if still running
                    sys.stderr.write(f"\n[Message listener error: {e}]\n")
                break
    
    def parse_aish_command(self, line):
        """Parse stdin line for aish CI messaging commands"""
        # Look for pattern: aish <ci-name> "message"
        pattern = r'^aish\s+([^\s"]+)\s+"([^"]*)"'
        match = re.match(pattern, line.strip())
        
        if match:
            target = match.group(1)
            message = match.group(2)
            
            # Check if target is a registered CI
            registry = CIRegistry()
            target_info = registry.get_ci(target)
            
            if target_info and target_info.get('type') == 'wrapped_ci':
                return {
                    'target': target,
                    'message': message
                }
        
        return None
    
    def send_message(self, target, content):
        """Send a message to another CI"""
        registry = CIRegistry()
        target_info = registry.get_ci(target)
        
        if not target_info:
            response = f"[Error: Unknown CI '{target}']\n"
            self.inject_to_stdin(response)
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
                # Inject confirmation to stdin
                response = f"[Sent to {target}]\n"
                self.inject_to_stdin(response)
            except Exception as e:
                response = f"[Failed to send to {target}: {e}]\n"
                self.inject_to_stdin(response)
    
    def inject_to_stdin(self, text):
        """Inject text as if it came from stdin"""
        if self.master_fd:
            # Inject the response back through stdin
            os.write(self.master_fd, text.encode('utf-8'))
    
    def display_incoming_message(self, message):
        """Display an incoming message via stdin injection"""
        timestamp = datetime.now().strftime('%H:%M')
        from_ci = message.get('from', 'Unknown')
        content = message.get('content', '')
        
        # Format message and inject via stdin
        display = f"\n[{timestamp}] Message from {from_ci}: {content}\n"
        self.inject_to_stdin(display)
        
        # Track recent messages
        self.recent_messages.append(message)
        self.recent_messages = self.recent_messages[-20:]
    
    def run_with_pty(self, command):
        """Run command with PTY for transparent I/O"""
        # Save current terminal settings if we have a tty
        old_tty = None
        if sys.stdin.isatty():
            old_tty = termios.tcgetattr(sys.stdin)
        
        try:
            # Create PTY
            self.child_pid, self.master_fd = pty.fork()
            
            if self.child_pid == 0:
                # Child process - exec the command
                os.chdir(self.working_dir)
                os.execvp(command[0], command)
            
            # Parent process - handle I/O
            # Set stdin to raw mode if we have a tty
            if old_tty:
                tty.setraw(sys.stdin.fileno())
            
            # Main I/O loop
            return_code = 0  # Default return code
            while True:
                # Check what's ready to read
                rfds, _, _ = select.select([sys.stdin, self.master_fd], [], [], 0.1)
                
                # Handle stdin -> master (user input)
                if sys.stdin in rfds:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if data:
                        # Buffer stdin to look for complete lines
                        self.stdin_buffer += data.decode('utf-8', errors='ignore')
                        
                        # Check for complete line with Enter
                        if '\n' in self.stdin_buffer or '\r' in self.stdin_buffer:
                            lines = self.stdin_buffer.split('\n')
                            for i, line in enumerate(lines[:-1]):
                                # Check if this is an aish CI command
                                cmd_info = self.parse_aish_command(line)
                                if cmd_info:
                                    # Intercept this line - don't pass to wrapped program
                                    self.intercepted_line = line
                                    # Execute the command
                                    self.send_message(cmd_info['target'], cmd_info['message'])
                                else:
                                    # Not a CI command, pass through normally
                                    os.write(self.master_fd, (line + '\n').encode('utf-8'))
                            
                            # Keep any incomplete line in buffer
                            self.stdin_buffer = lines[-1]
                        else:
                            # No complete line yet, pass through character by character
                            os.write(self.master_fd, data)
                            self.stdin_buffer = ""
                
                # Handle master -> stdout (program output)
                if self.master_fd in rfds:
                    try:
                        data = os.read(self.master_fd, 1024)
                        if not data:
                            break
                        
                        # Write to real stdout
                        os.write(sys.stdout.fileno(), data)
                    except OSError:
                        break
                
                # Check for incoming messages
                try:
                    message = self.message_queue.get_nowait()
                    self.display_incoming_message(message)
                except queue.Empty:
                    pass
                
                # Check if child process ended
                pid, status = os.waitpid(self.child_pid, os.WNOHANG)
                if pid != 0:
                    return_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1
                    break
            
            return return_code
            
        finally:
            # Restore terminal settings if we had them
            if old_tty:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
            
            # Clean up
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
    # Initialize TektonEnviron first
    from shared.env import TektonEnvironLock
    TektonEnvironLock.load()
    
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='ci-tool',
        description='CI Tool - Transparent aish command messaging',
        epilog='Example: aish ci-tool --name Casey --ci claude-opus-4 -- claude --debug'
    )
    parser.add_argument('--name', required=True, help='Registry name (e.g., Casey, Beth, coder-b)')
    parser.add_argument('--ci', help='Optional CI/model hint (e.g., claude-opus-4, llama3.3:70b)')
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
    if args.ci:
        sys.stderr.write(f"[CI Hint: {args.ci}]\n")
    sys.stderr.write(f"[Socket: {wrapper.socket_path}]\n")
    sys.stderr.write(f"[Messaging: aish <ci-name> \"message\"]\n")
    sys.stderr.write(f"[Running: {' '.join(args.command)}]\n\n")
    
    # Run with PTY
    try:
        return_code = wrapper.run_with_pty(args.command)
    except KeyboardInterrupt:
        sys.stderr.write("\n[CI Tool: Interrupted]\n")
        return_code = 130  # Standard shell interrupt code
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()