#!/usr/bin/env python3
"""
CI Message Wrapper
Enables @ command messaging for any CI tool by wrapping stdin/stdout
"""

import sys
import os
import re
import json
import socket
import select
import threading
import subprocess
import queue
from datetime import datetime
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.env import TektonEnviron
from shared.aish.src.registry.ci_registry import CIRegistry

class CIMessageWrapper:
    """Wraps any CI tool with messaging capabilities"""
    
    def __init__(self, name, ci_hint=None, working_dir=None):
        self.name = name  # Registry identifier (e.g., "Casey", "Beth", "coder-b")
        self.ci_hint = ci_hint  # Optional hint about what CI/model is used
        self.working_dir = working_dir or os.getcwd()
        
        # Message handling
        self.message_queue = queue.Queue()
        self.socket_path = f"/tmp/ci_msg_{self.name}.sock"
        self.in_code_block = False
        self.recent_messages = []
        
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
        
        # Add CI hint if provided
        if self.ci_hint:
            entry['ci_hint'] = self.ci_hint
            
        # Add directly to registry
        registry._registry[self.name] = entry
    
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
                print(f"\n[Message listener error: {e}]", file=sys.stderr)
    
    def parse_output_line(self, line):
        """Parse a line of output for @ commands"""
        # Check if we're in a code block
        if line.strip() == '```':
            self.in_code_block = not self.in_code_block
            return line, None
        
        # Don't parse inside code blocks
        if self.in_code_block:
            return line, None
        
        # Look for @ commands
        # Pattern: @command target "message"
        pattern = r'(@(?:send|ask|reply))\s+([^\s"]+)\s+"([^"]*)"'
        match = re.search(pattern, line)
        
        if match:
            command = match.group(1)
            target = match.group(2)
            message = match.group(3)
            
            # Return line as-is, plus the extracted command
            return line, {
                'command': command,
                'target': target,
                'message': message
            }
        
        # Check for @status
        if '@status' in line and not self.in_code_block:
            return line, {'command': '@status'}
        
        return line, None
    
    def execute_command(self, cmd_info):
        """Execute an @ command in the background"""
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
            print(f"\n[Error: Unknown target '{target}']", file=sys.stderr)
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
                print(f"\n[Sent to {target}]", file=sys.stderr)
            except Exception as e:
                print(f"\n[Failed to send to {target}: {e}]", file=sys.stderr)
    
    def show_status(self):
        """Display message status"""
        print("\n=== Message Status ===", file=sys.stderr)
        print(f"Recent messages: {len(self.recent_messages)}", file=sys.stderr)
        if self.recent_messages:
            for msg in self.recent_messages[-5:]:
                print(f"  {msg['from']}: {msg['content'][:50]}...", file=sys.stderr)
        print("===================\n", file=sys.stderr)
    
    def display_message(self, message):
        """Display an incoming message"""
        timestamp = datetime.now().strftime('%H:%M')
        msg_type = message.get('type', 'message')
        from_ci = message.get('from', 'Unknown')
        content = message.get('content', '')
        
        # Format based on type
        if msg_type == 'question':
            display = f"\n[{timestamp}] Question from {from_ci}: {content}\nReply with: @reply {from_ci} \"your answer\"\n"
        else:
            display = f"\n[{timestamp}] Message from {from_ci}: {content}\n"
        
        # Print to stderr so it doesn't interfere with stdout parsing
        print(display, file=sys.stderr)
        
        # Add to recent messages
        self.recent_messages.append(message)
        self.recent_messages = self.recent_messages[-20:]  # Keep last 20
    
    def run_wrapped_command(self, command_args):
        """Run the wrapped command with I/O interception"""
        # Start the subprocess
        process = subprocess.Popen(
            command_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Create threads for I/O handling
        def handle_stdout():
            """Read from subprocess stdout and parse for @ commands"""
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Parse the line
                    output_line, cmd_info = self.parse_output_line(line)
                    
                    # Always print the line
                    print(output_line, end='', flush=True)
                    
                    # Execute command if found
                    if cmd_info:
                        threading.Thread(
                            target=self.execute_command,
                            args=(cmd_info,),
                            daemon=True
                        ).start()
        
        def handle_stdin():
            """Read from our stdin and pass to subprocess, checking for messages"""
            while True:
                # Check for messages
                while not self.message_queue.empty():
                    try:
                        message = self.message_queue.get_nowait()
                        self.display_message(message)
                    except queue.Empty:
                        break
                
                # Check if stdin has data
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    line = sys.stdin.readline()
                    if line:
                        process.stdin.write(line)
                        process.stdin.flush()
                    else:
                        # EOF on stdin
                        process.stdin.close()
                        break
        
        # Start I/O threads
        stdout_thread = threading.Thread(target=handle_stdout, daemon=True)
        stdin_thread = threading.Thread(target=handle_stdin, daemon=True)
        
        stdout_thread.start()
        stdin_thread.start()
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Clean up
        self.cleanup()
        
        return return_code
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'socket'):
            self.socket.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)


def main():
    """Main entry point"""
    # Initialize TektonEnviron first since we're a top-level entry point
    from shared.env import TektonEnvironLock
    TektonEnvironLock.load()
    
    import argparse
    
    parser = argparse.ArgumentParser(
        prog='ci-tool',
        description='CI Tool - Adds @ command messaging to any program',
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
    print(f"[CI Tool: {args.name} ready]", file=sys.stderr)
    if args.ci:
        print(f"[CI Hint: {args.ci}]", file=sys.stderr)
    print(f"[Socket: {wrapper.socket_path}]", file=sys.stderr)
    print(f"[Running: {' '.join(args.command)}]\n", file=sys.stderr)
    
    # Run wrapped command
    return_code = wrapper.run_wrapped_command(args.command)
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()