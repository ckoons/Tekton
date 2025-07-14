"""
Sophia integration bridge for theory-experiment collaboration
Enables bidirectional communication between Noesis and Sophia
"""

import asyncio
import httpx
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ...models.experiment import ExperimentType, ExperimentStatus

logger = logging.getLogger(__name__)


class CollaborationProtocol(str, Enum):
    """Types of collaboration protocols between Noesis and Sophia"""
    THEORY_VALIDATION = "theory_validation"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENT_DESIGN = "experiment_design"
    RESULTS_INTERPRETATION = "results_interpretation"
    ITERATIVE_REFINEMENT = "iterative_refinement"


@dataclass
class TheoryExperimentProtocol:
    """Protocol for theory-experiment collaboration"""
    protocol_id: str
    protocol_type: CollaborationProtocol
    theory_component: Dict[str, Any]  # From Noesis
    experiment_component: Dict[str, Any]  # From/For Sophia
    iteration: int = 0
    status: str = "initialized"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'protocol_id': self.protocol_id,
            'protocol_type': self.protocol_type,
            'theory_component': self.theory_component,
            'experiment_component': self.experiment_component,
            'iteration': self.iteration,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'history': self.history
        }


class SophiaBridge:
    """
    Bridge for integrating Noesis theoretical analysis with Sophia experiments
    """
    
    def __init__(self, sophia_url: str = "http://localhost:8003"):
        self.sophia_url = sophia_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.active_protocols: Dict[str, TheoryExperimentProtocol] = {}
        
        logger.info(f"Initialized Sophia bridge with URL: {sophia_url}")
    
    async def create_theory_validation_protocol(self,
                                              theoretical_prediction: Dict[str, Any],
                                              confidence_intervals: Dict[str, Any],
                                              suggested_metrics: List[str]) -> TheoryExperimentProtocol:
        """
        Create a protocol for validating theoretical predictions
        
        Args:
            theoretical_prediction: Noesis theoretical model predictions
            confidence_intervals: Confidence intervals for predictions
            suggested_metrics: Metrics to validate
            
        Returns:
            Theory-experiment protocol
        """
        protocol_id = f"tep_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create experiment design for Sophia
        experiment_design = {
            "name": f"Theory Validation: {theoretical_prediction.get('model_type', 'Unknown')}",
            "description": f"Validating theoretical predictions from Noesis model",
            "experiment_type": "baseline_comparison",
            "hypothesis": self._format_hypothesis(theoretical_prediction),
            "metrics": suggested_metrics,
            "parameters": {
                "theoretical_baseline": theoretical_prediction,
                "confidence_intervals": confidence_intervals,
                "validation_criteria": self._generate_validation_criteria(
                    theoretical_prediction,
                    confidence_intervals
                )
            },
            "tags": ["theory_validation", "noesis_sophia_collaboration"]
        }
        
        protocol = TheoryExperimentProtocol(
            protocol_id=protocol_id,
            protocol_type=CollaborationProtocol.THEORY_VALIDATION,
            theory_component={
                "prediction": theoretical_prediction,
                "confidence_intervals": confidence_intervals,
                "suggested_metrics": suggested_metrics
            },
            experiment_component=experiment_design
        )
        
        self.active_protocols[protocol_id] = protocol
        
        # Submit to Sophia
        await self._submit_experiment_to_sophia(experiment_design, protocol_id)
        
        return protocol
    
    async def generate_hypothesis_from_analysis(self,
                                              analysis_results: Dict[str, Any],
                                              analysis_type: str) -> Dict[str, Any]:
        """
        Generate experimental hypothesis from theoretical analysis
        
        Args:
            analysis_results: Results from Noesis analysis
            analysis_type: Type of analysis performed
            
        Returns:
            Hypothesis and experiment design
        """
        # Extract key findings based on analysis type
        if analysis_type == "catastrophe_analysis":
            predictions = analysis_results.get("predictions", [])
            if predictions:
                hypothesis = (
                    f"The system will undergo a {predictions[0]['transition_type']} "
                    f"within {predictions[0].get('estimated_time', 'unknown')} time units"
                )
                experiment_type = "before_after"
            else:
                hypothesis = "The system is in a stable state with no imminent transitions"
                experiment_type = "baseline_comparison"
                
        elif analysis_type == "regime_dynamics":
            current_regime = analysis_results.get("current_regime")
            predicted_transitions = analysis_results.get("predicted_transitions", [])
            
            if predicted_transitions:
                next_transition = predicted_transitions[0]
                hypothesis = (
                    f"The system will transition from regime {current_regime} "
                    f"to regime {next_transition['to_regime']} "
                    f"with probability {next_transition['probability']:.2f}"
                )
                experiment_type = "parameter_tuning"
            else:
                hypothesis = f"The system will remain in regime {current_regime}"
                experiment_type = "baseline_comparison"
                
        elif analysis_type == "manifold_analysis":
            intrinsic_dim = analysis_results.get("manifold_structure", {}).get("intrinsic_dimension", 0)
            hypothesis = (
                f"The collective system operates in a {intrinsic_dim}-dimensional manifold "
                f"with characteristic topology"
            )
            experiment_type = "multivariate"
            
        else:
            hypothesis = "The theoretical model predicts specific system behavior"
            experiment_type = "baseline_comparison"
        
        # Design experiment
        experiment_design = await self._design_experiment_for_hypothesis(
            hypothesis,
            analysis_results,
            experiment_type
        )
        
        return {
            "hypothesis": hypothesis,
            "experiment_design": experiment_design,
            "source_analysis": analysis_type,
            "key_predictions": self._extract_key_predictions(analysis_results, analysis_type)
        }
    
    async def interpret_experiment_results(self,
                                         experiment_id: str,
                                         theoretical_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret Sophia experiment results in context of Noesis theory
        
        Args:
            experiment_id: Sophia experiment ID
            theoretical_context: Theoretical framework context
            
        Returns:
            Interpreted results with theoretical insights
        """
        # Fetch experiment results from Sophia
        experiment_results = await self._fetch_experiment_results(experiment_id)
        
        if not experiment_results:
            return {
                "status": "error",
                "message": "Could not fetch experiment results"
            }
        
        # Compare with theoretical predictions
        comparison = await self._compare_theory_experiment(
            theoretical_context,
            experiment_results
        )
        
        # Generate insights
        insights = self._generate_insights(comparison)
        
        # Suggest refinements
        refinements = self._suggest_theory_refinements(comparison, insights)
        
        return {
            "experiment_id": experiment_id,
            "experiment_results": experiment_results,
            "theoretical_comparison": comparison,
            "insights": insights,
            "suggested_refinements": refinements,
            "validation_status": self._determine_validation_status(comparison)
        }
    
    async def create_iterative_refinement_cycle(self,
                                              initial_theory: Dict[str, Any],
                                              max_iterations: int = 5) -> Dict[str, Any]:
        """
        Create an iterative theory-experiment refinement cycle
        
        Args:
            initial_theory: Initial theoretical model
            max_iterations: Maximum refinement iterations
            
        Returns:
            Refinement cycle configuration
        """
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cycle_config = {
            "cycle_id": cycle_id,
            "initial_theory": initial_theory,
            "max_iterations": max_iterations,
            "current_iteration": 0,
            "convergence_criteria": {
                "min_improvement": 0.01,
                "confidence_threshold": 0.95,
                "validation_success_rate": 0.8
            },
            "history": [],
            "status": "initialized"
        }
        
        # Start first iteration
        first_experiment = await self._design_experiment_for_hypothesis(
            self._format_hypothesis(initial_theory),
            initial_theory,
            "baseline_comparison"
        )
        
        cycle_config["current_experiment"] = first_experiment
        
        return cycle_config
    
    async def _submit_experiment_to_sophia(self,
                                         experiment_design: Dict[str, Any],
                                         protocol_id: str) -> Optional[str]:
        """Submit experiment design to Sophia"""
        try:
            response = await self.client.post(
                f"{self.sophia_url}/api/experiments",
                json=experiment_design
            )
            
            if response.status_code == 200:
                result = response.json()
                experiment_id = result.get("data", {}).get("experiment_id")
                
                # Update protocol
                if protocol_id in self.active_protocols:
                    protocol = self.active_protocols[protocol_id]
                    protocol.experiment_component["experiment_id"] = experiment_id
                    protocol.status = "experiment_created"
                    protocol.updated_at = datetime.now()
                    
                logger.info(f"Created Sophia experiment {experiment_id} for protocol {protocol_id}")
                return experiment_id
            else:
                logger.error(f"Failed to create Sophia experiment: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting to Sophia: {str(e)}")
            return None
    
    async def _fetch_experiment_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Fetch experiment results from Sophia"""
        try:
            response = await self.client.get(
                f"{self.sophia_url}/api/experiments/{experiment_id}/results"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch experiment results: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching from Sophia: {str(e)}")
            return None
    
    def _format_hypothesis(self, theoretical_prediction: Dict[str, Any]) -> str:
        """Format theoretical prediction as testable hypothesis"""
        model_type = theoretical_prediction.get("model_type", "unknown")
        
        if "transition" in theoretical_prediction:
            return (
                f"Based on {model_type} model, the system will exhibit "
                f"{theoretical_prediction['transition']['type']} transition "
                f"under specified conditions"
            )
        elif "regime" in theoretical_prediction:
            return (
                f"The {model_type} model predicts the system operates in "
                f"regime {theoretical_prediction['regime']} with specific dynamics"
            )
        else:
            return f"The {model_type} model predicts specific measurable behavior"
    
    def _generate_validation_criteria(self,
                                    prediction: Dict[str, Any],
                                    confidence_intervals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate criteria for validating predictions"""
        criteria = []
        
        for key, interval in confidence_intervals.items():
            criteria.append({
                "metric": key,
                "expected_range": [
                    interval.get("lower_bound", 0),
                    interval.get("upper_bound", 1)
                ],
                "confidence_level": interval.get("confidence_level", 0.95)
            })
        
        return criteria
    
    async def _design_experiment_for_hypothesis(self,
                                              hypothesis: str,
                                              context: Dict[str, Any],
                                              experiment_type: str) -> Dict[str, Any]:
        """Design experiment based on hypothesis and context"""
        # Extract relevant metrics
        metrics = self._extract_relevant_metrics(context)
        
        # Determine components
        components = context.get("components", ["collective_system"])
        
        # Create experiment design
        return {
            "name": f"Test: {hypothesis[:50]}...",
            "description": hypothesis,
            "experiment_type": experiment_type,
            "target_components": components,
            "hypothesis": hypothesis,
            "metrics": metrics,
            "parameters": {
                "context": context,
                "duration": "adaptive",
                "sample_size": self._estimate_sample_size(context)
            },
            "tags": ["theory_driven", "noesis_hypothesis"]
        }
    
    def _extract_relevant_metrics(self, context: Dict[str, Any]) -> List[str]:
        """Extract relevant metrics from context"""
        metrics = []
        
        # Standard metrics
        metrics.extend(["accuracy", "latency", "throughput"])
        
        # Context-specific metrics
        if "manifold" in str(context):
            metrics.extend(["dimensionality", "curvature", "topology_stability"])
        if "regime" in str(context):
            metrics.extend(["regime_stability", "transition_probability", "residence_time"])
        if "catastrophe" in str(context):
            metrics.extend(["warning_signals", "critical_distance", "bifurcation_parameter"])
        
        return list(set(metrics))
    
    def _estimate_sample_size(self, context: Dict[str, Any]) -> int:
        """Estimate required sample size based on context"""
        # Base sample size
        base_size = 100
        
        # Adjust based on complexity
        if context.get("n_regimes", 1) > 2:
            base_size *= 2
        if context.get("dimensionality", 1) > 10:
            base_size *= 1.5
        if "catastrophe" in str(context):
            base_size *= 3  # Need more samples near critical points
        
        return int(base_size)
    
    def _extract_key_predictions(self,
                               analysis_results: Dict[str, Any],
                               analysis_type: str) -> List[Dict[str, Any]]:
        """Extract key testable predictions from analysis"""
        predictions = []
        
        if analysis_type == "catastrophe_analysis":
            for pred in analysis_results.get("predictions", []):
                predictions.append({
                    "type": "phase_transition",
                    "transition_type": pred.get("transition_type"),
                    "confidence": pred.get("confidence"),
                    "warning_signals": pred.get("warning_signals", [])
                })
                
        elif analysis_type == "regime_dynamics":
            predictions.append({
                "type": "regime_stability",
                "current_regime": analysis_results.get("current_regime"),
                "stability_score": analysis_results.get("stability_scores", {}).get(
                    str(analysis_results.get("current_regime")), 0
                )
            })
            
        return predictions
    
    async def _compare_theory_experiment(self,
                                       theory: Dict[str, Any],
                                       experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Compare theoretical predictions with experimental results"""
        comparison = {
            "matches": [],
            "mismatches": [],
            "unexpected": [],
            "metrics": {}
        }
        
        # Extract experimental metrics
        exp_metrics = experiment.get("metrics_summary", {})
        
        # Compare each theoretical prediction
        for prediction_key, prediction_value in theory.get("predictions", {}).items():
            if prediction_key in exp_metrics:
                exp_value = exp_metrics[prediction_key].get("mean", 0)
                
                # Check if within confidence intervals
                ci = theory.get("confidence_intervals", {}).get(prediction_key, {})
                lower = ci.get("lower_bound", prediction_value * 0.9)
                upper = ci.get("upper_bound", prediction_value * 1.1)
                
                if lower <= exp_value <= upper:
                    comparison["matches"].append({
                        "metric": prediction_key,
                        "predicted": prediction_value,
                        "observed": exp_value,
                        "within_ci": True
                    })
                else:
                    comparison["mismatches"].append({
                        "metric": prediction_key,
                        "predicted": prediction_value,
                        "observed": exp_value,
                        "deviation": abs(exp_value - prediction_value) / prediction_value
                    })
        
        # Check for unexpected observations
        for exp_key in exp_metrics:
            if exp_key not in theory.get("predictions", {}):
                comparison["unexpected"].append({
                    "metric": exp_key,
                    "value": exp_metrics[exp_key]
                })
        
        return comparison
    
    def _generate_insights(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate insights from theory-experiment comparison"""
        insights = []
        
        # Analyze matches
        match_rate = len(comparison["matches"]) / (
            len(comparison["matches"]) + len(comparison["mismatches"]) + 1e-10
        )
        
        if match_rate > 0.8:
            insights.append("Theory shows strong agreement with experimental results")
        elif match_rate > 0.5:
            insights.append("Theory shows moderate agreement with experimental results")
        else:
            insights.append("Theory shows significant deviations from experimental results")
        
        # Analyze mismatches
        for mismatch in comparison["mismatches"]:
            if mismatch["deviation"] > 0.5:
                insights.append(
                    f"Large deviation in {mismatch['metric']}: "
                    f"theory predicts {mismatch['predicted']:.3f}, "
                    f"observed {mismatch['observed']:.3f}"
                )
        
        # Analyze unexpected
        if comparison["unexpected"]:
            insights.append(
                f"Experiment revealed {len(comparison['unexpected'])} "
                f"unexpected phenomena not predicted by theory"
            )
        
        return insights
    
    def _suggest_theory_refinements(self,
                                  comparison: Dict[str, Any],
                                  insights: List[str]) -> List[Dict[str, Any]]:
        """Suggest refinements to theoretical model"""
        refinements = []
        
        # Based on mismatches
        for mismatch in comparison["mismatches"]:
            if mismatch["deviation"] > 0.3:
                refinements.append({
                    "type": "parameter_adjustment",
                    "target": mismatch["metric"],
                    "suggestion": f"Adjust model parameters affecting {mismatch['metric']}",
                    "priority": "high" if mismatch["deviation"] > 0.5 else "medium"
                })
        
        # Based on unexpected observations
        if len(comparison["unexpected"]) > 2:
            refinements.append({
                "type": "model_extension",
                "suggestion": "Consider adding components to model unexpected phenomena",
                "new_variables": [u["metric"] for u in comparison["unexpected"]],
                "priority": "medium"
            })
        
        # Based on match rate
        match_rate = len(comparison["matches"]) / (
            len(comparison["matches"]) + len(comparison["mismatches"]) + 1e-10
        )
        
        if match_rate < 0.5:
            refinements.append({
                "type": "model_restructuring",
                "suggestion": "Consider fundamental changes to model structure",
                "priority": "high"
            })
        
        return refinements
    
    def _determine_validation_status(self, comparison: Dict[str, Any]) -> str:
        """Determine overall validation status"""
        match_rate = len(comparison["matches"]) / (
            len(comparison["matches"]) + len(comparison["mismatches"]) + 1e-10
        )
        
        if match_rate > 0.8:
            return "validated"
        elif match_rate > 0.5:
            return "partially_validated"
        else:
            return "not_validated"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()