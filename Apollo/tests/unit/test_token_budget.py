"""
Unit tests for the Token Budget Manager module.
"""

import os
import json
import tempfile
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

import pytest

from apollo.core.token_budget import (
    TokenBudgetManager,
    BudgetTier,
    BudgetPeriod,
    BudgetPolicy,
    BudgetAllocation
)


class TestTokenBudgetManager(unittest.TestCase):
    """Test cases for the TokenBudgetManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create a budget manager
        self.budget_manager = TokenBudgetManager(
            data_dir=self.test_dir
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    async def test_allocate_budget(self):
        """Test allocating a token budget."""
        # Test allocating a budget for a context
        context_id = "test-context-1"
        task_type = "test-task"
        component = "test-component"
        provider = "test-provider"
        model = "test-model"
        priority = 5
        requested_tokens = 1000
        
        # Allocate budget
        allocation = await self.budget_manager.allocate_budget(
            context_id=context_id,
            task_type=task_type,
            component=component,
            provider=provider,
            model=model,
            priority=priority,
            requested_tokens=requested_tokens
        )
        
        # Check allocation
        assert allocation is not None
        assert allocation.context_id == context_id
        assert allocation.task_type == task_type
        assert allocation.component == component
        assert allocation.provider == provider
        assert allocation.model == model
        assert allocation.priority == priority
        assert allocation.allocated_tokens >= requested_tokens
        assert allocation.request_time <= datetime.now()
        assert allocation.expiration > datetime.now()
        
        # Should be tracked in active allocations
        assert context_id in self.budget_manager.active_allocations
        
        # Test allocating another budget for the same context
        allocation2 = await self.budget_manager.allocate_budget(
            context_id=context_id,
            task_type="another-task",
            component=component,
            provider=provider,
            model=model,
            priority=7,  # Higher priority
            requested_tokens=2000  # More tokens
        )
        
        # Check allocation
        assert allocation2 is not None
        assert allocation2.context_id == context_id
        assert allocation2.task_type == "another-task"
        assert allocation2.priority == 7
        assert allocation2.allocated_tokens >= 2000
        
        # Should replace previous allocation
        assert len(self.budget_manager.active_allocations[context_id]) == 2
    
    async def test_get_budget_tier(self):
        """Test determining the budget tier based on model."""
        # Test LOCAL_LIGHTWEIGHT tier
        lightweight_tier = self.budget_manager._get_budget_tier(
            provider="local",
            model="codellama-7b"
        )
        assert lightweight_tier == BudgetTier.LOCAL_LIGHTWEIGHT
        
        # Test LOCAL_MIDWEIGHT tier
        midweight_tier = self.budget_manager._get_budget_tier(
            provider="local",
            model="haiku-2.3"
        )
        assert midweight_tier == BudgetTier.LOCAL_MIDWEIGHT
        
        # Test LOCAL_MIDWEIGHT for unknown local model
        unknown_local_tier = self.budget_manager._get_budget_tier(
            provider="local",
            model="unknown-model"
        )
        assert unknown_local_tier == BudgetTier.LOCAL_MIDWEIGHT
        
        # Test REMOTE_HEAVYWEIGHT tier
        heavyweight_tier = self.budget_manager._get_budget_tier(
            provider="anthropic",
            model="claude-3-opus"
        )
        assert heavyweight_tier == BudgetTier.REMOTE_HEAVYWEIGHT
        
        # Test REMOTE_HEAVYWEIGHT for any remote provider
        remote_tier = self.budget_manager._get_budget_tier(
            provider="openai",
            model="gpt-4"
        )
        assert remote_tier == BudgetTier.REMOTE_HEAVYWEIGHT
    
    async def test_calculate_allocation_size(self):
        """Test calculating allocation size based on task and priority."""
        # Test allocation size for different task types and priorities
        task_allocations = {
            "conversation": {
                BudgetTier.LOCAL_LIGHTWEIGHT: 4000,
                BudgetTier.LOCAL_MIDWEIGHT: 8000,
                BudgetTier.REMOTE_HEAVYWEIGHT: 16000
            },
            "code_completion": {
                BudgetTier.LOCAL_LIGHTWEIGHT: 6000,
                BudgetTier.LOCAL_MIDWEIGHT: 12000,
                BudgetTier.REMOTE_HEAVYWEIGHT: 24000
            },
            "code_analysis": {
                BudgetTier.LOCAL_LIGHTWEIGHT: 8000,
                BudgetTier.LOCAL_MIDWEIGHT: 16000,
                BudgetTier.REMOTE_HEAVYWEIGHT: 32000
            }
        }
        
        # Patch task_allocations
        with patch.object(self.budget_manager, "task_allocations", task_allocations):
            # Test conversation task with normal priority
            conversation_size = self.budget_manager._calculate_allocation_size(
                task_type="conversation",
                tier=BudgetTier.LOCAL_MIDWEIGHT,
                priority=5
            )
            assert conversation_size == 8000
            
            # Test code_completion task with high priority (should get bonus)
            high_priority_size = self.budget_manager._calculate_allocation_size(
                task_type="code_completion",
                tier=BudgetTier.REMOTE_HEAVYWEIGHT,
                priority=9
            )
            # Should get priority bonus
            assert high_priority_size > 24000
            
            # Test unknown task type (should use default)
            unknown_task_size = self.budget_manager._calculate_allocation_size(
                task_type="unknown_task",
                tier=BudgetTier.LOCAL_LIGHTWEIGHT,
                priority=5
            )
            # Should use default allocation
            assert unknown_task_size > 0
    
    async def test_check_budget_limit(self):
        """Test checking budget limits."""
        # Set up a budget policy
        policy = BudgetPolicy(
            tier=BudgetTier.LOCAL_MIDWEIGHT,
            task_type="test-task",
            component="test-component",
            limits={
                BudgetPeriod.HOURLY: 50000,
                BudgetPeriod.DAILY: 200000
            },
            enforcement_level="WARN"
        )
        
        # Add policy to manager
        self.budget_manager.budget_policies.append(policy)
        
        # Track some usage
        component = "test-component"
        tier = BudgetTier.LOCAL_MIDWEIGHT
        task_type = "test-task"
        
        # Add usage that doesn't exceed limits
        self.budget_manager._track_usage(
            component=component,
            tier=tier,
            task_type=task_type,
            tokens=10000
        )
        
        # Check limits
        result = await self.budget_manager._check_budget_limit(
            component=component,
            tier=tier,
            task_type=task_type,
            requested_tokens=5000
        )
        
        # Should be allowed
        assert result["allowed"] is True
        assert result["warnings"] == []
        
        # Add more usage to exceed hourly limit
        self.budget_manager._track_usage(
            component=component,
            tier=tier,
            task_type=task_type,
            tokens=40000
        )
        
        # Check limits again
        result = await self.budget_manager._check_budget_limit(
            component=component,
            tier=tier,
            task_type=task_type,
            requested_tokens=5000
        )
        
        # Should still be allowed (WARN level) but with warning
        assert result["allowed"] is True
        assert len(result["warnings"]) == 1
        assert "hourly" in result["warnings"][0].lower()
    
    async def test_track_usage(self):
        """Test tracking token usage."""
        # Track some usage
        component = "test-component"
        tier = BudgetTier.LOCAL_MIDWEIGHT
        task_type = "test-task"
        
        # Track usage
        self.budget_manager._track_usage(
            component=component,
            tier=tier,
            task_type=task_type,
            tokens=10000
        )
        
        # Check usage tracking
        component_key = f"{component}:{tier.value}:{task_type}"
        
        assert component_key in self.budget_manager.usage_tracking
        assert BudgetPeriod.HOURLY in self.budget_manager.usage_tracking[component_key]
        assert BudgetPeriod.DAILY in self.budget_manager.usage_tracking[component_key]
        assert BudgetPeriod.WEEKLY in self.budget_manager.usage_tracking[component_key]
        assert BudgetPeriod.MONTHLY in self.budget_manager.usage_tracking[component_key]
        
        # Check hourly usage
        hourly_usage = self.budget_manager.usage_tracking[component_key][BudgetPeriod.HOURLY]
        assert hourly_usage["tokens"] == 10000
        assert hourly_usage["last_updated"] <= datetime.now()
        
        # Track more usage
        self.budget_manager._track_usage(
            component=component,
            tier=tier,
            task_type=task_type,
            tokens=5000
        )
        
        # Check updated usage
        hourly_usage = self.budget_manager.usage_tracking[component_key][BudgetPeriod.HOURLY]
        assert hourly_usage["tokens"] == 15000
    
    async def test_save_load_usage(self):
        """Test saving and loading usage data."""
        # Track some usage
        component = "test-component"
        tier = BudgetTier.LOCAL_MIDWEIGHT
        task_type = "test-task"
        
        # Track usage
        self.budget_manager._track_usage(
            component=component,
            tier=tier,
            task_type=task_type,
            tokens=10000
        )
        
        # Save usage
        await self.budget_manager._save_usage_data()
        
        # Check that file was created
        usage_file = os.path.join(self.test_dir, "usage_tracking.json")
        assert os.path.exists(usage_file)
        
        # Create a new budget manager to load data
        new_manager = TokenBudgetManager(
            data_dir=self.test_dir
        )
        
        # Load usage data
        await new_manager._load_usage_data()
        
        # Check that data was loaded
        component_key = f"{component}:{tier.value}:{task_type}"
        assert component_key in new_manager.usage_tracking
        assert BudgetPeriod.HOURLY in new_manager.usage_tracking[component_key]
        
        # Check hourly usage
        hourly_usage = new_manager.usage_tracking[component_key][BudgetPeriod.HOURLY]
        assert hourly_usage["tokens"] == 10000
    
    async def test_expire_allocation(self):
        """Test allocation expiration."""
        # Allocate a budget with short expiration
        context_id = "test-context-expire"
        allocation = BudgetAllocation(
            context_id=context_id,
            task_type="test-task",
            component="test-component",
            provider="test-provider",
            model="test-model",
            tier=BudgetTier.LOCAL_MIDWEIGHT,
            priority=5,
            requested_tokens=1000,
            allocated_tokens=1000,
            policy=BudgetPolicy(
                tier=BudgetTier.LOCAL_MIDWEIGHT,
                task_type="test-task",
                component="test-component",
                limits={},
                enforcement_level="WARN"
            ),
            request_time=datetime.now(),
            expiration=datetime.now() + timedelta(seconds=0.1)  # Very short expiration
        )
        
        # Add to active allocations
        self.budget_manager.active_allocations[context_id] = [allocation]
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Check if expired
        is_expired = await self.budget_manager.is_allocation_expired(context_id)
        assert is_expired is True
        
        # Run cleanup
        await self.budget_manager._cleanup_expired_allocations()
        
        # Should be removed from active allocations
        assert context_id not in self.budget_manager.active_allocations


# Run tests using pytest
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])