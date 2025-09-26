#!/usr/bin/env python3
"""
Minimal CI wrapper for non-terminal tools - simple subprocess with stdin injection.
Parent process stays alive for socket listening, passes through stdout/stderr.
"""

import sys
import os
import subprocess
import socket
import json
import threading
import signal
import select
import time
from pathlib import Path
from datetime import datetime

class MinimalToolWrapper:
    def __init__(self, name, command, delimiter=None):
        self.name = name
        self.command = command
        self.delimiter = delimiter
        self.socket_path = f"/tmp/ci_msg_{name}.sock"
        self.process = None
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
        print(f"[CI Tool] Listening on {self.socket_path}", file=sys.stderr)

        # Register with CI registry
        self.register_ci()

    def register_ci(self):
        """Register this CI tool with the registry."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from shared.aish.src.registry.ci_registry import get_registry

            registry = get_registry()
            ci_info = {
                'name': self.name,
                'type': 'ci_tool',
                'socket': self.socket_path,
                'working_directory': os.getcwd(),
                'capabilities': ['messaging', 'minimal_stdin_injection'],
                'pid': os.getpid()
            }
            registry.register_wrapped_ci(ci_info)
            print(f"[CI Tool] Registered {self.name} as ci_tool", file=sys.stderr)
        except Exception as e:
            print(f"[CI Tool] Failed to register: {e}", file=sys.stderr)

    def unregister_ci(self):
        """Unregister this CI from the registry."""
        try:
            from shared.aish.src.registry.ci_registry import get_registry

            registry = get_registry()
            registry.unregister_wrapped_ci(self.name)
            print(f"[CI Tool] Unregistered {self.name}", file=sys.stderr)
        except Exception as e:
            print(f"[CI Tool] Failed to unregister: {e}", file=sys.stderr)

    def socket_listener(self):
        """Listen for messages and inject to process stdin."""
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
                    print(f"[CI Tool] Error receiving data: {e}", file=sys.stderr)
                    conn.close()
                    continue

                if data and self.process and self.process.stdin:
                    try:
                        message = json.loads(data)
                    except json.JSONDecodeError as e:
                        print(f"[CI Tool] Invalid JSON: {e}", file=sys.stderr)
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
                        print(f"[CI Tool] Executing command from {from_ci} with delimiter", file=sys.stderr)
                    else:
                        # Format as message notification
                        injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                        print(f"[CI Tool] Injected message from {from_ci}", file=sys.stderr)

                    # Inject to process stdin
                    try:
                        self.process.stdin.write(injection.encode('utf-8'))
                        self.process.stdin.flush()
                    except (BrokenPipeError, OSError) as e:
                        print(f"[CI Tool] Failed to inject to stdin: {e}", file=sys.stderr)
                        self.running = False

            except Exception as e:
                if self.running:
                    print(f"[CI Tool] Socket listener error: {e}", file=sys.stderr)

    def stdout_reader(self):
        """Read process stdout and pass through."""
        try:
            for line in iter(self.process.stdout.readline, b''):
                if line:
                    sys.stdout.buffer.write(line)
                    sys.stdout.flush()
        except Exception as e:
            if self.running:
                print(f"[CI Tool] Stdout reader error: {e}", file=sys.stderr)

    def stderr_reader(self):
        """Read process stderr and pass through."""
        try:
            for line in iter(self.process.stderr.readline, b''):
                if line:
                    sys.stderr.buffer.write(line)
                    sys.stderr.flush()
        except Exception as e:
            if self.running:
                print(f"[CI Tool] Stderr reader error: {e}", file=sys.stderr)

    def run(self):
        """Run the wrapper with minimal subprocess handling."""
        # Set up signal handlers
        def cleanup_handler(signum, frame):
            print(f"\n[CI Tool] Received signal {signum}, cleaning up...", file=sys.stderr)
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)

        try:
            # Set up socket first
            self.setup_socket()

            # Start the subprocess with pipes for stdin/stdout/stderr
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # Unbuffered
            )

            print(f"[CI Tool] Started process PID {self.process.pid}", file=sys.stderr)

            # Start threads for socket listener and output readers
            listener_thread = threading.Thread(target=self.socket_listener, daemon=True)
            stdout_thread = threading.Thread(target=self.stdout_reader, daemon=True)
            stderr_thread = threading.Thread(target=self.stderr_reader, daemon=True)

            listener_thread.start()
            stdout_thread.start()
            stderr_thread.start()

            # Wait for process to exit
            exit_code = self.process.wait()
            print(f"[CI Tool] Process exited with code {exit_code}", file=sys.stderr)

        except Exception as e:
            print(f"[CI Tool] Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        self.running = False

        # Terminate subprocess if still running
        if self.process:
            try:
                self.process.terminate()
                time.sleep(0.5)
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass

        # Unregister from CI registry
        self.unregister_ci()

        # Close socket
        try:
            self.sock.close()
        except:
            pass

        # Remove socket file
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
                print(f"[CI Tool] Removed socket {self.socket_path}", file=sys.stderr)
            except:
                pass

        print(f"[CI Tool] Cleanup completed", file=sys.stderr)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ci_tool_minimal.py [--name NAME] [--delimiter DELIM] -- command...", file=sys.stderr)
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
        i += 1

    if not command:
        print("Error: No command specified", file=sys.stderr)
        sys.exit(1)

    if not name:
        # Generate a default name if not provided
        import random
        name = f"tool_{random.randint(1000, 9999)}"
        print(f"[CI Tool] Using auto-generated name: {name}", file=sys.stderr)

    # Check for name uniqueness
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from shared.aish.src.registry.ci_registry import get_registry

    registry = get_registry()
    # Check and clean up dead entries like ci_terminal does
    existing = registry.get_by_name(name)
    if existing:
        # Check if it's actually alive
        pid = existing.get('pid')
        socket_path = existing.get('socket')
        is_alive = False

        if pid:
            try:
                os.kill(pid, 0)  # Check if process exists
                is_alive = True
            except (ProcessLookupError, PermissionError):
                is_alive = False

        # If it's dead, unregister it
        if not is_alive or not (socket_path and os.path.exists(socket_path)):
            print(f"[CI Tool] Cleaning up dead entry for '{name}' (PID {pid})", file=sys.stderr)
            registry.unregister_wrapped_ci(name)
        else:
            print(f"Error: '{name}' already exists in CI registry (PID {pid} is active)", file=sys.stderr)
            print("Please use a unique name", file=sys.stderr)
            sys.exit(1)

    # Create and run wrapper
    wrapper = MinimalToolWrapper(name, command, delimiter)
    wrapper.run()


if __name__ == "__main__":
    main()