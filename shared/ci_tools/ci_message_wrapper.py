#!/usr/bin/env python3
"""
CI Message Wrapper using PTY
Transparent message interception using pseudo-terminals
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
from datetime import datetime
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.env import TektonEnviron
from shared.aish.src.registry.ci_registry import get_registry as CIRegistry

class CIMessageWrapper:
    """Transparent CI wrapper using pseudo-terminal"""
    
    def __init__(self, name, ci_hint=None, working_dir=None):
        self.name = name
        self.ci_hint = ci_hint
        self.working_dir = working_dir or os.getcwd()
        
        # Message handling
        self.message_queue = queue.Queue()
        self.socket_path = f"/tmp/ci_msg_{self.name}.sock"
        self.in_code_block = False
        self.recent_messages = []
        self.parser_enabled = True  # Default to enabled
        
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
    
    def parse_line_for_commands(self, line):
        """Parse a line for @ commands"""
        # Check for parser control sequences
        if "### ci-tool parser DISABLE ###" in line:
            self.parser_enabled = False
            return None
        elif "### ci-tool parser ENABLE ###" in line:
            self.parser_enabled = True
            return None
        
        # If parser is disabled, don't parse anything
        if not self.parser_enabled:
            return None
        
        # Check if we're entering/exiting a code block
        if line.strip() == '```':
            self.in_code_block = not self.in_code_block
            return None
        
        # Don't parse inside code blocks
        if self.in_code_block:
            return None
        
        # Look for @ commands
        pattern = r'(@(?:send|ask|reply))\s+([^\s"]+)\s+"([^"]*)"'
        match = re.search(pattern, line)
        
        if match:
            return {
                'command': match.group(1),
                'target': match.group(2),
                'message': match.group(3)
            }
        
        # Check for @status
        if '@status' in line and not self.in_code_block:
            return {'command': '@status'}
        
        return None
    
    def execute_command(self, cmd_info):
        """Execute an @ command"""
        command = cmd_info['command']
        
        if command == '@send':
            self.send_message(cmd_info['target'], cmd_info['message'], 'message')
        elif command == '@ask':
            self.send_message(cmd_info['target'], cmd_info['message'], 'question')
        elif command == '@reply':
            self.send_message(cmd_info['target'], cmd_info['message'], 'reply')
        elif command == '@status':
            self.show_status()
    
    def send_message(self, target, content, msg_type):
        """Send a message to another CI"""
        registry = CIRegistry()
        target_info = registry.get_ci(target)
        
        if not target_info:
            self.inject_to_terminal(f"\n[Error: Unknown target '{target}']\n")
            return
        
        message = {
            'type': msg_type,
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
                self.inject_to_terminal(f"\n[Sent to {target}]\n")
            except Exception as e:
                self.inject_to_terminal(f"\n[Failed to send to {target}: {e}]\n")
    
    def show_status(self):
        """Display message status"""
        status = "\n=== Message Status ===\n"
        status += f"Recent messages: {len(self.recent_messages)}\n"
        if self.recent_messages:
            for msg in self.recent_messages[-5:]:
                status += f"  {msg['from']}: {msg['content'][:50]}...\n"
        status += "===================\n"
        self.inject_to_terminal(status)
    
    def inject_to_terminal(self, text):
        """Inject text to terminal (visible to user and program)"""
        if self.master_fd:
            os.write(self.master_fd, text.encode('utf-8'))
    
    def display_incoming_message(self, message):
        """Display an incoming message"""
        timestamp = datetime.now().strftime('%H:%M')
        msg_type = message.get('type', 'message')
        from_ci = message.get('from', 'Unknown')
        content = message.get('content', '')
        
        if msg_type == 'question':
            display = f"\n[{timestamp}] Question from {from_ci}: {content}\nReply with: @reply {from_ci} \"your answer\"\n"
        else:
            display = f"\n[{timestamp}] Message from {from_ci}: {content}\n"
        
        self.inject_to_terminal(display)
        self.recent_messages.append(message)
        self.recent_messages = self.recent_messages[-20:]
    
    def run_with_pty(self, command):
        """Run command with PTY for transparent I/O"""
        # Save current terminal settings
        old_tty = termios.tcgetattr(sys.stdin)
        
        try:
            # Create PTY
            self.child_pid, self.master_fd = pty.fork()
            
            if self.child_pid == 0:
                # Child process - exec the command
                os.chdir(self.working_dir)
                os.execvp(command[0], command)
            
            # Parent process - handle I/O
            # Set stdin to raw mode
            tty.setraw(sys.stdin.fileno())
            
            # Main I/O loop
            output_buffer = ""
            while True:
                # Check what's ready to read
                rfds, _, _ = select.select([sys.stdin, self.master_fd], [], [], 0.1)
                
                # Handle stdin -> master (user input)
                if sys.stdin in rfds:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if data:
                        os.write(self.master_fd, data)
                
                # Handle master -> stdout (program output)
                if self.master_fd in rfds:
                    try:
                        data = os.read(self.master_fd, 1024)
                        if not data:
                            break
                        
                        # Write to real stdout immediately
                        os.write(sys.stdout.fileno(), data)
                        
                        # Also buffer for line parsing
                        output_buffer += data.decode('utf-8', errors='ignore')
                        
                        # Parse complete lines
                        while '\n' in output_buffer:
                            line, output_buffer = output_buffer.split('\n', 1)
                            cmd_info = self.parse_line_for_commands(line)
                            if cmd_info:
                                # Execute command in background thread
                                threading.Thread(
                                    target=self.execute_command,
                                    args=(cmd_info,),
                                    daemon=True
                                ).start()
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
            # Restore terminal settings
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
        description='CI Tool - Transparent @ command messaging using PTY',
        epilog='Example: ci-tool --name Casey --ci claude-opus-4 -- claude --debug'
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