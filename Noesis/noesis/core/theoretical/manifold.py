"""
Manifold analysis for collective CI cognition
Implements dimensional reduction and geometric structure identification
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, LocallyLinearEmbedding
import logging

from .base import MathematicalFramework, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class ManifoldStructure:
    """Results of manifold analysis"""
    intrinsic_dimension: int
    principal_components: np.ndarray
    explained_variance: np.ndarray
    embedding_coordinates: np.ndarray
    topology_metrics: Dict[str, float] = field(default_factory=dict)
    regime_assignments: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'intrinsic_dimension': self.intrinsic_dimension,
            'principal_components': self.principal_components.tolist(),
            'explained_variance': self.explained_variance.tolist(),
            'embedding_coordinates': self.embedding_coordinates.tolist(),
            'topology_metrics': self.topology_metrics,
            'regime_assignments': self.regime_assignments.tolist() if self.regime_assignments is not None else None
        }


@dataclass 
class TrajectoryAnalysis:
    """Analysis of trajectory patterns in manifold"""
    trajectory_length: float
    curvature: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    turning_points: List[int]
    cyclic_patterns: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trajectory_length': self.trajectory_length,
            'curvature': self.curvature.tolist(),
            'velocity': self.velocity.tolist(),
            'acceleration': self.acceleration.tolist(),
            'turning_points': self.turning_points,
            'cyclic_patterns': self.cyclic_patterns
        }


class ManifoldAnalyzer(MathematicalFramework):
    """
    Analyzes the geometric structure of collective CI state spaces
    Implements PCA-based manifold identification and trajectory analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Analysis parameters
        self.variance_threshold = self.config.get('variance_threshold', 0.95)
        self.min_dimension = self.config.get('min_dimension', 2)
        self.max_dimension = self.config.get('max_dimension', 50)
        
        # Embedding parameters
        self.embedding_method = self.config.get('embedding_method', 'pca')
        self.n_neighbors = self.config.get('n_neighbors', 15)
        
        logger.info(f"Initialized ManifoldAnalyzer with variance threshold: {self.variance_threshold}")
    
    async def analyze(self, data: np.ndarray, **kwargs) -> AnalysisResult:
        """
        Main analysis entry point
        
        Args:
            data: Collective state data (n_samples, n_features)
            
        Returns:
            AnalysisResult containing ManifoldStructure
        """
        # Validate input
        is_valid, warnings = await self.validate_data(data)
        if not is_valid:
            return await self.prepare_results(
                data={'error': 'Invalid input data'},
                analysis_type='manifold_analysis',
                warnings=warnings
            )
        
        # Normalize data
        normalized_data = self.normalize_data(data, method='standard')
        
        # Perform manifold analysis
        manifold_structure = await self.analyze_collective_manifold(
            normalized_data,
            n_components=kwargs.get('n_components')
        )
        
        # Prepare results
        return await self.prepare_results(
            data={
                'manifold_structure': manifold_structure.to_dict(),
                'original_dimensions': data.shape[1],
                'n_samples': data.shape[0]
            },
            analysis_type='manifold_analysis',
            metadata={
                'embedding_method': self.embedding_method,
                'variance_threshold': self.variance_threshold
            },
            warnings=warnings
        )
    
    async def analyze_collective_manifold(self, 
                                        states: np.ndarray,
                                        n_components: Optional[int] = None) -> ManifoldStructure:
        """
        Perform dimensional reduction and identify manifold structure
        
        Args:
            states: Normalized collective states (n_samples, n_features)
            n_components: Number of components to extract (None for automatic)
            
        Returns:
            ManifoldStructure with analysis results
        """
        logger.info(f"Analyzing manifold for {states.shape[0]} states with {states.shape[1]} features")
        
        # Estimate intrinsic dimension if not specified
        if n_components is None:
            intrinsic_dim = await self.compute_intrinsic_dimension(states)
            n_components = min(intrinsic_dim, self.max_dimension)
        else:
            intrinsic_dim = n_components
        
        # Perform PCA
        pca = PCA(n_components=n_components)
        embedding = pca.fit_transform(states)
        
        # Compute additional embeddings if needed
        if self.embedding_method != 'pca' and states.shape[0] > 50:
            embedding = await self.compute_alternative_embedding(states, n_components)
        
        # Analyze topology
        topology_metrics = await self.analyze_topology(embedding)
        
        # Identify regimes if applicable
        regime_assignments = None
        if kwargs.get('identify_regimes', False):
            regime_assignments = await self.identify_manifold_regimes(embedding)
        
        return ManifoldStructure(
            intrinsic_dimension=intrinsic_dim,
            principal_components=pca.components_[:n_components],
            explained_variance=pca.explained_variance_ratio_[:n_components],
            embedding_coordinates=embedding,
            topology_metrics=topology_metrics,
            regime_assignments=regime_assignments
        )
    
    async def compute_intrinsic_dimension(self, data: np.ndarray) -> int:
        """
        Estimate intrinsic dimensionality using multiple methods
        
        Args:
            data: Input data (n_samples, n_features)
            
        Returns:
            Estimated intrinsic dimension
        """
        dimensions = []
        
        # Method 1: PCA explained variance
        pca_dim = self.estimate_dimensionality(data, method='pca_explained_variance')
        dimensions.append(pca_dim)
        
        # Method 2: Correlation dimension (if enough samples)
        if data.shape[0] > 100:
            try:
                corr_dim = self.estimate_dimensionality(data, method='correlation_dimension')
                dimensions.append(corr_dim)
            except Exception as e:
                logger.warning(f"Correlation dimension estimation failed: {e}")
        
        # Method 3: Local dimension estimation
        if data.shape[0] > 50:
            local_dims = await self.estimate_local_dimensions(data)
            if local_dims:
                dimensions.append(int(np.median(local_dims)))
        
        # Combine estimates
        if dimensions:
            intrinsic_dim = int(np.median(dimensions))
            logger.info(f"Intrinsic dimension estimates: {dimensions}, using: {intrinsic_dim}")
        else:
            intrinsic_dim = min(data.shape[1], 10)
            logger.warning(f"Could not estimate dimension, using default: {intrinsic_dim}")
        
        return max(self.min_dimension, intrinsic_dim)
    
    async def estimate_local_dimensions(self, data: np.ndarray, k: int = 15) -> List[int]:
        """
        Estimate local intrinsic dimensions using nearest neighbors
        
        Args:
            data: Input data
            k: Number of nearest neighbors
            
        Returns:
            List of local dimension estimates
        """
        from sklearn.neighbors import NearestNeighbors
        
        local_dims = []
        
        # Fit nearest neighbors
        nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree').fit(data)
        
        # Sample points for local analysis
        n_samples = min(100, data.shape[0])
        sample_indices = np.random.choice(data.shape[0], n_samples, replace=False)
        
        for idx in sample_indices:
            # Get k nearest neighbors
            distances, indices = nbrs.kneighbors([data[idx]])
            neighbor_points = data[indices[0][1:]]  # Exclude self
            
            # Local PCA
            local_pca = PCA(n_components=min(k-1, data.shape[1]))
            local_pca.fit(neighbor_points)
            
            # Estimate local dimension
            cumsum = np.cumsum(local_pca.explained_variance_ratio_)
            local_dim = np.argmax(cumsum >= 0.9) + 1
            local_dims.append(local_dim)
        
        return local_dims
    
    async def compute_alternative_embedding(self, 
                                          data: np.ndarray, 
                                          n_components: int) -> np.ndarray:
        """
        Compute alternative embeddings (t-SNE, LLE, etc.)
        
        Args:
            data: Input data
            n_components: Target dimensions
            
        Returns:
            Embedded coordinates
        """
        if self.embedding_method == 'tsne' and n_components <= 3:
            tsne = TSNE(n_components=n_components, perplexity=30, random_state=42)
            return tsne.fit_transform(data)
            
        elif self.embedding_method == 'lle':
            lle = LocallyLinearEmbedding(
                n_components=n_components,
                n_neighbors=self.n_neighbors,
                random_state=42
            )
            return lle.fit_transform(data)
            
        else:
            # Default to PCA
            pca = PCA(n_components=n_components)
            return pca.fit_transform(data)
    
    async def analyze_topology(self, embedding: np.ndarray) -> Dict[str, float]:
        """
        Analyze topological properties of the manifold
        
        Args:
            embedding: Embedded coordinates
            
        Returns:
            Dictionary of topology metrics
        """
        metrics = {}
        
        # Compute persistence homology features (simplified)
        distances = self.compute_distance_matrix(embedding)
        
        # Density estimate
        k = min(10, embedding.shape[0] - 1)
        knn_distances = np.sort(distances, axis=1)[:, 1:k+1]
        metrics['mean_local_density'] = float(1.0 / np.mean(knn_distances))
        metrics['density_variance'] = float(np.var(1.0 / knn_distances.mean(axis=1)))
        
        # Connectivity
        threshold = np.percentile(distances[distances > 0], 10)
        adjacency = distances <= threshold
        metrics['connectivity'] = float(np.mean(np.sum(adjacency, axis=1)))
        
        # Manifold curvature (simplified Ricci curvature)
        if embedding.shape[1] >= 2:
            curvature = await self.estimate_manifold_curvature(embedding)
            metrics['mean_curvature'] = float(np.mean(curvature))
            metrics['curvature_variance'] = float(np.var(curvature))
        
        return metrics
    
    async def estimate_manifold_curvature(self, embedding: np.ndarray) -> np.ndarray:
        """
        Estimate local curvature of the manifold
        
        Args:
            embedding: Embedded coordinates
            
        Returns:
            Local curvature estimates
        """
        n_points = embedding.shape[0]
        curvatures = np.zeros(n_points)
        
        # Simple discrete curvature estimation
        k = min(10, n_points - 1)
        
        for i in range(n_points):
            # Find k nearest neighbors
            distances = np.linalg.norm(embedding - embedding[i], axis=1)
            neighbor_indices = np.argsort(distances)[1:k+1]
            
            # Fit local quadratic form
            neighbors = embedding[neighbor_indices] - embedding[i]
            
            if embedding.shape[1] >= 2:
                # Simplified curvature based on local PCA
                local_pca = PCA(n_components=min(2, embedding.shape[1]))
                local_pca.fit(neighbors)
                
                # Curvature related to ratio of eigenvalues
                if len(local_pca.explained_variance_) >= 2:
                    curvatures[i] = (local_pca.explained_variance_[1] / 
                                   (local_pca.explained_variance_[0] + 1e-10))
        
        return curvatures
    
    async def identify_trajectory_patterns(self, 
                                         trajectory: np.ndarray) -> TrajectoryAnalysis:
        """
        Analyze movement patterns in reduced space
        
        Args:
            trajectory: Time series of points in manifold (n_timesteps, n_dims)
            
        Returns:
            TrajectoryAnalysis with pattern information
        """
        n_points = trajectory.shape[0]
        
        # Compute trajectory length
        segments = np.diff(trajectory, axis=0)
        segment_lengths = np.linalg.norm(segments, axis=1)
        trajectory_length = float(np.sum(segment_lengths))
        
        # Compute velocity and acceleration
        velocity = segments / 1.0  # Assuming unit time steps
        acceleration = np.diff(velocity, axis=0)
        
        # Pad to maintain array sizes
        velocity = np.vstack([velocity, velocity[-1]])
        acceleration = np.vstack([acceleration[-1], acceleration, acceleration[-1]])
        
        # Compute curvature
        curvature = np.zeros(n_points)
        for i in range(1, n_points - 1):
            v1 = trajectory[i] - trajectory[i-1]
            v2 = trajectory[i+1] - trajectory[i]
            
            # Angle between consecutive segments
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            curvature[i] = np.arccos(np.clip(cos_angle, -1, 1))
        
        # Identify turning points
        turning_points = []
        curvature_threshold = np.percentile(curvature, 90)
        for i in range(1, n_points - 1):
            if curvature[i] > curvature_threshold:
                if i == 1 or curvature[i] > curvature[i-1]:
                    if i == n_points - 2 or curvature[i] > curvature[i+1]:
                        turning_points.append(i)
        
        # Detect cyclic patterns (simplified)
        cyclic_patterns = await self.detect_cyclic_patterns(trajectory)
        
        return TrajectoryAnalysis(
            trajectory_length=trajectory_length,
            curvature=curvature,
            velocity=np.linalg.norm(velocity, axis=1),
            acceleration=np.linalg.norm(acceleration, axis=1),
            turning_points=turning_points,
            cyclic_patterns=cyclic_patterns
        )
    
    async def detect_cyclic_patterns(self, trajectory: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect cyclic or repeating patterns in trajectory
        
        Args:
            trajectory: Time series of points
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Simple autocorrelation-based cycle detection
        if trajectory.shape[0] > 20:
            # Compute autocorrelation of trajectory distances
            distances = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)
            
            # Normalize
            distances = (distances - np.mean(distances)) / (np.std(distances) + 1e-10)
            
            # Compute autocorrelation for different lags
            max_lag = min(len(distances) // 2, 100)
            autocorr = []
            
            for lag in range(1, max_lag):
                if lag < len(distances):
                    corr = np.corrcoef(distances[:-lag], distances[lag:])[0, 1]
                    autocorr.append(corr)
            
            # Find peaks in autocorrelation
            autocorr = np.array(autocorr)
            peaks = []
            
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > 0.5:  # Threshold for significant correlation
                    if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                        peaks.append(i + 1)  # +1 because we started lag at 1
            
            # Report detected cycles
            for period in peaks[:3]:  # Top 3 cycles
                patterns.append({
                    'type': 'periodic',
                    'period': period,
                    'strength': float(autocorr[period - 1]),
                    'confidence': float(autocorr[period - 1] ** 2)
                })
        
        return patterns
    
    async def identify_manifold_regimes(self, embedding: np.ndarray) -> np.ndarray:
        """
        Identify discrete regimes or clusters in the manifold
        
        Args:
            embedding: Embedded coordinates
            
        Returns:
            Regime assignments for each point
        """
        from sklearn.cluster import DBSCAN
        
        # Use DBSCAN for regime identification
        # Automatically determine eps using k-distance graph
        k = min(10, embedding.shape[0] // 10)
        distances = self.compute_distance_matrix(embedding)
        k_distances = np.sort(distances, axis=1)[:, k]
        eps = np.percentile(k_distances, 90)
        
        clustering = DBSCAN(eps=eps, min_samples=k).fit(embedding)
        
        return clustering.labels_