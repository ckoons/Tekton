"""
Structured log entry for the Tekton Centralized Logging System.

This module defines the LogEntry class, which represents a single log entry with
standardized fields and serialization methods.
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

from hermes.core.logging.base.levels import LogLevel


@dataclass
class LogEntry:
    """
    Structured log entry with standardized fields.
    
    This class represents a single log entry in the Centralized Logging System,
    with all required metadata and content fields.
    """
    
    # Metadata fields
    timestamp: float = field(default_factory=time.time)
    effective_timestamp: Optional[float] = None
    component: str = ""
    level: LogLevel = LogLevel.INFO
    schema_version: str = "1.0.0"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: Optional[str] = None
    
    # Content fields
    message: str = ""
    code: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values after creation."""
        # Set effective_timestamp to timestamp if not provided
        if self.effective_timestamp is None:
            self.effective_timestamp = self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        result = asdict(self)
        # Convert Enum to string representation
        result["level"] = self.level.name
        return result
    
    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create log entry from dictionary."""
        # Convert level string to Enum
        if "level" in data and isinstance(data["level"], str):
            data["level"] = LogLevel.from_string(data["level"])
        
        # Create instance
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LogEntry':
        """Create log entry from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)