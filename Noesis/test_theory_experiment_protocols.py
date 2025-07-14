"""
Tests for theory-experiment collaboration protocols between Noesis and Sophia
Validates the API endpoints and protocol management
"""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks
from typing import Dict, Any

from noesis.api.sophia_endpoints import router, sophia_bridge
from noesis.api.sophia_endpoints import (
    TheoryValidationRequest, 
    HypothesisGenerationRequest,
    ExperimentInterpretationRequest,
    IterativeRefinementRequest
)
from noesis.core.integration.sophia_bridge import TheoryExperimentProtocol, CollaborationProtocol
from noesis.models.experiment import TheoryDrivenExperiment


class TestSophiaAPIEndpoints:
    """Test Sophia integration API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client for API endpoints"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def sample_theory_validation_request(self):
        """Sample theory validation request"""
        return {
            "theoretical_prediction": {
                "model_type": "collective_manifold",
                "predictions": {
                    "intrinsic_dimension": 6,
                    "stability_score": 0.82,
                    "emergence_threshold": 150
                },
                "regime": "collaborative_intelligence"
            },
            "confidence_intervals": {
                "intrinsic_dimension": {
                    "lower_bound": 5,
                    "upper_bound": 7,
                    "confidence_level": 0.95
                },
                "stability_score": {
                    "lower_bound": 0.75,
                    "upper_bound": 0.90,
                    "confidence_level": 0.90
                }
            },
            "suggested_metrics": [
                "dimensional_accuracy",
                "stability_measure",
                "emergence_detection"
            ],
            "experiment_name": "Collective Intelligence Validation"
        }
    
    @pytest.fixture
    def sample_hypothesis_request(self):
        """Sample hypothesis generation request"""
        return {
            "analysis_results": {
                "manifold_structure": {
                    "intrinsic_dimension": 8,
                    "topology_complexity": 0.67,
                    "curvature_variance": 0.23
                },
                "regime_identification": {
                    "current_regime": 2,
                    "stability": 0.78,
                    "transition_indicators": ["variance_increase"]
                }
            },
            "analysis_type": "multi_component_analysis",
            "context": {
                "system_size": 5000,
                "time_horizon": 300,
                "analysis_confidence": 0.89
            }
        }
    
    @pytest.fixture
    def sample_experiment_interpretation_request(self):
        """Sample experiment interpretation request"""
        return {
            "experiment_id": "exp_validation_12345",
            "theoretical_context": {
                "original_predictions": {
                    "intrinsic_dimension": 6,
                    "stability_score": 0.82
                },
                "confidence_intervals": {
                    "intrinsic_dimension": {"lower_bound": 5, "upper_bound": 7}
                },
                "model_assumptions": ["linear_regime_transitions", "gaussian_noise"]
            }
        }
    
    async def test_validate_theory_endpoint(self, client, sample_theory_validation_request):
        """Test theory validation endpoint"""
        with patch.object(sophia_bridge, 'create_theory_validation_protocol') as mock_create:
            # Mock successful protocol creation
            mock_protocol = Mock()
            mock_protocol.protocol_id = "tep_20241201_123456"
            mock_protocol.to_dict.return_value = {
                "protocol_id": "tep_20241201_123456",
                "protocol_type": "theory_validation",
                "status": "experiment_created"
            }
            mock_protocol.experiment_component = {"experiment_id": "exp_val_001"}
            mock_create.return_value = mock_protocol
            
            response = client.post(
                "/api/sophia/validate-theory",
                json=sample_theory_validation_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert result["status"] == "success"
            assert "protocol" in result
            assert "sophia_experiment_id" in result
            assert "message" in result
            
            # Verify protocol creation was called
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args["theoretical_prediction"] == sample_theory_validation_request["theoretical_prediction"]
            assert call_args["confidence_intervals"] == sample_theory_validation_request["confidence_intervals"]
            assert call_args["suggested_metrics"] == sample_theory_validation_request["suggested_metrics"]
    
    async def test_generate_hypothesis_endpoint(self, client, sample_hypothesis_request):
        """Test hypothesis generation endpoint"""
        with patch.object(sophia_bridge, 'generate_hypothesis_from_analysis') as mock_generate:
            # Mock successful hypothesis generation
            mock_generate.return_value = {
                "hypothesis": "The system operates in an 8-dimensional manifold with regime transitions",
                "experiment_design": {
                    "name": "Multi-dimensional regime analysis",
                    "experiment_type": "multivariate",
                    "metrics": ["dimensionality", "regime_stability", "transition_frequency"]
                },
                "key_predictions": [
                    {
                        "type": "dimensional_structure",
                        "value": 8,
                        "confidence": 0.89
                    }
                ],
                "source_analysis": "multi_component_analysis"
            }
            
            response = client.post(
                "/api/sophia/generate-hypothesis",
                json=sample_hypothesis_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert result["status"] == "success"
            assert "hypothesis" in result
            assert "experiment_design" in result
            assert "key_predictions" in result
            assert "source_analysis" in result
            
            # Verify hypothesis content
            assert "8-dimensional manifold" in result["hypothesis"]
            assert result["experiment_design"]["experiment_type"] == "multivariate"
    
    async def test_interpret_results_endpoint(self, client, sample_experiment_interpretation_request):
        """Test experiment results interpretation endpoint"""
        with patch.object(sophia_bridge, 'interpret_experiment_results') as mock_interpret:
            # Mock successful interpretation
            mock_interpret.return_value = {
                "experiment_id": "exp_validation_12345",
                "interpretation": {
                    "theoretical_validation": "partial",
                    "key_findings": ["dimension_confirmed", "stability_deviation"],
                    "confidence": 0.87
                },
                "validation_status": "partially_validated",
                "insights": [
                    "Intrinsic dimension matches theoretical prediction",
                    "Stability score lower than predicted - suggests model refinement needed"
                ],
                "suggested_refinements": [
                    {
                        "type": "parameter_adjustment",
                        "target": "stability_model",
                        "suggestion": "Incorporate non-linear stability factors"
                    }
                ]
            }
            
            response = client.post(
                "/api/sophia/interpret-results",
                json=sample_experiment_interpretation_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert result["status"] == "success"
            assert "interpretation" in result
            assert "validation_status" in result
            assert "insights" in result
            assert "suggested_refinements" in result
            
            # Verify interpretation content
            assert result["validation_status"] == "partially_validated"
            assert len(result["insights"]) == 2
            assert len(result["suggested_refinements"]) == 1
    
    async def test_iterative_refinement_endpoint(self, client):
        """Test iterative refinement cycle creation endpoint"""
        refinement_request = {
            "initial_theory": {
                "model_type": "regime_dynamics",
                "parameters": {"n_regimes": 3, "stability_threshold": 0.8},
                "predictions": {"regime_transitions": 2, "stability_duration": 150}
            },
            "max_iterations": 3,
            "convergence_criteria": {
                "min_improvement": 0.05,
                "validation_threshold": 0.85
            }
        }
        
        with patch.object(sophia_bridge, 'create_iterative_refinement_cycle') as mock_create:
            # Mock successful cycle creation
            mock_create.return_value = {
                "cycle_id": "cycle_20241201_123456",
                "initial_theory": refinement_request["initial_theory"],
                "max_iterations": 3,
                "current_iteration": 0,
                "status": "initialized",
                "convergence_criteria": refinement_request["convergence_criteria"]
            }
            
            response = client.post(
                "/api/sophia/iterative-refinement",
                json=refinement_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert result["status"] == "success"
            assert "cycle_config" in result
            assert "message" in result
            
            # Verify cycle configuration
            cycle_config = result["cycle_config"]
            assert cycle_config["cycle_id"] == "cycle_20241201_123456"
            assert cycle_config["max_iterations"] == 3
            assert cycle_config["status"] == "initialized"
    
    async def test_get_active_protocols_endpoint(self, client):
        """Test getting active protocols endpoint"""
        # Mock active protocols
        mock_protocol1 = Mock()
        mock_protocol1.to_dict.return_value = {
            "protocol_id": "tep_001",
            "protocol_type": "theory_validation",
            "status": "experiment_running"
        }
        
        mock_protocol2 = Mock()
        mock_protocol2.to_dict.return_value = {
            "protocol_id": "tep_002", 
            "protocol_type": "hypothesis_generation",
            "status": "completed"
        }
        
        sophia_bridge.active_protocols = {
            "tep_001": mock_protocol1,
            "tep_002": mock_protocol2
        }
        
        response = client.get("/api/sophia/protocols")
        
        assert response.status_code == 200
        protocols = response.json()
        
        assert len(protocols) == 2
        protocol_ids = [p["protocol_id"] for p in protocols]
        assert "tep_001" in protocol_ids
        assert "tep_002" in protocol_ids
    
    async def test_get_specific_protocol_endpoint(self, client):
        """Test getting specific protocol endpoint"""
        # Mock specific protocol
        mock_protocol = Mock()
        mock_protocol.to_dict.return_value = {
            "protocol_id": "tep_specific",
            "protocol_type": "theory_validation",
            "theory_component": {"prediction": "test"},
            "experiment_component": {"experiment_id": "exp_123"},
            "status": "experiment_created",
            "created_at": "2024-12-01T12:00:00",
            "updated_at": "2024-12-01T12:30:00"
        }
        
        sophia_bridge.active_protocols = {"tep_specific": mock_protocol}
        
        response = client.get("/api/sophia/protocols/tep_specific")
        
        assert response.status_code == 200
        protocol = response.json()
        
        assert protocol["protocol_id"] == "tep_specific"
        assert protocol["protocol_type"] == "theory_validation"
        assert "theory_component" in protocol
        assert "experiment_component" in protocol
    
    async def test_get_nonexistent_protocol_endpoint(self, client):
        """Test getting nonexistent protocol returns 404"""
        sophia_bridge.active_protocols = {}
        
        response = client.get("/api/sophia/protocols/nonexistent")
        
        assert response.status_code == 404
        error = response.json()
        assert "not found" in error["detail"]
    
    async def test_create_experiment_from_theory_endpoint(self, client):
        """Test creating Sophia experiment directly from theory"""
        theory_experiment = {
            "name": "Direct Theory Test",
            "description": "Test direct theory-to-experiment conversion",
            "experiment_type": "baseline_comparison",
            "target_components": ["collective_system", "individual_agents"],
            "theoretical_basis": {
                "model": "manifold_dynamics",
                "assumptions": ["linear_transitions", "gaussian_noise"]
            },
            "predictions": {
                "accuracy": 0.92,
                "latency": 45,
                "dimensional_stability": 0.88
            },
            "validation_criteria": {
                "accuracy_threshold": 0.90,
                "latency_max": 50,
                "stability_min": 0.85
            },
            "suggested_metrics": ["accuracy", "latency", "dimensional_stability"],
            "parameters": {
                "duration": 300,
                "sample_size": 1000
            }
        }
        
        with patch.object(sophia_bridge, '_submit_experiment_to_sophia') as mock_submit:
            # Mock successful experiment submission
            mock_submit.return_value = "exp_direct_001"
            
            response = client.post(
                "/api/sophia/experiment-from-theory",
                json=theory_experiment
            )
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response
            assert result["status"] == "success"
            assert result["experiment_id"] == "exp_direct_001"
            assert "message" in result
            
            # Verify submission was called with correct parameters
            mock_submit.assert_called_once()
            call_args = mock_submit.call_args[0]
            submitted_experiment = call_args[0]
            
            assert submitted_experiment["name"] == "Direct Theory Test"
            assert submitted_experiment["experiment_type"] == "baseline_comparison"
            assert "theory_driven" in submitted_experiment["tags"]
            assert "noesis_generated" in submitted_experiment["tags"]
    
    async def test_integration_status_endpoint(self, client):
        """Test integration status endpoint"""
        sophia_bridge.sophia_url = "http://test-sophia:8000"
        
        # Mock some active protocols
        mock_protocol1 = Mock()
        mock_protocol1.protocol_type = CollaborationProtocol.THEORY_VALIDATION
        mock_protocol2 = Mock()
        mock_protocol2.protocol_type = CollaborationProtocol.HYPOTHESIS_GENERATION
        
        sophia_bridge.active_protocols = {
            "tep_001": mock_protocol1,
            "tep_002": mock_protocol2
        }
        
        response = client.get("/api/sophia/status")
        
        assert response.status_code == 200
        status = response.json()
        
        # Verify status information
        assert status["status"] == "active"
        assert status["sophia_url"] == "http://test-sophia:8000"
        assert status["active_protocols"] == 2
        assert len(status["protocol_types"]) == 2
        assert CollaborationProtocol.THEORY_VALIDATION in status["protocol_types"]
        assert CollaborationProtocol.HYPOTHESIS_GENERATION in status["protocol_types"]
        
        # Verify capabilities
        expected_capabilities = [
            "theory_validation",
            "hypothesis_generation", 
            "result_interpretation",
            "iterative_refinement"
        ]
        for capability in expected_capabilities:
            assert capability in status["capabilities"]


class TestProtocolLifecycle:
    """Test complete protocol lifecycle management"""
    
    async def test_theory_validation_protocol_lifecycle(self):
        """Test complete theory validation protocol lifecycle"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        
        # Step 1: Create protocol
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        bridge.client.post.return_value.json.return_value = {
            "data": {"experiment_id": "exp_lifecycle_001"}
        }
        
        theoretical_prediction = {
            "model_type": "collective_manifold",
            "predictions": {"intrinsic_dimension": 5, "stability": 0.85}
        }
        confidence_intervals = {
            "intrinsic_dimension": {"lower_bound": 4, "upper_bound": 6}
        }
        
        protocol = await bridge.create_theory_validation_protocol(
            theoretical_prediction=theoretical_prediction,
            confidence_intervals=confidence_intervals,
            suggested_metrics=["accuracy", "dimensionality"]
        )
        
        # Verify protocol creation
        assert protocol.status == "experiment_created"
        assert protocol.experiment_component["experiment_id"] == "exp_lifecycle_001"
        assert protocol.protocol_id in bridge.active_protocols
        
        # Step 2: Simulate experiment execution (happens in Sophia)
        # Protocol status would be updated by background monitoring
        
        # Step 3: Fetch and interpret results
        bridge.client.get.return_value = AsyncMock()
        bridge.client.get.return_value.status_code = 200
        bridge.client.get.return_value.json.return_value = {
            "experiment_id": "exp_lifecycle_001",
            "status": "completed",
            "metrics_summary": {
                "intrinsic_dimension": {"mean": 5.1, "std": 0.2},
                "stability": {"mean": 0.83, "std": 0.03},
                "accuracy": {"mean": 0.94, "std": 0.01}
            }
        }
        
        interpretation = await bridge.interpret_experiment_results(
            experiment_id="exp_lifecycle_001",
            theoretical_context={
                "predictions": theoretical_prediction["predictions"],
                "confidence_intervals": confidence_intervals
            }
        )
        
        # Verify interpretation
        assert interpretation["experiment_id"] == "exp_lifecycle_001"
        assert "theoretical_comparison" in interpretation
        assert "validation_status" in interpretation
        
        # Check that predictions were validated
        comparison = interpretation["theoretical_comparison"]
        assert len(comparison["matches"]) >= 2  # dimension and stability should match
        
        validation_status = interpretation["validation_status"]
        assert validation_status in ["validated", "partially_validated"]
    
    async def test_hypothesis_generation_to_experiment_lifecycle(self):
        """Test hypothesis generation leading to new experiments"""
        bridge = SophiaBridge("http://test-sophia:8000") 
        bridge.client = AsyncMock()
        
        # Step 1: Generate hypothesis from analysis
        analysis_results = {
            "critical_points": [
                {
                    "transition_type": "hopf_bifurcation",
                    "confidence": 0.91,
                    "location": [2.1, -0.8, 1.3]
                }
            ],
            "early_warning_signals": {
                "warning_level": "medium",
                "variance_increasing": True
            }
        }
        
        hypothesis_result = await bridge.generate_hypothesis_from_analysis(
            analysis_results=analysis_results,
            analysis_type="catastrophe_analysis"
        )
        
        # Verify hypothesis generation
        assert "hopf_bifurcation" in hypothesis_result["hypothesis"]
        experiment_design = hypothesis_result["experiment_design"]
        assert experiment_design["experiment_type"] == "before_after"
        
        # Step 2: Create theory validation protocol for the hypothesis
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        bridge.client.post.return_value.json.return_value = {
            "data": {"experiment_id": "exp_hypothesis_001"}
        }
        
        # Convert hypothesis to testable predictions
        hypothesis_predictions = {
            "transition_type": "hopf_bifurcation",
            "transition_confidence": 0.91,
            "warning_present": True
        }
        
        protocol = await bridge.create_theory_validation_protocol(
            theoretical_prediction=hypothesis_predictions,
            confidence_intervals={
                "transition_confidence": {"lower_bound": 0.85, "upper_bound": 0.95}
            },
            suggested_metrics=["bifurcation_parameter", "oscillation_frequency", "warning_signals"]
        )
        
        # Verify hypothesis-to-experiment conversion
        assert protocol.theory_component["prediction"] == hypothesis_predictions
        assert "bifurcation_parameter" in protocol.theory_component["suggested_metrics"]
    
    async def test_iterative_refinement_cycle(self):
        """Test iterative theory-experiment refinement"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        
        # Initial theory
        initial_theory = {
            "model_type": "regime_dynamics",
            "parameters": {"n_regimes": 3, "transition_rate": 0.15},
            "predictions": {"stability": 0.80, "transition_frequency": 0.20}
        }
        
        # Create refinement cycle
        cycle_config = await bridge.create_iterative_refinement_cycle(
            initial_theory=initial_theory,
            max_iterations=3
        )
        
        # Verify cycle initialization
        assert cycle_config["max_iterations"] == 3
        assert cycle_config["current_iteration"] == 0
        assert cycle_config["status"] == "initialized"
        assert "current_experiment" in cycle_config
        
        # Simulate refinement iterations
        refined_theories = []
        
        for iteration in range(3):
            # Mock experiment results that suggest refinements
            bridge.client.get.return_value = AsyncMock()
            bridge.client.get.return_value.status_code = 200
            bridge.client.get.return_value.json.return_value = {
                "metrics_summary": {
                    "stability": {"mean": 0.75 + iteration * 0.02},  # Gradually improving fit
                    "transition_frequency": {"mean": 0.18 + iteration * 0.01}
                }
            }
            
            # Interpret results and get refinement suggestions
            interpretation = await bridge.interpret_experiment_results(
                experiment_id=f"exp_refinement_{iteration}",
                theoretical_context={
                    "predictions": initial_theory["predictions"],
                    "confidence_intervals": {
                        "stability": {"lower_bound": 0.75, "upper_bound": 0.85}
                    }
                }
            )
            
            # Extract refinement suggestions
            refinements = interpretation["suggested_refinements"]
            
            # Apply refinements to create next theory iteration
            if refinements:
                refined_theory = initial_theory.copy()
                for refinement in refinements:
                    if refinement["type"] == "parameter_adjustment":
                        # Simulate parameter adjustment
                        if "transition_rate" in refinement.get("target", ""):
                            refined_theory["parameters"]["transition_rate"] *= 1.1
                
                refined_theories.append(refined_theory)
        
        # Verify refinement progression
        assert len(refined_theories) <= 3
        
        # Check that parameters evolved
        if refined_theories:
            final_theory = refined_theories[-1]
            original_rate = initial_theory["parameters"]["transition_rate"]
            final_rate = final_theory["parameters"]["transition_rate"] 
            assert final_rate != original_rate  # Parameters should have changed


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in theory-experiment protocols"""
    
    async def test_sophia_api_timeout_handling(self):
        """Test handling of Sophia API timeouts"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        
        # Mock timeout exception
        import httpx
        bridge.client.post.side_effect = httpx.TimeoutException("Request timeout")
        
        # Attempt to create protocol
        protocol = await bridge.create_theory_validation_protocol(
            theoretical_prediction={"test": "prediction"},
            confidence_intervals={"test": {"lower_bound": 0, "upper_bound": 1}},
            suggested_metrics=["accuracy"]
        )
        
        # Should create protocol locally even if Sophia submission fails
        assert isinstance(protocol, TheoryExperimentProtocol)
        assert protocol.status == "initialized"  # Not "experiment_created"
    
    async def test_invalid_experiment_id_handling(self):
        """Test handling of invalid experiment IDs"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        
        # Mock 404 response for invalid experiment ID
        bridge.client.get.return_value = AsyncMock()
        bridge.client.get.return_value.status_code = 404
        
        interpretation = await bridge.interpret_experiment_results(
            experiment_id="invalid_exp_id",
            theoretical_context={"predictions": {}}
        )
        
        # Should return error status
        assert interpretation["status"] == "error"
        assert "Could not fetch experiment results" in interpretation["message"]
    
    async def test_malformed_analysis_results_handling(self):
        """Test handling of malformed analysis results"""
        bridge = SophiaBridge("http://test-sophia:8000")
        
        # Test with missing required fields
        malformed_results = {
            "some_field": "some_value"
            # Missing expected fields like 'predictions', 'current_regime', etc.
        }
        
        # Should not crash, should generate generic hypothesis
        result = await bridge.generate_hypothesis_from_analysis(
            analysis_results=malformed_results,
            analysis_type="unknown_analysis"
        )
        
        assert "hypothesis" in result
        assert "experiment_design" in result
        assert result["hypothesis"]  # Should not be empty
        assert result["experiment_design"]["experiment_type"] == "baseline_comparison"  # Default type
    
    async def test_concurrent_protocol_conflicts(self):
        """Test handling of concurrent protocols for the same theory"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        
        # Mock successful responses
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        
        same_prediction = {"model": "test", "prediction": 42}
        same_intervals = {"prediction": {"lower_bound": 40, "upper_bound": 44}}
        
        # Create multiple protocols with same theory concurrently
        tasks = []
        for i in range(3):
            bridge.client.post.return_value.json.return_value = {
                "data": {"experiment_id": f"exp_concurrent_{i}"}
            }
            
            task = bridge.create_theory_validation_protocol(
                theoretical_prediction=same_prediction,
                confidence_intervals=same_intervals,
                suggested_metrics=[f"metric_{i}"]
            )
            tasks.append(task)
        
        protocols = await asyncio.gather(*tasks)
        
        # All protocols should be created successfully
        assert len(protocols) == 3
        assert len(bridge.active_protocols) == 3
        
        # Each should have unique protocol IDs
        protocol_ids = [p.protocol_id for p in protocols]
        assert len(set(protocol_ids)) == 3
    
    async def test_memory_management_with_many_protocols(self):
        """Test memory management with large numbers of protocols"""
        bridge = SophiaBridge("http://test-sophia:8000")
        bridge.client = AsyncMock()
        bridge.client.post.return_value = AsyncMock()
        bridge.client.post.return_value.status_code = 200
        
        # Create many protocols
        protocols = []
        for i in range(100):
            bridge.client.post.return_value.json.return_value = {
                "data": {"experiment_id": f"exp_{i:03d}"}
            }
            
            protocol = await bridge.create_theory_validation_protocol(
                theoretical_prediction={"iteration": i},
                confidence_intervals={"iteration": {"lower_bound": i-1, "upper_bound": i+1}},
                suggested_metrics=["accuracy"]
            )
            protocols.append(protocol)
        
        # Verify all protocols are stored
        assert len(bridge.active_protocols) == 100
        
        # In a real implementation, might want to test protocol cleanup/archiving
        # for completed experiments to manage memory
        completed_protocols = [p for p in protocols if p.status == "experiment_created"]
        assert len(completed_protocols) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])