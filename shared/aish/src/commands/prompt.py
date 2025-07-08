"""
Prompt command implementation for aish.
Sends high-priority messages to terminal prompt inboxes.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

def handle_prompt_command(args: List[str]) -> int:
    """
    Handle prompt command: aish prompt <target> "message"
    
    Args:
        args: Command arguments [target, message, ...]
        
    Returns:
        0 on success, 1 on error
    """
    if not args or args[0] == 'help':
        print("Usage: aish prompt <target> \"message\"")
        print()
        print("Send high-priority prompt to terminal(s)")
        print()
        print("Target formats:")
        print("  <name>       Send to specific terminal (e.g., 'teri')")
        print("  @<purpose>   Send to all terminals with purpose (e.g., '@test')")
        print()
        print("Examples:")
        print("  aish prompt teri \"Please review PR #42\"")
        print("  aish prompt @test \"Tests are failing\"")
        print("  aish prompt alice \"Urgent: Production issue\"")
        return 0
    
    if len(args) < 2:
        print("Error: Missing target or message", file=sys.stderr)
        print("Usage: aish prompt <target> \"message\"", file=sys.stderr)
        return 1
    
    target = args[0]
    # Join remaining args as message
    message = ' '.join(args[1:])
    
    # For now, use the regular terma send mechanism
    # TODO: When prompt inbox is implemented, send there instead
    from commands.terma import terma_send_message_to_terminal
    
    # Add prompt prefix to distinguish from regular messages
    prompt_message = f"[PROMPT] {message}"
    
    if target.startswith('@'):
        # Purpose-based routing
        purpose = target[1:]
        print(f"Sending prompt to all terminals with purpose '{purpose}'...")
        
        # Get terminal list from terma
        try:
            import urllib.request
            import urllib.error
            
            endpoint = os.environ.get('TERMA_ENDPOINT', 'http://localhost:8004')
            req = urllib.request.Request(f"{endpoint}/api/mcp/v2/terminals/list")
            
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode())
                terminals = data.get('terminals', [])
                
            # Filter by purpose using word-based matching
            from core.purpose_matcher import match_purpose
            matched_names = match_purpose(purpose, terminals)
            
            matched = []
            for terminal_name in matched_names:
                result = send_prompt(terminal_name, message)
                if result == 0:
                    matched.append(terminal_name)
            
            if matched:
                print(f"Prompt sent to {len(matched)} terminals: {', '.join(matched)}")
                return 0
            else:
                print(f"No terminals found with purpose '{purpose}'")
                return 1
                
        except Exception as e:
            print(f"Error accessing terminal list: {e}", file=sys.stderr)
            return 1
    else:
        # Direct terminal routing
        result = terma_send_message_to_terminal(target, prompt_message)
        if result == 0:
            print(f"Prompt sent to {target}")
        return result

def send_prompt(target: str, message: str) -> int:
    """
    Send a prompt message to a terminal.
    
    This will be updated to use prompt inbox when available.
    For now, uses regular message with [PROMPT] prefix.
    """
    from commands.terma import terma_send_message_to_terminal
    prompt_message = f"[PROMPT] {message}"
    return terma_send_message_to_terminal(target, prompt_message)