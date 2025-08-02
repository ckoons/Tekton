"""
Generic CI Tool Adapter for stdio-based tools.
Provides a flexible adapter for any tool that communicates via stdin/stdout.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..base_adapter import BaseCIToolAdapter


class GenericAdapter(BaseCIToolAdapter):
    """
    Generic adapter for stdio-based CI tools.
    
    Expects JSON communication by default but can handle plain text.
    Suitable for most command-line tools that read from stdin and write to stdout.
    """
    
    def __init__(self, tool_name: str, config: Dict[str, Any]):
        """
        Initialize generic adapter.
        
        Args:
            tool_name: Name of the tool
            config: Tool configuration including executable, args, etc.
        """
        # Get port from config
        port = config.get('port', 8500)
        super().__init__(tool_name, port, config)
        self.logger = logging.getLogger(f"ci_tools.adapters.generic.{tool_name}")
        
        # Get format preference from config
        self.input_format = config.get('input_format', 'json')
        self.output_format = config.get('output_format', 'json')
    
    def get_executable_path(self) -> Optional[Path]:
        """
        Get the path to the tool's executable.
        
        Returns:
            Path to executable from config
        """
        executable = self.config.get('executable')
        if executable:
            return Path(executable)
        return None
    
    def get_launch_args(self, session_id: Optional[str] = None) -> list:
        """
        Get command line arguments for launching the tool.
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            List of command line arguments from config
        """
        args = self.config.get('launch_args', [])
        if isinstance(args, str):
            # Split string args
            return args.split()
        return list(args) if args else []
        
    def translate_to_tool(self, message: Dict[str, Any]) -> str:
        """
        Translate message to tool format.
        
        Default behavior:
        - JSON mode: Send as JSON with 'message' field
        - Text mode: Send just the content
        
        Args:
            message: Standard message dict
            
        Returns:
            Formatted string for tool
        """
        content = message.get('content', '')
        
        if self.input_format == 'json':
            # JSON format - include metadata if available
            tool_message = {
                'message': content,
                'type': message.get('type', 'user'),
                'timestamp': message.get('timestamp'),
                'session': message.get('session'),
                'context': message.get('context', {})
            }
            
            # Remove None values
            tool_message = {k: v for k, v in tool_message.items() if v is not None}
            
            return json.dumps(tool_message) + '\n'
        else:
            # Plain text format
            return content + '\n'
    
    def translate_from_tool(self, output: str) -> Optional[Dict[str, Any]]:
        """
        Translate tool output to standard format.
        
        Default behavior:
        - Try to parse as JSON first
        - Fall back to plain text if JSON parsing fails
        
        Args:
            output: Raw output from tool
            
        Returns:
            Standard message dict or None
        """
        output = output.strip()
        if not output:
            return None
        
        if self.output_format == 'json':
            try:
                # Try to parse as JSON
                data = json.loads(output)
                
                # Handle different JSON structures
                if isinstance(data, dict):
                    # Extract content from various possible fields
                    content = (
                        data.get('response') or
                        data.get('content') or
                        data.get('message') or
                        data.get('text') or
                        json.dumps(data)  # Fallback to full JSON
                    )
                    
                    return {
                        'type': data.get('type', 'response'),
                        'content': content,
                        'metadata': data,
                        'tool': self.tool_name,
                        'timestamp': data.get('timestamp')
                    }
                else:
                    # Non-dict JSON (list, string, etc.)
                    return {
                        'type': 'response',
                        'content': json.dumps(data),
                        'tool': self.tool_name
                    }
                    
            except json.JSONDecodeError:
                # Not valid JSON, treat as plain text
                pass
        
        # Plain text format or JSON parse failed
        return {
            'type': 'response',
            'content': output,
            'tool': self.tool_name
        }
    
    def get_health_check_command(self) -> Optional[str]:
        """
        Get health check command based on config.
        
        Returns:
            Command string or None
        """
        health_check = self.config.get('health_check')
        
        if not health_check:
            return None
            
        # Map common health check types to commands
        health_check_commands = {
            'version': '--version',
            'help': '--help',
            'ping': 'ping',
            'status': 'status',
            'health': 'health'
        }
        
        if health_check in health_check_commands:
            return health_check_commands[health_check]
        else:
            # Assume it's a custom command
            return health_check
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate response from tool.
        
        Generic validation - just check for content.
        
        Args:
            response: Response dict
            
        Returns:
            True if valid
        """
        return bool(response and response.get('content'))