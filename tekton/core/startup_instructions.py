#!/usr/bin/env python3
"""
Startup Instructions - Standardized format for component initialization.

This module provides the StartUpInstructions class for passing
initialization parameters to components during startup.
"""

import json
import os
from shared.env import TektonEnviron
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

class StartUpInstructions:
    """
    Container for instructions passed to components during startup.
    
    This class provides a standardized format for components to exchange
    initialization parameters, activation triggers, and startup options.
    """
    
    def __init__(self, 
                component_id: str,
                component_type: str,
                data_directory: str,
                dependencies: List[str] = None,
                register: bool = True,
                capabilities: List[Dict[str, Any]] = None,
                metadata: Dict[str, Any] = None,
                sender_id: str = "tekton_launcher",
                timestamp: Optional[str] = None,
                activation_mode: str = "immediate",
                activation_trigger: Optional[str] = None,
                timeout: int = 30,
                hermes_url: Optional[str] = None,
                priority: int = 5):
        """
        Initialize new startup instructions.
        
        Args:
            component_id: ID of the component to start
            component_type: Type of component (e.g., 'harmonia', 'synthesis')
            data_directory: Directory for component data
            dependencies: List of component IDs that must be running
            register: Whether to register with Hermes
            capabilities: List of component capabilities
            metadata: Component metadata
            sender_id: ID of the component sending the instructions
            timestamp: ISO format timestamp (default: current time)
            activation_mode: When to activate ('immediate', 'trigger', 'manual')
            activation_trigger: Event/message that triggers activation
            timeout: Timeout in seconds for component startup
            hermes_url: URL for Hermes registration
            priority: Priority level (1-10, higher is more important)
        """
        self.component_id = component_id
        self.component_type = component_type
        self.data_directory = data_directory
        self.dependencies = dependencies or []
        self.register = register
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.sender_id = sender_id
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.activation_mode = activation_mode
        self.activation_trigger = activation_trigger
        self.timeout = timeout
        self.hermes_url = hermes_url or TektonEnviron.get("HERMES_URL", "http://localhost:5000/api")
        self.priority = max(1, min(10, priority))  # Clamp between 1 and 10
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert instructions to a dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "data_directory": self.data_directory,
            "dependencies": self.dependencies,
            "register": self.register,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "activation_mode": self.activation_mode,
            "activation_trigger": self.activation_trigger,
            "timeout": self.timeout,
            "hermes_url": self.hermes_url,
            "priority": self.priority
        }
        
    def to_json(self) -> str:
        """
        Convert instructions to JSON string.
        
        Returns:
            JSON representation
        """
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StartUpInstructions':
        """
        Create instructions from a dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            StartUpInstructions instance
        """
        return cls(
            component_id=data.get("component_id", ""),
            component_type=data.get("component_type", ""),
            data_directory=data.get("data_directory", ""),
            dependencies=data.get("dependencies", []),
            register=data.get("register", True),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {}),
            sender_id=data.get("sender_id", "tekton_launcher"),
            timestamp=data.get("timestamp"),
            activation_mode=data.get("activation_mode", "immediate"),
            activation_trigger=data.get("activation_trigger"),
            timeout=data.get("timeout", 30),
            hermes_url=data.get("hermes_url"),
            priority=data.get("priority", 5)
        )
        
    @classmethod
    def from_json(cls, json_str: str) -> 'StartUpInstructions':
        """
        Create instructions from a JSON string.
        
        Args:
            json_str: JSON representation
            
        Returns:
            StartUpInstructions instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save instructions to a file.
        
        Args:
            file_path: Path to save the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, file_path: str) -> 'StartUpInstructions':
        """
        Load instructions from a file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            StartUpInstructions instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        return cls.from_dict(data)