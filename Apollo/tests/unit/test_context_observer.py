"""
Unit tests for the Context Observer module.
"""

import os
import json
import tempfile
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

import pytest

from apollo.core.context_observer import ContextObserver
from apollo.models.context import (
    ContextMetrics,
    ContextState,
    ContextHealth
)


class TestContextObserver(unittest.TestCase):
    """Test cases for the ContextObserver class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create a mock RhetorInterface
        self.mock_rhetor = AsyncMock()
        
        # Default active sessions response
        self.mock_rhetor.get_active_sessions.return_value = []
        
        # Create context observer
        self.observer = ContextObserver(
            rhetor_interface=self.mock_rhetor,
            data_dir=self.test_dir,
            polling_interval=0.1  # Short interval for testing
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    async def test_start_stop(self):
        """Test starting and stopping the observer."""
        # Start the observer
        await self.observer.start()
        
        # Check that it's running
        assert self.observer.is_running
        assert self.observer.monitoring_task is not None
        
        # Stop the observer
        await self.observer.stop()
        
        # Check that it's stopped
        assert not self.observer.is_running
        assert self.observer.monitoring_task is None or self.observer.monitoring_task.done()
    
    async def test_calculate_health_score(self):
        """Test health score calculation."""
        # Create metrics with good health
        good_metrics = ContextMetrics(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            max_tokens=4000,
            token_utilization=0.375,  # 37.5%
            input_token_rate=10.0,
            output_token_rate=5.0,
            token_rate_change=0.0,
            repetition_score=0.1,  # 10%
            self_reference_score=0.05,  # 5%
            coherence_score=0.95,  # 95%
            latency=0.5,
            processing_time=1.0
        )
        
        # Calculate health score for good metrics
        good_score = self.observer._calculate_health_score(good_metrics)
        good_health = self.observer._determine_health_status(good_score)
        
        # Should be excellent health
        assert good_score > 0.9
        assert good_health == ContextHealth.EXCELLENT
        
        # Create metrics with poor health
        poor_metrics = ContextMetrics(
            input_tokens=3600,
            output_tokens=1800,
            total_tokens=5400,
            max_tokens=6000,
            token_utilization=0.9,  # 90%
            input_token_rate=10.0,
            output_token_rate=5.0,
            token_rate_change=-0.3,  # Decreasing rate
            repetition_score=0.4,  # 40%
            self_reference_score=0.25,  # 25%
            coherence_score=0.6,  # 60%
            latency=2.0,
            processing_time=3.0
        )
        
        # Calculate health score for poor metrics
        poor_score = self.observer._calculate_health_score(poor_metrics)
        poor_health = self.observer._determine_health_status(poor_score)
        
        # Should be poor or critical health
        assert poor_score < 0.6
        assert poor_health in [ContextHealth.POOR, ContextHealth.CRITICAL]
    
    async def test_collect_metrics(self):
        """Test collecting metrics from Rhetor."""
        # Set up mock active sessions
        mock_sessions = [
            {
                "context_id": "test-context-1",
                "component": "test-component",
                "provider": "test-provider",
                "model": "test-model",
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
                "max_tokens": 4000,
                "token_utilization": 0.375,
                "input_token_rate": 10.0,
                "output_token_rate": 5.0,
                "token_rate_change": 0.0,
                "repetition_score": 0.1,
                "self_reference_score": 0.05,
                "coherence_score": 0.95,
                "latency": 0.5,
                "processing_time": 1.0,
                "task_type": "test-task",
                "metadata": {"test": "data"}
            }
        ]
        
        self.mock_rhetor.get_active_sessions.return_value = mock_sessions
        
        # Call _collect_metrics directly
        await self.observer._collect_metrics()
        
        # Should have one active context
        assert len(self.observer.active_contexts) == 1
        assert "test-context-1" in self.observer.active_contexts
        
        # Check context data
        context = self.observer.active_contexts["test-context-1"]
        assert context.context_id == "test-context-1"
        assert context.component_id == "test-component"
        assert context.provider == "test-provider"
        assert context.model == "test-model"
        assert context.metrics.input_tokens == 1000
        assert context.metrics.output_tokens == 500
        assert context.metrics.total_tokens == 1500
        assert context.metrics.token_utilization == 0.375
        
        # Check history
        assert "test-context-1" in self.observer.context_history
        assert len(self.observer.context_history["test-context-1"]) == 1
        
        # Call _collect_metrics again with updated metrics
        mock_sessions[0]["total_tokens"] = 2000
        mock_sessions[0]["token_utilization"] = 0.5
        
        await self.observer._collect_metrics()
        
        # Should still have one active context
        assert len(self.observer.active_contexts) == 1
        
        # Check updated context data
        context = self.observer.active_contexts["test-context-1"]
        assert context.metrics.total_tokens == 2000
        assert context.metrics.token_utilization == 0.5
        
        # Check history (should have two records now)
        assert len(self.observer.context_history["test-context-1"]) == 2
    
    async def test_save_context_history(self):
        """Test saving context history to disk."""
        # Create a context and history
        context_id = "test-context-save"
        
        metrics = ContextMetrics(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            max_tokens=4000,
            token_utilization=0.375,
            input_token_rate=10.0,
            output_token_rate=5.0,
            token_rate_change=0.0,
            repetition_score=0.1,
            self_reference_score=0.05,
            coherence_score=0.95,
            latency=0.5,
            processing_time=1.0
        )
        
        # Create history records
        from apollo.models.context import ContextHistoryRecord
        history_record = ContextHistoryRecord(
            context_id=context_id,
            metrics=metrics,
            health=ContextHealth.EXCELLENT,
            health_score=0.95
        )
        
        # Add to history
        self.observer.context_history[context_id] = [history_record]
        
        # Save history
        await self.observer._save_context_history(context_id)
        
        # Check for file
        files = os.listdir(self.test_dir)
        assert len(files) == 1
        
        # Load file and check contents
        with open(os.path.join(self.test_dir, files[0]), "r") as f:
            data = json.load(f)
            
        assert len(data) == 1
        assert data[0]["context_id"] == context_id
        assert data[0]["health"] == "excellent"
        assert data[0]["health_score"] == 0.95
    
    async def test_callbacks(self):
        """Test callback registration and execution."""
        # Create callback mock
        callback_mock = AsyncMock()
        
        # Register callback
        self.observer.register_callback("on_metrics_update", callback_mock)
        
        # Set up mock active sessions
        mock_sessions = [
            {
                "context_id": "test-context-callback",
                "component": "test-component",
                "provider": "test-provider",
                "model": "test-model",
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
                "max_tokens": 4000,
                "token_utilization": 0.375,
                "input_token_rate": 10.0,
                "output_token_rate": 5.0,
                "token_rate_change": 0.0,
                "repetition_score": 0.1,
                "self_reference_score": 0.05,
                "coherence_score": 0.95,
                "latency": 0.5,
                "processing_time": 1.0,
                "task_type": "test-task",
                "metadata": {"test": "data"}
            }
        ]
        
        self.mock_rhetor.get_active_sessions.return_value = mock_sessions
        
        # First call should trigger on_context_created
        await self.observer._collect_metrics()
        
        # Second call should trigger on_metrics_update
        await self.observer._collect_metrics()
        
        # Check if callback was called
        assert callback_mock.call_count == 1
    
    async def test_suggest_action(self):
        """Test suggesting actions based on context health."""
        # Create context
        context_id = "test-context-action"
        
        # Create critical context
        metrics = ContextMetrics(
            input_tokens=3800,
            output_tokens=1900,
            total_tokens=5700,
            max_tokens=6000,
            token_utilization=0.95,
            input_token_rate=10.0,
            output_token_rate=5.0,
            token_rate_change=0.0,
            repetition_score=0.1,
            self_reference_score=0.05,
            coherence_score=0.95,
            latency=0.5,
            processing_time=1.0
        )
        
        health_score = self.observer._calculate_health_score(metrics)
        health = self.observer._determine_health_status(health_score)
        
        # Should be critical due to high token utilization
        assert health == ContextHealth.CRITICAL
        
        # Create critical context state
        context_state = ContextState(
            context_id=context_id,
            component_id="test-component",
            provider="test-provider",
            model="test-model",
            metrics=metrics,
            health=health,
            health_score=health_score,
            creation_time=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Add to active contexts
        self.observer.active_contexts[context_id] = context_state
        
        # Suggest action
        action = await self.observer.suggest_action(context_id)
        
        # Should suggest reset for critical health
        assert action is not None
        assert action.context_id == context_id
        assert action.action_type == "reset"
        assert action.priority == 10
    
    async def test_context_closed(self):
        """Test handling closed contexts."""
        # Set up mock active sessions
        mock_sessions = [
            {
                "context_id": "test-context-closed",
                "component": "test-component",
                "provider": "test-provider",
                "model": "test-model",
                "input_tokens": 1000,
                "output_tokens": 500,
                "total_tokens": 1500,
                "max_tokens": 4000,
                "token_utilization": 0.375,
                "input_token_rate": 10.0,
                "output_token_rate": 5.0,
                "token_rate_change": 0.0,
                "repetition_score": 0.1,
                "self_reference_score": 0.05,
                "coherence_score": 0.95,
                "latency": 0.5,
                "processing_time": 1.0,
                "task_type": "test-task",
                "metadata": {"test": "data"}
            }
        ]
        
        self.mock_rhetor.get_active_sessions.return_value = mock_sessions
        
        # First call should create the context
        await self.observer._collect_metrics()
        
        # Context should exist
        assert "test-context-closed" in self.observer.active_contexts
        
        # Now return empty sessions (context closed)
        self.mock_rhetor.get_active_sessions.return_value = []
        
        # Create callback mock for on_context_closed
        callback_mock = AsyncMock()
        self.observer.register_callback("on_context_closed", callback_mock)
        
        # Second call should detect closed context
        await self.observer._collect_metrics()
        
        # Context should be removed
        assert "test-context-closed" not in self.observer.active_contexts
        
        # Callback should be called
        assert callback_mock.call_count == 1


# Run tests using pytest
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])