"""
Integration utilities for Tekton metrics system.

This module provides tools for integrating the metrics system
with the Tekton core architecture.
"""

import logging
import functools
import time
from typing import Dict, List, Any, Optional, Callable, Union
import inspect

from .collector import MetricsCollector
from .storage.sqlite import SQLiteMetricsStorage
from .analysis.spectral_analyzer import SpectralAnalyzer
from .visualization import ConsoleVisualizer, JSONVisualizer

logger = logging.getLogger(__name__)

class MetricsManager:
    """Manages metrics collection and analysis for Tekton."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, storage_path=None, enabled=True):
        """Get the singleton instance of MetricsManager.
        
        Args:
            storage_path: Optional path to metrics storage
            enabled: Whether metrics collection is enabled
            
        Returns:
            MetricsManager instance
        """
        if cls._instance is None:
            cls._instance = cls(storage_path, enabled)
        return cls._instance
    
    def __init__(self, storage_path=None, enabled=True):
        """Initialize the metrics manager.
        
        Args:
            storage_path: Optional path to metrics storage
            enabled: Whether metrics collection is enabled
        """
        self.enabled = enabled
        
        # Initialize storage
        if storage_path:
            self.storage = SQLiteMetricsStorage(storage_path)
        else:
            # Store in tekton directory
            import os
            from pathlib import Path
            tekton_root = Path(__file__).parent.parent.parent.parent.absolute()
            db_path = os.path.join(tekton_root, "tekton_metrics.db")
            self.storage = SQLiteMetricsStorage(db_path)
        
        # Initialize collector and analyzer
        self.collector = MetricsCollector(self.storage)
        self.collector.active = enabled
        
        self.analyzer = SpectralAnalyzer(self.storage)
        
        # Initialize visualizers
        self.console_visualizer = ConsoleVisualizer(self.storage)
        self.json_visualizer = JSONVisualizer(self.storage)
        
        # Current session tracking
        self.current_session_id = None
        
        logger.info(f"Metrics Manager initialized (enabled={enabled}, storage={storage_path})")
    
    def start_session(self, prompt: str, config: Dict[str, Any]) -> str:
        """Start a new metrics collection session.
        
        Args:
            prompt: The input prompt text
            config: Configuration of components used
            
        Returns:
            Session ID
        """
        if not self.enabled:
            return None
            
        self.current_session_id = self.collector.start_session(prompt, config)
        return self.current_session_id
    
    def complete_session(self, response: str, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the current metrics collection session.
        
        Args:
            response: Response text generated
            performance_metrics: Performance metrics
            
        Returns:
            Collected session data
        """
        if not self.enabled or not self.current_session_id:
            return None
            
        session_data = self.collector.complete_session(response, performance_metrics)
        self.current_session_id = None
        
        if session_data:
            # Analyze the completed session
            analysis = self.analyzer.analyze_session(session_data)
            return analysis
        
        return None
    
    def record_component_activation(self, component_id: str, activation_data: Dict[str, Any]):
        """Record activation metrics for a component.
        
        Args:
            component_id: ID of the activated component
            activation_data: Data about the activation
        """
        if not self.enabled or not self.current_session_id:
            return
            
        self.collector.record_component_activation(component_id, activation_data)
    
    def record_propagation_step(self, source: str, destination: str, 
                               info_content: float, data: Optional[Dict[str, Any]] = None):
        """Record data propagation between components.
        
        Args:
            source: Source component ID
            destination: Destination component ID
            info_content: Measured information content
            data: Additional data about the propagation
        """
        if not self.enabled or not self.current_session_id:
            return
            
        self.collector.record_propagation_step(source, destination, info_content, data)
    
    def record_parameter_usage(self, component_id: str, total_params: int, active_params: int,
                              layer_data: Optional[Dict[str, Any]] = None):
        """Record parameter usage metrics.
        
        Args:
            component_id: ID of the component
            total_params: Total parameters available
            active_params: Number of active parameters
            layer_data: Optional layer-specific data
        """
        if not self.enabled or not self.current_session_id:
            return
            
        self.collector.record_parameter_usage(component_id, total_params, active_params, layer_data)
        
    def record_latent_reasoning(self, component_id: str, iteration: int, initial_confidence: float,
                               final_confidence: float, iterations_required: int,
                               reasoning_data: Optional[Dict[str, Any]] = None):
        """Record latent space reasoning metrics.
        
        Args:
            component_id: ID of the component doing the reasoning
            iteration: Current iteration number
            initial_confidence: Initial confidence score
            final_confidence: Final confidence score
            iterations_required: Total iterations required
            reasoning_data: Optional additional data about the reasoning process
        """
        if not self.enabled or not self.current_session_id:
            return
            
        self.collector.record_latent_reasoning(
            component_id, iteration, initial_confidence, final_confidence, 
            iterations_required, reasoning_data
        )
        
    def record_cross_modal_operation(self, source_modality: str, target_modality: str, 
                                    operation_type: str, success: bool,
                                    operation_data: Optional[Dict[str, Any]] = None):
        """Record cross-modal integration metrics.
        
        Args:
            source_modality: Source modality (e.g., "text", "image", "audio")
            target_modality: Target modality
            operation_type: Type of cross-modal operation
            success: Whether the operation was successful
            operation_data: Optional additional data about the operation
        """
        if not self.enabled or not self.current_session_id:
            return
            
        self.collector.record_cross_modal_operation(
            source_modality, target_modality, operation_type, success, operation_data
        )
        
    def record_concept_stability(self, concept_id: str, context: str, vector_representation: List[float],
                                stability_data: Optional[Dict[str, Any]] = None):
        """Record concept stability metrics.
        
        Args:
            concept_id: Identifier for the concept
            context: Context in which the concept was observed
            vector_representation: Vector representation of the concept
            stability_data: Optional additional data about concept stability
        """
        if not self.enabled or not self.current_session_id:
            return
            
        self.collector.record_concept_stability(
            concept_id, context, vector_representation, stability_data
        )
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a session by ID.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session data
        """
        return self.storage.get_session(session_id)
    
    def get_sessions(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get multiple sessions.
        
        Args:
            limit: Maximum number of sessions
            offset: Offset for pagination
            
        Returns:
            List of session data
        """
        return self.storage.get_sessions(limit=limit, offset=offset)
    
    def analyze_sessions(self, session_ids: List[str]) -> Dict[str, Any]:
        """Analyze multiple sessions.
        
        Args:
            session_ids: List of session IDs
            
        Returns:
            Analysis results
        """
        sessions = [self.get_session(session_id) for session_id in session_ids if session_id]
        sessions = [s for s in sessions if s]  # Filter out None values
        
        return self.analyzer.analyze_sessions(sessions)
    
    def find_catastrophe_points(self, limit: int = 100, window_size: int = 5) -> List[Dict[str, Any]]:
        """Identify potential catastrophe points in model behavior.
        
        Args:
            limit: Maximum number of sessions to analyze
            window_size: Window size for detecting sudden changes
            
        Returns:
            List of potential catastrophe points
        """
        sessions = self.get_sessions(limit=limit)
        return self.analyzer.identify_catastrophe_points(sessions, window_size=window_size)
        
    def analyze_bifurcation_proximity(self, num_recent: int = 10) -> Dict[str, Any]:
        """Calculate the bifurcation proximity index for recent sessions.
        
        BPI indicates how close the system is to a capability bifurcation.
        
        Args:
            num_recent: Number of recent sessions to consider
            
        Returns:
            Dict with bifurcation proximity analysis
        """
        sessions = self.get_sessions(limit=num_recent)
        return self.analyzer.calculate_bifurcation_proximity(sessions, num_recent=num_recent)
        
    def analyze_parameter_sensitivity(self, parameters: List[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Calculate sensitivity to different control parameters.
        
        Args:
            parameters: Optional list of parameters to analyze
            limit: Maximum number of sessions to analyze
            
        Returns:
            Dict with parameter sensitivity analysis
        """
        sessions = self.get_sessions(limit=limit)
        return self.analyzer.calculate_control_parameter_sensitivity(sessions, parameters=parameters)
        
    def detect_hysteresis(self, parameter: str, limit: int = 100) -> Dict[str, Any]:
        """Calculate hysteresis in performance as a parameter changes.
        
        Args:
            parameter: The parameter to analyze
            limit: Maximum number of sessions to analyze
            
        Returns:
            Dict with hysteresis analysis
        """
        sessions = self.get_sessions(limit=limit)
        return self.analyzer.calculate_hysteresis_detection(sessions, parameter=parameter)
    
    def visualize_session(self, session_id: str, format: str = "console") -> str:
        """Visualize a session.
        
        Args:
            session_id: ID of the session
            format: Output format (console or json)
            
        Returns:
            Visualization string
        """
        session = self.get_session(session_id)
        if not session:
            return f"Session {session_id} not found"
            
        if format == "json":
            return self.json_visualizer.visualize_session(session)
        else:
            return self.console_visualizer.visualize_session(session)
    
    def visualize_comparison(self, session_ids: List[str], format: str = "console") -> str:
        """Visualize a comparison of multiple sessions.
        
        Args:
            session_ids: List of session IDs
            format: Output format (console or json)
            
        Returns:
            Visualization string
        """
        sessions = [self.get_session(session_id) for session_id in session_ids if session_id]
        sessions = [s for s in sessions if s]  # Filter out None values
        
        if format == "json":
            return self.json_visualizer.visualize_comparison(sessions)
        else:
            return self.console_visualizer.visualize_comparison(sessions)
    
    def visualize_trend(self, limit: int = 10, format: str = "console") -> str:
        """Visualize a trend across multiple sessions.
        
        Args:
            limit: Maximum number of sessions
            format: Output format (console or json)
            
        Returns:
            Visualization string
        """
        sessions = self.get_sessions(limit=limit)
        
        if format == "json":
            return self.json_visualizer.visualize_trend(sessions)
        else:
            return self.console_visualizer.visualize_trend(sessions)


def track_metrics(func: Optional[Callable] = None, component_id: Optional[str] = None):
    """Decorator to track metrics for a function.
    
    Args:
        func: The function to decorate
        component_id: Optional component ID
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Get component ID
            cid = component_id
            if cid is None:
                # Try to infer from function name or module
                module = f.__module__.split('.')[-1]
                cid = f"{module}.{f.__name__}"
            
            # Get metrics manager
            metrics = MetricsManager.get_instance()
            
            # Record activation
            activation_data = {
                "args_count": len(args),
                "kwargs_count": len(kwargs),
                "function_name": f.__name__
            }
            metrics.record_component_activation(cid, activation_data)
            
            # Measure start time
            start_time = time.time()
            
            # Call the function
            result = f(*args, **kwargs)
            
            # Measure end time
            end_time = time.time()
            
            # Calculate result size
            result_size = 0
            if isinstance(result, str):
                result_size = len(result)
            elif isinstance(result, (list, tuple, dict)):
                result_size = len(result)
            
            # Record propagation
            # Assume the result propagates to the caller
            caller_frame = inspect.currentframe().f_back
            if caller_frame:
                caller_module = caller_frame.f_globals.get('__name__', '').split('.')[-1]
                caller_function = caller_frame.f_code.co_name
                caller_id = f"{caller_module}.{caller_function}"
                
                # Record propagation from this component to the caller
                metrics.record_propagation_step(
                    source=cid,
                    destination=caller_id,
                    info_content=result_size,
                    data={
                        "duration": end_time - start_time,
                        "result_type": type(result).__name__
                    }
                )
            
            return result
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)