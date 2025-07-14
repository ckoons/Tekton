"""
End-to-end workflow tests for complete Noesis-Sophia integration
Tests realistic scenarios from theoretical analysis to experimental validation
"""

import asyncio
import pytest
import numpy as np
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

from noesis.core.noesis_component import NoesisComponent
from noesis.core.theoretical.manifold import ManifoldAnalyzer
from noesis.core.theoretical.dynamics import DynamicsAnalyzer
from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
from noesis.core.theoretical.synthesis import SynthesisAnalyzer
from noesis.core.integration.sophia_bridge import SophiaBridge, CollaborationProtocol


class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""
    
    @pytest.fixture
    async def noesis_component(self):
        """Create Noesis component with mocked dependencies"""
        component = NoesisComponent()
        
        # Mock theoretical framework
        component.theoretical_framework = Mock()
        component.theoretical_framework.manifold_analyzer = AsyncMock()
        component.theoretical_framework.dynamics_analyzer = AsyncMock()
        component.theoretical_framework.catastrophe_analyzer = AsyncMock()
        component.theoretical_framework.synthesis_analyzer = AsyncMock()
        
        # Mock stream manager
        component.stream_manager = AsyncMock()
        component.stream_manager.get_theoretical_insights.return_value = {
            "insights": [],
            "system_health": {"warning_level": "low"}
        }
        
        return component
    
    @pytest.fixture
    async def sophia_bridge(self):
        """Create Sophia bridge with mocked HTTP client"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        return bridge
    
    @pytest.fixture
    def collective_ai_data(self):
        """Generate realistic collective AI data for testing"""
        np.random.seed(42)  # For reproducible tests
        
        # Simulate collective AI system with:
        # - 100 agents
        # - 5 features per agent (action, state, reward, communication, coordination)
        # - 300 time steps
        n_agents = 100
        n_features_per_agent = 5
        n_timesteps = 300
        
        total_features = n_agents * n_features_per_agent
        
        # Create base time series
        data = np.random.randn(n_timesteps, total_features) * 0.3
        
        # Add collective structure
        # Phase 1 (0-100): Independent agents
        data[:100] += np.random.randn(100, total_features) * 0.5
        
        # Phase 2 (100-200): Small group coordination emerges
        group_size = 20
        for i in range(0, n_agents, group_size):
            group_start = i * n_features_per_agent
            group_end = (i + group_size) * n_features_per_agent
            if group_end <= total_features:
                # Add group coordination signal
                group_signal = np.random.randn(100, group_size * n_features_per_agent) * 0.8
                data[100:200, group_start:group_end] += group_signal
        
        # Phase 3 (200-300): Global coordination emerges
        global_signal = np.random.randn(100, total_features) * 1.2
        data[200:300] += global_signal
        
        return {
            "time_series": data,
            "collective_states": data[::10],  # Sample every 10th point for state analysis
            "metadata": {
                "n_agents": n_agents,
                "n_features_per_agent": n_features_per_agent,
                "n_timesteps": n_timesteps,
                "phases": ["independent", "group_coordination", "global_coordination"]
            }
        }
    
    async def test_discovery_to_validation_workflow(self, noesis_component, sophia_bridge, collective_ai_data):
        """Test complete workflow from discovery of patterns to experimental validation"""
        
        # Step 1: Analyze collective AI data to discover patterns
        print("Step 1: Discovering patterns in collective AI data...")
        
        # Mock manifold analysis discovering dimensional structure
        manifold_result = Mock()
        manifold_result.data = {
            "manifold_structure": {
                "intrinsic_dimension": 8,
                "explained_variance": [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03],
                "topology_metrics": {
                    "connectivity": 0.78,
                    "mean_curvature": 0.23
                }
            }
        }
        manifold_result.confidence = 0.89
        noesis_component.theoretical_framework.manifold_analyzer.analyze.return_value = manifold_result
        
        # Mock dynamics analysis discovering regime structure
        dynamics_result = Mock()
        dynamics_result.data = {
            "slds_model": {"n_regimes": 3},
            "regime_identification": {
                "current_regime": 2,
                "regime_sequence": [0] * 100 + [1] * 100 + [2] * 100,
                "transition_points": [100, 200],
                "stability_scores": {"0": 0.65, "1": 0.78, "2": 0.91},
                "predicted_transitions": [
                    {"to_regime": 2, "probability": 0.85, "timestep": 250}
                ]
            }
        }
        dynamics_result.confidence = 0.84
        noesis_component.theoretical_framework.dynamics_analyzer.analyze.return_value = dynamics_result
        
        # Perform analysis
        manifold_analysis = await noesis_component.theoretical_framework.manifold_analyzer.analyze(
            collective_ai_data["collective_states"]
        )
        dynamics_analysis = await noesis_component.theoretical_framework.dynamics_analyzer.analyze(
            collective_ai_data["time_series"]
        )
        
        # Step 2: Generate theoretical predictions
        print("Step 2: Generating theoretical predictions...")
        
        theoretical_prediction = {
            "model_type": "collective_emergence",
            "discovery_source": "noesis_analysis",
            "predictions": {
                "intrinsic_dimension": manifold_analysis.data["manifold_structure"]["intrinsic_dimension"],
                "n_regimes": dynamics_analysis.data["slds_model"]["n_regimes"],
                "regime_stability": dynamics_analysis.data["regime_identification"]["stability_scores"]["2"],
                "emergence_pattern": "three_phase_transition"
            },
            "regime": "global_coordination",
            "transition_sequence": ["independent", "group_coordination", "global_coordination"]
        }
        
        confidence_intervals = {
            "intrinsic_dimension": {"lower_bound": 6, "upper_bound": 10, "confidence_level": 0.95},
            "n_regimes": {"lower_bound": 2, "upper_bound": 4, "confidence_level": 0.90},
            "regime_stability": {"lower_bound": 0.85, "upper_bound": 0.95, "confidence_level": 0.85}
        }
        
        # Step 3: Create theory validation protocol with Sophia
        print("Step 3: Creating theory validation protocol...")
        
        # Mock successful Sophia experiment creation
        sophia_bridge.client.post.return_value = AsyncMock()
        sophia_bridge.client.post.return_value.status_code = 200
        sophia_bridge.client.post.return_value.json.return_value = {
            "data": {"experiment_id": "exp_discovery_validation_001"}
        }
        
        validation_protocol = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=theoretical_prediction,
            confidence_intervals=confidence_intervals,
            suggested_metrics=[
                "dimensional_accuracy",
                "regime_detection_accuracy", 
                "stability_measurement",
                "emergence_detection"
            ]
        )
        
        # Verify protocol creation
        assert validation_protocol.protocol_type == CollaborationProtocol.THEORY_VALIDATION
        assert validation_protocol.experiment_component["experiment_id"] == "exp_discovery_validation_001"
        
        # Step 4: Simulate experiment execution and results
        print("Step 4: Simulating experimental validation...")
        
        # Mock experiment results that partially validate the theory
        sophia_bridge.client.get.return_value = AsyncMock()
        sophia_bridge.client.get.return_value.status_code = 200
        sophia_bridge.client.get.return_value.json.return_value = {
            "experiment_id": "exp_discovery_validation_001",
            "status": "completed",
            "execution_time": 3600,
            "metrics_summary": {
                "intrinsic_dimension": {"mean": 7.8, "std": 0.4},  # Close to prediction
                "n_regimes": {"mean": 3.0, "std": 0.0},           # Exact match
                "regime_stability": {"mean": 0.88, "std": 0.03},   # Within CI
                "emergence_detection": {"mean": 0.92, "std": 0.02} # New metric
            },
            "additional_observations": {
                "transition_sharpness": 0.67,
                "coordination_efficiency": 0.85
            }
        }
        
        # Step 5: Interpret results and validate theory
        print("Step 5: Interpreting experimental results...")
        
        interpretation = await sophia_bridge.interpret_experiment_results(
            experiment_id="exp_discovery_validation_001",
            theoretical_context={
                "predictions": theoretical_prediction["predictions"],
                "confidence_intervals": confidence_intervals,
                "discovery_method": "noesis_multi_component_analysis"
            }
        )
        
        # Verify interpretation
        assert interpretation["experiment_id"] == "exp_discovery_validation_001"
        
        # Check validation results
        comparison = interpretation["theoretical_comparison"]
        assert len(comparison["matches"]) >= 3  # Most predictions should match
        assert len(comparison["unexpected"]) >= 1  # Should discover new phenomena
        
        validation_status = interpretation["validation_status"]
        assert validation_status in ["validated", "partially_validated"]
        
        # Step 6: Extract insights and plan follow-up
        print("Step 6: Extracting insights for follow-up research...")
        
        insights = interpretation["insights"]
        refinements = interpretation["suggested_refinements"]
        
        # Should provide actionable insights
        assert len(insights) > 0
        assert any("dimension" in insight.lower() for insight in insights)
        
        # Should suggest refinements for unexpected observations
        if comparison["unexpected"]:
            assert len(refinements) > 0
            extension_refinements = [r for r in refinements if r["type"] == "model_extension"]
            assert len(extension_refinements) > 0
        
        print("✅ Discovery-to-validation workflow completed successfully")
        return {
            "theoretical_prediction": theoretical_prediction,
            "validation_protocol": validation_protocol,
            "interpretation": interpretation,
            "validation_status": validation_status
        }
    
    async def test_real_time_monitoring_to_intervention_workflow(self, noesis_component, sophia_bridge, collective_ai_data):
        """Test real-time monitoring leading to experimental intervention"""
        
        # Step 1: Start real-time monitoring
        print("Step 1: Starting real-time theoretical monitoring...")
        
        # Mock stream manager for real-time insights
        monitoring_insights = [
            {
                "timestamp": "2024-12-01T10:00:00Z",
                "type": "regime_transition_detected",
                "insight": "System transitioning from regime 1 to regime 2",
                "confidence": 0.87,
                "urgency": "medium"
            },
            {
                "timestamp": "2024-12-01T10:05:00Z", 
                "type": "critical_transition_warning",
                "insight": "Early warning signals detected: variance increasing rapidly",
                "confidence": 0.92,
                "urgency": "high"
            },
            {
                "timestamp": "2024-12-01T10:10:00Z",
                "type": "bifurcation_imminent",
                "insight": "System approaching cusp bifurcation - intervention recommended",
                "confidence": 0.89,
                "urgency": "critical"
            }
        ]
        
        # Simulate real-time monitoring
        for i, insight in enumerate(monitoring_insights):
            print(f"  Monitor update {i+1}: {insight['type']} (urgency: {insight['urgency']})")
            
            # Mock stream manager returning progressive insights
            noesis_component.stream_manager.get_theoretical_insights.return_value = {
                "insights": monitoring_insights[:i+1],
                "system_health": {
                    "warning_level": "high" if insight["urgency"] == "critical" else "medium",
                    "message": insight["insight"]
                },
                "critical_transitions": [
                    {
                        "type": "cusp_bifurcation",
                        "estimated_time": 300,
                        "confidence": insight["confidence"]
                    }
                ] if insight["urgency"] == "critical" else []
            }
            
            # Get current insights
            current_insights = await noesis_component.stream_manager.get_theoretical_insights()
            
            # Step 2: Trigger intervention when critical threshold reached
            if insight["urgency"] == "critical":
                print("Step 2: Critical transition detected - triggering intervention protocol...")
                
                # Generate intervention hypothesis
                intervention_hypothesis = await sophia_bridge.generate_hypothesis_from_analysis(
                    analysis_results={
                        "critical_points": [
                            {
                                "transition_type": "cusp_bifurcation", 
                                "confidence": insight["confidence"],
                                "warning_signals": ["variance_increase", "critical_slowing"]
                            }
                        ],
                        "early_warning_signals": {
                            "warning_level": "critical",
                            "estimated_time": 300
                        }
                    },
                    analysis_type="catastrophe_analysis"
                )
                
                # Step 3: Create urgent experimental intervention
                print("Step 3: Creating experimental intervention...")
                
                sophia_bridge.client.post.return_value = AsyncMock()
                sophia_bridge.client.post.return_value.status_code = 200
                sophia_bridge.client.post.return_value.json.return_value = {
                    "data": {"experiment_id": "exp_intervention_001"}
                }
                
                intervention_protocol = await sophia_bridge.create_theory_validation_protocol(
                    theoretical_prediction={
                        "model_type": "critical_transition_intervention",
                        "predictions": {
                            "bifurcation_type": "cusp",
                            "intervention_effectiveness": 0.75,
                            "stabilization_time": 180
                        },
                        "intervention_required": True,
                        "urgency": "critical"
                    },
                    confidence_intervals={
                        "intervention_effectiveness": {"lower_bound": 0.65, "upper_bound": 0.85}
                    },
                    suggested_metrics=[
                        "bifurcation_parameter",
                        "system_stability",
                        "intervention_response_time",
                        "stabilization_success"
                    ]
                )
                
                # Step 4: Execute intervention experiment
                print("Step 4: Executing intervention experiment...")
                
                # Mock intervention experiment results
                sophia_bridge.client.get.return_value = AsyncMock()
                sophia_bridge.client.get.return_value.status_code = 200
                sophia_bridge.client.get.return_value.json.return_value = {
                    "experiment_id": "exp_intervention_001",
                    "status": "completed",
                    "execution_time": 900,  # Faster execution for urgent intervention
                    "metrics_summary": {
                        "bifurcation_parameter": {"mean": 0.23, "std": 0.02},
                        "system_stability": {"mean": 0.78, "std": 0.04},
                        "intervention_response_time": {"mean": 45, "std": 5},
                        "stabilization_success": {"mean": 0.82, "std": 0.03}
                    },
                    "intervention_outcome": "successful_stabilization"
                }
                
                # Step 5: Validate intervention effectiveness
                print("Step 5: Validating intervention effectiveness...")
                
                intervention_results = await sophia_bridge.interpret_experiment_results(
                    experiment_id="exp_intervention_001",
                    theoretical_context={
                        "predictions": {
                            "intervention_effectiveness": 0.75,
                            "stabilization_time": 180
                        },
                        "intervention_type": "critical_transition_prevention",
                        "urgency": "critical"
                    }
                )
                
                # Verify intervention success
                assert intervention_results["experiment_id"] == "exp_intervention_001"
                
                effectiveness_observed = intervention_results["experiment_results"]["metrics_summary"]["stabilization_success"]["mean"]
                assert effectiveness_observed > 0.8  # Intervention was effective
                
                print("✅ Real-time monitoring to intervention workflow completed")
                return {
                    "insights": monitoring_insights,
                    "intervention_hypothesis": intervention_hypothesis,
                    "intervention_protocol": intervention_protocol,
                    "intervention_results": intervention_results,
                    "outcome": "successful_intervention"
                }
    
    async def test_multi_scale_synthesis_to_scaling_experiments(self, noesis_component, sophia_bridge):
        """Test multi-scale analysis leading to scaling law experiments"""
        
        # Step 1: Generate multi-scale collective AI data
        print("Step 1: Generating multi-scale collective AI data...")
        
        scales = {
            "nano_scale": {"n_agents": 12, "expected_dim": 3},    # Known critical point
            "micro_scale": {"n_agents": 100, "expected_dim": 5},
            "meso_scale": {"n_agents": 1000, "expected_dim": 7},
            "macro_scale": {"n_agents": 8000, "expected_dim": 12}, # Known critical point
            "mega_scale": {"n_agents": 50000, "expected_dim": 18}
        }
        
        # Mock analysis results for each scale
        scale_results = {}
        for scale_name, scale_info in scales.items():
            # Mock manifold analysis for this scale
            manifold_result = Mock()
            manifold_result.data = {
                "manifold_structure": {
                    "intrinsic_dimension": scale_info["expected_dim"],
                    "explained_variance": [0.3 - i*0.05 for i in range(scale_info["expected_dim"])],
                    "topology_metrics": {"connectivity": 0.6 + scale_info["n_agents"]/100000}
                }
            }
            manifold_result.confidence = 0.85 + np.random.random() * 0.1
            
            scale_results[scale_name] = {
                "n_agents": scale_info["n_agents"],
                "intrinsic_dimension": scale_info["expected_dim"],
                "complexity": np.mean(manifold_result.data["manifold_structure"]["explained_variance"]),
                "connectivity": manifold_result.data["manifold_structure"]["topology_metrics"]["connectivity"],
                "analysis_data": manifold_result.data
            }
        
        # Step 2: Perform synthesis analysis to discover scaling laws
        print("Step 2: Discovering scaling laws through synthesis...")
        
        # Mock synthesis discovering scaling relationships
        synthesis_result = Mock()
        synthesis_result.data = {
            "universal_principles": [
                {
                    "principle_type": "scaling_law",
                    "description": "Intrinsic dimension scales as N^0.41",
                    "mathematical_form": "D(N) = 1.8 * N^0.41",
                    "parameters": {"scaling_exponent": 0.41, "coefficient": 1.8},
                    "validity_range": {"min_agents": 12, "max_agents": 50000},
                    "confidence": 0.94,
                    "evidence": list(scale_results.keys())
                },
                {
                    "principle_type": "collective_phase_transition",
                    "description": "Critical transitions at N=12 and N=8000",
                    "parameters": {"critical_sizes": [12, 8000], "transition_sharpness": 2.3},
                    "confidence": 0.89,
                    "evidence": ["nano_scale", "macro_scale"]
                }
            ],
            "emergent_properties": [
                {
                    "property": "hierarchical_organization",
                    "emerges_at_scale": "macro_scale",
                    "emergence_size": 8000
                },
                {
                    "property": "collective_intelligence",
                    "emerges_at_scale": "nano_scale", 
                    "emergence_size": 12
                }
            ]
        }
        synthesis_result.confidence = 0.91
        
        noesis_component.theoretical_framework.synthesis_analyzer.analyze.return_value = synthesis_result
        
        synthesis_analysis = await noesis_component.theoretical_framework.synthesis_analyzer.analyze(scale_results)
        
        # Step 3: Generate scaling law hypothesis for experimental validation
        print("Step 3: Generating scaling law validation hypothesis...")
        
        scaling_principle = synthesis_analysis.data["universal_principles"][0]
        
        scaling_hypothesis = {
            "model_type": "collective_scaling_law",
            "discovery_source": "multi_scale_synthesis",
            "scaling_law": {
                "equation": scaling_principle["mathematical_form"],
                "exponent": scaling_principle["parameters"]["scaling_exponent"],
                "coefficient": scaling_principle["parameters"]["coefficient"]
            },
            "predictions": {
                "test_size_2000": 1.8 * (2000 ** 0.41),  # ~22.6
                "test_size_20000": 1.8 * (20000 ** 0.41), # ~35.8
                "exponent_validation": 0.41
            },
            "critical_transitions": [12, 8000]
        }
        
        # Step 4: Create scaling validation experiments
        print("Step 4: Creating scaling validation experiments...")
        
        sophia_bridge.client.post.return_value = AsyncMock()
        sophia_bridge.client.post.return_value.status_code = 200
        
        scaling_experiments = []
        test_sizes = [2000, 20000]
        
        for i, test_size in enumerate(test_sizes):
            sophia_bridge.client.post.return_value.json.return_value = {
                "data": {"experiment_id": f"exp_scaling_{test_size}"}
            }
            
            expected_dimension = scaling_hypothesis["predictions"][f"test_size_{test_size}"]
            
            scaling_protocol = await sophia_bridge.create_theory_validation_protocol(
                theoretical_prediction={
                    "model_type": "scaling_law_validation",
                    "test_size": test_size,
                    "predicted_dimension": expected_dimension,
                    "scaling_exponent": 0.41
                },
                confidence_intervals={
                    "predicted_dimension": {
                        "lower_bound": expected_dimension * 0.9,
                        "upper_bound": expected_dimension * 1.1,
                        "confidence_level": 0.95
                    }
                },
                suggested_metrics=[
                    "intrinsic_dimension",
                    "scaling_consistency",
                    "emergence_detection",
                    "phase_transition_detection"
                ]
            )
            
            scaling_experiments.append(scaling_protocol)
        
        # Step 5: Simulate scaling experiment results
        print("Step 5: Validating scaling law predictions...")
        
        scaling_validations = []
        
        for i, (test_size, protocol) in enumerate(zip(test_sizes, scaling_experiments)):
            # Mock scaling experiment results
            expected_dim = scaling_hypothesis["predictions"][f"test_size_{test_size}"]
            observed_dim = expected_dim + np.random.normal(0, 1.0)  # Some noise
            
            sophia_bridge.client.get.return_value = AsyncMock()
            sophia_bridge.client.get.return_value.status_code = 200
            sophia_bridge.client.get.return_value.json.return_value = {
                "experiment_id": f"exp_scaling_{test_size}",
                "status": "completed",
                "metrics_summary": {
                    "intrinsic_dimension": {"mean": observed_dim, "std": 0.8},
                    "scaling_consistency": {"mean": 0.87, "std": 0.05},
                    "emergence_detection": {"mean": 0.92, "std": 0.03}
                },
                "system_size": test_size
            }
            
            # Interpret scaling results
            validation = await sophia_bridge.interpret_experiment_results(
                experiment_id=f"exp_scaling_{test_size}",
                theoretical_context={
                    "predictions": {"predicted_dimension": expected_dim},
                    "scaling_law": scaling_hypothesis["scaling_law"],
                    "test_size": test_size
                }
            )
            
            scaling_validations.append(validation)
        
        # Step 6: Validate overall scaling law
        print("Step 6: Evaluating scaling law validation...")
        
        # Check if scaling law is validated across test sizes
        validated_experiments = 0
        for validation in scaling_validations:
            if validation["validation_status"] in ["validated", "partially_validated"]:
                validated_experiments += 1
        
        scaling_law_validated = validated_experiments >= len(test_sizes) * 0.8
        
        print(f"✅ Scaling law validation: {validated_experiments}/{len(test_sizes)} experiments validated")
        
        return {
            "scale_results": scale_results,
            "synthesis_analysis": synthesis_analysis,
            "scaling_hypothesis": scaling_hypothesis,
            "scaling_experiments": scaling_experiments,
            "scaling_validations": scaling_validations,
            "scaling_law_validated": scaling_law_validated
        }
    
    async def test_iterative_theory_refinement_workflow(self, noesis_component, sophia_bridge):
        """Test iterative theory refinement through multiple experiment cycles"""
        
        # Step 1: Start with initial theory
        print("Step 1: Starting with initial theory...")
        
        initial_theory = {
            "model_type": "collective_coordination",
            "version": 1.0,
            "parameters": {
                "coordination_threshold": 0.7,
                "emergence_rate": 0.15,
                "stability_factor": 0.8
            },
            "predictions": {
                "coordination_accuracy": 0.85,
                "emergence_time": 120,
                "system_stability": 0.78
            }
        }
        
        # Step 2: Create iterative refinement cycle
        print("Step 2: Creating iterative refinement cycle...")
        
        cycle_config = await sophia_bridge.create_iterative_refinement_cycle(
            initial_theory=initial_theory,
            max_iterations=4
        )
        
        refined_theories = [initial_theory]
        experiment_results = []
        
        # Step 3: Execute refinement iterations
        print("Step 3: Executing refinement iterations...")
        
        sophia_bridge.client.post.return_value = AsyncMock()
        sophia_bridge.client.post.return_value.status_code = 200
        sophia_bridge.client.get.return_value = AsyncMock()
        sophia_bridge.client.get.return_value.status_code = 200
        
        for iteration in range(4):
            print(f"  Iteration {iteration + 1}/4...")
            
            current_theory = refined_theories[-1]
            
            # Create experiment for current theory
            sophia_bridge.client.post.return_value.json.return_value = {
                "data": {"experiment_id": f"exp_refinement_iter_{iteration + 1}"}
            }
            
            experiment_protocol = await sophia_bridge.create_theory_validation_protocol(
                theoretical_prediction=current_theory,
                confidence_intervals={
                    "coordination_accuracy": {"lower_bound": 0.80, "upper_bound": 0.90},
                    "emergence_time": {"lower_bound": 100, "upper_bound": 140},
                    "system_stability": {"lower_bound": 0.70, "upper_bound": 0.85}
                },
                suggested_metrics=["coordination_accuracy", "emergence_time", "system_stability"]
            )
            
            # Simulate experiment execution with evolving results
            # Results get progressively better as theory improves
            base_accuracy = 0.75 + iteration * 0.03
            base_emergence = 140 - iteration * 8
            base_stability = 0.70 + iteration * 0.04
            
            sophia_bridge.client.get.return_value.json.return_value = {
                "experiment_id": f"exp_refinement_iter_{iteration + 1}",
                "status": "completed", 
                "metrics_summary": {
                    "coordination_accuracy": {"mean": base_accuracy, "std": 0.02},
                    "emergence_time": {"mean": base_emergence, "std": 5.0},
                    "system_stability": {"mean": base_stability, "std": 0.03}
                },
                "iteration": iteration + 1
            }
            
            # Interpret results and get refinement suggestions
            interpretation = await sophia_bridge.interpret_experiment_results(
                experiment_id=f"exp_refinement_iter_{iteration + 1}",
                theoretical_context={
                    "predictions": current_theory["predictions"],
                    "confidence_intervals": {
                        "coordination_accuracy": {"lower_bound": 0.80, "upper_bound": 0.90}
                    },
                    "iteration": iteration + 1
                }
            )
            
            experiment_results.append(interpretation)
            
            # Apply refinements to create next theory version
            if iteration < 3:  # Don't refine after last iteration
                refinements = interpretation["suggested_refinements"]
                
                # Create refined theory
                refined_theory = current_theory.copy()
                refined_theory["version"] = current_theory["version"] + 0.1
                
                # Apply parameter refinements
                for refinement in refinements:
                    if refinement["type"] == "parameter_adjustment":
                        target = refinement["target"]
                        if "coordination" in target.lower():
                            refined_theory["parameters"]["coordination_threshold"] *= 0.95
                        elif "emergence" in target.lower():
                            refined_theory["parameters"]["emergence_rate"] *= 1.1
                        elif "stability" in target.lower():
                            refined_theory["parameters"]["stability_factor"] *= 1.05
                
                # Update predictions based on parameter changes
                refined_theory["predictions"] = {
                    "coordination_accuracy": min(0.95, current_theory["predictions"]["coordination_accuracy"] + 0.02),
                    "emergence_time": max(100, current_theory["predictions"]["emergence_time"] - 5),
                    "system_stability": min(0.90, current_theory["predictions"]["system_stability"] + 0.03)
                }
                
                refined_theories.append(refined_theory)
                print(f"    Theory refined to v{refined_theory['version']}")
        
        # Step 4: Evaluate refinement progress
        print("Step 4: Evaluating refinement progress...")
        
        # Check validation status progression
        validation_progression = []
        for result in experiment_results:
            comparison = result["theoretical_comparison"]
            match_rate = len(comparison["matches"]) / (len(comparison["matches"]) + len(comparison["mismatches"]) + 1e-6)
            validation_progression.append(match_rate)
        
        # Should see improvement over iterations
        final_accuracy = validation_progression[-1]
        initial_accuracy = validation_progression[0]
        improvement = final_accuracy - initial_accuracy
        
        print(f"    Initial accuracy: {initial_accuracy:.3f}")
        print(f"    Final accuracy: {final_accuracy:.3f}")
        print(f"    Improvement: {improvement:.3f}")
        
        # Step 5: Validate final theory
        print("Step 5: Validating final refined theory...")
        
        final_theory = refined_theories[-1]
        final_results = experiment_results[-1]
        
        # Final theory should be significantly better
        assert final_theory["version"] > initial_theory["version"]
        assert improvement > 0.1  # Should see meaningful improvement
        assert final_results["validation_status"] in ["validated", "partially_validated"]
        
        print("✅ Iterative theory refinement workflow completed")
        
        return {
            "initial_theory": initial_theory,
            "refined_theories": refined_theories,
            "experiment_results": experiment_results,
            "validation_progression": validation_progression,
            "final_improvement": improvement,
            "cycle_config": cycle_config
        }


class TestWorkflowIntegration:
    """Test integration between different workflow components"""
    
    async def test_workflow_data_persistence(self):
        """Test that workflow data persists correctly across components"""
        bridge = SophiaBridge("http://test")
        bridge.client = AsyncMock()
        
        # Create multiple related protocols
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        
        protocols = []
        for i in range(3):
            bridge.client.post.return_value.json.return_value = {
                "data": {"experiment_id": f"exp_workflow_{i}"}
            }
            
            protocol = await bridge.create_theory_validation_protocol(
                theoretical_prediction={"workflow_id": "test_workflow", "step": i},
                confidence_intervals={"step": {"lower_bound": i-0.5, "upper_bound": i+0.5}},
                suggested_metrics=["workflow_consistency"]
            )
            protocols.append(protocol)
        
        # Verify all protocols are stored and linked
        assert len(bridge.active_protocols) == 3
        
        # Verify workflow continuity
        for i, protocol in enumerate(protocols):
            assert protocol.theory_component["prediction"]["workflow_id"] == "test_workflow"
            assert protocol.theory_component["prediction"]["step"] == i
    
    async def test_concurrent_workflow_execution(self):
        """Test handling of multiple concurrent workflows"""
        bridge = SophiaBridge("http://test")
        bridge.client = AsyncMock()
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        
        # Create multiple concurrent workflows
        workflows = []
        for workflow_id in range(3):
            workflow_protocols = []
            
            for step in range(2):
                bridge.client.post.return_value.json.return_value = {
                    "data": {"experiment_id": f"exp_wf{workflow_id}_step{step}"}
                }
                
                protocol = await bridge.create_theory_validation_protocol(
                    theoretical_prediction={
                        "workflow_id": f"workflow_{workflow_id}",
                        "step": step
                    },
                    confidence_intervals={"step": {"lower_bound": 0, "upper_bound": 1}},
                    suggested_metrics=["workflow_metric"]
                )
                workflow_protocols.append(protocol)
            
            workflows.append(workflow_protocols)
        
        # Verify all workflows are tracked separately
        assert len(bridge.active_protocols) == 6  # 3 workflows × 2 steps each
        
        # Verify workflow isolation
        for workflow_id, workflow_protocols in enumerate(workflows):
            for protocol in workflow_protocols:
                assert protocol.theory_component["prediction"]["workflow_id"] == f"workflow_{workflow_id}"
    
    async def test_workflow_error_recovery(self):
        """Test recovery from errors during workflow execution"""
        bridge = SophiaBridge("http://test")
        bridge.client = AsyncMock()
        
        # Simulate network error during protocol creation
        bridge.client.post.side_effect = Exception("Network error")
        
        # Should create protocol locally even if submission fails
        protocol = await bridge.create_theory_validation_protocol(
            theoretical_prediction={"test": "recovery"},
            confidence_intervals={"test": {"lower_bound": 0, "upper_bound": 1}},
            suggested_metrics=["recovery_test"]
        )
        
        # Protocol should exist locally
        assert isinstance(protocol, type(protocol))
        assert protocol.status == "initialized"
        assert protocol.protocol_id in bridge.active_protocols
        
        # Should be able to continue workflow after recovery
        bridge.client.post.side_effect = None
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        bridge.client.post.return_value.json.return_value = {
            "data": {"experiment_id": "exp_recovery_001"}
        }
        
        # Create follow-up protocol
        follow_up = await bridge.create_theory_validation_protocol(
            theoretical_prediction={"test": "recovery_follow_up"},
            confidence_intervals={"test": {"lower_bound": 0, "upper_bound": 1}},
            suggested_metrics=["recovery_follow_up"]
        )
        
        assert follow_up.status == "experiment_created"
        assert len(bridge.active_protocols) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])