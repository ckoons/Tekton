"""
Tests for the enhanced Apollo adapter.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from budget.adapters.apollo_enhancements import ApolloEnhancedAdapter
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert
)


class TestApolloEnhancedAdapter(unittest.TestCase):
    """Test the enhanced Apollo adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.patcher_debug_log = patch("budget.adapters.apollo_enhancements.debug_log")
        self.mock_debug_log = self.patcher_debug_log.start()
        
        self.patcher_budget_repo = patch("budget.adapters.apollo_enhancements.budget_repo")
        self.mock_budget_repo = self.patcher_budget_repo.start()
        
        self.patcher_policy_repo = patch("budget.adapters.apollo_enhancements.policy_repo")
        self.mock_policy_repo = self.patcher_policy_repo.start()
        
        self.patcher_allocation_repo = patch("budget.adapters.apollo_enhancements.allocation_repo")
        self.mock_allocation_repo = self.patcher_allocation_repo.start()
        
        self.patcher_usage_repo = patch("budget.adapters.apollo_enhancements.usage_repo")
        self.mock_usage_repo = self.patcher_usage_repo.start()
        
        self.patcher_alert_repo = patch("budget.adapters.apollo_enhancements.alert_repo")
        self.mock_alert_repo = self.patcher_alert_repo.start()
        
        self.patcher_pricing_repo = patch("budget.adapters.apollo_enhancements.pricing_repo")
        self.mock_pricing_repo = self.patcher_pricing_repo.start()
        
        self.patcher_budget_engine = patch("budget.adapters.apollo_enhancements.budget_engine")
        self.mock_budget_engine = self.patcher_budget_engine.start()
        
        self.patcher_allocation_manager = patch("budget.adapters.apollo_enhancements.allocation_manager")
        self.mock_allocation_manager = self.patcher_allocation_manager.start()
        
        self.patcher_apollo_adapter = patch("budget.adapters.apollo_enhancements.apollo_adapter")
        self.mock_apollo_adapter = self.patcher_apollo_adapter.start()
        self.mock_apollo_adapter.apollo_budget_id = "test-apollo-budget-id"
        
        # Create adapter
        self.adapter = ApolloEnhancedAdapter()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher_debug_log.stop()
        self.patcher_budget_repo.stop()
        self.patcher_policy_repo.stop()
        self.patcher_allocation_repo.stop()
        self.patcher_usage_repo.stop()
        self.patcher_alert_repo.stop()
        self.patcher_pricing_repo.stop()
        self.patcher_budget_engine.stop()
        self.patcher_allocation_manager.stop()
        self.patcher_apollo_adapter.stop()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.adapter.apollo_budget_id, "test-apollo-budget-id")
        self.assertEqual(self.adapter.base_adapter, self.mock_apollo_adapter)
    
    def test_provide_model_guidance(self):
        """Test providing model guidance."""
        # Mock budget summary
        mock_summary = MagicMock()
        mock_summary.token_usage_percentage = 0.8
        mock_summary.cost_usage_percentage = None
        self.mock_budget_engine.get_budget_summary.return_value = [mock_summary]
        
        # Mock pricing data
        mock_pricing1 = MagicMock()
        mock_pricing1.provider = "anthropic"
        mock_pricing1.model = "claude-3-sonnet"
        mock_pricing1.input_cost_per_token = 0.000003
        mock_pricing1.output_cost_per_token = 0.000015
        
        mock_pricing2 = MagicMock()
        mock_pricing2.provider = "openai"
        mock_pricing2.model = "gpt-4"
        mock_pricing2.input_cost_per_token = 0.00003
        mock_pricing2.output_cost_per_token = 0.00006
        
        mock_pricing3 = MagicMock()
        mock_pricing3.provider = "ollama"
        mock_pricing3.model = "llama3"
        mock_pricing3.input_cost_per_token = 0.0
        mock_pricing3.output_cost_per_token = 0.0
        
        self.mock_pricing_repo.get_all.return_value = [
            mock_pricing1, mock_pricing2, mock_pricing3
        ]
        
        # Call method
        result = self.adapter.provide_model_guidance(
            context_id="test-context-id",
            task_type="code",
            task_description="Write a function to sort a list",
            provider_preferences=["anthropic", "openai"],
            max_cost=0.01,
            preferred_tier=BudgetTier.REMOTE_HEAVYWEIGHT
        )
        
        # Verify
        self.assertEqual(result["context_id"], "test-context-id")
        self.assertEqual(result["task_type"], "code")
        self.assertTrue(result["approaching_budget_limit"])  # Since token_usage_percentage is 0.8
        self.assertEqual(result["preferred_tier"], "remote_heavyweight")
        self.assertEqual(len(result["recommended_models"]), 3)
        self.assertTrue("reasoning" in result)
        self.assertTrue(len(result["reasoning"]) > 0)
    
    def test_get_token_usage_analytics(self):
        """Test getting token usage analytics."""
        # Mock time range
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        # Mock usage records
        mock_record1 = MagicMock(spec=UsageRecord)
        mock_record1.provider = "anthropic"
        mock_record1.model = "claude-3-sonnet"
        mock_record1.component = "apollo"
        mock_record1.task_type = "code"
        mock_record1.input_tokens = 1000
        mock_record1.output_tokens = 500
        mock_record1.total_cost = 0.0105
        mock_record1.timestamp = start_time + timedelta(hours=2)
        
        mock_record2 = MagicMock(spec=UsageRecord)
        mock_record2.provider = "anthropic"
        mock_record2.model = "claude-3-sonnet"
        mock_record2.component = "rhetor"
        mock_record2.task_type = "chat"
        mock_record2.input_tokens = 800
        mock_record2.output_tokens = 400
        mock_record2.total_cost = 0.0084
        mock_record2.timestamp = start_time + timedelta(hours=4)
        
        mock_record3 = MagicMock(spec=UsageRecord)
        mock_record3.provider = "openai"
        mock_record3.model = "gpt-4"
        mock_record3.component = "apollo"
        mock_record3.task_type = "reasoning"
        mock_record3.input_tokens = 1200
        mock_record3.output_tokens = 600
        mock_record3.total_cost = 0.036
        mock_record3.timestamp = start_time + timedelta(hours=6)
        
        self.mock_usage_repo.get_by_time_range.return_value = [
            mock_record1, mock_record2, mock_record3
        ]
        
        # Call method
        result = self.adapter.get_token_usage_analytics(
            period=BudgetPeriod.DAILY,
            provider="anthropic"
        )
        
        # Verify
        self.assertEqual(result["period"], "daily")
        self.assertTrue("start_date" in result)
        self.assertTrue("end_date" in result)
        self.assertEqual(result["total_input_tokens"], 3000)  # All records combined
        self.assertEqual(result["total_output_tokens"], 1500)  # All records combined
        self.assertEqual(result["total_tokens"], 4500)
        self.assertEqual(result["total_cost"], 0.0549)
        self.assertEqual(result["record_count"], 3)
        
        # Verify providers
        self.assertEqual(len(result["providers"]), 2)
        self.assertIn("anthropic", result["providers"])
        self.assertIn("openai", result["providers"])
        
        # Verify components
        self.assertEqual(len(result["components"]), 2)
        self.assertIn("apollo", result["components"])
        self.assertIn("rhetor", result["components"])
        
        # Verify task types
        self.assertEqual(len(result["task_types"]), 3)
        self.assertIn("code", result["task_types"])
        self.assertIn("chat", result["task_types"])
        self.assertIn("reasoning", result["task_types"])
        
        # Verify time series is present
        self.assertIsNotNone(result["time_series"])
    
    def test_get_completion_efficiency(self):
        """Test getting completion efficiency."""
        # Mock time range
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        # Mock usage records for the target model
        mock_record1 = MagicMock(spec=UsageRecord)
        mock_record1.provider = "anthropic"
        mock_record1.model = "claude-3-sonnet"
        mock_record1.component = "apollo"
        mock_record1.task_type = "code"
        mock_record1.input_tokens = 1000
        mock_record1.output_tokens = 500
        mock_record1.total_cost = 0.0105
        
        mock_record2 = MagicMock(spec=UsageRecord)
        mock_record2.provider = "anthropic"
        mock_record2.model = "claude-3-sonnet"
        mock_record2.component = "apollo"
        mock_record2.task_type = "chat"
        mock_record2.input_tokens = 800
        mock_record2.output_tokens = 400
        mock_record2.total_cost = 0.0084
        
        self.mock_usage_repo.get_by_time_range.side_effect = [
            [mock_record1, mock_record2],  # First call for target model
            [mock_record1, mock_record2]   # Second call for all models
        ]
        
        # Call method
        result = self.adapter.get_completion_efficiency(
            provider="anthropic",
            model="claude-3-sonnet",
            period=BudgetPeriod.DAILY
        )
        
        # Verify
        self.assertEqual(result["provider"], "anthropic")
        self.assertEqual(result["model"], "claude-3-sonnet")
        self.assertEqual(result["period"], "daily")
        self.assertTrue(result["data_available"])
        self.assertEqual(result["completion_count"], 2)
        self.assertEqual(result["total_input_tokens"], 1800)
        self.assertEqual(result["total_output_tokens"], 900)
        self.assertEqual(result["total_tokens"], 2700)
        self.assertEqual(result["total_cost"], 0.0189)
        
        # Verify effectiveness metrics
        self.assertAlmostEqual(result["effectiveness_ratio"], 0.5, places=2)  # 900/1800
        self.assertTrue("cost_efficiency" in result)
        self.assertTrue("avg_cost_per_completion" in result)
        self.assertTrue("avg_tokens_per_completion" in result)
        
        # Verify task types
        self.assertEqual(len(result["task_types"]), 2)
        self.assertIn("code", result["task_types"])
        self.assertIn("chat", result["task_types"])
        
        # Verify alternatives and recommendations
        self.assertTrue("alternatives" in result)
        self.assertTrue("recommendations" in result)
    
    def test_get_completion_efficiency_no_data(self):
        """Test getting completion efficiency when no data is available."""
        # Mock empty usage records
        self.mock_usage_repo.get_by_time_range.return_value = []
        
        # Call method
        result = self.adapter.get_completion_efficiency(
            provider="anthropic",
            model="claude-3-sonnet",
            period=BudgetPeriod.DAILY
        )
        
        # Verify
        self.assertEqual(result["provider"], "anthropic")
        self.assertEqual(result["model"], "claude-3-sonnet")
        self.assertEqual(result["period"], "daily")
        self.assertFalse(result["data_available"])
        self.assertIn("message", result)
        self.assertEqual(result["message"], "No usage data available for this query")


if __name__ == '__main__':
    unittest.main()