"""
Apollo Integration Adapter

This module provides an adapter for integrating with Apollo's token budget system,
allowing a seamless transition to the consolidated Budget component.
"""

import os
import json
import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import requests
from shared.env import TektonEnviron
from shared.urls import apollo_url

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
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert
)
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo, alert_repo
)

# Import core components
from budget.core.engine import budget_engine
from budget.core.allocation import allocation_manager

class ApolloAdapter:
    """
    Adapter for integrating with Apollo's token budget system.
    
    This adapter provides compatibility with Apollo's token budget API,
    translating Apollo's calls to the new Budget component's domain model.
    """
    
    def __init__(self, api_base_url: Optional[str] = None):
        """
        Initialize the Apollo adapter.
        
        Args:
            api_base_url: Base URL for Apollo API (for migration purposes)
        """
        self.api_base_url = api_base_url or TektonEnviron.get("APOLLO_API_URL", apollo_url())
        
        # Apollo uses these tier names, which we map to our enum values
        self.tier_mapping = {
            "lightweight": BudgetTier.LOCAL_LIGHTWEIGHT,
            "midweight": BudgetTier.LOCAL_MIDWEIGHT,
            "heavyweight": BudgetTier.REMOTE_HEAVYWEIGHT
        }
        
        # Create or get the Apollo budget
        self.apollo_budget_id = self._get_or_create_apollo_budget()
    
    @log_function()
    def _get_or_create_apollo_budget(self) -> str:
        """
        Get or create a budget for Apollo.
        
        Returns:
            Budget ID
        """
        debug_log.info("apollo_adapter", "Getting or creating Apollo budget")
        
        # Check if Apollo budget already exists
        all_budgets = budget_repo.get_all()
        for budget in all_budgets:
            if budget.name == "Apollo Budget":
                debug_log.info("apollo_adapter", f"Using existing Apollo budget: {budget.budget_id}")
                return budget.budget_id
        
        # Create a new budget for Apollo
        budget = budget_engine.create_budget(
            name="Apollo Budget",
            description="Budget for Apollo component (migrated)",
            owner="apollo"
        )
        
        # Create default policies
        budget_engine.create_default_policies(budget.budget_id)
        
        debug_log.info("apollo_adapter", f"Created new Apollo budget: {budget.budget_id}")
        return budget.budget_id
    
    @log_function()
    def allocate_tokens(
        self,
        context_id: str,
        amount: int,
        tier: str = "heavyweight",
        model: Optional[str] = None,
        provider: Optional[str] = None,
        task_type: str = "generation",
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Allocate tokens for Apollo.
        
        Args:
            context_id: Context identifier
            amount: Number of tokens to allocate
            tier: Token tier (lightweight, midweight, heavyweight)
            model: Model name (optional)
            provider: Provider name (optional)
            task_type: Task type
            priority: Priority (1-10)
            
        Returns:
            Allocation details
        """
        debug_log.info("apollo_adapter", f"Allocating {amount} tokens for context {context_id}")
        
        # Map Apollo tier to Budget tier
        budget_tier = self.tier_mapping.get(tier.lower(), BudgetTier.REMOTE_HEAVYWEIGHT)
        
        try:
            # Create allocation using Budget component
            allocation = allocation_manager.allocate_budget(
                context_id=context_id,
                component="apollo",
                tokens=amount,
                budget_id=self.apollo_budget_id,
                tier=budget_tier,
                provider=provider,
                model=model,
                task_type=task_type,
                priority=priority
            )
            
            # Convert to Apollo response format
            return {
                "allocation_id": allocation.allocation_id,
                "context_id": allocation.context_id,
                "amount": allocation.tokens_allocated,
                "remaining": allocation.remaining_tokens,
                "tier": tier,
                "success": True
            }
        except Exception as e:
            debug_log.error("apollo_adapter", f"Error allocating tokens: {str(e)}")
            return {
                "context_id": context_id,
                "amount": 0,
                "remaining": 0,
                "tier": tier,
                "success": False,
                "error": str(e)
            }
    
    @log_function()
    def release_allocation(self, allocation_id: str) -> Dict[str, Any]:
        """
        Release a token allocation.
        
        Args:
            allocation_id: Allocation ID
            
        Returns:
            Release result
        """
        debug_log.info("apollo_adapter", f"Releasing allocation {allocation_id}")
        
        # Release allocation using Budget component
        success = allocation_manager.release_allocation(allocation_id)
        
        return {
            "allocation_id": allocation_id,
            "success": success
        }
    
    @log_function()
    def record_token_usage(
        self,
        context_id: str,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        model: str,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record token usage for Apollo.
        
        Args:
            context_id: Context identifier
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            provider: Provider name
            model: Model name
            request_id: Request ID (optional)
            
        Returns:
            Recording result
        """
        debug_log.info("apollo_adapter", 
                     f"Recording usage for context {context_id}: {input_tokens} input, {output_tokens} output")
        
        try:
            # Record usage using Budget component
            record = allocation_manager.record_usage(
                context_id=context_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider=provider,
                model=model,
                request_id=request_id
            )
            
            return {
                "context_id": context_id,
                "recorded_tokens": input_tokens + output_tokens,
                "remaining": record.remaining_tokens if record else 0,
                "success": True
            }
        except Exception as e:
            debug_log.error("apollo_adapter", f"Error recording token usage: {str(e)}")
            return {
                "context_id": context_id,
                "recorded_tokens": 0,
                "remaining": 0,
                "success": False,
                "error": str(e)
            }
    
    @log_function()
    def get_budget_status(
        self,
        period: str = "daily",
        tier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get budget status for Apollo.
        
        Args:
            period: Budget period (hourly, daily, weekly, monthly)
            tier: Budget tier (lightweight, midweight, heavyweight)
            
        Returns:
            Budget status
        """
        debug_log.info("apollo_adapter", f"Getting budget status for period {period}, tier {tier}")
        
        try:
            # Convert period string to enum
            budget_period = BudgetPeriod(period)
            
            # Convert tier string to enum if provided
            budget_tier = None
            if tier:
                budget_tier = self.tier_mapping.get(tier.lower())
            
            # Get budget summary using Budget component
            summaries = budget_engine.get_budget_summary(
                budget_id=self.apollo_budget_id,
                period=budget_period,
                tier=budget_tier
            )
            
            # Convert to Apollo response format
            result = {
                "period": period,
                "success": True,
                "tiers": {}
            }
            
            for summary in summaries:
                tier_key = "all"
                if summary.tier:
                    # Reverse lookup to get Apollo tier name
                    for apollo_tier, budget_tier_value in self.tier_mapping.items():
                        if budget_tier_value == summary.tier:
                            tier_key = apollo_tier
                            break
                
                result["tiers"][tier_key] = {
                    "allocated": summary.total_tokens_allocated,
                    "used": summary.total_tokens_used,
                    "remaining": summary.remaining_tokens or 0,
                    "limit": summary.token_limit or 0,
                    "usage_percentage": summary.token_usage_percentage or 0.0,
                    "limit_exceeded": summary.token_limit_exceeded
                }
            
            return result
        except Exception as e:
            debug_log.error("apollo_adapter", f"Error getting budget status: {str(e)}")
            return {
                "period": period,
                "success": False,
                "error": str(e)
            }
    
    @log_function()
    def get_allocation_status(self, allocation_id: str) -> Dict[str, Any]:
        """
        Get allocation status for Apollo.
        
        Args:
            allocation_id: Allocation ID
            
        Returns:
            Allocation status
        """
        debug_log.info("apollo_adapter", f"Getting allocation status for {allocation_id}")
        
        try:
            # Get allocation using Budget component
            allocation = allocation_repo.get_by_id(allocation_id)
            
            if not allocation:
                return {
                    "allocation_id": allocation_id,
                    "success": False,
                    "error": "Allocation not found"
                }
            
            # Reverse lookup to get Apollo tier name
            tier_name = "heavyweight"  # Default
            if allocation.tier:
                for apollo_tier, budget_tier_value in self.tier_mapping.items():
                    if budget_tier_value == allocation.tier:
                        tier_name = apollo_tier
                        break
            
            # Convert to Apollo response format
            return {
                "allocation_id": allocation.allocation_id,
                "context_id": allocation.context_id,
                "allocated": allocation.tokens_allocated,
                "used": allocation.tokens_used,
                "remaining": allocation.remaining_tokens,
                "tier": tier_name,
                "is_active": allocation.is_active,
                "created_at": allocation.creation_time.isoformat(),
                "expires_at": allocation.expiration_time.isoformat() if allocation.expiration_time else None,
                "success": True
            }
        except Exception as e:
            debug_log.error("apollo_adapter", f"Error getting allocation status: {str(e)}")
            return {
                "allocation_id": allocation_id,
                "success": False,
                "error": str(e)
            }
    
    @log_function()
    def set_budget_limit(
        self,
        tier: str,
        period: str,
        limit: int
    ) -> Dict[str, Any]:
        """
        Set budget limit for Apollo.
        
        Args:
            tier: Budget tier (lightweight, midweight, heavyweight)
            period: Budget period (hourly, daily, weekly, monthly)
            limit: Token limit
            
        Returns:
            Result of setting the limit
        """
        debug_log.info("apollo_adapter", f"Setting budget limit for {tier}/{period}: {limit}")
        
        try:
            # Convert period string to enum
            budget_period = BudgetPeriod(period)
            
            # Convert tier string to enum
            budget_tier = self.tier_mapping.get(tier.lower())
            if not budget_tier:
                return {
                    "success": False,
                    "error": f"Invalid tier: {tier}"
                }
            
            # Set policy using Budget component
            policy = budget_engine.set_policy(
                budget_id=self.apollo_budget_id,
                period=budget_period,
                token_limit=limit,
                tier=budget_tier,
                component="apollo",
                policy_type=BudgetPolicyType.WARN
            )
            
            return {
                "tier": tier,
                "period": period,
                "limit": limit,
                "policy_id": policy.policy_id,
                "success": True
            }
        except Exception as e:
            debug_log.error("apollo_adapter", f"Error setting budget limit: {str(e)}")
            return {
                "tier": tier,
                "period": period,
                "success": False,
                "error": str(e)
            }
    
    @log_function()
    async def migrate_from_apollo(self) -> Dict[str, Any]:
        """
        Migrate data from Apollo's token budget system.
        
        Returns:
            Migration results
        """
        debug_log.info("apollo_adapter", "Starting migration from Apollo")
        
        results = {
            "success": True,
            "budgets_migrated": 0,
            "policies_migrated": 0,
            "allocations_migrated": 0,
            "errors": []
        }
        
        try:
            # Fetch budget data from Apollo
            try:
                response = requests.get(f"{self.api_base_url}/api/apollo/budget/export")
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch budget data: {response.status_code}")
                
                budget_data = response.json()
            except Exception as e:
                debug_log.error("apollo_adapter", f"Error fetching budget data: {str(e)}")
                results["errors"].append(f"Error fetching budget data: {str(e)}")
                budget_data = {"policies": [], "allocations": []}
            
            # Process policies
            for policy_data in budget_data.get("policies", []):
                try:
                    # Convert Apollo policy to Budget policy
                    tier = self.tier_mapping.get(policy_data.get("tier", "heavyweight").lower())
                    period = BudgetPeriod(policy_data.get("period", "daily"))
                    
                    policy = budget_engine.set_policy(
                        budget_id=self.apollo_budget_id,
                        period=period,
                        token_limit=policy_data.get("limit", 100000),
                        tier=tier,
                        component="apollo",
                        policy_type=BudgetPolicyType.WARN
                    )
                    
                    results["policies_migrated"] += 1
                except Exception as e:
                    debug_log.error("apollo_adapter", f"Error migrating policy: {str(e)}")
                    results["errors"].append(f"Error migrating policy: {str(e)}")
            
            # Process allocations
            for alloc_data in budget_data.get("allocations", []):
                try:
                    # Only migrate active allocations
                    if not alloc_data.get("is_active", False):
                        continue
                    
                    # Convert Apollo allocation to Budget allocation
                    tier = self.tier_mapping.get(alloc_data.get("tier", "heavyweight").lower())
                    
                    allocation = allocation_manager.allocate_budget(
                        context_id=alloc_data.get("context_id", str(uuid.uuid4())),
                        component="apollo",
                        tokens=alloc_data.get("amount", 0),
                        budget_id=self.apollo_budget_id,
                        tier=tier,
                        provider=alloc_data.get("provider"),
                        model=alloc_data.get("model"),
                        task_type=alloc_data.get("task_type", "generation"),
                        priority=alloc_data.get("priority", 5)
                    )
                    
                    # If tokens have been used, record the usage
                    tokens_used = alloc_data.get("used", 0)
                    if tokens_used > 0:
                        # Assume 25% input, 75% output for migration
                        input_tokens = int(tokens_used * 0.25)
                        output_tokens = tokens_used - input_tokens
                        
                        allocation_manager.record_usage(
                            allocation_id=allocation.allocation_id,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            provider=alloc_data.get("provider", "unknown"),
                            model=alloc_data.get("model", "unknown")
                        )
                    
                    results["allocations_migrated"] += 1
                except Exception as e:
                    debug_log.error("apollo_adapter", f"Error migrating allocation: {str(e)}")
                    results["errors"].append(f"Error migrating allocation: {str(e)}")
            
            # Update results
            results["budgets_migrated"] = 1
            
            if results["errors"]:
                results["success"] = False
            
            debug_log.info("apollo_adapter", 
                         f"Migration completed: {results['policies_migrated']} policies, " +
                         f"{results['allocations_migrated']} allocations")
            
            return results
        except Exception as e:
            debug_log.error("apollo_adapter", f"Error during migration: {str(e)}")
            results["success"] = False
            results["errors"].append(f"Error during migration: {str(e)}")
            return results

# Create global instance
apollo_adapter = ApolloAdapter()