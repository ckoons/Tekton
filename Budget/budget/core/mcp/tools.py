"""
MCP Tools - Tool definitions for Budget MCP service.

This module provides tool definitions for the Budget MCP service,
using the FastMCP decorator-based approach.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import uuid

# Import FastMCP decorators if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    fastmcp_available = True
except ImportError:
    # Define dummy decorators for backward compatibility
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def mcp_capability(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
            
    fastmcp_available = False

# Import Budget domain models 
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert
)

# Import Budget component adapters
from budget.adapters import apollo_adapter, rhetor_adapter, apollo_enhanced

# Import Budget core services
from budget.core.engine import budget_engine
from budget.core.allocation import allocation_manager

# Import Budget repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo, alert_repo, pricing_repo
)

logger = logging.getLogger(__name__)

# --- Budget Management Tools ---

@mcp_capability(
    name="budget_management",
    description="Capability for token budget management",
    modality="resource"
)
@mcp_tool(
    name="AllocateBudget",
    description="Allocate token budget for a task",
    tags=["budget", "allocation"],
    category="budget"
)
async def allocate_budget(
    context_id: str,
    amount: int,
    component: str,
    tier: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    task_type: str = "default",
    priority: int = 5,
    allocation_manager_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Handle a budget allocation request.
    
    Args:
        context_id: Context ID for this allocation
        amount: Number of tokens to allocate
        component: Component requesting allocation
        tier: Optional budget tier
        provider: Optional provider name
        model: Optional model name
        task_type: Type of task for this allocation
        priority: Priority of this allocation
        allocation_manager_instance: Allocation manager (injected)
        
    Returns:
        Allocation result
    """
    if not allocation_manager_instance:
        allocation_manager_instance = allocation_manager
        
    try:
        # Convert string tier to enum if provided
        if isinstance(tier, str) and tier:
            tier = apollo_adapter.tier_mapping.get(tier.lower(), BudgetTier.REMOTE_HEAVYWEIGHT)
        
        # Allocate tokens
        allocation = allocation_manager_instance.allocate_budget(
            context_id=context_id,
            component=component,
            tokens=amount,
            tier=tier,
            provider=provider,
            model=model,
            task_type=task_type,
            priority=priority
        )
        
        return {
            "allocation_id": allocation.allocation_id,
            "context_id": allocation.context_id,
            "amount": allocation.tokens_allocated,
            "remaining": allocation.remaining_tokens,
            "tier": tier.value if isinstance(tier, BudgetTier) else tier,
            "provider": provider,
            "model": model
        }
    except Exception as e:
        logger.error(f"Error allocating tokens: {str(e)}")
        return {
            "error": f"Error allocating tokens: {str(e)}",
            "context_id": context_id,
            "amount": 0,
            "remaining": 0
        }

@mcp_capability(
    name="budget_management",
    description="Capability for token budget management",
    modality="resource"
)
@mcp_tool(
    name="CheckBudget",
    description="Check if a request is within budget limits",
    tags=["budget", "check"],
    category="budget"
)
async def check_budget(
    provider: str,
    model: str,
    input_text: str = "",
    component: str = "",
    task_type: str = "default",
    context_id: Optional[str] = None,
    engine_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Check if a request is within budget limits.
    
    Args:
        provider: Provider name
        model: Model name
        input_text: Input text for token estimation
        component: Component requesting budget check
        task_type: Type of task
        context_id: Optional context ID
        engine_instance: Budget engine (injected)
        
    Returns:
        Budget check result
    """
    if not engine_instance:
        engine_instance = budget_engine
        
    try:
        # Use the most appropriate adapter based on the component
        if component == "apollo":
            allowed, info = apollo_adapter.check_budget(
                provider=provider,
                model=model,
                input_text=input_text,
                component=component,
                task_type=task_type
            )
        # Rhetor request
        elif component == "rhetor":
            allowed, info = rhetor_adapter.check_budget(
                provider=provider,
                model=model,
                input_text=input_text,
                component=component,
                task_type=task_type,
                context_id=context_id
            )
        # Generic request - use Rhetor's implementation as fallback
        else:
            allowed, info = rhetor_adapter.check_budget(
                provider=provider,
                model=model,
                input_text=input_text,
                component=component,
                task_type=task_type,
                context_id=context_id
            )
        
        return {
            "allowed": allowed,
            "info": info
        }
    except Exception as e:
        logger.error(f"Error checking budget: {str(e)}")
        return {
            "allowed": False,
            "info": {"error": str(e)}
        }

@mcp_capability(
    name="budget_management",
    description="Capability for token budget management",
    modality="resource"
)
@mcp_tool(
    name="RecordUsage",
    description="Record token usage for a request",
    tags=["budget", "usage"],
    category="budget"
)
async def record_usage(
    provider: str,
    model: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    input_text: Optional[str] = None,
    output_text: Optional[str] = None,
    component: str = "",
    task_type: str = "default",
    context_id: Optional[str] = None,
    allocation_id: Optional[str] = None,
    request_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    allocation_manager_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Record token usage for a request.
    
    Args:
        provider: Provider name
        model: Model name
        input_tokens: Number of input tokens (provide either this OR input_text)
        output_tokens: Number of output tokens (provide either this OR output_text)
        input_text: Input text for token counting (provide either this OR input_tokens)
        output_text: Output text for token counting (provide either this OR output_tokens)
        component: Component recording usage
        task_type: Type of task
        context_id: Context ID for this usage record
        allocation_id: Optional allocation ID for existing allocation
        request_id: Optional request ID
        metadata: Optional metadata
        allocation_manager_instance: Allocation manager (injected)
        
    Returns:
        Usage record result
    """
    if not allocation_manager_instance:
        allocation_manager_instance = allocation_manager
        
    try:
        # Ensure we have a context ID
        if not context_id:
            context_id = str(uuid.uuid4())
            
        # Ensure we have metadata
        if metadata is None:
            metadata = {}
            
        # Case 1: Full text provided
        if input_text is not None and output_text is not None:
            if component == "rhetor":
                result = rhetor_adapter.record_completion(
                    provider=provider,
                    model=model,
                    input_text=input_text,
                    output_text=output_text,
                    component=component,
                    task_type=task_type,
                    context_id=context_id,
                    metadata=metadata
                )
            else:
                # Use Rhetor's implementation as fallback
                result = rhetor_adapter.record_completion(
                    provider=provider,
                    model=model,
                    input_text=input_text,
                    output_text=output_text,
                    component=component,
                    task_type=task_type,
                    context_id=context_id,
                    metadata=metadata
                )
        # Case 2: Token counts provided
        elif input_tokens is not None and output_tokens is not None:
            # Record by allocation ID if provided
            if allocation_id:
                record = allocation_manager_instance.record_usage(
                    allocation_id=allocation_id,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    provider=provider,
                    model=model,
                    request_id=request_id
                )
                result = {
                    "context_id": context_id,
                    "allocation_id": allocation_id,
                    "recorded_tokens": input_tokens + output_tokens,
                    "remaining": record.remaining_tokens if record else 0,
                    "success": True
                }
            # Record by context ID otherwise
            else:
                record = allocation_manager_instance.record_usage(
                    context_id=context_id,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    provider=provider,
                    model=model,
                    request_id=request_id
                )
                result = {
                    "context_id": context_id,
                    "recorded_tokens": input_tokens + output_tokens,
                    "remaining": record.remaining_tokens if record else 0,
                    "success": True
                }
        else:
            raise ValueError("Must provide either input_text/output_text or input_tokens/output_tokens")
        
        return result
    except Exception as e:
        logger.error(f"Error recording usage: {str(e)}")
        return {
            "context_id": context_id,
            "recorded_tokens": 0,
            "remaining": 0,
            "success": False,
            "error": str(e)
        }

@mcp_capability(
    name="budget_management",
    description="Capability for token budget management",
    modality="resource"
)
@mcp_tool(
    name="GetBudgetStatus",
    description="Get budget status for a component or tier",
    tags=["budget", "status"],
    category="budget"
)
async def get_budget_status(
    period: str = "daily",
    tier: Optional[str] = None,
    provider: Optional[str] = None,
    component: Optional[str] = None,
    engine_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get budget status for a component or tier.
    
    Args:
        period: Budget period ('daily', 'weekly', 'monthly')
        tier: Optional tier to filter by
        provider: Optional provider to filter by
        component: Optional component name (determines response format)
        engine_instance: Budget engine (injected)
        
    Returns:
        Budget status
    """
    if not engine_instance:
        engine_instance = budget_engine
        
    try:
        # Handle different component-specific logic
        if component == "apollo":
            result = apollo_adapter.get_budget_status(
                period=period,
                tier=tier
            )
        elif component == "rhetor":
            summaries = engine_instance.get_budget_summary(
                budget_id=rhetor_adapter.rhetor_budget_id,
                period=period,
                tier=tier,
                provider=provider
            )
            
            # Format in Rhetor's expected format
            result = {
                "period": period,
                "success": True,
                "tiers": {}
            }
            
            for summary in summaries:
                tier_key = "all"
                if summary.tier:
                    tier_key = summary.tier.value
                    
                result["tiers"][tier_key] = {
                    "allocated": summary.total_tokens_allocated,
                    "used": summary.total_tokens_used,
                    "remaining": summary.remaining_tokens or 0,
                    "limit": summary.token_limit or 0,
                    "usage_percentage": summary.token_usage_percentage or 0.0,
                    "limit_exceeded": summary.token_limit_exceeded
                }
        else:
            # Use the generic format for other components
            summaries = engine_instance.get_budget_summary(
                period=period,
                tier=tier,
                provider=provider
            )
            
            # Format in a generic format
            result = {
                "period": period,
                "success": True,
                "summaries": [
                    {
                        "budget_id": summary.budget_id,
                        "tier": summary.tier.value if summary.tier else None,
                        "provider": summary.provider,
                        "component": summary.component,
                        "tokens_allocated": summary.total_tokens_allocated,
                        "tokens_used": summary.total_tokens_used,
                        "tokens_remaining": summary.remaining_tokens,
                        "token_limit": summary.token_limit,
                        "token_usage_percentage": summary.token_usage_percentage,
                        "token_limit_exceeded": summary.token_limit_exceeded,
                        "cost": summary.total_cost,
                        "cost_limit": summary.cost_limit,
                        "cost_usage_percentage": summary.cost_usage_percentage,
                        "cost_limit_exceeded": summary.cost_limit_exceeded
                    }
                    for summary in summaries
                ]
            }
        
        return result
    except Exception as e:
        logger.error(f"Error getting budget status: {str(e)}")
        return {
            "period": period,
            "success": False,
            "error": str(e)
        }

# --- Model Recommendation Tools ---

@mcp_capability(
    name="model_recommendations",
    description="Capability for model selection and recommendations",
    modality="optimization"
)
@mcp_tool(
    name="GetModelRecommendations",
    description="Get model recommendations based on budget and task",
    tags=["model", "recommendations", "budget"],
    category="optimization"
)
async def get_model_recommendations(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    task_type: str = "default",
    context_size: int = 4000,
    engine_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get model recommendations based on budget and task.
    
    Args:
        provider: Optional provider name
        model: Optional model name
        task_type: Type of task
        context_size: Approximate context size in tokens
        engine_instance: Budget engine (injected)
        
    Returns:
        Model recommendations
    """
    if not engine_instance:
        engine_instance = budget_engine
        
    try:
        # Get model recommendations
        recommendations = engine_instance.get_model_recommendations(
            provider=provider,
            model=model,
            task_type=task_type,
            context_size=context_size
        )
        
        return {
            "provider": provider,
            "model": model,
            "task_type": task_type,
            "context_size": context_size,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Error getting model recommendations: {str(e)}")
        return {
            "provider": provider,
            "model": model,
            "recommendations": [],
            "error": str(e)
        }

@mcp_capability(
    name="model_recommendations",
    description="Capability for model selection and recommendations",
    modality="optimization"
)
@mcp_tool(
    name="RouteWithBudgetAwareness",
    description="Route to appropriate model based on budget awareness",
    tags=["model", "routing", "budget"],
    category="optimization"
)
async def route_with_budget_awareness(
    input_text: str,
    task_type: str = "default",
    default_provider: Optional[str] = None,
    default_model: Optional[str] = None,
    component: str = "",
    engine_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Route to appropriate model based on budget awareness.
    
    Args:
        input_text: Input text for token estimation and task analysis
        task_type: Type of task
        default_provider: Default provider name
        default_model: Default model name
        component: Component requesting routing
        engine_instance: Budget engine (injected)
        
    Returns:
        Routing decision
    """
    if not engine_instance:
        engine_instance = budget_engine
        
    try:
        # Use appropriate adapter
        if component == "rhetor":
            provider, model, warnings = rhetor_adapter.route_with_budget_awareness(
                input_text=input_text,
                task_type=task_type,
                default_provider=default_provider,
                default_model=default_model,
                component=component
            )
        else:
            # Use Rhetor's implementation as fallback
            provider, model, warnings = rhetor_adapter.route_with_budget_awareness(
                input_text=input_text,
                task_type=task_type,
                default_provider=default_provider,
                default_model=default_model,
                component=component
            )
        
        return {
            "provider": provider,
            "model": model,
            "warnings": warnings,
            "original_provider": default_provider,
            "original_model": default_model,
            "is_downgraded": provider != default_provider or model != default_model
        }
    except Exception as e:
        logger.error(f"Error routing with budget awareness: {str(e)}")
        return {
            "provider": default_provider,
            "model": default_model,
            "warnings": [f"Error: {str(e)}"],
            "original_provider": default_provider,
            "original_model": default_model,
            "is_downgraded": False,
            "error": str(e)
        }

# --- Analytics Tools ---

@mcp_capability(
    name="budget_analytics",
    description="Capability for budget and usage analytics",
    modality="analytics"
)
@mcp_tool(
    name="GetUsageAnalytics",
    description="Get token usage analytics",
    tags=["budget", "analytics", "usage"],
    category="analytics"
)
async def get_usage_analytics(
    period: str = "daily",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    component: Optional[str] = None,
    task_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    engine_instance: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get token usage analytics.
    
    Args:
        period: Time period for analytics ('daily', 'weekly', 'monthly')
        provider: Optional provider name to filter by
        model: Optional model name to filter by
        component: Optional component name to filter by
        task_type: Optional task type to filter by
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        engine_instance: Budget engine (injected)
        
    Returns:
        Usage analytics
    """
    if not engine_instance:
        engine_instance = budget_engine
        
    try:
        # Parse dates if provided
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date)
        if end_date:
            end_date_obj = datetime.fromisoformat(end_date)
        
        # Get usage analytics
        result = apollo_enhanced.get_token_usage_analytics(
            period=period,
            provider=provider,
            model=model,
            component=component,
            task_type=task_type,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        return result
    except Exception as e:
        logger.error(f"Error getting usage analytics: {str(e)}")
        return {
            "period": period,
            "success": False,
            "error": str(e)
        }

# --- Registration Functions ---

async def register_budget_tools(engine, tool_registry):
    """Register budget management tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping budget tool registration")
        return
        
    # Add engine/manager to tool kwargs
    allocate_budget.allocation_manager_instance = allocation_manager
    check_budget.engine_instance = engine
    record_usage.allocation_manager_instance = allocation_manager
    get_budget_status.engine_instance = engine
    get_model_recommendations.engine_instance = engine
    route_with_budget_awareness.engine_instance = engine
    
    # Register tools with tool registry
    await tool_registry.register_tool(allocate_budget._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(check_budget._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(record_usage._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(get_budget_status._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(get_model_recommendations._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(route_with_budget_awareness._mcp_tool_meta.to_dict())
    
    logger.info("Registered budget management and model recommendation tools with MCP service")

async def register_analytics_tools(engine, tool_registry):
    """Register analytics tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping analytics tool registration")
        return
        
    # Add engine to tool kwargs
    get_usage_analytics.engine_instance = engine
    
    # Register tools with tool registry
    await tool_registry.register_tool(get_usage_analytics._mcp_tool_meta.to_dict())
    
    logger.info("Registered analytics tools with MCP service")

def get_all_tools(budget_engine_instance=None):
    """Get all Budget MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPTool
    
    tools = []
    
    # Budget management tools
    tools.append(allocate_budget._mcp_tool_meta.to_dict())
    tools.append(check_budget._mcp_tool_meta.to_dict())
    tools.append(record_usage._mcp_tool_meta.to_dict())
    tools.append(get_budget_status._mcp_tool_meta.to_dict())
    
    # Model recommendation tools
    tools.append(get_model_recommendations._mcp_tool_meta.to_dict())
    tools.append(route_with_budget_awareness._mcp_tool_meta.to_dict())
    
    # Analytics tools
    tools.append(get_usage_analytics._mcp_tool_meta.to_dict())
    
    return tools

def get_all_capabilities(budget_engine_instance=None):
    """Get all Budget MCP capabilities."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty capabilities list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPCapability
    
    capabilities = []
    
    # Add unique capabilities
    capability_names = set()
    
    # Budget management capability
    if "budget_management" not in capability_names:
        capabilities.append(MCPCapability(
            name="budget_management",
            description="Capability for token budget management",
            modality="resource"
        ))
        capability_names.add("budget_management")
    
    # Model recommendations capability
    if "model_recommendations" not in capability_names:
        capabilities.append(MCPCapability(
            name="model_recommendations",
            description="Capability for model selection and recommendations",
            modality="optimization"
        ))
        capability_names.add("model_recommendations")
    
    # Budget analytics capability
    if "budget_analytics" not in capability_names:
        capabilities.append(MCPCapability(
            name="budget_analytics",
            description="Capability for budget and usage analytics",
            modality="analytics"
        ))
        capability_names.add("budget_analytics")
    
    return capabilities