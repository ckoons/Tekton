"""
Chat Command Handler
Executes commands from chat interface (aish, shell, etc.)
First stage backend processor for Tekton chat commands
"""

import subprocess
import asyncio
import json
import os
import re
from typing import Dict, Any, Optional
from pathlib import Path

# Safe command whitelist
SAFE_SHELL_COMMANDS = {
    'ls', 'pwd', 'date', 'whoami', 'git', 'ps', 
    'grep', 'find', 'cat', 'head', 'tail', 'wc',
    'echo', 'env', 'which', 'tekton-status', 'aish'
}

# Dangerous patterns to block
DANGEROUS_PATTERNS = [
    r'rm\s+-rf', r'sudo', r'>\s*/dev/', r'dd\s+if=',
    r'mkfs', r';\s*rm', r'&&\s*rm', r'\|\s*rm',
    r'format\s+c:', r'del\s+/f', r'chmod\s+777',
    r'curl.*\|\s*sh', r'wget.*\|\s*sh'
]

class ChatCommandHandler:
    """Handles command execution from chat interfaces"""
    
    def __init__(self):
        self.forward_states = {}  # Track forwarded CIs
        self._load_forward_states()
    
    def _load_forward_states(self):
        """Load persistent forward states from CI registry"""
        try:
            registry_path = Path.home() / '.tekton' / 'aish' / 'ci-registry' / 'forward_states.json'
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    self.forward_states = json.load(f)
        except Exception as e:
            print(f"Could not load forward states: {e}")
    
    def _save_forward_states(self):
        """Save forward states to CI registry"""
        try:
            registry_path = Path.home() / '.tekton' / 'aish' / 'ci-registry' / 'forward_states.json'
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_path, 'w') as f:
                json.dump(self.forward_states, f, indent=2)
        except Exception as e:
            print(f"Could not save forward states: {e}")
    
    async def handle_command(self, command_type: str, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command from chat interface
        
        Args:
            command_type: Type of command (aish, shell, forward, etc.)
            command: Command string to execute
            context: Context including component name, user, etc.
        
        Returns:
            Dict with output, error, type fields
        """
        
        if command_type == "aish":
            return await self.execute_aish_command(command, context)
        elif command_type == "shell":
            return await self.execute_shell_command(command, context)
        elif command_type == "forward":
            return await self.handle_forward_command(command, context)
        elif command_type == "unforward":
            return await self.handle_unforward_command(command, context)
        else:
            return {
                "type": "error",
                "output": f"Unknown command type: {command_type}",
                "error": True
            }
    
    async def execute_aish_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an aish command"""
        try:
            # Build full aish command
            full_command = f"aish {command}"
            
            # Execute with timeout
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, 'TEKTON_CONTEXT': context.get('component', 'unknown')}
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "type": "error",
                    "output": "Command timed out after 10 seconds",
                    "error": True
                }
            
            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace').strip()
            stderr_str = stderr.decode('utf-8', errors='replace').strip()
            
            if process.returncode != 0:
                return {
                    "type": "error",
                    "output": stderr_str or f"Command failed with exit code {process.returncode}",
                    "error": True
                }
            
            return {
                "type": "system",
                "output": stdout_str or "Command completed",
                "error": False
            }
            
        except Exception as e:
            return {
                "type": "error",
                "output": f"Failed to execute aish command: {str(e)}",
                "error": True
            }
    
    async def execute_shell_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a shell command if safe"""
        
        # Check if command is safe
        if not self.is_safe_shell_command(command):
            return {
                "type": "error",
                "output": f"Command blocked for safety: {command}",
                "error": True
            }
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=context.get('working_dir', os.getcwd())
            )
            
            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "type": "error",
                    "output": "Command timed out after 5 seconds",
                    "error": True
                }
            
            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace').strip()
            stderr_str = stderr.decode('utf-8', errors='replace').strip()
            
            # Truncate long output (25K character limit)
            if len(stdout_str) > 25000:
                stdout_str = stdout_str[:25000] + "\n... (response truncated at 25,000 characters)"
            
            if process.returncode != 0:
                return {
                    "type": "error",
                    "output": stderr_str or f"Command failed with exit code {process.returncode}",
                    "error": True
                }
            
            return {
                "type": "system",
                "output": stdout_str or "Command completed",
                "error": False
            }
            
        except Exception as e:
            return {
                "type": "error",
                "output": f"Failed to execute shell command: {str(e)}",
                "error": True
            }
    
    def is_safe_shell_command(self, command: str) -> bool:
        """Check if shell command is safe to execute"""
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        # Get first word of command
        first_word = command.split()[0] if command.split() else ""
        
        # Check if in safe command list
        if first_word not in SAFE_SHELL_COMMANDS:
            # Allow full paths to safe commands
            if '/' in first_word:
                base_command = os.path.basename(first_word)
                if base_command not in SAFE_SHELL_COMMANDS:
                    return False
            else:
                return False
        
        return True
    
    async def handle_forward_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle aish forward command"""
        
        # Parse: forward <ci-name> <model> [args...]
        parts = command.split(maxsplit=2)
        if len(parts) < 2:
            return {
                "type": "error",
                "output": "Usage: forward <ci-name> <model> [args...]",
                "error": True
            }
        
        ci_name = parts[0]
        model = parts[1]
        args = parts[2] if len(parts) > 2 else ""
        
        # Store forward state persistently
        self.forward_states[ci_name] = {
            "model": model,
            "args": args,
            "started": asyncio.get_event_loop().time(),
            "component": context.get('component', 'unknown')
        }
        self._save_forward_states()
        
        # Execute forward command
        forward_cmd = f"aish forward {ci_name} {model} {args}".strip()
        result = await self.execute_aish_command(f"forward {ci_name} {model} {args}", context)
        
        if not result.get('error'):
            result['output'] = f"Forwarded {ci_name} to {model}"
        
        return result
    
    async def handle_unforward_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle aish unforward command"""
        
        # Parse: unforward <ci-name>
        parts = command.split(maxsplit=1)
        if not parts:
            return {
                "type": "error",
                "output": "Usage: unforward <ci-name>",
                "error": True
            }
        
        ci_name = parts[0]
        
        # Remove forward state
        if ci_name in self.forward_states:
            del self.forward_states[ci_name]
            self._save_forward_states()
            
            # Execute unforward command
            result = await self.execute_aish_command(f"unforward {ci_name}", context)
            
            if not result.get('error'):
                result['output'] = f"Unforwarded {ci_name}, returning to default model"
            
            return result
        else:
            return {
                "type": "system",
                "output": f"{ci_name} was not forwarded",
                "error": False
            }
    
    def get_forward_state(self, ci_name: str) -> Optional[Dict[str, Any]]:
        """Get forward state for a CI"""
        return self.forward_states.get(ci_name)
    
    def list_forwards(self) -> Dict[str, Any]:
        """List all active forwards"""
        if not self.forward_states:
            return {
                "type": "system",
                "output": "No active forwards",
                "error": False
            }
        
        lines = ["Active forwards:"]
        for ci_name, state in self.forward_states.items():
            lines.append(f"  {ci_name} → {state['model']}")
        
        return {
            "type": "system",
            "output": "\n".join(lines),
            "error": False
        }


# Global handler instance
_handler = None

def get_handler() -> ChatCommandHandler:
    """Get or create global handler instance"""
    global _handler
    if _handler is None:
        _handler = ChatCommandHandler()
    return _handler


async def handle_chat_command(command_type: str, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main entry point for handling chat commands
    
    Args:
        command_type: Type of command (aish, shell, forward, etc.)
        command: Command string to execute
        context: Optional context dict
    
    Returns:
        Dict with output, error, type fields
    """
    handler = get_handler()
    context = context or {}
    return await handler.handle_command(command_type, command, context)


# FastAPI endpoint integration
def create_chat_command_endpoint(app):
    """Create FastAPI endpoint for chat commands"""
    from fastapi import HTTPException
    from pydantic import BaseModel
    
    class CommandRequest(BaseModel):
        type: str
        command: str
        context: Dict[str, Any] = {}
    
    @app.post("/api/chat/command")
    async def execute_chat_command(request: CommandRequest):
        """Execute command from chat interface"""
        try:
            result = await handle_chat_command(
                request.type,
                request.command,
                request.context
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))