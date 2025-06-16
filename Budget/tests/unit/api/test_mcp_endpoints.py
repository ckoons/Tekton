"""
Tests for the MCP Protocol endpoints.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from datetime import datetime, timedelta

from budget.api.mcp_endpoints import (
    MCPMessage, MCPRequest, MCPResponse, MCPEvent,
    handle_allocate_tokens, handle_check_budget, handle_record_usage,
    handle_get_budget_status, handle_get_model_recommendations,
    handle_route_with_budget_awareness, handle_get_usage_analytics,
    process_mcp_message
)


class TestMCPEndpoints(unittest.TestCase):
    """Test the MCP Protocol endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock debug_log
        self.patcher_debug_log = patch("budget.api.mcp_endpoints.debug_log")
        self.mock_debug_log = self.patcher_debug_log.start()
        
        # Mock adapters
        self.patcher_apollo_adapter = patch("budget.api.mcp_endpoints.apollo_adapter")
        self.mock_apollo_adapter = self.patcher_apollo_adapter.start()
        
        self.patcher_rhetor_adapter = patch("budget.api.mcp_endpoints.rhetor_adapter")
        self.mock_rhetor_adapter = self.patcher_rhetor_adapter.start()
        self.mock_rhetor_adapter.rhetor_budget_id = "test-rhetor-budget-id"
        
        self.patcher_apollo_enhanced = patch("budget.api.mcp_endpoints.apollo_enhanced")
        self.mock_apollo_enhanced = self.patcher_apollo_enhanced.start()
        
        # Mock core services
        self.patcher_budget_engine = patch("budget.api.mcp_endpoints.budget_engine")
        self.mock_budget_engine = self.patcher_budget_engine.start()
        
        self.patcher_allocation_manager = patch("budget.api.mcp_endpoints.allocation_manager")
        self.mock_allocation_manager = self.patcher_allocation_manager.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher_debug_log.stop()
        self.patcher_apollo_adapter.stop()
        self.patcher_rhetor_adapter.stop()
        self.patcher_apollo_enhanced.stop()
        self.patcher_budget_engine.stop()
        self.patcher_allocation_manager.stop()
    
    async def test_process_mcp_message_unknown(self):
        """Test processing an unknown message type."""
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="test-component",
            message_type="unknown.message",
            payload={}
        )
        
        # Process message
        response = await process_mcp_message(message)
        
        # Verify
        self.assertEqual(response.status, "error")
        self.assertEqual(response.message_type, "budget.error")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertIn("Unknown message type", response.error)
    
    async def test_handle_allocate_tokens(self):
        """Test handling allocate_tokens message."""
        # Mock allocation
        mock_allocation = MagicMock()
        mock_allocation.allocation_id = "test-allocation-id"
        mock_allocation.context_id = "test-context-id"
        mock_allocation.tokens_allocated = 1000
        mock_allocation.remaining_tokens = 1000
        
        # Set up allocation_manager mock
        self.mock_allocation_manager.allocate_budget.return_value = mock_allocation
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="test-component",
            message_type="budget.allocate_tokens",
            payload={
                "context_id": "test-context-id",
                "amount": 1000,
                "tier": "remote_heavyweight",
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "task_type": "code",
                "priority": 8
            }
        )
        
        # Handle message
        response = await handle_allocate_tokens(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.allocation_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["allocation_id"], "test-allocation-id")
        self.assertEqual(response.payload["context_id"], "test-context-id")
        self.assertEqual(response.payload["amount"], 1000)
        self.assertEqual(response.payload["remaining"], 1000)
        self.assertEqual(response.payload["tier"], "remote_heavyweight")
        self.assertEqual(response.payload["provider"], "anthropic")
        self.assertEqual(response.payload["model"], "claude-3-sonnet")
        
        # Verify allocation_manager called correctly
        self.mock_allocation_manager.allocate_budget.assert_called_once()
        args, kwargs = self.mock_allocation_manager.allocate_budget.call_args
        self.assertEqual(kwargs["context_id"], "test-context-id")
        self.assertEqual(kwargs["component"], "test-component")
        self.assertEqual(kwargs["tokens"], 1000)
        self.assertEqual(kwargs["task_type"], "code")
        self.assertEqual(kwargs["priority"], 8)
    
    async def test_handle_check_budget_apollo(self):
        """Test handling check_budget message from Apollo."""
        # Mock check_budget
        self.mock_apollo_adapter.check_budget.return_value = (
            True, {"allowed": True, "reason": "Within budget"}
        )
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="apollo",
            message_type="budget.check_budget",
            payload={
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "input_text": "Test input",
                "task_type": "code"
            }
        )
        
        # Handle message
        response = await handle_check_budget(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.check_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertTrue(response.payload["allowed"])
        self.assertEqual(response.payload["info"]["allowed"], True)
        self.assertEqual(response.payload["info"]["reason"], "Within budget")
        
        # Verify adapter called correctly
        self.mock_apollo_adapter.check_budget.assert_called_once()
        args, kwargs = self.mock_apollo_adapter.check_budget.call_args
        self.assertEqual(kwargs["provider"], "anthropic")
        self.assertEqual(kwargs["model"], "claude-3-sonnet")
        self.assertEqual(kwargs["input_text"], "Test input")
        self.assertEqual(kwargs["component"], "apollo")
        self.assertEqual(kwargs["task_type"], "code")
    
    async def test_handle_check_budget_rhetor(self):
        """Test handling check_budget message from Rhetor."""
        # Mock check_budget
        self.mock_rhetor_adapter.check_budget.return_value = (
            True, {"allowed": True, "reason": "Within budget"}
        )
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="rhetor",
            message_type="budget.check_budget",
            payload={
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "input_text": "Test input",
                "task_type": "code",
                "context_id": "test-context-id"
            }
        )
        
        # Handle message
        response = await handle_check_budget(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.check_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertTrue(response.payload["allowed"])
        self.assertEqual(response.payload["info"]["allowed"], True)
        self.assertEqual(response.payload["info"]["reason"], "Within budget")
        
        # Verify adapter called correctly
        self.mock_rhetor_adapter.check_budget.assert_called_once()
        args, kwargs = self.mock_rhetor_adapter.check_budget.call_args
        self.assertEqual(kwargs["provider"], "anthropic")
        self.assertEqual(kwargs["model"], "claude-3-sonnet")
        self.assertEqual(kwargs["input_text"], "Test input")
        self.assertEqual(kwargs["component"], "rhetor")
        self.assertEqual(kwargs["task_type"], "code")
        self.assertEqual(kwargs["context_id"], "test-context-id")
    
    async def test_handle_record_usage_with_text(self):
        """Test handling record_usage message with text."""
        # Mock record_completion
        self.mock_rhetor_adapter.record_completion.return_value = {
            "context_id": "test-context-id",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_cost": 0.00105
        }
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="ergon",
            message_type="budget.record_usage",
            payload={
                "context_id": "test-context-id",
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "input_text": "Test input",
                "output_text": "Test output",
                "task_type": "code",
                "metadata": {"request_id": "test-request-id"}
            }
        )
        
        # Handle message
        response = await handle_record_usage(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.usage_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["context_id"], "test-context-id")
        self.assertEqual(response.payload["input_tokens"], 100)
        self.assertEqual(response.payload["output_tokens"], 50)
        self.assertEqual(response.payload["total_cost"], 0.00105)
        
        # Verify adapter called correctly
        self.mock_rhetor_adapter.record_completion.assert_called_once()
        args, kwargs = self.mock_rhetor_adapter.record_completion.call_args
        self.assertEqual(kwargs["provider"], "anthropic")
        self.assertEqual(kwargs["model"], "claude-3-sonnet")
        self.assertEqual(kwargs["input_text"], "Test input")
        self.assertEqual(kwargs["output_text"], "Test output")
        self.assertEqual(kwargs["component"], "ergon")
        self.assertEqual(kwargs["task_type"], "code")
        self.assertEqual(kwargs["context_id"], "test-context-id")
        self.assertEqual(kwargs["metadata"], {"request_id": "test-request-id"})
    
    async def test_handle_record_usage_with_tokens(self):
        """Test handling record_usage message with token counts."""
        # Mock record usage
        mock_record = MagicMock()
        mock_record.remaining_tokens = 900
        self.mock_allocation_manager.record_usage.return_value = mock_record
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="ergon",
            message_type="budget.record_usage",
            payload={
                "context_id": "test-context-id",
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "input_tokens": 100,
                "output_tokens": 50,
                "allocation_id": "test-allocation-id",
                "request_id": "test-request-id"
            }
        )
        
        # Handle message
        response = await handle_record_usage(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.usage_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["context_id"], "test-context-id")
        self.assertEqual(response.payload["allocation_id"], "test-allocation-id")
        self.assertEqual(response.payload["recorded_tokens"], 150)
        self.assertEqual(response.payload["remaining"], 900)
        self.assertTrue(response.payload["success"])
        
        # Verify allocation_manager called correctly
        self.mock_allocation_manager.record_usage.assert_called_once()
        args, kwargs = self.mock_allocation_manager.record_usage.call_args
        self.assertEqual(kwargs["allocation_id"], "test-allocation-id")
        self.assertEqual(kwargs["input_tokens"], 100)
        self.assertEqual(kwargs["output_tokens"], 50)
        self.assertEqual(kwargs["provider"], "anthropic")
        self.assertEqual(kwargs["model"], "claude-3-sonnet")
        self.assertEqual(kwargs["request_id"], "test-request-id")
    
    async def test_handle_get_budget_status_apollo(self):
        """Test handling get_budget_status message from Apollo."""
        # Mock get_budget_status
        self.mock_apollo_adapter.get_budget_status.return_value = {
            "period": "daily",
            "success": True,
            "tiers": {
                "heavyweight": {
                    "allocated": 10000,
                    "used": 5000,
                    "remaining": 5000,
                    "limit": 10000,
                    "usage_percentage": 0.5,
                    "limit_exceeded": False
                }
            }
        }
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="apollo",
            message_type="budget.get_budget_status",
            payload={
                "period": "daily",
                "tier": "heavyweight"
            }
        )
        
        # Handle message
        response = await handle_get_budget_status(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.status_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["period"], "daily")
        self.assertTrue(response.payload["success"])
        self.assertIn("tiers", response.payload)
        self.assertIn("heavyweight", response.payload["tiers"])
        
        # Verify adapter called correctly
        self.mock_apollo_adapter.get_budget_status.assert_called_once()
        args, kwargs = self.mock_apollo_adapter.get_budget_status.call_args
        self.assertEqual(kwargs["period"], "daily")
        self.assertEqual(kwargs["tier"], "heavyweight")
    
    async def test_handle_get_budget_status_rhetor(self):
        """Test handling get_budget_status message from Rhetor."""
        # Mock get_budget_summary
        mock_summary = MagicMock()
        mock_summary.tier = "remote_heavyweight"
        mock_summary.total_tokens_allocated = 10000
        mock_summary.total_tokens_used = 5000
        mock_summary.remaining_tokens = 5000
        mock_summary.token_limit = 10000
        mock_summary.token_usage_percentage = 0.5
        mock_summary.token_limit_exceeded = False
        
        self.mock_budget_engine.get_budget_summary.return_value = [mock_summary]
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="rhetor",
            message_type="budget.get_budget_status",
            payload={
                "period": "daily",
                "tier": "remote_heavyweight",
                "provider": "anthropic"
            }
        )
        
        # Handle message
        response = await handle_get_budget_status(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.status_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["period"], "daily")
        self.assertTrue(response.payload["success"])
        self.assertIn("tiers", response.payload)
        self.assertIn("remote_heavyweight", response.payload["tiers"])
        
        # Verify budget_engine called correctly
        self.mock_budget_engine.get_budget_summary.assert_called_once()
        args, kwargs = self.mock_budget_engine.get_budget_summary.call_args
        self.assertEqual(kwargs["budget_id"], "test-rhetor-budget-id")
        self.assertEqual(kwargs["period"], "daily")
        self.assertEqual(kwargs["tier"], "remote_heavyweight")
        self.assertEqual(kwargs["provider"], "anthropic")
    
    async def test_handle_get_model_recommendations(self):
        """Test handling get_model_recommendations message."""
        # Mock get_model_recommendations
        self.mock_budget_engine.get_model_recommendations.return_value = [
            {
                "provider": "anthropic",
                "model": "claude-3-haiku",
                "estimated_cost": 0.0005,
                "savings": 0.001,
                "savings_percent": 66.7
            }
        ]
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="test-component",
            message_type="budget.get_model_recommendations",
            payload={
                "provider": "anthropic",
                "model": "claude-3-sonnet",
                "task_type": "code",
                "context_size": 5000
            }
        )
        
        # Handle message
        response = await handle_get_model_recommendations(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.recommendations_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["provider"], "anthropic")
        self.assertEqual(response.payload["model"], "claude-3-sonnet")
        self.assertEqual(response.payload["task_type"], "code")
        self.assertEqual(response.payload["context_size"], 5000)
        self.assertEqual(len(response.payload["recommendations"]), 1)
        self.assertEqual(response.payload["recommendations"][0]["provider"], "anthropic")
        self.assertEqual(response.payload["recommendations"][0]["model"], "claude-3-haiku")
        
        # Verify budget_engine called correctly
        self.mock_budget_engine.get_model_recommendations.assert_called_once()
        args, kwargs = self.mock_budget_engine.get_model_recommendations.call_args
        self.assertEqual(kwargs["provider"], "anthropic")
        self.assertEqual(kwargs["model"], "claude-3-sonnet")
        self.assertEqual(kwargs["task_type"], "code")
        self.assertEqual(kwargs["context_size"], 5000)
    
    async def test_handle_route_with_budget_awareness(self):
        """Test handling route_with_budget_awareness message."""
        # Mock route_with_budget_awareness
        self.mock_rhetor_adapter.route_with_budget_awareness.return_value = (
            "anthropic", "claude-3-haiku", 
            ["Budget limit exceeded. Downgraded from anthropic/claude-3-sonnet to anthropic/claude-3-haiku"]
        )
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="rhetor",
            message_type="budget.route_with_budget_awareness",
            payload={
                "input_text": "Test input",
                "task_type": "code",
                "default_provider": "anthropic",
                "default_model": "claude-3-sonnet"
            }
        )
        
        # Handle message
        response = await handle_route_with_budget_awareness(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.routing_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["provider"], "anthropic")
        self.assertEqual(response.payload["model"], "claude-3-haiku")
        self.assertEqual(response.payload["original_provider"], "anthropic")
        self.assertEqual(response.payload["original_model"], "claude-3-sonnet")
        self.assertTrue(response.payload["is_downgraded"])
        self.assertTrue(len(response.payload["warnings"]) > 0)
        
        # Verify adapter called correctly
        self.mock_rhetor_adapter.route_with_budget_awareness.assert_called_once()
        args, kwargs = self.mock_rhetor_adapter.route_with_budget_awareness.call_args
        self.assertEqual(kwargs["input_text"], "Test input")
        self.assertEqual(kwargs["task_type"], "code")
        self.assertEqual(kwargs["default_provider"], "anthropic")
        self.assertEqual(kwargs["default_model"], "claude-3-sonnet")
        self.assertEqual(kwargs["component"], "rhetor")
    
    async def test_handle_get_usage_analytics(self):
        """Test handling get_usage_analytics message."""
        # Mock get_token_usage_analytics
        self.mock_apollo_enhanced.get_token_usage_analytics.return_value = {
            "period": "daily",
            "total_input_tokens": 3000,
            "total_output_tokens": 1500,
            "total_tokens": 4500,
            "total_cost": 0.05,
            "providers": {
                "anthropic": {
                    "input_tokens": 3000,
                    "output_tokens": 1500,
                    "total_tokens": 4500,
                    "cost": 0.05,
                    "count": 3
                }
            }
        }
        
        # Create message
        message = MCPRequest(
            message_id="test-message-id",
            sender="test-component",
            message_type="budget.get_usage_analytics",
            payload={
                "period": "daily",
                "provider": "anthropic",
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-01-02T00:00:00"
            }
        )
        
        # Handle message
        response = await handle_get_usage_analytics(message)
        
        # Verify
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message_type, "budget.analytics_response")
        self.assertEqual(response.request_id, "test-message-id")
        self.assertEqual(response.payload["period"], "daily")
        self.assertEqual(response.payload["total_input_tokens"], 3000)
        self.assertEqual(response.payload["total_output_tokens"], 1500)
        self.assertEqual(response.payload["total_tokens"], 4500)
        self.assertEqual(response.payload["total_cost"], 0.05)
        
        # Verify apollo_enhanced called correctly
        self.mock_apollo_enhanced.get_token_usage_analytics.assert_called_once()
        args, kwargs = self.mock_apollo_enhanced.get_token_usage_analytics.call_args
        self.assertEqual(kwargs["period"], "daily")
        self.assertEqual(kwargs["provider"], "anthropic")
        self.assertEqual(str(kwargs["start_date"]), "2023-01-01 00:00:00")
        self.assertEqual(str(kwargs["end_date"]), "2023-01-02 00:00:00")


if __name__ == '__main__':
    unittest.main()