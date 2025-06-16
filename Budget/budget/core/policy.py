"""
Budget Policy Enforcement System

This module provides functionality for enforcing budget policies,
making budget-aware decisions, and selecting optimal models.
"""

import os
from datetime import datetime
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
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority
)
from budget.core.constants import (
    DEFAULT_MODEL_TIERS, DEFAULT_PROVIDER_TIERS
)

# Import repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo,
    alert_repo, pricing_repo
)

# Import other modules
from budget.core.engine import budget_engine
from budget.core.allocation import allocation_manager


class PolicyEnforcer:
    """
    Enforces budget policies and makes budget-aware decisions.
    
    This class is responsible for routing requests, selecting models,
    and enforcing budget policies.
    """
    
    def __init__(self):
        """Initialize the policy enforcer."""
        pass
        
    @log_function()
    def route_with_budget_awareness(
        self,
        input_text: str,
        task_type: str,
        default_provider: str,
        default_model: str,
        component: str = "unknown",
        budget_id: Optional[str] = None,
        priority: int = 5
    ) -> Tuple[str, str, List[str]]:
        """
        Route a request with budget awareness.
        
        This method checks if the default model is within budget limits
        and finds alternatives if needed.
        
        Args:
            input_text: Input text for cost estimation
            task_type: Type of task (code, chat, etc.)
            default_provider: Default provider
            default_model: Default model
            component: Component making the request
            budget_id: Budget ID (optional)
            priority: Task priority (1-10)
            
        Returns:
            Tuple of (provider, model, warnings)
        """
        debug_log.info("budget_policy", 
                     f"Routing request with budget awareness: "
                     f"{default_provider}/{default_model}, task: {task_type}")
        
        # Estimate input tokens
        input_tokens = len(input_text.split()) // 0.75  # Rough approximation
        
        # Check if default model is within budget
        allowed, info = allocation_manager.check_budget(
            provider=default_provider,
            model=default_model,
            input_tokens=input_tokens,
            component=component,
            task_type=task_type,
            budget_id=budget_id
        )
        
        # If allowed and not critical priority, use default model
        if allowed and priority < 10:
            debug_log.debug("budget_policy", 
                          f"Default model {default_provider}/{default_model} is within budget")
            return default_provider, default_model, []
            
        # If allowed but critical priority, still use default model
        # but perhaps log that it's a critical request
        if allowed and priority == 10:
            debug_log.info("budget_policy", 
                          f"Critical priority request using {default_provider}/{default_model}")
            return default_provider, default_model, []
            
        # If not allowed, need to find alternatives
        debug_log.warn("budget_policy", 
                      f"Budget limit would be exceeded for {default_provider}/{default_model}")
        
        # Get model recommendations
        recommendations = budget_engine.get_model_recommendations(
            provider=default_provider,
            model=default_model,
            task_type=task_type,
            context_size=input_tokens * 5  # Rough estimate of context size
        )
        
        warnings = []
        
        # Add warning about budget limit
        warnings.append(f"Budget limit exceeded for {default_provider}/{default_model}")
        
        if not recommendations:
            debug_log.warn("budget_policy", "No alternative models found")
            warnings.append("No cheaper alternatives available")
            
            # If critical priority, use default model anyway
            if priority == 10:
                debug_log.warn("budget_policy", 
                              "Using default model despite budget limits due to critical priority")
                warnings.append("Using default model due to critical priority")
                return default_provider, default_model, warnings
                
            # Try to find any free model
            free_models = []
            
            for provider in ["ollama", "local"]:
                # Check if any models from this provider are available
                if not free_models:
                    session = pricing_repo.db_repository.db_manager.get_session()
                    
                    try:
                        from budget.data.db_models import ProviderPricingDB
                        
                        results = session.query(ProviderPricingDB).filter(
                            ProviderPricingDB.provider == provider,
                            ProviderPricingDB.input_cost_per_token == 0.0,
                            ProviderPricingDB.output_cost_per_token == 0.0
                        ).all()
                        
                        if results:
                            # Pick the first free model
                            free_model = results[0].model
                            free_models.append((provider, free_model))
                            
                    finally:
                        session.close()
            
            if free_models:
                provider, model = free_models[0]
                warnings.append(f"Downgrading to free model: {provider}/{model}")
                
                debug_log.info("budget_policy", 
                             f"Downgrading to free model: {provider}/{model}")
                
                return provider, model, warnings
                
            # If no free models found, use default model as last resort
            warnings.append("Using default model as last resort")
            
            debug_log.warn("budget_policy", 
                          "Using default model as last resort despite budget limits")
            
            return default_provider, default_model, warnings
            
        # Use the best recommendation
        best_rec = recommendations[0]
        provider = best_rec["provider"]
        model = best_rec["model"]
        
        # Add warning about downgrading
        warnings.append(
            f"Downgrading to cheaper model: {provider}/{model} "
            f"(saves {best_rec['savings_percent']:.1f}%)"
        )
        
        debug_log.info("budget_policy", 
                     f"Downgrading to cheaper model: {provider}/{model}")
        
        # Check if the alternative is within budget
        allowed, alt_info = allocation_manager.check_budget(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            component=component,
            task_type=task_type,
            budget_id=budget_id
        )
        
        if allowed:
            debug_log.debug("budget_policy", 
                          f"Alternative model {provider}/{model} is within budget")
            return provider, model, warnings
            
        # If alternative is also not within budget but it's cheaper, use it anyway
        debug_log.warn("budget_policy", 
                     f"Alternative model {provider}/{model} also exceeds budget, "
                     f"but is cheaper than default")
        
        warnings.append("Alternative model also exceeds budget but is cheaper")
        
        return provider, model, warnings
        
    @log_function()
    def select_optimal_tier(
        self,
        task_description: str,
        default_tier: BudgetTier = BudgetTier.REMOTE_HEAVYWEIGHT
    ) -> BudgetTier:
        """
        Select the optimal tier for a task based on its description.
        
        Args:
            task_description: Description of the task
            default_tier: Default tier to use if no better match
            
        Returns:
            Selected BudgetTier
        """
        debug_log.info("budget_policy", "Selecting optimal tier for task")
        
        # This is a simplified version that would ideally use LLM assistance
        # for better classification of tasks based on their complexity
        
        # Simple keyword-based classification
        lightweight_keywords = [
            "file", "list", "search", "find", "read", "write", "copy",
            "move", "rename", "delete", "simple", "basic", "directory"
        ]
        
        midweight_keywords = [
            "refactor", "optimize", "debug", "analyze", "parse", "format",
            "transform", "convert", "generate", "test", "validate", "check"
        ]
        
        heavyweight_keywords = [
            "complex", "architecture", "design", "create", "implement",
            "algorithm", "advanced", "sophisticated", "intricate", "challenging",
            "difficult", "explain", "teach", "learn", "understand", "reasoning"
        ]
        
        # Convert to lowercase for matching
        task_lower = task_description.lower()
        
        # Count keyword matches for each tier
        lightweight_score = sum(1 for kw in lightweight_keywords if kw in task_lower)
        midweight_score = sum(1 for kw in midweight_keywords if kw in task_lower)
        heavyweight_score = sum(1 for kw in heavyweight_keywords if kw in task_lower)
        
        # Select tier with highest score
        if lightweight_score > midweight_score and lightweight_score > heavyweight_score:
            selected_tier = BudgetTier.LOCAL_LIGHTWEIGHT
        elif midweight_score > lightweight_score and midweight_score > heavyweight_score:
            selected_tier = BudgetTier.LOCAL_MIDWEIGHT
        elif heavyweight_score > 0:
            selected_tier = BudgetTier.REMOTE_HEAVYWEIGHT
        else:
            # Default to provided tier if no clear winner
            selected_tier = default_tier
            
        debug_log.debug("budget_policy", 
                       f"Selected tier {selected_tier.value} for task "
                       f"(scores: L={lightweight_score}, M={midweight_score}, H={heavyweight_score})")
        
        return selected_tier
        
    @log_function()
    def recommend_budget_optimization(self, budget_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide budget optimization recommendations.
        
        Args:
            budget_id: Budget ID (optional)
            
        Returns:
            Dictionary with optimization recommendations
        """
        debug_log.info("budget_policy", "Generating budget optimization recommendations")
        
        # Get budget summaries
        daily_summaries = budget_engine.get_budget_summary(
            budget_id=budget_id,
            period=BudgetPeriod.DAILY
        )
        
        monthly_summaries = budget_engine.get_budget_summary(
            budget_id=budget_id,
            period=BudgetPeriod.MONTHLY
        )
        
        # Get usage data
        daily_usage = usage_repo.get_usage_summary(
            period=BudgetPeriod.DAILY,
            budget_id=budget_id
        )
        
        monthly_usage = usage_repo.get_usage_summary(
            period=BudgetPeriod.MONTHLY,
            budget_id=budget_id
        )
        
        # Initialize recommendations
        recommendations = {
            "cost_reduction": [],
            "token_optimization": [],
            "policy_adjustments": [],
            "model_recommendations": [],
            "usage_insights": []
        }
        
        # Check for high-cost models
        if "provider" in daily_usage["groups"] and "model" in daily_usage["groups"]:
            # Find top 3 most expensive models by cost
            model_costs = []
            
            for provider, provider_data in daily_usage["groups"]["provider"].items():
                for model, model_data in daily_usage["groups"]["model"].items():
                    if model_data["cost"] > 0:
                        model_costs.append({
                            "provider": provider,
                            "model": model,
                            "cost": model_data["cost"],
                            "tokens": model_data["total_tokens"]
                        })
            
            # Sort by cost (highest first)
            model_costs.sort(key=lambda m: m["cost"], reverse=True)
            
            # Take top 3
            expensive_models = model_costs[:3]
            
            for model_info in expensive_models:
                # Get alternatives
                alternatives = budget_engine.get_model_recommendations(
                    provider=model_info["provider"],
                    model=model_info["model"],
                    context_size=model_info["tokens"]
                )
                
                if alternatives:
                    best_alt = alternatives[0]
                    recommendations["model_recommendations"].append({
                        "current_model": f"{model_info['provider']}/{model_info['model']}",
                        "current_cost": model_info["cost"],
                        "recommended_model": f"{best_alt['provider']}/{best_alt['model']}",
                        "estimated_savings": best_alt["savings"],
                        "savings_percent": best_alt["savings_percent"]
                    })
        
        # Check for budget utilization
        for summary in monthly_summaries:
            # Check if cost limit defined
            if summary.cost_limit:
                usage_percent = summary.cost_usage_percentage or 0
                
                # Check if significantly under budget
                if usage_percent < 0.5:
                    recommendations["policy_adjustments"].append({
                        "type": "reduce_cost_limit",
                        "current_limit": summary.cost_limit,
                        "recommended_limit": summary.cost_limit * 0.7,
                        "reason": "Current usage is significantly below the monthly limit"
                    })
                # Check if frequently exceeding budget
                elif usage_percent > 0.95:
                    recommendations["policy_adjustments"].append({
                        "type": "increase_cost_limit",
                        "current_limit": summary.cost_limit,
                        "recommended_limit": summary.cost_limit * 1.2,
                        "reason": "Current usage is consistently near or exceeding the monthly limit"
                    })
            
            # Check if token limit defined
            if summary.token_limit:
                usage_percent = summary.token_usage_percentage or 0
                
                # Check if significantly under budget
                if usage_percent < 0.5:
                    recommendations["policy_adjustments"].append({
                        "type": "reduce_token_limit",
                        "current_limit": summary.token_limit,
                        "recommended_limit": int(summary.token_limit * 0.7),
                        "reason": "Current usage is significantly below the monthly token limit"
                    })
                # Check if frequently exceeding budget
                elif usage_percent > 0.95:
                    recommendations["policy_adjustments"].append({
                        "type": "increase_token_limit",
                        "current_limit": summary.token_limit,
                        "recommended_limit": int(summary.token_limit * 1.2),
                        "reason": "Current usage is consistently near or exceeding the monthly token limit"
                    })
        
        # Usage pattern recommendations
        if "component" in monthly_usage["groups"]:
            # Find top component by usage
            components = []
            for comp, comp_data in monthly_usage["groups"]["component"].items():
                if comp_data["cost"] > 0:
                    components.append({
                        "name": comp,
                        "cost": comp_data["cost"],
                        "tokens": comp_data["total_tokens"]
                    })
            
            # Sort by cost (highest first)
            components.sort(key=lambda c: c["cost"], reverse=True)
            
            if components:
                # Top component by cost
                top_component = components[0]
                
                recommendations["usage_insights"].append({
                    "component": top_component["name"],
                    "cost": top_component["cost"],
                    "tokens": top_component["tokens"],
                    "description": f"Highest cost component, using {top_component['tokens']} tokens",
                    "recommendation": "Consider optimizing prompt design or caching results"
                })
                
        # Token optimization recommendations
        recommendations["token_optimization"].append({
            "type": "prompt_design",
            "description": "Optimize prompts to reduce token usage",
            "recommendation": "Review prompts for verbosity and unnecessary instructions"
        })
        
        recommendations["token_optimization"].append({
            "type": "caching",
            "description": "Implement caching for common queries",
            "recommendation": "Store and reuse results for frequently asked questions"
        })
        
        debug_log.info("budget_policy", 
                     f"Generated {len(recommendations['cost_reduction']) + len(recommendations['token_optimization']) + len(recommendations['policy_adjustments']) + len(recommendations['model_recommendations']) + len(recommendations['usage_insights'])} recommendations")
        
        return recommendations


# Create singleton instance
policy_enforcer = PolicyEnforcer()

# Alias for backward compatibility
policy_manager = policy_enforcer