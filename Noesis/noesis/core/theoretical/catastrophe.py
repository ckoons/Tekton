"""
Catastrophe theory analysis for critical transitions
Identifies bifurcations and phase transitions in collective CI systems
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from scipy.optimize import minimize
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
import logging

from .base import MathematicalFramework, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class CriticalPoint:
    """Identified critical transition point"""
    location: np.ndarray
    transition_type: str  # bifurcation, phase_transition, fold, cusp
    stability_change: Dict[str, float]
    warning_signals: List[str]
    control_parameters: Dict[str, float]
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'location': self.location.tolist(),
            'transition_type': self.transition_type,
            'stability_change': self.stability_change,
            'warning_signals': self.warning_signals,
            'control_parameters': self.control_parameters,
            'confidence': self.confidence
        }


@dataclass
class StabilityLandscape:
    """Stability landscape analysis results"""
    potential_surface: np.ndarray
    stable_regions: List[Dict[str, Any]]
    unstable_regions: List[Dict[str, Any]]
    separatrices: List[np.ndarray]
    basin_boundaries: List[np.ndarray]
    gradient_field: np.ndarray
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'potential_surface_shape': list(self.potential_surface.shape),
            'n_stable_regions': len(self.stable_regions),
            'n_unstable_regions': len(self.unstable_regions),
            'stable_regions': self.stable_regions,
            'unstable_regions': self.unstable_regions
        }


class CatastropheAnalyzer(MathematicalFramework):
    """
    Analyzes critical transitions using catastrophe theory
    Detects bifurcations, phase transitions, and early warning signals
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Analysis parameters
        self.window_size = self.config.get('window_size', 50)
        self.warning_threshold = self.config.get('warning_threshold', 2.0)
        self.potential_resolution = self.config.get('potential_resolution', 100)
        
        # Catastrophe types to detect
        self.catastrophe_types = ['fold', 'cusp', 'swallowtail', 'butterfly']
        
        logger.info("Initialized CatastropheAnalyzer")
    
    async def analyze(self, data: Any, **kwargs) -> AnalysisResult:
        """
        Analyze for critical transitions
        
        Args:
            data: System state data or trajectory
            
        Returns:
            AnalysisResult with catastrophe analysis
        """
        # Handle different input types
        if isinstance(data, dict):
            manifold = data.get('manifold')
            dynamics = data.get('dynamics')
            trajectory = data.get('trajectory')
        else:
            # Assume it's a trajectory
            trajectory = data
            manifold = None
            dynamics = None
        
        # Detect critical points
        critical_points = await self.detect_critical_transitions(
            manifold, dynamics, trajectory
        )
        
        # Analyze stability landscape if we have manifold data
        stability_landscape = None
        if manifold is not None:
            stability_landscape = await self.analyze_stability_landscape(
                manifold.get('embedding_coordinates', np.array([]))
            )
        
        # Compute early warning signals
        warning_signals = await self.compute_early_warning_signals(trajectory)
        
        return await self.prepare_results(
            data={
                'critical_points': [cp.to_dict() for cp in critical_points],
                'stability_landscape': stability_landscape.to_dict() if stability_landscape else None,
                'early_warning_signals': warning_signals,
                'n_critical_points': len(critical_points)
            },
            analysis_type='catastrophe_analysis',
            metadata={
                'window_size': self.window_size,
                'catastrophe_types_checked': self.catastrophe_types
            }
        )
    
    async def detect_critical_transitions(self,
                                        manifold: Optional[Dict[str, Any]],
                                        dynamics: Optional[Dict[str, Any]], 
                                        trajectory: Optional[np.ndarray]) -> List[CriticalPoint]:
        """
        Detect critical transition points
        
        Args:
            manifold: Manifold structure data
            dynamics: Dynamics model data
            trajectory: System trajectory
            
        Returns:
            List of detected critical points
        """
        critical_points = []
        
        # Method 1: Trajectory-based detection
        if trajectory is not None and len(trajectory) > 0:
            trajectory_critical = await self.detect_trajectory_transitions(trajectory)
            critical_points.extend(trajectory_critical)
        
        # Method 2: Dynamics-based detection (if SLDS model available)
        if dynamics is not None:
            dynamics_critical = await self.detect_dynamics_bifurcations(dynamics)
            critical_points.extend(dynamics_critical)
        
        # Method 3: Manifold-based detection
        if manifold is not None:
            manifold_critical = await self.detect_manifold_singularities(manifold)
            critical_points.extend(manifold_critical)
        
        # Merge nearby critical points
        critical_points = self.merge_nearby_critical_points(critical_points)
        
        return critical_points
    
    async def detect_trajectory_transitions(self, 
                                          trajectory: np.ndarray) -> List[CriticalPoint]:
        """
        Detect transitions from trajectory analysis
        
        Args:
            trajectory: Time series of states
            
        Returns:
            List of critical points
        """
        critical_points = []
        
        if len(trajectory) < self.window_size * 2:
            return critical_points
        
        # Compute local variance over sliding windows
        variances = []
        for i in range(len(trajectory) - self.window_size):
            window = trajectory[i:i + self.window_size]
            variances.append(np.var(window, axis=0).mean())
        
        variances = np.array(variances)
        
        # Detect variance peaks (critical slowing down)
        peaks, properties = find_peaks(
            variances, 
            height=np.mean(variances) + self.warning_threshold * np.std(variances),
            distance=self.window_size // 2
        )
        
        for peak_idx in peaks:
            # Analyze transition type
            transition_type = await self.classify_transition_type(
                trajectory, 
                peak_idx + self.window_size // 2
            )
            
            # Compute stability change
            pre_var = np.mean(variances[max(0, peak_idx - 10):peak_idx])
            post_var = np.mean(variances[peak_idx:min(len(variances), peak_idx + 10)])
            
            critical_points.append(CriticalPoint(
                location=trajectory[peak_idx + self.window_size // 2],
                transition_type=transition_type,
                stability_change={
                    'variance_ratio': float(post_var / (pre_var + 1e-10)),
                    'variance_change': float(post_var - pre_var)
                },
                warning_signals=['critical_slowing_down', 'increased_variance'],
                control_parameters={},
                confidence=float(properties['peak_heights'][list(peaks).index(peak_idx)] / 
                                (np.max(variances) + 1e-10))
            ))
        
        # Detect sudden jumps
        diffs = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)
        jump_threshold = np.mean(diffs) + 3 * np.std(diffs)
        
        jumps = np.where(diffs > jump_threshold)[0]
        for jump_idx in jumps:
            critical_points.append(CriticalPoint(
                location=trajectory[jump_idx],
                transition_type='discontinuous_transition',
                stability_change={
                    'jump_magnitude': float(diffs[jump_idx]),
                    'relative_jump': float(diffs[jump_idx] / (np.mean(diffs) + 1e-10))
                },
                warning_signals=['sudden_jump'],
                control_parameters={},
                confidence=0.8
            ))
        
        return critical_points
    
    async def detect_dynamics_bifurcations(self, 
                                         dynamics: Dict[str, Any]) -> List[CriticalPoint]:
        """
        Detect bifurcations from dynamics model
        
        Args:
            dynamics: SLDS model data
            
        Returns:
            List of critical points
        """
        critical_points = []
        
        # Extract transition matrices if available
        if 'slds_model' not in dynamics:
            return critical_points
        
        slds_data = dynamics['slds_model']
        transition_matrices = slds_data.get('transition_matrices', {})
        
        # Analyze each regime's stability
        for regime_str, A_matrix_list in transition_matrices.items():
            A = np.array(A_matrix_list)
            eigenvalues = np.linalg.eigvals(A)
            
            # Check for bifurcation conditions
            max_real_part = np.max(np.real(eigenvalues))
            
            # Hopf bifurcation: complex eigenvalues crossing imaginary axis
            complex_mask = np.abs(np.imag(eigenvalues)) > 1e-6
            if np.any(complex_mask):
                crossing_eigenvalues = eigenvalues[complex_mask & (np.abs(np.real(eigenvalues)) < 0.1)]
                if len(crossing_eigenvalues) > 0:
                    critical_points.append(CriticalPoint(
                        location=np.array([0.0]),  # Placeholder location
                        transition_type='hopf_bifurcation',
                        stability_change={
                            'max_real_eigenvalue': float(max_real_part),
                            'oscillation_frequency': float(np.mean(np.abs(np.imag(crossing_eigenvalues))))
                        },
                        warning_signals=['eigenvalue_crossing', 'oscillatory_behavior'],
                        control_parameters={'regime': int(regime_str)},
                        confidence=0.7
                    ))
            
            # Saddle-node bifurcation: real eigenvalue crossing zero
            zero_crossing = np.any(np.abs(eigenvalues) < 0.1)
            if zero_crossing:
                critical_points.append(CriticalPoint(
                    location=np.array([0.0]),  # Placeholder location
                    transition_type='saddle_node_bifurcation',
                    stability_change={
                        'min_eigenvalue': float(np.min(np.abs(eigenvalues))),
                        'stability_margin': float(1.0 - np.max(np.abs(eigenvalues)))
                    },
                    warning_signals=['zero_eigenvalue', 'marginal_stability'],
                    control_parameters={'regime': int(regime_str)},
                    confidence=0.6
                ))
        
        return critical_points
    
    async def detect_manifold_singularities(self, 
                                          manifold: Dict[str, Any]) -> List[CriticalPoint]:
        """
        Detect singularities in manifold structure
        
        Args:
            manifold: Manifold analysis data
            
        Returns:
            List of critical points
        """
        critical_points = []
        
        embedding = np.array(manifold.get('embedding_coordinates', []))
        if len(embedding) < 10:
            return critical_points
        
        # Analyze curvature for fold catastrophes
        curvature_data = manifold.get('topology_metrics', {})
        mean_curvature = curvature_data.get('mean_curvature', 0)
        curvature_var = curvature_data.get('curvature_variance', 0)
        
        if curvature_var > 0.5:  # High curvature variance indicates potential folds
            # Find high curvature regions
            # This is simplified - in practice would compute local curvature
            critical_points.append(CriticalPoint(
                location=np.mean(embedding, axis=0),
                transition_type='fold_catastrophe',
                stability_change={
                    'curvature_mean': float(mean_curvature),
                    'curvature_variance': float(curvature_var)
                },
                warning_signals=['high_curvature_variance'],
                control_parameters={},
                confidence=0.5
            ))
        
        return critical_points
    
    async def classify_transition_type(self, 
                                     trajectory: np.ndarray, 
                                     transition_idx: int) -> str:
        """
        Classify the type of transition
        
        Args:
            trajectory: Full trajectory
            transition_idx: Index of transition
            
        Returns:
            Transition type string
        """
        window = self.window_size // 2
        
        # Get pre and post transition segments
        pre_start = max(0, transition_idx - window)
        pre_end = transition_idx
        post_start = transition_idx
        post_end = min(len(trajectory), transition_idx + window)
        
        if pre_end - pre_start < 5 or post_end - post_start < 5:
            return 'unknown_transition'
        
        pre_segment = trajectory[pre_start:pre_end]
        post_segment = trajectory[post_start:post_end]
        
        # Check for discontinuity
        gap = np.linalg.norm(trajectory[transition_idx] - trajectory[transition_idx - 1])
        typical_step = np.mean(np.linalg.norm(np.diff(trajectory, axis=0), axis=1))
        
        if gap > 5 * typical_step:
            return 'discontinuous_transition'
        
        # Check for bifurcation patterns
        pre_var = np.var(pre_segment, axis=0).mean()
        post_var = np.var(post_segment, axis=0).mean()
        
        if post_var > 2 * pre_var:
            return 'pitchfork_bifurcation'
        elif post_var < 0.5 * pre_var:
            return 'reverse_bifurcation'
        
        # Check for oscillatory behavior
        if len(post_segment) > 10:
            # Simple FFT to detect oscillations
            fft = np.fft.fft(post_segment[:, 0])
            freqs = np.fft.fftfreq(len(post_segment))
            
            # Find dominant frequency
            power = np.abs(fft) ** 2
            dominant_freq_idx = np.argmax(power[1:len(power)//2]) + 1
            
            if power[dominant_freq_idx] > 10 * np.mean(power):
                return 'hopf_bifurcation'
        
        return 'smooth_transition'
    
    async def analyze_stability_landscape(self, 
                                        embedding: np.ndarray) -> StabilityLandscape:
        """
        Analyze the stability landscape of the system
        
        Args:
            embedding: Points in reduced space
            
        Returns:
            Stability landscape analysis
        """
        if len(embedding) < 10 or embedding.shape[1] < 2:
            # Not enough data for landscape analysis
            return StabilityLandscape(
                potential_surface=np.array([]),
                stable_regions=[],
                unstable_regions=[],
                separatrices=[],
                basin_boundaries=[],
                gradient_field=np.array([])
            )
        
        # Create grid for potential surface
        x_min, x_max = embedding[:, 0].min(), embedding[:, 0].max()
        y_min, y_max = embedding[:, 1].min(), embedding[:, 1].max()
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        # Add padding
        x_min -= 0.1 * x_range
        x_max += 0.1 * x_range
        y_min -= 0.1 * y_range
        y_max += 0.1 * y_range
        
        resolution = self.potential_resolution
        x_grid = np.linspace(x_min, x_max, resolution)
        y_grid = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Estimate potential using kernel density
        potential = await self.estimate_potential_surface(embedding, X, Y)
        
        # Compute gradient field
        gy, gx = np.gradient(potential)
        gradient_field = np.stack([-gx, -gy], axis=-1)  # Negative for downhill flow
        
        # Find stable and unstable regions
        stable_regions, unstable_regions = await self.identify_stability_regions(
            potential, X, Y
        )
        
        # Find separatrices (simplified - just high gradient lines)
        gradient_magnitude = np.sqrt(gx**2 + gy**2)
        separatrix_mask = gradient_magnitude > np.percentile(gradient_magnitude, 90)
        
        # Extract separatrix points
        sep_points = np.column_stack([X[separatrix_mask], Y[separatrix_mask]])
        separatrices = [sep_points[i:i+10] for i in range(0, len(sep_points), 10)]
        
        return StabilityLandscape(
            potential_surface=potential,
            stable_regions=stable_regions,
            unstable_regions=unstable_regions,
            separatrices=separatrices,
            basin_boundaries=separatrices,  # Simplified - same as separatrices
            gradient_field=gradient_field
        )
    
    async def estimate_potential_surface(self, 
                                       points: np.ndarray, 
                                       X: np.ndarray, 
                                       Y: np.ndarray) -> np.ndarray:
        """
        Estimate potential surface using kernel density estimation
        
        Args:
            points: Data points
            X, Y: Grid coordinates
            
        Returns:
            Potential surface
        """
        from scipy.stats import gaussian_kde
        
        # Fit KDE
        if points.shape[1] >= 2:
            kde = gaussian_kde(points[:, :2].T)
            
            # Evaluate on grid
            positions = np.vstack([X.ravel(), Y.ravel()])
            density = kde(positions).reshape(X.shape)
            
            # Convert density to potential (negative log)
            potential = -np.log(density + 1e-10)
            
            # Normalize
            potential -= potential.min()
            potential /= potential.max() + 1e-10
        else:
            potential = np.zeros_like(X)
        
        return potential
    
    async def identify_stability_regions(self, 
                                       potential: np.ndarray,
                                       X: np.ndarray,
                                       Y: np.ndarray) -> Tuple[List[Dict], List[Dict]]:
        """
        Identify stable and unstable regions
        
        Args:
            potential: Potential surface
            X, Y: Grid coordinates
            
        Returns:
            Lists of stable and unstable regions
        """
        from scipy.ndimage import label, find_objects
        
        stable_regions = []
        unstable_regions = []
        
        # Find local minima (stable)
        gy, gx = np.gradient(potential)
        gyy, gyx = np.gradient(gy)
        gxy, gxx = np.gradient(gx)
        
        # Hessian determinant
        det_hessian = gxx * gyy - gxy * gyx
        
        # Local minima: positive determinant and positive trace
        trace_hessian = gxx + gyy
        minima_mask = (det_hessian > 0) & (trace_hessian > 0)
        
        # Label connected regions
        labeled_minima, n_minima = label(minima_mask)
        
        for i in range(1, n_minima + 1):
            region_mask = labeled_minima == i
            if np.sum(region_mask) > 5:  # Minimum size
                region_indices = np.where(region_mask)
                center_x = float(X[region_indices].mean())
                center_y = float(Y[region_indices].mean())
                
                stable_regions.append({
                    'center': [center_x, center_y],
                    'size': int(np.sum(region_mask)),
                    'depth': float(potential[region_indices].mean()),
                    'type': 'local_minimum'
                })
        
        # Saddle points (unstable)
        saddle_mask = (det_hessian < 0)
        labeled_saddles, n_saddles = label(saddle_mask)
        
        for i in range(1, n_saddles + 1):
            region_mask = labeled_saddles == i
            if np.sum(region_mask) > 5:
                region_indices = np.where(region_mask)
                center_x = float(X[region_indices].mean())
                center_y = float(Y[region_indices].mean())
                
                unstable_regions.append({
                    'center': [center_x, center_y],
                    'size': int(np.sum(region_mask)),
                    'height': float(potential[region_indices].mean()),
                    'type': 'saddle_point'
                })
        
        return stable_regions, unstable_regions
    
    async def compute_early_warning_signals(self, 
                                          trajectory: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        Compute early warning signals for critical transitions
        
        Args:
            trajectory: System trajectory
            
        Returns:
            Dictionary of warning signals
        """
        if trajectory is None or len(trajectory) < self.window_size * 2:
            return {}
        
        signals = {}
        
        # Compute rolling statistics
        window = self.window_size
        n_windows = len(trajectory) - window + 1
        
        variances = []
        autocorrelations = []
        skewnesses = []
        
        for i in range(n_windows):
            segment = trajectory[i:i + window]
            
            # Variance
            variances.append(np.var(segment, axis=0).mean())
            
            # Lag-1 autocorrelation
            if segment.shape[1] > 0:
                autocorr = np.corrcoef(segment[:-1, 0], segment[1:, 0])[0, 1]
                autocorrelations.append(autocorr)
            
            # Skewness
            skewnesses.append(float(np.mean(((segment - segment.mean(axis=0)) / 
                                            (segment.std(axis=0) + 1e-10)) ** 3)))
        
        # Trend analysis
        time = np.arange(len(variances))
        
        # Variance trend
        if len(variances) > 10:
            var_trend = np.polyfit(time, variances, 1)[0]
            signals['variance_trend'] = float(var_trend)
            signals['variance_increasing'] = bool(var_trend > 0)
        
        # Autocorrelation trend
        if len(autocorrelations) > 10:
            ac_trend = np.polyfit(time, autocorrelations, 1)[0]
            signals['autocorrelation_trend'] = float(ac_trend)
            signals['critical_slowing_down'] = bool(ac_trend > 0)
        
        # Skewness changes
        if len(skewnesses) > 10:
            signals['mean_skewness'] = float(np.mean(skewnesses))
            signals['skewness_variance'] = float(np.var(skewnesses))
        
        # Composite warning indicator
        warning_score = 0.0
        if signals.get('variance_increasing', False):
            warning_score += 0.4
        if signals.get('critical_slowing_down', False):
            warning_score += 0.4
        if abs(signals.get('mean_skewness', 0)) > 0.5:
            warning_score += 0.2
            
        signals['composite_warning_score'] = float(warning_score)
        signals['warning_level'] = 'high' if warning_score > 0.7 else 'medium' if warning_score > 0.4 else 'low'
        
        return signals
    
    def merge_nearby_critical_points(self, 
                                   critical_points: List[CriticalPoint],
                                   distance_threshold: float = 0.1) -> List[CriticalPoint]:
        """
        Merge critical points that are close together
        
        Args:
            critical_points: List of critical points
            distance_threshold: Distance threshold for merging
            
        Returns:
            Merged list of critical points
        """
        if len(critical_points) <= 1:
            return critical_points
        
        merged = []
        used = set()
        
        for i, cp1 in enumerate(critical_points):
            if i in used:
                continue
                
            # Find nearby points
            nearby = [i]
            for j, cp2 in enumerate(critical_points[i+1:], start=i+1):
                if j not in used:
                    dist = np.linalg.norm(cp1.location - cp2.location)
                    if dist < distance_threshold:
                        nearby.append(j)
                        used.add(j)
            
            # Merge nearby points
            if len(nearby) > 1:
                # Average location
                locations = [critical_points[idx].location for idx in nearby]
                merged_location = np.mean(locations, axis=0)
                
                # Combine warning signals
                all_warnings = []
                for idx in nearby:
                    all_warnings.extend(critical_points[idx].warning_signals)
                
                # Use highest confidence
                max_confidence_idx = max(nearby, 
                                       key=lambda idx: critical_points[idx].confidence)
                base_point = critical_points[max_confidence_idx]
                
                merged.append(CriticalPoint(
                    location=merged_location,
                    transition_type=base_point.transition_type,
                    stability_change=base_point.stability_change,
                    warning_signals=list(set(all_warnings)),
                    control_parameters=base_point.control_parameters,
                    confidence=base_point.confidence
                ))
            else:
                merged.append(cp1)
        
        return merged