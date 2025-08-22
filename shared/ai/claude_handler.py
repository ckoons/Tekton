"""
Claude Handler for Model Escalation
Handles spawning Claude processes for forwarded CIs
"""

import subprocess
import asyncio
import json
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))
from aish.src.registry.ci_registry import get_registry


class ClaudeHandler:
    """Handles Claude process management for forwarded CIs"""
    
    def __init__(self):
        self.claude_processes = {}  # Track active Claude processes per CI
        
    async def handle_forwarded_message(self, ci_name: str, message: str) -> str:
        """
        Handle a message for a forwarded CI.
        
        NEW: Checks for sunset/sunrise prompts first!
        
        Args:
            ci_name: Name of the CI (e.g., 'numa-ci')
            message: Message to send to Claude
            
        Returns:
            Claude's response
        """
        registry = get_registry()
        
        # SUNSET/SUNRISE CHECK - Priority over normal forwarding
        next_prompt = registry.get_next_prompt(ci_name)
        if next_prompt:
            # Handle sunset protocol
            if next_prompt.startswith('SUNSET_PROTOCOL'):
                # Send sunset message directly
                response = await self.execute_claude('claude --print', next_prompt, ci_name)
                
                # Store the response in last_output for auto-detection
                registry.update_ci_last_output(ci_name, {
                    'user_message': next_prompt,
                    'content': response
                })
                
                # Clear the next_prompt after use
                registry.clear_next_prompt(ci_name)
                
                return response
            
            # Handle sunrise with system prompt injection
            elif next_prompt.startswith('--append-system-prompt'):
                # Extract the system prompt content
                import re
                match = re.search(r"--append-system-prompt\s+'([^']*)'", next_prompt)
                if match:
                    system_content = match.group(1)
                    # Build Claude command with both the system prompt and continue
                    claude_cmd = f"claude --print --continue --append-system-prompt '{system_content}'"
                else:
                    claude_cmd = f"claude --print {next_prompt}"
                
                response = await self.execute_claude(claude_cmd, message, ci_name)
                
                # Clear the next_prompt and sunrise_context after use
                registry.clear_next_prompt(ci_name)
                registry.clear_sunrise_context(ci_name)
                
                return response
        
        # Normal forwarding check
        forward_state = registry.get_forward_state(ci_name)
        
        if not forward_state or forward_state.get('model') != 'claude':
            # Not forwarded to Claude, return None to use default
            return None
            
        # Get Claude command from forward state
        claude_cmd = forward_state.get('args', 'claude --print')
        
        # For normal Claude forwarding, check if --continue should be added
        if '--continue' not in claude_cmd and next_prompt is None:
            # Add --continue for normal conversation flow
            claude_cmd = claude_cmd.replace('--print', '--print --continue')
        
        # Execute Claude with the message
        return await self.execute_claude(claude_cmd, message, ci_name)
    
    async def execute_claude(self, claude_cmd: str, message: str, ci_name: str) -> str:
        """
        Execute Claude command with message.
        
        Args:
            claude_cmd: Full Claude command (e.g., 'claude --print')
            message: Message to send
            ci_name: CI name for context
            
        Returns:
            Claude's response
        """
        try:
            # Parse command into list
            cmd_parts = claude_cmd.split()
            
            # Determine launch directory
            import os
            from shared.env import TektonEnviron
            from pathlib import Path
            
            tekton_root = Path(TektonEnviron.get('TEKTON_ROOT', '.'))
            
            # Always use TEKTON_ROOT as the launch directory
            # This ensures each instance (Tekton, Coder-A/B/C) uses its own context
            launch_dir = str(tekton_root)
            
            
            # Create subprocess with specified working directory
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=launch_dir  # Set working directory for Claude
            )
            
            # Send message and get response - NO TIMEOUT for Claude
            # Claude can take 5+ minutes for complex tasks
            stdout, stderr = await process.communicate(input=message.encode())
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace')
                if not error_msg.strip():
                    # If stderr is empty, check stdout for any output
                    output = stdout.decode('utf-8', errors='replace').strip()
                    if output:
                        return f"Claude error (exit code {process.returncode}): {output}"
                    else:
                        return f"Claude error: Process exited with code {process.returncode} but no error message"
                return f"Claude error: {error_msg}"
            
            response = stdout.decode('utf-8', errors='replace').strip()
            return response or "Claude returned empty response"
        except FileNotFoundError:
            return "Claude not found. Please install Claude CLI."
        except Exception as e:
            return f"Claude execution error: {str(e)}"
    
    async def check_claude_available(self) -> bool:
        """Check if Claude CLI is available."""
        try:
            process = await asyncio.create_subprocess_exec(
                'which', 'claude',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            stdout, _ = await process.communicate()
            return process.returncode == 0
        except:
            return False
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get information about active Claude sessions."""
        registry = get_registry()
        forward_states = registry.list_forward_states()
        
        claude_sessions = {}
        for ci_name, state in forward_states.items():
            if state.get('model') == 'claude':
                claude_sessions[ci_name] = {
                    'command': state.get('args'),
                    'started': state.get('started'),
                    'active': state.get('active', True)
                }
        
        return claude_sessions


# Global handler instance
_claude_handler = None

def get_claude_handler() -> ClaudeHandler:
    """Get or create global Claude handler."""
    global _claude_handler
    if _claude_handler is None:
        _claude_handler = ClaudeHandler()
    return _claude_handler


async def process_with_claude(ci_name: str, message: str) -> Optional[str]:
    """
    Process a message with Claude if the CI is forwarded.
    
    Args:
        ci_name: CI name
        message: Message to process
        
    Returns:
        Claude's response or None if not forwarded
    """
    handler = get_claude_handler()
    return await handler.handle_forwarded_message(ci_name, message)