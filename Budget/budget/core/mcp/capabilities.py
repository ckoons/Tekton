"""
MCP capabilities for Budget Management System.

This module defines the Model Context Protocol capabilities that Budget provides
for resource allocation, cost tracking, model selection, and analytics.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class BudgetManagementCapability(MCPCapability):
    """Capability for budget allocation and resource management."""
    
    name = "budget_management"
    description = "Manage budgets, allocate resources, and track spending"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_budget",
            "get_budget",
            "update_budget",
            "delete_budget",
            "allocate_resources",
            "track_spending",
            "get_budget_status",
            "set_budget_limits",
            "calculate_remaining_budget"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "resource_management",
            "provider": "budget",
            "requires_auth": False,
            "rate_limited": True,
            "budget_types": ["project", "component", "model", "infrastructure"],
            "allocation_methods": ["percentage", "fixed", "dynamic", "priority_based"],
            "tracking_granularity": ["hourly", "daily", "weekly", "monthly"],
            "currency_support": ["USD", "EUR", "credits", "tokens"],
            "cost_categories": ["compute", "storage", "network", "licensing", "support"]
        }


class ModelRecommendationCapability(MCPCapability):
    """Capability for AI model selection and optimization recommendations."""
    
    name = "model_recommendations"
    description = "Recommend optimal AI models based on budget and performance constraints"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "recommend_model",
            "compare_models",
            "optimize_model_selection",
            "estimate_model_costs",
            "get_model_pricing",
            "analyze_cost_efficiency",
            "predict_usage_costs",
            "suggest_alternatives"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "ai_optimization",
            "provider": "budget",
            "requires_auth": False,
            "model_types": ["language", "vision", "embedding", "multimodal"],
            "providers": ["openai", "anthropic", "local", "custom"],
            "optimization_criteria": ["cost", "performance", "latency", "accuracy"],
            "recommendation_algorithms": ["cost_based", "performance_based", "hybrid"],
            "pricing_models": ["per_token", "per_request", "subscription", "compute_time"]
        }


class BudgetAnalyticsCapability(MCPCapability):
    """Capability for budget analytics and reporting."""
    
    name = "budget_analytics"
    description = "Analyze spending patterns, generate reports, and provide insights"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "generate_spending_report",
            "analyze_usage_patterns",
            "predict_future_costs",
            "identify_cost_anomalies",
            "compare_budget_periods",
            "calculate_roi",
            "track_budget_variance",
            "export_analytics_data"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "analytics",
            "provider": "budget",
            "requires_auth": False,
            "report_types": ["summary", "detailed", "trending", "comparative"],
            "analytics_periods": ["daily", "weekly", "monthly", "quarterly", "yearly"],
            "export_formats": ["json", "csv", "pdf", "excel"],
            "visualization_types": ["charts", "graphs", "tables", "dashboards"],
            "prediction_models": ["linear", "exponential", "seasonal", "machine_learning"]
        }


class CostOptimizationCapability(MCPCapability):
    """Capability for cost optimization and efficiency improvements."""
    
    name = "cost_optimization"
    description = "Optimize costs and improve resource efficiency"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "identify_optimization_opportunities",
            "suggest_cost_reductions",
            "optimize_resource_allocation",
            "recommend_scaling_strategies",
            "analyze_utilization_efficiency",
            "calculate_potential_savings",
            "implement_cost_controls",
            "monitor_optimization_impact"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "optimization",
            "provider": "budget",
            "requires_auth": False,
            "optimization_strategies": ["rightsizing", "scheduling", "caching", "batching"],
            "efficiency_metrics": ["cost_per_unit", "utilization_rate", "performance_ratio"],
            "saving_categories": ["compute", "storage", "licensing", "operational"],
            "implementation_complexity": ["low", "medium", "high"],
            "roi_calculation": ["immediate", "short_term", "long_term"]
        }


# Export all capabilities
__all__ = [
    "BudgetManagementCapability",
    "ModelRecommendationCapability",
    "BudgetAnalyticsCapability",
    "CostOptimizationCapability"
]