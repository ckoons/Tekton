"""
MCP (Model Context Protocol) tools for Noesis theoretical analysis
Provides high-level access to mathematical analysis capabilities
"""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

from ..core.theoretical import (
    ManifoldAnalyzer, DynamicsAnalyzer, CatastropheAnalyzer, 
    SynthesisAnalyzer, AnalysisResult
)
from ..core.integration.data_models import CollectiveState

logger = logging.getLogger(__name__)


class NoesisMCPTools:
    """
    MCP tool implementations for theoretical analysis
    """
    
    def __init__(self):
        # Initialize analyzers
        self.manifold_analyzer = ManifoldAnalyzer()
        self.dynamics_analyzer = DynamicsAnalyzer()
        self.catastrophe_analyzer = CatastropheAnalyzer()
        self.synthesis_analyzer = SynthesisAnalyzer()
        
        # Cache for recent analyses
        self.analysis_cache = {}
        
        logger.info("Initialized Noesis MCP tools")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get MCP tool definitions for registration
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "analyze_cognitive_manifold",
                "description": "Complete manifold analysis including PCA, dimensionality, and structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collective_states": {
                            "type": "array",
                            "description": "List of CI collective states"
                        },
                        "analysis_depth": {
                            "type": "string",
                            "enum": ["basic", "detailed", "comprehensive"],
                            "default": "detailed",
                            "description": "Level of detail for analysis"
                        }
                    },
                    "required": ["collective_states"]
                }
            },
            {
                "name": "identify_regime_dynamics",
                "description": "SLDS modeling to identify cognitive regimes and transitions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "time_series_data": {
                            "type": "array",
                            "description": "Temporal sequence of collective states"
                        },
                        "expected_regimes": {
                            "type": "integer",
                            "default": 4,
                            "description": "Number of regimes to identify"
                        }
                    },
                    "required": ["time_series_data"]
                }
            },
            {
                "name": "predict_phase_transitions",
                "description": "Predict critical transitions using catastrophe theory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "current_state": {
                            "type": "object",
                            "description": "Current collective configuration"
                        },
                        "lookahead_window": {
                            "type": "integer",
                            "default": 10,
                            "description": "Time horizon for predictions"
                        }
                    },
                    "required": ["current_state"]
                }
            },
            {
                "name": "extract_universal_principles",
                "description": "Identify patterns that hold across scales",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "multi_scale_data": {
                            "type": "object",
                            "description": "Data from different collective sizes"
                        },
                        "principle_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["scaling", "fractal", "emergent"],
                            "description": "Types of principles to extract"
                        }
                    },
                    "required": ["multi_scale_data"]
                }
            },
            {
                "name": "generate_theoretical_model",
                "description": "Create predictive model from observations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "training_data": {
                            "type": "array",
                            "description": "Historical collective behavior"
                        },
                        "model_type": {
                            "type": "string",
                            "enum": ["geometric", "dynamic", "hybrid"],
                            "default": "hybrid",
                            "description": "Type of model to generate"
                        }
                    },
                    "required": ["training_data"]
                }
            },
            {
                "name": "validate_with_experiment",
                "description": "Interface with Sophia for theory validation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "theoretical_prediction": {
                            "type": "object",
                            "description": "Model predictions"
                        },
                        "experiment_design": {
                            "type": "object",
                            "description": "Proposed experimental setup"
                        }
                    },
                    "required": ["theoretical_prediction", "experiment_design"]
                }
            },
            {
                "name": "analyze_collective_trajectory",
                "description": "Time-series analysis of CI collective evolution",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trajectory_data": {
                            "type": "array",
                            "description": "Temporal evolution data"
                        },
                        "analysis_methods": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["fourier", "wavelet", "recurrence"],
                            "description": "Methods to apply"
                        }
                    },
                    "required": ["trajectory_data"]
                }
            },
            {
                "name": "compute_criticality_metrics",
                "description": "Identify lines of criticality in the manifold",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "state_space": {
                            "type": "array",
                            "description": "High-dimensional state representation"
                        },
                        "criticality_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["variance", "correlation", "entropy"],
                            "description": "Which metrics to compute"
                        }
                    },
                    "required": ["state_space"]
                }
            }
        ]
    
    async def analyze_cognitive_manifold(self, 
                                       collective_states: List[Dict[str, Any]], 
                                       analysis_depth: str = "detailed") -> Dict[str, Any]:
        """
        Complete manifold analysis including PCA, dimensionality, and structure
        
        Args:
            collective_states: List of CI collective states
            analysis_depth: Level of detail (basic, detailed, comprehensive)
            
        Returns:
            Analysis results
        """
        try:
            # Convert states to numpy array
            state_array = self._prepare_state_array(collective_states)
            
            # Perform manifold analysis
            result = await self.manifold_analyzer.analyze(state_array)
            
            # Add additional analysis based on depth
            if analysis_depth in ["detailed", "comprehensive"]:
                # Analyze trajectories if temporal data available
                if len(state_array) > 10:
                    trajectory_analysis = await self.manifold_analyzer.identify_trajectory_patterns(
                        state_array
                    )
                    result.data['trajectory_analysis'] = trajectory_analysis.to_dict()
            
            if analysis_depth == "comprehensive":
                # Add regime identification
                manifold_data = result.data.get('manifold_structure', {})
                if 'embedding_coordinates' in manifold_data:
                    embedding = np.array(manifold_data['embedding_coordinates'])
                    regimes = await self.manifold_analyzer.identify_manifold_regimes(embedding)
                    result.data['regime_assignments'] = regimes.tolist()
            
            return {
                "status": "success",
                "analysis_type": "cognitive_manifold",
                "results": result.data,
                "metadata": result.metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in manifold analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "cognitive_manifold"
            }
    
    async def identify_regime_dynamics(self, 
                                     time_series_data: List[Dict[str, Any]], 
                                     expected_regimes: int = 4) -> Dict[str, Any]:
        """
        SLDS modeling to identify cognitive regimes and transitions
        
        Args:
            time_series_data: Temporal sequence of collective states
            expected_regimes: Number of regimes to identify
            
        Returns:
            Regime analysis results
        """
        try:
            # Prepare time series
            time_series = self._prepare_state_array(time_series_data)
            
            # Perform dynamics analysis
            result = await self.dynamics_analyzer.analyze(
                time_series, 
                n_regimes=expected_regimes
            )
            
            # Extract key insights
            regime_data = result.data.get('regime_identification', {})
            
            return {
                "status": "success",
                "analysis_type": "regime_dynamics",
                "current_regime": regime_data.get('current_regime'),
                "regime_sequence": regime_data.get('regime_sequence', []),
                "transition_points": regime_data.get('transition_points', []),
                "stability_scores": regime_data.get('stability_scores', {}),
                "predicted_transitions": regime_data.get('predicted_transitions', []),
                "full_results": result.data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in regime dynamics analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "regime_dynamics"
            }
    
    async def predict_phase_transitions(self, 
                                      current_state: Dict[str, Any], 
                                      lookahead_window: int = 10) -> Dict[str, Any]:
        """
        Predict critical transitions using catastrophe theory
        
        Args:
            current_state: Current collective configuration
            lookahead_window: Time horizon for predictions
            
        Returns:
            Phase transition predictions
        """
        try:
            # Get recent trajectory if available
            trajectory = current_state.get('recent_trajectory', [current_state])
            trajectory_array = self._prepare_state_array(trajectory)
            
            # Analyze for catastrophes
            analysis_data = {
                'trajectory': trajectory_array,
                'current_state': trajectory_array[-1] if len(trajectory_array) > 0 else None
            }
            
            result = await self.catastrophe_analyzer.analyze(analysis_data)
            
            # Extract predictions
            critical_points = result.data.get('critical_points', [])
            warning_signals = result.data.get('early_warning_signals', {})
            
            # Generate predictions
            predictions = []
            for cp in critical_points:
                if cp.get('confidence', 0) > 0.5:
                    predictions.append({
                        'transition_type': cp.get('transition_type'),
                        'warning_signals': cp.get('warning_signals', []),
                        'confidence': cp.get('confidence'),
                        'estimated_time': lookahead_window * (1 - cp.get('confidence', 0.5))
                    })
            
            return {
                "status": "success",
                "analysis_type": "phase_transitions",
                "predictions": predictions,
                "warning_level": warning_signals.get('warning_level', 'low'),
                "warning_signals": warning_signals,
                "critical_points_detected": len(critical_points),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in phase transition prediction: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "phase_transitions"
            }
    
    async def extract_universal_principles(self, 
                                         multi_scale_data: Dict[str, Any], 
                                         principle_types: List[str] = None) -> Dict[str, Any]:
        """
        Identify patterns that hold across scales
        
        Args:
            multi_scale_data: Data from different collective sizes
            principle_types: Types of principles to extract
            
        Returns:
            Universal principles found
        """
        try:
            if principle_types is None:
                principle_types = ["scaling", "fractal", "emergent"]
            
            # Perform synthesis analysis
            result = await self.synthesis_analyzer.analyze(multi_scale_data)
            
            # Filter principles by type
            all_principles = result.data.get('universal_principles', [])
            filtered_principles = []
            
            for principle in all_principles:
                principle_type = principle.get('principle_type', '')
                if any(pt in principle_type for pt in principle_types):
                    filtered_principles.append(principle)
            
            return {
                "status": "success",
                "analysis_type": "universal_principles",
                "principles": filtered_principles,
                "total_found": len(all_principles),
                "filtered_count": len(filtered_principles),
                "scaling_analysis": result.data.get('scaling_analysis'),
                "emergent_properties": result.data.get('emergent_properties', []),
                "cross_scale_patterns": result.data.get('cross_scale_patterns', []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting universal principles: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "universal_principles"
            }
    
    async def generate_theoretical_model(self, 
                                       training_data: List[Dict[str, Any]], 
                                       model_type: str = "hybrid") -> Dict[str, Any]:
        """
        Create predictive model from observations
        
        Args:
            training_data: Historical collective behavior
            model_type: Type of model (geometric, dynamic, hybrid)
            
        Returns:
            Generated theoretical model
        """
        try:
            # Prepare training data
            data_array = self._prepare_state_array(training_data)
            
            model_components = {}
            
            # Generate model based on type
            if model_type in ["geometric", "hybrid"]:
                # Manifold model
                manifold_result = await self.manifold_analyzer.analyze(data_array)
                model_components['manifold'] = manifold_result.data
            
            if model_type in ["dynamic", "hybrid"]:
                # Dynamics model
                dynamics_result = await self.dynamics_analyzer.analyze(data_array)
                model_components['dynamics'] = dynamics_result.data
            
            # Add catastrophe analysis for all types
            catastrophe_data = {
                'trajectory': data_array,
                'manifold': model_components.get('manifold'),
                'dynamics': model_components.get('dynamics')
            }
            catastrophe_result = await self.catastrophe_analyzer.analyze(catastrophe_data)
            model_components['catastrophe'] = catastrophe_result.data
            
            # Generate model ID
            model_id = f"noesis_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Cache the model
            self.analysis_cache[model_id] = {
                'model_type': model_type,
                'components': model_components,
                'training_size': len(training_data),
                'created_at': datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "analysis_type": "theoretical_model",
                "model_id": model_id,
                "model_type": model_type,
                "components": list(model_components.keys()),
                "model_summary": self._summarize_model(model_components),
                "training_samples": len(training_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating theoretical model: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "theoretical_model"
            }
    
    async def validate_with_experiment(self, 
                                     theoretical_prediction: Dict[str, Any], 
                                     experiment_design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interface with Sophia for theory validation
        
        Args:
            theoretical_prediction: Model predictions
            experiment_design: Proposed experimental setup
            
        Returns:
            Validation protocol for Sophia
        """
        try:
            # Prepare validation request
            validation_request = {
                "request_type": "theory_validation",
                "theoretical_prediction": theoretical_prediction,
                "experiment_design": experiment_design,
                "suggested_metrics": self._suggest_validation_metrics(theoretical_prediction),
                "expected_outcomes": self._generate_expected_outcomes(theoretical_prediction),
                "confidence_intervals": self._compute_confidence_intervals(theoretical_prediction)
            }
            
            # TODO: Actually interface with Sophia when integration is ready
            # For now, return the validation protocol
            
            return {
                "status": "success",
                "analysis_type": "experiment_validation",
                "validation_protocol": validation_request,
                "sophia_integration": "pending",
                "instructions": "Submit this protocol to Sophia for experimental validation",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in experiment validation: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "experiment_validation"
            }
    
    async def analyze_collective_trajectory(self, 
                                          trajectory_data: List[Dict[str, Any]], 
                                          analysis_methods: List[str] = None) -> Dict[str, Any]:
        """
        Time-series analysis of CI collective evolution
        
        Args:
            trajectory_data: Temporal evolution data
            analysis_methods: Methods to apply
            
        Returns:
            Trajectory analysis results
        """
        try:
            if analysis_methods is None:
                analysis_methods = ["fourier", "wavelet", "recurrence"]
            
            # Prepare trajectory
            trajectory = self._prepare_state_array(trajectory_data)
            
            # Basic trajectory analysis from manifold analyzer
            trajectory_analysis = await self.manifold_analyzer.identify_trajectory_patterns(
                trajectory
            )
            
            results = {
                "basic_analysis": trajectory_analysis.to_dict(),
                "methods_applied": []
            }
            
            # Apply requested methods
            if "fourier" in analysis_methods:
                fourier_results = self._fourier_analysis(trajectory)
                results["fourier_analysis"] = fourier_results
                results["methods_applied"].append("fourier")
            
            if "wavelet" in analysis_methods:
                wavelet_results = self._wavelet_analysis(trajectory)
                results["wavelet_analysis"] = wavelet_results
                results["methods_applied"].append("wavelet")
            
            if "recurrence" in analysis_methods:
                recurrence_results = self._recurrence_analysis(trajectory)
                results["recurrence_analysis"] = recurrence_results
                results["methods_applied"].append("recurrence")
            
            return {
                "status": "success",
                "analysis_type": "collective_trajectory",
                "results": results,
                "trajectory_length": len(trajectory),
                "dimensionality": trajectory.shape[1] if len(trajectory) > 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in trajectory analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "collective_trajectory"
            }
    
    async def compute_criticality_metrics(self, 
                                        state_space: List[Dict[str, Any]], 
                                        criticality_indicators: List[str] = None) -> Dict[str, Any]:
        """
        Identify lines of criticality in the manifold
        
        Args:
            state_space: High-dimensional state representation
            criticality_indicators: Which metrics to compute
            
        Returns:
            Criticality metrics
        """
        try:
            if criticality_indicators is None:
                criticality_indicators = ["variance", "correlation", "entropy"]
            
            # Prepare state space
            states = self._prepare_state_array(state_space)
            
            metrics = {}
            
            # Compute requested indicators
            if "variance" in criticality_indicators:
                # Compute variance along different directions
                variances = np.var(states, axis=0)
                metrics["variance"] = {
                    "mean_variance": float(np.mean(variances)),
                    "max_variance": float(np.max(variances)),
                    "variance_ratio": float(np.max(variances) / (np.min(variances) + 1e-10)),
                    "high_variance_dimensions": np.where(variances > np.mean(variances) + np.std(variances))[0].tolist()
                }
            
            if "correlation" in criticality_indicators:
                # Compute correlation structure
                if states.shape[0] > 1:
                    corr_matrix = np.corrcoef(states.T)
                    eigenvalues = np.linalg.eigvals(corr_matrix)
                    
                    metrics["correlation"] = {
                        "max_correlation": float(np.max(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))),
                        "mean_correlation": float(np.mean(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))),
                        "largest_eigenvalue": float(np.max(np.real(eigenvalues))),
                        "spectral_gap": float(np.max(np.real(eigenvalues)) - np.sort(np.real(eigenvalues))[-2])
                    }
            
            if "entropy" in criticality_indicators:
                # Compute entropy-based metrics
                # Simplified - using variance as proxy for entropy
                normalized_states = (states - np.mean(states, axis=0)) / (np.std(states, axis=0) + 1e-10)
                
                metrics["entropy"] = {
                    "differential_entropy_estimate": float(-np.sum(np.log(np.std(states, axis=0) + 1e-10))),
                    "complexity_estimate": float(np.mean(np.abs(np.diff(normalized_states, axis=0))))
                }
            
            # Identify critical regions
            critical_regions = self._identify_critical_regions(states, metrics)
            
            return {
                "status": "success",
                "analysis_type": "criticality_metrics",
                "metrics": metrics,
                "critical_regions": critical_regions,
                "indicators_computed": list(metrics.keys()),
                "state_space_size": states.shape,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error computing criticality metrics: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "analysis_type": "criticality_metrics"
            }
    
    # Helper methods
    
    def _prepare_state_array(self, states: List[Dict[str, Any]]) -> np.ndarray:
        """
        Convert list of state dictionaries to numpy array
        
        Args:
            states: List of state dictionaries
            
        Returns:
            Numpy array of states
        """
        if not states:
            return np.array([])
        
        # Extract numerical features
        arrays = []
        for state in states:
            if isinstance(state, dict):
                # Try different common formats
                if 'vector' in state:
                    arrays.append(np.array(state['vector']))
                elif 'features' in state:
                    arrays.append(np.array(state['features']))
                elif 'state' in state:
                    arrays.append(np.array(state['state']))
                else:
                    # Try to extract all numerical values
                    values = []
                    for v in state.values():
                        if isinstance(v, (int, float)):
                            values.append(v)
                        elif isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                            values.extend(v)
                    if values:
                        arrays.append(np.array(values))
            elif isinstance(state, (list, np.ndarray)):
                arrays.append(np.array(state))
        
        if not arrays:
            return np.array([])
        
        # Ensure all arrays have same length
        max_len = max(len(a) for a in arrays)
        padded_arrays = []
        for a in arrays:
            if len(a) < max_len:
                padded = np.pad(a, (0, max_len - len(a)), mode='constant')
                padded_arrays.append(padded)
            else:
                padded_arrays.append(a)
        
        return np.array(padded_arrays)
    
    def _summarize_model(self, model_components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of theoretical model
        
        Args:
            model_components: Model components
            
        Returns:
            Model summary
        """
        summary = {}
        
        if 'manifold' in model_components:
            manifold_data = model_components['manifold'].get('manifold_structure', {})
            summary['intrinsic_dimension'] = manifold_data.get('intrinsic_dimension')
            summary['n_samples'] = model_components['manifold'].get('n_samples')
        
        if 'dynamics' in model_components:
            dynamics_data = model_components['dynamics']
            if 'slds_model' in dynamics_data:
                summary['n_regimes'] = dynamics_data['slds_model'].get('n_regimes')
            if 'regime_identification' in dynamics_data:
                summary['current_regime'] = dynamics_data['regime_identification'].get('current_regime')
        
        if 'catastrophe' in model_components:
            catastrophe_data = model_components['catastrophe']
            summary['n_critical_points'] = catastrophe_data.get('n_critical_points', 0)
            summary['warning_level'] = catastrophe_data.get('early_warning_signals', {}).get('warning_level', 'unknown')
        
        return summary
    
    def _suggest_validation_metrics(self, prediction: Dict[str, Any]) -> List[str]:
        """
        Suggest metrics for validating theoretical prediction
        
        Args:
            prediction: Theoretical prediction
            
        Returns:
            List of suggested metrics
        """
        metrics = ["prediction_accuracy", "confidence_interval_coverage"]
        
        if "regime" in str(prediction):
            metrics.extend(["regime_identification_accuracy", "transition_timing_error"])
        
        if "manifold" in str(prediction):
            metrics.extend(["dimensional_stability", "embedding_quality"])
        
        if "critical" in str(prediction) or "transition" in str(prediction):
            metrics.extend(["early_warning_detection_rate", "false_positive_rate"])
        
        return metrics
    
    def _generate_expected_outcomes(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate expected experimental outcomes from prediction
        
        Args:
            prediction: Theoretical prediction
            
        Returns:
            Expected outcomes
        """
        outcomes = {
            "primary_outcome": "Theory validation",
            "success_criteria": []
        }
        
        if isinstance(prediction, dict):
            if "confidence" in prediction:
                outcomes["expected_confidence"] = prediction["confidence"]
                outcomes["success_criteria"].append(f"Observed confidence > {prediction['confidence'] * 0.8}")
            
            if "transition_type" in prediction:
                outcomes["expected_transition"] = prediction["transition_type"]
                outcomes["success_criteria"].append(f"Observe {prediction['transition_type']} transition")
        
        return outcomes
    
    def _compute_confidence_intervals(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute confidence intervals for prediction
        
        Args:
            prediction: Theoretical prediction
            
        Returns:
            Confidence intervals
        """
        intervals = {}
        
        if isinstance(prediction, dict):
            for key, value in prediction.items():
                if isinstance(value, (int, float)):
                    # Simple confidence interval
                    margin = abs(value) * 0.1  # 10% margin
                    intervals[key] = {
                        "point_estimate": value,
                        "lower_bound": value - margin,
                        "upper_bound": value + margin,
                        "confidence_level": 0.95
                    }
        
        return intervals
    
    def _fourier_analysis(self, trajectory: np.ndarray) -> Dict[str, Any]:
        """
        Perform Fourier analysis on trajectory
        
        Args:
            trajectory: Time series data
            
        Returns:
            Fourier analysis results
        """
        if len(trajectory) < 2:
            return {"error": "Insufficient data for Fourier analysis"}
        
        results = {}
        
        # Analyze each dimension
        for dim in range(min(trajectory.shape[1], 3)):  # Limit to first 3 dimensions
            signal = trajectory[:, dim]
            
            # Compute FFT
            fft = np.fft.fft(signal)
            freqs = np.fft.fftfreq(len(signal))
            
            # Find dominant frequencies
            power = np.abs(fft) ** 2
            dominant_idx = np.argsort(power)[-5:]  # Top 5 frequencies
            
            results[f"dimension_{dim}"] = {
                "dominant_frequencies": freqs[dominant_idx].tolist(),
                "power_spectrum_peaks": power[dominant_idx].tolist(),
                "total_power": float(np.sum(power)),
                "spectral_entropy": float(-np.sum(power * np.log(power + 1e-10)) / np.log(len(power)))
            }
        
        return results
    
    def _wavelet_analysis(self, trajectory: np.ndarray) -> Dict[str, Any]:
        """
        Perform wavelet analysis on trajectory
        
        Args:
            trajectory: Time series data
            
        Returns:
            Wavelet analysis results
        """
        if len(trajectory) < 4:
            return {"error": "Insufficient data for wavelet analysis"}
        
        # Simplified wavelet analysis using differences at multiple scales
        results = {}
        
        for scale in [1, 2, 4, 8]:
            if scale >= len(trajectory):
                continue
            
            # Simple Haar wavelet approximation
            coeffs = []
            for i in range(0, len(trajectory) - scale, scale):
                segment = trajectory[i:i+scale]
                coeff = np.mean(segment, axis=0)
                coeffs.append(coeff)
            
            coeffs = np.array(coeffs)
            
            results[f"scale_{scale}"] = {
                "n_coefficients": len(coeffs),
                "mean_magnitude": float(np.mean(np.linalg.norm(coeffs, axis=1))),
                "variance": float(np.var(np.linalg.norm(coeffs, axis=1)))
            }
        
        return results
    
    def _recurrence_analysis(self, trajectory: np.ndarray) -> Dict[str, Any]:
        """
        Perform recurrence analysis on trajectory
        
        Args:
            trajectory: Time series data
            
        Returns:
            Recurrence analysis results
        """
        if len(trajectory) < 10:
            return {"error": "Insufficient data for recurrence analysis"}
        
        # Compute recurrence matrix
        n = len(trajectory)
        distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                distances[i, j] = np.linalg.norm(trajectory[i] - trajectory[j])
        
        # Threshold for recurrence
        threshold = np.percentile(distances, 10)
        recurrence_matrix = distances < threshold
        
        # Compute recurrence metrics
        results = {
            "recurrence_rate": float(np.sum(recurrence_matrix) / (n * n)),
            "determinism": float(self._compute_determinism(recurrence_matrix)),
            "mean_diagonal_length": float(self._compute_mean_diagonal_length(recurrence_matrix)),
            "entropy": float(self._compute_recurrence_entropy(recurrence_matrix))
        }
        
        return results
    
    def _compute_determinism(self, recurrence_matrix: np.ndarray) -> float:
        """
        Compute determinism from recurrence matrix
        
        Args:
            recurrence_matrix: Binary recurrence matrix
            
        Returns:
            Determinism score
        """
        n = len(recurrence_matrix)
        diagonal_lines = 0
        total_points = np.sum(recurrence_matrix)
        
        # Count diagonal lines
        for offset in range(1, n):
            diagonal = np.diagonal(recurrence_matrix, offset)
            # Count consecutive True values
            in_line = False
            line_length = 0
            
            for point in diagonal:
                if point:
                    if not in_line:
                        in_line = True
                        line_length = 1
                    else:
                        line_length += 1
                else:
                    if in_line and line_length >= 2:
                        diagonal_lines += line_length
                    in_line = False
                    line_length = 0
            
            if in_line and line_length >= 2:
                diagonal_lines += line_length
        
        return diagonal_lines / (total_points + 1e-10)
    
    def _compute_mean_diagonal_length(self, recurrence_matrix: np.ndarray) -> float:
        """
        Compute mean diagonal line length
        
        Args:
            recurrence_matrix: Binary recurrence matrix
            
        Returns:
            Mean diagonal length
        """
        n = len(recurrence_matrix)
        lengths = []
        
        for offset in range(1, n):
            diagonal = np.diagonal(recurrence_matrix, offset)
            
            # Find line lengths
            in_line = False
            line_length = 0
            
            for point in diagonal:
                if point:
                    if not in_line:
                        in_line = True
                        line_length = 1
                    else:
                        line_length += 1
                else:
                    if in_line and line_length >= 2:
                        lengths.append(line_length)
                    in_line = False
                    line_length = 0
            
            if in_line and line_length >= 2:
                lengths.append(line_length)
        
        return np.mean(lengths) if lengths else 0.0
    
    def _compute_recurrence_entropy(self, recurrence_matrix: np.ndarray) -> float:
        """
        Compute entropy of recurrence matrix
        
        Args:
            recurrence_matrix: Binary recurrence matrix
            
        Returns:
            Recurrence entropy
        """
        # Simplified entropy based on distribution of line lengths
        n = len(recurrence_matrix)
        line_lengths = []
        
        for offset in range(-n+1, n):
            diagonal = np.diagonal(recurrence_matrix, offset)
            if len(diagonal) > 0:
                # Count consecutive segments
                segments = np.split(diagonal, np.where(~diagonal)[0])
                for seg in segments:
                    if len(seg) >= 2 and np.all(seg):
                        line_lengths.append(len(seg))
        
        if not line_lengths:
            return 0.0
        
        # Compute probability distribution
        unique_lengths, counts = np.unique(line_lengths, return_counts=True)
        probs = counts / np.sum(counts)
        
        # Shannon entropy
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        
        return entropy
    
    def _identify_critical_regions(self, states: np.ndarray, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify critical regions based on metrics
        
        Args:
            states: State space data
            metrics: Computed metrics
            
        Returns:
            List of critical regions
        """
        critical_regions = []
        
        # Check variance indicators
        if 'variance' in metrics:
            var_data = metrics['variance']
            if var_data['variance_ratio'] > 10:
                critical_regions.append({
                    'type': 'high_variance_ratio',
                    'indicator': 'variance',
                    'severity': 'high',
                    'dimensions': var_data['high_variance_dimensions']
                })
        
        # Check correlation indicators
        if 'correlation' in metrics:
            corr_data = metrics['correlation']
            if corr_data['spectral_gap'] < 0.1:
                critical_regions.append({
                    'type': 'small_spectral_gap',
                    'indicator': 'correlation',
                    'severity': 'medium',
                    'value': corr_data['spectral_gap']
                })
        
        # Check entropy indicators
        if 'entropy' in metrics:
            entropy_data = metrics['entropy']
            if entropy_data['complexity_estimate'] > 0.8:
                critical_regions.append({
                    'type': 'high_complexity',
                    'indicator': 'entropy',
                    'severity': 'medium',
                    'value': entropy_data['complexity_estimate']
                })
        
        return critical_regions