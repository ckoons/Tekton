#!/usr/bin/env python3
"""
Session Manager for Greek Chorus (Claude Code)
Handles session resets and continuation logic for long conversations

This helps manage the context window by:
1. Detecting when context is getting too large
2. Providing clean reset points
3. Managing --continue flag usage
4. Preserving essential context during resets
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import subprocess
import shutil

# Add parent paths for imports
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.env import TektonEnviron, TektonEnvironLock
    # Load environment when running as script
    TektonEnvironLock.load()
except ImportError:
    # Fallback if shared.env not available
    class TektonEnviron:
        @staticmethod
        def get(key, default=None):
            return os.environ.get(key, default)
    
    class TektonEnvironLock:
        @staticmethod
        def load():
            pass


class GreekChorusSession:
    """Manages Claude Code session state for the Greek Chorus"""
    
    def __init__(self):
        self.claude_dir = Path.home() / ".claude"
        self.tekton_session_dir = Path.home() / ".tekton" / "session"
        self.tekton_session_dir.mkdir(parents=True, exist_ok=True)
        
        # Get current working directory for project-specific conversations
        cwd = Path.cwd()
        # Convert path to Claude's format: /Users/name/path -> -Users-name-path
        project_path = str(cwd).replace('/', '-')
        self.project_dir = self.claude_dir / "projects" / project_path
        
        self.state_file = self.tekton_session_dir / "chorus_state.json"
        # Get context limit after loading environment (in KB)
        self.context_limit_kb = int(TektonEnviron.get("CHORUS_CONTEXT_LIMIT_KB", "500"))  # 500KB default
        
    def check_context_size(self) -> Tuple[bool, int, str]:
        """
        Check if context is getting too large
        
        Returns:
            (needs_reset, size_kb, message)
        """
        # Check for project-specific conversation files
        if self.project_dir.exists():
            # Find the most recent JSONL file
            jsonl_files = list(self.project_dir.glob("*.jsonl"))
            if jsonl_files:
                # Get the most recently modified file
                most_recent = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                size_bytes = most_recent.stat().st_size
                size_kb = size_bytes // 1024
                
                if size_kb > self.context_limit_kb:
                    return True, size_kb, f"Context too large ({size_kb}KB > {self.context_limit_kb}KB limit)"
                elif size_kb > self.context_limit_kb * 0.8:
                    return False, size_kb, f"Context getting large ({size_kb}KB, approaching {self.context_limit_kb}KB limit)"
                else:
                    return False, size_kb, f"Context size OK ({size_kb}KB)"
        
        return False, 0, "No conversation history found"
    
    def get_session_state(self) -> Dict:
        """Get current session state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "ready_for_continue": False,
            "last_reset": None,
            "mode": None
        }
    
    def _get_current_conversation_file(self) -> Optional[Path]:
        """Get the current conversation JSONL file"""
        if self.project_dir.exists():
            jsonl_files = list(self.project_dir.glob("*.jsonl"))
            if jsonl_files:
                return max(jsonl_files, key=lambda f: f.stat().st_mtime)
        return None
    
    def reset_session(self, mode: str = "soft") -> Dict[str, str]:
        """
        Reset the Claude Code session
        
        Args:
            mode: "soft" (preserve context) or "hard" (complete reset)
            
        Returns:
            Status dictionary with result message
        """
        result = {
            "status": "success",
            "mode": mode,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Get current conversation file
        current_convo = self._get_current_conversation_file()
        
        if mode == "hard" or mode == "soft":
            # For both modes, we need to move the large conversation file
            if current_convo and current_convo.exists():
                # Create backup directory
                backup_dir = self.project_dir / "archived"
                backup_dir.mkdir(exist_ok=True)
                
                # Archive the conversation with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archived_name = f"archived_{timestamp}_{current_convo.name}"
                archived_path = backup_dir / archived_name
                
                # Move the file
                shutil.move(str(current_convo), str(archived_path))
                result["archived"] = str(archived_path)
                result["archived_size"] = f"{archived_path.stat().st_size // 1024}KB"
                
                if mode == "hard":
                    result["message"] = f"Hard reset complete. Conversation archived. Start fresh with next prompt."
                else:
                    result["message"] = f"Soft reset complete. Large conversation archived. Use --continue on next prompt."
            else:
                result["message"] = "No large conversation file found to reset."
        
        # Create reset marker for soft reset
        if mode == "soft" and self.claude_dir.exists():
            reset_marker = {
                "type": "session_reset",
                "mode": mode,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Context reset for continuation"
            }
            
            marker_file = self.claude_dir / "reset_marker.json"
            with open(marker_file, 'w') as f:
                json.dump(reset_marker, f, indent=2)
        
        # Update state file
        state = {
            "ready_for_continue": True,
            "last_reset": datetime.now(timezone.utc).isoformat(),
            "mode": mode
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        return result
    
    def should_use_continue(self) -> bool:
        """Check if next prompt should use --continue"""
        state = self.get_session_state()
        return state.get("ready_for_continue", False)
    
    def mark_continue_used(self):
        """Mark that --continue has been used"""
        state = self.get_session_state()
        state["ready_for_continue"] = False
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_context_summary(self) -> Dict:
        """Get summary of current context state"""
        needs_reset, size_kb, message = self.check_context_size()
        state = self.get_session_state()
        
        # Try to count messages from JSONL file
        message_count = 0
        if self.project_dir.exists():
            jsonl_files = list(self.project_dir.glob("*.jsonl"))
            if jsonl_files:
                most_recent = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                try:
                    # Count lines in JSONL file (each line is a message)
                    with open(most_recent) as f:
                        message_count = sum(1 for _ in f)
                except:
                    pass
        
        return {
            "size_kb": size_kb,
            "message_count": message_count,
            "needs_reset": needs_reset,
            "status_message": message,
            "ready_for_continue": state.get("ready_for_continue", False),
            "last_reset": state.get("last_reset"),
            "recommendation": self._get_recommendation(needs_reset, size_kb)
        }
    
    def _get_recommendation(self, needs_reset: bool, size_kb: int) -> str:
        """Get recommendation for user"""
        if needs_reset:
            return "Run: chorus-reset --soft"
        elif size_kb > self.context_limit_kb * 0.8:
            return "Consider running chorus-reset soon"
        elif self.should_use_continue():
            return "Use --continue on next prompt"
        else:
            return "Context healthy, proceed normally"
    
    def auto_manage(self, message: str) -> Tuple[str, str]:
        """
        Automatically manage the session and return the command to use
        
        Args:
            message: The message to send
            
        Returns:
            (command, explanation)
        """
        needs_reset, size_kb, status = self.check_context_size()
        
        if needs_reset:
            # Auto-reset
            self.reset_session("soft")
            return f"claude --continue '{message}'", "Auto-reset performed, using --continue"
        
        if self.should_use_continue():
            self.mark_continue_used()
            return f"claude --continue '{message}'", "Using --continue after reset"
        
        return f"echo '{message}'", "Normal message"


def main():
    """CLI interface for session management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Greek Chorus Session Manager")
    parser.add_argument("--reset", choices=["soft", "hard"], 
                       help="Reset the session")
    parser.add_argument("--check", action="store_true",
                       help="Check session status")
    parser.add_argument("--auto", type=str,
                       help="Auto-manage and send message")
    
    args = parser.parse_args()
    
    session = GreekChorusSession()
    
    if args.reset:
        result = session.reset_session(args.reset)
        print(f"🎭 Reset complete ({args.reset} mode)")
        print(f"   {result['message']}")
        
    elif args.check:
        summary = session.get_context_summary()
        print("🎭 Greek Chorus Session Status")
        print("━" * 40)
        print(f"Context size: {summary['size_kb']}KB")
        print(f"Messages: {summary['message_count']}")
        print(f"Status: {summary['status_message']}")
        print(f"Ready for --continue: {summary['ready_for_continue']}")
        print(f"Recommendation: {summary['recommendation']}")
        
    elif args.auto:
        command, explanation = session.auto_manage(args.auto)
        print(f"🎭 {explanation}")
        print(f"   Executing: {command}")
        os.system(command)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()