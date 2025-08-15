"""
CI Tool wrapper command handler for aish.
Launches wrapped CI terminals with aish messaging support.
"""

import sys
import os
import subprocess
from pathlib import Path

def handle_ci_tool_command(args):
    """
    Handle ci-tool command to launch simple wrapped processes.
    
    Usage:
      aish ci-tool --name <name> -- <command...>
    
    Examples:
      aish ci-tool --name processor -- python script.py
      aish ci-tool --name logger -- node app.js
    """
    # Find where 'ci-tool' appears in argv
    try:
        ci_tool_idx = sys.argv.index('ci-tool')
        # Get all args after 'ci-tool'
        ci_tool_args = sys.argv[ci_tool_idx + 1:]
    except ValueError:
        # Shouldn't happen but handle gracefully
        ci_tool_args = args or []
    
    if not ci_tool_args or (ci_tool_args and ci_tool_args[0] in ['help', '-h', '--help']):
        show_ci_tool_help()
        return True
    
    # Build the command to execute the simple wrapper
    wrapper_path = Path(__file__).parent.parent / 'ci_simple_wrapper.py'
    
    if not wrapper_path.exists():
        print(f"Error: Simple wrapper not found at {wrapper_path}")
        return
    
    # Extract name and delimiter from arguments
    name = None
    delimiter = None
    for i, arg in enumerate(ci_tool_args):
        if arg in ['--name', '-n'] and i + 1 < len(ci_tool_args):
            name = ci_tool_args[i + 1]
        elif arg in ['--delimiter', '-d'] and i + 1 < len(ci_tool_args):
            delimiter = ci_tool_args[i + 1]
    
    # Set TEKTON_CI_NAME environment variable if name was provided
    env = os.environ.copy()
    if name:
        env['TEKTON_CI_NAME'] = name
    
    # Pass all arguments directly to simple wrapper
    cmd = [sys.executable, str(wrapper_path)] + ci_tool_args
    
    try:
        # Execute wrapper with the environment
        os.execvpe(cmd[0], cmd, env)
    except Exception as e:
        print(f"Error launching ci-tool: {e}")
        sys.exit(1)


def show_ci_tool_help():
    """Show help for ci-tool command."""
    print("""CI Tool - Simple Process Wrapper with Message Injection

Usage:
  aish ci-tool --name <name> [--delimiter <string>] -- <command...>

Options:
  -n, --name <name>          Required. Name for this process's message socket
  -d, --delimiter <string>   Optional. Default delimiter for auto-execution

Examples:
  # Launch Python script with message injection
  aish ci-tool --name processor -- python data_processor.py
  aish ci-tool -n processor -d "\\n" -- python data_processor.py
  
  # Launch Node.js application
  aish ci-tool --name server -- node server.js
  aish ci-tool -n server --delimiter "\\n\\n" -- node server.js
  
  # Launch any command-line tool
  aish ci-tool --name analyzer -- ./analyze_data.sh
  
  # Background execution with output capture
  aish ci-tool -n processor -- python script.py &
  aish ci-tool -n server -- node server.js 2>&1 | tee server.log &

Messaging:
  Once launched, messages can be injected into the process's stdin:
    ./send_test_message.py <name> <from> <message>
  
  Example:
    # In another terminal:
    ./send_test_message.py processor control "START_BATCH_JOB"
    
    # The processor sees on stdin:
    [15:23] Message from control: START_BATCH_JOB

Notes:
  - Uses subprocess with stdin pipe control
  - Messages are injected into the process's stdin stream
  - Suitable for non-terminal programs and scripts
  - For terminal programs (like Claude, bash), use 'aish ci-terminal' instead
""")