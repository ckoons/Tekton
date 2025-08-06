"""
CI Terminal command handler for aish.
Launches terminal programs with PTY-based message injection.
"""

import sys
import os
from pathlib import Path

def handle_ci_terminal_command(args):
    """
    Handle ci-terminal command to launch PTY-wrapped terminals.
    
    Usage:
      aish ci-terminal --name <name> -- <command...>
    
    Examples:
      aish ci-terminal --name wilma-ci -- claude
      aish ci-terminal --name casey -- bash
    """
    # Find where 'ci-terminal' appears in argv
    try:
        ci_terminal_idx = sys.argv.index('ci-terminal')
        # Get all args after 'ci-terminal'
        ci_terminal_args = sys.argv[ci_terminal_idx + 1:]
    except ValueError:
        # Shouldn't happen but handle gracefully
        ci_terminal_args = args or []
    
    if not ci_terminal_args or (ci_terminal_args and ci_terminal_args[0] in ['help', '-h', '--help']):
        show_ci_terminal_help()
        return True
    
    # Extract name from arguments to check uniqueness
    name = None
    for i, arg in enumerate(ci_terminal_args):
        if arg == '--name' and i + 1 < len(ci_terminal_args):
            name = ci_terminal_args[i + 1]
            break
    
    # Check name uniqueness if provided
    if name:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from shared.aish.src.registry.ci_registry import get_registry
        
        registry = get_registry()
        if registry.get_by_name(name):
            print(f"Error: '{name}' already exists in CI registry")
            print("Please use a unique name")
            sys.exit(1)
    
    # Build the command to execute the PTY wrapper
    wrapper_path = Path(__file__).parent.parent / 'ci_pty_wrapper.py'
    
    if not wrapper_path.exists():
        print(f"Error: PTY wrapper not found at {wrapper_path}")
        return
    
    # Pass all arguments directly to PTY wrapper
    cmd = [sys.executable, str(wrapper_path)] + ci_terminal_args
    
    try:
        # Execute wrapper in a subprocess
        os.execvp(cmd[0], cmd)
    except Exception as e:
        print(f"Error launching ci-terminal: {e}")
        sys.exit(1)


def show_ci_terminal_help():
    """Show help for ci-terminal command."""
    print("""CI Terminal - PTY-based Terminal Wrapper with Message Injection

Usage:
  aish ci-terminal --name <name> -- <command...>

Options:
  --name <name>     Required. Name for this terminal's message socket

Examples:
  # Launch Claude with message injection
  aish ci-terminal --name wilma-ci -- claude
  
  # Launch bash with message injection
  aish ci-terminal --name casey -- bash
  
  # Launch Python REPL
  aish ci-terminal --name python-ci -- python3

Messaging:
  Once launched, you can inject messages using:
    aish send-test-message.py <name> <from> <message>
  
  Or programmatically from other scripts/wrappers.
  
  Example:
    # In another terminal:
    ./send_test_message.py wilma-ci alice "Hello Wilma!"
    
    # Wilma's terminal shows:
    [15:23] Message from alice: Hello Wilma!

Notes:
  - Uses PTY (pseudo-terminal) for proper terminal program support
  - Messages are injected directly into the terminal's input stream
  - Suitable for interactive programs like Claude, bash, Python REPL
  - For non-terminal programs, use 'aish ci-tool' instead
""")