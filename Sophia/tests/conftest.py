"""
Pytest configuration and fixtures for Sophia tests
"""

import asyncio
import pytest
import os
import sys
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, MagicMock

# Add Sophia root to path
sophia_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if sophia_root not in sys.path:
    sys.path.insert(0, sophia_root)

# Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(sophia_root, '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_database():
    """Mock database for testing"""
    from sophia.core.database import DatabaseManager
    
    db = AsyncMock(spec=DatabaseManager)
    db.is_connected.return_value = True
    db.execute_query.return_value = []
    db.insert_metric.return_value = "test_id"
    db.get_metrics.return_value = []
    db.get_experiments.return_value = []
    db.get_recommendations.return_value = []
    
    return db


@pytest.fixture
async def mock_metrics_engine():
    """Mock metrics engine for testing"""
    from sophia.core.metrics_engine import MetricsEngine
    
    engine = AsyncMock(spec=MetricsEngine)
    engine.is_initialized = True
    engine.record_metric.return_value = "test_metric_id"
    engine.query_metrics.return_value = []
    engine.aggregate_metrics.return_value = {"time_series": []}
    engine.get_registered_components.return_value = [
        {"component_id": "test_component", "name": "Test Component"}
    ]
    
    return engine


@pytest.fixture
async def mock_analysis_engine():
    """Mock analysis engine for testing"""
    from sophia.core.analysis_engine import AnalysisEngine
    
    engine = AsyncMock(spec=AnalysisEngine)
    engine.is_initialized = True
    engine.analyze_metric_patterns.return_value = {
        "patterns": {"pattern_strength": 0.7},
        "statistics": {"mean": 10.5, "std_dev": 2.1},
        "anomalies": {"points": []},
        "trends": {"has_trend": False}
    }
    engine.detect_anomalies.return_value = {
        "anomalies": [],
        "anomaly_count": 0
    }
    
    return engine


@pytest.fixture
async def mock_experiment_framework():
    """Mock experiment framework for testing"""
    from sophia.core.experiment_framework import ExperimentFramework
    
    framework = AsyncMock(spec=ExperimentFramework)
    framework.is_initialized = True
    framework.create_experiment.return_value = "test_experiment_id"
    framework.start_experiment.return_value = True
    framework.get_experiment_status.return_value = "running"
    framework.get_experiment_results.return_value = {
        "status": "completed",
        "metrics_summary": {}
    }
    
    return framework


@pytest.fixture
async def mock_ml_engine():
    """Mock ML engine for testing"""
    from sophia.core.ml_engine import MLEngine
    
    engine = AsyncMock(spec=MLEngine)
    engine.is_initialized = True
    engine.predict.return_value = [0.8, 0.2]
    engine.classify_text.return_value = {"positive": 0.7, "negative": 0.3}
    engine.generate_embeddings.return_value = [0.1] * 384
    
    return engine


@pytest.fixture
async def mock_sophia_component(
    mock_metrics_engine,
    mock_analysis_engine,
    mock_experiment_framework,
    mock_ml_engine
):
    """Mock Sophia component with all engines"""
    from sophia.core.sophia_component import SophiaComponent
    
    component = AsyncMock(spec=SophiaComponent)
    component.initialized = True
    component.metrics_engine = mock_metrics_engine
    component.analysis_engine = mock_analysis_engine
    component.experiment_framework = mock_experiment_framework
    component.ml_engine = mock_ml_engine
    component.active_connections = []
    
    return component


@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing"""
    return [
        {
            "metric_id": "test.metric",
            "value": 10.5,
            "timestamp": "2024-01-01T12:00:00Z",
            "source": "test_component",
            "tags": ["test"]
        },
        {
            "metric_id": "test.metric",
            "value": 11.2,
            "timestamp": "2024-01-01T12:01:00Z",
            "source": "test_component",
            "tags": ["test"]
        }
    ]


@pytest.fixture
def sample_experiment_data():
    """Sample experiment data for testing"""
    return {
        "name": "Test Experiment",
        "description": "Test experiment description",
        "experiment_type": "a_b_test",
        "target_components": ["test_component"],
        "hypothesis": "Test hypothesis",
        "metrics": ["test.metric"],
        "parameters": {
            "control_percentage": 50,
            "treatment_percentage": 50
        }
    }


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing"""
    return {
        "patterns": [
            {
                "pattern_type": "clustering",
                "confidence": 0.8,
                "location": {"data_space": "reduced_dimensions"},
                "parameters": {"n_clusters": 3},
                "description": "Data forms 3 distinct clusters"
            }
        ],
        "causal_relationships": [
            {
                "cause": "metric_a",
                "effect": "metric_b",
                "strength": 0.7,
                "lag": 2,
                "confidence": 0.85,
                "mechanism": "linear"
            }
        ],
        "complex_events": [],
        "predictions": {
            "test.metric": {
                "predictions": [12.0, 12.5, 13.0],
                "confidence_intervals": [[11.5, 12.5], [12.0, 13.0], [12.5, 13.5]]
            }
        }
    }