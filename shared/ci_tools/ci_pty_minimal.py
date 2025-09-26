#!/usr/bin/env python3
"""
Minimal CI wrapper for terminal programs - PTY for injection only.
Parent process stays alive for socket listening, no stdout/stdin handling.
"""

import sys
import os
import pty
import socket
import json
import threading
import signal
import time
import select
import termios
import tty
from pathlib import Path
from datetime import datetime

class MinimalPTYWrapper:
    def __init__(self, name, command, delimiter=None):
        self.name = name
        self.command = command
        self.delimiter = delimiter
        self.socket_path = f"/tmp/ci_msg_{name}.sock"
        self.master_fd = None
        self.child_pid = None
        self.running = True

    def setup_socket(self):
        """Set up Unix socket for receiving messages."""
        # Clean up any existing socket
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.socket_path)
        self.sock.listen(5)
        os.chmod(self.socket_path, 0o666)
        print(f"[CI Wrapper] Listening on {self.socket_path}", file=sys.stderr)

        # Register with CI registry
        self.register_ci()

    def register_ci(self):
        """Register this CI terminal with the registry."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from shared.aish.src.registry.ci_registry import get_registry

            registry = get_registry()
            ci_info = {
                'name': self.name,
                'type': 'ci_terminal',
                'socket': self.socket_path,
                'working_directory': os.getcwd(),
                'capabilities': ['messaging', 'minimal_pty_injection'],
                'pid': os.getpid()
            }
            registry.register_wrapped_ci(ci_info)
            print(f"[CI Wrapper] Registered {self.name} as ci_terminal", file=sys.stderr)
        except Exception as e:
            print(f"[CI Wrapper] Failed to register: {e}", file=sys.stderr)

    def unregister_ci(self):
        """Unregister this CI from the registry."""
        try:
            from shared.aish.src.registry.ci_registry import get_registry

            registry = get_registry()
            registry.unregister_wrapped_ci(self.name)
            print(f"[CI Wrapper] Unregistered {self.name}", file=sys.stderr)
        except Exception as e:
            print(f"[CI Wrapper] Failed to unregister: {e}", file=sys.stderr)

    def socket_listener(self):
        """Listen for messages and inject to PTY master."""
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
                    print(f"[CI Wrapper] Error receiving data: {e}", file=sys.stderr)
                    conn.close()
                    continue

                if data and self.master_fd:
                    try:
                        message = json.loads(data)
                    except json.JSONDecodeError as e:
                        print(f"[CI Wrapper] Invalid JSON: {e}", file=sys.stderr)
                        continue

                    # Extract message details
                    from_ci = message.get('from', 'unknown')
                    # Handle both 'message' and 'content' keys for compatibility
                    content = message.get('message') or message.get('content', '')
                    # Handle both 'use_delimiter' and 'execute' for compatibility
                    use_delimiter = message.get('use_delimiter', False) or message.get('execute', False)

                    # Format the injection
                    if use_delimiter:
                        # Use message delimiter if provided, otherwise wrapper delimiter, otherwise newline
                        delimiter = message.get('delimiter', self.delimiter or '\n')
                        injection = content + delimiter
                        print(f"[CI Wrapper] Executing command from {from_ci} with delimiter", file=sys.stderr)
                    else:
                        # Format as message notification
                        injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                        print(f"[CI Wrapper] Injected message from {from_ci}", file=sys.stderr)

                    # Inject to PTY master - this goes to the child's stdin
                    try:
                        os.write(self.master_fd, injection.encode('utf-8'))
                    except OSError as e:
                        print(f"[CI Wrapper] Failed to inject to PTY: {e}", file=sys.stderr)
                        if e.errno == 5:  # I/O error - child probably died
                            self.running = False

            except Exception as e:
                if self.running:
                    print(f"[CI Wrapper] Socket listener error: {e}", file=sys.stderr)

    def run(self):
        """Run the wrapper with minimal PTY handling."""
        # Set up signal handlers
        def cleanup_handler(signum, frame):
            print(f"\n[CI Wrapper] Received signal {signum}, cleaning up...", file=sys.stderr)
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)

        try:
            # Set up socket first (before fork)
            self.setup_socket()

            # Create PTY and fork
            self.child_pid, self.master_fd = pty.fork()

            if self.child_pid == 0:
                # Child process - just exec the command
                # The child inherits the slave side of the PTY as its stdin/stdout/stderr
                os.execvp(self.command[0], self.command)
            else:
                # Parent process - only handle socket listening and injection
                print(f"[CI Wrapper] Started child PID {self.child_pid}", file=sys.stderr)

                # Start socket listener in background thread
                listener_thread = threading.Thread(target=self.socket_listener, daemon=True)
                listener_thread.start()

                # We need to relay PTY output to stdout and stdin to PTY
                # Otherwise the terminal appears frozen
                import select
                import termios
                import tty

                # Save terminal settings
                old_tty = None
                try:
                    if sys.stdin.isatty():
                        old_tty = termios.tcgetattr(sys.stdin)
                        tty.setraw(sys.stdin.fileno())
                except:
                    pass

                try:
                    while True:
                        # Check for I/O
                        r, w, e = select.select([self.master_fd, sys.stdin], [], [], 0.1)

                        if self.master_fd in r:
                            try:
                                data = os.read(self.master_fd, 10240)
                                if data:
                                    os.write(sys.stdout.fileno(), data)
                                else:
                                    break  # EOF
                            except OSError:
                                break

                        if sys.stdin in r:
                            try:
                                data = os.read(sys.stdin.fileno(), 10240)
                                if data:
                                    os.write(self.master_fd, data)
                                else:
                                    break  # EOF
                            except OSError:
                                break

                        # Check if child is still alive
                        pid, status = os.waitpid(self.child_pid, os.WNOHANG)
                        if pid != 0:
                            exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1
                            print(f"\n[CI Wrapper] Child process {pid} exited with code {exit_code}", file=sys.stderr)
                            break

                finally:
                    # Restore terminal settings
                    if old_tty:
                        try:
                            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
                        except:
                            pass

        except Exception as e:
            print(f"[CI Wrapper] Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        self.running = False

        # Unregister from CI registry
        self.unregister_ci()

        # Close master FD
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass

        # Close socket
        try:
            self.sock.close()
        except:
            pass

        # Remove socket file
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
                print(f"[CI Wrapper] Removed socket {self.socket_path}", file=sys.stderr)
            except:
                pass

        print(f"[CI Wrapper] Cleanup completed", file=sys.stderr)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ci_pty_minimal.py [--name NAME] [--delimiter DELIM] -- command...", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    name = None
    delimiter = None
    command = []
    parsing_command = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if parsing_command:
            command.append(arg)
        elif arg == "--":
            parsing_command = True
        elif arg in ["--name", "-n"] and i + 1 < len(sys.argv):
            name = sys.argv[i + 1]
            i += 1
        elif arg in ["--delimiter", "-d"] and i + 1 < len(sys.argv):
            delimiter = sys.argv[i + 1]
            # Interpret escape sequences
            delimiter = delimiter.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
            i += 1
        elif arg == "--injection-info":
            print("Injection: Minimal PTY (direct to master fd)")
            sys.exit(0)
        i += 1

    if not command:
        print("Error: No command specified", file=sys.stderr)
        sys.exit(1)

    if not name:
        # Generate a default name if not provided
        import random
        name = f"ci_{random.randint(1000, 9999)}"
        print(f"[CI Wrapper] Using auto-generated name: {name}", file=sys.stderr)

    # Check for name uniqueness
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from shared.aish.src.registry.ci_registry import get_registry

    registry = get_registry()
    if registry.get_by_name(name):
        print(f"Error: '{name}' already exists in CI registry", file=sys.stderr)
        print("Please use a unique name", file=sys.stderr)
        sys.exit(1)

    # Create and run wrapper
    wrapper = MinimalPTYWrapper(name, command, delimiter)
    wrapper.run()


if __name__ == "__main__":
    main()