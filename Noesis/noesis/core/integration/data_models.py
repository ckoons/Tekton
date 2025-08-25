"""
Data models for integration between Noesis and other Tekton components
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import numpy as np


@dataclass
class CollectiveState:
    """
    Represents the state of a collective CI system at a point in time
    """
    timestamp: datetime
    n_agents: int
    state_vector: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'n_agents': self.n_agents,
            'state': self.state_vector.tolist(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollectiveState':
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            n_agents=data['n_agents'],
            state_vector=np.array(data['state']),
            metadata=data.get('metadata', {})
        )


@dataclass
class EngramStream:
    """
    Represents a stream of memory/state data from Engram
    """
    stream_id: str
    source: str  # Which CI or collective
    stream_type: str  # continuous, snapshot, event-based
    dimensions: int
    sampling_rate: float  # Hz
    buffer_size: int = 1000
    data_buffer: List[CollectiveState] = field(default_factory=list)
    
    def add_state(self, state: CollectiveState):
        """Add state to buffer, maintaining size limit"""
        self.data_buffer.append(state)
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)
    
    def get_recent_states(self, n: int) -> List[CollectiveState]:
        """Get n most recent states"""
        return self.data_buffer[-n:] if n <= len(self.data_buffer) else self.data_buffer
    
    def to_array(self) -> np.ndarray:
        """Convert buffer to numpy array for analysis"""
        if not self.data_buffer:
            return np.array([])
        return np.array([state.state_vector for state in self.data_buffer])


@dataclass
class TheoryExperimentLink:
    """
    Links theoretical predictions with experimental validations
    """
    link_id: str
    theory_id: str  # From Noesis
    experiment_id: str  # From Sophia
    predictions: Dict[str, Any]
    validation_metrics: List[str]
    status: str = "pending"
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    validated_at: Optional[datetime] = None
    
    def update_results(self, results: Dict[str, Any]):
        """Update with experimental results"""
        self.results = results
        self.validated_at = datetime.now()
        self.status = "completed"


@dataclass
class AnalysisRequest:
    """
    Request for theoretical analysis from other components
    """
    request_id: str
    source_component: str
    analysis_type: str
    data: Dict[str, Any]
    priority: str = "normal"
    callback_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'source_component': self.source_component,
            'analysis_type': self.analysis_type,
            'data': self.data,
            'priority': self.priority,
            'callback_url': self.callback_url,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class VisualizationRequest:
    """
    Request for visualization of theoretical analysis
    """
    viz_id: str
    analysis_type: str
    data: Dict[str, Any]
    viz_type: str  # manifold_3d, regime_timeline, catastrophe_surface, etc.
    options: Dict[str, Any] = field(default_factory=dict)
    target_component: str = "ui"  # Where to send visualization
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'viz_id': self.viz_id,
            'analysis_type': self.analysis_type,
            'data': self.data,
            'viz_type': self.viz_type,
            'options': self.options,
            'target_component': self.target_component
        }