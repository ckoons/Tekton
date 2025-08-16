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
        
        Args:
            ci_name: Name of the CI (e.g., 'numa-ci')
            message: Message to send to Claude
            
        Returns:
            Claude's response
        """
        registry = get_registry()
        forward_state = registry.get_forward_state(ci_name)
        
        if not forward_state or forward_state.get('model') != 'claude':
            # Not forwarded to Claude, return None to use default
            return None
            
        # Get Claude command from forward state
        claude_cmd = forward_state.get('args', 'claude --print')
        
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
            
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send message and get response
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=message.encode()),
                timeout=30.0  # 30 second timeout for Claude
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace')
                return f"Claude error: {error_msg}"
            
            response = stdout.decode('utf-8', errors='replace').strip()
            return response or "Claude returned empty response"
            
        except asyncio.TimeoutError:
            return "Claude timed out after 30 seconds"
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