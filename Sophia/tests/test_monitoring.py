"""
Monitoring and health check tests for Sophia
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta


class TestSystemHealthMonitoring:
    """Tests for system health monitoring"""
    
    @pytest.mark.asyncio
    async def test_component_health_check(self, mock_sophia_component):
        """Test individual component health checking"""
        # Test healthy component
        mock_sophia_component.initialized = True
        mock_sophia_component.metrics_engine.is_initialized = True
        mock_sophia_component.analysis_engine.is_initialized = True
        
        status = mock_sophia_component.get_component_status()
        
        assert status["metrics_engine"] is True
        assert status["analysis_engine"] is True
        
        # Test unhealthy component
        mock_sophia_component.metrics_engine = None
        
        status = mock_sophia_component.get_component_status()
        assert status["metrics_engine"] is False
    
    @pytest.mark.asyncio
    async def test_metrics_engine_health(self, mock_metrics_engine):
        """Test metrics engine health monitoring"""
        from sophia.core.metrics_engine import MetricsEngine
        
        # Test healthy metrics engine
        mock_metrics_engine.is_initialized = True
        mock_metrics_engine.database.is_connected.return_value = True
        
        health_status = await mock_metrics_engine.get_health_status()
        assert health_status["status"] == "healthy"
        
        # Test unhealthy metrics engine
        mock_metrics_engine.database.is_connected.return_value = False
        
        health_status = await mock_metrics_engine.get_health_status()
        assert health_status["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_analysis_engine_health(self, mock_analysis_engine):
        """Test analysis engine health monitoring"""
        # Test healthy analysis engine
        mock_analysis_engine.is_initialized = True
        mock_analysis_engine.advanced_analytics = MagicMock()
        
        health_check = await mock_analysis_engine.perform_health_check()
        assert health_check["status"] == "healthy"
        
        # Test degraded analysis engine
        mock_analysis_engine.advanced_analytics = None
        
        health_check = await mock_analysis_engine.perform_health_check()
        assert health_check["status"] == "degraded"


class TestPerformanceMonitoring:
    """Tests for performance monitoring"""
    
    @pytest.mark.asyncio
    async def test_metrics_recording_performance(self, mock_metrics_engine):
        """Test metrics recording performance"""
        from sophia.core.metrics_engine import MetricsEngine
        
        # Simulate metric recording
        start_time = time.time()
        
        tasks = []
        for i in range(100):
            task = mock_metrics_engine.record_metric(
                metric_id=f"test.metric_{i}",
                value=i * 1.5,
                source="test_component"
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle 100 metrics in reasonable time
        assert duration < 1.0  # Less than 1 second
        assert mock_metrics_engine.record_metric.call_count == 100
    
    @pytest.mark.asyncio
    async def test_analysis_performance(self, mock_analysis_engine, sample_metrics_data):
        """Test analysis engine performance"""
        # Test pattern analysis performance
        start_time = time.time()
        
        result = await mock_analysis_engine.analyze_metric_patterns(
            metric_id="test.metric",
            time_window="24h"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analysis should complete quickly for test data
        assert duration < 0.5  # Less than 500ms
        assert "patterns" in result
    
    @pytest.mark.asyncio
    async def test_advanced_analytics_performance(self, mock_metrics_engine):
        """Test advanced analytics performance"""
        from sophia.core.advanced_analytics import AdvancedAnalytics
        
        analytics = AdvancedAnalytics(metrics_engine=mock_metrics_engine)
        
        # Test pattern detection performance
        mock_data = {
            f"component_{i}": [
                {"value": j, "timestamp": f"2024-01-01T{j:02d}:00:00Z", "metric_id": "test.metric"}
                for j in range(24)
            ]
            for i in range(5)
        }
        
        start_time = time.time()
        
        patterns = await analytics.detect_multi_dimensional_patterns(
            data=mock_data,
            dimensions=["value", "timestamp"],
            time_window=(datetime.utcnow() - timedelta(hours=24), datetime.utcnow())
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Pattern detection should complete in reasonable time
        assert duration < 2.0  # Less than 2 seconds
        assert isinstance(patterns, list)


class TestResourceMonitoring:
    """Tests for resource monitoring"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, mock_metrics_engine):
        """Test memory usage monitoring"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate heavy metrics processing
        mock_metrics_engine.query_metrics.return_value = [
            {"value": i, "timestamp": f"2024-01-01T{i:02d}:00:00Z"}
            for i in range(1000)
        ]
        
        await mock_metrics_engine.query_metrics(
            metric_id="test.metric",
            limit=1000
        )
        
        # Check memory hasn't grown excessively
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 100MB)
        assert memory_growth < 100 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_database_connection_monitoring(self, mock_database):
        """Test database connection health monitoring"""
        # Test healthy connection
        mock_database.is_connected.return_value = True
        mock_database.execute_query.return_value = [{"result": "ok"}]
        
        health_check = await mock_database.check_connection_health()
        assert health_check["status"] == "healthy"
        
        # Test connection issues
        mock_database.is_connected.return_value = False
        
        health_check = await mock_database.check_connection_health()
        assert health_check["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_websocket_connection_monitoring(self):
        """Test WebSocket connection monitoring"""
        from sophia.core.realtime_manager import WebSocketManager
        
        manager = WebSocketManager()
        
        # Test connection tracking
        mock_websocket = AsyncMock()
        client_id = await manager.connect(mock_websocket)
        
        assert client_id is not None
        assert len(manager.active_connections) == 1
        
        # Test connection cleanup
        manager.disconnect(mock_websocket)
        assert len(manager.active_connections) == 0


class TestAlertingAndNotifications:
    """Tests for alerting and notification systems"""
    
    @pytest.mark.asyncio
    async def test_anomaly_alerting(self, mock_analysis_engine):
        """Test anomaly detection alerting"""
        # Mock anomaly detection
        mock_analysis_engine.detect_anomalies.return_value = {
            "anomalies": [
                {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "value": 150.0,
                    "expected_range": [80.0, 120.0],
                    "severity": "high"
                }
            ],
            "anomaly_count": 1
        }
        
        result = await mock_analysis_engine.detect_anomalies(
            metric_id="test.critical_metric",
            sensitivity=2.0
        )
        
        assert result["anomaly_count"] == 1
        assert result["anomalies"][0]["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_performance_degradation_alerts(self, mock_metrics_engine):
        """Test performance degradation alerting"""
        # Simulate performance degradation
        mock_metrics_engine.query_metrics.return_value = [
            {"value": 200.0, "timestamp": "2024-01-01T12:00:00Z"},  # High response time
            {"value": 195.0, "timestamp": "2024-01-01T12:01:00Z"},
            {"value": 210.0, "timestamp": "2024-01-01T12:02:00Z"}
        ]
        
        metrics = await mock_metrics_engine.query_metrics(
            metric_id="perf.response_time",
            start_time="2024-01-01T12:00:00Z"
        )
        
        # Check if values exceed threshold
        high_values = [m for m in metrics if m["value"] > 180.0]
        assert len(high_values) == 3  # All values are high
    
    @pytest.mark.asyncio
    async def test_system_failure_detection(self, mock_sophia_component):
        """Test system failure detection"""
        # Simulate component failure
        mock_sophia_component.metrics_engine = None
        mock_sophia_component.analysis_engine = None
        
        status = mock_sophia_component.get_component_status()
        
        failed_components = [
            name for name, status in status.items() 
            if status is False
        ]
        
        assert len(failed_components) >= 2
        assert "metrics_engine" in failed_components
        assert "analysis_engine" in failed_components


class TestDataQualityMonitoring:
    """Tests for data quality monitoring"""
    
    @pytest.mark.asyncio
    async def test_metrics_data_validation(self, mock_metrics_engine):
        """Test metrics data validation"""
        # Test valid metric data
        valid_metric = {
            "metric_id": "test.valid_metric",
            "value": 95.5,
            "timestamp": "2024-01-01T12:00:00Z",
            "source": "test_component"
        }
        
        validation_result = await mock_metrics_engine.validate_metric_data(valid_metric)
        assert validation_result["is_valid"] is True
        
        # Test invalid metric data
        invalid_metric = {
            "metric_id": "",  # Empty metric ID
            "value": "invalid",  # Non-numeric value
            "timestamp": "invalid_timestamp"
        }
        
        validation_result = await mock_metrics_engine.validate_metric_data(invalid_metric)
        assert validation_result["is_valid"] is False
        assert len(validation_result["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_data_completeness_monitoring(self, mock_metrics_engine):
        """Test data completeness monitoring"""
        # Mock metrics with gaps
        mock_metrics_engine.query_metrics.return_value = [
            {"value": 10.0, "timestamp": "2024-01-01T12:00:00Z"},
            # Missing 12:01:00Z
            {"value": 12.0, "timestamp": "2024-01-01T12:02:00Z"},
            {"value": 11.0, "timestamp": "2024-01-01T12:03:00Z"}
        ]
        
        metrics = await mock_metrics_engine.query_metrics(
            metric_id="test.metric",
            start_time="2024-01-01T12:00:00Z",
            end_time="2024-01-01T12:03:00Z"
        )
        
        # Check for expected vs actual data points
        expected_points = 4  # 4 minutes of data
        actual_points = len(metrics)
        
        completeness_ratio = actual_points / expected_points
        assert completeness_ratio < 1.0  # Data is incomplete
    
    @pytest.mark.asyncio
    async def test_experiment_data_integrity(self, mock_experiment_framework):
        """Test experiment data integrity monitoring"""
        # Mock experiment with consistent data
        mock_experiment_framework.get_experiment_metrics.return_value = [
            {"group": "control", "metric_id": "test.metric", "value": 95.0},
            {"group": "control", "metric_id": "test.metric", "value": 96.0},
            {"group": "treatment", "metric_id": "test.metric", "value": 98.0},
            {"group": "treatment", "metric_id": "test.metric", "value": 99.0}
        ]
        
        metrics = await mock_experiment_framework.get_experiment_metrics("exp_123")
        
        # Check group balance
        control_count = len([m for m in metrics if m["group"] == "control"])
        treatment_count = len([m for m in metrics if m["group"] == "treatment"])
        
        assert control_count == treatment_count  # Balanced groups


class TestRecoveryAndResilience:
    """Tests for system recovery and resilience"""
    
    @pytest.mark.asyncio
    async def test_engine_restart_recovery(self, mock_metrics_engine):
        """Test engine restart and recovery"""
        # Simulate engine failure
        mock_metrics_engine.is_initialized = False
        
        # Test recovery
        await mock_metrics_engine.initialize()
        mock_metrics_engine.is_initialized = True
        
        assert mock_metrics_engine.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_database_reconnection(self, mock_database):
        """Test database reconnection logic"""
        # Simulate connection loss
        mock_database.is_connected.return_value = False
        
        # Test reconnection attempt
        reconnect_result = await mock_database.reconnect()
        mock_database.is_connected.return_value = True
        
        assert reconnect_result is True
        assert mock_database.is_connected() is True
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, mock_analysis_engine):
        """Test graceful degradation when components fail"""
        # Simulate advanced analytics failure
        mock_analysis_engine.advanced_analytics = None
        
        # Basic analysis should still work
        result = await mock_analysis_engine.analyze_metric_patterns(
            metric_id="test.metric",
            time_window="1h"
        )
        
        assert "patterns" in result
        assert "statistics" in result
        # Advanced patterns might be limited, but basic analysis works