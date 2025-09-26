#!/usr/bin/env python3
"""
Simple CI wrapper for terminal programs - pure injection mechanism.
Uses tmux to manage the terminal and only injects messages via socket.
"""

import sys
import os
import socket
import json
import threading
import signal
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Import hook system if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from shared.ci_tools.ci_wrapper_hooks import CIHookSystem
    hooks_available = True
except ImportError:
    hooks_available = False

class SimpleWrapper:
    def __init__(self, name, command, delimiter=None, enable_hooks=True):
        self.name = name
        self.command = command
        self.delimiter = delimiter
        self.socket_path = f"/tmp/ci_msg_{name}.sock"
        self.tmux_session = f"ci_{name}"
        self.running = True
        self.enable_hooks = enable_hooks and hooks_available

        # Initialize hook system if needed
        if self.enable_hooks:
            self.hook_system = CIHookSystem(name)

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
            from shared.aish.src.registry.ci_registry import get_registry

            registry = get_registry()
            ci_info = {
                'name': self.name,
                'type': 'ci_terminal',
                'socket': self.socket_path,
                'working_directory': os.getcwd(),
                'capabilities': ['messaging', 'tmux_injection'],
                'pid': os.getpid(),
                'tmux_session': self.tmux_session
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
        """Listen for messages and inject to tmux session."""
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

                if data:
                    try:
                        message = json.loads(data)
                    except json.JSONDecodeError as e:
                        print(f"[CI Wrapper] Invalid JSON: {e}", file=sys.stderr)
                        continue

                    # Extract message details
                    from_ci = message.get('from', 'unknown')
                    content = message.get('message', '')
                    use_delimiter = message.get('use_delimiter', False)

                    # Format the injection
                    if use_delimiter and self.delimiter:
                        # Auto-execute with delimiter
                        injection = content + self.delimiter
                        print(f"[CI Wrapper] Executing command from {from_ci} with delimiter", file=sys.stderr)
                    else:
                        # Format as message notification
                        injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                        print(f"[CI Wrapper] Injected message from {from_ci}", file=sys.stderr)

                    # Inject to tmux session
                    self.inject_to_tmux(injection)

            except Exception as e:
                if self.running:
                    print(f"[CI Wrapper] Socket listener error: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()

    def inject_to_tmux(self, text):
        """Inject text to the tmux session."""
        try:
            # Use tmux send-keys to inject text
            # -l flag means literal (don't interpret keys)
            subprocess.run([
                "tmux", "send-keys", "-t", self.tmux_session, "-l", text
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[CI Wrapper] Failed to inject to tmux: {e}", file=sys.stderr)

    def start_tmux_session(self):
        """Start the command in a tmux session."""
        # Check if tmux session already exists
        result = subprocess.run(
            ["tmux", "has-session", "-t", self.tmux_session],
            capture_output=True
        )

        if result.returncode == 0:
            # Session exists, kill it first
            print(f"[CI Wrapper] Killing existing tmux session {self.tmux_session}", file=sys.stderr)
            subprocess.run(["tmux", "kill-session", "-t", self.tmux_session], capture_output=True)
            time.sleep(0.5)

        # Create new tmux session with the command
        cmd = " ".join(self.command)
        print(f"[CI Wrapper] Starting tmux session {self.tmux_session} with: {cmd}", file=sys.stderr)

        # Start detached tmux session
        subprocess.run([
            "tmux", "new-session", "-d", "-s", self.tmux_session,
            cmd
        ], check=True)

        print(f"[CI Wrapper] Started tmux session {self.tmux_session}", file=sys.stderr)

    def attach_to_tmux(self):
        """Attach the user to the tmux session."""
        print(f"[CI Wrapper] Attaching to tmux session {self.tmux_session}", file=sys.stderr)

        # Replace current process with tmux attach
        os.execvp("tmux", ["tmux", "attach-session", "-t", self.tmux_session])

    def run(self):
        """Run the wrapper."""
        # Set up signal handlers
        def cleanup_handler(signum, frame):
            print(f"\n[CI Wrapper] Received signal {signum}, cleaning up...", file=sys.stderr)
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)

        try:
            # Start tmux session
            self.start_tmux_session()

            # Set up socket
            self.setup_socket()

            # Start socket listener in background
            listener_thread = threading.Thread(target=self.socket_listener, daemon=True)
            listener_thread.start()

            # Give tmux a moment to start
            time.sleep(0.5)

            # Attach to tmux session (this replaces our process)
            self.attach_to_tmux()

        except Exception as e:
            print(f"[CI Wrapper] Error: {e}", file=sys.stderr)
            self.cleanup()
            sys.exit(1)

    def cleanup(self):
        """Clean up resources."""
        self.running = False

        # Unregister from CI registry
        self.unregister_ci()

        # Close socket
        try:
            self.sock.close()
        except:
            pass

        # Remove socket file
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
            print(f"[CI Wrapper] Removed socket {self.socket_path}", file=sys.stderr)

        print(f"[CI Wrapper] Cleaned up", file=sys.stderr)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ci_pty_wrapper_simple.py [--name NAME] [--delimiter DELIM] [--os-injection MODE] -- command...", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    name = "default"
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
            print("OS injection: tmux (always available)")
            sys.exit(0)
        elif arg == "--os-injection":
            # Ignored for compatibility
            i += 1
        i += 1

    if not command:
        print("Error: No command specified", file=sys.stderr)
        sys.exit(1)

    # Create and run wrapper
    wrapper = SimpleWrapper(name, command, delimiter)
    wrapper.run()


if __name__ == "__main__":
    main()