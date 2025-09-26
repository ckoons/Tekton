#!/usr/bin/env python3
"""
PTY-based CI wrapper for terminal programs with message injection
Enhanced with mandatory sundown/sunrise hooks for memory management
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
import time
from datetime import datetime
from pathlib import Path

# Import hook system
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from shared.ci_tools.ci_wrapper_hooks import CIHookSystem
    hooks_available = True
except ImportError:
    hooks_available = False

class PTYWrapper:
    def __init__(self, name, command, delimiter=None, enable_hooks=True):
        self.name = name
        self.command = command
        self.delimiter = delimiter  # Store default delimiter for auto-execution
        self.socket_path = f"/tmp/ci_msg_{name}.sock"
        self.master_fd = None
        self.child_pid = None
        self.running = True
        self.enable_hooks = enable_hooks and hooks_available

        # Initialize hook system for mandatory operations
        if self.enable_hooks:
            self.hook_system = CIHookSystem(name)
            self.session_output = []
            self.output_buffer = []

        # No buffering - simple pass-through
        # Keep hooks for compatibility but no output buffering
        
    def setup_socket(self):
        """Set up Unix socket for receiving messages"""
        # If socket exists, check for orphaned process
        if os.path.exists(self.socket_path):
            try:
                import subprocess
                result = subprocess.run(['lsof', '-t', self.socket_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    old_pid = int(result.stdout.strip())
                    # Verify it's a CI wrapper process (not some other process)
                    try:
                        with open(f'/proc/{old_pid}/cmdline', 'r') as f:
                            cmdline = f.read()
                    except:
                        # Fall back to ps command for macOS
                        ps_result = subprocess.run(['ps', '-p', str(old_pid), '-o', 'command='],
                                                 capture_output=True, text=True)
                        cmdline = ps_result.stdout
                    
                    # Check if it's a CI wrapper for the same name
                    if ('ci_pty_wrapper' in cmdline or 'ci-tool' in cmdline) and self.name in cmdline:
                        print(f"[PTY Wrapper] Found orphaned process {old_pid}, terminating...", file=sys.stderr)
                        os.kill(old_pid, signal.SIGTERM)
                        import time
                        time.sleep(0.5)
                        # Check if still exists and force kill if needed
                        try:
                            os.kill(old_pid, 0)  # Check if process exists
                            os.kill(old_pid, signal.SIGKILL)
                            print(f"[PTY Wrapper] Force killed orphaned process {old_pid}", file=sys.stderr)
                        except ProcessLookupError:
                            print(f"[PTY Wrapper] Orphaned process {old_pid} terminated cleanly", file=sys.stderr)
            except Exception as e:
                print(f"[PTY Wrapper] Could not check for orphaned process: {e}", file=sys.stderr)
            
            # Remove the socket file
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
        """Unregister this CI from the registry."""
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

    # Removed buffering methods - no longer needed
    
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
                
                try:
                    data = conn.recv(4096).decode('utf-8')
                    conn.close()
                except Exception as e:
                    print(f"[PTY Wrapper] Error receiving data: {e}", file=sys.stderr)
                    conn.close()
                    continue
                
                if data and self.master_fd:
                    try:
                        message = json.loads(data)
                    except json.JSONDecodeError as e:
                        print(f"[PTY Wrapper] Invalid JSON: {e}", file=sys.stderr)
                        continue
                    
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
                        print(f"[PTY Wrapper] Executing command from {from_ci} with delimiter", file=sys.stderr)
                    else:
                        # Format as message notification
                        injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                        print(f"[PTY Wrapper] Injected message from {from_ci}", file=sys.stderr)
                    
                    # Direct write for message injection
                    os.write(self.master_fd, injection.encode('utf-8'))
                    
            except Exception as e:
                if self.running:
                    print(f"[PTY Wrapper] Socket listener error: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    # Don't let the listener thread die - continue listening
                    continue
    
    def run(self):
        """Run the wrapped command in a PTY"""
        # Set up signal handler for clean shutdown
        def signal_handler(signum, frame):
            print(f"\n[PTY Wrapper] Received signal {signum}, cleaning up...", file=sys.stderr)
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)  # Handle terminal hangup
        
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
        else:
            # Parent process - handle I/O
            print(f"[PTY Wrapper] Started child PID {self.child_pid}", file=sys.stderr)
            
            # Check if we have a valid terminal
            has_terminal = sys.stdin.isatty()
            old_tty = None

            try:
                if has_terminal:
                    # Save terminal settings and use raw mode
                    # This is needed for proper input handling with Claude
                    try:
                        old_tty = termios.tcgetattr(sys.stdin)
                        # Use raw mode - this works best with Claude
                        tty.setraw(sys.stdin.fileno())
                    except:
                        # If we can't get terminal attributes, continue
                        has_terminal = False
                        print(f"[PTY Wrapper] Running without terminal (background mode)", file=sys.stderr)
                
                # Simple pass-through I/O loop - no buffering
                stdin_closed = False

                while True:
                    try:
                        # Build select list
                        read_fds = [self.master_fd]
                        if has_terminal and not stdin_closed:
                            read_fds.append(sys.stdin)

                        r, w, e = select.select(read_fds, [], [], 0.1)
                        
                        if self.master_fd in r:
                            try:
                                data = os.read(self.master_fd, 10240)
                                if data:
                                    # Simple pass-through - write ONCE to stdout
                                    os.write(1, data)  # Direct to stdout

                                    # Process through hooks if enabled (but don't write again!)
                                    if self.enable_hooks:
                                        try:
                                            output_str = data.decode('utf-8', errors='replace')
                                            self.output_buffer.append(output_str)

                                            # Check for complete lines to process
                                            full_output = ''.join(self.output_buffer)
                                            if '\n' in full_output or len(full_output) > 1024:
                                                # Process through hooks
                                                context = {
                                                    'output': full_output,
                                                    'ci_name': self.name,
                                                    'session_output': '\n'.join(self.session_output)
                                                }
                                                context = self.hook_system.execute_hooks('post_output', context)

                                                # Store for session history
                                                self.session_output.append(full_output)

                                                # Check if sundown required
                                                if context.get('require_sundown'):
                                                    sundown_prompt = self.hook_system._get_sundown_prompt()
                                                    prompt_bytes = sundown_prompt.encode('utf-8')
                                                    # Inject sundown prompt to PTY
                                                    os.write(self.master_fd, prompt_bytes)

                                                self.output_buffer = []
                                        except Exception as e:
                                            print(f"[Hook Error] {e}", file=sys.stderr)
                                elif not data:
                                    # EOF from child
                                    break
                            except OSError:
                                break
                        
                        if has_terminal and sys.stdin in r:
                            try:
                                data = os.read(sys.stdin.fileno(), 10240)
                                if data:
                                    # Simple pass-through - user input to PTY
                                    os.write(self.master_fd, data)
                                else:
                                    # EOF on stdin - terminal disconnected
                                    print(f"\n[PTY Wrapper] stdin closed, terminal disconnected", file=sys.stderr)
                                    stdin_closed = True
                                    # Continue running to keep the wrapped process alive
                            except (OSError, BrokenPipeError):
                                stdin_closed = True
                    except (KeyboardInterrupt, OSError):
                        break
                    
                    # Check if child is still alive
                    pid, status = os.waitpid(self.child_pid, os.WNOHANG)
                    if pid != 0:
                        print(f"\n[PTY Wrapper] Child process {self.child_pid} exited", file=sys.stderr)
                        break
                    
                    # Check parent process periodically (detect orphan state)
                    if os.getppid() == 1:  # Parent is init, we're orphaned
                        print(f"\n[PTY Wrapper] Orphaned (parent died), cleaning up...", file=sys.stderr)
                        break
                        
            finally:
                # Restore terminal settings if we had them
                if old_tty and has_terminal:
                    try:
                        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, old_tty)
                    except:
                        pass  # Terminal may be gone
                self.cleanup()
    
    def cleanup(self):
        """Clean up resources with mandatory sundown check"""
        self.running = False

        # No buffering to flush - just ensure clean exit

        # Execute pre-sundown hooks if enabled
        if self.enable_hooks and hasattr(self, 'session_output') and self.session_output:
            try:
                context = {
                    'session_output': '\n'.join(self.session_output),
                    'ci_name': self.name
                }

                # Check for sundown
                context = self.hook_system.execute_hooks('pre_sundown', context)

                if context.get('block_exit'):
                    # Sundown required but not provided
                    print("\n" + "="*60, file=sys.stderr)
                    print("WARNING: Session ending without sundown notes!", file=sys.stderr)
                    print("Next session will start without context.", file=sys.stderr)
                    print("="*60 + "\n", file=sys.stderr)

                    # Try auto-generation one more time
                    if context.get('auto_sundown'):
                        print("Auto-generated sundown stored:", file=sys.stderr)
                        print(context['auto_sundown'][:500] + "...", file=sys.stderr)

                # Execute post-sundown hooks
                self.hook_system.execute_hooks('post_sundown', context)
            except Exception as e:
                print(f"[Sundown Error] {e}", file=sys.stderr)

        # Terminate child process if still running
        if self.child_pid:
            try:
                os.kill(self.child_pid, signal.SIGTERM)
                print(f"[PTY Wrapper] Sent SIGTERM to child {self.child_pid}", file=sys.stderr)
                import time
                time.sleep(0.5)
                # Check if still running and force kill if needed
                try:
                    os.kill(self.child_pid, 0)  # Check if process exists
                    os.kill(self.child_pid, signal.SIGKILL)
                    print(f"[PTY Wrapper] Force killed child {self.child_pid}", file=sys.stderr)
                except ProcessLookupError:
                    pass  # Process already terminated
            except ProcessLookupError:
                pass  # Process already terminated
        
        # Unregister from CI registry
        self.unregister_ci()
        
        # Close master FD
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass  # Already closed
        
        # Clean up socket
        if hasattr(self, 'sock'):
            try:
                self.sock.close()
            except:
                pass
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
                print(f"[PTY Wrapper] Removed socket {self.socket_path}", file=sys.stderr)
            except:
                pass
        
        print(f"[PTY Wrapper] Cleaned up", file=sys.stderr)

def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PTY wrapper with message injection')
    parser.add_argument('--name', '-n', help='CI name for socket')
    parser.add_argument('--delimiter', '-d', default=None, help='Default delimiter for auto-execution')
    parser.add_argument('--no-hooks', action='store_true', help='Disable mandatory sundown hooks')
    parser.add_argument('command', nargs='*', help='Command to wrap')
    
    args = parser.parse_args()
    
    # Require command and name
    if not args.command:
        parser.error("command is required")
    if not args.name:
        parser.error("--name/-n is required")
    
    # Decode escape sequences in delimiter if provided
    if args.delimiter:
        try:
            args.delimiter = args.delimiter.encode('utf-8').decode('unicode_escape')
        except:
            pass  # Keep original if decoding fails
    
    # Check for name uniqueness
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from shared.aish.src.registry.ci_registry import get_registry
    
    registry = get_registry()
    if registry.get_by_name(args.name):
        print(f"Error: '{args.name}' already exists in CI registry", file=sys.stderr)
        print("Please use a unique name", file=sys.stderr)
        sys.exit(1)
    
    # Create wrapper with hooks enabled by default
    enable_hooks = not args.no_hooks
    if hooks_available:
        if enable_hooks:
            print(f"[PTY Wrapper] Sundown/sunrise hooks ENABLED for {args.name}", file=sys.stderr)
        else:
            print(f"[PTY Wrapper] Hooks disabled for {args.name}", file=sys.stderr)
    else:
        print(f"[PTY Wrapper] Hook system not available", file=sys.stderr)

    wrapper = PTYWrapper(args.name, args.command, args.delimiter, enable_hooks=enable_hooks)
    wrapper.run()

if __name__ == "__main__":
    main()