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
import signal
from datetime import datetime

class SimpleWrapper:
    def __init__(self, name, command, delimiter=None):
        self.name = name
        self.command = command
        self.delimiter = delimiter  # Store default delimiter for auto-execution
        self.socket_path = f"/tmp/ci_msg_{name}.sock"  # Use same pattern as PTY wrapper
        self.process = None
        self.running = True
        
    def setup_socket(self):
        """Set up Unix socket for receiving messages"""
        # Check for orphaned process like PTY wrapper does
        if os.path.exists(self.socket_path):
            try:
                result = subprocess.run(['lsof', '-t', self.socket_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    old_pid = int(result.stdout.strip())
                    # Check if it's a CI wrapper for the same name
                    ps_result = subprocess.run(['ps', '-p', str(old_pid), '-o', 'command='],
                                             capture_output=True, text=True)
                    cmdline = ps_result.stdout
                    if ('ci_simple_wrapper' in cmdline or 'ci-tool' in cmdline) and self.name in cmdline:
                        print(f"[Wrapper] Found orphaned process {old_pid}, terminating...", file=sys.stderr)
                        os.kill(old_pid, signal.SIGTERM)
                        import time
                        time.sleep(0.5)
                        try:
                            os.kill(old_pid, 0)
                            os.kill(old_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
            except Exception as e:
                print(f"[Wrapper] Could not check for orphaned process: {e}", file=sys.stderr)
            
            os.unlink(self.socket_path)
        
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.socket_path)
        self.sock.listen(5)
        os.chmod(self.socket_path, 0o666)
        print(f"[Wrapper] Listening on {self.socket_path}", file=sys.stderr)
        
        # Register with CI registry
        self.register_ci()
    
    def register_ci(self):
        """Register this CI with the registry."""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from shared.aish.src.registry.ci_registry import get_registry
            
            registry = get_registry()
            ci_info = {
                'name': self.name,
                'type': 'ci_tool',
                'socket': self.socket_path,
                'working_directory': os.getcwd(),
                'capabilities': ['messaging', 'stdin_injection'],
                'pid': os.getpid()
            }
            registry.register_wrapped_ci(ci_info)
            print(f"[Wrapper] Registered {self.name} as ci_tool", file=sys.stderr)
        except Exception as e:
            print(f"[Wrapper] Failed to register: {e}", file=sys.stderr)
    
    def unregister_ci(self):
        """Unregister this CI from the registry."""
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from shared.aish.src.registry.ci_registry import get_registry
            
            registry = get_registry()
            registry.unregister_wrapped_ci(self.name)
            print(f"[Wrapper] Unregistered {self.name}", file=sys.stderr)
        except Exception as e:
            print(f"[Wrapper] Failed to unregister: {e}", file=sys.stderr)
    
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
                    execute = message.get('execute', False)
                    
                    # Check if we should append delimiter for execution
                    if execute:
                        # Use message delimiter, wrapper delimiter, or default to \n
                        raw_delimiter = message.get('delimiter', self.delimiter or '\n')
                        # Decode escape sequences in delimiter
                        try:
                            delimiter = raw_delimiter.encode('utf-8').decode('unicode_escape')
                        except:
                            delimiter = raw_delimiter
                        # For raw command execution, just send content + delimiter
                        injection = content + delimiter
                        print(f"[Wrapper] Executing command from {from_ci} with delimiter", file=sys.stderr)
                    else:
                        # Format as message notification
                        injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                        print(f"[Wrapper] Injected message from {from_ci}", file=sys.stderr)
                    
                    self.process.stdin.write(injection.encode('utf-8'))
                    self.process.stdin.flush()
                    
            except Exception as e:
                if self.running:
                    print(f"[Wrapper] Socket error: {e}", file=sys.stderr)
    
    def run(self):
        """Run the wrapped command with stdin control"""
        # Set up signal handler for clean shutdown
        def signal_handler(signum, frame):
            print(f"\n[Wrapper] Received signal {signum}, cleaning up...", file=sys.stderr)
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
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
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        
        # Unregister from CI registry
        self.unregister_ci()
        
        # Clean up socket
        if hasattr(self, 'sock'):
            try:
                self.sock.close()
            except:
                pass
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
                print(f"[Wrapper] Removed socket {self.socket_path}", file=sys.stderr)
            except:
                pass
        
        print(f"[Wrapper] Cleaned up", file=sys.stderr)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple CI wrapper with stdin injection')
    parser.add_argument('--name', '-n', required=True, help='CI name for socket')
    parser.add_argument('--delimiter', '-d', default=None, help='Default delimiter for auto-execution')
    parser.add_argument('command', nargs='+', help='Command to wrap')
    
    args = parser.parse_args()
    
    # Decode escape sequences in delimiter if provided
    if args.delimiter:
        try:
            args.delimiter = args.delimiter.encode('utf-8').decode('unicode_escape')
        except:
            pass  # Keep original if decoding fails
    
    wrapper = SimpleWrapper(args.name, args.command, args.delimiter)
    wrapper.run()

if __name__ == "__main__":
    main()