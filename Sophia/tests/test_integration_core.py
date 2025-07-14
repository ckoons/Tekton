"""
Integration tests for Sophia core engines
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta


class TestMetricsEngineIntegration:
    """Integration tests for MetricsEngine"""
    
    @pytest.mark.asyncio
    async def test_metrics_pipeline_flow(self, mock_database):
        """Test complete metrics recording and querying pipeline"""
        from sophia.core.metrics_engine import MetricsEngine
        
        # Create engine with mocked database
        engine = MetricsEngine()
        engine.database = mock_database
        engine.is_initialized = True
        
        # Test metric recording
        metric_id = await engine.record_metric(
            metric_id="test.performance",
            value=95.5,
            source="test_component",
            tags=["performance", "test"]
        )
        
        assert metric_id is not None
        mock_database.insert_metric.assert_called_once()
        
        # Test metric querying
        mock_database.get_metrics.return_value = [
            {
                "id": "metric_1",
                "metric_id": "test.performance",
                "value": 95.5,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "test_component"
            }
        ]
        
        metrics = await engine.query_metrics(
            metric_id="test.performance",
            source="test_component"
        )
        
        assert len(metrics) == 1
        assert metrics[0]["metric_id"] == "test.performance"
        mock_database.get_metrics.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_metrics_aggregation(self, mock_database):
        """Test metrics aggregation functionality"""
        from sophia.core.metrics_engine import MetricsEngine
        
        engine = MetricsEngine()
        engine.database = mock_database
        engine.is_initialized = True
        
        # Mock aggregated data
        mock_database.get_aggregated_metrics.return_value = [
            {
                "start_time": "2024-01-01T12:00:00Z",
                "end_time": "2024-01-01T12:15:00Z",
                "value": 95.0,
                "count": 10
            }
        ]
        
        result = await engine.aggregate_metrics(
            metric_id="test.performance",
            aggregation="avg",
            interval="15m"
        )
        
        assert "time_series" in result
        mock_database.get_aggregated_metrics.assert_called_once()


class TestAnalysisEngineIntegration:
    """Integration tests for AnalysisEngine"""
    
    @pytest.mark.asyncio
    async def test_pattern_analysis_flow(self, mock_metrics_engine):
        """Test complete pattern analysis workflow"""
        from sophia.core.analysis_engine import AnalysisEngine
        
        engine = AnalysisEngine()
        engine.metrics_engine = mock_metrics_engine
        engine.is_initialized = True
        
        # Mock metrics data
        mock_metrics_engine.query_metrics.return_value = [
            {"value": 10.0, "timestamp": "2024-01-01T12:00:00Z"},
            {"value": 11.0, "timestamp": "2024-01-01T12:01:00Z"},
            {"value": 10.5, "timestamp": "2024-01-01T12:02:00Z"}
        ]
        
        mock_metrics_engine.aggregate_metrics.return_value = {
            "time_series": [
                {"start_time": "2024-01-01T12:00:00Z", "value": 10.5}
            ]
        }
        
        # Test pattern analysis
        result = await engine.analyze_metric_patterns(
            metric_id="test.metric",
            time_window="1h"
        )
        
        assert "patterns" in result
        assert "statistics" in result
        assert "anomalies" in result
        assert "trends" in result
        mock_metrics_engine.query_metrics.assert_called()
        mock_metrics_engine.aggregate_metrics.assert_called()
    
    @pytest.mark.asyncio
    async def test_advanced_analytics_integration(self, mock_metrics_engine):
        """Test advanced analytics integration"""
        from sophia.core.analysis_engine import AnalysisEngine
        
        engine = AnalysisEngine()
        engine.metrics_engine = mock_metrics_engine
        engine.is_initialized = True
        
        # Initialize advanced analytics
        await engine.initialize()
        
        # Test pattern detection
        patterns = await engine.detect_multi_dimensional_patterns(
            component_filter="test",
            time_window="1h"
        )
        
        assert isinstance(patterns, list)
        
        # Test causal analysis
        relationships = await engine.analyze_causal_relationships(
            target_metric="test.target",
            candidate_causes=["test.cause1", "test.cause2"],
            time_window="7d"
        )
        
        assert isinstance(relationships, list)


class TestExperimentFrameworkIntegration:
    """Integration tests for ExperimentFramework"""
    
    @pytest.mark.asyncio
    async def test_experiment_lifecycle(self, mock_database, mock_metrics_engine):
        """Test complete experiment lifecycle"""
        from sophia.core.experiment_framework import ExperimentFramework
        
        framework = ExperimentFramework()
        framework.database = mock_database
        framework.metrics_engine = mock_metrics_engine
        framework.is_initialized = True
        
        # Test experiment creation
        experiment_data = {
            "name": "Test Experiment",
            "experiment_type": "a_b_test",
            "target_components": ["test_component"],
            "hypothesis": "Test hypothesis",
            "metrics": ["test.metric"]
        }
        
        mock_database.insert_experiment.return_value = "exp_123"
        
        experiment_id = await framework.create_experiment(experiment_data)
        
        assert experiment_id == "exp_123"
        mock_database.insert_experiment.assert_called_once()
        
        # Test experiment execution
        mock_database.get_experiment.return_value = {
            "id": "exp_123",
            "status": "draft",
            "experiment_type": "a_b_test",
            **experiment_data
        }
        
        success = await framework.start_experiment(experiment_id)
        assert success is True
        
        # Test experiment analysis
        mock_database.get_experiment_metrics.return_value = [
            {"metric_id": "test.metric", "value": 95.0, "group": "control"},
            {"metric_id": "test.metric", "value": 97.0, "group": "treatment"}
        ]
        
        results = await framework.get_experiment_results(experiment_id)
        assert "status" in results
    
    @pytest.mark.asyncio
    async def test_theory_validation_experiments(self, mock_database, sample_experiment_data):
        """Test theory validation experiment types"""
        from sophia.core.experiment_framework import ExperimentFramework, ExperimentType
        
        framework = ExperimentFramework()
        framework.database = mock_database
        framework.is_initialized = True
        
        # Test each theory validation experiment type
        validation_types = [
            ExperimentType.MANIFOLD_VALIDATION,
            ExperimentType.DYNAMICS_VALIDATION,
            ExperimentType.CATASTROPHE_VALIDATION,
            ExperimentType.SCALING_VALIDATION
        ]
        
        for exp_type in validation_types:
            experiment_data = {
                **sample_experiment_data,
                "experiment_type": exp_type,
                "name": f"Theory Validation: {exp_type}"
            }
            
            mock_database.insert_experiment.return_value = f"exp_{exp_type}"
            
            experiment_id = await framework.create_experiment(experiment_data)
            assert experiment_id == f"exp_{exp_type}"


class TestAdvancedAnalyticsIntegration:
    """Integration tests for Advanced Analytics"""
    
    @pytest.mark.asyncio
    async def test_pattern_detection_pipeline(self, mock_metrics_engine):
        """Test pattern detection pipeline"""
        from sophia.core.advanced_analytics import AdvancedAnalytics
        
        analytics = AdvancedAnalytics(
            metrics_engine=mock_metrics_engine
        )
        
        # Mock data for pattern detection
        mock_data = {
            "component_1": [
                {"value": 10.0, "timestamp": "2024-01-01T12:00:00Z", "metric_id": "test.metric"},
                {"value": 11.0, "timestamp": "2024-01-01T12:01:00Z", "metric_id": "test.metric"}
            ]
        }
        
        patterns = await analytics.detect_multi_dimensional_patterns(
            data=mock_data,
            dimensions=["value", "timestamp"],
            time_window=(datetime.utcnow() - timedelta(hours=1), datetime.utcnow())
        )
        
        assert isinstance(patterns, list)
    
    @pytest.mark.asyncio
    async def test_causal_analysis_pipeline(self, mock_metrics_engine):
        """Test causal analysis pipeline"""
        from sophia.core.advanced_analytics import AdvancedAnalytics
        
        analytics = AdvancedAnalytics(
            metrics_engine=mock_metrics_engine
        )
        
        # Mock time series data
        mock_data = {
            "cause_metric": [
                {"metric_id": "cause_metric", "value": 1.0, "timestamp": "2024-01-01T12:00:00Z"},
                {"metric_id": "cause_metric", "value": 2.0, "timestamp": "2024-01-01T12:01:00Z"}
            ],
            "effect_metric": [
                {"metric_id": "effect_metric", "value": 10.0, "timestamp": "2024-01-01T12:00:00Z"},
                {"metric_id": "effect_metric", "value": 20.0, "timestamp": "2024-01-01T12:01:00Z"}
            ]
        }
        
        relationships = await analytics.perform_causal_analysis(
            data=mock_data,
            target_metric="effect_metric",
            candidate_causes=["cause_metric"]
        )
        
        assert isinstance(relationships, list)


class TestGreekChorusCognitionIntegration:
    """Integration tests for Greek Chorus Cognition Tracking"""
    
    @pytest.mark.asyncio
    async def test_workflow_tracking(self, mock_metrics_engine, mock_analysis_engine):
        """Test Greek Chorus workflow tracking"""
        from sophia.core.chorus_cognition import GreekChorusCognitionTracker
        
        tracker = GreekChorusCognitionTracker(
            metrics_engine=mock_metrics_engine,
            analysis_engine=mock_analysis_engine
        )
        
        # Test workflow step tracking
        await tracker.track_chorus_workflow(
            ci_id="ci_1",
            workflow_step={
                "type": "task_review",
                "task_id": "task_123",
                "status": "completed"
            }
        )
        
        # Test problem solving session
        problem = {
            "id": "problem_1",
            "text": "Test problem",
            "difficulty": "medium"
        }
        
        from sophia.core.chorus_cognition import SolutionPhase
        
        await tracker.start_problem_solving(
            problem=problem,
            phase=SolutionPhase.PARALLEL_QUICK
        )
        
        assert "problem_1" in tracker.problem_traces
        assert "problem_1" in tracker.active_problems
        
        # Test solution attempt recording
        await tracker.record_solution_attempt(
            problem_id="problem_1",
            ci_ids=["ci_1", "ci_2"],
            solution="Test solution",
            confidence=0.8
        )
        
        trace = tracker.problem_traces["problem_1"]
        assert trace.initial_solvers == ["ci_1", "ci_2"]
        assert trace.initial_confidence == 0.8
    
    @pytest.mark.asyncio
    async def test_collective_intelligence_analysis(self, mock_metrics_engine):
        """Test collective intelligence analysis"""
        from sophia.core.chorus_cognition import GreekChorusCognitionTracker
        
        tracker = GreekChorusCognitionTracker(
            metrics_engine=mock_metrics_engine
        )
        
        # Add some test data
        tracker.collective_metrics['problem_solving_rate'] = [0.8, 0.85, 0.9]
        tracker.collective_metrics['emergence_indicators'] = [
            {
                'type': 'voting_consensus',
                'consensus': 0.8,
                'timestamp': datetime.utcnow()
            }
        ]
        
        analysis = await tracker.analyze_collective_intelligence()
        
        assert "performance_metrics" in analysis
        assert "emergence_patterns" in analysis
        assert "team_dynamics" in analysis
        assert "cognitive_evolution" in analysis


class TestSophiaComponentIntegration:
    """Integration tests for SophiaComponent"""
    
    @pytest.mark.asyncio
    async def test_component_initialization(self):
        """Test Sophia component initialization"""
        from sophia.core.sophia_component import SophiaComponent
        
        with patch.multiple(
            'sophia.core.sophia_component',
            get_metrics_engine=AsyncMock(),
            get_analysis_engine=AsyncMock(),
            get_experiment_framework=AsyncMock(),
            get_recommendation_system=AsyncMock(),
            get_intelligence_measurement=AsyncMock(),
            get_ml_engine=AsyncMock()
        ):
            component = SophiaComponent()
            
            # Mock the initialization process
            component.metrics_engine = AsyncMock()
            component.analysis_engine = AsyncMock()
            component.experiment_framework = AsyncMock()
            component.recommendation_system = AsyncMock()
            component.intelligence_measurement = AsyncMock()
            component.ml_engine = AsyncMock()
            
            await component._component_specific_init()
            
            assert component.initialized is True
    
    @pytest.mark.asyncio
    async def test_component_status_check(self, mock_sophia_component):
        """Test component status checking"""
        status = mock_sophia_component.get_component_status()
        
        assert "metrics_engine" in status
        assert "analysis_engine" in status
        assert "experiment_framework" in status
        assert status["metrics_engine"] is True