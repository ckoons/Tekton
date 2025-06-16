"""
MCP Tools - Tool definitions for Apollo MCP service.

This module provides tool definitions for the Apollo MCP service,
using the FastMCP decorator-based approach.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

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

logger = logging.getLogger(__name__)

# Action Planning Tools

@mcp_capability(
    name="action_planning",
    description="Capability for planning actions based on context",
    modality="reasoning"
)
@mcp_tool(
    name="PlanActions",
    description="Plan a sequence of actions based on a goal and context",
    tags=["action", "planning", "sequence"],
    category="action_planning"
)
async def plan_actions(
    goal: str,
    context: Dict[str, Any],
    max_steps: int = 5,
    action_planner: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Plan a sequence of actions based on a goal and context.
    
    Args:
        goal: Goal to achieve
        context: Context information
        max_steps: Maximum number of steps in the plan
        action_planner: Action planner to use (injected)
        
    Returns:
        Action plan
    """
    if not action_planner:
        return {
            "error": "Action planner not provided"
        }
        
    try:
        # Create plan
        action_plan = await action_planner.create_plan(
            goal=goal,
            context=context,
            max_steps=max_steps
        )
        
        return {
            "goal": goal,
            "plan": action_plan,
            "steps": len(action_plan),
            "context_elements_used": action_planner.get_context_elements_used()
        }
    except Exception as e:
        logger.error(f"Error planning actions: {e}")
        return {
            "error": f"Error planning actions: {e}"
        }

@mcp_capability(
    name="action_execution",
    description="Capability for executing planned actions",
    modality="execution"
)
@mcp_tool(
    name="ExecuteAction",
    description="Execute a single action from a plan",
    tags=["action", "execution"],
    category="action_planning"
)
async def execute_action(
    action: Dict[str, Any],
    context: Dict[str, Any],
    action_planner: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Execute a single action from a plan.
    
    Args:
        action: Action to execute
        context: Context information
        action_planner: Action planner to use (injected)
        
    Returns:
        Execution result
    """
    if not action_planner:
        return {
            "error": "Action planner not provided"
        }
        
    try:
        # Execute action
        result = await action_planner.execute_action(
            action=action,
            context=context
        )
        
        return {
            "action": action,
            "result": result,
            "success": True,
            "updated_context": action_planner.get_updated_context()
        }
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return {
            "error": f"Error executing action: {e}",
            "success": False
        }

# Context Observation Tools

@mcp_capability(
    name="context_observation",
    description="Capability for observing and analyzing context",
    modality="analysis"
)
@mcp_tool(
    name="AnalyzeContext",
    description="Analyze the current context",
    tags=["context", "analysis"],
    category="context_observation"
)
async def analyze_context(
    context: Dict[str, Any],
    focus_areas: Optional[List[str]] = None,
    context_observer: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyze the current context.
    
    Args:
        context: Context to analyze
        focus_areas: Optional areas to focus the analysis on
        context_observer: Context observer to use (injected)
        
    Returns:
        Context analysis
    """
    if not context_observer:
        return {
            "error": "Context observer not provided"
        }
        
    try:
        # Analyze context
        analysis = await context_observer.analyze_context(
            context=context,
            focus_areas=focus_areas
        )
        
        return {
            "analysis": analysis,
            "focus_areas": focus_areas,
            "context_size": len(context),
            "insights": context_observer.get_insights()
        }
    except Exception as e:
        logger.error(f"Error analyzing context: {e}")
        return {
            "error": f"Error analyzing context: {e}"
        }

@mcp_capability(
    name="context_observation",
    description="Capability for observing and analyzing context",
    modality="analysis"
)
@mcp_tool(
    name="UpdateContext",
    description="Update the context with new information",
    tags=["context", "update"],
    category="context_observation"
)
async def update_context(
    context: Dict[str, Any],
    updates: Dict[str, Any],
    context_observer: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Update the context with new information.
    
    Args:
        context: Current context
        updates: Updates to apply to the context
        context_observer: Context observer to use (injected)
        
    Returns:
        Updated context
    """
    if not context_observer:
        return {
            "error": "Context observer not provided"
        }
        
    try:
        # Update context
        updated_context = await context_observer.update_context(
            context=context,
            updates=updates
        )
        
        return {
            "updated_context": updated_context,
            "changes": len(updates),
            "merge_conflicts": context_observer.get_merge_conflicts()
        }
    except Exception as e:
        logger.error(f"Error updating context: {e}")
        return {
            "error": f"Error updating context: {e}"
        }

# Message Handling Tools

@mcp_capability(
    name="message_handling",
    description="Capability for processing and generating messages",
    modality="communication"
)
@mcp_tool(
    name="GenerateResponse",
    description="Generate a response to a message",
    tags=["message", "response"],
    category="message_handling"
)
async def generate_response(
    message: Dict[str, Any],
    context: Dict[str, Any],
    response_type: str = "chat",
    message_handler: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Generate a response to a message.
    
    Args:
        message: Message to respond to
        context: Context information
        response_type: Type of response to generate
        message_handler: Message handler to use (injected)
        
    Returns:
        Generated response
    """
    if not message_handler:
        return {
            "error": "Message handler not provided"
        }
        
    try:
        # Generate response
        response = await message_handler.generate_response(
            message=message,
            context=context,
            response_type=response_type
        )
        
        return {
            "response": response,
            "response_type": response_type,
            "context_used": message_handler.get_context_used()
        }
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {
            "error": f"Error generating response: {e}"
        }

@mcp_capability(
    name="message_analysis",
    description="Capability for analyzing messages",
    modality="analysis"
)
@mcp_tool(
    name="AnalyzeMessage",
    description="Analyze a message for intent and content",
    tags=["message", "analysis"],
    category="message_handling"
)
async def analyze_message(
    message: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    message_handler: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyze a message for intent and content.
    
    Args:
        message: Message to analyze
        context: Optional context information
        message_handler: Message handler to use (injected)
        
    Returns:
        Message analysis
    """
    if not message_handler:
        return {
            "error": "Message handler not provided"
        }
        
    try:
        # Analyze message
        analysis = await message_handler.analyze_message(
            message=message,
            context=context
        )
        
        return {
            "analysis": analysis,
            "intent": analysis.get("intent"),
            "entities": analysis.get("entities", []),
            "sentiment": analysis.get("sentiment")
        }
    except Exception as e:
        logger.error(f"Error analyzing message: {e}")
        return {
            "error": f"Error analyzing message: {e}"
        }

# Prediction Tools

@mcp_capability(
    name="predictive_analysis",
    description="Capability for making predictions based on context",
    modality="prediction"
)
@mcp_tool(
    name="PredictNextAction",
    description="Predict the next action based on context and history",
    tags=["prediction", "action"],
    category="prediction"
)
async def predict_next_action(
    context: Dict[str, Any],
    history: List[Dict[str, Any]],
    predictive_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Predict the next action based on context and history.
    
    Args:
        context: Current context
        history: Action history
        predictive_engine: Predictive engine to use (injected)
        
    Returns:
        Predicted next action
    """
    if not predictive_engine:
        return {
            "error": "Predictive engine not provided"
        }
        
    try:
        # Predict next action
        prediction = await predictive_engine.predict_next_action(
            context=context,
            history=history
        )
        
        return {
            "prediction": prediction,
            "confidence": prediction.get("confidence", 0.0),
            "alternatives": prediction.get("alternatives", []),
            "rationale": prediction.get("rationale")
        }
    except Exception as e:
        logger.error(f"Error predicting next action: {e}")
        return {
            "error": f"Error predicting next action: {e}"
        }

@mcp_capability(
    name="predictive_analysis",
    description="Capability for making predictions based on context",
    modality="prediction"
)
@mcp_tool(
    name="PredictOutcome",
    description="Predict the outcome of an action",
    tags=["prediction", "outcome"],
    category="prediction"
)
async def predict_outcome(
    action: Dict[str, Any],
    context: Dict[str, Any],
    predictive_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Predict the outcome of an action.
    
    Args:
        action: Action to predict the outcome for
        context: Current context
        predictive_engine: Predictive engine to use (injected)
        
    Returns:
        Predicted outcome
    """
    if not predictive_engine:
        return {
            "error": "Predictive engine not provided"
        }
        
    try:
        # Predict outcome
        prediction = await predictive_engine.predict_outcome(
            action=action,
            context=context
        )
        
        return {
            "prediction": prediction,
            "confidence": prediction.get("confidence", 0.0),
            "potential_issues": prediction.get("potential_issues", []),
            "expected_impact": prediction.get("expected_impact")
        }
    except Exception as e:
        logger.error(f"Error predicting outcome: {e}")
        return {
            "error": f"Error predicting outcome: {e}"
        }

# Protocol Tools

@mcp_capability(
    name="protocol_enforcement",
    description="Capability for enforcing communication protocols",
    modality="communication"
)
@mcp_tool(
    name="ValidateProtocol",
    description="Validate if a message follows the protocol",
    tags=["protocol", "validation"],
    category="protocol"
)
async def validate_protocol(
    message: Dict[str, Any],
    protocol_name: str,
    protocol_enforcer: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Validate if a message follows the protocol.
    
    Args:
        message: Message to validate
        protocol_name: Name of the protocol to validate against
        protocol_enforcer: Protocol enforcer to use (injected)
        
    Returns:
        Validation result
    """
    if not protocol_enforcer:
        return {
            "error": "Protocol enforcer not provided"
        }
        
    try:
        # Validate protocol
        result = await protocol_enforcer.validate_message(
            message=message,
            protocol_name=protocol_name
        )
        
        return {
            "valid": result.get("valid", False),
            "protocol": protocol_name,
            "violations": result.get("violations", []),
            "suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        logger.error(f"Error validating protocol: {e}")
        return {
            "error": f"Error validating protocol: {e}"
        }

@mcp_capability(
    name="protocol_enforcement",
    description="Capability for enforcing communication protocols",
    modality="communication"
)
@mcp_tool(
    name="EnforceProtocol",
    description="Enforce protocol rules on a message",
    tags=["protocol", "enforcement"],
    category="protocol"
)
async def enforce_protocol(
    message: Dict[str, Any],
    protocol_name: str,
    protocol_enforcer: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Enforce protocol rules on a message.
    
    Args:
        message: Message to enforce protocol on
        protocol_name: Name of the protocol to enforce
        protocol_enforcer: Protocol enforcer to use (injected)
        
    Returns:
        Enforced message
    """
    if not protocol_enforcer:
        return {
            "error": "Protocol enforcer not provided"
        }
        
    try:
        # Enforce protocol
        result = await protocol_enforcer.enforce_protocol(
            message=message,
            protocol_name=protocol_name
        )
        
        return {
            "enforced_message": result.get("message"),
            "changes_made": result.get("changes", []),
            "protocol": protocol_name
        }
    except Exception as e:
        logger.error(f"Error enforcing protocol: {e}")
        return {
            "error": f"Error enforcing protocol: {e}"
        }

# Budget Tools

@mcp_capability(
    name="token_budgeting",
    description="Capability for managing token budgets",
    modality="resource"
)
@mcp_tool(
    name="AllocateBudget",
    description="Allocate a token budget for a task",
    tags=["budget", "allocation"],
    category="budget"
)
async def allocate_budget(
    task: Dict[str, Any],
    context_size: int,
    model_name: str,
    token_budget: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Allocate a token budget for a task.
    
    Args:
        task: Task to allocate budget for
        context_size: Size of the context in tokens
        model_name: Name of the model to use
        token_budget: Token budget manager to use (injected)
        
    Returns:
        Budget allocation
    """
    if not token_budget:
        return {
            "error": "Token budget manager not provided"
        }
        
    try:
        # Allocate budget
        allocation = await token_budget.allocate(
            task=task,
            context_size=context_size,
            model_name=model_name
        )
        
        return {
            "allocation": allocation,
            "input_tokens": allocation.get("input_tokens", 0),
            "output_tokens": allocation.get("output_tokens", 0),
            "total_tokens": allocation.get("total_tokens", 0),
            "model_name": model_name
        }
    except Exception as e:
        logger.error(f"Error allocating budget: {e}")
        return {
            "error": f"Error allocating budget: {e}"
        }

@mcp_capability(
    name="token_budgeting",
    description="Capability for managing token budgets",
    modality="resource"
)
@mcp_tool(
    name="OptimizeContext",
    description="Optimize a context to fit within a token budget",
    tags=["budget", "optimization"],
    category="budget"
)
async def optimize_context(
    context: Dict[str, Any],
    max_tokens: int,
    token_budget: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Optimize a context to fit within a token budget.
    
    Args:
        context: Context to optimize
        max_tokens: Maximum number of tokens
        token_budget: Token budget manager to use (injected)
        
    Returns:
        Optimized context
    """
    if not token_budget:
        return {
            "error": "Token budget manager not provided"
        }
        
    try:
        # Optimize context
        result = await token_budget.optimize_context(
            context=context,
            max_tokens=max_tokens
        )
        
        return {
            "optimized_context": result.get("context"),
            "original_tokens": result.get("original_tokens", 0),
            "optimized_tokens": result.get("optimized_tokens", 0),
            "savings": result.get("savings", 0),
            "trimmed_keys": result.get("trimmed_keys", [])
        }
    except Exception as e:
        logger.error(f"Error optimizing context: {e}")
        return {
            "error": f"Error optimizing context: {e}"
        }

# Registration functions

async def register_action_planning_tools(action_planner, tool_registry):
    """Register action planning tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Add action planner to tool kwargs
    plan_actions.action_planner = action_planner
    execute_action.action_planner = action_planner
    
    # Register tools with tool registry
    await tool_registry.register_tool(plan_actions._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(execute_action._mcp_tool_meta.to_dict())
    
    logger.info("Registered action planning tools with MCP service")

async def register_context_tools(context_observer, tool_registry):
    """Register context tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Add context observer to tool kwargs
    analyze_context.context_observer = context_observer
    update_context.context_observer = context_observer
    
    # Register tools with tool registry
    await tool_registry.register_tool(analyze_context._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(update_context._mcp_tool_meta.to_dict())
    
    logger.info("Registered context tools with MCP service")

async def register_message_tools(message_handler, tool_registry):
    """Register message tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Add message handler to tool kwargs
    generate_response.message_handler = message_handler
    analyze_message.message_handler = message_handler
    
    # Register tools with tool registry
    await tool_registry.register_tool(generate_response._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(analyze_message._mcp_tool_meta.to_dict())
    
    logger.info("Registered message tools with MCP service")

async def register_prediction_tools(predictive_engine, tool_registry):
    """Register prediction tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Add predictive engine to tool kwargs
    predict_next_action.predictive_engine = predictive_engine
    predict_outcome.predictive_engine = predictive_engine
    
    # Register tools with tool registry
    await tool_registry.register_tool(predict_next_action._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(predict_outcome._mcp_tool_meta.to_dict())
    
    logger.info("Registered prediction tools with MCP service")

async def register_protocol_tools(protocol_enforcer, tool_registry):
    """Register protocol tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Add protocol enforcer to tool kwargs
    validate_protocol.protocol_enforcer = protocol_enforcer
    enforce_protocol.protocol_enforcer = protocol_enforcer
    
    # Register tools with tool registry
    await tool_registry.register_tool(validate_protocol._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(enforce_protocol._mcp_tool_meta.to_dict())
    
    logger.info("Registered protocol tools with MCP service")

async def register_budget_tools(token_budget, tool_registry):
    """Register budget tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, using legacy tool registration")
        return
        
    # Add token budget to tool kwargs
    allocate_budget.token_budget = token_budget
    optimize_context.token_budget = token_budget
    
    # Register tools with tool registry
    await tool_registry.register_tool(allocate_budget._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(optimize_context._mcp_tool_meta.to_dict())
    
    logger.info("Registered budget tools with MCP service")


def get_all_tools(apollo_manager=None):
    """Get all Apollo MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    tools = []
    
    # Action planning tools
    tools.append(plan_actions._mcp_tool_meta.to_dict())
    tools.append(execute_action._mcp_tool_meta.to_dict())
    
    # Context observation tools
    tools.append(analyze_context._mcp_tool_meta.to_dict())
    tools.append(update_context._mcp_tool_meta.to_dict())
    
    # Message handling tools
    tools.append(generate_response._mcp_tool_meta.to_dict())
    tools.append(analyze_message._mcp_tool_meta.to_dict())
    
    # Prediction tools
    tools.append(predict_next_action._mcp_tool_meta.to_dict())
    tools.append(predict_outcome._mcp_tool_meta.to_dict())
    
    # Protocol tools
    tools.append(validate_protocol._mcp_tool_meta.to_dict())
    tools.append(enforce_protocol._mcp_tool_meta.to_dict())
    
    # Budget tools
    tools.append(allocate_budget._mcp_tool_meta.to_dict())
    tools.append(optimize_context._mcp_tool_meta.to_dict())
    
    logger.info(f"get_all_tools returning {len(tools)} Apollo MCP tools")
    return tools