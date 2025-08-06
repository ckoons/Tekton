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
    
    # Pass all arguments directly to simple wrapper
    cmd = [sys.executable, str(wrapper_path)] + ci_tool_args
    
    try:
        # Execute wrapper in a subprocess
        os.execvp(cmd[0], cmd)
    except Exception as e:
        print(f"Error launching ci-tool: {e}")
        sys.exit(1)


def show_ci_tool_help():
    """Show help for ci-tool command."""
    print("""CI Tool - Simple Process Wrapper with Message Injection

Usage:
  aish ci-tool --name <name> -- <command...>

Options:
  --name <name>     Required. Name for this process's message socket

Examples:
  # Launch Python script with message injection
  aish ci-tool --name processor -- python data_processor.py
  
  # Launch Node.js application
  aish ci-tool --name server -- node server.js
  
  # Launch any command-line tool
  aish ci-tool --name analyzer -- ./analyze_data.sh

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