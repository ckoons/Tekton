"""
Dynamics analysis for collective AI systems
Implements SLDS (Switching Linear Dynamical Systems) for regime identification
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from scipy import linalg
from scipy.stats import multivariate_normal
import logging

from .base import MathematicalFramework, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class SLDSModel:
    """Switching Linear Dynamical System model"""
    n_regimes: int
    transition_matrices: Dict[int, np.ndarray]  # A matrices for each regime
    observation_matrices: Dict[int, np.ndarray]  # C matrices for each regime
    process_noise: Dict[int, np.ndarray]  # Q matrices
    observation_noise: Dict[int, np.ndarray]  # R matrices
    transition_probabilities: np.ndarray  # Markov transition matrix
    initial_state_means: Dict[int, np.ndarray]
    initial_state_covariances: Dict[int, np.ndarray]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'n_regimes': self.n_regimes,
            'transition_matrices': {k: v.tolist() for k, v in self.transition_matrices.items()},
            'observation_matrices': {k: v.tolist() for k, v in self.observation_matrices.items()},
            'transition_probabilities': self.transition_probabilities.tolist(),
            'model_type': 'SLDS'
        }


@dataclass
class RegimeIdentification:
    """Results of regime identification analysis"""
    current_regime: int
    regime_probabilities: np.ndarray
    regime_sequence: List[int]
    transition_points: List[int]
    stability_scores: Dict[int, float]
    predicted_transitions: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'current_regime': self.current_regime,
            'regime_probabilities': self.regime_probabilities.tolist(),
            'regime_sequence': self.regime_sequence,
            'transition_points': self.transition_points,
            'stability_scores': self.stability_scores,
            'predicted_transitions': self.predicted_transitions
        }


class DynamicsAnalyzer(MathematicalFramework):
    """
    Analyzes dynamical properties of collective AI systems
    Uses SLDS to model regime switches and transitions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # SLDS parameters
        self.default_n_regimes = self.config.get('n_regimes', 4)
        self.em_iterations = self.config.get('em_iterations', 50)
        self.convergence_threshold = self.config.get('convergence_threshold', 1e-4)
        
        # Regime detection parameters
        self.min_regime_duration = self.config.get('min_regime_duration', 10)
        self.transition_threshold = self.config.get('transition_threshold', 0.7)
        
        logger.info(f"Initialized DynamicsAnalyzer with {self.default_n_regimes} regimes")
    
    async def analyze(self, data: np.ndarray, **kwargs) -> AnalysisResult:
        """
        Analyze dynamics of collective AI system
        
        Args:
            data: Time series data (n_timesteps, n_features)
            
        Returns:
            AnalysisResult containing dynamics analysis
        """
        # Validate input
        is_valid, warnings = await self.validate_data(data)
        if not is_valid:
            return await self.prepare_results(
                data={'error': 'Invalid input data'},
                analysis_type='dynamics_analysis',
                warnings=warnings
            )
        
        # Fit SLDS model
        n_regimes = kwargs.get('n_regimes', self.default_n_regimes)
        slds_model = await self.fit_slds_model(data, n_regimes)
        
        # Identify regimes
        regime_identification = await self.identify_regimes(slds_model, data)
        
        # Analyze stability
        stability_analysis = await self.analyze_regime_stability(
            slds_model, 
            regime_identification.regime_sequence
        )
        
        return await self.prepare_results(
            data={
                'slds_model': slds_model.to_dict(),
                'regime_identification': regime_identification.to_dict(),
                'stability_analysis': stability_analysis,
                'n_timesteps': data.shape[0],
                'n_features': data.shape[1]
            },
            analysis_type='dynamics_analysis',
            metadata={
                'n_regimes': n_regimes,
                'em_iterations': self.em_iterations
            },
            warnings=warnings
        )
    
    async def fit_slds_model(self, 
                           time_series: np.ndarray,
                           n_regimes: int = 4) -> SLDSModel:
        """
        Fit Switching Linear Dynamical System model
        
        Args:
            time_series: Time series data (n_timesteps, n_features)
            n_regimes: Number of discrete regimes
            
        Returns:
            Fitted SLDS model
        """
        logger.info(f"Fitting SLDS with {n_regimes} regimes to {time_series.shape[0]} timesteps")
        
        n_timesteps, n_features = time_series.shape
        
        # Initialize model parameters
        model = await self.initialize_slds_parameters(time_series, n_regimes)
        
        # EM algorithm for SLDS
        prev_likelihood = -np.inf
        
        for iteration in range(self.em_iterations):
            # E-step: Compute regime probabilities
            regime_probs, likelihood = await self.slds_e_step(model, time_series)
            
            # Check convergence
            if abs(likelihood - prev_likelihood) < self.convergence_threshold:
                logger.info(f"SLDS converged after {iteration + 1} iterations")
                break
            prev_likelihood = likelihood
            
            # M-step: Update parameters
            model = await self.slds_m_step(model, time_series, regime_probs)
        
        return model
    
    async def initialize_slds_parameters(self, 
                                       data: np.ndarray, 
                                       n_regimes: int) -> SLDSModel:
        """
        Initialize SLDS parameters using k-means clustering
        
        Args:
            data: Time series data
            n_regimes: Number of regimes
            
        Returns:
            Initialized SLDS model
        """
        from sklearn.cluster import KMeans
        
        n_timesteps, n_features = data.shape
        
        # Cluster data to initialize regimes
        kmeans = KMeans(n_clusters=n_regimes, random_state=42)
        labels = kmeans.fit_predict(data)
        
        # Initialize parameters for each regime
        transition_matrices = {}
        observation_matrices = {}
        process_noise = {}
        observation_noise = {}
        initial_means = {}
        initial_covs = {}
        
        for regime in range(n_regimes):
            # Get data points in this regime
            regime_mask = labels == regime
            regime_data = data[regime_mask]
            
            if len(regime_data) < 2:
                # Not enough data, use identity matrices
                transition_matrices[regime] = np.eye(n_features) * 0.9
                observation_matrices[regime] = np.eye(n_features)
            else:
                # Simple linear regression for dynamics
                X = regime_data[:-1]
                Y = regime_data[1:]
                
                if len(X) > 0:
                    # A = Y.T @ X @ inv(X.T @ X)
                    try:
                        transition_matrices[regime] = Y.T @ X @ np.linalg.inv(X.T @ X + 0.01 * np.eye(n_features))
                    except:
                        transition_matrices[regime] = np.eye(n_features) * 0.9
                else:
                    transition_matrices[regime] = np.eye(n_features) * 0.9
                
                observation_matrices[regime] = np.eye(n_features)
            
            # Noise covariances
            process_noise[regime] = np.eye(n_features) * 0.1
            observation_noise[regime] = np.eye(n_features) * 0.1
            
            # Initial state
            if len(regime_data) > 0:
                initial_means[regime] = np.mean(regime_data, axis=0)
                initial_covs[regime] = np.cov(regime_data.T) + 0.01 * np.eye(n_features)
            else:
                initial_means[regime] = np.zeros(n_features)
                initial_covs[regime] = np.eye(n_features)
        
        # Initialize transition probabilities (uniform with self-transition bias)
        transition_probs = np.ones((n_regimes, n_regimes)) / n_regimes
        np.fill_diagonal(transition_probs, 0.8)
        transition_probs /= transition_probs.sum(axis=1, keepdims=True)
        
        return SLDSModel(
            n_regimes=n_regimes,
            transition_matrices=transition_matrices,
            observation_matrices=observation_matrices,
            process_noise=process_noise,
            observation_noise=observation_noise,
            transition_probabilities=transition_probs,
            initial_state_means=initial_means,
            initial_state_covariances=initial_covs
        )
    
    async def slds_e_step(self, 
                         model: SLDSModel, 
                         data: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        E-step of EM algorithm: compute regime probabilities
        
        Args:
            model: Current SLDS model
            data: Time series data
            
        Returns:
            Regime probabilities and likelihood
        """
        n_timesteps, n_features = data.shape
        n_regimes = model.n_regimes
        
        # Forward-backward algorithm
        alpha = np.zeros((n_timesteps, n_regimes))  # Forward probabilities
        beta = np.zeros((n_timesteps, n_regimes))   # Backward probabilities
        
        # Forward pass
        for regime in range(n_regimes):
            # Initial state likelihood
            mean = model.initial_state_means[regime]
            cov = model.initial_state_covariances[regime]
            alpha[0, regime] = multivariate_normal.pdf(data[0], mean, cov)
        
        alpha[0] /= alpha[0].sum() + 1e-10
        
        for t in range(1, n_timesteps):
            for regime in range(n_regimes):
                # Observation likelihood
                obs_mean = data[t-1] @ model.transition_matrices[regime].T
                obs_cov = model.process_noise[regime]
                likelihood = multivariate_normal.pdf(data[t], obs_mean, obs_cov)
                
                # Transition probability
                alpha[t, regime] = likelihood * (alpha[t-1] @ model.transition_probabilities[:, regime])
            
            alpha[t] /= alpha[t].sum() + 1e-10
        
        # Backward pass
        beta[-1] = 1.0
        
        for t in range(n_timesteps - 2, -1, -1):
            for regime in range(n_regimes):
                for next_regime in range(n_regimes):
                    # Observation likelihood for next timestep
                    obs_mean = data[t] @ model.transition_matrices[next_regime].T
                    obs_cov = model.process_noise[next_regime]
                    likelihood = multivariate_normal.pdf(data[t+1], obs_mean, obs_cov)
                    
                    beta[t, regime] += (
                        beta[t+1, next_regime] * 
                        model.transition_probabilities[regime, next_regime] * 
                        likelihood
                    )
        
        # Compute gamma (regime probabilities)
        gamma = alpha * beta
        gamma /= gamma.sum(axis=1, keepdims=True) + 1e-10
        
        # Log likelihood
        log_likelihood = np.sum(np.log(alpha.sum(axis=1) + 1e-10))
        
        return gamma, log_likelihood
    
    async def slds_m_step(self, 
                         model: SLDSModel, 
                         data: np.ndarray, 
                         gamma: np.ndarray) -> SLDSModel:
        """
        M-step of EM algorithm: update model parameters
        
        Args:
            model: Current SLDS model
            data: Time series data
            gamma: Regime probabilities from E-step
            
        Returns:
            Updated SLDS model
        """
        n_timesteps, n_features = data.shape
        n_regimes = model.n_regimes
        
        # Update transition matrices
        new_transition_matrices = {}
        new_process_noise = {}
        
        for regime in range(n_regimes):
            # Weighted regression for dynamics
            weights = gamma[:, regime]
            
            if np.sum(weights) > 1e-6:
                # Weighted least squares
                X = data[:-1]
                Y = data[1:]
                W = np.diag(weights[:-1])
                
                # A = (Y.T @ W @ X) @ inv(X.T @ W @ X)
                try:
                    XWX = X.T @ W @ X + 0.01 * np.eye(n_features)
                    XWY = X.T @ W @ Y
                    new_transition_matrices[regime] = np.linalg.solve(XWX, XWY).T
                    
                    # Process noise
                    residuals = Y - X @ new_transition_matrices[regime].T
                    weighted_residuals = residuals * np.sqrt(weights[:-1, np.newaxis])
                    new_process_noise[regime] = (weighted_residuals.T @ weighted_residuals) / np.sum(weights[:-1])
                except:
                    new_transition_matrices[regime] = model.transition_matrices[regime]
                    new_process_noise[regime] = model.process_noise[regime]
            else:
                new_transition_matrices[regime] = model.transition_matrices[regime]
                new_process_noise[regime] = model.process_noise[regime]
        
        # Update transition probabilities
        new_transition_probs = np.zeros((n_regimes, n_regimes))
        
        for t in range(n_timesteps - 1):
            for i in range(n_regimes):
                for j in range(n_regimes):
                    new_transition_probs[i, j] += gamma[t, i] * gamma[t+1, j]
        
        new_transition_probs /= new_transition_probs.sum(axis=1, keepdims=True) + 1e-10
        
        # Update initial state parameters
        new_initial_means = {}
        new_initial_covs = {}
        
        for regime in range(n_regimes):
            weight = gamma[0, regime]
            if weight > 1e-6:
                new_initial_means[regime] = data[0] * weight
                diff = data[0] - model.initial_state_means[regime]
                new_initial_covs[regime] = weight * np.outer(diff, diff)
            else:
                new_initial_means[regime] = model.initial_state_means[regime]
                new_initial_covs[regime] = model.initial_state_covariances[regime]
        
        return SLDSModel(
            n_regimes=n_regimes,
            transition_matrices=new_transition_matrices,
            observation_matrices=model.observation_matrices,  # Keep observation matrices fixed
            process_noise=new_process_noise,
            observation_noise=model.observation_noise,
            transition_probabilities=new_transition_probs,
            initial_state_means=new_initial_means,
            initial_state_covariances=new_initial_covs
        )
    
    async def identify_regimes(self, 
                             model: SLDSModel, 
                             data: np.ndarray) -> RegimeIdentification:
        """
        Identify current regime and transition points
        
        Args:
            model: Fitted SLDS model
            data: Time series data
            
        Returns:
            Regime identification results
        """
        # Get regime probabilities
        gamma, _ = await self.slds_e_step(model, data)
        
        # Viterbi algorithm for most likely sequence
        regime_sequence = await self.viterbi_decode(model, data)
        
        # Find transition points
        transition_points = []
        for t in range(1, len(regime_sequence)):
            if regime_sequence[t] != regime_sequence[t-1]:
                transition_points.append(t)
        
        # Current regime
        current_regime = regime_sequence[-1]
        current_probs = gamma[-1]
        
        # Stability scores
        stability_scores = {}
        for regime in range(model.n_regimes):
            # Stability based on self-transition probability and regime duration
            regime_mask = np.array(regime_sequence) == regime
            if np.any(regime_mask):
                avg_duration = self.compute_average_duration(regime_mask)
                stability_scores[regime] = (
                    model.transition_probabilities[regime, regime] * 
                    min(avg_duration / self.min_regime_duration, 1.0)
                )
            else:
                stability_scores[regime] = 0.0
        
        # Predict future transitions
        predicted_transitions = await self.predict_transitions(
            model, 
            current_regime, 
            current_probs
        )
        
        return RegimeIdentification(
            current_regime=current_regime,
            regime_probabilities=current_probs,
            regime_sequence=regime_sequence,
            transition_points=transition_points,
            stability_scores=stability_scores,
            predicted_transitions=predicted_transitions
        )
    
    async def viterbi_decode(self, 
                           model: SLDSModel, 
                           data: np.ndarray) -> List[int]:
        """
        Viterbi algorithm for most likely state sequence
        
        Args:
            model: SLDS model
            data: Observation sequence
            
        Returns:
            Most likely regime sequence
        """
        n_timesteps = len(data)
        n_regimes = model.n_regimes
        
        # Initialize
        delta = np.zeros((n_timesteps, n_regimes))
        psi = np.zeros((n_timesteps, n_regimes), dtype=int)
        
        # Initial state
        for regime in range(n_regimes):
            mean = model.initial_state_means[regime]
            cov = model.initial_state_covariances[regime]
            delta[0, regime] = np.log(multivariate_normal.pdf(data[0], mean, cov) + 1e-10)
        
        # Forward pass
        for t in range(1, n_timesteps):
            for j in range(n_regimes):
                # Observation likelihood
                obs_mean = data[t-1] @ model.transition_matrices[j].T
                obs_cov = model.process_noise[j]
                obs_likelihood = np.log(multivariate_normal.pdf(data[t], obs_mean, obs_cov) + 1e-10)
                
                # Find best previous state
                scores = delta[t-1] + np.log(model.transition_probabilities[:, j] + 1e-10)
                psi[t, j] = np.argmax(scores)
                delta[t, j] = scores[psi[t, j]] + obs_likelihood
        
        # Backward pass
        path = np.zeros(n_timesteps, dtype=int)
        path[-1] = np.argmax(delta[-1])
        
        for t in range(n_timesteps - 2, -1, -1):
            path[t] = psi[t+1, path[t+1]]
        
        return path.tolist()
    
    def compute_average_duration(self, regime_mask: np.ndarray) -> float:
        """
        Compute average duration of regime episodes
        
        Args:
            regime_mask: Boolean mask for regime occurrences
            
        Returns:
            Average duration
        """
        # Find contiguous segments
        changes = np.diff(np.concatenate([[False], regime_mask, [False]]).astype(int))
        starts = np.where(changes == 1)[0]
        ends = np.where(changes == -1)[0]
        
        if len(starts) > 0:
            durations = ends - starts
            return float(np.mean(durations))
        return 0.0
    
    async def predict_transitions(self, 
                                model: SLDSModel,
                                current_regime: int,
                                current_probs: np.ndarray,
                                horizon: int = 10) -> List[Dict[str, Any]]:
        """
        Predict future regime transitions
        
        Args:
            model: SLDS model
            current_regime: Current regime
            current_probs: Current regime probabilities
            horizon: Prediction horizon
            
        Returns:
            List of predicted transitions
        """
        predictions = []
        
        # Simulate forward using transition matrix
        probs = current_probs.copy()
        
        for t in range(1, horizon + 1):
            # Update probabilities
            probs = probs @ model.transition_probabilities
            
            # Check for likely transition
            if np.argmax(probs) != current_regime and probs[np.argmax(probs)] > self.transition_threshold:
                predictions.append({
                    'timestep': t,
                    'from_regime': current_regime,
                    'to_regime': int(np.argmax(probs)),
                    'probability': float(probs[np.argmax(probs)]),
                    'confidence': float(probs[np.argmax(probs)] - probs[current_regime])
                })
                
                # Update current regime for next predictions
                current_regime = np.argmax(probs)
        
        return predictions
    
    async def analyze_regime_stability(self, 
                                     model: SLDSModel,
                                     regime_sequence: List[int]) -> Dict[str, Any]:
        """
        Analyze stability properties of regimes
        
        Args:
            model: SLDS model
            regime_sequence: Historical regime sequence
            
        Returns:
            Stability analysis results
        """
        stability_results = {}
        
        for regime in range(model.n_regimes):
            # Analyze transition matrix eigenvalues
            A = model.transition_matrices[regime]
            eigenvalues = np.linalg.eigvals(A)
            
            # Stability based on spectral radius
            spectral_radius = np.max(np.abs(eigenvalues))
            is_stable = spectral_radius < 1.0
            
            # Lyapunov exponent (simplified)
            if len(eigenvalues) > 0:
                lyapunov = np.log(np.abs(eigenvalues[0]))
            else:
                lyapunov = 0.0
            
            # Residence time
            regime_mask = np.array(regime_sequence) == regime
            residence_time = self.compute_average_duration(regime_mask)
            
            stability_results[f'regime_{regime}'] = {
                'spectral_radius': float(spectral_radius),
                'is_stable': bool(is_stable),
                'lyapunov_exponent': float(lyapunov),
                'average_residence_time': float(residence_time),
                'eigenvalues': eigenvalues.tolist()
            }
        
        return stability_results