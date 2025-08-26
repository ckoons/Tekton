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

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        message_buffer,
        state_checkpoint,
        performance_boundary
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func): return func
        return decorator
    def integration_point(**kwargs):
        def decorator(func): return func
        return decorator
    def message_buffer(**kwargs):
        def decorator(func): return func
        return decorator
    def state_checkpoint(**kwargs):
        def decorator(func): return func
        return decorator
    def performance_boundary(**kwargs):
        def decorator(func): return func
        return decorator

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent))
from aish.src.registry.ci_registry import get_registry


@architecture_decision(
    title="Claude Process Handler",
    description="Manages Claude CLI processes for forwarded CIs",
    rationale="Claude requires special handling as a single-prompt model",
    alternatives_considered=["API integration", "Embedded model", "WebSocket bridge"],
    impacts=["ci_forwarding", "message_buffering", "response_latency"],
    decided_by="Casey",
    decision_date="2025-08-24"
)
class ClaudeHandler:
    """Handles Claude process management for forwarded CIs"""
    
    def __init__(self):
        self.claude_processes = {}  # Track active Claude processes per CI
        
    @integration_point(
        name="CI Message Forwarding",
        description="Main entry point for forwarding CI messages to Claude",
        integrates_with=["TokenManager", "SundownSunriseManager", "CIRegistry"],
        data_flow="ci_message -> token_check -> sundown_check -> claude_execution"
    )
    @state_checkpoint(
        name="Token Usage Check",
        checkpoint_type="validation",
        description="Validates token budget before message processing"
    )
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
        
        if not forward_state:
            return None
            
        # Check if model is a Claude variant
        model = forward_state.get('model', '').lower()
        is_claude = ('claude' in model or 
                    'anthropic' in model or
                    model in ['sonnet', 'opus', 'haiku'])
        
        if not is_claude:
            # Not forwarded to Claude, return None to use default
            return None
            
        # Build Claude command based on model
        model_name = forward_state.get('model', 'claude')
        args = forward_state.get('args', '')
        
        # Map model names to Claude CLI arguments
        if 'claude-3-5-sonnet' in model_name:
            claude_cmd = 'claude --model claude-3-5-sonnet-latest --print'
        elif 'claude-3-5-haiku' in model_name:
            claude_cmd = 'claude --model claude-3-5-haiku-latest --print'
        elif 'claude-opus-4' in model_name:
            claude_cmd = 'claude --model claude-opus-4-1-20250805 --print'
        elif args:
            # Use provided args if any
            claude_cmd = args
        else:
            # Default Claude command
            claude_cmd = 'claude --print'
        
        # Add any additional args
        if args and 'claude' not in args:
            claude_cmd += f' {args}'
        
        # For normal Claude forwarding, check if --continue should be added
        if '--continue' not in claude_cmd and next_prompt is None:
            # Check if CI needs fresh start (after sundown)
            needs_fresh = registry.get_needs_fresh_start(ci_name) if hasattr(registry, 'get_needs_fresh_start') else False
            
            if not needs_fresh:
                # Add --continue for normal conversation flow
                claude_cmd = claude_cmd.replace('--print', '--print --continue')
            else:
                # Clear the fresh start flag after use
                if hasattr(registry, 'set_needs_fresh_start'):
                    registry.set_needs_fresh_start(ci_name, False)
        
        # Check for buffered messages from other CIs
        from shared.aish.src.core.unified_sender import get_buffered_messages
        buffered = get_buffered_messages(ci_name, clear=False)  # Don't clear yet
        
        # @integration_point: TOKEN MANAGEMENT
        # Integration: claude_handler → TokenManager → sundown decision
        # This section integrates with Rhetor's TokenManager for proactive management
        try:
            from Rhetor.rhetor.core.token_manager import get_token_manager
            token_mgr = get_token_manager()
            
            # Determine model from command
            if 'opus' in claude_cmd:
                model = 'claude-opus-4'
            elif 'sonnet' in claude_cmd:
                model = 'claude-3-5-sonnet'
            elif 'haiku' in claude_cmd:
                model = 'claude-3-5-haiku'
            else:
                model = 'claude-3-sonnet'  # Default
            
            # Initialize tracking if needed
            if ci_name not in token_mgr.usage_tracker:
                token_mgr.init_ci_tracking(ci_name, model)
            
            # Estimate prompt size
            system_prompt = ""  # TODO: Get actual system prompt if available
            estimate = token_mgr.estimate_prompt_size(
                ci_name, 
                message,
                system_prompt=system_prompt,
                buffered_messages=buffered or ""
            )
            
            # Check if we should trigger sundown
            should_sundown, reason = token_mgr.should_sundown(ci_name)
            
            if not estimate['fits']:
                print(f"[Claude Handler] WARNING: Prompt may exceed token limit for {ci_name}")
                print(f"  Total tokens: {estimate['total']}, Limit: {estimate['limit']}")
                print(f"  Recommendation: {estimate['recommendation']}")
                
                # @state_checkpoint: Critical token threshold
                # If critical, PREVENT sending and force sundown
                if estimate['percentage'] >= 0.95:
                    print(f"[Claude Handler] CRITICAL: Triggering emergency sundown for {ci_name}")
                    
                    # PREVENT the message from being sent
                    error_msg = (
                        f"🛑 PROMPT TOO LARGE: {estimate['percentage']:.1f}% of token limit\n"
                        f"Total tokens: {estimate['total']:,} / Limit: {estimate['limit']:,}\n\n"
                        f"Automatic sundown triggered. The CI needs to preserve context first.\n"
                        f"Run: aish sundown {ci_name}\n"
                        f"Then: aish sunrise {ci_name}"
                    )
                    
                    # Set fresh start flag
                    registry.set_needs_fresh_start(ci_name, True)
                    
                    # Return error instead of sending to Claude
                    return error_msg
                    
            elif should_sundown and estimate['percentage'] >= 0.85:
                print(f"[Claude Handler] AUTO-TRIGGERING SUNDOWN for {ci_name}: {reason}")
                
                # Auto-inject sundown prompt WITH context (use --continue)
                sundown_prompt = (
                    "\n\n[SYSTEM: Approaching token limit. Time to wrap up.]\n"
                    "Please summarize:\n"
                    "1. What you've been working on\n"
                    "2. Key decisions or insights\n"
                    "3. What should continue tomorrow\n"
                    "Keep it concise but complete.\n\n"
                )
                
                # Prepend sundown prompt to user message
                combined_message = sundown_prompt + combined_message
                print(f"[Claude Handler] Injected sundown prompt, keeping context with --continue")
                
                # Mark that after THIS response, we need fresh start
                # TODO: Need to monitor response and set flag after
                
            # Update usage tracking
            token_mgr.update_usage(ci_name, 'buffered_messages', buffered or "")
            token_mgr.update_usage(ci_name, 'conversation_history', message)
            
        except Exception as e:
            # Don't fail if token management has issues
            print(f"[Claude Handler] Token management error (non-fatal): {e}")
        
        # Now clear the buffered messages after checking
        buffered = get_buffered_messages(ci_name, clear=True)
        
        # Combine user message with buffered messages
        if buffered:
            combined_message = message + buffered
            print(f"[Claude Handler] Injecting buffered messages for {ci_name}")
        else:
            combined_message = message
        
        # Execute Claude with the combined message
        response = await self.execute_claude(claude_cmd, combined_message, ci_name)
        
        # Monitor response for sundown completion
        try:
            from shared.ai.response_monitor import handle_post_response
            handle_post_response(ci_name, combined_message, response)
        except Exception as e:
            # Don't fail if monitor has issues
            print(f"[Claude Handler] Response monitor error (non-fatal): {e}")
        
        return response
    
    @performance_boundary(
        name="Claude Process Execution",
        timeout_ms=300000,  # 5 minutes
        sla_ms=60000,  # Expected 1 minute response
        description="No timeout for Claude - can take 5+ minutes for complex tasks"
    )
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