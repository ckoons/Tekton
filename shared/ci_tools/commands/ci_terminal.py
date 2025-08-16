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
    
    # Extract name, delimiter, and OS injection setting from arguments
    name = None
    delimiter = None
    os_injection = None
    injection_info = False
    for i, arg in enumerate(ci_terminal_args):
        if arg in ['--name', '-n'] and i + 1 < len(ci_terminal_args):
            name = ci_terminal_args[i + 1]
        elif arg in ['--delimiter', '-d'] and i + 1 < len(ci_terminal_args):
            delimiter = ci_terminal_args[i + 1]
        elif arg == '--os-injection' and i + 1 < len(ci_terminal_args):
            os_injection = ci_terminal_args[i + 1]
        elif arg == '--injection-info':
            injection_info = True
    
    # If injection info requested, pass it through to the wrapper
    if injection_info:
        wrapper_path = Path(__file__).parent.parent / 'ci_pty_wrapper.py'
        cmd = [sys.executable, str(wrapper_path), '--injection-info']
        os.execvp(cmd[0], cmd)
        return
    
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
    
    # Set TEKTON_CI_NAME environment variable if name was provided
    env = os.environ.copy()
    if name:
        env['TEKTON_CI_NAME'] = name
    
    # Pass all arguments directly to PTY wrapper
    cmd = [sys.executable, str(wrapper_path)] + ci_terminal_args
    
    try:
        # Execute wrapper with the environment
        os.execvpe(cmd[0], cmd, env)
    except Exception as e:
        print(f"Error launching ci-terminal: {e}")
        sys.exit(1)


def show_ci_terminal_help():
    """Show help for ci-terminal command."""
    print("""CI Terminal - PTY-based Terminal Wrapper with Message Injection

Usage:
  aish ci-terminal --name <name> [options] -- <command...>

Options:
  -n, --name <name>          Required. Name for this terminal's message socket
  -d, --delimiter <string>   Optional. Default delimiter for auto-execution
  --os-injection {on,off,auto}  OS-level keystroke injection (default: auto)
  --injection-info          Show OS injection capabilities and exit

Examples:
  # Launch Claude with OS injection (auto-detected)
  aish ci-terminal --name wilma-ci -- claude
  aish ci-terminal -n claude-ci -d "\\n" -- claude
  
  # Force OS injection on for a program
  aish ci-terminal -n vim-ci --os-injection on -- vim
  
  # Force OS injection off (use PTY only)
  aish ci-terminal --name bash-ci --os-injection off -- bash
  
  # Launch Python REPL with double newline delimiter
  aish ci-terminal --name python-ci -d "\\n\\n" -- python3
  
  # Check OS injection capabilities
  aish ci-terminal --injection-info
  
  # Background execution
  aish ci-terminal -n claude-ci -- claude &

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