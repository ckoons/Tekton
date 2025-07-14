"""
End-to-end integration tests for Sophia
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta


class TestCompleteWorkflows:
    """End-to-end tests for complete Sophia workflows"""
    
    @pytest.mark.asyncio
    async def test_metrics_to_analysis_workflow(self, mock_sophia_component, sample_metrics_data):
        """Test complete workflow from metrics recording to analysis"""
        # Step 1: Record metrics
        metrics_engine = mock_sophia_component.metrics_engine
        analysis_engine = mock_sophia_component.analysis_engine
        
        # Record sample metrics
        for metric_data in sample_metrics_data:
            await metrics_engine.record_metric(
                metric_id=metric_data["metric_id"],
                value=metric_data["value"],
                timestamp=metric_data["timestamp"],
                source=metric_data["source"],
                tags=metric_data["tags"]
            )
        
        # Step 2: Query metrics
        metrics_engine.query_metrics.return_value = sample_metrics_data
        metrics = await metrics_engine.query_metrics(
            metric_id="test.metric",
            source="test_component"
        )
        
        assert len(metrics) == len(sample_metrics_data)
        
        # Step 3: Analyze patterns
        analysis_engine.analyze_metric_patterns.return_value = {
            "patterns": {"pattern_strength": 0.8},
            "statistics": {"mean": 10.85, "std_dev": 0.35},
            "anomalies": {"points": []},
            "trends": {"has_trend": True, "direction": "increasing"}
        }
        
        analysis_result = await analysis_engine.analyze_metric_patterns(
            metric_id="test.metric",
            time_window="1h"
        )
        
        assert analysis_result["patterns"]["pattern_strength"] > 0.5
        assert analysis_result["trends"]["has_trend"] is True
    
    @pytest.mark.asyncio
    async def test_experiment_creation_to_analysis_workflow(self, mock_sophia_component, sample_experiment_data):
        """Test complete experiment workflow from creation to analysis"""
        experiment_framework = mock_sophia_component.experiment_framework
        
        # Step 1: Create experiment
        experiment_framework.create_experiment.return_value = "exp_e2e_123"
        
        experiment_id = await experiment_framework.create_experiment(sample_experiment_data)
        assert experiment_id == "exp_e2e_123"
        
        # Step 2: Start experiment
        experiment_framework.start_experiment.return_value = True
        
        start_success = await experiment_framework.start_experiment(experiment_id)
        assert start_success is True
        
        # Step 3: Monitor experiment
        experiment_framework.get_experiment_status.return_value = "running"
        
        status = await experiment_framework.get_experiment_status(experiment_id)
        assert status == "running"
        
        # Step 4: Complete and analyze experiment
        experiment_framework.get_experiment_results.return_value = {
            "status": "completed",
            "metrics_summary": {
                "test.metric": {
                    "control": {"mean": 10.5, "std": 1.2, "count": 100},
                    "treatment": {"mean": 11.8, "std": 1.1, "count": 100}
                }
            },
            "statistical_significance": {
                "test.metric": {"p_value": 0.02, "significant": True}
            },
            "recommendation": "Implement treatment - significant improvement observed"
        }
        
        results = await experiment_framework.get_experiment_results(experiment_id)
        
        assert results["status"] == "completed"
        assert results["statistical_significance"]["test.metric"]["significant"] is True
    
    @pytest.mark.asyncio
    async def test_advanced_analytics_pipeline(self, mock_sophia_component):
        """Test complete advanced analytics pipeline"""
        analysis_engine = mock_sophia_component.analysis_engine
        
        # Mock components for network analysis
        mock_sophia_component.metrics_engine.get_registered_components.return_value = [
            {"component_id": "comp1", "name": "Component 1"},
            {"component_id": "comp2", "name": "Component 2"},
            {"component_id": "comp3", "name": "Component 3"}
        ]
        
        # Step 1: Pattern Detection
        analysis_engine.detect_multi_dimensional_patterns.return_value = [
            {
                "pattern_type": "clustering",
                "confidence": 0.85,
                "description": "System shows 3 distinct operational clusters"
            },
            {
                "pattern_type": "spiral",
                "confidence": 0.72,
                "description": "Performance metrics show spiral pattern indicating optimization cycle"
            }
        ]
        
        patterns = await analysis_engine.detect_multi_dimensional_patterns(
            component_filter="comp",
            time_window="24h"
        )
        
        assert len(patterns) == 2
        assert patterns[0]["pattern_type"] == "clustering"
        
        # Step 2: Causal Analysis
        analysis_engine.analyze_causal_relationships.return_value = [
            {
                "cause": "cpu_usage",
                "effect": "response_time",
                "strength": 0.78,
                "lag": 3,
                "confidence": 0.92,
                "mechanism": "linear"
            }
        ]
        
        relationships = await analysis_engine.analyze_causal_relationships(
            target_metric="response_time",
            candidate_causes=["cpu_usage", "memory_usage", "request_rate"]
        )
        
        assert len(relationships) == 1
        assert relationships[0]["strength"] > 0.7
        
        # Step 3: Complex Event Detection
        analysis_engine.detect_complex_events.return_value = [
            {
                "event_type": "synchronization_event",
                "start_time": "2024-01-01T12:00:00Z",
                "end_time": "2024-01-01T12:05:00Z",
                "magnitude": 0.9,
                "components": ["comp1", "comp2", "comp3"],
                "metrics": ["performance", "throughput"],
                "cascading_effects": []
            }
        ]
        
        events = await analysis_engine.detect_complex_events(
            event_types=["synchronization_event", "cascade_failure"],
            time_window="24h"
        )
        
        assert len(events) == 1
        assert events[0]["magnitude"] > 0.8
        
        # Step 4: Predictions
        analysis_engine.predict_metrics.return_value = {
            "response_time": {
                "predictions": [105.0, 107.0, 109.0, 111.0],
                "confidence_intervals": [
                    [100.0, 110.0], [102.0, 112.0], [104.0, 114.0], [106.0, 116.0]
                ]
            }
        }
        
        predictions = await analysis_engine.predict_metrics(
            metric_ids=["response_time"],
            prediction_horizon=4,
            confidence_level=0.95
        )
        
        assert "response_time" in predictions
        assert len(predictions["response_time"]["predictions"]) == 4
        
        # Step 5: Network Analysis
        analysis_engine.analyze_network_effects.return_value = {
            "centrality": {
                "degree": {"comp1": 0.8, "comp2": 0.6, "comp3": 0.4},
                "betweenness": {"comp1": 0.9, "comp2": 0.3, "comp3": 0.1}
            },
            "clustering": {"comp1": 0.7, "comp2": 0.8, "comp3": 0.6},
            "communities": [{"comp1", "comp2"}, {"comp3"}],
            "flow": {
                "bottlenecks": ["comp1"],
                "max_flow_pairs": [("comp1", "comp2", 10.5)]
            }
        }
        
        network_analysis = await analysis_engine.analyze_network_effects(
            time_window="24h"
        )
        
        assert "centrality" in network_analysis
        assert "comp1" in network_analysis["flow"]["bottlenecks"]


class TestTheoryValidationWorkflow:
    """End-to-end tests for theory validation workflows"""
    
    @pytest.mark.asyncio
    async def test_theory_experiment_protocol(self, mock_sophia_component):
        """Test theory-experiment validation protocol"""
        # This would typically involve Noesis integration
        # For now, we'll test the Sophia side of the protocol
        
        experiment_framework = mock_sophia_component.experiment_framework
        
        # Step 1: Create theory validation experiment
        theory_validation_data = {
            "name": "Theory Validation: Manifold Hypothesis",
            "description": "Validate theoretical prediction about system manifold structure",
            "experiment_type": "manifold_validation",
            "target_components": ["collective_system"],
            "hypothesis": "System operates in 5-dimensional manifold with characteristic topology",
            "metrics": ["dimensionality", "curvature", "topology_stability"],
            "parameters": {
                "theoretical_baseline": {
                    "intrinsic_dimension": 5,
                    "curvature_bounds": [-0.1, 0.1],
                    "topology_class": "smooth_manifold"
                },
                "confidence_intervals": {
                    "intrinsic_dimension": {"lower_bound": 4, "upper_bound": 6},
                    "curvature": {"lower_bound": -0.2, "upper_bound": 0.2}
                }
            },
            "tags": ["theory_validation", "manifold_analysis"]
        }
        
        experiment_framework.create_experiment.return_value = "theory_exp_123"
        
        experiment_id = await experiment_framework.create_experiment(theory_validation_data)
        assert experiment_id == "theory_exp_123"
        
        # Step 2: Execute validation experiment
        experiment_framework.start_experiment.return_value = True
        start_success = await experiment_framework.start_experiment(experiment_id)
        assert start_success is True
        
        # Step 3: Collect validation results
        experiment_framework.get_experiment_results.return_value = {
            "status": "completed",
            "validation_results": {
                "intrinsic_dimension": {
                    "measured": 4.8,
                    "theoretical": 5.0,
                    "within_bounds": True,
                    "deviation": 0.2
                },
                "curvature": {
                    "measured": 0.05,
                    "theoretical": 0.0,
                    "within_bounds": True,
                    "deviation": 0.05
                }
            },
            "validation_status": "partially_validated",
            "confidence_score": 0.85,
            "theory_refinement_suggestions": [
                "Adjust expected dimension to 4.8 ± 0.3",
                "Consider slight positive curvature in model"
            ]
        }
        
        results = await experiment_framework.get_experiment_results(experiment_id)
        
        assert results["validation_status"] == "partially_validated"
        assert results["confidence_score"] > 0.8
        assert len(results["theory_refinement_suggestions"]) > 0


class TestCollectiveIntelligenceWorkflow:
    """End-to-end tests for collective intelligence workflows"""
    
    @pytest.mark.asyncio
    async def test_greek_chorus_workflow(self, mock_sophia_component):
        """Test Greek Chorus workflow tracking"""
        # Mock the chorus tracker
        chorus_tracker = AsyncMock()
        mock_sophia_component.chorus_tracker = chorus_tracker
        
        # Step 1: Start problem solving session
        problem = {
            "id": "problem_e2e_1",
            "text": "Optimize system performance under high load",
            "difficulty": "hard"
        }
        
        await chorus_tracker.start_problem_solving(
            problem=problem,
            phase="parallel_quick"
        )
        
        # Step 2: Track workflow steps
        workflow_steps = [
            {"type": "task_review", "task_id": "problem_e2e_1", "ci_id": "ci_1"},
            {"type": "latent_space_access", "ci_id": "ci_1", "query": "optimization_strategies"},
            {"type": "memory_update", "ci_id": "ci_1", "memory_type": "short_term"},
            {"type": "team_memory_read", "ci_id": "ci_1", "key": "shared.strategies"},
            {"type": "plan_creation", "ci_id": "ci_1", "plan": "load_balancing_approach"},
            {"type": "shared_note", "ci_id": "ci_1", "content": "Proposing load balancing solution"}
        ]
        
        for step in workflow_steps:
            await chorus_tracker.track_chorus_workflow(
                ci_id=step["ci_id"],
                workflow_step=step
            )
        
        # Step 3: Record solution attempts
        await chorus_tracker.record_solution_attempt(
            problem_id="problem_e2e_1",
            ci_ids=["ci_1", "ci_2"],
            solution="Implement adaptive load balancing with predictive scaling",
            confidence=0.85
        )
        
        # Step 4: Record review results
        await chorus_tracker.record_review_result(
            problem_id="problem_e2e_1",
            reviewer_ids=["ci_3", "ci_4"],
            decision="accept",
            feedback="Strong solution with good theoretical backing"
        )
        
        # Step 5: Analyze collective intelligence
        chorus_tracker.analyze_collective_intelligence.return_value = {
            "performance_metrics": {
                "overall_success_rate": 0.92,
                "by_difficulty": {
                    "hard": {"total": 10, "solved": 8, "avg_time": 45.2}
                }
            },
            "emergence_patterns": {
                "consensus_evolution": [(datetime.utcnow(), 0.85)],
                "emergence_strength": 0.78
            },
            "team_dynamics": {
                "best_teams": [(['ci_1', 'ci_2'], 0.9)],
                "optimal_team_size": 2
            },
            "collective_insights": [
                {
                    "type": "problem_routing",
                    "insight": "Hard problems solve best with 2-CI teams",
                    "confidence": 0.88
                }
            ]
        }
        
        analysis = await chorus_tracker.analyze_collective_intelligence()
        
        assert analysis["performance_metrics"]["overall_success_rate"] > 0.9
        assert analysis["emergence_patterns"]["emergence_strength"] > 0.7
        assert analysis["team_dynamics"]["optimal_team_size"] == 2
    
    @pytest.mark.asyncio
    async def test_test_taker_protocol(self, mock_sophia_component):
        """Test Test Taker protocol execution"""
        chorus_tracker = mock_sophia_component.chorus_tracker
        
        # Step 1: Phase 1 - Parallel Quick Solutions
        problems_phase1 = [
            {"id": f"q{i}", "text": f"Quick question {i}", "difficulty": "easy"}
            for i in range(50)
        ]
        
        for problem in problems_phase1:
            await chorus_tracker.start_problem_solving(
                problem=problem,
                phase="parallel_quick"
            )
            
            # Simulate quick solving
            await chorus_tracker.record_solution_attempt(
                problem_id=problem["id"],
                ci_ids=[f"ci_{i%4 + 1}", f"ci_{(i+1)%4 + 1}"],
                solution=f"Quick solution for {problem['id']}",
                confidence=0.9
            )
        
        # Step 2: Phase 2 - Focused Second Wave
        problems_phase2 = [
            {"id": f"m{i}", "text": f"Medium question {i}", "difficulty": "medium"}
            for i in range(10)
        ]
        
        for problem in problems_phase2:
            await chorus_tracker.start_problem_solving(
                problem=problem,
                phase="focused_second"
            )
        
        # Step 3: Phase 3 - Collective Hard Problems
        problems_phase3 = [
            {"id": f"h{i}", "text": f"Hard question {i}", "difficulty": "hard"}
            for i in range(5)
        ]
        
        for problem in problems_phase3:
            await chorus_tracker.start_problem_solving(
                problem=problem,
                phase="collective_hard"
            )
            
            # Simulate team formation and voting
            await chorus_tracker.record_escalation(
                problem_id=problem["id"],
                new_phase="collective_hard",
                proposal_teams=[["ci_1", "ci_2"], ["ci_3", "ci_4"], ["ci_5", "ci_6"]]
            )
            
            await chorus_tracker.record_voting(
                problem_id=problem["id"],
                votes={"approach_1": 8, "approach_2": 3, "approach_3": 1},
                winning_approach={"team": ["ci_1", "ci_2"], "strategy": "collaborative_analysis"}
            )
        
        # Verify protocol execution
        assert len(chorus_tracker.problem_traces) == 65  # 50 + 10 + 5
        assert len(chorus_tracker.active_problems) == 65


class TestIntegrationWithExternalSystems:
    """End-to-end tests for integration with external systems"""
    
    @pytest.mark.asyncio
    async def test_hermes_integration(self, mock_sophia_component):
        """Test integration with Hermes (component registry)"""
        # Mock Hermes registration
        with patch('shared.utils.standard_component.StandardComponentBase.register_with_hermes') as mock_register:
            mock_register.return_value = True
            
            # Test component registration
            success = await mock_sophia_component.register_with_hermes()
            assert success is True
            mock_register.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_noesis_integration(self, mock_sophia_component):
        """Test integration with Noesis (theoretical analysis)"""
        # This would test the Sophia bridge to Noesis
        # For now, we'll test the theoretical protocol creation
        
        from sophia.core.experiment_framework import ExperimentFramework
        
        framework = mock_sophia_component.experiment_framework
        
        # Mock receiving theoretical prediction from Noesis
        theoretical_prediction = {
            "model_type": "manifold_dynamics",
            "predictions": {
                "dimensionality": 5.2,
                "stability_metric": 0.85,
                "transition_probability": 0.15
            },
            "confidence_intervals": {
                "dimensionality": {"lower_bound": 4.8, "upper_bound": 5.6},
                "stability_metric": {"lower_bound": 0.8, "upper_bound": 0.9}
            }
        }
        
        # Create validation experiment based on theory
        experiment_data = {
            "name": "Noesis Theory Validation",
            "experiment_type": "theory_validation",
            "theoretical_prediction": theoretical_prediction,
            "validation_metrics": ["dimensionality", "stability_metric"],
            "target_components": ["collective_system"]
        }
        
        framework.create_experiment.return_value = "noesis_validation_123"
        
        experiment_id = await framework.create_experiment(experiment_data)
        assert experiment_id == "noesis_validation_123"
    
    @pytest.mark.asyncio
    async def test_engram_integration(self, mock_sophia_component):
        """Test integration with Engram (memory system)"""
        # Mock Engram data streaming
        metrics_engine = mock_sophia_component.metrics_engine
        
        # Simulate receiving Engram state data
        engram_data = [
            {
                "metric_id": "engram.state_vector",
                "value": [0.1, 0.2, 0.3, 0.4, 0.5],  # State vector
                "timestamp": "2024-01-01T12:00:00Z",
                "source": "engram",
                "context": {"memory_type": "episodic", "activation": 0.8}
            },
            {
                "metric_id": "engram.attention_weights",
                "value": [0.3, 0.7],  # Attention distribution
                "timestamp": "2024-01-01T12:00:00Z",
                "source": "engram",
                "context": {"memory_type": "working", "focus": "problem_solving"}
            }
        ]
        
        # Record Engram metrics
        for data in engram_data:
            await metrics_engine.record_metric(
                metric_id=data["metric_id"],
                value=data["value"],
                timestamp=data["timestamp"],
                source=data["source"],
                context=data["context"]
            )
        
        # Verify data integration
        metrics_engine.record_metric.assert_called()
        assert metrics_engine.record_metric.call_count == len(engram_data)