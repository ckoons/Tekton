#!/usr/bin/env python3
"""
StartUp Instructions for Harmonia

This module defines the StartUpInstructions class for structured initialization
of the Harmonia workflow orchestration engine.
"""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from shared.utils.env_config import get_component_config
from shared.env import TektonEnviron

# Configure logging
logger = logging.getLogger(__name__)


def _get_hermes_url() -> str:
    """Get Hermes URL from environment configuration."""
    config = get_component_config()
    hermes_port = getattr(config.hermes, "port", 8001) if hasattr(config, "hermes") else 8001
    hermes_host = TektonEnviron.get("HERMES_HOST", "localhost")
    return f"http://{hermes_host}:{hermes_port}"


@dataclass
class StartUpInstructions:
    """
    Container for instructions passed to Harmonia during startup.
    
    This class provides a standardized format for passing initialization
    parameters, component references, and startup options.
    """
    
    # Component identification
    component_name: str = "harmonia"
    component_id: str = "harmonia.workflow"
    version: str = "0.1.0"
    
    # Startup configuration
    data_directory: str = field(default_factory=lambda: os.path.expanduser("~/.harmonia"))
    config_file: Optional[str] = None
    log_level: str = "INFO"
    
    # Component dependencies
    hermes_url: str = field(default_factory=lambda: _get_hermes_url())
    engram_url: Optional[str] = None
    ergon_url: Optional[str] = None
    prometheus_url: Optional[str] = None
    synthesis_url: Optional[str] = None
    
    # Startup behavior
    auto_register: bool = True
    initialize_db: bool = True
    load_previous_state: bool = True
    
    # Advanced options
    max_workflows: int = 100
    database_type: str = "sqlite"  # 'sqlite', 'postgresql'
    database_url: Optional[str] = None
    
    # Extension points
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the instructions to a dictionary.
        
        Returns:
            Dictionary representation of the instructions
        """
        return asdict(self)
    
    def to_json(self) -> str:
        """
        Convert the instructions to a JSON string.
        
        Returns:
            JSON string representation of the instructions
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StartUpInstructions':
        """
        Create StartUpInstructions from a dictionary.
        
        Args:
            data: Dictionary representation of the instructions
            
        Returns:
            StartUpInstructions instance
        """
        # Filter out keys that aren't in the dataclass to avoid errors
        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StartUpInstructions':
        """
        Create StartUpInstructions from a JSON string.
        
        Args:
            json_str: JSON string representation of the instructions
            
        Returns:
            StartUpInstructions instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'StartUpInstructions':
        """
        Create StartUpInstructions from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            StartUpInstructions instance
        """
        with open(file_path, 'r') as f:
            return cls.from_json(f.read())
    
    def to_file(self, file_path: str) -> None:
        """
        Write the instructions to a JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        with open(file_path, 'w') as f:
            f.write(self.to_json())
    
    def get_database_url(self) -> str:
        """
        Get the database URL, based on the configuration.
        
        Returns:
            Database URL as a string
        """
        if self.database_url:
            return self.database_url
            
        if self.database_type == "sqlite":
            os.makedirs(self.data_directory, exist_ok=True)
            return f"sqlite:///{self.data_directory}/harmonia.db"
        elif self.database_type == "postgresql":
            # Default PostgreSQL connection if not specified
            return "postgresql://harmonia:harmonia@localhost/harmonia"
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")


def fields(cls):
    """Helper function to get fields of a dataclass even when imported from other modules."""
    import dataclasses
    return dataclasses.fields(cls)