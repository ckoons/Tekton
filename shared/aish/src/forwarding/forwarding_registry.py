"""
AI Forwarding Registry for aish.

Manages the forwarding table that routes AI messages to human terminals.
"""

import json
import os
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class ForwardingRegistry:
    """Manages AI message forwarding configuration."""
    
    def __init__(self):
        tekton_root = os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        self.config_dir = Path(tekton_root) / '.tekton' / 'aish'
        self.config_file = self.config_dir / 'forwarding.json'
        self.forwards = self.load()
    
    def load(self) -> Dict[str, str]:
        """Load forwarding configuration from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    data = json.load(f)
                    return data.get('forwards', {})
            except Exception:
                return {}
        return {}
    
    def save(self):
        """Save forwarding configuration to disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        data = {
            'version': '1.0',
            'forwards': self.forwards,
            'last_updated': datetime.now().isoformat()
        }
        
        # Atomic write with file locking
        temp_file = self.config_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
        
        # Replace original file
        temp_file.replace(self.config_file)
    
    def set_forward(self, ai_name: str, terminal_name: str):
        """Forward AI messages to terminal."""
        self.forwards[ai_name] = terminal_name
        self.save()
    
    def remove_forward(self, ai_name: str):
        """Stop forwarding AI messages."""
        if ai_name in self.forwards:
            del self.forwards[ai_name]
            self.save()
    
    def get_forward(self, ai_name: str) -> Optional[str]:
        """Get forwarding destination for AI."""
        return self.forwards.get(ai_name)
    
    def list_forwards(self) -> Dict[str, str]:
        """Get all active forwards."""
        return self.forwards.copy()