"""
Pipeline parser for AI shell syntax
"""

import re
from typing import List, Dict, Any

class PipelineParser:
    """Parse AI pipeline commands"""
    
    def __init__(self):
        # Patterns for parsing
        self.pipe_pattern = re.compile(r'\s*\|\s*')
        self.redirect_pattern = re.compile(r'\s*([<>])\s*')
        self.ai_pattern = re.compile(r'^[a-zA-Z_]\w*$')
    
    def parse(self, command: str) -> Dict[str, Any]:
        """
        Parse an AI pipeline command
        
        Examples:
            echo "test" | apollo
            apollo | athena | sophia
            team-chat "message"
            apollo > output.txt
        """
        # Remove extra whitespace
        command = command.strip()
        
        # Check for special commands
        if command.startswith('team-chat'):
            return self._parse_team_chat(command)
        
        # Parse pipeline
        segments = self.pipe_pattern.split(command)
        
        if len(segments) == 1:
            # No pipes, check for redirects
            return self._parse_single_command(command)
        else:
            # Pipeline command
            return self._parse_pipeline(segments)
    
    def _parse_team_chat(self, command: str) -> Dict[str, Any]:
        """Parse team-chat command"""
        # Extract message (handle quotes)
        match = re.match(r'team-chat\s+["\'](.+)["\']', command)
        if match:
            return {
                'type': 'team-chat',
                'message': match.group(1)
            }
        else:
            # Unquoted message
            parts = command.split(None, 1)
            if len(parts) == 2:
                return {
                    'type': 'team-chat',
                    'message': parts[1]
                }
            else:
                raise ValueError("team-chat requires a message")
    
    def _parse_single_command(self, command: str) -> Dict[str, Any]:
        """Parse single command (no pipes)"""
        # Check for redirects
        if '>' in command:
            parts = command.split('>', 1)
            return {
                'type': 'redirect',
                'command': parts[0].strip(),
                'output': parts[1].strip()
            }
        elif '<' in command:
            parts = command.split('<', 1)
            return {
                'type': 'input',
                'command': parts[0].strip(),
                'input': parts[1].strip()
            }
        else:
            # Check for direct AI command: ai_name "message"
            # Match patterns like: apollo "hello" or numa 'test message'
            match = re.match(r'^([a-zA-Z_]\w*)\s+["\'](.+)["\']$', command)
            if match:
                ai_name = match.group(1)
                message = match.group(2)
                # Convert to echo | ai pipeline format
                return {
                    'type': 'pipeline',
                    'stages': [
                        {'type': 'echo', 'content': message},
                        {'type': 'ai', 'name': ai_name}
                    ]
                }
            
            # Simple command
            return {
                'type': 'simple',
                'command': command
            }
    
    def _parse_pipeline(self, segments: List[str]) -> Dict[str, Any]:
        """Parse pipeline of commands"""
        stages = []
        
        for segment in segments:
            segment = segment.strip()
            
            # Handle echo commands
            if segment.startswith('echo '):
                stages.append({
                    'type': 'echo',
                    'content': self._extract_echo_content(segment)
                })
            # Handle AI names
            elif self.ai_pattern.match(segment):
                stages.append({
                    'type': 'ai',
                    'name': segment
                })
            # Handle complex commands
            else:
                stages.append({
                    'type': 'command',
                    'content': segment
                })
        
        return {
            'type': 'pipeline',
            'stages': stages
        }
    
    def _extract_echo_content(self, command: str) -> str:
        """Extract content from echo command"""
        # Remove 'echo ' prefix
        content = command[5:].strip()
        
        # Handle quoted strings
        if (content.startswith('"') and content.endswith('"')) or \
           (content.startswith("'") and content.endswith("'")):
            return content[1:-1]
        else:
            return content