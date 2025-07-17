"""
Conversation history management for aish.

Provides Unix-style history tracking with AI responses, supporting:
- Simple text format like bash history
- JSON export via jc-style conversion
- Replay functionality
- Search and filtering
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from shared.env import TektonEnviron


class AIHistory:
    """
    Manages conversation history for aish sessions.
    
    History format:
    1716: echo "what day was yesterday?" | numa
          # Response: Sunday June 29, 2025
    1717: echo "analyze this code" | apollo | athena  
          # apollo: "Code has 3 main functions..."
          # athena: "Architectural patterns suggest..."
    """
    
    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize history manager.
        
        Args:
            history_file: Path to history file (defaults to ~/.aish_history)
        """
        if history_file:
            self.history_file = Path(history_file)
        else:
            tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
            self.history_file = Path(tekton_root) / '.tekton' / 'aish' / '.aish_history'
        
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        self.session_file = Path(tekton_root) / '.tekton' / 'aish' / 'sessions' / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        self.command_number = self._get_last_command_number() + 1
        
        # Ensure directories exist
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _get_last_command_number(self) -> int:
        """Get the last command number from history."""
        if not self.history_file.exists():
            return 0
            
        try:
            with open(self.history_file, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if line.strip() and not line.startswith('#'):
                        # Extract command number
                        num_str = line.split(':')[0].strip()
                        if num_str.isdigit():
                            return int(num_str)
        except Exception:
            pass
            
        return 0
    
    def add_command(self, command: str, responses: Dict[str, str]) -> int:
        """
        Add a command and its responses to history.
        
        Args:
            command: The command executed
            responses: Dictionary of AI responses {ai_name: response}
            
        Returns:
            Command number assigned
        """
        cmd_num = self.command_number
        self.command_number += 1
        
        # Format for text file
        text_entry = f"{cmd_num}: {command}\n"
        for ai_name, response in responses.items():
            # Truncate long responses for readability
            truncated = response[:100] + "..." if len(response) > 100 else response
            text_entry += f"      # {ai_name}: {truncated}\n"
        
        # Append to text history
        with open(self.history_file, 'a') as f:
            f.write(text_entry)
        
        # Save to JSON session
        json_entry = {
            "number": cmd_num,
            "timestamp": time.time(),
            "command": command,
            "responses": responses
        }
        self._append_json_entry(json_entry)
        
        return cmd_num
    
    def _append_json_entry(self, entry: Dict):
        """Append entry to JSON session file."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"session": str(datetime.now()), "entries": []}
            
            data["entries"].append(entry)
            
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # Don't fail on JSON errors
            print(f"Warning: Failed to save JSON history: {e}")
    
    def get_history(self, lines: Optional[int] = None) -> List[str]:
        """
        Get history entries.
        
        Args:
            lines: Number of recent lines to return (None for all)
            
        Returns:
            List of history lines
        """
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, 'r') as f:
            all_lines = f.readlines()
            
        if lines:
            return all_lines[-lines:]
        return all_lines
    
    def search(self, pattern: str) -> List[str]:
        """
        Search history for pattern.
        
        Args:
            pattern: Search pattern
            
        Returns:
            Matching history entries
        """
        if not self.history_file.exists():
            return []
        
        matches = []
        current_entry = []
        
        with open(self.history_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    # New command
                    if current_entry and pattern.lower() in ''.join(current_entry).lower():
                        matches.extend(current_entry)
                    current_entry = [line]
                else:
                    # Part of current entry
                    current_entry.append(line)
        
        # Check last entry
        if current_entry and pattern.lower() in ''.join(current_entry).lower():
            matches.extend(current_entry)
        
        return matches
    
    def get_command_by_number(self, number: int) -> Optional[Tuple[str, Dict[str, str]]]:
        """
        Get a specific command by number.
        
        Args:
            number: Command number
            
        Returns:
            Tuple of (command, responses) or None
        """
        # Try JSON first for complete data
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    for entry in data.get("entries", []):
                        if entry["number"] == number:
                            return entry["command"], entry["responses"]
            except Exception:
                pass
        
        # Fallback to text parsing
        if not self.history_file.exists():
            return None
        
        with open(self.history_file, 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if line.startswith(f"{number}:"):
                command = line.split(':', 1)[1].strip()
                responses = {}
                
                # Parse responses
                j = i + 1
                while j < len(lines) and lines[j].startswith('      #'):
                    resp_line = lines[j].strip()[1:].strip()
                    if ':' in resp_line:
                        ai_name, response = resp_line.split(':', 1)
                        responses[ai_name.strip()] = response.strip()
                    j += 1
                
                return command, responses
        
        return None
    
    def export_json(self, start: Optional[int] = None, end: Optional[int] = None) -> str:
        """
        Export history as JSON (for jc-style processing).
        
        Args:
            start: Starting command number
            end: Ending command number
            
        Returns:
            JSON string
        """
        entries = []
        
        # Read from session files
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        session_dir = Path(tekton_root) / '.tekton' / 'aish' / 'sessions'
        if session_dir.exists():
            for session_file in sorted(session_dir.glob('*.json')):
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                        for entry in data.get("entries", []):
                            if start and entry["number"] < start:
                                continue
                            if end and entry["number"] > end:
                                continue
                            entries.append(entry)
                except Exception:
                    continue
        
        return json.dumps({"history": entries}, indent=2)
    
    def replay(self, number: int) -> Optional[str]:
        """
        Get command for replay.
        
        Args:
            number: Command number to replay
            
        Returns:
            Command string or None
        """
        result = self.get_command_by_number(number)
        if result:
            return result[0]
        return None
    
    def add_exchange(self, ai_name: str, message: str, response: str):
        """
        Add a single AI exchange to history.
        
        Args:
            ai_name: Name of the AI
            message: Message sent to AI
            response: Response from AI
        """
        # Format as a simple command
        command = f'echo "{message}" | {ai_name}'
        responses = {ai_name: response}
        self.add_command(command, responses)
    
    def clear(self):
        """Clear history (with backup)."""
        if self.history_file.exists():
            # Backup current history
            backup = self.history_file.with_suffix('.bak')
            self.history_file.rename(backup)
            
        # Reset command number
        self.command_number = 1