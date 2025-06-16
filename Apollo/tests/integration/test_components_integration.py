"""
Integration tests for Apollo components.

These tests verify the interaction between multiple Apollo components.
"""

import os
import json
import tempfile
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

import pytest

from apollo.core.apollo_manager import ApolloManager
from apollo.core.context_observer import ContextObserver
from apollo.core.token_budget import TokenBudgetManager
from apollo.core.predictive_engine import PredictiveEngine
from apollo.core.action_planner import ActionPlanner
from apollo.core.protocol_enforcer import ProtocolEnforcer
from apollo.core.message_handler import MessageHandler
from apollo.core.interfaces.rhetor import RhetorInterface

from apollo.models.context import (
    ContextMetrics,
    ContextState,
    ContextHealth,
    ContextAction
)

from apollo.models.message import (
    TektonMessage,
    MessageType,
    MessagePriority
)


class TestComponentsIntegration(unittest.TestCase):
    """Test cases for integrating multiple Apollo components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create subdirectories for component data
        self.context_dir = os.path.join(self.test_dir, "context_data")
        self.budget_dir = os.path.join(self.test_dir, "budget_data")
        self.prediction_dir = os.path.join(self.test_dir, "prediction_data")
        self.action_dir = os.path.join(self.test_dir, "action_data")
        self.protocol_dir = os.path.join(self.test_dir, "protocol_data")
        self.message_dir = os.path.join(self.test_dir, "message_data")
        
        os.makedirs(self.context_dir, exist_ok=True)
        os.makedirs(self.budget_dir, exist_ok=True)
        os.makedirs(self.prediction_dir, exist_ok=True)
        os.makedirs(self.action_dir, exist_ok=True)
        os.makedirs(self.protocol_dir, exist_ok=True)
        os.makedirs(self.message_dir, exist_ok=True)
        
        # Create mock Rhetor interface
        self.mock_rhetor = AsyncMock()
        self.mock_rhetor.get_active_sessions.return_value = []
        
        # Create mock Hermes client
        self.mock_hermes = AsyncMock()
        self.mock_hermes.send_message.return_value = True
        self.mock_hermes.send_batch.return_value = True
        self.mock_hermes.subscribe.return_value = "test-subscription-id"
        self.mock_hermes.unsubscribe.return_value = True
        
        # Create components
        self.context_observer = ContextObserver(
            rhetor_interface=self.mock_rhetor,
            data_dir=self.context_dir,
            polling_interval=0.1  # Short interval for testing
        )
        
        self.token_budget = TokenBudgetManager(
            data_dir=self.budget_dir
        )
        
        self.protocol_enforcer = ProtocolEnforcer(
            protocols_dir=os.path.join(self.protocol_dir, "definitions"),
            data_dir=self.protocol_dir,
            load_defaults=False
        )
        
        self.predictive_engine = PredictiveEngine(
            context_observer=self.context_observer,
            data_dir=self.prediction_dir,
            prediction_interval=0.1  # Short interval for testing
        )
        
        self.action_planner = ActionPlanner(
            context_observer=self.context_observer,
            predictive_engine=self.predictive_engine,
            data_dir=self.action_dir,
            planning_interval=0.1  # Short interval for testing
        )
        
        self.message_handler = MessageHandler(
            component_name="apollo",
            hermes_client=self.mock_hermes,
            protocol_enforcer=self.protocol_enforcer,
            data_dir=self.message_dir
        )
        
        # Create Apollo manager
        self.apollo_manager = ApolloManager(
            rhetor_interface=self.mock_rhetor,
            data_dir=self.test_dir
        )
        
        # Register components with Apollo manager
        self.apollo_manager.context_observer = self.context_observer
        self.apollo_manager.token_budget_manager = self.token_budget
        self.apollo_manager.protocol_enforcer = self.protocol_enforcer
        self.apollo_manager.predictive_engine = self.predictive_engine
        self.apollo_manager.action_planner = self.action_planner
        self.apollo_manager.message_handler = self.message_handler
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    async def start_components(self):
        """Start all components for testing."""
        # Start components
        await self.message_handler.start()
        await self.context_observer.start()
        await self.predictive_engine.start()
        await self.action_planner.start()
        await self.apollo_manager.start()
    
    async def stop_components(self):
        """Stop all components after testing."""
        # Stop components in reverse order
        await self.apollo_manager.stop()
        await self.action_planner.stop()
        await self.predictive_engine.stop()
        await self.context_observer.stop()
        await self.message_handler.stop()
    
    async def test_context_to_prediction_to_action(self):
        """Test context state flowing to prediction to action."""
        # Start components
        await self.start_components()
        
        try:
            # Set up mock session that will trigger action
            critical_session = {
                "context_id": "test-context-flow",
                "component": "test-component",
                "provider": "test-provider",
                "model": "test-model",
                "input_tokens": 3800,
                "output_tokens": 1900,
                "total_tokens": 5700,
                "max_tokens": 6000,
                "token_utilization": 0.95,  # High utilization to trigger action
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
            
            self.mock_rhetor.get_active_sessions.return_value = [critical_session]
            
            # Wait for components to process
            await asyncio.sleep(0.5)
            
            # Context should be observed
            assert "test-context-flow" in self.context_observer.active_contexts
            
            # Context should have critical health
            context = self.context_observer.active_contexts["test-context-flow"]
            assert context.health == ContextHealth.CRITICAL
            
            # Wait for prediction engine to process
            await asyncio.sleep(0.5)
            
            # Should have prediction for context
            prediction = self.predictive_engine.get_prediction("test-context-flow")
            assert prediction is not None
            assert prediction.context_id == "test-context-flow"
            
            # Wait for action planner to process
            await asyncio.sleep(0.5)
            
            # Should have action for context
            actions = self.action_planner.get_actions("test-context-flow")
            assert len(actions) > 0
            
            # Should suggest reset action for critical health
            action = actions[0]
            assert action.context_id == "test-context-flow"
            assert action.action_type == "reset"
            assert action.priority >= 8  # High priority
            
            # Test Apollo manager dashboard
            dashboard = self.apollo_manager.get_context_dashboard("test-context-flow")
            assert dashboard is not None
            assert "state" in dashboard
            assert "health_trend" in dashboard
            assert "summary" in dashboard
            
            # Dashboard should include prediction and action
            assert "prediction" in dashboard
            assert "actions" in dashboard
            assert len(dashboard["actions"]) > 0
            
        finally:
            # Stop components
            await self.stop_components()
    
    async def test_budget_allocation_flow(self):
        """Test budget allocation flow."""
        # Start components
        await self.start_components()
        
        try:
            # Request a budget allocation
            allocation = await self.token_budget.allocate_budget(
                context_id="test-context-budget",
                task_type="conversation",
                component="test-component",
                provider="anthropic",
                model="claude-3-opus",
                priority=7,
                requested_tokens=5000
            )
            
            # Verify allocation
            assert allocation is not None
            assert allocation.context_id == "test-context-budget"
            assert allocation.task_type == "conversation"
            assert allocation.allocated_tokens >= 5000
            
            # Should be tracked in token budget manager
            assert "test-context-budget" in self.token_budget.active_allocations
            
            # Should be able to get through Apollo manager
            system_status = self.apollo_manager.get_system_status()
            assert system_status is not None
            
            # Verify system status
            assert "active_contexts" in system_status
            assert "components_status" in system_status
            assert system_status["system_running"] is True
            
        finally:
            # Stop components
            await self.stop_components()
    
    async def test_protocol_enforcement_flow(self):
        """Test protocol enforcement flow."""
        # Start components
        await self.start_components()
        
        try:
            # Add a test protocol
            from apollo.models.protocol import (
                ProtocolDefinition,
                ProtocolType,
                ProtocolSeverity,
                ProtocolScope,
                EnforcementMode,
                MessageFormatRule
            )
            
            protocol = ProtocolDefinition(
                protocol_id="test.protocol.flow",
                name="Test Protocol",
                description="A test protocol for integration testing",
                type=ProtocolType.MESSAGE_FORMAT,
                scope=ProtocolScope.GLOBAL,
                enforcement_mode=EnforcementMode.WARN,
                severity=ProtocolSeverity.WARNING,
                applicable_components=["*"],
                rules=MessageFormatRule(
                    required_fields=["message_id", "source", "type"]
                ).dict()
            )
            
            self.protocol_enforcer.add_protocol(protocol)
            
            # Create valid message
            valid_message = {
                "message_id": "test-message",
                "source": "test-component",
                "type": "test.message",
                "content": "Test content"
            }
            
            context = {
                "component": "test-component",
                "message_type": "test.message"
            }
            
            # Process through protocol enforcer
            result = await self.protocol_enforcer.handle_message(valid_message, context)
            
            # Should pass validation
            assert result == valid_message
            
            # Create invalid message
            invalid_message = {
                # Missing message_id
                "source": "test-component",
                "type": "test.message",
                "content": "Test content"
            }
            
            # Process through protocol enforcer
            result = await self.protocol_enforcer.handle_message(invalid_message, context)
            
            # Should still pass (WARN mode) but generate violation
            assert result == invalid_message
            
            # Should have violation in history
            assert len(self.protocol_enforcer.violation_history) > 0
            violation = self.protocol_enforcer.violation_history[0]
            assert violation.protocol_id == "test.protocol.flow"
            assert "message_id" in violation.message
            
            # Should have updated stats
            stats = self.protocol_enforcer.get_protocol_stats("test.protocol.flow")
            assert stats.total_evaluations > 0
            assert stats.total_violations > 0
            
        finally:
            # Stop components
            await self.stop_components()
    
    async def test_message_handling_flow(self):
        """Test message handling flow."""
        # Start components
        await self.start_components()
        
        try:
            # Create a test message
            test_message = TektonMessage(
                message_id="test-message-flow",
                type=MessageType.CONTEXT_HEALTH,
                source="test-component",
                context_id="test-context-message",
                payload={
                    "health": "critical",
                    "health_score": 0.3,
                    "reason": "High token utilization"
                }
            )
            
            # Send message
            await self.message_handler.send_message(test_message)
            
            # Should queue message for sending
            assert self.message_handler.outbound_queue.qsize() > 0
            
            # Wait for message to be processed
            await asyncio.sleep(0.2)
            
            # Should have called Hermes client
            assert self.mock_hermes.send_batch.called
            
            # Test receiving a message
            received_message = TektonMessage(
                message_id="received-message",
                type=MessageType.ACTION_RECOMMENDED,
                source="other-component",
                context_id="test-context-message",
                payload={
                    "action_type": "reset",
                    "priority": 10,
                    "reason": "Critical context health"
                }
            )
            
            # Create a test callback
            callback_mock = AsyncMock()
            
            # Register callback for message type
            self.message_handler.register_message_callback(
                MessageType.ACTION_RECOMMENDED,
                callback_mock
            )
            
            # Receive message
            await self.message_handler.receive_message(received_message)
            
            # Wait for message to be processed
            await asyncio.sleep(0.2)
            
            # Should have queued message
            assert self.message_handler.inbound_queue.qsize() == 0  # Should be processed
            
            # Statistics should be available
            queue_stats = self.message_handler.get_queue_stats()
            assert queue_stats is not None
            
        finally:
            # Stop components
            await self.stop_components()


# Run tests using pytest
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])