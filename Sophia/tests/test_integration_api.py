"""
Integration tests for Sophia API endpoints
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import json


@pytest.fixture
def test_client():
    """Create test client for Sophia API"""
    with patch('sophia.api.app.component') as mock_component:
        mock_component.initialized = True
        mock_component.check_all_engines_initialized.return_value = True
        mock_component.get_capabilities.return_value = ["metrics", "analytics"]
        mock_component.get_metadata.return_value = {"description": "Test"}
        mock_component.get_component_status.return_value = {"status": "healthy"}
        
        from sophia.api.app import app
        yield TestClient(app)


class TestMetricsAPIIntegration:
    """Integration tests for Metrics API"""
    
    def test_record_metric_endpoint(self, test_client):
        """Test metric recording endpoint"""
        metric_data = {
            "metric_id": "test.performance",
            "value": 95.5,
            "source": "test_component",
            "tags": ["performance", "test"]
        }
        
        with patch('sophia.api.endpoints.metrics.get_metrics_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.record_metric.return_value = "metric_123"
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/metrics", json=metric_data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "metric_id" in result["data"]
    
    def test_query_metrics_endpoint(self, test_client):
        """Test metrics querying endpoint"""
        with patch('sophia.api.endpoints.metrics.get_metrics_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.query_metrics.return_value = [
                {
                    "metric_id": "test.performance",
                    "value": 95.5,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ]
            mock_get_engine.return_value = mock_engine
            
            response = test_client.get("/api/v1/metrics?metric_id=test.performance")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert len(result["data"]) == 1
    
    def test_aggregate_metrics_endpoint(self, test_client):
        """Test metrics aggregation endpoint"""
        aggregation_data = {
            "metric_id": "test.performance",
            "aggregation": "avg",
            "interval": "1h",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-01T23:59:59Z"
        }
        
        with patch('sophia.api.endpoints.metrics.get_metrics_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.aggregate_metrics.return_value = {
                "time_series": [
                    {"start_time": "2024-01-01T12:00:00Z", "value": 95.0}
                ]
            }
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/metrics/aggregate", json=aggregation_data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "time_series" in result["data"]


class TestAnalyticsAPIIntegration:
    """Integration tests for Analytics API"""
    
    def test_pattern_detection_endpoint(self, test_client):
        """Test pattern detection endpoint"""
        pattern_request = {
            "component_filter": "test",
            "dimensions": ["value", "timestamp"],
            "time_window": "24h"
        }
        
        with patch('sophia.api.endpoints.analytics.get_analysis_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.detect_multi_dimensional_patterns.return_value = [
                {
                    "pattern_type": "clustering",
                    "confidence": 0.8,
                    "description": "Test pattern"
                }
            ]
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/analytics/patterns/detect", json=pattern_request)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert len(result["patterns"]) == 1
    
    def test_causal_analysis_endpoint(self, test_client):
        """Test causal analysis endpoint"""
        causal_request = {
            "target_metric": "perf.response_time",
            "candidate_causes": ["res.cpu_usage", "res.memory_usage"],
            "time_window": "7d",
            "max_lag": 10
        }
        
        with patch('sophia.api.endpoints.analytics.get_analysis_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.analyze_causal_relationships.return_value = [
                {
                    "cause": "res.cpu_usage",
                    "effect": "perf.response_time",
                    "strength": 0.7,
                    "lag": 2,
                    "confidence": 0.85,
                    "mechanism": "linear"
                }
            ]
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/analytics/causality/analyze", json=causal_request)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert len(result["relationships"]) == 1
    
    def test_complex_events_endpoint(self, test_client):
        """Test complex events detection endpoint"""
        events_request = {
            "event_types": ["cascade_failure", "synchronization_event"],
            "time_window": "24h"
        }
        
        with patch('sophia.api.endpoints.analytics.get_analysis_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.detect_complex_events.return_value = [
                {
                    "event_type": "cascade_failure",
                    "start_time": "2024-01-01T12:00:00Z",
                    "end_time": "2024-01-01T12:05:00Z",
                    "magnitude": 0.8,
                    "components": ["comp1", "comp2"],
                    "metrics": ["metric1"],
                    "cascading_effects": []
                }
            ]
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/analytics/events/detect", json=events_request)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert len(result["events"]) == 1
    
    def test_predictions_endpoint(self, test_client):
        """Test predictions endpoint"""
        prediction_request = {
            "metric_ids": ["perf.response_time", "res.cpu_usage"],
            "prediction_horizon": 24,
            "confidence_level": 0.95
        }
        
        with patch('sophia.api.endpoints.analytics.get_analysis_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.predict_metrics.return_value = {
                "perf.response_time": {
                    "predictions": [100, 105, 110],
                    "confidence_intervals": [[95, 105], [100, 110], [105, 115]]
                }
            }
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/analytics/predict", json=prediction_request)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "perf.response_time" in result["predictions"]
    
    def test_network_analysis_endpoint(self, test_client):
        """Test network analysis endpoint"""
        network_request = {
            "time_window": "24h"
        }
        
        with patch('sophia.api.endpoints.analytics.get_analysis_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_engine.analyze_network_effects.return_value = {
                "centrality": {
                    "degree": {"comp1": 0.8, "comp2": 0.6}
                },
                "clustering": {"comp1": 0.5},
                "paths": {"average_shortest_path": 2.5}
            }
            mock_get_engine.return_value = mock_engine
            
            response = test_client.post("/api/v1/analytics/network/analyze", json=network_request)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "centrality" in result["analysis"]
    
    def test_analytics_capabilities_endpoint(self, test_client):
        """Test analytics capabilities endpoint"""
        response = test_client.get("/api/v1/analytics/capabilities")
        
        assert response.status_code == 200
        result = response.json()
        assert "pattern_detection" in result
        assert "causal_analysis" in result
        assert "complex_events" in result
        assert "predictions" in result
        assert "network_analysis" in result


class TestExperimentsAPIIntegration:
    """Integration tests for Experiments API"""
    
    def test_create_experiment_endpoint(self, test_client):
        """Test experiment creation endpoint"""
        experiment_data = {
            "name": "Test Experiment",
            "description": "Test experiment description",
            "experiment_type": "a_b_test",
            "target_components": ["test_component"],
            "hypothesis": "Test hypothesis",
            "metrics": ["test.metric"]
        }
        
        with patch('sophia.api.endpoints.experiments.get_experiment_framework') as mock_get_framework:
            mock_framework = AsyncMock()
            mock_framework.create_experiment.return_value = "exp_123"
            mock_get_framework.return_value = mock_framework
            
            response = test_client.post("/api/v1/experiments", json=experiment_data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "experiment_id" in result["data"]
    
    def test_start_experiment_endpoint(self, test_client):
        """Test experiment start endpoint"""
        with patch('sophia.api.endpoints.experiments.get_experiment_framework') as mock_get_framework:
            mock_framework = AsyncMock()
            mock_framework.start_experiment.return_value = True
            mock_get_framework.return_value = mock_framework
            
            response = test_client.post("/api/v1/experiments/exp_123/start")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
    
    def test_get_experiment_results_endpoint(self, test_client):
        """Test experiment results endpoint"""
        with patch('sophia.api.endpoints.experiments.get_experiment_framework') as mock_get_framework:
            mock_framework = AsyncMock()
            mock_framework.get_experiment_results.return_value = {
                "status": "completed",
                "metrics_summary": {"test.metric": {"mean": 95.5}}
            }
            mock_get_framework.return_value = mock_framework
            
            response = test_client.get("/api/v1/experiments/exp_123/results")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "metrics_summary" in result["data"]


class TestInfrastructureEndpoints:
    """Integration tests for infrastructure endpoints"""
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert "component" in result
        assert "version" in result
    
    def test_ready_endpoint(self, test_client):
        """Test readiness check endpoint"""
        response = test_client.get("/ready")
        
        assert response.status_code == 200
        result = response.json()
        assert "ready" in result
        assert "component" in result
    
    def test_discovery_endpoint(self, test_client):
        """Test service discovery endpoint"""
        response = test_client.get("/discovery")
        
        assert response.status_code == 200
        result = response.json()
        assert "component" in result
        assert "endpoints" in result
        assert "capabilities" in result


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection and basic messaging"""
        from fastapi.testclient import TestClient
        from sophia.api.app import app
        
        with patch('sophia.api.app.component') as mock_component:
            mock_component.initialized = True
            mock_component.active_connections = []
            
            with patch('sophia.core.realtime_manager.get_websocket_manager') as mock_get_manager:
                mock_manager = AsyncMock()
                mock_manager.connect.return_value = "client_123"
                mock_get_manager.return_value = mock_manager
                
                client = TestClient(app)
                
                with client.websocket_connect("/ws") as websocket:
                    # Test ping message
                    websocket.send_json({"type": "ping"})
                    data = websocket.receive_json()
                    assert data["type"] == "pong"
    
    @pytest.mark.asyncio
    async def test_websocket_subscription(self):
        """Test WebSocket event subscription"""
        from fastapi.testclient import TestClient
        from sophia.api.app import app
        
        with patch('sophia.api.app.component') as mock_component:
            mock_component.initialized = True
            mock_component.active_connections = []
            
            with patch('sophia.core.realtime_manager.get_websocket_manager') as mock_get_manager:
                mock_manager = AsyncMock()
                mock_manager.connect.return_value = "client_123"
                mock_get_manager.return_value = mock_manager
                
                client = TestClient(app)
                
                with client.websocket_connect("/ws") as websocket:
                    # Test subscription
                    websocket.send_json({
                        "type": "subscribe",
                        "event_types": ["pattern_detected", "complex_event"]
                    })
                    data = websocket.receive_json()
                    assert data["type"] == "subscribed"
                    assert data["event_types"] == ["pattern_detected", "complex_event"]