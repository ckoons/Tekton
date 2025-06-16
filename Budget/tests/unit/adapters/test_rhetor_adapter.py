"""
Tests for the Rhetor adapter.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from budget.adapters.rhetor import RhetorAdapter
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert
)


class TestRhetorAdapter(unittest.TestCase):
    """Test the Rhetor adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.patcher_debug_log = patch("budget.adapters.rhetor.debug_log")
        self.mock_debug_log = self.patcher_debug_log.start()
        
        self.patcher_budget_repo = patch("budget.adapters.rhetor.budget_repo")
        self.mock_budget_repo = self.patcher_budget_repo.start()
        
        self.patcher_policy_repo = patch("budget.adapters.rhetor.policy_repo")
        self.mock_policy_repo = self.patcher_policy_repo.start()
        
        self.patcher_allocation_repo = patch("budget.adapters.rhetor.allocation_repo")
        self.mock_allocation_repo = self.patcher_allocation_repo.start()
        
        self.patcher_usage_repo = patch("budget.adapters.rhetor.usage_repo")
        self.mock_usage_repo = self.patcher_usage_repo.start()
        
        self.patcher_alert_repo = patch("budget.adapters.rhetor.alert_repo")
        self.mock_alert_repo = self.patcher_alert_repo.start()
        
        self.patcher_pricing_repo = patch("budget.adapters.rhetor.pricing_repo")
        self.mock_pricing_repo = self.patcher_pricing_repo.start()
        
        self.patcher_budget_engine = patch("budget.adapters.rhetor.budget_engine")
        self.mock_budget_engine = self.patcher_budget_engine.start()
        
        self.patcher_allocation_manager = patch("budget.adapters.rhetor.allocation_manager")
        self.mock_allocation_manager = self.patcher_allocation_manager.start()
        
        # Mock the budget repo to return an existing Rhetor budget
        mock_budget = MagicMock(spec=Budget)
        mock_budget.budget_id = "test-rhetor-budget-id"
        mock_budget.name = "Rhetor Budget"
        self.mock_budget_repo.get_all.return_value = [mock_budget]
        
        # Create adapter
        self.adapter = RhetorAdapter()
    
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
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.adapter.rhetor_budget_id, "test-rhetor-budget-id")
        self.assertDictEqual(self.adapter.period_mapping, {
            "daily": BudgetPeriod.DAILY,
            "weekly": BudgetPeriod.WEEKLY,
            "monthly": BudgetPeriod.MONTHLY
        })
        self.assertDictEqual(self.adapter.policy_mapping, {
            "ignore": BudgetPolicyType.IGNORE,
            "warn": BudgetPolicyType.WARN,
            "enforce": BudgetPolicyType.HARD_LIMIT
        })
    
    def test_init_creates_rhetor_budget_if_not_exists(self):
        """Test that a new Rhetor budget is created if one doesn't exist."""
        # Mock the budget repo to return no budgets
        self.mock_budget_repo.get_all.return_value = []
        
        # Mock budget engine to return a new budget
        mock_budget = MagicMock(spec=Budget)
        mock_budget.budget_id = "new-rhetor-budget-id"
        self.mock_budget_engine.create_budget.return_value = mock_budget
        
        # Create adapter
        adapter = RhetorAdapter()
        
        # Verify
        self.assertEqual(adapter.rhetor_budget_id, "new-rhetor-budget-id")
        self.mock_budget_engine.create_budget.assert_called_once_with(
            name="Rhetor Budget", 
            description="Budget for Rhetor component (migrated)",
            owner="rhetor"
        )
        self.mock_budget_engine.create_default_policies.assert_called_once_with(
            "new-rhetor-budget-id"
        )
    
    def test_calculate_cost(self):
        """Test calculating cost."""
        # Mock pricing
        mock_pricing = MagicMock()
        mock_pricing.input_cost_per_token = 0.000003
        mock_pricing.output_cost_per_token = 0.000015
        self.mock_pricing_repo.get_current_pricing.return_value = mock_pricing
        
        # Mock token counting
        self.mock_allocation_manager.count_tokens.side_effect = [100, 50]
        
        # Call method
        result = self.adapter.calculate_cost(
            provider="anthropic",
            model="claude-3-sonnet",
            input_text="Test input",
            output_text="Test output"
        )
        
        # Verify
        self.assertEqual(result["input_tokens"], 100)
        self.assertEqual(result["output_tokens"], 50)
        self.assertEqual(result["input_cost"], 0.0003)
        self.assertEqual(result["output_cost"], 0.00075)
        self.assertEqual(result["total_cost"], 0.00105)
        
        self.mock_allocation_manager.count_tokens.assert_any_call(
            "anthropic", "claude-3-sonnet", "Test input"
        )
        self.mock_allocation_manager.count_tokens.assert_any_call(
            "anthropic", "claude-3-sonnet", "Test output"
        )
    
    def test_calculate_cost_with_no_pricing(self):
        """Test calculating cost when no pricing is found."""
        # Mock pricing not found
        self.mock_pricing_repo.get_current_pricing.return_value = None
        
        # Mock token counting
        self.mock_allocation_manager.count_tokens.side_effect = [100, 50]
        
        # Call method
        result = self.adapter.calculate_cost(
            provider="unknown",
            model="unknown-model",
            input_text="Test input",
            output_text="Test output"
        )
        
        # Verify
        self.assertEqual(result["input_tokens"], 100)
        self.assertEqual(result["output_tokens"], 50)
        self.assertEqual(result["input_cost"], 0.0)
        self.assertEqual(result["output_cost"], 0.0)
        self.assertEqual(result["total_cost"], 0.0)
    
    def test_estimate_cost(self):
        """Test estimating cost."""
        # Mock calculate_cost method
        with patch.object(
            self.adapter, 'calculate_cost', 
            return_value={
                "input_tokens": 100,
                "output_tokens": 200,
                "input_cost": 0.0003,
                "output_cost": 0.0015,
                "total_cost": 0.0018
            }
        ) as mock_calculate_cost:
            # Call method
            result = self.adapter.estimate_cost(
                provider="anthropic",
                model="claude-3-sonnet",
                input_text="Test input",
                estimated_output_length=500
            )
            
            # Verify
            self.assertEqual(result["input_tokens"], 100)
            self.assertEqual(result["output_tokens"], 200)
            self.assertEqual(result["input_cost"], 0.0003)
            self.assertEqual(result["output_cost"], 0.0015)
            self.assertEqual(result["total_cost"], 0.0018)
            
            # Verify estimate output was generated
            mock_calculate_cost.assert_called_once()
            args, kwargs = mock_calculate_cost.call_args
            self.assertEqual(kwargs["provider"], "anthropic")
            self.assertEqual(kwargs["model"], "claude-3-sonnet")
            self.assertEqual(kwargs["input_text"], "Test input")
            self.assertEqual(len(kwargs["output_text"]), 500)
    
    def test_record_completion(self):
        """Test recording a completion."""
        # Mock calculate_cost method
        with patch.object(
            self.adapter, 'calculate_cost', 
            return_value={
                "input_tokens": 100,
                "output_tokens": 50,
                "input_cost": 0.0003,
                "output_cost": 0.00075,
                "total_cost": 0.00105
            }
        ):
            # Mock usage repo
            mock_record = MagicMock(spec=UsageRecord)
            mock_record.record_id = "test-record-id"
            self.mock_usage_repo.create.return_value = mock_record
            
            # Call method
            result = self.adapter.record_completion(
                provider="anthropic",
                model="claude-3-sonnet",
                input_text="Test input",
                output_text="Test output",
                component="test-component",
                task_type="test-task",
                context_id="test-context-id"
            )
            
            # Verify
            self.assertEqual(result["provider"], "anthropic")
            self.assertEqual(result["model"], "claude-3-sonnet")
            self.assertEqual(result["component"], "test-component")
            self.assertEqual(result["task_type"], "test-task")
            self.assertEqual(result["input_tokens"], 100)
            self.assertEqual(result["output_tokens"], 50)
            self.assertEqual(result["total_tokens"], 150)
            self.assertEqual(result["input_cost"], 0.0003)
            self.assertEqual(result["output_cost"], 0.00075)
            self.assertEqual(result["total_cost"], 0.00105)
            self.assertEqual(result["record_id"], "test-record-id")
            self.assertEqual(result["context_id"], "test-context-id")
            
            # Verify usage record was created
            self.mock_usage_repo.create.assert_called_once()
            args, kwargs = self.mock_usage_repo.create.call_args
            record = args[0]
            self.assertEqual(record.budget_id, "test-rhetor-budget-id")
            self.assertEqual(record.context_id, "test-context-id")
            self.assertEqual(record.component, "test-component")
            self.assertEqual(record.provider, "anthropic")
            self.assertEqual(record.model, "claude-3-sonnet")
            self.assertEqual(record.task_type, "test-task")
            self.assertEqual(record.input_tokens, 100)
            self.assertEqual(record.output_tokens, 50)
            self.assertEqual(record.input_cost, 0.0003)
            self.assertEqual(record.output_cost, 0.00075)
            self.assertEqual(record.total_cost, 0.00105)
    
    def test_check_budget_for_free_model(self):
        """Test checking budget for a free model."""
        # Mock estimate_cost method
        with patch.object(
            self.adapter, 'estimate_cost', 
            return_value={
                "input_tokens": 100,
                "output_tokens": 50,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0
            }
        ):
            # Call method
            allowed, info = self.adapter.check_budget(
                provider="ollama",
                model="llama3",
                input_text="Test input"
            )
            
            # Verify
            self.assertTrue(allowed)
            self.assertTrue(info["allowed"])
            self.assertEqual(info["reason"], "Free model")
    
    def test_check_budget_with_cost_limit_exceeded(self):
        """Test checking budget when cost limit is exceeded."""
        # Mock estimate_cost method
        with patch.object(
            self.adapter, 'estimate_cost', 
            return_value={
                "input_tokens": 100,
                "output_tokens": 50,
                "input_cost": 0.0003,
                "output_cost": 0.00075,
                "total_cost": 0.00105
            }
        ):
            # Mock budget summary
            mock_summary = MagicMock()
            mock_summary.total_cost = 9.999
            self.mock_budget_engine.get_budget_summary.return_value = [mock_summary]
            
            # Mock policy
            mock_policy = MagicMock(spec=BudgetPolicy)
            mock_policy.cost_limit = 10.0
            mock_policy.type = BudgetPolicyType.HARD_LIMIT
            self.mock_policy_repo.get_active_policies.return_value = [mock_policy]
            
            # Call method
            allowed, info = self.adapter.check_budget(
                provider="anthropic",
                model="claude-3-sonnet",
                input_text="Test input"
            )
            
            # Verify
            self.assertFalse(allowed)
            self.assertFalse(info["allowed"])
            self.assertEqual(info["reason"], "Daily budget limit exceeded")
            self.assertEqual(info["limit"], 10.0)
            self.assertEqual(info["usage"], 9.999)
            self.assertEqual(info["estimated_cost"], 0.00105)
    
    def test_get_usage_summary(self):
        """Test getting usage summary."""
        # Mock time range calculation
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        with patch.object(
            self.adapter, '_get_time_range_for_period',
            return_value=(start_time, end_time)
        ):
            # Mock budget summary
            mock_summary = MagicMock()
            self.mock_budget_engine.get_budget_summary.return_value = [mock_summary]
            
            # Mock usage records
            mock_record1 = MagicMock(spec=UsageRecord)
            mock_record1.provider = "anthropic"
            mock_record1.input_tokens = 100
            mock_record1.output_tokens = 50
            mock_record1.total_cost = 0.00105
            
            mock_record2 = MagicMock(spec=UsageRecord)
            mock_record2.provider = "openai"
            mock_record2.input_tokens = 200
            mock_record2.output_tokens = 100
            mock_record2.total_cost = 0.0031
            
            self.mock_usage_repo.get_by_time_range.return_value = [mock_record1, mock_record2]
            
            # Call method
            result = self.adapter.get_usage_summary(
                period=BudgetPeriod.DAILY,
                group_by="provider"
            )
            
            # Verify
            self.assertEqual(result["period"], "daily")
            self.assertEqual(result["total_cost"], 0.00415)
            self.assertEqual(result["total_input_tokens"], 300)
            self.assertEqual(result["total_output_tokens"], 150)
            self.assertEqual(result["total_tokens"], 450)
            self.assertEqual(result["count"], 2)
            
            # Verify groups
            self.assertEqual(len(result["groups"]), 2)
            self.assertIn("anthropic", result["groups"])
            self.assertIn("openai", result["groups"])
            
            # Verify anthropic group
            anthropic_group = result["groups"]["anthropic"]
            self.assertEqual(anthropic_group["cost"], 0.00105)
            self.assertEqual(anthropic_group["input_tokens"], 100)
            self.assertEqual(anthropic_group["output_tokens"], 50)
            self.assertEqual(anthropic_group["count"], 1)
            
            # Verify openai group
            openai_group = result["groups"]["openai"]
            self.assertEqual(openai_group["cost"], 0.0031)
            self.assertEqual(openai_group["input_tokens"], 200)
            self.assertEqual(openai_group["output_tokens"], 100)
            self.assertEqual(openai_group["count"], 1)
    
    def test_route_with_budget_awareness(self):
        """Test routing with budget awareness."""
        # Case 1: Default model is allowed and no alternatives
        with patch.object(
            self.adapter, 'check_budget',
            return_value=(True, {"allowed": True})
        ):
            # Call method
            provider, model, warnings = self.adapter.route_with_budget_awareness(
                input_text="Test input",
                task_type="test-task",
                default_provider="anthropic",
                default_model="claude-3-sonnet"
            )
            
            # Verify
            self.assertEqual(provider, "anthropic")
            self.assertEqual(model, "claude-3-sonnet")
            self.assertEqual(warnings, [])
        
        # Case 2: Default model is allowed but cheaper alternative exists and we're approaching limit
        with patch.object(
            self.adapter, 'check_budget',
            return_value=(True, {
                "allowed": True,
                "alternatives": [{
                    "provider": "anthropic",
                    "model": "claude-3-haiku",
                    "savings": 0.0005,
                    "savings_percent": 50.0
                }]
            })
        ), patch.object(
            self.adapter, 'get_enforcement_policy',
            return_value=BudgetPolicyType.SOFT_LIMIT.value
        ):
            # Mock budget summary
            mock_summary = MagicMock()
            mock_summary.cost_usage_percentage = 0.85
            self.mock_budget_engine.get_budget_summary.return_value = [mock_summary]
            
            # Call method
            provider, model, warnings = self.adapter.route_with_budget_awareness(
                input_text="Test input",
                task_type="test-task",
                default_provider="anthropic",
                default_model="claude-3-sonnet"
            )
            
            # Verify
            self.assertEqual(provider, "anthropic")
            self.assertEqual(model, "claude-3-haiku")
            self.assertTrue(len(warnings) > 0)
            self.assertTrue("Budget approaching limit" in warnings[0])
        
        # Case 3: Default model is not allowed, use alternative
        with patch.object(
            self.adapter, 'check_budget',
            return_value=(False, {
                "allowed": False,
                "alternatives": [{
                    "provider": "anthropic",
                    "model": "claude-3-haiku",
                    "savings": 0.0005,
                    "savings_percent": 50.0
                }]
            })
        ):
            # Call method
            provider, model, warnings = self.adapter.route_with_budget_awareness(
                input_text="Test input",
                task_type="test-task",
                default_provider="anthropic",
                default_model="claude-3-sonnet"
            )
            
            # Verify
            self.assertEqual(provider, "anthropic")
            self.assertEqual(model, "claude-3-haiku")
            self.assertTrue(len(warnings) > 0)
            self.assertTrue("Budget limit exceeded" in warnings[0])
        
        # Case 4: Default model not allowed and no alternatives, use free model
        with patch.object(
            self.adapter, 'check_budget',
            return_value=(False, {
                "allowed": False,
                "alternatives": []
            })
        ), patch.object(
            self.adapter, '_get_free_models',
            return_value=[{"provider": "ollama", "model": "llama3"}]
        ):
            # Call method
            provider, model, warnings = self.adapter.route_with_budget_awareness(
                input_text="Test input",
                task_type="test-task",
                default_provider="anthropic",
                default_model="claude-3-sonnet"
            )
            
            # Verify
            self.assertEqual(provider, "ollama")
            self.assertEqual(model, "llama3")
            self.assertTrue(len(warnings) > 0)
            self.assertTrue("Using free model" in warnings[0])
        
        # Case 5: Default model not allowed, no alternatives, no free models
        with patch.object(
            self.adapter, 'check_budget',
            return_value=(False, {
                "allowed": False,
                "alternatives": []
            })
        ), patch.object(
            self.adapter, '_get_free_models',
            return_value=[]
        ):
            # Call method
            provider, model, warnings = self.adapter.route_with_budget_awareness(
                input_text="Test input",
                task_type="test-task",
                default_provider="anthropic",
                default_model="claude-3-sonnet"
            )
            
            # Verify default is used as fallback
            self.assertEqual(provider, "anthropic")
            self.assertEqual(model, "claude-3-sonnet")
            self.assertTrue(len(warnings) > 0)
            self.assertTrue("Budget limit exceeded but no alternatives available" in warnings[0])


if __name__ == '__main__':
    unittest.main()