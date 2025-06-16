"""
Budget Allocation System

This module provides functionality for allocating and tracking token and cost budgets.
It is responsible for creating budget allocations, tracking usage against those
allocations, and enforcing allocation limits.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import models and constants
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    BudgetAllocation, UsageRecord
)
from budget.core.constants import (
    DEFAULT_TOKEN_LIMITS, DEFAULT_ALLOCATIONS, 
    DEFAULT_MODEL_TIERS, DEFAULT_PROVIDER_TIERS
)

# Import repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo,
    alert_repo, pricing_repo
)


class AllocationManager:
    """
    Manages token and cost budget allocations.
    
    This class is responsible for creating allocations, tracking usage,
    and enforcing allocation limits.
    """
    
    def __init__(self):
        """Initialize the allocation manager."""
        # Default tier mappings
        self.model_tiers = DEFAULT_MODEL_TIERS
        self.provider_tiers = DEFAULT_PROVIDER_TIERS
        self.component_tiers = {}  # Will be populated during runtime
        
    @log_function()
    def determine_tier(
        self, 
        component: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> BudgetTier:
        """
        Determine the appropriate budget tier based on component, provider, and model.
        
        Args:
            component: Component ID
            provider: Provider ID
            model: Model ID
            
        Returns:
            BudgetTier
        """
        # Check if model has a specific tier
        if model and model.lower() in self.model_tiers:
            tier_value = self.model_tiers[model.lower()]
            debug_log.debug("budget_allocation", 
                           f"Determined tier for model {model}: {tier_value}")
            return BudgetTier(tier_value)
            
        # Check if component has a specific tier
        if component and component in self.component_tiers:
            tier_value = self.component_tiers[component]
            debug_log.debug("budget_allocation", 
                           f"Determined tier for component {component}: {tier_value}")
            return BudgetTier(tier_value)
            
        # Check if provider has a default tier
        if provider and provider.lower() in self.provider_tiers:
            tier_value = self.provider_tiers[provider.lower()]
            debug_log.debug("budget_allocation", 
                           f"Determined tier for provider {provider}: {tier_value}")
            return BudgetTier(tier_value)
            
        # Default to remote heavyweight (most conservative)
        debug_log.debug("budget_allocation", 
                       "No specific tier found, defaulting to REMOTE_HEAVYWEIGHT")
        return BudgetTier.REMOTE_HEAVYWEIGHT
        
    @log_function()
    def get_default_allocation(
        self,
        task_type: str,
        priority: int
    ) -> int:
        """
        Get the default token allocation for a task type and priority.
        
        Args:
            task_type: Type of task (default, chat, coding, etc.)
            priority: Task priority (1-10)
            
        Returns:
            Default token allocation
        """
        # Check if we have defaults for this task type
        if task_type in DEFAULT_ALLOCATIONS:
            # Try to get allocation for specific priority
            if priority in DEFAULT_ALLOCATIONS[task_type]:
                allocation = DEFAULT_ALLOCATIONS[task_type][priority]
                debug_log.debug("budget_allocation", 
                              f"Default allocation for {task_type}/{priority}: {allocation}")
                return allocation
            
            # Fall back to normal priority
            allocation = DEFAULT_ALLOCATIONS[task_type][5]  # NORMAL priority
            debug_log.debug("budget_allocation", 
                          f"Default allocation for {task_type}/NORMAL: {allocation}")
            return allocation
        
        # Fall back to default task type
        if priority in DEFAULT_ALLOCATIONS["default"]:
            allocation = DEFAULT_ALLOCATIONS["default"][priority]
        else:
            allocation = DEFAULT_ALLOCATIONS["default"][5]  # NORMAL priority
            
        debug_log.debug("budget_allocation", 
                       f"Default fallback allocation: {allocation}")
        return allocation
        
    @log_function()
    def estimate_cost(
        self,
        provider: str,
        model: str,
        tokens: int,
        input_ratio: float = 0.25  # Default: 25% of tokens are input
    ) -> float:
        """
        Estimate the cost for a token allocation.
        
        Args:
            provider: Provider name
            model: Model name
            tokens: Total tokens to estimate cost for
            input_ratio: Ratio of input tokens to total tokens
            
        Returns:
            Estimated cost in USD
        """
        # Get current pricing
        pricing = pricing_repo.get_current_pricing(provider, model)
        
        if not pricing:
            debug_log.warn("budget_allocation", 
                          f"No pricing found for {provider}/{model}, assuming zero cost")
            return 0.0
            
        # Calculate estimated input and output tokens
        input_tokens = int(tokens * input_ratio)
        output_tokens = tokens - input_tokens
        
        # Calculate costs
        input_cost = input_tokens * pricing.input_cost_per_token
        output_cost = output_tokens * pricing.output_cost_per_token
        total_cost = input_cost + output_cost
        
        debug_log.debug("budget_allocation", 
                      f"Estimated cost for {tokens} tokens ({provider}/{model}): ${total_cost:.6f}")
        
        return total_cost
        
    @log_function()
    def allocate_budget(
        self,
        context_id: str,
        component: str,
        task_type: str = "default",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        priority: int = 5,
        token_count: Optional[int] = None,
        budget_id: Optional[str] = None,
        expiration: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[BudgetAllocation]:
        """
        Allocate a token budget for an LLM operation.
        
        Args:
            context_id: Context identifier
            component: Component ID
            task_type: Task type
            provider: Provider ID (optional)
            model: Model ID (optional)
            priority: Task priority (1-10)
            token_count: Requested token count (optional)
            budget_id: Budget ID to allocate from (optional)
            expiration: Expiration time (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            BudgetAllocation or None if allocation failed
        """
        debug_log.info("budget_allocation", 
                     f"Allocating budget for context {context_id}, component {component}, "
                     f"task_type {task_type}, priority {priority}")
        
        # Determine tier based on component, provider, and model
        tier = self.determine_tier(component, provider, model)
        
        # Determine token count if not specified
        if token_count is None:
            token_count = self.get_default_allocation(task_type, priority)
            
        # Check if there are any hard-limit policies that would be exceeded
        policies = policy_repo.get_active_policies(
            tier=tier,
            provider=provider,
            component=component,
            task_type=task_type
        )
        
        # Filter policies by type HARD_LIMIT
        hard_limit_policies = [
            p for p in policies 
            if p.type == BudgetPolicyType.HARD_LIMIT
        ]
        
        # Check if any hard limits would be exceeded
        hard_limit_exceeded = False
        for policy in hard_limit_policies:
            # Skip if policy doesn't apply to this budget
            if budget_id and policy.budget_id and policy.budget_id != budget_id:
                continue
                
            # Get current period usage
            period_usage = usage_repo.get_usage_summary(
                period=policy.period,
                budget_id=budget_id if policy.budget_id else None,
                provider=provider if policy.provider else None,
                component=component if policy.component else None,
                task_type=task_type if policy.task_type else None
            )
            
            # Check if adding this allocation would exceed the limit
            if policy.token_limit:
                current_usage = period_usage["total_tokens"]
                if current_usage + token_count > policy.token_limit:
                    hard_limit_exceeded = True
                    debug_log.warn("budget_allocation", 
                                  f"Hard token limit exceeded for {tier} "
                                  f"(current: {current_usage}, "
                                  f"adding: {token_count}, limit: {policy.token_limit})")
                    break
                    
            # Check cost limit if applicable
            if policy.cost_limit and provider and model:
                current_cost = period_usage["total_cost"]
                estimated_cost = self.estimate_cost(provider, model, token_count)
                
                if current_cost + estimated_cost > policy.cost_limit:
                    hard_limit_exceeded = True
                    debug_log.warn("budget_allocation", 
                                 f"Hard cost limit exceeded for {tier} "
                                 f"(current: ${current_cost:.2f}, "
                                 f"adding: ${estimated_cost:.2f}, "
                                 f"limit: ${policy.cost_limit:.2f})")
                    break
        
        # Enforce hard limits unless this is a critical priority task
        if hard_limit_exceeded and priority < 10:  # Not CRITICAL
            debug_log.warn("budget_allocation", 
                          f"Budget hard limit exceeded for {tier}, allocation denied")
            return None
            
        # Estimate cost if possible
        estimated_cost = 0.0
        if provider and model:
            estimated_cost = self.estimate_cost(provider, model, token_count)
            
        # Create allocation
        allocation = BudgetAllocation(
            allocation_id=str(uuid.uuid4()),
            budget_id=budget_id,
            context_id=context_id,
            component=component,
            tier=tier,
            provider=provider,
            model=model,
            task_type=task_type,
            priority=priority,
            tokens_allocated=token_count,
            tokens_used=0,
            input_tokens_used=0,
            output_tokens_used=0,
            estimated_cost=estimated_cost,
            actual_cost=0.0,
            creation_time=datetime.now(),
            expiration_time=expiration,
            is_active=True,
            metadata=metadata or {}
        )
        
        # Save to repository
        saved_allocation = allocation_repo.create(allocation)
        
        debug_log.info("budget_allocation", 
                     f"Created allocation {saved_allocation.allocation_id} "
                     f"with {token_count} tokens and estimated cost ${estimated_cost:.4f}")
        
        return saved_allocation
        
    @log_function()
    def record_usage(
        self,
        context_id: str,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        model: str,
        component: str,
        task_type: str = "default",
        operation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[UsageRecord, Optional[BudgetAllocation]]:
        """
        Record token and cost usage.
        
        Args:
            context_id: Context identifier
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            provider: Provider name
            model: Model name
            component: Component name
            task_type: Task type
            operation_id: Operation identifier (optional)
            request_id: Request identifier (optional)
            user_id: User identifier (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Tuple of (UsageRecord, updated BudgetAllocation or None)
        """
        debug_log.info("budget_allocation", 
                     f"Recording usage for context {context_id}: "
                     f"{input_tokens} input + {output_tokens} output tokens "
                     f"({provider}/{model})")
        
        # Calculate cost
        pricing = pricing_repo.get_current_pricing(provider, model)
        
        input_cost = 0.0
        output_cost = 0.0
        total_cost = 0.0
        pricing_version = None
        
        if pricing:
            input_cost = input_tokens * pricing.input_cost_per_token
            output_cost = output_tokens * pricing.output_cost_per_token
            total_cost = input_cost + output_cost
            pricing_version = pricing.version
            
            debug_log.debug("budget_allocation", 
                          f"Calculated cost: ${total_cost:.6f} "
                          f"(input: ${input_cost:.6f}, output: ${output_cost:.6f})")
        else:
            debug_log.warn("budget_allocation", 
                          f"No pricing found for {provider}/{model}, assuming zero cost")
            
        # Create usage record
        usage_record = UsageRecord(
            record_id=str(uuid.uuid4()),
            context_id=context_id,
            component=component,
            provider=provider,
            model=model,
            task_type=task_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            pricing_version=pricing_version,
            timestamp=datetime.now(),
            operation_id=operation_id,
            request_id=request_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        # Save usage record
        saved_record = usage_repo.create(usage_record)
        
        # Try to find an active allocation for this context
        allocation = allocation_repo.get_by_context_id(context_id)
        
        # If allocation exists, update its usage
        if allocation:
            debug_log.debug("budget_allocation", 
                          f"Updating existing allocation {allocation.allocation_id}")
                          
            updated_allocation = allocation_repo.update_usage(
                allocation_id=allocation.allocation_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=total_cost
            )
            
            if updated_allocation:
                debug_log.info("budget_allocation", 
                             f"Updated allocation {updated_allocation.allocation_id}: "
                             f"{updated_allocation.tokens_used}/{updated_allocation.tokens_allocated} "
                             f"tokens used (${updated_allocation.actual_cost:.4f})")
                             
                # Link usage record to allocation
                saved_record.allocation_id = updated_allocation.allocation_id
                usage_repo.update(saved_record)
            else:
                debug_log.warn("budget_allocation", 
                              f"Failed to update allocation {allocation.allocation_id}")
                
            return saved_record, updated_allocation
            
        # No allocation found, just return the usage record
        debug_log.info("budget_allocation", 
                     f"No active allocation found for context {context_id}")
        return saved_record, None
        
    @log_function()
    def check_budget(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        component: str,
        task_type: str = "default",
        budget_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is within budget limits.
        
        Args:
            provider: Provider name
            model: Model name
            input_tokens: Input tokens for the request
            component: Component name
            task_type: Task type
            budget_id: Budget ID to check against (optional)
            
        Returns:
            Tuple of (True if allowed, info dict with details)
        """
        debug_log.info("budget_allocation", 
                     f"Checking budget for {provider}/{model}, "
                     f"{input_tokens} input tokens, component {component}")
        
        # Determine tier
        tier = self.determine_tier(component, provider, model)
        
        # Estimate output tokens (typically 4x input for chat/completion)
        estimated_output = input_tokens * 4
        
        # Estimate total tokens
        total_tokens = input_tokens + estimated_output
        
        # Estimate cost
        estimated_cost = self.estimate_cost(
            provider=provider,
            model=model,
            tokens=total_tokens,
            input_ratio=input_tokens / total_tokens
        )
        
        # If cost is 0, always allow
        if estimated_cost == 0:
            return True, {
                "allowed": True,
                "reason": "Free model",
                "tier": tier.value,
                "estimated_cost": 0.0,
                "estimated_tokens": total_tokens
            }
            
        # Get active policies
        policies = policy_repo.get_active_policies(
            tier=tier,
            provider=provider,
            component=component,
            task_type=task_type
        )
        
        # Filter policies by budget ID if specified
        if budget_id:
            policies = [p for p in policies if not p.budget_id or p.budget_id == budget_id]
            
        # Check periods in order (most restrictive first)
        for period in [BudgetPeriod.HOURLY, BudgetPeriod.DAILY, 
                      BudgetPeriod.WEEKLY, BudgetPeriod.MONTHLY]:
                      
            # Get policies for this period
            period_policies = [p for p in policies if p.period == period]
            
            # Skip if no policies for this period
            if not period_policies:
                continue
                
            # Get current usage
            period_usage = usage_repo.get_usage_summary(
                period=period,
                budget_id=budget_id,
                provider=provider,
                component=component,
                task_type=task_type
            )
            
            current_tokens = period_usage["total_tokens"]
            current_cost = period_usage["total_cost"]
            
            # Check each policy
            for policy in period_policies:
                # Check token limit
                if policy.token_limit and current_tokens + total_tokens > policy.token_limit:
                    if policy.type == BudgetPolicyType.HARD_LIMIT:
                        return False, {
                            "allowed": False,
                            "reason": f"{period.value.capitalize()} token limit exceeded",
                            "policy_type": policy.type.value,
                            "limit": policy.token_limit,
                            "usage": current_tokens,
                            "estimated_additional": total_tokens,
                            "tier": tier.value,
                            "period": period.value
                        }
                    elif policy.type == BudgetPolicyType.SOFT_LIMIT:
                        debug_log.warn("budget_allocation", 
                                      f"{period.value.capitalize()} token soft limit will be exceeded: "
                                      f"{current_tokens} + {total_tokens} > {policy.token_limit}")
                        
                # Check cost limit
                if policy.cost_limit and current_cost + estimated_cost > policy.cost_limit:
                    if policy.type == BudgetPolicyType.HARD_LIMIT:
                        return False, {
                            "allowed": False,
                            "reason": f"{period.value.capitalize()} cost limit exceeded",
                            "policy_type": policy.type.value,
                            "limit": policy.cost_limit,
                            "usage": current_cost,
                            "estimated_additional": estimated_cost,
                            "tier": tier.value,
                            "period": period.value
                        }
                    elif policy.type == BudgetPolicyType.SOFT_LIMIT:
                        debug_log.warn("budget_allocation", 
                                      f"{period.value.capitalize()} cost soft limit will be exceeded: "
                                      f"${current_cost:.2f} + ${estimated_cost:.2f} > ${policy.cost_limit:.2f}")
        
        # If we get here, request is allowed
        return True, {
            "allowed": True,
            "tier": tier.value,
            "estimated_cost": estimated_cost,
            "estimated_tokens": total_tokens
        }
        
    @log_function()
    def set_component_tier(self, component: str, tier: Union[str, BudgetTier]) -> bool:
        """
        Set the budget tier for a component.
        
        Args:
            component: Component identifier
            tier: Budget tier
            
        Returns:
            True if successful
        """
        if isinstance(tier, str):
            try:
                tier = BudgetTier(tier)
            except ValueError:
                debug_log.error("budget_allocation", f"Invalid tier: {tier}")
                return False
                
        self.component_tiers[component] = tier.value
        debug_log.info("budget_allocation", f"Set tier for {component} to {tier.value}")
        return True


# Create singleton instance
allocation_manager = AllocationManager()