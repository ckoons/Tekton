"""
Core metrics collection for Tekton architecture.

This module provides tools for collecting performance and
architectural metrics during system operation.
"""

import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Data structure for storing metrics from a processing session."""
    
    id: str
    prompt: str
    config: Dict[str, Any]
    start_time: float
    
    # Runtime data
    component_activations: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    propagation_path: List[Dict[str, Any]] = field(default_factory=list)
    parameter_usage: Dict[str, Dict[str, float]] = field(default_factory=dict)
    latent_reasoning: List[Dict[str, Any]] = field(default_factory=list)
    cross_modal_operations: List[Dict[str, Any]] = field(default_factory=list)
    concept_stability: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    # Results
    end_time: Optional[float] = None
    response: Optional[str] = None
    performance: Dict[str, Any] = field(default_factory=dict)
    
    # Derived metrics
    spectral_metrics: Dict[str, float] = field(default_factory=dict)
    catastrophe_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON for storage."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionData':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class MetricsCollector:
    """Collects metrics during system operation."""
    
    def __init__(self, storage_engine=None):
        """Initialize metrics collector.
        
        Args:
            storage_engine: Optional storage engine for metrics
        """
        self.storage = storage_engine
        self.current_session = None
        self.active = True
    
    def start_session(self, prompt: str, config: Dict[str, Any]) -> str:
        """Start a new metrics collection session.
        
        Args:
            prompt: The input prompt text
            config: Configuration of components used
            
        Returns:
            Session ID
        """
        if not self.active:
            logger.info("Metrics collection disabled")
            return "disabled"
            
        session_id = str(uuid.uuid4())
        self.current_session = SessionData(
            id=session_id,
            prompt=prompt,
            config=config,
            start_time=time.time()
        )
        
        logger.debug(f"Started metrics session {session_id}")
        return session_id
    
    def record_component_activation(self, 
                                   component_id: str, 
                                   activation_data: Dict[str, Any]):
        """Record activation metrics for a component.
        
        Args:
            component_id: ID of the activated component
            activation_data: Data about the activation
        """
        if not self.active or not self.current_session:
            return
            
        if component_id not in self.current_session.component_activations:
            self.current_session.component_activations[component_id] = []
            
        activation_record = {
            "timestamp": time.time(),
            **activation_data
        }
        
        self.current_session.component_activations[component_id].append(activation_record)
    
    def record_propagation_step(self, 
                               source: str, 
                               destination: str, 
                               info_content: float,
                               data: Optional[Dict[str, Any]] = None):
        """Record data propagation between components.
        
        Args:
            source: Source component ID
            destination: Destination component ID
            info_content: Measured information content
            data: Additional data about the propagation
        """
        if not self.active or not self.current_session:
            return
            
        step_data = {
            "timestamp": time.time(),
            "source": source,
            "destination": destination,
            "info_content": info_content
        }
        
        if data:
            step_data.update(data)
            
        self.current_session.propagation_path.append(step_data)
    
    def record_parameter_usage(self,
                              component_id: str,
                              total_params: int,
                              active_params: int,
                              layer_data: Optional[Dict[str, Any]] = None):
        """Record parameter usage metrics.
        
        Args:
            component_id: ID of the component
            total_params: Total parameters available
            active_params: Number of active parameters
            layer_data: Optional layer-specific data
        """
        if not self.active or not self.current_session:
            return
            
        usage_data = {
            "timestamp": time.time(),
            "total": total_params,
            "active": active_params,
            "utilization": active_params / total_params if total_params > 0 else 0
        }
        
        if layer_data:
            usage_data["layers"] = layer_data
            
        self.current_session.parameter_usage[component_id] = usage_data
        
    def record_latent_reasoning(self,
                               component_id: str,
                               iteration: int,
                               initial_confidence: float,
                               final_confidence: float,
                               iterations_required: int,
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
        if not self.active or not self.current_session:
            return
            
        reasoning_record = {
            "timestamp": time.time(),
            "component_id": component_id,
            "iteration": iteration,
            "initial_confidence": initial_confidence,
            "final_confidence": final_confidence,
            "iterations_required": iterations_required,
            "cognitive_convergence_rate": (final_confidence - initial_confidence) / max(1, iterations_required)
        }
        
        if reasoning_data:
            reasoning_record.update(reasoning_data)
            
        self.current_session.latent_reasoning.append(reasoning_record)
        
    def record_cross_modal_operation(self,
                                    source_modality: str,
                                    target_modality: str,
                                    operation_type: str,
                                    success: bool,
                                    operation_data: Optional[Dict[str, Any]] = None):
        """Record cross-modal integration metrics.
        
        Args:
            source_modality: Source modality (e.g., "text", "image", "audio")
            target_modality: Target modality
            operation_type: Type of cross-modal operation
            success: Whether the operation was successful
            operation_data: Optional additional data about the operation
        """
        if not self.active or not self.current_session:
            return
            
        operation_record = {
            "timestamp": time.time(),
            "source_modality": source_modality,
            "target_modality": target_modality,
            "operation_type": operation_type,
            "success": success
        }
        
        if operation_data:
            operation_record.update(operation_data)
            
        self.current_session.cross_modal_operations.append(operation_record)
        
    def record_concept_stability(self,
                                concept_id: str,
                                context: str,
                                vector_representation: List[float],
                                stability_data: Optional[Dict[str, Any]] = None):
        """Record concept stability metrics.
        
        Args:
            concept_id: Identifier for the concept
            context: Context in which the concept was observed
            vector_representation: Vector representation of the concept
            stability_data: Optional additional data about concept stability
        """
        if not self.active or not self.current_session:
            return
            
        if concept_id not in self.current_session.concept_stability:
            self.current_session.concept_stability[concept_id] = []
            
        stability_record = {
            "timestamp": time.time(),
            "context": context,
            "vector_representation": vector_representation
        }
        
        if stability_data:
            stability_record.update(stability_data)
            
        self.current_session.concept_stability[concept_id].append(stability_record)
    
    def complete_session(self, 
                        response: str, 
                        performance_metrics: Dict[str, Any],
                        calculate_spectral: bool = True):
        """Complete the metrics collection session.
        
        Args:
            response: Response text generated
            performance_metrics: Performance metrics
            calculate_spectral: Whether to calculate spectral metrics
        """
        if not self.active or not self.current_session:
            return
            
        self.current_session.end_time = time.time()
        self.current_session.response = response
        self.current_session.performance = performance_metrics
        
        # Calculate spectral metrics
        if calculate_spectral:
            self._calculate_spectral_metrics()
        
        # Save to storage if available
        if self.storage:
            try:
                self.storage.store_session(self.current_session)
                logger.debug(f"Stored metrics for session {self.current_session.id}")
            except Exception as e:
                logger.error(f"Failed to store metrics: {str(e)}")
        
        session_data = self.current_session
        self.current_session = None
        return session_data
    
    def _calculate_spectral_metrics(self):
        """Calculate spectral analysis metrics from collected data."""
        if not self.current_session:
            return
            
        spectral_metrics = {}
        catastrophe_metrics = {}
        
        # Calculate Depth Efficiency (DE)
        # DE = performance / layer count
        try:
            total_layers = sum(len(data.get("layers", {})) 
                             for data in self.current_session.parameter_usage.values())
            if "accuracy" in self.current_session.performance and total_layers > 0:
                spectral_metrics["depth_efficiency"] = self.current_session.performance["accuracy"] / total_layers
        except (KeyError, ZeroDivisionError):
            spectral_metrics["depth_efficiency"] = 0
            
        # Calculate Parametric Utilization (PU)
        # PU = active parameters / total parameters
        try:
            total_params = sum(data["total"] for data in self.current_session.parameter_usage.values())
            active_params = sum(data["active"] for data in self.current_session.parameter_usage.values())
            
            if total_params > 0:
                spectral_metrics["parametric_utilization"] = active_params / total_params
            else:
                spectral_metrics["parametric_utilization"] = 0
        except (KeyError, ZeroDivisionError):
            spectral_metrics["parametric_utilization"] = 0
            
        # Calculate Minimum Propagation Threshold (MPT)
        # MPT = shortest successful path through components
        try:
            if self.current_session.propagation_path:
                # Count unique components in the propagation path
                components = set()
                for step in self.current_session.propagation_path:
                    components.add(step["source"])
                    components.add(step["destination"])
                
                spectral_metrics["min_propagation_threshold"] = len(components)
            else:
                spectral_metrics["min_propagation_threshold"] = 0
        except Exception:
            spectral_metrics["min_propagation_threshold"] = 0
            
        # Calculate Modularity Quotient (MQ)
        # MQ = 1 - (cross-module info flow / within-module info flow)
        try:
            cross_module_flow = 0
            within_module_flow = 0
            
            for step in self.current_session.propagation_path:
                # If source and destination are in the same component family
                if step["source"].split('.')[0] == step["destination"].split('.')[0]:
                    within_module_flow += step.get("info_content", 1)
                else:
                    cross_module_flow += step.get("info_content", 1)
            
            total_flow = cross_module_flow + within_module_flow
            if total_flow > 0:
                spectral_metrics["modularity_quotient"] = 1 - (cross_module_flow / total_flow)
            else:
                spectral_metrics["modularity_quotient"] = 0
        except Exception:
            spectral_metrics["modularity_quotient"] = 0
        
        # Calculate Cognitive Convergence Rate (CCR)
        # CCR = (final confidence - initial confidence) / iteration count
        try:
            if self.current_session.latent_reasoning:
                ccr_values = [record.get("cognitive_convergence_rate", 0) 
                             for record in self.current_session.latent_reasoning]
                spectral_metrics["cognitive_convergence_rate"] = sum(ccr_values) / len(ccr_values)
            else:
                spectral_metrics["cognitive_convergence_rate"] = 0
        except Exception:
            spectral_metrics["cognitive_convergence_rate"] = 0
            
        # Calculate Latent Space Navigation Efficiency (LSNE)
        # LSNE = (conceptual distance covered) / (computational steps required)
        try:
            if self.current_session.latent_reasoning:
                # Use iteration counts as proxy for computational steps
                total_iterations = sum(record.get("iterations_required", 1) 
                                      for record in self.current_session.latent_reasoning)
                
                # Use confidence gain as proxy for conceptual distance
                total_confidence_gain = sum(record.get("final_confidence", 0) - record.get("initial_confidence", 0)
                                          for record in self.current_session.latent_reasoning)
                
                if total_iterations > 0:
                    spectral_metrics["latent_space_navigation_efficiency"] = total_confidence_gain / total_iterations
                else:
                    spectral_metrics["latent_space_navigation_efficiency"] = 0
            else:
                spectral_metrics["latent_space_navigation_efficiency"] = 0
        except Exception:
            spectral_metrics["latent_space_navigation_efficiency"] = 0
            
        # Calculate Cross-Modal Integration Index (CMII)
        # CMII = Σ(cross-modal transfer success) / total cross-modal operations
        try:
            if self.current_session.cross_modal_operations:
                successful_ops = sum(1 for op in self.current_session.cross_modal_operations if op.get("success", False))
                total_ops = len(self.current_session.cross_modal_operations)
                
                if total_ops > 0:
                    spectral_metrics["cross_modal_integration_index"] = successful_ops / total_ops
                else:
                    spectral_metrics["cross_modal_integration_index"] = 0
            else:
                spectral_metrics["cross_modal_integration_index"] = 0
        except Exception:
            spectral_metrics["cross_modal_integration_index"] = 0
            
        # Calculate Conceptual Stability Coefficient (CSC)
        # CSC = 1 - (concept vector deviation across inputs / maximum possible deviation)
        try:
            if self.current_session.concept_stability:
                stability_scores = []
                
                for concept_id, observations in self.current_session.concept_stability.items():
                    if len(observations) >= 2:
                        # Calculate pairwise cosine similarities between vector representations
                        similarities = []
                        
                        for i in range(len(observations)):
                            vec1 = observations[i].get("vector_representation", [])
                            
                            for j in range(i+1, len(observations)):
                                vec2 = observations[j].get("vector_representation", [])
                                
                                # Skip if vectors are empty
                                if not vec1 or not vec2 or len(vec1) != len(vec2):
                                    continue
                                    
                                # Calculate cosine similarity
                                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                                mag1 = sum(a * a for a in vec1) ** 0.5
                                mag2 = sum(b * b for b in vec2) ** 0.5
                                
                                if mag1 > 0 and mag2 > 0:
                                    similarity = dot_product / (mag1 * mag2)
                                    similarities.append(similarity)
                        
                        if similarities:
                            avg_similarity = sum(similarities) / len(similarities)
                            stability_scores.append(avg_similarity)
                
                if stability_scores:
                    # Conceptual stability is the average similarity across concepts
                    # (1 = perfectly stable, 0 = completely unstable)
                    spectral_metrics["conceptual_stability_coefficient"] = sum(stability_scores) / len(stability_scores)
                else:
                    spectral_metrics["conceptual_stability_coefficient"] = 0
            else:
                spectral_metrics["conceptual_stability_coefficient"] = 0
        except Exception:
            spectral_metrics["conceptual_stability_coefficient"] = 0
            
        # Calculate Bifurcation Proximity Index (BPI) - catastrophe theory metric
        # This is a placeholder implementation as BPI requires historical data comparison
        catastrophe_metrics["bifurcation_proximity_index"] = 0
            
        # Calculate Control Parameter Sensitivity - catastrophe theory metric
        # This is a placeholder as we need to implement parameter perturbation analysis
        catastrophe_metrics["control_parameter_sensitivity"] = {}
            
        # Calculate State Space Stability Metric (SSSM) - catastrophe theory metric
        # SSSM = 1 / (average performance variance under noise)
        # For now, use a default value
        catastrophe_metrics["state_space_stability"] = 1.0
            
        # Calculate Hysteresis Detection Index (HDI) - catastrophe theory metric
        # This would require comparing upward and downward parameter sweeps
        catastrophe_metrics["hysteresis_detection_index"] = 0
            
        # Calculate Critical Slowing Down Detector (CSDD) - catastrophe theory metric
        # This would require comparing convergence times to baseline
        catastrophe_metrics["critical_slowing_down"] = 1.0
            
        # Store the calculated metrics
        self.current_session.spectral_metrics = spectral_metrics
        self.current_session.catastrophe_metrics = catastrophe_metrics