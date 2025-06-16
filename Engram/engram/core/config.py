#!/usr/bin/env python3
"""
Engram Configuration Module

Provides configuration management for Engram with support for defaults,
environment variables, and a config file.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("engram.config")

# Default configuration
DEFAULT_CONFIG = {
    # Core settings
    "client_id": "claude",
    "data_dir": os.path.expanduser("~/.engram"),
    
    # Server settings
    "host": "127.0.0.1",
    "port": 8000,
    "mcp_host": "127.0.0.1",
    "mcp_port": 8001,
    "enable_mcp": True,
    
    # Feature settings
    "auto_agency": True,
    "debug": False,
    
    # Memory settings
    "default_importance": 3,
    "max_memories_per_request": 10,
    
    # Advanced settings
    "memory_expiration_days": 90,
    "vector_search_enabled": True,
}

class EngramConfig:
    """Configuration manager for Engram"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration with default values, then load from:
        1. Config file (if exists)
        2. Environment variables
        
        Args:
            config_path: Path to config file (default: ~/.engram/config.json)
        """
        # Initialize with defaults
        self.config = DEFAULT_CONFIG.copy()
        
        # Determine config path
        self.config_path = config_path or os.path.join(
            os.path.expanduser(self.config["data_dir"]), 
            "config.json"
        )
        
        # Load configuration from file if it exists
        self._load_config_from_file()
        
        # Override with environment variables
        self._load_config_from_env()
    
    def _load_config_from_file(self) -> None:
        """Load configuration from JSON file if it exists"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                    logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")
    
    def _load_config_from_env(self) -> None:
        """Override configuration with environment variables"""
        # Environment variable format: ENGRAM_UPPER_CASE_SETTING
        # Example: ENGRAM_CLIENT_ID=custom-id
        for key in self.config.keys():
            env_key = f"ENGRAM_{key.upper()}"
            if env_key in os.environ:
                # Convert value to appropriate type based on default
                default_type = type(self.config[key])
                try:
                    if default_type == bool:
                        # Special handling for boolean values
                        val = os.environ[env_key].lower()
                        self.config[key] = val in ('true', 'yes', '1', 'y')
                    elif default_type == int:
                        self.config[key] = int(os.environ[env_key])
                    else:
                        self.config[key] = default_type(os.environ[env_key])
                    logger.debug(f"Set {key}={self.config[key]} from environment")
                except Exception as e:
                    logger.warning(f"Error processing environment variable {env_key}: {e}")
    
    def save(self) -> bool:
        """Save current configuration to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, values: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(values)
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax"""
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary syntax"""
        self.config[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Check if configuration contains key"""
        return key in self.config
    
    def __repr__(self) -> str:
        """String representation"""
        return f"EngramConfig({self.config})"


# Global configuration instance
_config_instance = None

def get_config(config_path: Optional[str] = None) -> EngramConfig:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = EngramConfig(config_path)
    return _config_instance


if __name__ == "__main__":
    # If run directly, print current configuration
    import argparse
    
    parser = argparse.ArgumentParser(description="Engram Configuration Utility")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--save", action="store_true", help="Save current config to file")
    parser.add_argument("--set", nargs=2, action="append", metavar=("KEY", "VALUE"), 
                       help="Set configuration value (can be used multiple times)")
    args = parser.parse_args()
    
    # Configure logging for direct execution
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    config = get_config(args.config)
    
    # Set values if specified
    if args.set:
        for key, value in args.set:
            # Try to convert to appropriate type
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            config.set(key, value)
    
    # Save if requested
    if args.save:
        config.save()
    
    # Print current config
    print(json.dumps(config.config, indent=2))