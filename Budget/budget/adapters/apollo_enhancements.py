"""
Apollo Integration Enhancements

This module extends the Apollo adapter with additional features to improve
integration with the Budget component.
"""

import os
import json
import logging
import asyncio
import uuid
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

# Import base Apollo adapter
from budget.adapters.apollo import apollo_adapter


class ApolloEnhancedAdapter:
    """
    Enhanced adapter for Apollo's token budget system.
    
    This class extends the base Apollo adapter with advanced features like
    provider guidance, comprehensive pricing migration, and improved analytics.
    """
    
    def __init__(self):
        """Initialize the enhanced Apollo adapter."""
        # Use the base adapter for core functionality
        self.base_adapter = apollo_adapter
        self.apollo_budget_id = self.base_adapter.apollo_budget_id
    
    @log_function()
    def provide_model_guidance(
        self,
        context_id: str,
        task_type: str,
        task_description: str,
        provider_preferences: Optional[List[str]] = None,
        max_cost: Optional[float] = None,
        preferred_tier: Optional[Union[str, BudgetTier]] = None
    ) -> Dict[str, Any]:
        """
        Provide guidance on model selection based on task requirements.
        
        Args:
            context_id: Context identifier
            task_type: Type of task (code, chat, reasoning, etc.)
            task_description: Description of the task
            provider_preferences: Preferred providers in order
            max_cost: Maximum cost allowed for the task
            preferred_tier: Preferred model tier
            
        Returns:
            Dictionary with model recommendations
        """
        debug_log.info("apollo_enhanced", 
                     f"Providing model guidance for {task_type} task")
        
        # Convert string tier to enum if needed
        if isinstance(preferred_tier, str) and preferred_tier:
            try:
                preferred_tier = self.base_adapter.tier_mapping.get(
                    preferred_tier.lower(), BudgetTier.REMOTE_HEAVYWEIGHT
                )
            except:
                preferred_tier = BudgetTier.REMOTE_HEAVYWEIGHT
        
        # Default to heavyweight tier if not specified
        preferred_tier = preferred_tier or BudgetTier.REMOTE_HEAVYWEIGHT
        
        # Get budget summaries
        summaries = budget_engine.get_budget_summary(
            budget_id=self.apollo_budget_id,
            period=BudgetPeriod.DAILY
        )
        
        # Determine if we're approaching daily budget limits
        approaching_limit = False
        if summaries:
            for summary in summaries:
                if (summary.token_limit and summary.token_usage_percentage and 
                    summary.token_usage_percentage > 0.7):
                    approaching_limit = True
                    break
                    
                if (summary.cost_limit and summary.cost_usage_percentage and 
                    summary.cost_usage_percentage > 0.7):
                    approaching_limit = True
                    break
        
        # Get all available models from pricing repository
        all_pricing = pricing_repo.get_all()
        
        # Filter models based on constraints
        candidate_models = []
        
        for pricing in all_pricing:
            # Skip if provider is not in preferences (if specified)
            if (provider_preferences and 
                pricing.provider not in provider_preferences):
                continue
                
            # Estimate cost for a typical request (1000 input, 800 output tokens)
            estimated_cost = (
                1000 * pricing.input_cost_per_token + 
                800 * pricing.output_cost_per_token
            )
            
            # Skip if above max cost (if specified)
            if max_cost is not None and estimated_cost > max_cost:
                continue
                
            # Determine model tier
            model_tier = self._determine_model_tier(pricing.provider, pricing.model)
            
            # Add to candidates
            candidate_models.append({
                "provider": pricing.provider,
                "model": pricing.model,
                "tier": model_tier.value if model_tier else None,
                "estimated_cost": estimated_cost,
                "input_cost_per_token": pricing.input_cost_per_token,
                "output_cost_per_token": pricing.output_cost_per_token
            })
        
        # Sort candidates by preference
        candidate_models = self._sort_model_candidates(
            candidate_models,
            task_type=task_type,
            provider_preferences=provider_preferences,
            preferred_tier=preferred_tier,
            approaching_limit=approaching_limit
        )
        
        # Return top 3 recommendations
        recommended_models = candidate_models[:3]
        
        return {
            "context_id": context_id,
            "task_type": task_type,
            "approaching_budget_limit": approaching_limit,
            "preferred_tier": preferred_tier.value if preferred_tier else None,
            "recommended_models": recommended_models,
            "reasoning": self._generate_recommendation_reasoning(
                task_type=task_type,
                task_description=task_description,
                approaching_limit=approaching_limit,
                recommended_models=recommended_models,
                preferred_tier=preferred_tier
            )
        }
    
    def _determine_model_tier(self, provider: str, model: str) -> Optional[BudgetTier]:
        """
        Determine the tier of a model based on its capabilities.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            Budget tier or None if unknown
        """
        # This is a simplified heuristic - a real implementation would use a more
        # comprehensive model capability database
        
        # Anthropic models
        if provider == "anthropic":
            if "opus" in model.lower():
                return BudgetTier.REMOTE_HEAVYWEIGHT
            elif "sonnet" in model.lower():
                return BudgetTier.REMOTE_HEAVYWEIGHT
            elif "haiku" in model.lower():
                return BudgetTier.LOCAL_MIDWEIGHT
            else:
                return BudgetTier.REMOTE_HEAVYWEIGHT
                
        # OpenAI models
        elif provider == "openai":
            if "gpt-4" in model.lower():
                return BudgetTier.REMOTE_HEAVYWEIGHT
            elif "gpt-3.5" in model.lower():
                return BudgetTier.LOCAL_MIDWEIGHT
            else:
                return BudgetTier.REMOTE_HEAVYWEIGHT
                
        # Local models
        elif provider in ["ollama", "simulated"]:
            return BudgetTier.LOCAL_LIGHTWEIGHT
            
        # Unknown model
        return None
    
    def _sort_model_candidates(
        self,
        candidates: List[Dict[str, Any]],
        task_type: str,
        provider_preferences: Optional[List[str]],
        preferred_tier: Optional[BudgetTier],
        approaching_limit: bool
    ) -> List[Dict[str, Any]]:
        """
        Sort model candidates based on preferences and constraints.
        
        Args:
            candidates: List of candidate models
            task_type: Type of task
            provider_preferences: Preferred providers in order
            preferred_tier: Preferred model tier
            approaching_limit: Whether we're approaching budget limits
            
        Returns:
            Sorted list of model candidates
        """
        # Task-specific provider preferences
        task_provider_weights = {
            "code": {"anthropic": 1.0, "openai": 0.8, "ollama": 0.6, "simulated": 0.3},
            "chat": {"openai": 1.0, "anthropic": 0.9, "ollama": 0.7, "simulated": 0.3},
            "reasoning": {"anthropic": 1.0, "openai": 0.9, "ollama": 0.5, "simulated": 0.3},
            "creative": {"openai": 1.0, "anthropic": 0.8, "ollama": 0.6, "simulated": 0.3},
            "default": {"anthropic": 1.0, "openai": 0.9, "ollama": 0.7, "simulated": 0.3}
        }
        
        # Get weights for this task type
        weights = task_provider_weights.get(task_type, task_provider_weights["default"])
        
        # Add score to each candidate
        for candidate in candidates:
            # Base score
            score = 1.0
            
            # Provider score
            provider = candidate["provider"]
            provider_weight = weights.get(provider, 0.5)
            score *= provider_weight
            
            # Provider preference boost
            if provider_preferences and provider in provider_preferences:
                # Boost based on position in preferences
                position = provider_preferences.index(provider)
                preference_boost = 1.0 / (position + 1)
                score *= (1.0 + preference_boost)
            
            # Tier match
            if preferred_tier and candidate["tier"]:
                candidate_tier = BudgetTier(candidate["tier"])
                if candidate_tier == preferred_tier:
                    score *= 1.5
                # If approaching limit and preferred tier is heavyweight, boost lower tiers
                elif approaching_limit and preferred_tier == BudgetTier.REMOTE_HEAVYWEIGHT:
                    if candidate_tier == BudgetTier.LOCAL_MIDWEIGHT:
                        score *= 1.3
                    elif candidate_tier == BudgetTier.LOCAL_LIGHTWEIGHT:
                        score *= 1.1
            
            # Cost efficiency (lower cost gets higher score)
            if candidate["estimated_cost"] > 0:
                cost_factor = 1.0 / (1.0 + 100 * candidate["estimated_cost"])
                score *= (1.0 + cost_factor)
            
            # Store score
            candidate["score"] = score
        
        # Sort by score (descending)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates
    
    def _generate_recommendation_reasoning(
        self,
        task_type: str,
        task_description: str,
        approaching_limit: bool,
        recommended_models: List[Dict[str, Any]],
        preferred_tier: Optional[BudgetTier]
    ) -> str:
        """
        Generate reasoning for model recommendations.
        
        Args:
            task_type: Type of task
            task_description: Description of the task
            approaching_limit: Whether we're approaching budget limits
            recommended_models: List of recommended models
            preferred_tier: Preferred model tier
            
        Returns:
            Reasoning text
        """
        # Build reasoning
        reasoning_parts = []
        
        # Task-based reasoning
        task_reasoning = {
            "code": "This task involves code generation or analysis, where Claude models typically excel.",
            "chat": "This conversational task benefits from models with strong dialog capabilities.",
            "reasoning": "This task requires complex reasoning, favoring models with strong analytical abilities.",
            "creative": "This creative task benefits from models with strong generative capabilities.",
            "default": "This task requires a balanced model with good general capabilities."
        }
        
        reasoning_parts.append(task_reasoning.get(task_type, task_reasoning["default"]))
        
        # Budget limit reasoning
        if approaching_limit:
            reasoning_parts.append(
                "Your daily budget is approaching its limit, so more cost-effective "
                "models are prioritized."
            )
        
        # Tier preference reasoning
        if preferred_tier:
            tier_reasoning = {
                BudgetTier.LOCAL_LIGHTWEIGHT: "You indicated a preference for lightweight models, which are typically faster and more cost-effective.",
                BudgetTier.LOCAL_MIDWEIGHT: "You indicated a preference for mid-tier models, balancing capability and cost.",
                BudgetTier.REMOTE_HEAVYWEIGHT: "You indicated a preference for high-capability models, optimizing for performance over cost."
            }
            reasoning_parts.append(tier_reasoning.get(preferred_tier, ""))
        
        # Model-specific reasoning
        if recommended_models:
            top_model = recommended_models[0]
            if top_model["provider"] == "anthropic" and "claude" in top_model["model"].lower():
                if "opus" in top_model["model"].lower():
                    reasoning_parts.append(
                        f"{top_model['model']} offers Claude's highest capabilities "
                        f"for complex tasks, though at higher cost."
                    )
                elif "sonnet" in top_model["model"].lower():
                    reasoning_parts.append(
                        f"{top_model['model']} offers excellent performance across most tasks "
                        f"with a good balance of capability and cost."
                    )
                elif "haiku" in top_model["model"].lower():
                    reasoning_parts.append(
                        f"{top_model['model']} offers good capabilities at significantly lower "
                        f"cost than heavier models."
                    )
            elif top_model["provider"] == "openai":
                if "gpt-4" in top_model["model"].lower():
                    reasoning_parts.append(
                        f"{top_model['model']} offers strong performance across most tasks, "
                        f"particularly excelling at instruction following."
                    )
                elif "gpt-3.5" in top_model["model"].lower():
                    reasoning_parts.append(
                        f"{top_model['model']} offers good capabilities at much lower "
                        f"cost than GPT-4 models."
                    )
            elif top_model["provider"] == "ollama":
                reasoning_parts.append(
                    f"{top_model['model']} provides local inference capabilities at zero cost, "
                    f"though with some performance trade-offs."
                )
        
        # Join reasoning parts
        return " ".join(reasoning_parts)
    
    @log_function()
    def get_token_usage_analytics(
        self,
        period: Union[BudgetPeriod, str] = BudgetPeriod.DAILY,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        component: Optional[str] = None,
        task_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed analytics for token usage.
        
        Args:
            period: Budget period
            provider: Filter by provider
            model: Filter by model
            component: Filter by component
            task_type: Filter by task type
            start_date: Custom start date
            end_date: Custom end date
            
        Returns:
            Dictionary with token usage analytics
        """
        debug_log.info("apollo_enhanced", 
                     f"Getting token usage analytics for {period}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        # If start_date and end_date provided, use custom range
        if start_date and end_date:
            custom_range = True
        else:
            custom_range = False
            # Calculate date range based on period
            now = datetime.now()
            
            if period == BudgetPeriod.HOURLY:
                start_date = now.replace(minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(hours=1)
            elif period == BudgetPeriod.DAILY:
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            elif period == BudgetPeriod.WEEKLY:
                # Start of week (Monday)
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=7)
            elif period == BudgetPeriod.MONTHLY:
                # Start of month
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # End of month (start of next month)
                if now.month == 12:
                    end_date = datetime(now.year + 1, 1, 1)
                else:
                    end_date = datetime(now.year, now.month + 1, 1)
        
        # Get usage records
        filters = {}
        if provider:
            filters["provider"] = provider
        if model:
            filters["model"] = model
        if component:
            filters["component"] = component
        if task_type:
            filters["task_type"] = task_type
            
        # Get usage records
        records = usage_repo.get_by_time_range(
            start_time=start_date,
            end_time=end_date,
            budget_id=self.apollo_budget_id,
            **filters
        )
        
        # Calculate usage statistics
        total_input_tokens = sum(record.input_tokens for record in records)
        total_output_tokens = sum(record.output_tokens for record in records)
        total_tokens = total_input_tokens + total_output_tokens
        total_cost = sum(record.total_cost for record in records)
        
        # Record count
        record_count = len(records)
        
        # Group by provider
        providers = {}
        for record in records:
            provider_key = record.provider
            if provider_key not in providers:
                providers[provider_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                    "count": 0,
                    "models": {}
                }
            
            # Update provider stats
            providers[provider_key]["input_tokens"] += record.input_tokens
            providers[provider_key]["output_tokens"] += record.output_tokens
            providers[provider_key]["total_tokens"] += record.input_tokens + record.output_tokens
            providers[provider_key]["cost"] += record.total_cost
            providers[provider_key]["count"] += 1
            
            # Update model stats
            model_key = record.model
            if model_key not in providers[provider_key]["models"]:
                providers[provider_key]["models"][model_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                    "count": 0
                }
            
            providers[provider_key]["models"][model_key]["input_tokens"] += record.input_tokens
            providers[provider_key]["models"][model_key]["output_tokens"] += record.output_tokens
            providers[provider_key]["models"][model_key]["total_tokens"] += record.input_tokens + record.output_tokens
            providers[provider_key]["models"][model_key]["cost"] += record.total_cost
            providers[provider_key]["models"][model_key]["count"] += 1
        
        # Group by component
        components = {}
        for record in records:
            component_key = record.component
            if component_key not in components:
                components[component_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                    "count": 0
                }
            
            # Update component stats
            components[component_key]["input_tokens"] += record.input_tokens
            components[component_key]["output_tokens"] += record.output_tokens
            components[component_key]["total_tokens"] += record.input_tokens + record.output_tokens
            components[component_key]["cost"] += record.total_cost
            components[component_key]["count"] += 1
        
        # Group by task type
        task_types = {}
        for record in records:
            task_type_key = record.task_type
            if task_type_key not in task_types:
                task_types[task_type_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                    "count": 0
                }
            
            # Update task type stats
            task_types[task_type_key]["input_tokens"] += record.input_tokens
            task_types[task_type_key]["output_tokens"] += record.output_tokens
            task_types[task_type_key]["total_tokens"] += record.input_tokens + record.output_tokens
            task_types[task_type_key]["cost"] += record.total_cost
            task_types[task_type_key]["count"] += 1
        
        # Get time window statistics if enough data is available
        time_series = None
        if len(records) >= 10:
            # Calculate time window
            time_range = end_date - start_date
            
            # Choose appropriate window size
            if time_range.total_seconds() <= 3600:  # 1 hour or less
                window_size = timedelta(minutes=5)
                window_format = "%H:%M"
            elif time_range.total_seconds() <= 86400:  # 1 day or less
                window_size = timedelta(hours=1)
                window_format = "%H:00"
            elif time_range.total_seconds() <= 604800:  # 1 week or less
                window_size = timedelta(days=1)
                window_format = "%m-%d"
            else:  # more than 1 week
                window_size = timedelta(days=7)
                window_format = "Week %U"
            
            # Sort records by timestamp
            sorted_records = sorted(records, key=lambda x: x.timestamp)
            
            # Create time windows
            windows = []
            current_time = start_date
            while current_time < end_date:
                windows.append({
                    "start": current_time,
                    "end": current_time + window_size,
                    "label": current_time.strftime(window_format),
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0,
                    "count": 0
                })
                current_time += window_size
            
            # Assign records to windows
            for record in sorted_records:
                for window in windows:
                    if window["start"] <= record.timestamp < window["end"]:
                        window["input_tokens"] += record.input_tokens
                        window["output_tokens"] += record.output_tokens
                        window["cost"] += record.total_cost
                        window["count"] += 1
                        break
            
            # Remove empty windows from the end
            while windows and windows[-1]["count"] == 0:
                windows.pop()
                
            # Convert to time series format
            time_series = {
                "labels": [w["label"] for w in windows],
                "input_tokens": [w["input_tokens"] for w in windows],
                "output_tokens": [w["output_tokens"] for w in windows],
                "costs": [w["cost"] for w in windows],
                "counts": [w["count"] for w in windows]
            }
        
        # Return analytics data
        return {
            "period": period.value if not custom_range else "custom",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "record_count": record_count,
            "providers": providers,
            "components": components,
            "task_types": task_types,
            "time_series": time_series,
            "budget_id": self.apollo_budget_id
        }
    
    @log_function()
    async def migrate_pricing_data(self) -> Dict[str, Any]:
        """
        Migrate pricing data from Apollo.
        
        Returns:
            Migration results
        """
        debug_log.info("apollo_enhanced", "Migrating pricing data from Apollo")
        
        results = {
            "success": True,
            "pricing_records_migrated": 0,
            "errors": []
        }
        
        try:
            # Define standard pricing for Apollo models
            # This is a simplified version of what would be fetched from Apollo's API
            pricing_data = {
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
                "ollama": {
                    "llama3": {
                        "input_cost_per_token": 0.0,
                        "output_cost_per_token": 0.0,
                    }
                },
                "simulated": {
                    "simulated-standard": {
                        "input_cost_per_token": 0.0,
                        "output_cost_per_token": 0.0,
                    }
                }
            }
            
            # Try to fetch from Apollo API
            try:
                response = requests.get(f"{self.base_adapter.api_base_url}/api/apollo/pricing")
                if response.status_code == 200:
                    api_pricing = response.json()
                    
                    # Merge API pricing with default pricing
                    for provider, models in api_pricing.items():
                        if provider not in pricing_data:
                            pricing_data[provider] = {}
                            
                        for model, model_pricing in models.items():
                            pricing_data[provider][model] = model_pricing
            except Exception as e:
                debug_log.warn("apollo_enhanced", 
                             f"Could not fetch pricing from Apollo API: {str(e)}")
                results["errors"].append(f"Could not fetch pricing from Apollo API: {str(e)}")
            
            # Create pricing records
            for provider, models in pricing_data.items():
                for model, price_info in models.items():
                    try:
                        # Check if pricing already exists
                        existing_pricing = pricing_repo.get_current_pricing(provider, model)
                        
                        if existing_pricing:
                            # Skip if already exists
                            debug_log.info("apollo_enhanced", 
                                         f"Pricing for {provider}/{model} already exists, skipping")
                            continue
                            
                        # Create pricing record
                        pricing = ProviderPricing(
                            pricing_id=str(uuid.uuid4()),
                            provider=provider,
                            model=model,
                            price_type=PriceType.TOKEN_BASED,
                            input_cost_per_token=price_info["input_cost_per_token"],
                            output_cost_per_token=price_info["output_cost_per_token"],
                            version="1.0",
                            source="apollo_migration",
                            verified=True,
                            effective_date=datetime.now()
                        )
                        
                        # Save pricing
                        pricing_repo.create(pricing)
                        
                        results["pricing_records_migrated"] += 1
                    except Exception as e:
                        debug_log.error("apollo_enhanced", f"Error migrating pricing: {str(e)}")
                        results["errors"].append(f"Error migrating pricing for {provider}/{model}: {str(e)}")
            
            # Update results
            if results["errors"]:
                results["success"] = False
            
            debug_log.info("apollo_enhanced", 
                         f"Pricing migration completed: {results['pricing_records_migrated']} records")
            
            return results
        except Exception as e:
            debug_log.error("apollo_enhanced", f"Error during pricing migration: {str(e)}")
            results["success"] = False
            results["errors"].append(f"Error during pricing migration: {str(e)}")
            return results
    
    @log_function()
    def get_completion_efficiency(
        self,
        provider: str,
        model: str,
        context_id: Optional[str] = None,
        period: Union[BudgetPeriod, str] = BudgetPeriod.DAILY
    ) -> Dict[str, Any]:
        """
        Get completion efficiency metrics for a provider/model.
        
        Args:
            provider: Provider name
            model: Model name
            context_id: Filter by context ID (optional)
            period: Budget period
            
        Returns:
            Dictionary with efficiency metrics
        """
        debug_log.info("apollo_enhanced", 
                     f"Getting completion efficiency for {provider}/{model}")
        
        # Convert string period to enum if needed
        if isinstance(period, str):
            period = BudgetPeriod(period)
        
        # Calculate date range based on period
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
            # Default to daily
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
        
        # Get usage records
        filters = {
            "provider": provider,
            "model": model
        }
        
        if context_id:
            filters["context_id"] = context_id
        
        records = usage_repo.get_by_time_range(
            start_time=start_time,
            end_time=end_time,
            budget_id=self.apollo_budget_id,
            **filters
        )
        
        # If no records, return empty metrics
        if not records:
            return {
                "provider": provider,
                "model": model,
                "period": period.value,
                "context_id": context_id,
                "data_available": False,
                "message": "No usage data available for this query"
            }
        
        # Calculate efficiency metrics
        total_input_tokens = sum(record.input_tokens for record in records)
        total_output_tokens = sum(record.output_tokens for record in records)
        total_tokens = total_input_tokens + total_output_tokens
        total_cost = sum(record.total_cost for record in records)
        
        # Calculate effectiveness ratio (output tokens / input tokens)
        effectiveness_ratio = total_output_tokens / total_input_tokens if total_input_tokens > 0 else 0
        
        # Calculate cost efficiency (output tokens per dollar)
        cost_efficiency = total_output_tokens / total_cost if total_cost > 0 else float('inf')
        
        # Calculate average cost per completion
        avg_cost_per_completion = total_cost / len(records) if records else 0
        
        # Calculate average tokens per completion
        avg_tokens_per_completion = total_tokens / len(records) if records else 0
        
        # Group by task type
        task_types = {}
        for record in records:
            task_type = record.task_type
            if task_type not in task_types:
                task_types[task_type] = {
                    "count": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0
                }
            
            task_types[task_type]["count"] += 1
            task_types[task_type]["input_tokens"] += record.input_tokens
            task_types[task_type]["output_tokens"] += record.output_tokens
            task_types[task_type]["cost"] += record.total_cost
        
        # Calculate efficiency metrics for each task type
        for task_type, stats in task_types.items():
            stats["avg_input_tokens"] = stats["input_tokens"] / stats["count"] if stats["count"] > 0 else 0
            stats["avg_output_tokens"] = stats["output_tokens"] / stats["count"] if stats["count"] > 0 else 0
            stats["effectiveness_ratio"] = stats["output_tokens"] / stats["input_tokens"] if stats["input_tokens"] > 0 else 0
            stats["cost_efficiency"] = stats["output_tokens"] / stats["cost"] if stats["cost"] > 0 else float('inf')
            stats["avg_cost_per_completion"] = stats["cost"] / stats["count"] if stats["count"] > 0 else 0
        
        # Get comparison with other providers
        other_providers = []
        if total_tokens > 0:
            # Get records for other providers with the same task types
            task_type_list = list(task_types.keys())
            
            other_records = usage_repo.get_by_time_range(
                start_time=start_time,
                end_time=end_time,
                budget_id=self.apollo_budget_id
            )
            
            # Group by provider and model
            provider_models = {}
            for record in other_records:
                if record.provider == provider and record.model == model:
                    continue
                    
                if record.task_type not in task_type_list:
                    continue
                    
                key = f"{record.provider}/{record.model}"
                if key not in provider_models:
                    provider_models[key] = {
                        "provider": record.provider,
                        "model": record.model,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                        "count": 0
                    }
                
                provider_models[key]["input_tokens"] += record.input_tokens
                provider_models[key]["output_tokens"] += record.output_tokens
                provider_models[key]["cost"] += record.total_cost
                provider_models[key]["count"] += 1
            
            # Calculate metrics for each alternative
            for key, stats in provider_models.items():
                if stats["input_tokens"] > 0 and stats["count"] > 0:
                    effectiveness = stats["output_tokens"] / stats["input_tokens"]
                    cost_eff = stats["output_tokens"] / stats["cost"] if stats["cost"] > 0 else float('inf')
                    
                    # Comparison relative to current model
                    effectiveness_diff = (effectiveness / effectiveness_ratio - 1) * 100 if effectiveness_ratio > 0 else 0
                    cost_diff = (cost_eff / cost_efficiency - 1) * 100 if cost_efficiency > 0 and cost_efficiency != float('inf') else 0
                    
                    other_providers.append({
                        "provider": stats["provider"],
                        "model": stats["model"],
                        "effectiveness_ratio": effectiveness,
                        "effectiveness_diff": effectiveness_diff,
                        "cost_efficiency": cost_eff,
                        "cost_diff": cost_diff,
                        "count": stats["count"]
                    })
            
            # Sort by cost efficiency
            other_providers.sort(key=lambda x: x["cost_efficiency"], reverse=True)
        
        # Build recommendations based on the data
        recommendations = []
        
        # Check if there are more efficient alternatives
        if other_providers:
            more_efficient = [p for p in other_providers if p["cost_diff"] > 20 and p["count"] >= 3]
            if more_efficient:
                top_alt = more_efficient[0]
                recommendations.append(
                    f"Consider using {top_alt['provider']}/{top_alt['model']} for similar tasks "
                    f"({top_alt['cost_diff']:.1f}% more cost-efficient)"
                )
        
        # Check task type efficiency
        if len(task_types) > 1:
            # Find most and least efficient task types
            task_efficiency = [(task, stats["cost_efficiency"]) 
                             for task, stats in task_types.items()]
            task_efficiency.sort(key=lambda x: x[1], reverse=True)
            
            if len(task_efficiency) >= 2:
                most_efficient = task_efficiency[0]
                least_efficient = task_efficiency[-1]
                
                if most_efficient[1] > least_efficient[1] * 1.5:
                    recommendations.append(
                        f"This model is most efficient for '{most_efficient[0]}' tasks "
                        f"and least efficient for '{least_efficient[0]}' tasks"
                    )
        
        # Check if very short prompts are used
        avg_input = total_input_tokens / len(records) if records else 0
        if avg_input < 50:
            recommendations.append(
                "Your prompts are shorter than average. Consider providing more context "
                "to get more detailed responses."
            )
        
        # Check if very long prompts are used
        if avg_input > 3000:
            recommendations.append(
                "Your prompts are longer than average. Consider using more concise prompts "
                "to reduce token usage and costs."
            )
        
        # Return metrics
        return {
            "provider": provider,
            "model": model,
            "period": period.value,
            "context_id": context_id,
            "data_available": True,
            "completion_count": len(records),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "effectiveness_ratio": effectiveness_ratio,
            "cost_efficiency": cost_efficiency,
            "avg_cost_per_completion": avg_cost_per_completion,
            "avg_tokens_per_completion": avg_tokens_per_completion,
            "task_types": task_types,
            "alternatives": other_providers[:5],  # Limit to top 5
            "recommendations": recommendations
        }


# Create singleton instance
apollo_enhanced = ApolloEnhancedAdapter()