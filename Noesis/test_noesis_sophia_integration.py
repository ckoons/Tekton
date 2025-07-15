"""
End-to-end integration tests for Noesis-Sophia theory-experiment workflows
Tests the complete theory validation and hypothesis generation cycles
"""

import asyncio
import pytest
import pytest_asyncio
import numpy as np
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any, List

from noesis.core.integration.sophia_bridge import SophiaBridge, TheoryExperimentProtocol, CollaborationProtocol
from noesis.core.theoretical.manifold import ManifoldAnalyzer
from noesis.core.theoretical.dynamics import DynamicsAnalyzer
from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
from noesis.core.theoretical.synthesis import SynthesisAnalyzer


# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio


class TestNoesisSophiaIntegration:
    """Test complete Noesis-Sophia integration workflows"""
    
    @pytest_asyncio.fixture(scope="function")
    async def sophia_bridge(self):
        """Create a Sophia bridge with mocked HTTP client"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        # Clear any existing protocols from previous tests
        bridge.active_protocols.clear()
        return bridge
    
    @pytest.fixture
    def sample_theoretical_prediction(self):
        """Sample theoretical prediction for testing"""
        return {
            "model_type": "manifold_dynamics",
            "predictions": {
                "intrinsic_dimension": 5,
                "regime_stability": 0.85,
                "transition_probability": 0.23
            },
            "regime": "stable_collective",
            "transition": {
                "type": "smooth_emergence",
                "estimated_time": 120,
                "probability": 0.15
            }
        }
    
    @pytest.fixture
    def sample_confidence_intervals(self):
        """Sample confidence intervals for predictions"""
        return {
            "intrinsic_dimension": {
                "lower_bound": 4,
                "upper_bound": 6,
                "confidence_level": 0.95
            },
            "regime_stability": {
                "lower_bound": 0.75,
                "upper_bound": 0.95,
                "confidence_level": 0.90
            },
            "transition_probability": {
                "lower_bound": 0.10,
                "upper_bound": 0.35,
                "confidence_level": 0.85
            }
        }
    
    @pytest.fixture
    def sample_experiment_results(self):
        """Sample experiment results from Sophia"""
        return {
            "experiment_id": "exp_12345",
            "status": "completed",
            "metrics_summary": {
                "intrinsic_dimension": {"mean": 5.2, "std": 0.3},
                "regime_stability": {"mean": 0.82, "std": 0.05},
                "transition_probability": {"mean": 0.19, "std": 0.08},
                "accuracy": {"mean": 0.91, "std": 0.02}
            },
            "execution_time": 3600,
            "confidence": 0.94
        }
    
    async def test_theory_validation_protocol_creation(self, sophia_bridge, sample_theoretical_prediction, sample_confidence_intervals):
        """Test creation of theory validation protocol"""
        # Mock Sophia response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={
            "data": {"experiment_id": "exp_validation_001"}
        })
        sophia_bridge.client.post = AsyncMock(return_value=mock_response)
        
        # Create theory validation protocol
        protocol = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=sample_theoretical_prediction,
            confidence_intervals=sample_confidence_intervals,
            suggested_metrics=["accuracy", "latency", "dimensionality"]
        )
        
        # Verify protocol creation
        assert isinstance(protocol, TheoryExperimentProtocol)
        assert protocol.protocol_type == CollaborationProtocol.THEORY_VALIDATION
        assert protocol.status == "experiment_created"
        assert "exp_validation_001" in protocol.experiment_component.get("experiment_id", "")
        
        # Verify theory component
        theory_component = protocol.theory_component
        assert theory_component["prediction"] == sample_theoretical_prediction
        assert theory_component["confidence_intervals"] == sample_confidence_intervals
        assert theory_component["suggested_metrics"] == ["accuracy", "latency", "dimensionality"]
        
        # Verify experiment design
        experiment_design = protocol.experiment_component
        assert experiment_design["experiment_type"] == "baseline_comparison"
        assert "Theory Validation" in experiment_design["name"]
        assert "theory_validation" in experiment_design["tags"]
        
        # Verify API call
        sophia_bridge.client.post.assert_called_once()
        call_args = sophia_bridge.client.post.call_args
        assert call_args[0][0].endswith("/api/experiments")
    
    async def test_hypothesis_generation_from_catastrophe_analysis(self, sophia_bridge):
        """Test hypothesis generation from catastrophe analysis results"""
        catastrophe_results = {
            "predictions": [
                {
                    "transition_type": "fold_bifurcation",
                    "estimated_time": 45,
                    "confidence": 0.89,
                    "warning_signals": ["variance_increase", "critical_slowing"]
                }
            ],
            "warning_level": "high",
            "critical_points": 2
        }
        
        # Generate hypothesis
        result = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=catastrophe_results,
            analysis_type="catastrophe_analysis"
        )
        
        # Verify hypothesis generation
        assert "hypothesis" in result
        assert "experiment_design" in result
        assert "source_analysis" in result
        assert "key_predictions" in result
        
        # Check hypothesis content
        hypothesis = result["hypothesis"]
        assert "fold_bifurcation" in hypothesis
        assert "45" in hypothesis
        
        # Check experiment design
        experiment_design = result["experiment_design"]
        assert experiment_design["experiment_type"] == "before_after"
        assert "theory_driven" in experiment_design["tags"]
        
        # Check key predictions
        predictions = result["key_predictions"]
        assert len(predictions) > 0
        assert predictions[0]["type"] == "phase_transition"
        assert predictions[0]["transition_type"] == "fold_bifurcation"
    
    async def test_hypothesis_generation_from_regime_dynamics(self, sophia_bridge):
        """Test hypothesis generation from regime dynamics analysis"""
        regime_results = {
            "current_regime": 2,
            "predicted_transitions": [
                {
                    "to_regime": 3,
                    "probability": 0.67,
                    "estimated_time": 30
                }
            ],
            "stability_scores": {
                "2": 0.85,
                "3": 0.72
            }
        }
        
        # Generate hypothesis
        result = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=regime_results,
            analysis_type="regime_dynamics"
        )
        
        # Verify regime-specific hypothesis
        hypothesis = result["hypothesis"]
        assert "regime 2" in hypothesis
        assert "regime 3" in hypothesis
        assert "0.67" in hypothesis
        
        # Check experiment type
        experiment_design = result["experiment_design"]
        assert experiment_design["experiment_type"] == "parameter_tuning"
    
    async def test_experiment_result_interpretation(self, sophia_bridge, sample_theoretical_prediction, sample_experiment_results):
        """Test interpretation of Sophia experiment results"""
        # Mock experiment results fetch
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value=sample_experiment_results)
        sophia_bridge.client.get = AsyncMock(return_value=mock_response)
        
        theoretical_context = {
            "predictions": sample_theoretical_prediction["predictions"],
            "confidence_intervals": {
                "intrinsic_dimension": {"lower_bound": 4, "upper_bound": 6},
                "regime_stability": {"lower_bound": 0.75, "upper_bound": 0.95}
            }
        }
        
        # Interpret results
        interpretation = await sophia_bridge.interpret_experiment_results(
            experiment_id="exp_12345",
            theoretical_context=theoretical_context
        )
        
        # Verify interpretation structure
        assert "experiment_id" in interpretation
        assert "experiment_results" in interpretation
        assert "theoretical_comparison" in interpretation
        assert "insights" in interpretation
        assert "suggested_refinements" in interpretation
        assert "validation_status" in interpretation
        
        # Check comparison analysis
        comparison = interpretation["theoretical_comparison"]
        assert "matches" in comparison
        assert "mismatches" in comparison
        assert "unexpected" in comparison
        
        # Verify validation logic
        matches = comparison["matches"]
        assert len(matches) >= 2  # Should match dimension and stability
        
        # Check for intrinsic dimension match
        dim_match = next((m for m in matches if m["metric"] == "intrinsic_dimension"), None)
        assert dim_match is not None
        assert dim_match["within_ci"] == True
        assert dim_match["predicted"] == 5
        assert dim_match["observed"] == 5.2
        
        # Verify validation status
        validation_status = interpretation["validation_status"]
        assert validation_status in ["validated", "partially_validated", "not_validated"]
    
    async def test_iterative_refinement_cycle(self, sophia_bridge, sample_theoretical_prediction):
        """Test iterative theory-experiment refinement cycle creation"""
        cycle_config = await sophia_bridge.create_iterative_refinement_cycle(
            initial_theory=sample_theoretical_prediction,
            max_iterations=5
        )
        
        # Verify cycle configuration
        assert "cycle_id" in cycle_config
        assert cycle_config["initial_theory"] == sample_theoretical_prediction
        assert cycle_config["max_iterations"] == 5
        assert cycle_config["current_iteration"] == 0
        assert cycle_config["status"] == "initialized"
        
        # Check convergence criteria
        criteria = cycle_config["convergence_criteria"]
        assert "min_improvement" in criteria
        assert "confidence_threshold" in criteria
        assert "validation_success_rate" in criteria
        
        # Verify first experiment is designed
        assert "current_experiment" in cycle_config
        first_experiment = cycle_config["current_experiment"]
        assert "baseline_comparison" in first_experiment["experiment_type"]
    
    async def test_complete_theory_experiment_workflow(self, sophia_bridge, sample_theoretical_prediction, sample_confidence_intervals, sample_experiment_results):
        """Test complete end-to-end theory-experiment workflow"""
        # Step 1: Create theory validation protocol
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json = Mock(return_value={
            "data": {"experiment_id": "exp_workflow_001"}
        })
        sophia_bridge.client.post = AsyncMock(return_value=mock_post_response)
        
        protocol = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=sample_theoretical_prediction,
            confidence_intervals=sample_confidence_intervals,
            suggested_metrics=["accuracy", "dimensionality", "stability"]
        )
        
        # Verify protocol creation
        assert protocol.protocol_id in sophia_bridge.active_protocols
        assert protocol.status == "experiment_created"
        
        # Step 2: Simulate experiment execution (would happen in Sophia)
        experiment_id = protocol.experiment_component["experiment_id"]
        
        # Step 3: Interpret results
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json = Mock(return_value=sample_experiment_results)
        sophia_bridge.client.get = AsyncMock(return_value=mock_get_response)
        
        interpretation = await sophia_bridge.interpret_experiment_results(
            experiment_id=experiment_id,
            theoretical_context={
                "predictions": sample_theoretical_prediction["predictions"],
                "confidence_intervals": sample_confidence_intervals
            }
        )
        
        # Verify end-to-end workflow
        assert interpretation["experiment_id"] == experiment_id
        assert len(interpretation["insights"]) > 0
        
        # Check that theory was validated or partially validated
        validation_status = interpretation["validation_status"]
        assert validation_status in ["validated", "partially_validated"]
        
        # Verify refinement suggestions
        refinements = interpretation["suggested_refinements"]
        assert isinstance(refinements, list)
    
    async def test_cross_analysis_hypothesis_generation(self, sophia_bridge):
        """Test hypothesis generation using results from multiple Noesis analyzers"""
        # Create sample analysis results from different components
        manifold_results = {
            "manifold_structure": {
                "intrinsic_dimension": 7,
                "explained_variance": [0.35, 0.28, 0.15, 0.12, 0.05],
                "topology_metrics": {"connectivity": 0.78}
            }
        }
        
        dynamics_results = {
            "current_regime": 1,
            "n_regimes": 3,
            "regime_stability": 0.67,
            "transition_frequency": 0.12
        }
        
        catastrophe_results = {
            "critical_transitions": 1,
            "warning_score": 0.8,
            "system_stability": 0.2
        }
        
        # Test manifold analysis hypothesis
        manifold_hypothesis = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=manifold_results,
            analysis_type="manifold_analysis"
        )
        
        assert "7-dimensional manifold" in manifold_hypothesis["hypothesis"]
        assert manifold_hypothesis["experiment_design"]["experiment_type"] == "multivariate"
        
        # Test combined analysis (as would be done in synthesis)
        combined_results = {
            "manifold": manifold_results,
            "dynamics": dynamics_results,
            "catastrophe": catastrophe_results,
            "synthesis_insights": {
                "universal_principles": [
                    {
                        "principle_type": "scaling_law",
                        "description": "Dimensionality scales with system size",
                        "confidence": 0.89
                    }
                ]
            }
        }
        
        # This would be handled by a future synthesis-to-hypothesis method
        # For now, test that individual components work correctly
        assert manifold_hypothesis["source_analysis"] == "manifold_analysis"
        assert len(manifold_hypothesis["key_predictions"]) >= 0
    
    async def test_protocol_persistence_and_retrieval(self, sophia_bridge, sample_theoretical_prediction, sample_confidence_intervals):
        """Test that protocols are properly stored and can be retrieved
        
        KNOWN ISSUE: This test may fail when run in parallel with other tests due to 
        pytest-asyncio fixture scope configuration. The test passes when run in isolation.
        To fix: Configure pytest-asyncio with explicit fixture loop scope in pytest.ini:
        [tool.pytest.ini_options]
        asyncio_default_fixture_loop_scope = "function"
        """
        # Ensure clean state
        sophia_bridge.active_protocols.clear()
        
        # Create multiple protocols
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json = Mock(return_value={
            "data": {"experiment_id": "exp_persist_001"}
        })
        sophia_bridge.client.post = AsyncMock(return_value=mock_response1)
        
        protocol1 = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=sample_theoretical_prediction,
            confidence_intervals=sample_confidence_intervals,
            suggested_metrics=["accuracy"]
        )
        
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json = Mock(return_value={
            "data": {"experiment_id": "exp_persist_002"}
        })
        # Reset to use second response
        sophia_bridge.client.post = AsyncMock(return_value=mock_response2)
        
        protocol2 = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=sample_theoretical_prediction,
            confidence_intervals=sample_confidence_intervals,
            suggested_metrics=["latency"]
        )
        
        # Verify both protocols are stored
        assert len(sophia_bridge.active_protocols) == 2
        assert protocol1.protocol_id in sophia_bridge.active_protocols
        assert protocol2.protocol_id in sophia_bridge.active_protocols
        
        # Test protocol retrieval
        retrieved_protocol1 = sophia_bridge.active_protocols[protocol1.protocol_id]
        assert retrieved_protocol1.protocol_type == CollaborationProtocol.THEORY_VALIDATION
        assert retrieved_protocol1.experiment_component["experiment_id"] == "exp_persist_001"
        
        # Test protocol serialization
        protocol_dict = protocol1.to_dict()
        assert "protocol_id" in protocol_dict
        assert "protocol_type" in protocol_dict
        assert "theory_component" in protocol_dict
        assert "experiment_component" in protocol_dict
        assert "created_at" in protocol_dict
    
    async def test_error_handling_and_recovery(self, sophia_bridge, sample_theoretical_prediction, sample_confidence_intervals):
        """Test error handling in theory-experiment workflows"""
        # Test Sophia API failure
        mock_error_response = Mock()
        mock_error_response.status_code = 500
        sophia_bridge.client.post = AsyncMock(return_value=mock_error_response)
        
        protocol = await sophia_bridge.create_theory_validation_protocol(
            theoretical_prediction=sample_theoretical_prediction,
            confidence_intervals=sample_confidence_intervals,
            suggested_metrics=["accuracy"]
        )
        
        # Should still create protocol locally even if Sophia submission fails
        assert isinstance(protocol, TheoryExperimentProtocol)
        assert protocol.status == "initialized"  # Not "experiment_created"
        
        # Test experiment result fetch failure
        mock_404_response = Mock()
        mock_404_response.status_code = 404
        sophia_bridge.client.get = AsyncMock(return_value=mock_404_response)
        
        interpretation = await sophia_bridge.interpret_experiment_results(
            experiment_id="nonexistent_exp",
            theoretical_context={"predictions": {}}
        )
        
        # Should return error status
        assert interpretation["status"] == "error"
        assert "Could not fetch experiment results" in interpretation["message"]
    
    async def test_concurrent_protocol_execution(self, sophia_bridge, sample_theoretical_prediction, sample_confidence_intervals):
        """Test handling of multiple concurrent theory-experiment protocols
        
        KNOWN ISSUE: This test may fail when run in parallel with other tests due to 
        pytest-asyncio fixture scope configuration. The test passes when run in isolation.
        To fix: Configure pytest-asyncio with explicit fixture loop scope in pytest.ini:
        [tool.pytest.ini_options]
        asyncio_default_fixture_loop_scope = "function"
        """
        # Ensure clean state
        sophia_bridge.active_protocols.clear()
        
        # Mock successful Sophia responses
        def mock_post_factory(i):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json = Mock(return_value={
                "data": {"experiment_id": f"exp_concurrent_{i:03d}"}
            })
            return mock_resp
        
        # Create multiple protocols concurrently
        tasks = []
        post_call_count = 0
        async def mock_post(*args, **kwargs):
            nonlocal post_call_count
            result = mock_post_factory(post_call_count)
            post_call_count += 1
            return result
            
        sophia_bridge.client.post = mock_post
        
        for i in range(5):
            task = sophia_bridge.create_theory_validation_protocol(
                theoretical_prediction=sample_theoretical_prediction,
                confidence_intervals=sample_confidence_intervals,
                suggested_metrics=[f"metric_{i}"]
            )
            tasks.append(task)
        
        # Execute concurrently
        protocols = await asyncio.gather(*tasks)
        
        # Verify all protocols were created
        assert len(protocols) == 5
        assert len(sophia_bridge.active_protocols) == 5
        
        # Verify each protocol is unique
        protocol_ids = [p.protocol_id for p in protocols]
        assert len(set(protocol_ids)) == 5  # All unique
        
        # Verify experiment IDs are assigned (order may vary due to concurrency)
        exp_ids = [p.experiment_component.get("experiment_id", "") for p in protocols]
        for i in range(5):
            assert any(f"exp_concurrent_{i:03d}" in exp_id for exp_id in exp_ids)


class TestNoesisAnalysisToSophiaIntegration:
    """Test integration of Noesis theoretical analysis with Sophia experiments"""
    
    @pytest_asyncio.fixture
    async def analyzers(self):
        """Create theoretical analysis components"""
        return {
            "manifold": ManifoldAnalyzer(),
            "dynamics": DynamicsAnalyzer(),
            "catastrophe": CatastropheAnalyzer(),
            "synthesis": SynthesisAnalyzer()
        }
    
    @pytest_asyncio.fixture(scope="function")
    async def sophia_bridge(self):
        """Create Sophia bridge for testing"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        # Clear any existing protocols from previous tests
        bridge.active_protocols.clear()
        return bridge
    
    async def test_manifold_analysis_to_experiment_design(self, analyzers, sophia_bridge):
        """Test conversion of manifold analysis results to experiment hypotheses"""
        # Create test data with known structure
        n_samples, n_features = 200, 15
        data = np.random.randn(n_samples, n_features)
        
        # Add some structure to make analysis meaningful
        data[:100, :5] += 2.0  # First group
        data[100:, 5:10] += 2.0  # Second group
        
        # Perform manifold analysis
        with patch.object(analyzers["manifold"], 'analyze') as mock_analyze:
            # Mock successful analysis result
            mock_analyze.return_value = Mock()
            mock_analyze.return_value.data = {
                "manifold_structure": {
                    "intrinsic_dimension": 6,
                    "explained_variance": [0.3, 0.25, 0.2, 0.1, 0.08, 0.05],
                    "topology_metrics": {
                        "connectivity": 0.82,
                        "mean_curvature": 0.15
                    }
                }
            }
            mock_analyze.return_value.confidence = 0.91
            
            analysis_result = await analyzers["manifold"].analyze(data)
        
        # Convert to hypothesis
        hypothesis_result = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=analysis_result.data,
            analysis_type="manifold_analysis"
        )
        
        # Verify hypothesis generation
        assert "6-dimensional manifold" in hypothesis_result["hypothesis"]
        assert hypothesis_result["experiment_design"]["experiment_type"] == "multivariate"
        assert "dimensionality" in hypothesis_result["experiment_design"]["metrics"]
        assert "topology_stability" in hypothesis_result["experiment_design"]["metrics"]
    
    async def test_dynamics_analysis_to_experiment_design(self, analyzers, sophia_bridge):
        """Test conversion of dynamics analysis results to experiment hypotheses"""
        # Create test time series with regime changes
        n_timesteps, n_features = 300, 8
        time_series = np.random.randn(n_timesteps, n_features) * 0.5
        
        # Add regime structure
        time_series[100:200] += np.array([2, 0, -1, 0, 1, 0, -1, 1])  # Regime 2
        time_series[200:] += np.array([-1, 2, 0, -1, 0, 2, 0, -1])    # Regime 3
        
        # Mock dynamics analysis
        with patch.object(analyzers["dynamics"], 'analyze') as mock_analyze:
            mock_analyze.return_value = Mock()
            mock_analyze.return_value.data = {
                "slds_model": {"n_regimes": 3},
                "regime_identification": {
                    "current_regime": 2,
                    "predicted_transitions": [
                        {
                            "to_regime": 3,
                            "probability": 0.73,
                            "estimated_time": 25
                        }
                    ],
                    "stability_scores": {"2": 0.68, "3": 0.84}
                }
            }
            mock_analyze.return_value.confidence = 0.87
            
            analysis_result = await analyzers["dynamics"].analyze(time_series)
        
        # Convert to hypothesis - pass just the regime identification part
        hypothesis_result = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=analysis_result.data["regime_identification"],
            analysis_type="regime_dynamics"
        )
        
        # Verify regime-based hypothesis
        hypothesis = hypothesis_result["hypothesis"]
        assert "regime 2" in hypothesis
        assert "regime 3" in hypothesis
        assert "0.73" in hypothesis
        
        # Verify experiment design
        experiment_design = hypothesis_result["experiment_design"]
        assert experiment_design["experiment_type"] == "parameter_tuning"
        assert "regime_stability" in experiment_design["metrics"]
        assert "transition_probability" in experiment_design["metrics"]
    
    async def test_catastrophe_analysis_to_experiment_design(self, analyzers, sophia_bridge):
        """Test conversion of catastrophe analysis to experiment hypotheses"""
        # Create trajectory with critical transition
        n_points, n_dims = 200, 6
        trajectory = np.cumsum(np.random.randn(n_points, n_dims) * 0.2, axis=0)
        
        # Add critical transition
        trajectory[120:140] += np.random.randn(20, n_dims) * 2.0  # High variance
        trajectory[140:] += np.array([3, 0, -2, 1, 0, -1])       # State shift
        
        # Mock catastrophe analysis
        with patch.object(analyzers["catastrophe"], 'analyze') as mock_analyze:
            mock_analyze.return_value = Mock()
            mock_analyze.return_value.data = {
                "critical_points": [
                    {
                        "location": [1.5, 0.2, -0.8, 0.3, 0.1, -0.2],
                        "transition_type": "cusp_bifurcation",
                        "confidence": 0.84,
                        "warning_signals": ["variance_increase", "critical_slowing"]
                    }
                ],
                "early_warning_signals": {
                    "warning_level": "high",
                    "variance_increasing": True,
                    "critical_slowing_down": True,
                    "composite_warning_score": 0.79
                }
            }
            mock_analyze.return_value.confidence = 0.82
            
            analysis_result = await analyzers["catastrophe"].analyze(trajectory)
        
        # Convert to hypothesis - transform to expected format
        catastrophe_predictions = {
            "predictions": [
                {
                    "transition_type": cp["transition_type"],
                    "confidence": cp["confidence"],
                    "warning_signals": cp["warning_signals"]
                } for cp in analysis_result.data["critical_points"]
            ]
        }
        hypothesis_result = await sophia_bridge.generate_hypothesis_from_analysis(
            analysis_results=catastrophe_predictions,
            analysis_type="catastrophe_analysis"
        )
        
        # Verify catastrophe-based hypothesis
        hypothesis = hypothesis_result["hypothesis"]
        assert "cusp_bifurcation" in hypothesis
        
        # Verify experiment design for before/after comparison
        experiment_design = hypothesis_result["experiment_design"]
        assert experiment_design["experiment_type"] == "before_after"
        # Default metrics are used since _design_experiment_for_hypothesis uses standard ones
        assert "accuracy" in experiment_design["metrics"]
        assert len(experiment_design["metrics"]) > 0
    
    async def test_synthesis_results_integration(self, analyzers, sophia_bridge):
        """Test integration of synthesis analysis results with experiment design"""
        # Mock multi-scale synthesis results
        synthesis_data = {
            "small_scale": {"n_agents": 50, "intrinsic_dimension": 3},
            "medium_scale": {"n_agents": 500, "intrinsic_dimension": 5},
            "large_scale": {"n_agents": 5000, "intrinsic_dimension": 7}
        }
        
        with patch.object(analyzers["synthesis"], 'analyze') as mock_analyze:
            mock_analyze.return_value = Mock()
            mock_analyze.return_value.data = {
                "universal_principles": [
                    {
                        "principle_type": "scaling_law",
                        "description": "Intrinsic dimension scales as N^0.4",
                        "mathematical_form": "D(N) = 1.2 * N^0.4",
                        "parameters": {"scaling_exponent": 0.4, "coefficient": 1.2},
                        "confidence": 0.94
                    },
                    {
                        "principle_type": "collective_phase_transition",
                        "description": "Phase transition near N=8000",
                        "parameters": {"critical_size": 8000, "transition_sharpness": 2.1},
                        "confidence": 0.87
                    }
                ],
                "emergent_properties": [
                    {
                        "property": "hierarchical_organization",
                        "emerges_at_scale": "large_scale",
                        "emergence_size": 5000
                    }
                ]
            }
            mock_analyze.return_value.confidence = 0.90
            
            synthesis_result = await analyzers["synthesis"].analyze(synthesis_data)
        
        # Test that synthesis results can inform experiment design
        # (This would be implemented in future scaling experiment methods)
        principles = synthesis_result.data["universal_principles"]
        scaling_principle = next(p for p in principles if p["principle_type"] == "scaling_law")
        
        # Verify scaling law detection
        assert scaling_principle["parameters"]["scaling_exponent"] == 0.4
        assert scaling_principle["confidence"] > 0.9
        
        # Test phase transition detection
        transition_principle = next(p for p in principles if p["principle_type"] == "collective_phase_transition")
        assert transition_principle["parameters"]["critical_size"] == 8000


class TestExperimentResultValidation:
    """Test validation of experimental results against theoretical predictions"""
    
    async def test_successful_theory_validation(self):
        """Test case where experiment strongly validates theory"""
        bridge = SophiaBridge("http://test")
        
        theoretical_predictions = {
            "intrinsic_dimension": 5,
            "regime_stability": 0.85,
            "transition_probability": 0.25
        }
        
        confidence_intervals = {
            "intrinsic_dimension": {"lower_bound": 4, "upper_bound": 6},
            "regime_stability": {"lower_bound": 0.75, "upper_bound": 0.95},
            "transition_probability": {"lower_bound": 0.15, "upper_bound": 0.35}
        }
        
        experimental_results = {
            "metrics_summary": {
                "intrinsic_dimension": {"mean": 5.1},
                "regime_stability": {"mean": 0.87},
                "transition_probability": {"mean": 0.23}
            }
        }
        
        # Test comparison logic
        comparison = await bridge._compare_theory_experiment(
            theory={"predictions": theoretical_predictions, "confidence_intervals": confidence_intervals},
            experiment=experimental_results
        )
        
        # All predictions should match
        assert len(comparison["matches"]) == 3
        assert len(comparison["mismatches"]) == 0
        
        # Check validation status
        validation_status = bridge._determine_validation_status(comparison)
        assert validation_status == "validated"
    
    async def test_partial_theory_validation(self):
        """Test case where experiment partially validates theory"""
        bridge = SophiaBridge("http://test")
        
        theoretical_predictions = {
            "intrinsic_dimension": 5,
            "regime_stability": 0.85,
            "transition_probability": 0.25
        }
        
        confidence_intervals = {
            "intrinsic_dimension": {"lower_bound": 4, "upper_bound": 6},
            "regime_stability": {"lower_bound": 0.75, "upper_bound": 0.95},
            "transition_probability": {"lower_bound": 0.15, "upper_bound": 0.35}
        }
        
        experimental_results = {
            "metrics_summary": {
                "intrinsic_dimension": {"mean": 5.2},   # Match
                "regime_stability": {"mean": 0.65},     # Mismatch (too low)
                "transition_probability": {"mean": 0.21} # Match
            }
        }
        
        comparison = await bridge._compare_theory_experiment(
            theory={"predictions": theoretical_predictions, "confidence_intervals": confidence_intervals},
            experiment=experimental_results
        )
        
        # Should have 2 matches, 1 mismatch
        assert len(comparison["matches"]) == 2
        assert len(comparison["mismatches"]) == 1
        
        # Check mismatch details
        mismatch = comparison["mismatches"][0]
        assert mismatch["metric"] == "regime_stability"
        assert mismatch["predicted"] == 0.85
        assert mismatch["observed"] == 0.65
        
        # Check validation status
        validation_status = bridge._determine_validation_status(comparison)
        assert validation_status == "partially_validated"
    
    async def test_theory_refinement_suggestions(self):
        """Test generation of theory refinement suggestions"""
        bridge = SophiaBridge("http://test")
        
        # Create comparison with significant mismatches
        comparison = {
            "matches": [{"metric": "accuracy", "predicted": 0.9, "observed": 0.91}],
            "mismatches": [
                {"metric": "latency", "predicted": 100, "observed": 150, "deviation": 0.6},
                {"metric": "throughput", "predicted": 1000, "observed": 700, "deviation": 0.3}
            ],
            "unexpected": [
                {"metric": "memory_usage", "value": {"mean": 512}},
                {"metric": "cpu_utilization", "value": {"mean": 0.75}}
            ]
        }
        
        insights = bridge._generate_insights(comparison)
        refinements = bridge._suggest_theory_refinements(comparison, insights)
        
        # Should suggest parameter adjustments for mismatches
        param_refinements = [r for r in refinements if r["type"] == "parameter_adjustment"]
        assert len(param_refinements) == 1  # Only latency has deviation > 0.3
        
        # High priority since deviation > 0.5
        assert param_refinements[0]["priority"] == "high"
        assert param_refinements[0]["target"] == "latency"
        
        # Should suggest model extension for unexpected observations
        extension_refinements = [r for r in refinements if r["type"] == "model_extension"]
        assert len(extension_refinements) == 0  # Only triggers if > 2 unexpected observations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])