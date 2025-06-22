"""
Base Landmark class and types
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
import json


@dataclass
class Landmark:
    """Base landmark class for marking important code locations"""
    
    # Required fields
    id: str
    type: str  # architecture_decision, performance_boundary, etc.
    title: str
    description: str
    file_path: str
    line_number: int
    
    # Auto-populated fields
    timestamp: datetime = field(default_factory=datetime.now)
    author: str = field(default="system")
    
    # Optional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_landmarks: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, type: str, title: str, description: str = "", **kwargs) -> 'Landmark':
        """Factory method for creating landmarks with auto-generated ID"""
        landmark_id = kwargs.pop('id', str(uuid.uuid4()))
        
        return cls(
            id=landmark_id,
            type=type,
            title=title,
            description=description,
            timestamp=datetime.now(),
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert landmark to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'timestamp': self.timestamp.isoformat(),
            'author': self.author,
            'metadata': self.metadata,
            'tags': self.tags,
            'related_landmarks': self.related_landmarks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Landmark':
        """Create landmark from dictionary"""
        # Handle timestamp conversion
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @property
    def component(self) -> str:
        """Extract component name from file path"""
        path = Path(self.file_path)
        # Find Tekton component (e.g., Hermes, Apollo, etc.)
        for part in path.parts:
            if part in ['Hermes', 'Apollo', 'Engram', 'Athena', 'Prometheus', 
                       'Budget', 'Harmonia', 'Rhetor', 'Sophia', 'Telos', 
                       'shared', 'Ergon', 'Synthesis', 'Metis', 'Terma']:
                return part
        return 'unknown'
    
    def __str__(self) -> str:
        return f"[{self.type}] {self.title} ({self.file_path}:{self.line_number})"


# Specific landmark types with additional fields

@dataclass
class ArchitectureDecision(Landmark):
    """Marks architectural decisions in code"""
    
    def __post_init__(self):
        self.type = "architecture_decision"
        # Extract from metadata
        self.alternatives_considered = self.metadata.get('alternatives_considered', [])
        self.rationale = self.metadata.get('rationale', '')
        self.impacts = self.metadata.get('impacts', [])
        self.decided_by = self.metadata.get('decided_by', self.author)
        self.decision_date = self.metadata.get('date', self.timestamp.date().isoformat())


@dataclass 
class PerformanceBoundary(Landmark):
    """Marks performance-critical code sections"""
    
    def __post_init__(self):
        self.type = "performance_boundary"
        # Extract from metadata
        self.sla = self.metadata.get('sla', '')
        self.optimization_notes = self.metadata.get('optimization_notes', '')
        self.metrics = self.metadata.get('metrics', {})


@dataclass
class APIContract(Landmark):
    """Marks API boundaries and contracts"""
    
    def __post_init__(self):
        self.type = "api_contract"
        # Extract from metadata
        self.endpoint = self.metadata.get('endpoint', '')
        self.method = self.metadata.get('method', '')
        self.request_schema = self.metadata.get('request_schema', {})
        self.response_schema = self.metadata.get('response_schema', {})
        self.auth_required = self.metadata.get('auth_required', False)


@dataclass
class DangerZone(Landmark):
    """Marks complex or risky code sections"""
    
    def __post_init__(self):
        self.type = "danger_zone"
        # Extract from metadata
        self.risk_level = self.metadata.get('risk_level', 'medium')
        self.risks = self.metadata.get('risks', [])
        self.mitigation = self.metadata.get('mitigation', '')
        self.review_required = self.metadata.get('review_required', False)


@dataclass
class IntegrationPoint(Landmark):
    """Marks where components integrate"""
    
    def __post_init__(self):
        self.type = "integration_point"
        # Extract from metadata
        self.source_component = self.metadata.get('source_component', self.component)
        self.target_component = self.metadata.get('target_component', '')
        self.protocol = self.metadata.get('protocol', '')
        self.data_flow = self.metadata.get('data_flow', '')


@dataclass
class StateCheckpoint(Landmark):
    """Marks important state management points"""
    
    def __post_init__(self):
        self.type = "state_checkpoint"
        # Extract from metadata
        self.state_type = self.metadata.get('state_type', '')
        self.persistence = self.metadata.get('persistence', False)
        self.consistency_requirements = self.metadata.get('consistency_requirements', '')
        self.recovery_strategy = self.metadata.get('recovery_strategy', '')