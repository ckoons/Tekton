"""
Budget Engine Core

This module contains the core budget management engine for the Budget component.
It provides budget creation, policy management, and reporting functionality.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from landmarks import architecture_decision, performance_boundary, danger_zone

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
    Budget, BudgetPolicy, BudgetSummary, Alert
)
from budget.core.constants import (
    DEFAULT_TOKEN_LIMITS, DEFAULT_COST_LIMITS, 
    ALERT_THRESHOLDS
)

# Import repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo,
    alert_repo, pricing_repo
)

# Import allocation manager
from budget.core.allocation import allocation_manager


@architecture_decision(
    title="Policy-based budget enforcement",
    rationale="Use flexible policy system with tiers, periods, and thresholds for granular budget control",
    alternatives_considered=["Hard limits only", "Manual approval process", "Post-hoc billing"])
@danger_zone(
    title="Budget enforcement logic",
    risk_level="high",
    risks=["Service interruption", "Incorrect cost calculation", "Policy bypass"],
    mitigations=["Warning thresholds", "Override mechanisms", "Audit logging"],
    review_required=True
)
class BudgetEngine:
    """
    Core budget management engine.
    
    This class provides functionality for creating and managing budgets,
    setting policies, and generating reports.
    """
    
    def __init__(self):
        """Initialize the budget engine."""
        pass
        
    @log_function()
    def create_budget(
        self,
        name: str,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Budget:
        """
        Create a new budget.
        
        Args:
            name: Budget name
            description: Budget description
            owner: Budget owner
            metadata: Additional metadata
            
        Returns:
            Created budget
        """
        debug_log.info("budget_engine", f"Creating budget: {name}")
        
        # Create budget entity
        budget = Budget(
            budget_id=str(uuid.uuid4()),
            name=name,
            description=description,
            owner=owner,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
            metadata=metadata or {}
        )
        
        # Save to repository
        saved_budget = budget_repo.create(budget)
        
        debug_log.info("budget_engine", f"Created budget {saved_budget.budget_id}: {name}")
        
        return saved_budget
        
    @log_function()
    def create_default_policies(
        self,
        budget_id: str,
        token_limits: Optional[Dict[str, Dict[str, int]]] = None,
        cost_limits: Optional[Dict[str, float]] = None
    ) -> List[BudgetPolicy]:
        """
        Create default policies for a budget.
        
        Args:
            budget_id: Budget ID
            token_limits: Custom token limits by tier and period (optional)
            cost_limits: Custom cost limits by period (optional)
            
        Returns:
            List of created policies
        """
        debug_log.info("budget_engine", f"Creating default policies for budget {budget_id}")
        
        # Use default limits if not provided
        token_limits = token_limits or DEFAULT_TOKEN_LIMITS
        cost_limits = cost_limits or DEFAULT_COST_LIMITS
        
        # Get budget
        budget = budget_repo.get_by_id(budget_id)
        if not budget:
            debug_log.error("budget_engine", f"Budget {budget_id} not found")
            return []
            
        created_policies = []
        
        # Create token-based policies for each tier and period
        for tier, limits in token_limits.items():
            for period, limit in limits.items():
                policy = BudgetPolicy(
                    policy_id=str(uuid.uuid4()),
                    budget_id=budget_id,
                    type=BudgetPolicyType.WARN,
                    period=BudgetPeriod(period),
                    tier=BudgetTier(tier),
                    token_limit=limit,
                    warning_threshold=ALERT_THRESHOLDS["warning"],
                    action_threshold=ALERT_THRESHOLDS["critical"],
                    start_date=datetime.now(),
                    enabled=True
                )
                
                # Save to repository
                saved_policy = policy_repo.create(policy)
                created_policies.append(saved_policy)
                
                debug_log.debug("budget_engine", 
                               f"Created token policy for {tier}/{period}: "
                               f"{limit} tokens (budget: {budget_id})")
        
        # Create cost-based policies for each period
        for period, limit in cost_limits.items():
            policy = BudgetPolicy(
                policy_id=str(uuid.uuid4()),
                budget_id=budget_id,
                type=BudgetPolicyType.WARN,
                period=BudgetPeriod(period),
                cost_limit=limit,
                warning_threshold=ALERT_THRESHOLDS["warning"],
                action_threshold=ALERT_THRESHOLDS["critical"],
                start_date=datetime.now(),
                enabled=True
            )
            
            # Save to repository
            saved_policy = policy_repo.create(policy)
            created_policies.append(saved_policy)
            
            debug_log.debug("budget_engine", 
                           f"Created cost policy for {period}: "
                           f"${limit} (budget: {budget_id})")
                           
        # Update budget with policy IDs
        budget.policies = [p.policy_id for p in created_policies]
        budget_repo.update(budget)
        
        debug_log.info("budget_engine", 
                      f"Created {len(created_policies)} default policies for budget {budget_id}")
        
        return created_policies
        
    @log_function()
    def set_policy(
        self,
        budget_id: Optional[str] = None,
        period: Union[str, BudgetPeriod] = BudgetPeriod.DAILY,
        token_limit: Optional[int] = None,
        cost_limit: Optional[float] = None,
        tier: Optional[Union[str, BudgetTier]] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        task_type: Optional[str] = None,
        policy_type: Union[str, BudgetPolicyType] = BudgetPolicyType.WARN,
        enabled: bool = True
    ) -> BudgetPolicy:
        """
        Create or update a budget policy.
        
        Args:
            budget_id: Budget ID (optional)
            period: Budget period
            token_limit: Token limit (required if cost_limit not provided)
            cost_limit: Cost limit (required if token_limit not provided)
            tier: Budget tier (optional)
            provider: Provider name (optional)
            component: Component name (optional)
            task_type: Task type (optional)
            policy_type: Policy type (warn, hard_limit, etc.)
            enabled: Whether the policy is enabled
            
        Returns:
            Created or updated policy
        """
        debug_log.info("budget_engine", f"Setting {period} policy for budget {budget_id}")
        
        # Convert string values to enums
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        if isinstance(tier, str) and tier:
            tier = BudgetTier(tier)
            
        if isinstance(policy_type, str):
            policy_type = BudgetPolicyType(policy_type)
            
        # Ensure either token_limit or cost_limit is provided
        if token_limit is None and cost_limit is None:
            debug_log.error("budget_engine", "Either token_limit or cost_limit must be provided")
            raise ValueError("Either token_limit or cost_limit must be provided")
            
        # Try to find existing policy with same criteria
        existing_policy = None
        
        existing_policies = policy_repo.get_active_policies(
            tier=tier,
            provider=provider,
            component=component,
            task_type=task_type
        )
        
        for policy in existing_policies:
            if policy.period == period and policy.budget_id == budget_id:
                # Found matching policy
                existing_policy = policy
                break
                
        if existing_policy:
            # Update existing policy
            debug_log.debug("budget_engine", 
                          f"Updating existing policy {existing_policy.policy_id}")
            
            # Update fields
            if token_limit is not None:
                existing_policy.token_limit = token_limit
            if cost_limit is not None:
                existing_policy.cost_limit = cost_limit
                
            existing_policy.type = policy_type
            existing_policy.enabled = enabled
            existing_policy.updated_at = datetime.now()
            
            # Save to repository
            updated_policy = policy_repo.update(existing_policy)
            
            debug_log.info("budget_engine", 
                         f"Updated policy {updated_policy.policy_id} for {period}")
            
            return updated_policy
            
        else:
            # Create new policy
            debug_log.debug("budget_engine", "Creating new policy")
            
            policy = BudgetPolicy(
                policy_id=str(uuid.uuid4()),
                budget_id=budget_id,
                type=policy_type,
                period=period,
                tier=tier,
                provider=provider,
                component=component,
                task_type=task_type,
                token_limit=token_limit,
                cost_limit=cost_limit,
                warning_threshold=ALERT_THRESHOLDS["warning"],
                action_threshold=ALERT_THRESHOLDS["critical"],
                start_date=datetime.now(),
                enabled=enabled
            )
            
            # Save to repository
            saved_policy = policy_repo.create(policy)
            
            # If budget_id provided, add policy to budget
            if budget_id:
                budget = budget_repo.get_by_id(budget_id)
                if budget:
                    budget.policies.append(saved_policy.policy_id)
                    budget_repo.update(budget)
                    
            debug_log.info("budget_engine", 
                         f"Created new policy {saved_policy.policy_id} for {period}")
            
            return saved_policy
            
    @log_function()
    def disable_policy(self, policy_id: str) -> bool:
        """
        Disable a budget policy.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            True if successful
        """
        debug_log.info("budget_engine", f"Disabling policy {policy_id}")
        
        # Get policy
        policy = policy_repo.get_by_id(policy_id)
        if not policy:
            debug_log.error("budget_engine", f"Policy {policy_id} not found")
            return False
            
        # Disable policy
        policy.enabled = False
        policy_repo.update(policy)
        
        debug_log.info("budget_engine", f"Disabled policy {policy_id}")
        
        return True
        
    @log_function()
    def get_budget_summary(
        self,
        budget_id: Optional[str] = None,
        period: Union[str, BudgetPeriod] = BudgetPeriod.DAILY,
        tier: Optional[Union[str, BudgetTier]] = None,
        provider: Optional[str] = None,
        component: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[BudgetSummary]:
        """
        Get a summary of budget usage.
        
        Args:
            budget_id: Budget ID (optional)
            period: Budget period
            tier: Budget tier (optional)
            provider: Provider name (optional)
            component: Component name (optional)
            task_type: Task type (optional)
            
        Returns:
            List of budget summaries
        """
        debug_log.info("budget_engine", 
                     f"Getting budget summary for {period} period")
        
        # Convert string values to enums
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        if isinstance(tier, str) and tier:
            tier = BudgetTier(tier)
            
        # Get relevant policies
        policies = policy_repo.get_active_policies(
            tier=tier,
            provider=provider,
            component=component,
            task_type=task_type
        )
        
        # Filter by budget_id if provided
        if budget_id:
            policies = [p for p in policies if not p.budget_id or p.budget_id == budget_id]
            
        # Filter by period
        policies = [p for p in policies if p.period == period]
        
        if not policies:
            debug_log.debug("budget_engine", 
                           f"No active policies found for {period} period")
            return []
            
        # Calculate time range for period
        now = datetime.now()
        if period == BudgetPeriod.HOURLY:
            start_time = now.replace(minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
        elif period == BudgetPeriod.DAILY:
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            # Start of week (Monday)
            start_time = now - timedelta(days=now.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=7)
        elif period == BudgetPeriod.MONTHLY:
            # Start of month
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # End of month (start of next month)
            if now.month == 12:
                end_time = datetime(now.year + 1, 1, 1)
            else:
                end_time = datetime(now.year, now.month + 1, 1)
        else:
            # Unsupported period for summary
            debug_log.warn("budget_engine", 
                          f"Unsupported period for summary: {period}")
            return []
            
        # Get usage summary
        usage_summary = usage_repo.get_usage_summary(
            period=period,
            budget_id=budget_id,
            provider=provider,
            component=component,
            task_type=task_type
        )
        
        # Get active allocations
        active_allocations = allocation_repo.get_active_allocations(
            budget_id=budget_id,
            component=component,
            tier=tier,
            provider=provider,
            task_type=task_type
        )
        
        # Create summaries for each policy
        summaries = []
        
        for policy in policies:
            # Create summary
            summary = BudgetSummary(
                budget_id=policy.budget_id,
                period=period,
                tier=policy.tier,
                provider=policy.provider,
                component=policy.component,
                task_type=policy.task_type,
                
                # Token tracking
                total_tokens_allocated=sum(a.tokens_allocated for a in active_allocations 
                                          if self._allocation_matches_policy(a, policy)),
                total_tokens_used=usage_summary["total_tokens"],
                token_limit=policy.token_limit,
                token_usage_percentage=(usage_summary["total_tokens"] / policy.token_limit 
                                       if policy.token_limit else None),
                
                # Cost tracking
                total_cost=usage_summary["total_cost"],
                cost_limit=policy.cost_limit,
                cost_usage_percentage=(usage_summary["total_cost"] / policy.cost_limit 
                                      if policy.cost_limit else None),
                
                # Period metrics
                active_allocations=len([a for a in active_allocations 
                                      if self._allocation_matches_policy(a, policy)]),
                start_time=start_time,
                end_time=end_time
            )
            
            summaries.append(summary)
            
        debug_log.info("budget_engine", 
                     f"Generated {len(summaries)} summaries for {period} period")
        
        return summaries
        
    def _allocation_matches_policy(self, allocation, policy):
        """
        Check if an allocation matches a policy.
        
        Args:
            allocation: Budget allocation
            policy: Budget policy
            
        Returns:
            True if allocation matches policy criteria
        """
        # Check tier
        if policy.tier and allocation.tier != policy.tier:
            return False
            
        # Check provider
        if policy.provider and allocation.provider != policy.provider:
            return False
            
        # Check component
        if policy.component and allocation.component != policy.component:
            return False
            
        # Check task_type
        if policy.task_type and allocation.task_type != policy.task_type:
            return False
            
        # Check budget_id
        if policy.budget_id and allocation.budget_id != policy.budget_id:
            return False
            
        return True
        
    @log_function()
    def check_and_create_alerts(
        self,
        budget_id: Optional[str] = None,
        period: Optional[Union[str, BudgetPeriod]] = None
    ) -> List[Alert]:
        """
        Check for budget violations and create alerts.
        
        Args:
            budget_id: Budget ID (optional)
            period: Budget period (optional, checks all periods if not provided)
            
        Returns:
            List of created alerts
        """
        debug_log.info("budget_engine", "Checking for budget violations")
        
        # Convert string values to enums
        if isinstance(period, str) and period:
            period = BudgetPeriod(period)
            
        # Determine periods to check
        periods = [period] if period else list(BudgetPeriod)
        
        # Exclude PER_SESSION and PER_TASK
        periods = [p for p in periods if p not in 
                  [BudgetPeriod.PER_SESSION, BudgetPeriod.PER_TASK]]
        
        created_alerts = []
        
        # Check each period
        for period in periods:
            # Get summaries for this period
            summaries = self.get_budget_summary(
                budget_id=budget_id,
                period=period
            )
            
            for summary in summaries:
                # Check token limit if applicable
                if summary.token_limit and summary.token_usage_percentage:
                    # Check if token limit is exceeded
                    if summary.token_usage_percentage > 1.0:
                        # Create alert for token limit exceeded
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            budget_id=summary.budget_id,
                            severity="error",
                            type="token_limit_exceeded",
                            message=f"{period.value.capitalize()} token budget exceeded",
                            details={
                                "period": period.value,
                                "tier": summary.tier.value if summary.tier else None,
                                "provider": summary.provider,
                                "component": summary.component,
                                "task_type": summary.task_type,
                                "token_limit": summary.token_limit,
                                "tokens_used": summary.total_tokens_used,
                                "usage_percentage": summary.token_usage_percentage
                            },
                            timestamp=datetime.now()
                        )
                        
                        # Save to repository
                        saved_alert = alert_repo.create(alert)
                        created_alerts.append(saved_alert)
                        
                        debug_log.warn("budget_engine", 
                                     f"Token limit exceeded for {period.value}: "
                                     f"{summary.total_tokens_used}/{summary.token_limit} "
                                     f"({summary.token_usage_percentage:.2%})")
                                     
                    # Check if approaching warning threshold
                    elif (summary.token_usage_percentage > ALERT_THRESHOLDS["warning"] and
                         summary.token_usage_percentage < 1.0):
                        # Create alert for approaching token limit
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            budget_id=summary.budget_id,
                            severity="warning",
                            type="token_limit_approaching",
                            message=f"{period.value.capitalize()} token budget approaching limit",
                            details={
                                "period": period.value,
                                "tier": summary.tier.value if summary.tier else None,
                                "provider": summary.provider,
                                "component": summary.component,
                                "task_type": summary.task_type,
                                "token_limit": summary.token_limit,
                                "tokens_used": summary.total_tokens_used,
                                "usage_percentage": summary.token_usage_percentage
                            },
                            timestamp=datetime.now()
                        )
                        
                        # Save to repository
                        saved_alert = alert_repo.create(alert)
                        created_alerts.append(saved_alert)
                        
                        debug_log.info("budget_engine", 
                                     f"Approaching token limit for {period.value}: "
                                     f"{summary.total_tokens_used}/{summary.token_limit} "
                                     f"({summary.token_usage_percentage:.2%})")
                
                # Check cost limit if applicable
                if summary.cost_limit and summary.cost_usage_percentage:
                    # Check if cost limit is exceeded
                    if summary.cost_usage_percentage > 1.0:
                        # Create alert for cost limit exceeded
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            budget_id=summary.budget_id,
                            severity="error",
                            type="cost_limit_exceeded",
                            message=f"{period.value.capitalize()} cost budget exceeded",
                            details={
                                "period": period.value,
                                "tier": summary.tier.value if summary.tier else None,
                                "provider": summary.provider,
                                "component": summary.component,
                                "task_type": summary.task_type,
                                "cost_limit": summary.cost_limit,
                                "cost_used": summary.total_cost,
                                "usage_percentage": summary.cost_usage_percentage
                            },
                            timestamp=datetime.now()
                        )
                        
                        # Save to repository
                        saved_alert = alert_repo.create(alert)
                        created_alerts.append(saved_alert)
                        
                        debug_log.warn("budget_engine", 
                                     f"Cost limit exceeded for {period.value}: "
                                     f"${summary.total_cost:.2f}/${summary.cost_limit:.2f} "
                                     f"({summary.cost_usage_percentage:.2%})")
                                     
                    # Check if approaching warning threshold
                    elif (summary.cost_usage_percentage > ALERT_THRESHOLDS["warning"] and
                         summary.cost_usage_percentage < 1.0):
                        # Create alert for approaching cost limit
                        alert = Alert(
                            alert_id=str(uuid.uuid4()),
                            budget_id=summary.budget_id,
                            severity="warning",
                            type="cost_limit_approaching",
                            message=f"{period.value.capitalize()} cost budget approaching limit",
                            details={
                                "period": period.value,
                                "tier": summary.tier.value if summary.tier else None,
                                "provider": summary.provider,
                                "component": summary.component,
                                "task_type": summary.task_type,
                                "cost_limit": summary.cost_limit,
                                "cost_used": summary.total_cost,
                                "usage_percentage": summary.cost_usage_percentage
                            },
                            timestamp=datetime.now()
                        )
                        
                        # Save to repository
                        saved_alert = alert_repo.create(alert)
                        created_alerts.append(saved_alert)
                        
                        debug_log.info("budget_engine", 
                                     f"Approaching cost limit for {period.value}: "
                                     f"${summary.total_cost:.2f}/${summary.cost_limit:.2f} "
                                     f"({summary.cost_usage_percentage:.2%})")
                        
        debug_log.info("budget_engine", 
                     f"Created {len(created_alerts)} alerts for budget violations")
        
        return created_alerts
        
    @log_function()
    def get_model_recommendations(
        self,
        provider: str,
        model: str,
        task_type: str = "default",
        context_size: int = 4000
    ) -> List[Dict[str, Any]]:
        """
        Get model recommendations based on budget constraints.
        
        Args:
            provider: Current provider
            model: Current model
            task_type: Task type
            context_size: Estimated context size in tokens
            
        Returns:
            List of recommended models with pricing information
        """
        debug_log.info("budget_engine", 
                     f"Getting model recommendations for {provider}/{model}")
        
        # Get current pricing
        current_pricing = pricing_repo.get_current_pricing(provider, model)
        if not current_pricing:
            debug_log.warn("budget_engine", 
                         f"No pricing found for {provider}/{model}")
            return []
            
        # Calculate current estimated cost for this context size
        # Assume 25% input, 75% output for typical completion
        input_tokens = int(context_size * 0.25)
        output_tokens = int(context_size * 0.75)
        
        current_cost = (
            input_tokens * current_pricing.input_cost_per_token +
            output_tokens * current_pricing.output_cost_per_token
        )
        
        # Get all current pricing data
        # This could be optimized with a repository method
        all_pricing = []
        session = pricing_repo.db_repository.db_manager.get_session()
        
        try:
            from sqlalchemy import and_, or_
            from datetime import datetime
            from budget.data.db_models import ProviderPricingDB
            
            now = datetime.now()
            
            results = session.query(ProviderPricingDB).filter(
                ProviderPricingDB.effective_date <= now,
                or_(
                    ProviderPricingDB.end_date == None,
                    ProviderPricingDB.end_date > now
                )
            ).all()
            
            all_pricing = [pricing_repo.db_repository._to_pydantic(result) 
                         for result in results]
                         
        finally:
            session.close()
            
        # Find cheaper alternatives
        cheaper_models = []
        
        for pricing in all_pricing:
            # Skip the current model
            if pricing.provider == provider and pricing.model == model:
                continue
                
            # Calculate cost for this model
            model_cost = (
                input_tokens * pricing.input_cost_per_token +
                output_tokens * pricing.output_cost_per_token
            )
            
            # Only include cheaper models
            if model_cost < current_cost:
                savings = current_cost - model_cost
                savings_percent = (savings / current_cost) * 100 if current_cost > 0 else 0
                
                cheaper_models.append({
                    "provider": pricing.provider,
                    "model": pricing.model,
                    "estimated_cost": model_cost,
                    "savings": savings,
                    "savings_percent": savings_percent,
                    "input_cost_per_token": pricing.input_cost_per_token,
                    "output_cost_per_token": pricing.output_cost_per_token
                })
                
        # Sort by savings (highest first)
        cheaper_models.sort(key=lambda m: m["savings"], reverse=True)
        
        debug_log.info("budget_engine", 
                     f"Found {len(cheaper_models)} cheaper alternatives")
        
        return cheaper_models


# Create singleton instance
budget_engine = BudgetEngine()


def get_budget_engine() -> BudgetEngine:
    """
    Get the singleton budget engine instance.
    
    Returns:
        BudgetEngine: The budget engine instance
    """
    return budget_engine