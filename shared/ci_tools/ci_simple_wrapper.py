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
from typing import Optional

# Import OS injection module
try:
    # Try relative import first (when used as module)
    from .os_injection import (
        OSInjector, 
        should_use_os_injection,
        inject_message_with_delimiter,
        get_injection_info
    )
    OS_INJECTION_AVAILABLE = True
except ImportError:
    try:
        # Try absolute import (when run directly)
        from os_injection import (
            OSInjector, 
            should_use_os_injection,
            inject_message_with_delimiter,
            get_injection_info
        )
        OS_INJECTION_AVAILABLE = True
    except ImportError:
        OS_INJECTION_AVAILABLE = False

class SimpleWrapper:
    def __init__(self, name, command, delimiter=None, use_os_injection=None):
        self.name = name
        self.command = command
        self.delimiter = delimiter  # Store default delimiter for auto-execution
        self.socket_path = f"/tmp/ci_msg_{name}.sock"  # Use same pattern as PTY wrapper
        self.process = None
        self.running = True
        
        # Determine if we should use OS injection
        if OS_INJECTION_AVAILABLE:
            prog_name = command[0] if command else ''
            self.use_os_injection = should_use_os_injection(prog_name, use_os_injection)
            if self.use_os_injection:
                self.injector = OSInjector()
                if not self.injector.is_available():
                    print(f"[Wrapper] OS injection requested but not available", file=sys.stderr)
                    self.use_os_injection = False
                else:
                    print(f"[Wrapper] OS injection enabled for {prog_name}", file=sys.stderr)
        else:
            self.use_os_injection = False
        
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
                    use_os_injection = message.get('os_injection', None)  # Allow per-message override
                    
                    # Check if we should append delimiter for execution
                    if execute:
                        # Use message delimiter, wrapper delimiter, or default to \n
                        raw_delimiter = message.get('delimiter', self.delimiter or '\n')
                        # Decode escape sequences in delimiter
                        try:
                            delimiter = raw_delimiter.encode('utf-8').decode('unicode_escape')
                        except:
                            delimiter = raw_delimiter
                        
                        # Determine injection method for this message
                        should_inject = use_os_injection if use_os_injection is not None else self.use_os_injection
                        
                        if should_inject and OS_INJECTION_AVAILABLE:
                            # Use OS-level injection
                            if inject_message_with_delimiter(content, delimiter, True):
                                print(f"[Wrapper] OS-injected command from {from_ci}", file=sys.stderr)
                            else:
                                # Fallback to stdin injection if OS injection fails
                                print(f"[Wrapper] OS injection failed, using stdin", file=sys.stderr)
                                injection = content + delimiter
                                self.process.stdin.write(injection.encode('utf-8'))
                                self.process.stdin.flush()
                        else:
                            # Use normal stdin injection
                            injection = content + delimiter
                            self.process.stdin.write(injection.encode('utf-8'))
                            self.process.stdin.flush()
                            print(f"[Wrapper] Stdin-injected command from {from_ci}", file=sys.stderr)
                    else:
                        # Format as message notification (always use stdin for notifications)
                        injection = f"\n[{datetime.now().strftime('%H:%M')}] Message from {from_ci}: {content}\n"
                        self.process.stdin.write(injection.encode('utf-8'))
                        self.process.stdin.flush()
                        print(f"[Wrapper] Injected message from {from_ci}", file=sys.stderr)
                    
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
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple CI wrapper with stdin injection')
    parser.add_argument('--name', '-n', help='CI name for socket')
    parser.add_argument('--delimiter', '-d', default=None, help='Default delimiter for auto-execution')
    parser.add_argument('--os-injection', choices=['on', 'off', 'auto'], default='auto',
                       help='OS-level keystroke injection mode (default: auto)')
    parser.add_argument('--injection-info', action='store_true',
                       help='Show OS injection capabilities and exit')
    parser.add_argument('command', nargs='*', help='Command to wrap')
    
    args = parser.parse_args()
    
    # Show injection info if requested
    if args.injection_info:
        if OS_INJECTION_AVAILABLE:
            info = get_injection_info()
            print(f"OS Injection Available: {info['available']}")
            print(f"Platform: {info['platform']}")
            print(f"Method: {info['method']}")
            print(f"Auto-detected TUI Programs: {', '.join(info['tui_programs'])}")
        else:
            print("OS injection module not available")
        sys.exit(0)
    
    # Require command and name if not showing info
    if not args.command:
        parser.error("command is required unless using --injection-info")
    if not args.name:
        parser.error("--name/-n is required when running a command")
    
    # Decode escape sequences in delimiter if provided
    if args.delimiter:
        try:
            args.delimiter = args.delimiter.encode('utf-8').decode('unicode_escape')
        except:
            pass  # Keep original if decoding fails
    
    # Parse OS injection preference
    use_os_injection = None if args.os_injection == 'auto' else (args.os_injection == 'on')
    
    wrapper = SimpleWrapper(args.name, args.command, args.delimiter, use_os_injection)
    wrapper.run()

if __name__ == "__main__":
    main()