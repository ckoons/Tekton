"""
Claude Code adapter for CI Tools integration.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..base_adapter import BaseCIToolAdapter


class ClaudeCodeAdapter(BaseCIToolAdapter):
    """
    Adapter for Claude Code integration.
    
    Handles the specifics of communicating with Claude Code
    through stdin/stdout while presenting a socket interface.
    """
    
    def __init__(self, tool_name: str = 'claude-code', config: Optional[Dict[str, Any]] = None):
        """Initialize Claude Code adapter."""
        # If config is passed, use it; otherwise use defaults
        if config and isinstance(config, dict):
            # Extract port from config if available
            port = config.get('port', 8400)
            if port == 'auto':
                port = 8400  # Default port for now
        else:
            # Legacy support: if tool_name is actually a port number
            if isinstance(tool_name, int):
                port = tool_name
                tool_name = 'claude-code'
            else:
                port = 8400
        
        default_config = {
            'display_name': 'Claude Code',
            'executable': 'claude-code',
            'capabilities': {
                'code_analysis': True,
                'code_generation': True,
                'refactoring': True,
                'multi_file': True,
                'project_context': True,
                'debugging': True,
                'testing': True,
                'documentation': True
            },
            'environment': {
                'CLAUDE_CODE_MODE': 'socket',
                'CLAUDE_CODE_FORMAT': 'json'
            }
        }
        
        # Merge configs if provided
        if config and isinstance(config, dict):
            default_config.update(config)
        
        super().__init__(tool_name, port, default_config)
        
        # Claude Code specific state
        self.context_window = []
        self.max_context_messages = 10
        self.session_id = None
        self.message_count = 0
        self.use_claude_max = True  # Use subscription instead of API
    
    def get_executable_path(self) -> Optional[Path]:
        """Find Claude Code executable."""
        # First check if we have executable in config (from tools.json)
        if self.config and 'executable' in self.config:
            exe_path = Path(self.config['executable'])
            if exe_path.exists():
                return exe_path
        
        # Check common locations
        possible_paths = [
            Path('/usr/local/bin/claude-code'),
            Path('/opt/claude-code/bin/claude-code'),
            Path.home() / '.local' / 'bin' / 'claude-code',
            Path('/Applications/Claude Code.app/Contents/MacOS/Claude Code')  # macOS
        ]
        
        # Check PATH
        claude_in_path = shutil.which('claude-code')
        if claude_in_path:
            return Path(claude_in_path)
        
        # Check configured path
        import os
        configured_path = os.environ.get('CLAUDE_CODE_PATH')
        if configured_path:
            path = Path(configured_path)
            if path.exists():
                return path
        
        # Check common locations
        for path in possible_paths:
            if path.exists():
                return path
        
        self.logger.error("Claude Code executable not found")
        return None
    
    def get_launch_args(self, session_id: Optional[str] = None) -> List[str]:
        """Get Claude Code launch arguments."""
        # Start with base args from config
        if self.config and 'launch_args' in self.config:
            args = self.config['launch_args'].copy()
        else:
            args = ['--print']
        
        # For Claude Max, we'll maintain context through our own message history
        # rather than relying on --continue which seems problematic
        
        # Add workspace if in project directory
        import os
        workspace = os.getcwd()
        if workspace and '--add-dir' not in str(args):
            args.extend(['--add-dir', workspace])
        
        return args
    
    def translate_to_tool(self, message: Dict[str, Any]) -> str:
        """Translate Tekton message to Claude Code format."""
        # Each interaction is standalone - like a new day
        # The message should already contain any necessary context
        return message.get('content', '')
    
    def translate_from_tool(self, output: str) -> Dict[str, Any]:
        """Translate Claude Code output to Tekton format."""
        self.message_count += 1
        
        # Simple response for Claude Max subscription mode
        return {
            'type': 'response',
            'ci': 'claude-code',
            'content': output.strip(),
            'metadata': {
                'message_count': self.message_count,
                'format': 'plain_text',
                'subscription': 'Claude Max',
                'mode': 'stateless'  # Each message is independent
            },
            'timestamp': time.time()
        }
    
    def should_reset_session(self) -> bool:
        """Check if we should reset the session."""
        # Reset after 50 messages or if explicitly requested
        return self.message_count > 50
    
    def reset_session(self):
        """Reset the session, dropping the session ID."""
        self.logger.info(f"Resetting session (was: {self.session_id})")
        self.session_id = None
        self.message_count = 0
        self.context_window = []
    
    def send_shutdown_command(self):
        """Send graceful shutdown to Claude Code."""
        # For batch mode, there's nothing to shutdown
        pass
    
    def on_output(self, message: Dict[str, Any]):
        """Handle output from Claude Code."""
        # Update metrics
        if message.get('metadata', {}).get('tokens_used'):
            self.metrics['total_tokens'] = self.metrics.get('total_tokens', 0) + \
                                           message['metadata']['tokens_used']
        
        # Check for errors
        if message.get('metadata', {}).get('status') == 'error':
            self.logger.error(f"Claude Code error: {message.get('content')}")
            self.metrics['errors'] += 1
    
    def on_error(self, error: str):
        """Handle Claude Code errors."""
        self.logger.error(f"Claude Code stderr: {error}")
        
        # Check for known error patterns
        if "rate limit" in error.lower():
            self.logger.warning("Rate limit detected")
        elif "context length" in error.lower():
            self.logger.warning("Context length exceeded, trimming context")
            self._trim_context()
    
    def _map_action(self, message: Dict[str, Any]) -> str:
        """Map Tekton message type to Claude Code action."""
        msg_type = message.get('type', 'message')
        
        action_map = {
            'message': 'chat',
            'command': 'execute',
            'analyze': 'analyze_code',
            'generate': 'generate_code',
            'refactor': 'refactor_code',
            'debug': 'debug_code',
            'test': 'generate_tests'
        }
        
        return action_map.get(msg_type, 'chat')
    
    def _update_context(self, message: Dict[str, Any]):
        """Update context window with new message."""
        context_msg = {
            'role': 'user',
            'content': message.get('content', ''),
            'timestamp': time.time()
        }
        
        self.context_window.append(context_msg)
        
        # Trim if too long
        if len(self.context_window) > self.max_context_messages:
            self.context_window = self.context_window[-self.max_context_messages:]
    
    def _get_context_messages(self) -> List[Dict[str, Any]]:
        """Get formatted context messages."""
        return [
            {
                'role': msg['role'],
                'content': msg['content']
            }
            for msg in self.context_window[-5:]  # Last 5 messages
        ]
    
    def _trim_context(self):
        """Trim context window to reduce token usage."""
        # Keep only recent messages
        self.context_window = self.context_window[-5:]
        self.logger.info("Trimmed context window")
    
    def _extract_capabilities(self, output: Dict[str, Any]) -> List[str]:
        """Extract which capabilities were used."""
        capabilities = []
        
        # Check output type
        output_type = output.get('type', '')
        if 'analysis' in output_type:
            capabilities.append('code_analysis')
        elif 'generated' in output_type:
            capabilities.append('code_generation')
        elif 'refactored' in output_type:
            capabilities.append('refactoring')
        
        return capabilities


# Import time at module level
import time