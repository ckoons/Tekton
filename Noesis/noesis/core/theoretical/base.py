"""
Base mathematical framework for theoretical analysis
Provides foundation for all Noesis mathematical operations
"""

import numpy as np
import scipy
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Standard result format for all theoretical analyses"""
    analysis_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'analysis_type': self.analysis_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'metadata': self.metadata,
            'confidence': self.confidence,
            'warnings': self.warnings
        }


class MathematicalFramework(ABC):
    """
    Base class for all theoretical analysis components
    Provides common mathematical utilities and validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.numpy = np
        self.scipy = scipy
        
        # Numerical tolerance settings
        self.eps = self.config.get('epsilon', 1e-10)
        self.max_iterations = self.config.get('max_iterations', 1000)
        
        # Validation settings
        self.validate_inputs = self.config.get('validate_inputs', True)
        self.check_stability = self.config.get('check_stability', True)
        
        logger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")
    
    async def analyze(self, data: Any, **kwargs) -> AnalysisResult:
        """
        Main analysis entry point
        Subclasses must implement this method
        """
        raise NotImplementedError("Subclasses must implement analyze()")
    
    async def validate_data(self, data: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Validate input data for numerical stability and proper format
        
        Args:
            data: Input data array
            
        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []
        
        if not self.validate_inputs:
            return True, warnings
        
        # Check for NaN or Inf
        if np.any(np.isnan(data)):
            warnings.append("Data contains NaN values")
            return False, warnings
            
        if np.any(np.isinf(data)):
            warnings.append("Data contains infinite values")
            return False, warnings
        
        # Check dimensionality
        if data.ndim == 0:
            warnings.append("Data is scalar, expected array")
            return False, warnings
        
        # Check for empty data
        if data.size == 0:
            warnings.append("Data is empty")
            return False, warnings
        
        # Check numerical range
        data_range = np.ptp(data)
        if data_range < self.eps:
            warnings.append(f"Data range ({data_range}) is below epsilon threshold")
        
        # Check condition number for 2D arrays
        if data.ndim == 2 and data.shape[0] == data.shape[1]:
            try:
                cond = np.linalg.cond(data)
                if cond > 1e10:
                    warnings.append(f"High condition number ({cond:.2e}), matrix may be ill-conditioned")
            except:
                pass
        
        return True, warnings
    
    def normalize_data(self, data: np.ndarray, method: str = 'standard') -> np.ndarray:
        """
        Normalize data using specified method
        
        Args:
            data: Input data
            method: Normalization method ('standard', 'minmax', 'robust')
            
        Returns:
            Normalized data
        """
        if method == 'standard':
            # Zero mean, unit variance
            mean = np.mean(data, axis=0)
            std = np.std(data, axis=0)
            std[std < self.eps] = 1.0  # Avoid division by zero
            return (data - mean) / std
            
        elif method == 'minmax':
            # Scale to [0, 1]
            data_min = np.min(data, axis=0)
            data_max = np.max(data, axis=0)
            range_val = data_max - data_min
            range_val[range_val < self.eps] = 1.0
            return (data - data_min) / range_val
            
        elif method == 'robust':
            # Use median and MAD
            median = np.median(data, axis=0)
            mad = np.median(np.abs(data - median), axis=0)
            mad[mad < self.eps] = 1.0
            return (data - median) / (1.4826 * mad)
            
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    def compute_distance_matrix(self, points: np.ndarray, metric: str = 'euclidean') -> np.ndarray:
        """
        Compute pairwise distance matrix
        
        Args:
            points: Array of points (n_points, n_dimensions)
            metric: Distance metric to use
            
        Returns:
            Distance matrix (n_points, n_points)
        """
        from scipy.spatial.distance import pdist, squareform
        
        if metric == 'euclidean':
            # Optimized euclidean distance
            return squareform(pdist(points, metric='euclidean'))
        else:
            # Use scipy for other metrics
            return squareform(pdist(points, metric=metric))
    
    def estimate_dimensionality(self, data: np.ndarray, method: str = 'pca_explained_variance') -> int:
        """
        Estimate intrinsic dimensionality of data
        
        Args:
            data: Input data (n_samples, n_features)
            method: Method to use for estimation
            
        Returns:
            Estimated intrinsic dimension
        """
        if method == 'pca_explained_variance':
            # Use PCA explained variance ratio
            from sklearn.decomposition import PCA
            
            n_components = min(data.shape)
            pca = PCA(n_components=n_components)
            pca.fit(data)
            
            # Find dimension that explains threshold variance
            explained_variance_ratio = pca.explained_variance_ratio_
            cumsum = np.cumsum(explained_variance_ratio)
            threshold = self.config.get('variance_threshold', 0.95)
            
            dimension = np.argmax(cumsum >= threshold) + 1
            return int(dimension)
            
        elif method == 'correlation_dimension':
            # Grassberger-Procaccia algorithm
            # Simplified implementation
            distances = self.compute_distance_matrix(data)
            distances = distances[np.triu_indices_from(distances, k=1)]
            
            # Compute correlation sum for different radii
            radii = np.logspace(np.log10(distances.min()), np.log10(distances.max()), 50)
            correlation_sums = []
            
            for r in radii:
                c_r = np.mean(distances <= r)
                if c_r > 0:
                    correlation_sums.append(c_r)
            
            # Estimate slope in log-log plot
            if len(correlation_sums) > 10:
                log_r = np.log(radii[:len(correlation_sums)])
                log_c = np.log(correlation_sums)
                
                # Linear fit in middle region
                n = len(log_r)
                start = n // 4
                end = 3 * n // 4
                
                slope, _ = np.polyfit(log_r[start:end], log_c[start:end], 1)
                return int(np.ceil(slope))
            
            return data.shape[1]  # Fallback
            
        else:
            raise ValueError(f"Unknown dimensionality estimation method: {method}")
    
    def check_numerical_stability(self, result: Any) -> List[str]:
        """
        Check numerical stability of results
        
        Args:
            result: Computation result to check
            
        Returns:
            List of stability warnings
        """
        warnings = []
        
        if not self.check_stability:
            return warnings
        
        # Check for numerical issues in arrays
        if isinstance(result, np.ndarray):
            if np.any(np.isnan(result)):
                warnings.append("Result contains NaN values")
            if np.any(np.isinf(result)):
                warnings.append("Result contains infinite values")
            
            # Check for extreme values
            if result.size > 0:
                max_abs = np.max(np.abs(result))
                if max_abs > 1e10:
                    warnings.append(f"Result contains very large values (max: {max_abs:.2e})")
                elif max_abs < 1e-10:
                    warnings.append(f"Result contains very small values (max: {max_abs:.2e})")
        
        return warnings
    
    async def prepare_results(self, 
                            data: Dict[str, Any], 
                            analysis_type: str,
                            metadata: Optional[Dict[str, Any]] = None,
                            warnings: Optional[List[str]] = None) -> AnalysisResult:
        """
        Prepare standardized analysis results
        
        Args:
            data: Analysis results
            analysis_type: Type of analysis performed
            metadata: Additional metadata
            warnings: Any warnings generated
            
        Returns:
            Standardized AnalysisResult
        """
        # Add stability checks
        stability_warnings = []
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                stability_warnings.extend(self.check_numerical_stability(value))
        
        all_warnings = (warnings or []) + stability_warnings
        
        # Calculate confidence based on warnings
        confidence = 1.0
        if all_warnings:
            confidence -= 0.1 * len(all_warnings)
            confidence = max(confidence, 0.1)
        
        return AnalysisResult(
            analysis_type=analysis_type,
            data=data,
            metadata=metadata or {},
            confidence=confidence,
            warnings=all_warnings
        )
    
    def save_checkpoint(self, state: Dict[str, Any], checkpoint_name: str):
        """Save analysis checkpoint for recovery"""
        # TODO: Implement checkpoint saving
        pass
    
    def load_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Load analysis checkpoint"""
        # TODO: Implement checkpoint loading
        return {}