"""Configuration utilities for Terma"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

logger = logging.getLogger(__name__)

# Define available LLM providers and their models
LLM_PROVIDERS = {
    "claude": {
        "name": "Claude",
        "models": [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"}
        ],
        "default": "claude-3-sonnet-20240229"
    },
    "openai": {
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
        ],
        "default": "gpt-4"
    },
    "local": {
        "name": "Local LLM",
        "models": [
            {"id": "mistral-7b", "name": "Mistral 7B"},
            {"id": "llama-2-13b", "name": "LLaMA 2 13B"}
        ],
        "default": "mistral-7b"
    }
}

class Config:
    """Configuration manager for Terma"""
    
    def __init__(self, config_path=None):
        """Initialize the configuration manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.path.expanduser("~/.terma/config.json")
        self.config = {}
        self._load()
        
    def _load(self):
        """Load the configuration file"""
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self.config = {}
        else:
            self._create_default()
            
    def _create_default(self):
        """Create a default configuration"""
        self.config = {
            "terminal": {
                "default_shell": os.environ.get("SHELL", "/bin/bash"),
                "font_size": 14,
                "theme": "dark"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8765
            },
            "llm": {
                "provider": "claude",
                "model": "claude-3-sonnet-20240229",
                "adapter_url": os.environ.get("RHETOR_URL", "http://localhost:8003"),
                "adapter_ws_url": os.environ.get("RHETOR_WS_URL", "ws://localhost:8003/ws"),
                "system_prompt": "You are a terminal assistant that helps users with command-line tasks. Provide concise explanations and suggestions for terminal commands. Focus on being helpful, accurate, and security-conscious."
            }
        }
        self._save()
        
    def _save(self):
        """Save the configuration file"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get(self, key, default=None):
        """Get a configuration value
        
        Args:
            key: The configuration key (can be dot-separated)
            default: Default value if the key doesn't exist
            
        Returns:
            The configuration value
        """
        # Check environment variable first (with TERMA_ prefix)
        env_key = "TERMA_" + key.upper().replace(".", "_")
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
            
        # Then check config file
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def set(self, key, value):
        """Set a configuration value
        
        Args:
            key: The configuration key (can be dot-separated)
            value: The value to set
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save()
        
    def get_all_llm_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get all available LLM providers and their models
        
        Returns:
            Dict of provider information
        """
        return LLM_PROVIDERS
        
    def get_provider_models(self, provider_id: str) -> List[Dict[str, str]]:
        """Get all models for a specific provider
        
        Args:
            provider_id: Provider identifier
            
        Returns:
            List of model information dictionaries
        """
        provider = LLM_PROVIDERS.get(provider_id, {})
        return provider.get("models", [])
