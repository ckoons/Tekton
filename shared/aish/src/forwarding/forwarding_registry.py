"""
AI Forwarding Registry for aish.

Manages the forwarding table that routes CI messages to human terminals.
"""

import json
import os
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from shared.env import TektonEnviron

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator


class ForwardingRegistry:
    """Manages CI message forwarding configuration."""
    
    def __init__(self):
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        self.config_dir = Path(tekton_root) / '.tekton' / 'aish'
        self.config_file = self.config_dir / 'forwarding.json'
        self.forwards = self.load()
    
    @state_checkpoint(
        title="Forward Configuration Load",
        description="Loads and normalizes forwarding configuration with JSON mode support",
        state_type="configuration",
        validation="All forwards normalized to dict format"
    )
    def load(self) -> Dict[str, any]:
        """Load forwarding configuration from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    data = json.load(f)
                    forwards = data.get('forwards', {})
                    # Convert old string format to new dict format for backward compatibility
                    normalized = {}
                    for key, value in forwards.items():
                        if isinstance(value, str):
                            # Old format: just terminal name
                            normalized[key] = {"terminal": value, "json_mode": False}
                        else:
                            # New format: dict with terminal and json_mode
                            normalized[key] = value
                    return normalized
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
    
    @api_contract(
        title="Forward Rule Registration",
        description="Registers AI-to-terminal forwarding with optional JSON mode",
        endpoint="internal",
        method="function",
        request_schema={"ai_name": "string", "terminal_name": "string", "json_mode": "boolean"},
        response_schema={"success": "boolean"}
    )
    def set_forward(self, ai_name: str, terminal_name: str, json_mode: bool = False):
        """Forward CI messages to terminal."""
        self.forwards[ai_name] = {"terminal": terminal_name, "json_mode": json_mode}
        self.save()
    
    def remove_forward(self, ai_name: str):
        """Stop forwarding CI messages."""
        if ai_name in self.forwards:
            del self.forwards[ai_name]
            self.save()
    
    def get_forward(self, ai_name: str) -> Optional[str]:
        """Get forwarding destination for CI (returns terminal name for backward compatibility)."""
        forward_config = self.forwards.get(ai_name)
        if forward_config:
            if isinstance(forward_config, dict):
                return forward_config.get("terminal")
            else:
                # Shouldn't happen after load() normalization, but handle just in case
                return forward_config
        return None
    
    @api_contract(
        title="Forward Configuration Retrieval",
        description="Gets full forwarding configuration including JSON mode flag",
        endpoint="internal",
        method="function",
        request_schema={"ai_name": "string"},
        response_schema={"terminal": "string", "json_mode": "boolean"}
    )
    def get_forward_config(self, ai_name: str) -> Optional[Dict[str, any]]:
        """Get full forwarding configuration for CI including JSON mode."""
        return self.forwards.get(ai_name)
    
    def list_forwards(self) -> Dict[str, str]:
        """Get all active forwards."""
        return self.forwards.copy()