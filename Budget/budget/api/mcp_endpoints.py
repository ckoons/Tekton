"""
MCP Protocol Endpoints for the Budget Component

This module provides Multi-Component Protocol (MCP) endpoints for the Budget component,
enabling standardized inter-component communication following Tekton's Single Port
Architecture pattern.
"""

import os
import json
import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, WebSocket, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

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

# Import domain models
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, TaskPriority,
    Budget, BudgetPolicy, BudgetAllocation, UsageRecord, Alert
)

# Import component adapters
from budget.adapters import apollo_adapter, rhetor_adapter, apollo_enhanced

# Import core services
from budget.core.engine import budget_engine, get_budget_engine
from budget.core.allocation import allocation_manager

# Import repositories
from budget.data.repository import (
    budget_repo, policy_repo, allocation_repo, usage_repo, alert_repo, pricing_repo
)

# Import FastMCP if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        mcp_processor,
        MCPClient
    )
    from tekton.mcp.fastmcp.schema import (
        ToolSchema,
        ProcessorSchema,
        MessageSchema,
        ResponseSchema,
        MCPRequest,
        MCPResponse,
        MCPCapability,
        MCPTool
    )
    from tekton.mcp.fastmcp.adapters import adapt_tool, adapt_processor
    from tekton.mcp.fastmcp.exceptions import MCPProcessingError
    from tekton.mcp.fastmcp.utils.endpoints import (
        create_mcp_router,
        add_standard_mcp_endpoints
    )
    fastmcp_available = True
except ImportError:
    fastmcp_available = False

# Import Budget MCP tools if FastMCP is available
if fastmcp_available:
    from budget.core.mcp import (
        get_all_tools,
        get_all_capabilities
    )

# Initialize logger
logger = logging.getLogger(__name__)

# Create MCP router using FastMCP if available
if fastmcp_available:
    mcp_router = create_mcp_router(
        prefix="/api/mcp",
        tags=["MCP Protocol"]
    )
else:
    # Create traditional router
    mcp_router = APIRouter(prefix="/api/mcp", tags=["MCP Protocol"])


# --- MCP Message Models (for backward compatibility) ---

class MCPMessage(BaseModel):
    """Base model for MCP messages."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = Field(default_factory=dict)


class MCPRequest(BaseModel):
    """Model for MCP request messages."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = Field(default_factory=dict)
    reply_to: Optional[str] = None
    timeout: Optional[float] = None


class MCPResponse(BaseModel):
    """Model for MCP response messages."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
    status: str
    error: Optional[str] = None


class MCPEvent(BaseModel):
    """Model for MCP event messages."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = Field(default_factory=dict)
    event_type: str
    severity: str = "info"


# --- Legacy MCP API Endpoint (for backward compatibility) ---

@mcp_router.post("/message", response_model=MCPResponse)
@log_function(level="INFO")
async def process_mcp_message(message: MCPRequest) -> MCPResponse:
    """
    Process an MCP protocol message.
    
    This endpoint handles incoming MCP messages from other components and routes
    them to the appropriate message handler based on the message type.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", f"Received MCP message: {message.message_type}")
    
    try:
        # Process based on message type
        if message.message_type == "budget.allocate_tokens":
            return await handle_allocate_tokens(message)
        elif message.message_type == "budget.check_budget":
            return await handle_check_budget(message)
        elif message.message_type == "budget.record_usage":
            return await handle_record_usage(message)
        elif message.message_type == "budget.get_budget_status":
            return await handle_get_budget_status(message)
        elif message.message_type == "budget.get_model_recommendations":
            return await handle_get_model_recommendations(message)
        elif message.message_type == "budget.route_with_budget_awareness":
            return await handle_route_with_budget_awareness(message)
        elif message.message_type == "budget.get_usage_analytics":
            return await handle_get_usage_analytics(message)
        else:
            # Unknown message type
            debug_log.warn("mcp_endpoints", f"Unknown message type: {message.message_type}")
            return MCPResponse(
                message_id=str(uuid.uuid4()),
                sender="budget",
                message_type="budget.error",
                request_id=message.message_id,
                status="error",
                error=f"Unknown message type: {message.message_type}",
                payload={}
            )
    except Exception as e:
        # Handle any exceptions
        debug_log.error("mcp_endpoints", f"Error processing message: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.error",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={}
        )


# --- Message Handlers (for backward compatibility) ---

@log_function(level="INFO")
async def handle_allocate_tokens(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.allocate_tokens message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling allocate_tokens message")
    
    # Extract parameters from payload
    payload = message.payload
    context_id = payload.get("context_id", str(uuid.uuid4()))
    amount = payload.get("amount", 0)
    
    # Use sender as component if not specified
    component = payload.get("component", message.sender)
    
    # Extract optional parameters
    tier = payload.get("tier")
    provider = payload.get("provider")
    model = payload.get("model")
    task_type = payload.get("task_type", "default")
    priority = payload.get("priority", 5)
    
    try:
        # Convert string tier to enum if provided
        if isinstance(tier, str) and tier:
            # Try to map through Apollo's adapter for compatibility
            tier = apollo_adapter.tier_mapping.get(tier.lower(), BudgetTier.REMOTE_HEAVYWEIGHT)
        
        # Allocate tokens
        allocation = allocation_manager.allocate_budget(
            context_id=context_id,
            component=component,
            tokens=amount,
            tier=tier,
            provider=provider,
            model=model,
            task_type=task_type,
            priority=priority
        )
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.allocation_response",
            request_id=message.message_id,
            status="success",
            payload={
                "allocation_id": allocation.allocation_id,
                "context_id": allocation.context_id,
                "amount": allocation.tokens_allocated,
                "remaining": allocation.remaining_tokens,
                "tier": tier.value if isinstance(tier, BudgetTier) else tier,
                "provider": provider,
                "model": model
            }
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error allocating tokens: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.allocation_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "context_id": context_id,
                "amount": 0,
                "remaining": 0
            }
        )


@log_function(level="INFO")
async def handle_check_budget(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.check_budget message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling check_budget message")
    
    # Extract parameters from payload
    payload = message.payload
    provider = payload.get("provider")
    model = payload.get("model")
    input_text = payload.get("input_text", "")
    
    # Use sender as component if not specified
    component = payload.get("component", message.sender)
    
    # Extract optional parameters
    task_type = payload.get("task_type", "default")
    context_id = payload.get("context_id")
    
    try:
        # Check if this is an Apollo request
        if message.sender == "apollo":
            allowed, info = apollo_adapter.check_budget(
                provider=provider,
                model=model,
                input_text=input_text,
                component=component,
                task_type=task_type
            )
        # Check if this is a Rhetor request
        elif message.sender == "rhetor":
            allowed, info = rhetor_adapter.check_budget(
                provider=provider,
                model=model,
                input_text=input_text,
                component=component,
                task_type=task_type,
                context_id=context_id
            )
        # Generic request
        else:
            # Use Rhetor's implementation as it's more feature-complete
            allowed, info = rhetor_adapter.check_budget(
                provider=provider,
                model=model,
                input_text=input_text,
                component=component,
                task_type=task_type,
                context_id=context_id
            )
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.check_response",
            request_id=message.message_id,
            status="success",
            payload={
                "allowed": allowed,
                "info": info
            }
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error checking budget: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.check_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "allowed": False,
                "info": {"error": str(e)}
            }
        )


@log_function(level="INFO")
async def handle_record_usage(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.record_usage message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling record_usage message")
    
    # Extract parameters from payload
    payload = message.payload
    context_id = payload.get("context_id", str(uuid.uuid4()))
    provider = payload.get("provider")
    model = payload.get("model")
    
    # Input/output text or token counts
    input_text = payload.get("input_text")
    output_text = payload.get("output_text")
    input_tokens = payload.get("input_tokens")
    output_tokens = payload.get("output_tokens")
    
    # Use sender as component if not specified
    component = payload.get("component", message.sender)
    
    # Extract optional parameters
    task_type = payload.get("task_type", "default")
    metadata = payload.get("metadata", {})
    allocation_id = payload.get("allocation_id")
    request_id = payload.get("request_id")
    
    try:
        # Handle recording based on data provided
        # Case 1: Full text provided
        if input_text is not None and output_text is not None:
            if message.sender == "rhetor":
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
                record = allocation_manager.record_usage(
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
                record = allocation_manager.record_usage(
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
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.usage_response",
            request_id=message.message_id,
            status="success",
            payload=result
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error recording usage: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.usage_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "context_id": context_id,
                "recorded_tokens": 0,
                "remaining": 0,
                "success": False
            }
        )


@log_function(level="INFO")
async def handle_get_budget_status(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.get_budget_status message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling get_budget_status message")
    
    # Extract parameters from payload
    payload = message.payload
    period = payload.get("period", "daily")
    tier = payload.get("tier")
    provider = payload.get("provider")
    
    try:
        # Check if this is an Apollo request
        if message.sender == "apollo":
            result = apollo_adapter.get_budget_status(
                period=period,
                tier=tier
            )
        # Check if this is a Rhetor request
        elif message.sender == "rhetor":
            summaries = budget_engine.get_budget_summary(
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
        # Generic request
        else:
            # Get summaries
            summaries = budget_engine.get_budget_summary(
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
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.status_response",
            request_id=message.message_id,
            status="success",
            payload=result
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error getting budget status: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.status_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "period": period,
                "success": False
            }
        )


@log_function(level="INFO")
async def handle_get_model_recommendations(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.get_model_recommendations message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling get_model_recommendations message")
    
    # Extract parameters from payload
    payload = message.payload
    provider = payload.get("provider")
    model = payload.get("model")
    task_type = payload.get("task_type", "default")
    context_size = payload.get("context_size", 4000)
    
    try:
        # Get model recommendations
        recommendations = budget_engine.get_model_recommendations(
            provider=provider,
            model=model,
            task_type=task_type,
            context_size=context_size
        )
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.recommendations_response",
            request_id=message.message_id,
            status="success",
            payload={
                "provider": provider,
                "model": model,
                "task_type": task_type,
                "context_size": context_size,
                "recommendations": recommendations
            }
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error getting model recommendations: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.recommendations_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "provider": provider,
                "model": model,
                "recommendations": []
            }
        )


@log_function(level="INFO")
async def handle_route_with_budget_awareness(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.route_with_budget_awareness message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling route_with_budget_awareness message")
    
    # Extract parameters from payload
    payload = message.payload
    input_text = payload.get("input_text", "")
    task_type = payload.get("task_type", "default")
    default_provider = payload.get("default_provider")
    default_model = payload.get("default_model")
    
    # Use sender as component if not specified
    component = payload.get("component", message.sender)
    
    try:
        # Check if this is a Rhetor request
        if message.sender == "rhetor":
            provider, model, warnings = rhetor_adapter.route_with_budget_awareness(
                input_text=input_text,
                task_type=task_type,
                default_provider=default_provider,
                default_model=default_model,
                component=component
            )
        # Generic request
        else:
            # Use Rhetor's implementation as fallback
            provider, model, warnings = rhetor_adapter.route_with_budget_awareness(
                input_text=input_text,
                task_type=task_type,
                default_provider=default_provider,
                default_model=default_model,
                component=component
            )
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.routing_response",
            request_id=message.message_id,
            status="success",
            payload={
                "provider": provider,
                "model": model,
                "warnings": warnings,
                "original_provider": default_provider,
                "original_model": default_model,
                "is_downgraded": provider != default_provider or model != default_model
            }
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error routing with budget awareness: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.routing_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "provider": default_provider,
                "model": default_model,
                "warnings": [f"Error: {str(e)}"],
                "original_provider": default_provider,
                "original_model": default_model,
                "is_downgraded": False
            }
        )


@log_function(level="INFO")
async def handle_get_usage_analytics(message: MCPRequest) -> MCPResponse:
    """
    Handle a budget.get_usage_analytics message.
    
    Args:
        message: The MCP request message
        
    Returns:
        MCPResponse: The response message
    """
    debug_log.info("mcp_endpoints", "Handling get_usage_analytics message")
    
    # Extract parameters from payload
    payload = message.payload
    period = payload.get("period", "daily")
    provider = payload.get("provider")
    model = payload.get("model")
    component = payload.get("component")
    task_type = payload.get("task_type")
    
    # Custom date range (optional)
    start_date_str = payload.get("start_date")
    end_date_str = payload.get("end_date")
    
    try:
        # Parse dates if provided
        start_date = None
        end_date = None
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str)
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str)
        
        # Get usage analytics
        result = apollo_enhanced.get_token_usage_analytics(
            period=period,
            provider=provider,
            model=model,
            component=component,
            task_type=task_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create response
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.analytics_response",
            request_id=message.message_id,
            status="success",
            payload=result
        )
    except Exception as e:
        debug_log.error("mcp_endpoints", f"Error getting usage analytics: {str(e)}")
        return MCPResponse(
            message_id=str(uuid.uuid4()),
            sender="budget",
            message_type="budget.analytics_response",
            request_id=message.message_id,
            status="error",
            error=str(e),
            payload={
                "period": period,
                "success": False,
                "error": str(e)
            }
        )


# --- MCP Event Publishing ---

@log_function(level="INFO")
async def publish_budget_event(
    event_type: str,
    payload: Dict[str, Any],
    severity: str = "info"
) -> MCPEvent:
    """
    Publish a budget event using the MCP protocol.
    
    This function creates an MCPEvent and can be used to publish events to 
    Hermes for distribution to other components.
    
    Args:
        event_type: Type of event
        payload: Event payload
        severity: Event severity (info, warning, error)
        
    Returns:
        MCPEvent: The created event
    """
    debug_log.info("mcp_endpoints", f"Publishing budget event: {event_type}")
    
    # Create event
    event = MCPEvent(
        message_id=str(uuid.uuid4()),
        sender="budget",
        message_type="budget.event",
        event_type=event_type,
        severity=severity,
        payload=payload,
        timestamp=datetime.now()
    )
    
    # TODO: Publish to Hermes via WebSocket or HTTP
    # For now, just log the event
    debug_log.info("mcp_endpoints", f"Event {event_type}: {payload}")
    
    return event


# --- FastMCP Integration ---

# Define FastMCP handler functions
async def get_capabilities_func(engine):
    """Get Budget MCP capabilities."""
    if not fastmcp_available:
        return []
        
    return get_all_capabilities(engine)

async def get_tools_func(engine):
    """Get Budget MCP tools."""
    if not fastmcp_available:
        return []
        
    return get_all_tools(engine)

async def process_request_func(engine, request):
    """Process an MCP request."""
    # Make sure the engine is initialized
    if not isinstance(engine, dict) and getattr(engine, "is_initialized", None) and not engine.is_initialized:
        await engine.initialize()
    
    try:
        # Check if tool is supported
        tool_name = request.tool
        
        # Define a mapping of tool names to handler functions
        from budget.core.mcp.tools import (
            allocate_budget, check_budget, record_usage, get_budget_status,
            get_model_recommendations, route_with_budget_awareness, get_usage_analytics
        )
        
        tool_handlers = {
            # Budget Management
            "AllocateBudget": allocate_budget,
            "CheckBudget": check_budget,
            "RecordUsage": record_usage,
            "GetBudgetStatus": get_budget_status,
            
            # Model Recommendations
            "GetModelRecommendations": get_model_recommendations,
            "RouteWithBudgetAwareness": route_with_budget_awareness,
            
            # Analytics
            "GetUsageAnalytics": get_usage_analytics
        }
        
        # Check if tool is supported
        if tool_name not in tool_handlers:
            return MCPResponse(
                status="error",
                error=f"Unsupported tool: {tool_name}",
                result=None
            )
            
        # Call the appropriate handler
        handler = tool_handlers[tool_name]
        
        # Set engine instance if needed
        parameters = request.parameters or {}
        if "engine_instance" not in parameters:
            parameters["engine_instance"] = engine
            
        if "allocation_manager_instance" not in parameters:
            parameters["allocation_manager_instance"] = allocation_manager
            
        # Execute handler
        result = await handler(**parameters)
        
        return MCPResponse(
            status="success",
            result=result,
            error=None
        )
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return MCPResponse(
            status="error",
            error=f"Error processing request: {str(e)}",
            result=None
        )

# Add standard MCP endpoints if FastMCP is available
if fastmcp_available:
    try:
        # Add standard MCP endpoints to the router
        add_standard_mcp_endpoints(
            router=mcp_router,
            get_capabilities_func=get_capabilities_func,
            get_tools_func=get_tools_func,
            process_request_func=process_request_func,
            component_manager_dependency=get_budget_engine
        )
        
        logger.info("Added FastMCP endpoints to Budget API")
    except Exception as e:
        logger.error(f"Error adding FastMCP endpoints: {e}")