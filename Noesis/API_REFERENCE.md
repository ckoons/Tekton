# Noesis Theoretical Analysis - API Reference

This document provides detailed API reference for the Noesis theoretical analysis framework components.

## Core Classes

### MathematicalFramework (Base Class)

**Location**: `noesis.core.theoretical.base`

```python
class MathematicalFramework:
    """Base class for all theoretical analysis components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    async def analyze(self, data: Any, **kwargs) -> AnalysisResult
    async def validate_data(self, data: np.ndarray) -> Tuple[bool, List[str]]
    def normalize_data(self, data: np.ndarray, method: str = 'standard') -> np.ndarray
    def compute_distance_matrix(self, points: np.ndarray, metric: str = 'euclidean') -> np.ndarray
    def estimate_dimensionality(self, data: np.ndarray, method: str = 'pca_explained_variance') -> int
    def check_numerical_stability(self, result: Any) -> List[str]
    async def prepare_results(self, data: Dict[str, Any], analysis_type: str, 
                             metadata: Optional[Dict[str, Any]] = None,
                             warnings: Optional[List[str]] = None) -> AnalysisResult
```

**Configuration Parameters**:
```python
config = {
    'epsilon': 1e-10,              # Numerical tolerance
    'max_iterations': 1000,        # Maximum iterations for iterative algorithms
    'validate_inputs': True,       # Enable input validation
    'check_stability': True,       # Enable numerical stability checks
    'variance_threshold': 0.95     # Explained variance threshold for dimensionality
}
```

### AnalysisResult

**Location**: `noesis.core.theoretical.base`

```python
@dataclass
class AnalysisResult:
    """Standard result format for all theoretical analyses"""
    analysis_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]
```

## Manifold Analysis

### ManifoldAnalyzer

**Location**: `noesis.core.theoretical.manifold`

```python
class ManifoldAnalyzer(MathematicalFramework):
    """Analyzes geometric structure of collective AI state spaces"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    async def analyze(self, data: np.ndarray, **kwargs) -> AnalysisResult
    async def analyze_collective_manifold(self, states: np.ndarray,
                                        n_components: Optional[int] = None) -> ManifoldStructure
    async def compute_intrinsic_dimension(self, data: np.ndarray) -> int
    async def estimate_local_dimensions(self, data: np.ndarray, k: int = 15) -> List[int]
    async def compute_alternative_embedding(self, data: np.ndarray, 
                                          n_components: int) -> np.ndarray
    async def analyze_topology(self, embedding: np.ndarray) -> Dict[str, float]
    async def estimate_manifold_curvature(self, embedding: np.ndarray) -> np.ndarray
    async def identify_trajectory_patterns(self, trajectory: np.ndarray) -> TrajectoryAnalysis
    async def detect_cyclic_patterns(self, trajectory: np.ndarray) -> List[Dict[str, Any]]
    async def identify_manifold_regimes(self, embedding: np.ndarray) -> np.ndarray
```

**Configuration Parameters**:
```python
config = {
    'variance_threshold': 0.95,     # Explained variance threshold
    'min_dimension': 2,             # Minimum intrinsic dimension
    'max_dimension': 50,            # Maximum intrinsic dimension
    'embedding_method': 'pca',      # 'pca', 'tsne', 'lle'
    'n_neighbors': 15               # Neighbors for local methods
}
```

**Input Data**:
```python
# Collective state data
data = np.ndarray  # Shape: (n_samples, n_features)
# - n_samples: Number of time points or observations
# - n_features: Dimensionality of collective state space
```

**Return Data**:
```python
result.data = {
    'manifold_structure': {
        'intrinsic_dimension': int,
        'principal_components': List[List[float]],
        'explained_variance': List[float],
        'embedding_coordinates': List[List[float]],
        'topology_metrics': {
            'mean_local_density': float,
            'density_variance': float,
            'connectivity': float,
            'mean_curvature': float,
            'curvature_variance': float
        },
        'regime_assignments': Optional[List[int]]
    },
    'original_dimensions': int,
    'n_samples': int
}
```

### ManifoldStructure

```python
@dataclass
class ManifoldStructure:
    """Results of manifold analysis"""
    intrinsic_dimension: int
    principal_components: np.ndarray
    explained_variance: np.ndarray
    embedding_coordinates: np.ndarray
    topology_metrics: Dict[str, float] = field(default_factory=dict)
    regime_assignments: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]
```

### TrajectoryAnalysis

```python
@dataclass 
class TrajectoryAnalysis:
    """Analysis of trajectory patterns in manifold"""
    trajectory_length: float
    curvature: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    turning_points: List[int]
    cyclic_patterns: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]
```

## Dynamics Analysis

### DynamicsAnalyzer

**Location**: `noesis.core.theoretical.dynamics`

```python
class DynamicsAnalyzer(MathematicalFramework):
    """Analyzes dynamical properties using SLDS"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    async def analyze(self, data: np.ndarray, **kwargs) -> AnalysisResult
    async def fit_slds_model(self, time_series: np.ndarray,
                           n_regimes: int = 4) -> SLDSModel
    async def initialize_slds_parameters(self, data: np.ndarray, 
                                       n_regimes: int) -> SLDSModel
    async def slds_e_step(self, model: SLDSModel, 
                         data: np.ndarray) -> Tuple[np.ndarray, float]
    async def slds_m_step(self, model: SLDSModel, data: np.ndarray, 
                         gamma: np.ndarray) -> SLDSModel
    async def identify_regimes(self, model: SLDSModel, 
                             data: np.ndarray) -> RegimeIdentification
    async def viterbi_decode(self, model: SLDSModel, 
                           data: np.ndarray) -> List[int]
    def compute_average_duration(self, regime_mask: np.ndarray) -> float
    async def predict_transitions(self, model: SLDSModel, current_regime: int,
                                current_probs: np.ndarray, horizon: int = 10) -> List[Dict[str, Any]]
    async def analyze_regime_stability(self, model: SLDSModel,
                                     regime_sequence: List[int]) -> Dict[str, Any]
```

**Configuration Parameters**:
```python
config = {
    'n_regimes': 4,                 # Number of discrete regimes
    'em_iterations': 50,            # EM algorithm iterations
    'convergence_threshold': 1e-4,  # Convergence tolerance
    'min_regime_duration': 10,      # Minimum regime duration
    'transition_threshold': 0.7     # Transition probability threshold
}
```

**Input Data**:
```python
# Time series data
data = np.ndarray  # Shape: (n_timesteps, n_features)
# - n_timesteps: Number of time points
# - n_features: Dimensionality of system state
```

**Return Data**:
```python
result.data = {
    'slds_model': {
        'n_regimes': int,
        'transition_matrices': Dict[str, List[List[float]]],
        'observation_matrices': Dict[str, List[List[float]]],
        'transition_probabilities': List[List[float]],
        'model_type': 'SLDS'
    },
    'regime_identification': {
        'current_regime': int,
        'regime_probabilities': List[float],
        'regime_sequence': List[int],
        'transition_points': List[int],
        'stability_scores': Dict[str, float],
        'predicted_transitions': List[Dict[str, Any]]
    },
    'stability_analysis': Dict[str, Any],
    'n_timesteps': int,
    'n_features': int
}
```

### SLDSModel

```python
@dataclass
class SLDSModel:
    """Switching Linear Dynamical System model"""
    n_regimes: int
    transition_matrices: Dict[int, np.ndarray]
    observation_matrices: Dict[int, np.ndarray]
    process_noise: Dict[int, np.ndarray]
    observation_noise: Dict[int, np.ndarray]
    transition_probabilities: np.ndarray
    initial_state_means: Dict[int, np.ndarray]
    initial_state_covariances: Dict[int, np.ndarray]
    
    def to_dict(self) -> Dict[str, Any]
```

### RegimeIdentification

```python
@dataclass
class RegimeIdentification:
    """Results of regime identification analysis"""
    current_regime: int
    regime_probabilities: np.ndarray
    regime_sequence: List[int]
    transition_points: List[int]
    stability_scores: Dict[int, float]
    predicted_transitions: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]
```

## Catastrophe Analysis

### CatastropheAnalyzer

**Location**: `noesis.core.theoretical.catastrophe`

```python
class CatastropheAnalyzer(MathematicalFramework):
    """Analyzes critical transitions using catastrophe theory"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    async def analyze(self, data: Any, **kwargs) -> AnalysisResult
    async def detect_critical_transitions(self, manifold: Optional[Dict[str, Any]],
                                        dynamics: Optional[Dict[str, Any]], 
                                        trajectory: Optional[np.ndarray]) -> List[CriticalPoint]
    async def detect_trajectory_transitions(self, trajectory: np.ndarray) -> List[CriticalPoint]
    async def detect_dynamics_bifurcations(self, dynamics: Dict[str, Any]) -> List[CriticalPoint]
    async def detect_manifold_singularities(self, manifold: Dict[str, Any]) -> List[CriticalPoint]
    async def classify_transition_type(self, trajectory: np.ndarray, 
                                     transition_idx: int) -> str
    async def analyze_stability_landscape(self, embedding: np.ndarray) -> StabilityLandscape
    async def estimate_potential_surface(self, points: np.ndarray, 
                                       X: np.ndarray, Y: np.ndarray) -> np.ndarray
    async def identify_stability_regions(self, potential: np.ndarray,
                                       X: np.ndarray, Y: np.ndarray) -> Tuple[List[Dict], List[Dict]]
    async def compute_early_warning_signals(self, trajectory: Optional[np.ndarray]) -> Dict[str, Any]
    def merge_nearby_critical_points(self, critical_points: List[CriticalPoint],
                                   distance_threshold: float = 0.1) -> List[CriticalPoint]
```

**Configuration Parameters**:
```python
config = {
    'window_size': 50,              # Window size for rolling analysis
    'warning_threshold': 2.0,       # Standard deviations for warning signals
    'potential_resolution': 100,    # Resolution for potential surface
    'catastrophe_types': ['fold', 'cusp', 'swallowtail', 'butterfly']
}
```

**Input Data**:
```python
# Multi-component data
data = {
    'trajectory': np.ndarray,       # Shape: (n_points, n_dimensions)
    'manifold': Dict[str, Any],     # Manifold analysis results
    'dynamics': Dict[str, Any]      # Dynamics analysis results
}

# Or single trajectory
data = np.ndarray  # Shape: (n_points, n_dimensions)
```

**Return Data**:
```python
result.data = {
    'critical_points': List[{
        'location': List[float],
        'transition_type': str,
        'stability_change': Dict[str, float],
        'warning_signals': List[str],
        'control_parameters': Dict[str, float],
        'confidence': float
    }],
    'stability_landscape': Optional[{
        'potential_surface_shape': List[int],
        'n_stable_regions': int,
        'n_unstable_regions': int,
        'stable_regions': List[Dict[str, Any]],
        'unstable_regions': List[Dict[str, Any]]
    }],
    'early_warning_signals': {
        'variance_trend': float,
        'variance_increasing': bool,
        'autocorrelation_trend': float,
        'critical_slowing_down': bool,
        'mean_skewness': float,
        'skewness_variance': float,
        'composite_warning_score': float,
        'warning_level': str  # 'low', 'medium', 'high'
    },
    'n_critical_points': int
}
```

### CriticalPoint

```python
@dataclass
class CriticalPoint:
    """Identified critical transition point"""
    location: np.ndarray
    transition_type: str
    stability_change: Dict[str, float]
    warning_signals: List[str]
    control_parameters: Dict[str, float]
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]
```

### StabilityLandscape

```python
@dataclass
class StabilityLandscape:
    """Stability landscape analysis results"""
    potential_surface: np.ndarray
    stable_regions: List[Dict[str, Any]]
    unstable_regions: List[Dict[str, Any]]
    separatrices: List[np.ndarray]
    basin_boundaries: List[np.ndarray]
    gradient_field: np.ndarray
    
    def to_dict(self) -> Dict[str, Any]
```

## Synthesis Analysis

### SynthesisAnalyzer

**Location**: `noesis.core.theoretical.synthesis`

```python
class SynthesisAnalyzer(MathematicalFramework):
    """Synthesizes findings to extract universal principles"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    async def analyze(self, data: Dict[str, Any], **kwargs) -> AnalysisResult
    async def extract_universal_principles(self, multi_scale_data: Dict[str, Any]) -> List[UniversalPrinciple]
    async def check_collective_intelligence_principle(self, data: Dict[str, Any]) -> Optional[UniversalPrinciple]
    async def find_scaling_laws(self, data: Dict[str, Any]) -> List[UniversalPrinciple]
    async def fit_power_law(self, x: np.ndarray, y: np.ndarray) -> Tuple[float, float]
    async def find_fractal_patterns(self, data: Dict[str, Any]) -> List[UniversalPrinciple]
    async def analyze_dimensional_patterns(self, data: Dict[str, Any]) -> List[UniversalPrinciple]
    async def find_conservation_laws(self, data: Dict[str, Any]) -> List[UniversalPrinciple]
    async def analyze_scaling_properties(self, data: Dict[str, Any]) -> Optional[ScalingAnalysis]
    async def identify_emergent_properties(self, data: Dict[str, Any]) -> List[Dict[str, Any]]
    async def find_cross_scale_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]
```

**Configuration Parameters**:
```python
config = {
    'min_scale_ratio': 10,          # Minimum ratio between scales
    'confidence_threshold': 0.8,    # Confidence threshold for principles
    'n_bootstrap': 100,             # Bootstrap samples for statistics
    'known_patterns': {             # Known collective intelligence patterns
        'collective_phase_transitions': {
            'n_agents': [12, 8000, 80000],
            'properties': ['AGI', 'clustering', 'hierarchical']
        }
    }
}
```

**Input Data**:
```python
# Multi-scale analysis results
data = {
    'scale_name_1': {
        'n_agents': int,
        'intrinsic_dimension': int,
        'analysis_data': Dict[str, Any],
        # ... other scale-specific metrics
    },
    'scale_name_2': {
        # ... similar structure
    }
    # ... more scales
}
```

**Return Data**:
```python
result.data = {
    'universal_principles': List[{
        'principle_type': str,
        'description': str,
        'mathematical_form': str,
        'parameters': Dict[str, float],
        'validity_range': Dict[str, Any],
        'confidence': float,
        'evidence': List[Dict[str, Any]]
    }],
    'scaling_analysis': Optional[{
        'scaling_exponents': Dict[str, float],
        'fractal_dimensions': Dict[str, float],
        'self_similarity_scores': Dict[str, float],
        'scale_invariant_features': List[str],
        'critical_exponents': Dict[str, float]
    }],
    'emergent_properties': List[{
        'property': str,
        'emerges_at_scale': str,
        'emergence_size': int,
        'value': Any
    }],
    'cross_scale_patterns': List[{
        'type': str,
        'scales': List[str],
        'size_ratio': float,
        'relationship': str
    }],
    'n_principles_found': int
}
```

### UniversalPrinciple

```python
@dataclass
class UniversalPrinciple:
    """Identified universal principle or pattern"""
    principle_type: str
    description: str
    mathematical_form: str
    parameters: Dict[str, float]
    validity_range: Dict[str, Any]
    confidence: float
    evidence: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]
```

### ScalingAnalysis

```python
@dataclass
class ScalingAnalysis:
    """Results of scaling analysis"""
    scaling_exponents: Dict[str, float]
    fractal_dimensions: Dict[str, float]
    self_similarity_scores: Dict[str, float]
    scale_invariant_features: List[str]
    critical_exponents: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]
```

## Integration Classes

### NoesisComponent Integration

**Location**: `noesis.core.noesis_component`

```python
class NoesisComponent:
    """Main Noesis component with theoretical analysis capabilities"""
    
    async def init(self)
    async def get_theoretical_insights(self) -> Dict[str, Any]
    async def start_streaming(self) -> bool
    async def stop_streaming(self) -> bool
    async def get_stream_status(self) -> Dict[str, Any]
    def get_capabilities(self) -> List[str]
    def get_metadata(self) -> Dict[str, Any]
    async def shutdown(self)
```

**Theoretical Framework Access**:
```python
component = NoesisComponent()
await component.init()

# Access individual analyzers
manifold_analyzer = component.theoretical_framework.manifold_analyzer
dynamics_analyzer = component.theoretical_framework.dynamics_analyzer
catastrophe_analyzer = component.theoretical_framework.catastrophe_analyzer
synthesis_analyzer = component.theoretical_framework.synthesis_analyzer
```

### Streaming Integration

**Location**: `noesis.core.integration.stream_manager`

```python
class TheoreticalStreamManager:
    """Manages streaming theoretical analysis"""
    
    async def initialize(self, config: Dict[str, Any])
    async def start_streaming(self) -> bool
    async def stop_streaming(self) -> bool
    def get_stream_status(self) -> Dict[str, Any]
    async def get_theoretical_insights(self) -> Dict[str, Any]
    def get_analysis_results(self) -> Dict[str, Any]
```

## REST API Endpoints

### Analysis Endpoints

```http
POST /api/analysis/manifold
Content-Type: application/json

{
    "data": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
    "config": {
        "embedding_method": "pca",
        "variance_threshold": 0.95
    }
}
```

```http
POST /api/analysis/dynamics
Content-Type: application/json

{
    "data": [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]],
    "config": {
        "n_regimes": 3,
        "em_iterations": 50
    }
}
```

```http
POST /api/analysis/catastrophe
Content-Type: application/json

{
    "trajectory": [[1.0, 2.0], [2.0, 3.0]],
    "manifold": {...},
    "dynamics": {...},
    "config": {
        "window_size": 50
    }
}
```

```http
POST /api/analysis/synthesis
Content-Type: application/json

{
    "multi_scale_data": {
        "small": {"n_agents": 50, "intrinsic_dimension": 3},
        "large": {"n_agents": 5000, "intrinsic_dimension": 7}
    },
    "config": {
        "confidence_threshold": 0.8
    }
}
```

### Streaming Endpoints

```http
GET /api/streaming/status
```

```http
POST /api/streaming/start
Content-Type: application/json

{
    "config": {
        "poll_interval": 5.0,
        "analysis_window": 100
    }
}
```

```http
POST /api/streaming/stop
```

```http
GET /api/streaming/insights
```

### Response Format

All API endpoints return standardized responses:

```json
{
    "success": true,
    "analysis_type": "manifold_analysis",
    "timestamp": "2024-01-01T12:00:00Z",
    "data": {
        // Analysis-specific results
    },
    "metadata": {
        "execution_time": 1.23,
        "configuration": {...}
    },
    "confidence": 0.95,
    "warnings": []
}
```

## Error Handling

### Exception Types

```python
# Custom exceptions
class NoesisAnalysisError(Exception):
    """Base exception for analysis errors"""
    pass

class DataValidationError(NoesisAnalysisError):
    """Invalid input data"""
    pass

class ConvergenceError(NoesisAnalysisError):
    """Algorithm convergence failure"""
    pass

class NumericalInstabilityError(NoesisAnalysisError):
    """Numerical stability issues"""
    pass
```

### Error Response Format

```json
{
    "success": false,
    "error": {
        "type": "DataValidationError",
        "message": "Input data contains NaN values",
        "details": {
            "nan_count": 5,
            "affected_features": [0, 2, 4]
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Type Definitions

### Common Types

```python
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np

# Type aliases
Vector = np.ndarray
Matrix = np.ndarray
ScalarArray = np.ndarray
ConfigDict = Dict[str, Any]
ResultDict = Dict[str, Any]
MetricsDict = Dict[str, float]

# Analysis data types
CollectiveStateData = np.ndarray      # Shape: (n_samples, n_features)
TimeSeriesData = np.ndarray           # Shape: (n_timesteps, n_features)
TrajectoryData = np.ndarray           # Shape: (n_points, n_dimensions)
MultiScaleData = Dict[str, Any]       # Scale name -> scale data

# Result containers
AnalysisResults = Union[
    'ManifoldStructure',
    'SLDSModel',
    'RegimeIdentification',
    'CriticalPoint',
    'StabilityLandscape',
    'UniversalPrinciple',
    'ScalingAnalysis'
]
```

## Performance Guidelines

### Memory Requirements

| Data Size | Memory Usage | Recommended Configuration |
|-----------|--------------|--------------------------|
| Small (<1K samples) | <100MB | Standard settings |
| Medium (1K-10K) | 100MB-1GB | Reduce iterations |
| Large (>10K) | >1GB | Subsample or batch process |

### Execution Time Estimates

| Analysis Type | Small Data | Medium Data | Large Data |
|---------------|------------|-------------|------------|
| Manifold (PCA) | <1s | 1-10s | 10-60s |
| Manifold (t-SNE) | 1-5s | 10-60s | 60-300s |
| Dynamics (SLDS) | 1-5s | 5-30s | 30-180s |
| Catastrophe | <1s | 1-5s | 5-30s |
| Synthesis | <1s | 1-5s | 5-20s |

### Optimization Tips

1. **Use appropriate algorithms for data size**:
   ```python
   config = {
       'embedding_method': 'pca' if n_samples > 1000 else 'tsne',
       'em_iterations': 20 if n_samples > 5000 else 50
   }
   ```

2. **Enable parallel processing**:
   ```python
   import asyncio
   
   tasks = [
       analyzer1.analyze(data1),
       analyzer2.analyze(data2)
   ]
   results = await asyncio.gather(*tasks)
   ```

3. **Use data subsampling for large datasets**:
   ```python
   if len(data) > 10000:
       indices = np.random.choice(len(data), 10000, replace=False)
       data = data[indices]
   ```

This API reference provides complete documentation for integrating and extending the Noesis theoretical analysis framework.