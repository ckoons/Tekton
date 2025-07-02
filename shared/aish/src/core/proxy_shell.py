#!/usr/bin/env python3
"""
aish Transparent Proxy Shell
The "inner-brain" enhancement that makes terminals smarter without changing the interface.

Philosophy: Enhance don't change. Like middleware that sits invisibly between
user and system, intercepting only when AI assistance is needed.
"""

import os
import sys
import subprocess
import signal
import re
import select
import threading
import time
from typing import Optional, List, Tuple
from pathlib import Path

from parser.pipeline import PipelineParser
from registry.socket_registry import SocketRegistry
from core.history import AIHistory


class TransparentAishProxy:
    """
    Transparent shell proxy that enhances terminal with AI capabilities.
    
    Acts as middleware between user and base shell:
    - Intercepts AI pipeline commands (echo "test" | apollo)
    - Passes through everything else transparently (ls, git, npm, etc.)
    - Maintains full shell compatibility and TTY behavior
    """
    
    def __init__(self, rhetor_endpoint=None, debug=False, base_shell=None):
        # Initialize AI components
        if rhetor_endpoint:
            self.rhetor_endpoint = rhetor_endpoint
        else:
            port = os.environ.get('TEKTON_RHETOR_PORT', '8003')
            self.rhetor_endpoint = f"http://localhost:{port}"
        
        self.debug = debug
        self.parser = PipelineParser()
        self.registry = SocketRegistry(self.rhetor_endpoint, debug=debug)
        self.ai_history = AIHistory()
        
        # Shell configuration
        self.base_shell = base_shell or os.environ.get("SHELL", "/bin/bash")
        self.active_sockets = {}
        
        # State tracking
        self.context = {
            "pwd": os.getcwd(),
            "env": os.environ.copy(),
            "last_exit_code": 0
        }
        
        # AI detection patterns
        self.ai_patterns = self._compile_ai_patterns()
        
        if self.debug:
            print(f"[aish-proxy] Initialized with base shell: {self.base_shell}")
            print(f"[aish-proxy] Rhetor endpoint: {self.rhetor_endpoint}")
    
    def _compile_ai_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns that indicate AI command intent."""
        patterns = [
            # Explicit AI commands
            r"^ai:",
            r"^@ai\b",
            
            # AI pipeline patterns (ai_name in pipe)
            r"\|\s*(apollo|athena|rhetor|sophia|hermes|prometheus|telos|ergon|engram|numa|noesis)\b",
            r"\b(apollo|athena|rhetor|sophia|hermes|prometheus|telos|ergon|engram|numa|noesis)\s*\|",
            
            # Team chat
            r"^team-chat\b",
            
            # Natural language patterns
            r"^(show me|tell me|what is|what are|find)",
            r"^(how do i|how to|help me)",
            r"^(explain|analyze|debug|fix)",
            r"(please|could you|can you)\b.*\?",
            r"\?\s*$",  # Questions ending with ?
            
            # Echo to AI pattern
            r"echo\s+[\"'].*[\"']\s*\|\s*(apollo|athena|rhetor|sophia|hermes|prometheus|telos|ergon|engram|numa|noesis)"
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def should_intercept(self, command: str) -> bool:
        """
        Determine if command should be handled by AI system or passed to shell.
        
        Returns True for AI commands, False for normal shell commands.
        """
        command = command.strip()
        
        # Empty commands go to shell
        if not command:
            return False
        
        # Check against AI patterns
        for pattern in self.ai_patterns:
            if pattern.search(command):
                if self.debug:
                    print(f"[aish-proxy] AI pattern matched: {pattern.pattern}")
                return True
        
        # Check for complex natural language (heuristic)
        word_count = len(command.split())
        if word_count > 5 and not command.startswith(("/", ".", "sudo", "cd")):
            # Likely natural language, but check for common shell patterns first
            shell_indicators = ["ls", "cd", "git", "npm", "make", "docker", "kubectl", "ssh"]
            if not any(cmd in command.lower() for cmd in shell_indicators):
                if self.debug:
                    print(f"[aish-proxy] Natural language detected: {command}")
                return True
        
        return False
    
    def execute_shell_command(self, command: str) -> int:
        """
        Execute command in base shell with full transparency.
        
        This maintains TTY behavior, signals, and all shell features.
        """
        try:
            if self.debug:
                print(f"[aish-proxy] Passing to shell: {command}")
            
            # Execute in base shell with full TTY passthrough
            process = subprocess.Popen(
                [self.base_shell, "-c", command],
                cwd=self.context["pwd"],
                env=self.context["env"],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                preexec_fn=os.setsid  # Create process group for signal handling
            )
            
            # Wait for completion
            exit_code = process.wait()
            self.context["last_exit_code"] = exit_code
            
            # Update working directory if it might have changed
            self._sync_working_directory()
            
            return exit_code
            
        except KeyboardInterrupt:
            # Forward Ctrl+C to child process
            if process.poll() is None:
                os.killpg(os.getpgid(process.pid), signal.SIGINT)
            return 130  # Standard exit code for Ctrl+C
        except Exception as e:
            print(f"aish: shell error: {e}", file=sys.stderr)
            return 1
    
    def execute_ai_command(self, command: str) -> int:
        """Execute command through AI pipeline system."""
        try:
            if self.debug:
                print(f"[aish-proxy] Processing AI command: {command}")
            
            # Strip AI prefixes if present
            if command.startswith("ai:"):
                command = command[3:].strip()
            elif command.startswith("@ai"):
                command = command[3:].strip()
            
            # Parse and execute AI pipeline
            pipeline = self.parser.parse(command)
            
            if self.debug:
                print(f"[aish-proxy] Parsed pipeline: {pipeline}")
            
            # Execute pipeline and track responses
            result, responses = self._execute_ai_pipeline_with_tracking(pipeline)
            
            # Add to AI history if we got responses
            if responses:
                self.ai_history.add_command(command, responses)
            
            # Output result
            if result:
                print(result)
            
            return 0
            
        except Exception as e:
            print(f"aish: AI command error: {e}", file=sys.stderr)
            return 1
    
    def _execute_ai_pipeline_with_tracking(self, pipeline):
        """Execute AI pipeline and track responses (reuse existing logic)."""
        pipeline_type = pipeline.get('type')
        responses = {}
        
        if pipeline_type == 'team-chat':
            result = self._execute_team_chat(pipeline['message'])
            # Parse team chat responses (simplified)
            responses['team-chat'] = result
            return result, responses
            
        elif pipeline_type == 'pipeline':
            # Reuse existing pipeline execution logic
            from core.shell import AIShell
            temp_shell = AIShell(self.rhetor_endpoint, self.debug)
            result, responses = temp_shell._execute_pipe_stages_with_tracking(pipeline['stages'])
            return result, responses
            
        elif pipeline_type == 'simple':
            result = f"Simple AI command: {pipeline['command']}"
            return result, {}
            
        else:
            return f"Unsupported AI pipeline type: {pipeline_type}", {}
    
    def _execute_team_chat(self, message):
        """Execute team-chat broadcast."""
        self.registry.write("team-chat-all", message)
        responses = self.registry.read("team-chat-all")
        return '\n'.join(responses) if responses else "No responses yet"
    
    def _sync_working_directory(self):
        """Sync working directory with actual filesystem state."""
        try:
            # Get current working directory
            actual_pwd = os.getcwd()
            if actual_pwd != self.context["pwd"]:
                self.context["pwd"] = actual_pwd
                if self.debug:
                    print(f"[aish-proxy] Working directory synced: {actual_pwd}")
        except Exception:
            pass  # Ignore sync errors
    
    def handle_builtin_commands(self, command: str) -> Optional[int]:
        """
        Handle built-in aish commands that don't go to shell or AI.
        
        Returns exit code if handled, None if should be processed normally.
        """
        command = command.strip()
        
        if command == "exit":
            if self.debug:
                print("[aish-proxy] Exit requested")
            return 0
        
        elif command in ["aish-help", "aish --help"]:
            self._show_help()
            return 0
        
        elif command in ["aish-status", "aish --status"]:
            self._show_status()
            return 0
        
        elif command.startswith("cd "):
            # Handle cd specially to update context
            new_dir = command[3:].strip()
            try:
                os.chdir(new_dir)
                self.context["pwd"] = os.getcwd()
                return 0
            except Exception as e:
                print(f"cd: {e}", file=sys.stderr)
                return 1
        
        return None  # Not handled, continue normal processing
    
    def process_command(self, command: str) -> int:
        """
        Main command processing logic.
        
        The heart of the transparent proxy - decides whether to route
        to AI system or pass through to shell.
        """
        # Handle built-in commands first
        builtin_result = self.handle_builtin_commands(command)
        if builtin_result is not None:
            return builtin_result
        
        # Route based on content
        if self.should_intercept(command):
            return self.execute_ai_command(command)
        else:
            return self.execute_shell_command(command)
    
    def run_single_command(self, command: str) -> int:
        """Execute a single command and return exit code."""
        return self.process_command(command)
    
    def run_interactive(self):
        """
        Run interactive shell mode.
        
        This provides a basic REPL for testing the proxy concept.
        In production, this would be replaced by PTY integration.
        """
        print("aish transparent proxy - AI-enhanced shell")
        print(f"Base shell: {self.base_shell}")
        print("Type 'aish-help' for help, 'exit' to quit")
        print()
        
        while True:
            try:
                # Simple prompt (would be enhanced in production)
                pwd_display = os.path.basename(self.context["pwd"]) or self.context["pwd"]
                prompt = f"aish:{pwd_display}$ "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                exit_code = self.process_command(command)
                
                if command == "exit":
                    break
                    
            except KeyboardInterrupt:
                print()  # New line after ^C
                continue
            except EOFError:
                print()  # New line after ^D
                break
            except Exception as e:
                print(f"aish: unexpected error: {e}", file=sys.stderr)
    
    def _show_help(self):
        """Show help for the transparent proxy."""
        print("""
aish Transparent Proxy - AI-Enhanced Shell

The proxy automatically detects and routes commands:

AI Commands (routed to Tekton AI system):
  echo "analyze this code" | apollo
  team-chat "what should we optimize?"
  show me the git log
  how do I fix this error?

Shell Commands (passed through transparently):
  ls -la
  git status
  npm install
  cd /path/to/project

Built-in Commands:
  aish-help     - Show this help
  aish-status   - Show AI system status
  exit          - Exit aish proxy

The proxy enhances your terminal without changing normal shell behavior.
All standard commands, pipes, redirections work exactly as before.
""")
    
    def _show_status(self):
        """Show status of AI system connection."""
        print("aish Proxy Status:")
        print(f"  Base shell: {self.base_shell}")
        print(f"  Rhetor endpoint: {self.rhetor_endpoint}")
        print(f"  Working directory: {self.context['pwd']}")
        print(f"  Last exit code: {self.context['last_exit_code']}")
        
        # Test AI connection
        try:
            ais = self.registry.discover_ais(force_refresh=True)
            if ais:
                print(f"  AI specialists: {len(ais)} available")
            else:
                print("  AI specialists: None (check Rhetor connection)")
        except Exception as e:
            print(f"  AI specialists: Connection error - {e}")


def main():
    """Entry point for testing the transparent proxy."""
    import argparse
    
    parser = argparse.ArgumentParser(description="aish Transparent Proxy")
    parser.add_argument("-c", "--command", help="Execute single command")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--shell", help="Base shell to use", default=None)
    parser.add_argument("--rhetor", help="Rhetor endpoint", default=None)
    
    args = parser.parse_args()
    
    # Create proxy
    proxy = TransparentAishProxy(
        rhetor_endpoint=args.rhetor,
        debug=args.debug,
        base_shell=args.shell
    )
    
    if args.command:
        # Single command mode
        exit_code = proxy.run_single_command(args.command)
        sys.exit(exit_code)
    else:
        # Interactive mode
        proxy.run_interactive()


if __name__ == "__main__":
    main()