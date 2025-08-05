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
    Handle ci-tool command to launch wrapped CI terminals.
    
    Usage:
      aish ci-tool --name <name> [--ci <model>] [--dir <path>] -- <command...>
    
    Examples:
      aish ci-tool --name Casey --ci claude-opus-4 -- claude --debug
      aish ci-tool --name Betty-ci -- claude
    """
    if not args or args[0] in ['help', '-h', '--help']:
        show_ci_tool_help()
        return
    
    # Build the command to execute the actual ci-tool wrapper
    ci_tool_path = Path(__file__).parent.parent / 'ci-tool'
    
    if not ci_tool_path.exists():
        print(f"Error: ci-tool wrapper not found at {ci_tool_path}")
        return
    
    # Pass all arguments directly to ci-tool
    cmd = [str(ci_tool_path)] + args
    
    try:
        # Execute ci-tool in a subprocess
        # Use execvp to replace the current process
        os.execvp(cmd[0], cmd)
    except Exception as e:
        print(f"Error launching ci-tool: {e}")
        sys.exit(1)


def show_ci_tool_help():
    """Show help for ci-tool command."""
    print("""CI Tool - Wrapped CI Terminal with aish Messaging

Usage:
  aish ci-tool --name <name> [options] -- <command...>

Options:
  --name <name>     Required. Registry name for this CI (e.g., Casey, Betty-ci)
  --ci <model>      Optional. CI/model hint (e.g., claude-opus-4, llama3.3:70b)
  --dir <path>      Optional. Working directory (defaults to current directory)

Examples:
  # Launch Claude with messaging capabilities
  aish ci-tool --name Casey --ci claude-opus-4 -- claude --debug
  
  # Launch another Claude instance
  aish ci-tool --name Betty-ci -- claude
  
  # Launch a different tool
  aish ci-tool --name Reviewer --ci gpt-4 -- openai-cli

Messaging:
  Once launched, you can send messages between wrapped CIs using:
    aish <ci-name> "message"
  
  Example:
    # In Casey's terminal:
    aish Betty-ci "Hi Betty, can you help with the API?"
    
    # Betty sees:
    [15:23] Message from Casey: Hi Betty, can you help with the API?
    
    # Betty types:
    aish Casey "Sure! What do you need?"

Notes:
  - The CI name must be unique across all running wrapped CIs
  - Messages are delivered via Unix sockets
  - Only wrapped CIs (launched with ci-tool) can receive messages
  - Use 'aish list' to see all registered CIs including wrapped ones
""")