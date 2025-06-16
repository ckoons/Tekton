"""
Budget LLM Assistant

This module provides LLM-based budget analysis and optimization recommendations.
It leverages prompt templates to generate insights and suggestions for cost optimization.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

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

# Import budget models
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType,
    Budget, BudgetPolicy, BudgetAllocation, Alert, ProviderPricing
)

class BudgetAssistant:
    """
    LLM-based budget assistant that provides insights and recommendations.
    
    Uses prompt templates and LLM calls to analyze budget data and generate
    actionable recommendations for cost optimization.
    """
    
    def __init__(self, llm_client=None, engine=None):
        """
        Initialize the budget assistant.
        
        Args:
            llm_client: Client for making LLM API calls
            engine: Budget engine instance
        """
        self.llm_client = llm_client
        self.engine = engine
        self.prompt_templates = self._load_prompt_templates()
        
        # Set preferred model for each analysis type
        self.preferred_models = {
            "budget_analysis": "claude-3-sonnet",
            "cost_optimization": "claude-3-sonnet", 
            "model_selection": "claude-3-haiku"
        }
        
        debug_log.info("budget_assistant", "Budget Assistant initialized")
    
    def _load_prompt_templates(self) -> Dict[str, Any]:
        """
        Load prompt templates from the prompt_templates directory.
        
        Returns:
            Dict[str, Any]: Dictionary of loaded prompt templates
        """
        templates = {}
        template_dir = Path(__file__).parent.parent / "prompt_templates"
        
        if not template_dir.exists():
            debug_log.error("budget_assistant", f"Template directory not found: {template_dir}")
            return templates
        
        for template_file in template_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template = json.load(f)
                    templates[template["name"]] = template
                debug_log.info("budget_assistant", f"Loaded template: {template['name']}")
            except Exception as e:
                debug_log.error("budget_assistant", f"Error loading template {template_file}: {str(e)}")
        
        return templates
    
    async def analyze_budget(self, period: BudgetPeriod = BudgetPeriod.DAILY, days: int = 30) -> Dict[str, Any]:
        """
        Analyze budget usage patterns and provide insights.
        
        Args:
            period: Budget period to analyze
            days: Number of days of data to include
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        debug_log.info("budget_assistant", f"Analyzing budget for period: {period}")
        
        # Get usage data from the engine
        if not self.engine:
            debug_log.error("budget_assistant", "Budget engine not initialized")
            return {
                "error": "Budget engine not initialized",
                "success": False
            }
        
        # Get budget summaries and usage data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            summaries = await self.engine.get_budget_summaries(period=period)
            usage_records = await self.engine.get_usage_records(
                start_date=start_date,
                end_date=end_date,
                period=period
            )
            
            # Format data for the LLM
            usage_data = {
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summaries": [s.dict() for s in summaries],
                "usage_records": [r.dict() for r in usage_records]
            }
            
            # Check if LLM client is available
            if not self.llm_client:
                debug_log.error("budget_assistant", "LLM client not initialized")
                return {
                    "error": "LLM client not initialized",
                    "success": False,
                    "raw_data": usage_data
                }
            
            # Get the budget analysis template
            template = self.prompt_templates.get("budget_analysis")
            if not template:
                debug_log.error("budget_assistant", "Budget analysis template not found")
                return {
                    "error": "Budget analysis template not found",
                    "success": False,
                    "raw_data": usage_data
                }
            
            # Format the LLM request
            system_prompt = template["template"]["system"]
            user_prompt = template["template"]["user"].format(
                usage_data=json.dumps(usage_data, default=str)
            )
            
            # Call the LLM
            response = await self.llm_client.complete(
                model=self.preferred_models["budget_analysis"],
                system=system_prompt,
                prompt=user_prompt,
                temperature=0.2,
                max_tokens=1500
            )
            
            # Return the analysis
            return {
                "success": True,
                "analysis": response["content"],
                "raw_data": usage_data
            }
            
        except Exception as e:
            debug_log.error("budget_assistant", f"Error analyzing budget: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    async def get_optimization_recommendations(self, period: BudgetPeriod = BudgetPeriod.DAILY, days: int = 30) -> Dict[str, Any]:
        """
        Get cost optimization recommendations based on usage patterns.
        
        Args:
            period: Budget period to analyze
            days: Number of days of data to include
            
        Returns:
            Dict[str, Any]: Optimization recommendations
        """
        debug_log.info("budget_assistant", f"Getting optimization recommendations for period: {period}")
        
        # Check if engine is initialized
        if not self.engine:
            debug_log.error("budget_assistant", "Budget engine not initialized")
            return {
                "error": "Budget engine not initialized",
                "success": False
            }
        
        # Get budget data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            # Get usage data
            usage_records = await self.engine.get_usage_records(
                start_date=start_date,
                end_date=end_date,
                period=period
            )
            
            # Get pricing data
            pricing_data = await self.engine.get_pricing_data()
            
            # Format data for the LLM
            usage_data = {
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "usage_records": [r.dict() for r in usage_records],
                "aggregated_by_component": await self._aggregate_by_component(usage_records),
                "aggregated_by_model": await self._aggregate_by_model(usage_records)
            }
            
            pricing_formatted = {
                "models": [p.dict() for p in pricing_data]
            }
            
            # Check if LLM client is available
            if not self.llm_client:
                debug_log.error("budget_assistant", "LLM client not initialized")
                return {
                    "error": "LLM client not initialized",
                    "success": False,
                    "raw_data": {
                        "usage": usage_data,
                        "pricing": pricing_formatted
                    }
                }
            
            # Get the cost optimization template
            template = self.prompt_templates.get("cost_optimization")
            if not template:
                debug_log.error("budget_assistant", "Cost optimization template not found")
                return {
                    "error": "Cost optimization template not found",
                    "success": False,
                    "raw_data": {
                        "usage": usage_data,
                        "pricing": pricing_formatted
                    }
                }
            
            # Format the LLM request
            system_prompt = template["template"]["system"]
            user_prompt = template["template"]["user"].format(
                usage_data=json.dumps(usage_data, default=str),
                pricing_data=json.dumps(pricing_formatted, default=str)
            )
            
            # Call the LLM
            response = await self.llm_client.complete(
                model=self.preferred_models["cost_optimization"],
                system=system_prompt,
                prompt=user_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Return the recommendations
            return {
                "success": True,
                "recommendations": response["content"],
                "raw_data": {
                    "usage": usage_data,
                    "pricing": pricing_formatted
                }
            }
            
        except Exception as e:
            debug_log.error("budget_assistant", f"Error getting optimization recommendations: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    async def recommend_model(
        self,
        task_description: str,
        input_length: int,
        output_length: int,
        usage_frequency: int,
        budget_limit: float,
        priority_areas: str
    ) -> Dict[str, Any]:
        """
        Recommend the best model for a specific task based on requirements and budget.
        
        Args:
            task_description: Description of the task
            input_length: Expected input length in tokens
            output_length: Expected output length in tokens
            usage_frequency: How many times the task will be performed daily
            budget_limit: Maximum budget in USD
            priority_areas: Areas of importance (e.g., accuracy, speed)
            
        Returns:
            Dict[str, Any]: Model recommendations
        """
        debug_log.info("budget_assistant", "Getting model recommendations")
        
        # Check if engine is initialized
        if not self.engine:
            debug_log.error("budget_assistant", "Budget engine not initialized")
            return {
                "error": "Budget engine not initialized",
                "success": False
            }
        
        try:
            # Get pricing data
            pricing_data = await self.engine.get_pricing_data()
            
            # Format model data
            model_data = {
                "models": []
            }
            
            # Add model capabilities based on what we know
            for pricing in pricing_data:
                capabilities = []
                
                # Add capabilities based on model name and provider
                if "gpt-4" in pricing.model.lower():
                    capabilities = ["code_generation", "reasoning", "instruction_following", "tool_use"]
                elif "gpt-3.5" in pricing.model.lower():
                    capabilities = ["code_generation", "instruction_following"]
                elif "claude-3-opus" in pricing.model.lower():
                    capabilities = ["code_generation", "reasoning", "instruction_following", "tool_use"]
                elif "claude-3-sonnet" in pricing.model.lower():
                    capabilities = ["code_generation", "reasoning", "instruction_following"]
                elif "claude-3-haiku" in pricing.model.lower():
                    capabilities = ["code_generation", "instruction_following"]
                elif "llama" in pricing.model.lower() or "mistral" in pricing.model.lower():
                    capabilities = ["code_generation", "instruction_following"]
                else:
                    capabilities = ["instruction_following"]
                
                # Add context length based on model
                context_length = 4000  # Default
                if "gpt-4" in pricing.model.lower() and "32k" in pricing.model.lower():
                    context_length = 32000
                elif "gpt-4" in pricing.model.lower() and "128k" in pricing.model.lower():
                    context_length = 128000
                elif "gpt-4" in pricing.model.lower():
                    context_length = 8000
                elif "gpt-3.5" in pricing.model.lower() and "16k" in pricing.model.lower():
                    context_length = 16000
                elif "gpt-3.5" in pricing.model.lower():
                    context_length = 4000
                elif "claude-3-opus" in pricing.model.lower():
                    context_length = 200000
                elif "claude-3-sonnet" in pricing.model.lower():
                    context_length = 100000
                elif "claude-3-haiku" in pricing.model.lower():
                    context_length = 48000
                elif "llama-3" in pricing.model.lower() and "70b" in pricing.model.lower():
                    context_length = 8000
                
                model_data["models"].append({
                    "name": pricing.model,
                    "provider": pricing.provider,
                    "context_length": context_length,
                    "input_price": pricing.input_cost_per_token,
                    "output_price": pricing.output_cost_per_token,
                    "capabilities": capabilities
                })
            
            # Check if LLM client is available
            if not self.llm_client:
                debug_log.error("budget_assistant", "LLM client not initialized")
                return {
                    "error": "LLM client not initialized",
                    "success": False,
                    "raw_data": model_data
                }
            
            # Get the model selection template
            template = self.prompt_templates.get("model_selection")
            if not template:
                debug_log.error("budget_assistant", "Model selection template not found")
                return {
                    "error": "Model selection template not found",
                    "success": False,
                    "raw_data": model_data
                }
            
            # Format the LLM request
            system_prompt = template["template"]["system"]
            user_prompt = template["template"]["user"].format(
                task_description=task_description,
                input_length=input_length,
                output_length=output_length,
                usage_frequency=usage_frequency,
                budget_limit=budget_limit,
                priority_areas=priority_areas,
                model_data=json.dumps(model_data)
            )
            
            # Call the LLM
            response = await self.llm_client.complete(
                model=self.preferred_models["model_selection"],
                system=system_prompt,
                prompt=user_prompt,
                temperature=0.2,
                max_tokens=1500
            )
            
            # Return the recommendations
            return {
                "success": True,
                "recommendations": response["content"],
                "raw_data": model_data
            }
            
        except Exception as e:
            debug_log.error("budget_assistant", f"Error getting model recommendations: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    async def _aggregate_by_component(self, usage_records: List[Any]) -> Dict[str, Any]:
        """
        Aggregate usage data by component.
        
        Args:
            usage_records: List of usage records
            
        Returns:
            Dict[str, Any]: Aggregated data by component
        """
        result = {}
        
        for record in usage_records:
            component = record.component
            if component not in result:
                result[component] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "models": {}
                }
            
            # Update component totals
            result[component]["input_tokens"] += record.input_tokens
            result[component]["output_tokens"] += record.output_tokens
            result[component]["total_tokens"] += (record.input_tokens + record.output_tokens)
            result[component]["total_cost"] += record.total_cost
            
            # Update model breakdown
            model_key = f"{record.provider}/{record.model}"
            if model_key not in result[component]["models"]:
                result[component]["models"][model_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
            
            result[component]["models"][model_key]["input_tokens"] += record.input_tokens
            result[component]["models"][model_key]["output_tokens"] += record.output_tokens
            result[component]["models"][model_key]["total_tokens"] += (record.input_tokens + record.output_tokens)
            result[component]["models"][model_key]["total_cost"] += record.total_cost
        
        return result
    
    async def _aggregate_by_model(self, usage_records: List[Any]) -> Dict[str, Any]:
        """
        Aggregate usage data by model.
        
        Args:
            usage_records: List of usage records
            
        Returns:
            Dict[str, Any]: Aggregated data by model
        """
        result = {}
        
        for record in usage_records:
            model_key = f"{record.provider}/{record.model}"
            if model_key not in result:
                result[model_key] = {
                    "provider": record.provider,
                    "model": record.model,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "components": {}
                }
            
            # Update model totals
            result[model_key]["input_tokens"] += record.input_tokens
            result[model_key]["output_tokens"] += record.output_tokens
            result[model_key]["total_tokens"] += (record.input_tokens + record.output_tokens)
            result[model_key]["total_cost"] += record.total_cost
            
            # Update component breakdown
            component = record.component
            if component not in result[model_key]["components"]:
                result[model_key]["components"][component] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
            
            result[model_key]["components"][component]["input_tokens"] += record.input_tokens
            result[model_key]["components"][component]["output_tokens"] += record.output_tokens
            result[model_key]["components"][component]["total_tokens"] += (record.input_tokens + record.output_tokens)
            result[model_key]["components"][component]["total_cost"] += record.total_cost
        
        return result

# Factory function to create budget assistant
async def create_budget_assistant():
    """
    Factory function to create a budget assistant instance.
    
    Returns:
        BudgetAssistant: Initialized budget assistant
    """
    try:
        # Import here to avoid circular imports
        from budget.core.engine import get_budget_engine
        from budget.adapters.llm_adapter import get_llm_client
        
        engine = await get_budget_engine()
        llm_client = await get_llm_client()
        
        return BudgetAssistant(llm_client=llm_client, engine=engine)
    except Exception as e:
        debug_log.error("budget_assistant", f"Error creating budget assistant: {str(e)}")
        return BudgetAssistant()