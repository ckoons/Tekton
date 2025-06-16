"""
Rhetor Integration Adapter

This module provides an adapter for integrating with Rhetor's cost budget system,
allowing a seamless transition to the consolidated Budget component.
"""

import os
import json
import logging
import asyncio
import uuid
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
import requests

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

# Import domain models and repositories
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority, PriceType,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert, ProviderPricing
)
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo, alert_repo, pricing_repo
)

# Import core components
from budget.core.engine import budget_engine
from budget.core.allocation import allocation_manager


class RhetorAdapter:
    """
    Adapter for integrating with Rhetor's cost budget system.
    
    This adapter provides compatibility with Rhetor's budget API,
    translating Rhetor's calls to the new Budget component's domain model.
    """
    
    def __init__(self, api_base_url: Optional[str] = None, db_path: Optional[str] = None):
        """
        Initialize the Rhetor adapter.
        
        Args:
            api_base_url: Base URL for Rhetor API (for migration purposes)
            db_path: Path to Rhetor's SQLite database (for migration)
        """
        self.api_base_url = api_base_url or os.environ.get("RHETOR_API_URL", "http://localhost:8003")
        self.db_path = db_path or os.path.expanduser("~/.tekton/data/rhetor/budget.db")
        
        # Map Rhetor periods to our enum values
        self.period_mapping = {
            "daily": BudgetPeriod.DAILY,
            "weekly": BudgetPeriod.WEEKLY,
            "monthly": BudgetPeriod.MONTHLY
        }
        
        # Map Rhetor policies to our enum values
        self.policy_mapping = {
            "ignore": BudgetPolicyType.IGNORE,
            "warn": BudgetPolicyType.WARN,
            "enforce": BudgetPolicyType.HARD_LIMIT
        }
        
        # Create or get the Rhetor budget
        self.rhetor_budget_id = self._get_or_create_rhetor_budget()
    
    @log_function()
    def _get_or_create_rhetor_budget(self) -> str:
        """
        Get or create a budget for Rhetor.
        
        Returns:
            Budget ID
        """
        debug_log.info("rhetor_adapter", "Getting or creating Rhetor budget")
        
        # Check if Rhetor budget already exists
        all_budgets = budget_repo.get_all()
        for budget in all_budgets:
            if budget.name == "Rhetor Budget":
                debug_log.info("rhetor_adapter", f"Using existing Rhetor budget: {budget.budget_id}")
                return budget.budget_id
        
        # Create a new budget for Rhetor
        budget = budget_engine.create_budget(
            name="Rhetor Budget",
            description="Budget for Rhetor component (migrated)",
            owner="rhetor"
        )
        
        # Create default policies
        budget_engine.create_default_policies(budget.budget_id)
        
        debug_log.info("rhetor_adapter", f"Created new Rhetor budget: {budget.budget_id}")
        return budget.budget_id
    
    @log_function()
    def calculate_cost(
        self, 
        provider: str, 
        model: str, 
        input_text: str, 
        output_text: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate the cost of a request.
        
        Args:
            provider: Provider name (anthropic, openai, etc.)
            model: Model name
            input_text: Input text
            output_text: Output text (optional)
            
        Returns:
            Dictionary with token counts and costs
        """
        debug_log.info("rhetor_adapter", f"Calculating cost for {provider}/{model}")
        
        # Get current pricing from Budget component
        pricing = pricing_repo.get_current_pricing(provider, model)
        
        # Count tokens using the Budget component's token counter
        input_tokens = allocation_manager.count_tokens(provider, model, input_text)
        output_tokens = allocation_manager.count_tokens(provider, model, output_text) if output_text else 0
        
        # Calculate costs
        if pricing:
            input_cost = input_tokens * pricing.input_cost_per_token
            output_cost = output_tokens * pricing.output_cost_per_token
            total_cost = input_cost + output_cost
        else:
            # No pricing found, assume zero cost
            debug_log.warn("rhetor_adapter", f"No pricing found for {provider}/{model}")
            input_cost = 0.0
            output_cost = 0.0
            total_cost = 0.0
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    @log_function()
    def estimate_cost(
        self, 
        provider: str, 
        model: str, 
        input_text: str, 
        estimated_output_length: int = 500
    ) -> Dict[str, Any]:
        """
        Estimate the cost of a request before making it.
        
        Args:
            provider: Provider name
            model: Model name
            input_text: Input text
            estimated_output_length: Estimated output length in characters
            
        Returns:
            Dictionary with estimated token counts and costs
        """
        debug_log.info("rhetor_adapter", 
                     f"Estimating cost for {provider}/{model} with output length {estimated_output_length}")
        
        # For estimation, we create a dummy output text with the estimated length
        estimated_output = "a" * estimated_output_length
        return self.calculate_cost(provider, model, input_text, estimated_output)
    
    @log_function()
    def record_completion(
        self,
        provider: str,
        model: str,
        input_text: str,
        output_text: str,
        component: str = "rhetor",
        task_type: str = "default",
        context_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a completed LLM request.
        
        Args:
            provider: Provider name
            model: Model name
            input_text: Input text
            output_text: Output text
            component: Component that made the request
            task_type: Type of task
            context_id: Context identifier (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Dictionary with usage data
        """
        debug_log.info("rhetor_adapter", f"Recording completion for {provider}/{model}")
        
        # Calculate cost
        cost_data = self.calculate_cost(provider, model, input_text, output_text)
        input_tokens = cost_data["input_tokens"]
        output_tokens = cost_data["output_tokens"]
        total_cost = cost_data["total_cost"]
        
        # Generate context_id if not provided
        if not context_id:
            context_id = str(uuid.uuid4())
        
        # Record using Budget component
        record = usage_repo.create(UsageRecord(
            record_id=str(uuid.uuid4()),
            budget_id=self.rhetor_budget_id,
            context_id=context_id,
            component=component,
            provider=provider,
            model=model,
            task_type=task_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=cost_data["input_cost"],
            output_cost=cost_data["output_cost"],
            total_cost=total_cost,
            metadata=metadata or {}
        ))
        
        return {
            "provider": provider,
            "model": model,
            "component": component,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": cost_data["input_cost"],
            "output_cost": cost_data["output_cost"],
            "total_cost": total_cost,
            "record_id": record.record_id,
            "context_id": context_id
        }
    
    @log_function()
    def check_budget(
        self, 
        provider: str, 
        model: str, 
        input_text: str,
        component: str = "rhetor",
        task_type: str = "default",
        context_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is within budget limits.
        
        Args:
            provider: Provider name
            model: Model name
            input_text: Input text
            component: Component making the request
            task_type: Type of task
            context_id: Context identifier (optional)
            
        Returns:
            Tuple of (True if allowed, info dict with details)
        """
        debug_log.info("rhetor_adapter", f"Checking budget for {provider}/{model}")
        
        # Estimate cost
        cost_estimate = self.estimate_cost(provider, model, input_text)
        estimated_cost = cost_estimate["total_cost"]
        
        # If cost is 0, always allow
        if estimated_cost == 0:
            return True, {
                "allowed": True,
                "reason": "Free model",
                "cost_estimate": cost_estimate
            }
        
        # Get context_id if not provided
        if not context_id:
            context_id = str(uuid.uuid4())
        
        # Check budget policies
        for period in [BudgetPeriod.DAILY, BudgetPeriod.WEEKLY, BudgetPeriod.MONTHLY]:
            # Get usage for this period
            summary = budget_engine.get_budget_summary(
                budget_id=self.rhetor_budget_id,
                period=period
            )
            
            # Skip if no summaries found
            if not summary:
                continue
                
            # Get summary for this period
            usage_summary = summary[0]
            
            # Get policy for this period
            policies = policy_repo.get_active_policies(
                budget_id=self.rhetor_budget_id,
                period=period
            )
            
            if not policies:
                continue
                
            policy = policies[0]
            
            # Check if cost limit is set and would be exceeded
            if policy.cost_limit and usage_summary.total_cost + estimated_cost > policy.cost_limit:
                # Check policy type
                if policy.type == BudgetPolicyType.HARD_LIMIT:
                    return False, {
                        "allowed": False,
                        "reason": f"{period.value.capitalize()} budget limit exceeded",
                        "limit": policy.cost_limit,
                        "usage": usage_summary.total_cost,
                        "estimated_cost": estimated_cost,
                        "policy": policy.type,
                        "cost_estimate": cost_estimate
                    }
                elif policy.type == BudgetPolicyType.WARN or policy.type == BudgetPolicyType.SOFT_LIMIT:
                    # Create a warning but allow
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        budget_id=self.rhetor_budget_id,
                        policy_id=policy.policy_id,
                        severity="warning",
                        type="cost_limit_approaching",
                        message=f"{period.value.capitalize()} cost budget approaching limit",
                        details={
                            "period": period.value,
                            "provider": provider,
                            "model": model,
                            "component": component,
                            "task_type": task_type,
                            "context_id": context_id,
                            "cost_limit": policy.cost_limit,
                            "cost_used": usage_summary.total_cost,
                            "estimated_cost": estimated_cost,
                            "usage_percentage": (usage_summary.total_cost + estimated_cost) / policy.cost_limit
                        },
                        timestamp=datetime.now()
                    )
                    
                    alert_repo.create(alert)
        
        # Find alternatives if this is an expensive model
        alternatives = []
        if estimated_cost > 0:
            recommendations = budget_engine.get_model_recommendations(
                provider=provider,
                model=model,
                task_type=task_type,
                context_size=cost_estimate["input_tokens"] + cost_estimate["output_tokens"]
            )
            
            # Only include top 3 alternatives for simplicity
            alternatives = recommendations[:3]
        
        # If we get here, the request is allowed
        return True, {
            "allowed": True,
            "cost_estimate": cost_estimate,
            "alternatives": alternatives,
            "context_id": context_id
        }
    
    @log_function()
    def get_usage_summary(
        self, 
        period: Union[BudgetPeriod, str] = BudgetPeriod.DAILY,
        group_by: str = "provider"
    ) -> Dict[str, Any]:
        """
        Get a summary of usage for a period, grouped by provider, model, or component.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            group_by: Field to group by (provider, model, component, task_type)
            
        Returns:
            Dictionary with usage summary
        """
        debug_log.info("rhetor_adapter", f"Getting usage summary for period {period}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        # Get budget summaries
        summaries = budget_engine.get_budget_summary(
            budget_id=self.rhetor_budget_id,
            period=period
        )
        
        if not summaries:
            return {
                "period": period.value,
                "total_cost": 0.0,
                "total_tokens": 0,
                "groups": {}
            }
        
        # Get usage records for this period
        time_range = self._get_time_range_for_period(period)
        records = usage_repo.get_by_time_range(
            start_time=time_range[0],
            end_time=time_range[1],
            budget_id=self.rhetor_budget_id
        )
        
        # Group by specified field
        groups = {}
        for record in records:
            key = getattr(record, group_by, "unknown")
            
            if key not in groups:
                groups[key] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "count": 0
                }
            
            groups[key]["cost"] += record.total_cost
            groups[key]["input_tokens"] += record.input_tokens
            groups[key]["output_tokens"] += record.output_tokens
            groups[key]["count"] += 1
        
        # Calculate totals
        total_cost = sum(record.total_cost for record in records)
        total_input_tokens = sum(record.input_tokens for record in records)
        total_output_tokens = sum(record.output_tokens for record in records)
        
        return {
            "period": period.value,
            "total_cost": total_cost,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "count": len(records),
            "groups": groups
        }
    
    def _get_time_range_for_period(self, period: BudgetPeriod) -> Tuple[datetime, datetime]:
        """
        Get time range for a budget period.
        
        Args:
            period: Budget period
            
        Returns:
            Tuple of (start_time, end_time)
        """
        now = datetime.now()
        
        if period == BudgetPeriod.DAILY:
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
            # Unsupported period, default to daily
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
        return start_time, end_time
    
    @log_function()
    def get_budget_limit(self, period: Union[BudgetPeriod, str], provider: str = "all") -> float:
        """
        Get the budget limit for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            provider: Provider name or "all" for global limit
            
        Returns:
            Budget limit amount (0 if no limit set)
        """
        debug_log.info("rhetor_adapter", f"Getting budget limit for {period}/{provider}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        # Get policies for this period
        policies = policy_repo.get_active_policies(
            budget_id=self.rhetor_budget_id,
            period=period,
            provider=provider if provider != "all" else None
        )
        
        if not policies:
            return 0.0
            
        # Find policy with cost limit
        for policy in policies:
            if policy.cost_limit is not None:
                return policy.cost_limit
                
        return 0.0
    
    @log_function()
    def set_budget_limit(
        self, 
        period: Union[BudgetPeriod, str], 
        limit_amount: float,
        provider: str = "all",
        enforcement: Optional[Union[BudgetPolicyType, str]] = None
    ) -> bool:
        """
        Set the budget limit for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            limit_amount: Budget limit amount
            provider: Provider name or "all" for global limit
            enforcement: Budget enforcement policy (ignore, warn, enforce)
            
        Returns:
            True if successful
        """
        debug_log.info("rhetor_adapter", 
                     f"Setting budget limit for {period}/{provider}: ${limit_amount}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        # Convert string enforcement to enum if needed
        if isinstance(enforcement, str) and enforcement:
            enforcement = self.policy_mapping.get(enforcement, BudgetPolicyType.WARN)
        
        enforcement = enforcement or BudgetPolicyType.WARN
        
        try:
            # Set policy using Budget component
            policy = budget_engine.set_policy(
                budget_id=self.rhetor_budget_id,
                period=period,
                cost_limit=limit_amount,
                provider=provider if provider != "all" else None,
                component="rhetor",
                policy_type=enforcement
            )
            
            return True
        except Exception as e:
            debug_log.error("rhetor_adapter", f"Error setting budget limit: {str(e)}")
            return False
    
    @log_function()
    def set_enforcement_policy(
        self, 
        period: Union[BudgetPeriod, str], 
        policy: Union[BudgetPolicyType, str],
        provider: str = "all"
    ) -> bool:
        """
        Set the budget enforcement policy for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            policy: Budget enforcement policy (ignore, warn, enforce)
            provider: Provider name or "all" for global policy
            
        Returns:
            True if successful
        """
        debug_log.info("rhetor_adapter", f"Setting enforcement policy for {period}: {policy}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
            
        # Convert string policy to enum if needed
        if isinstance(policy, str):
            policy = self.policy_mapping.get(policy, BudgetPolicyType.WARN)
        
        # Get existing policies for this period
        existing_policies = policy_repo.get_active_policies(
            budget_id=self.rhetor_budget_id,
            period=period,
            provider=provider if provider != "all" else None
        )
        
        if not existing_policies:
            # No existing policy, create one with default limit (0)
            budget_engine.set_policy(
                budget_id=self.rhetor_budget_id,
                period=period,
                cost_limit=0.0,
                provider=provider if provider != "all" else None,
                component="rhetor",
                policy_type=policy
            )
        else:
            # Update existing policies
            for existing_policy in existing_policies:
                existing_policy.type = policy
                policy_repo.update(existing_policy)
                
        return True
    
    @log_function()
    def get_enforcement_policy(self, period: Union[BudgetPeriod, str], provider: str = "all") -> str:
        """
        Get the budget enforcement policy for a period.
        
        Args:
            period: Budget period (daily, weekly, monthly)
            provider: Provider name or "all" for global policy
            
        Returns:
            Budget enforcement policy (ignore, warn, enforce)
        """
        debug_log.info("rhetor_adapter", f"Getting enforcement policy for {period}/{provider}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        # Get policies for this period
        policies = policy_repo.get_active_policies(
            budget_id=self.rhetor_budget_id,
            period=period,
            provider=provider if provider != "all" else None
        )
        
        if not policies:
            return BudgetPolicyType.WARN.value
            
        # Return first policy's type
        return policies[0].type.value
    
    @log_function()
    def route_with_budget_awareness(
        self,
        input_text: str,
        task_type: str,
        default_provider: str,
        default_model: str,
        component: str = "rhetor"
    ) -> Tuple[str, str, List[str]]:
        """
        Route a request with budget awareness.
        
        Args:
            input_text: Input text for cost estimation
            task_type: Type of task (code, chat, etc.)
            default_provider: Default provider
            default_model: Default model
            component: Component making the request
            
        Returns:
            Tuple of (provider, model, warnings)
        """
        debug_log.info("rhetor_adapter", 
                     f"Routing with budget awareness for {default_provider}/{default_model}")
        
        # Check if the default model is within budget
        allowed, info = self.check_budget(
            provider=default_provider,
            model=default_model,
            input_text=input_text,
            component=component,
            task_type=task_type
        )
        
        # If allowed, use the default model
        if allowed and not info.get("alternatives"):
            return default_provider, default_model, []
            
        # If allowed but cheaper alternatives exist, check if we should downgrade
        if allowed and info.get("alternatives"):
            # Get policies to see if we should enforce soft limits
            daily_policy_type = self.get_enforcement_policy(BudgetPeriod.DAILY)
            
            # Only downgrade for soft_limit policy
            if daily_policy_type == BudgetPolicyType.SOFT_LIMIT.value:
                # Check if we're approaching the limit
                summary = budget_engine.get_budget_summary(
                    budget_id=self.rhetor_budget_id,
                    period=BudgetPeriod.DAILY
                )
                
                if summary and summary[0].cost_usage_percentage > 0.8:
                    # We're approaching the limit, use the cheaper alternative
                    alt = info["alternatives"][0]
                    downgrade_warning = (
                        f"Budget approaching limit ({summary[0].cost_usage_percentage:.2%}). "
                        f"Downgraded from {default_provider}/{default_model} to "
                        f"{alt['provider']}/{alt['model']} to save "
                        f"${alt['savings']:.4f} ({alt['savings_percent']:.2f}%)"
                    )
                    return alt["provider"], alt["model"], [downgrade_warning]
            
            # Otherwise use the default model            
            return default_provider, default_model, []
            
        # If not allowed, use the cheapest alternative
        if info.get("alternatives"):
            alt = info["alternatives"][0]
            downgrade_warning = (
                f"Budget limit exceeded. Downgraded from {default_provider}/{default_model} "
                f"to {alt['provider']}/{alt['model']}"
            )
            return alt["provider"], alt["model"], [downgrade_warning]
        
        # If no affordable alternative, use a free model if available
        free_models = self._get_free_models()
        if free_models:
            # Choose first free model
            free_model = free_models[0]
            downgrade_warning = (
                f"Budget limit exceeded. Using free model {free_model['provider']}/{free_model['model']}"
            )
            return free_model["provider"], free_model["model"], [downgrade_warning]
        
        # If no free models, use the default as a fallback with a warning
        emergency_warning = "Budget limit exceeded but no alternatives available. Using default model."
        return default_provider, default_model, [emergency_warning]
    
    def _get_free_models(self) -> List[Dict[str, str]]:
        """
        Get list of free models.
        
        Returns:
            List of free models
        """
        # Get all current pricing
        all_pricing = pricing_repo.get_all()
        
        # Filter for free models
        free_models = []
        for pricing in all_pricing:
            if pricing.input_cost_per_token == 0 and pricing.output_cost_per_token == 0:
                free_models.append({
                    "provider": pricing.provider,
                    "model": pricing.model
                })
                
        return free_models
    
    @log_function()
    def get_model_tiers(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get models categorized by pricing tier.
        
        Returns:
            Dictionary with models by tier
        """
        debug_log.info("rhetor_adapter", "Getting model tiers")
        
        # Define tiers
        tiers = {
            "free": [],
            "low": [],
            "medium": [],
            "high": []
        }
        
        # Get all current pricing
        all_pricing = pricing_repo.get_all()
        
        for pricing in all_pricing:
            # Calculate cost per 1K tokens
            cost_per_1k = (pricing.input_cost_per_token + pricing.output_cost_per_token) * 1000
            
            # Categorize by cost
            if cost_per_1k == 0:
                tier = "free"
            elif cost_per_1k < 0.01:
                tier = "low"
            elif cost_per_1k < 0.05:
                tier = "medium"
            else:
                tier = "high"
            
            # Add to appropriate tier
            tiers[tier].append({
                "provider": pricing.provider,
                "model": pricing.model,
                "cost_per_1k_tokens": cost_per_1k
            })
        
        return tiers
    
    @log_function()
    async def migrate_from_rhetor(self) -> Dict[str, Any]:
        """
        Migrate data from Rhetor's budget system.
        
        Returns:
            Migration results
        """
        debug_log.info("rhetor_adapter", "Starting migration from Rhetor")
        
        results = {
            "success": True,
            "budgets_migrated": 0,
            "policies_migrated": 0,
            "usage_records_migrated": 0,
            "pricing_records_migrated": 0,
            "errors": []
        }
        
        # Check if Rhetor database exists
        if not os.path.exists(self.db_path):
            debug_log.error("rhetor_adapter", f"Rhetor database not found at {self.db_path}")
            results["success"] = False
            results["errors"].append(f"Rhetor database not found at {self.db_path}")
            return results
        
        try:
            # Connect to Rhetor database
            rhetor_conn = sqlite3.connect(self.db_path)
            rhetor_conn.row_factory = sqlite3.Row
            
            # Migrate budget settings
            try:
                debug_log.info("rhetor_adapter", "Migrating budget settings")
                
                cursor = rhetor_conn.cursor()
                cursor.execute("SELECT * FROM budget_settings WHERE active = 1")
                budget_settings = cursor.fetchall()
                
                for setting in budget_settings:
                    try:
                        # Map period and enforcement
                        period = self.period_mapping.get(setting["period"], BudgetPeriod.DAILY)
                        enforcement = self.policy_mapping.get(setting["enforcement"], BudgetPolicyType.WARN)
                        
                        # Create policy
                        policy = budget_engine.set_policy(
                            budget_id=self.rhetor_budget_id,
                            period=period,
                            cost_limit=setting["limit_amount"],
                            provider=setting["provider"] if setting["provider"] != "all" else None,
                            policy_type=enforcement
                        )
                        
                        results["policies_migrated"] += 1
                    except Exception as e:
                        debug_log.error("rhetor_adapter", f"Error migrating budget setting: {str(e)}")
                        results["errors"].append(f"Error migrating budget setting: {str(e)}")
            except Exception as e:
                debug_log.error("rhetor_adapter", f"Error migrating budget settings: {str(e)}")
                results["errors"].append(f"Error migrating budget settings: {str(e)}")
            
            # Migrate usage records
            try:
                debug_log.info("rhetor_adapter", "Migrating usage records")
                
                cursor = rhetor_conn.cursor()
                cursor.execute("SELECT * FROM usage ORDER BY timestamp")
                usage_records = cursor.fetchall()
                
                for record in usage_records:
                    try:
                        # Convert timestamp
                        timestamp = datetime.fromisoformat(record["timestamp"])
                        
                        # Create metadata
                        metadata = None
                        if record["metadata"]:
                            try:
                                metadata = json.loads(record["metadata"])
                            except:
                                metadata = {"original_metadata": record["metadata"]}
                        
                        # Create record
                        usage_record = UsageRecord(
                            record_id=str(uuid.uuid4()),
                            budget_id=self.rhetor_budget_id,
                            context_id=f"rhetor_migration_{record['id']}",
                            component=record["component"],
                            provider=record["provider"],
                            model=record["model"],
                            task_type=record["task_type"],
                            input_tokens=record["input_tokens"],
                            output_tokens=record["output_tokens"],
                            total_cost=record["cost"],
                            timestamp=timestamp,
                            metadata=metadata or {}
                        )
                        
                        # Save record
                        usage_repo.create(usage_record)
                        
                        results["usage_records_migrated"] += 1
                    except Exception as e:
                        debug_log.error("rhetor_adapter", f"Error migrating usage record: {str(e)}")
                        results["errors"].append(f"Error migrating usage record: {str(e)}")
            except Exception as e:
                debug_log.error("rhetor_adapter", f"Error migrating usage records: {str(e)}")
                results["errors"].append(f"Error migrating usage records: {str(e)}")
            
            # Migrate pricing data
            try:
                debug_log.info("rhetor_adapter", "Migrating pricing data")
                
                # Extract pricing from Rhetor's hardcoded pricing
                pricing_data = self._extract_rhetor_pricing()
                
                for provider, models in pricing_data.items():
                    for model, price_info in models.items():
                        try:
                            # Create pricing record
                            pricing = ProviderPricing(
                                pricing_id=str(uuid.uuid4()),
                                provider=provider,
                                model=model,
                                price_type=PriceType.TOKEN_BASED,
                                input_cost_per_token=price_info["input_cost_per_token"],
                                output_cost_per_token=price_info["output_cost_per_token"],
                                version="1.0",
                                source="rhetor_migration",
                                verified=True,
                                effective_date=datetime.now()
                            )
                            
                            # Save pricing
                            pricing_repo.create(pricing)
                            
                            results["pricing_records_migrated"] += 1
                        except Exception as e:
                            debug_log.error("rhetor_adapter", f"Error migrating pricing: {str(e)}")
                            results["errors"].append(f"Error migrating pricing: {str(e)}")
            except Exception as e:
                debug_log.error("rhetor_adapter", f"Error migrating pricing data: {str(e)}")
                results["errors"].append(f"Error migrating pricing data: {str(e)}")
            
            # Close Rhetor database
            rhetor_conn.close()
            
            # Update results
            results["budgets_migrated"] = 1
            
            if results["errors"]:
                results["success"] = False
            
            debug_log.info("rhetor_adapter", 
                         f"Migration completed: {results['policies_migrated']} policies, " +
                         f"{results['usage_records_migrated']} usage records, " +
                         f"{results['pricing_records_migrated']} pricing records")
            
            return results
        except Exception as e:
            debug_log.error("rhetor_adapter", f"Error during migration: {str(e)}")
            results["success"] = False
            results["errors"].append(f"Error during migration: {str(e)}")
            return results
    
    def _extract_rhetor_pricing(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Extract pricing data from Rhetor's hardcoded pricing.
        
        Returns:
            Dictionary with pricing data
        """
        # This is a simplified version of the pricing data from Rhetor
        # In a real implementation, we would read this from the Rhetor database or API
        return {
            "anthropic": {
                "claude-3-opus-20240229": {
                    "input_cost_per_token": 0.000015,
                    "output_cost_per_token": 0.000075,
                },
                "claude-3-sonnet-20240229": {
                    "input_cost_per_token": 0.000003,
                    "output_cost_per_token": 0.000015,
                },
                "claude-3-haiku-20240307": {
                    "input_cost_per_token": 0.00000025,
                    "output_cost_per_token": 0.00000125,
                },
                "claude-3-5-sonnet-20240620": {
                    "input_cost_per_token": 0.000003,
                    "output_cost_per_token": 0.000013,
                }
            },
            "openai": {
                "gpt-4": {
                    "input_cost_per_token": 0.00003,
                    "output_cost_per_token": 0.00006,
                },
                "gpt-4-turbo": {
                    "input_cost_per_token": 0.00001,
                    "output_cost_per_token": 0.00003,
                },
                "gpt-4o": {
                    "input_cost_per_token": 0.00001,
                    "output_cost_per_token": 0.00003,
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_token": 0.0000005,
                    "output_cost_per_token": 0.0000015,
                }
            },
            "ollama": {  # Local models are free
                "llama3": {
                    "input_cost_per_token": 0.0,
                    "output_cost_per_token": 0.0,
                }
            },
            "simulated": {  # Simulated provider is free
                "simulated-standard": {
                    "input_cost_per_token": 0.0,
                    "output_cost_per_token": 0.0,
                }
            }
        }


# Create global instance
rhetor_adapter = RhetorAdapter()