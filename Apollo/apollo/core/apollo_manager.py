"""
Apollo Manager Module.

This module provides a high-level manager that coordinates the Context Observer,
Predictive Engine, and Action Planner components. It integrates their functionality
and provides a simplified interface for the Apollo API.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable

from apollo.models.context import (
    ContextState,
    ContextPrediction,
    ContextAction,
    ContextHealth
)
from apollo.core.context_observer import ContextObserver
from apollo.core.predictive_engine import PredictiveEngine
from apollo.core.action_planner import ActionPlanner
from apollo.core.interfaces.rhetor import RhetorInterface
from apollo.core.message_handler import MessageHandler
from apollo.core.protocol_enforcer import ProtocolEnforcer
from apollo.core.token_budget import TokenBudgetManager

# Configure logging first
logger = logging.getLogger(__name__)

# Import FastMCP integration
try:
    # Import FastMCP functionality
    from tekton.mcp.fastmcp import (
        MCPClient,
        adapt_tool,
        adapt_processor
    )
    from tekton.mcp.fastmcp.schema import (
        MCPRequest, 
        MCPResponse,
        MCPTool,
        MCPCapability
    )
    
    # Import our MCP module tools
    from apollo.core.mcp import (
        fastmcp_available,
        register_action_planning_tools,
        register_context_tools,
        register_message_tools,
        register_prediction_tools,
        register_protocol_tools,
        register_budget_tools,
        get_capabilities,
        get_tools
    )
    fastmcp_available = True
except ImportError as e:
    fastmcp_available = False
    logger.warning(f"FastMCP integration not available: {e}. Some MCP functionality will be limited")


class ApolloManager:
    """
    High-level manager for Apollo components.
    
    This class coordinates the Context Observer, Predictive Engine, and Action
    Planner components, providing a simplified interface for the Apollo API.
    """
    
    def __init__(
        self,
        rhetor_interface: Optional[RhetorInterface] = None,
        data_dir: Optional[str] = None,
        enable_predictive: bool = True,
        enable_actions: bool = True,
        enable_message_handler: bool = True,
        enable_protocol_enforcer: bool = True,
        enable_token_budget: bool = True
    ):
        """
        Initialize the Apollo Manager.
        
        Args:
            rhetor_interface: Interface for communicating with Rhetor
            data_dir: Root directory for storing data
            enable_predictive: Whether to enable the predictive engine
            enable_actions: Whether to enable the action planner
            enable_message_handler: Whether to enable the message handler
            enable_protocol_enforcer: Whether to enable the protocol enforcer
            enable_token_budget: Whether to enable the token budget
        """
        # Set up data directory
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo by default
            default_data_dir = os.path.join(
                TektonEnviron.get('TEKTON_DATA_DIR', 
                              os.path.join(TektonEnviron.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Sub-directories for component data
        context_data_dir = os.path.join(self.data_dir, "context_data")
        prediction_data_dir = os.path.join(self.data_dir, "prediction_data")
        action_data_dir = os.path.join(self.data_dir, "action_data")
        message_data_dir = os.path.join(self.data_dir, "message_data")
        protocol_data_dir = os.path.join(self.data_dir, "protocol_data")
        budget_data_dir = os.path.join(self.data_dir, "budget_data")
        
        # Create rhetor interface if not provided
        self.rhetor_interface = rhetor_interface or RhetorInterface()
        
        # Initialize components
        self.context_observer = ContextObserver(
            rhetor_interface=self.rhetor_interface,
            data_dir=context_data_dir
        )
        
        self.predictive_engine = PredictiveEngine(
            context_observer=self.context_observer,
            data_dir=prediction_data_dir
        ) if enable_predictive else None
        
        self.action_planner = ActionPlanner(
            context_observer=self.context_observer,
            predictive_engine=self.predictive_engine,
            data_dir=action_data_dir
        ) if enable_actions else None
        
        # Initialize additional components for MCP
        self.message_handler = MessageHandler(
            component_name="apollo",
            data_dir=message_data_dir
        ) if enable_message_handler else None
        
        self.protocol_enforcer = ProtocolEnforcer(
            data_dir=protocol_data_dir
        ) if enable_protocol_enforcer else None
        
        self.token_budget_manager = TokenBudgetManager(
            data_dir=budget_data_dir
        ) if enable_token_budget else None
        
        # For task management
        self.is_running = False
        
        # Set up component connections
        self._connect_components()
    
    def _connect_components(self):
        """Set up connections between components."""
        # Connect context observer to predictive engine
        if self.context_observer and self.predictive_engine:
            # Register callbacks for health changes
            self.context_observer.register_callback(
                "on_health_change",
                self._on_context_health_change
            )
        
        # Connect predictive engine to action planner
        if self.predictive_engine and self.action_planner:
            # No specific callbacks needed currently
            pass
    
    async def _on_context_health_change(self, context_state: ContextState, previous_health: ContextHealth):
        """
        Handle context health change events.
        
        Args:
            context_state: Current context state
            previous_health: Previous health status
        """
        # If health degraded significantly, trigger immediate prediction and action planning
        if (previous_health in [ContextHealth.EXCELLENT, ContextHealth.GOOD] and 
            context_state.health in [ContextHealth.POOR, ContextHealth.CRITICAL]):
            
            logger.info(f"Context {context_state.context_id} health degraded from {previous_health} to {context_state.health}")
            
            # Immediate action planning happens in action planner's own loop
            pass
    
    async def start(self):
        """Start all Apollo components."""
        if self.is_running:
            logger.warning("Apollo Manager is already running")
            return
            
        self.is_running = True
        
        # Start context observer
        await self.context_observer.start()
        
        # Start predictive engine if enabled
        if self.predictive_engine:
            await self.predictive_engine.start()
            
        # Start action planner if enabled
        if self.action_planner:
            await self.action_planner.start()
            
        # Start message handler if enabled
        if self.message_handler:
            await self.message_handler.start()
            
        # Start protocol enforcer if enabled
        if self.protocol_enforcer:
            await self.protocol_enforcer.start()
            
        # Start token budget manager if enabled
        if self.token_budget_manager:
            await self.token_budget_manager.start()
            
        # Register MCP tools if FastMCP is available
        if fastmcp_available:
            try:
                # Create a dummy tool registry for now
                # In a full implementation, we would use a proper tool registry
                class DummyToolRegistry:
                    async def register_tool(self, tool_spec):
                        logger.info(f"Registering tool: {tool_spec.get('name')}")
                        return tool_spec.get("id")
                
                tool_registry = DummyToolRegistry()
                
                # Register tools for each component
                if self.action_planner:
                    await register_action_planning_tools(self.action_planner, tool_registry)
                    
                if self.context_observer:
                    await register_context_tools(self.context_observer, tool_registry)
                    
                if self.message_handler:
                    await register_message_tools(self.message_handler, tool_registry)
                    
                if self.predictive_engine:
                    await register_prediction_tools(self.predictive_engine, tool_registry)
                    
                if self.protocol_enforcer:
                    await register_protocol_tools(self.protocol_enforcer, tool_registry)
                    
                if self.token_budget_manager:
                    await register_budget_tools(self.token_budget_manager, tool_registry)
                    
                logger.info("Registered MCP tools")
            except Exception as e:
                logger.error(f"Error registering MCP tools: {e}")
            
        logger.info("Apollo Manager started")
    
    async def stop(self):
        """Stop all Apollo components."""
        if not self.is_running:
            logger.warning("Apollo Manager is not running")
            return
            
        self.is_running = False
        
        # Stop components in reverse order
        if self.token_budget_manager:
            await self.token_budget_manager.stop()
            
        if self.protocol_enforcer:
            await self.protocol_enforcer.stop()
            
        if self.message_handler:
            await self.message_handler.stop()
            
        if self.action_planner:
            await self.action_planner.stop()
            
        if self.predictive_engine:
            await self.predictive_engine.stop()
            
        await self.context_observer.stop()
        
        logger.info("Apollo Manager stopped")
    
    # Context Observer Proxy Methods
    
    def get_context_state(self, context_id: str) -> Optional[ContextState]:
        """
        Get the current state of a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            ContextState or None if not found
        """
        return self.context_observer.get_context_state(context_id)
    
    def get_all_context_states(self) -> List[ContextState]:
        """
        Get states for all active contexts.
        
        Returns:
            List of ContextState objects
        """
        return self.context_observer.get_all_context_states()
    
    def get_context_history(self, context_id: str, limit: int = None) -> List[Any]:
        """
        Get history for a specific context.
        
        Args:
            context_id: Context identifier
            limit: Maximum number of records to return
            
        Returns:
            List of context history records
        """
        return self.context_observer.get_context_history(context_id, limit)
    
    def get_health_distribution(self) -> Dict[ContextHealth, int]:
        """
        Get distribution of context health across all active contexts.
        
        Returns:
            Dictionary mapping health status to count
        """
        return self.context_observer.get_health_distribution()
    
    def get_critical_contexts(self) -> List[ContextState]:
        """
        Get contexts with critical health status.
        
        Returns:
            List of ContextState objects with critical health
        """
        return self.context_observer.get_critical_contexts()
    
    async def suggest_action(self, context_id: str) -> Optional[ContextAction]:
        """
        Suggest an action for a context based on its health.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Suggested ContextAction or None
        """
        return await self.context_observer.suggest_action(context_id)
    
    # Predictive Engine Proxy Methods
    
    def get_prediction(self, context_id: str) -> Optional[ContextPrediction]:
        """
        Get the latest prediction for a specific context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Latest prediction or None if no predictions exist
        """
        if not self.predictive_engine:
            return None
            
        return self.predictive_engine.get_prediction(context_id)
    
    def get_all_predictions(self) -> Dict[str, ContextPrediction]:
        """
        Get the latest prediction for all contexts.
        
        Returns:
            Dictionary mapping context IDs to their latest predictions
        """
        if not self.predictive_engine:
            return {}
            
        return self.predictive_engine.get_all_predictions()
    
    def get_predictions_by_health(self, health: ContextHealth) -> List[ContextPrediction]:
        """
        Get all predictions with a specific predicted health status.
        
        Args:
            health: Health status to filter by
            
        Returns:
            List of predictions with the specified health status
        """
        if not self.predictive_engine:
            return []
            
        return self.predictive_engine.get_predictions_by_health(health)
    
    def get_critical_predictions(self) -> List[ContextPrediction]:
        """
        Get predictions that indicate critical future issues.
        
        Returns:
            List of predictions with critical health status
        """
        if not self.predictive_engine:
            return []
            
        return self.predictive_engine.get_critical_predictions()
    
    # Action Planner Proxy Methods
    
    def get_actions(self, context_id: str) -> List[ContextAction]:
        """
        Get all actions for a specific context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            List of actions for the context
        """
        if not self.action_planner:
            return []
            
        return self.action_planner.get_actions(context_id)
    
    def get_highest_priority_action(self, context_id: str) -> Optional[ContextAction]:
        """
        Get the highest priority action for a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Highest priority action or None
        """
        if not self.action_planner:
            return None
            
        return self.action_planner.get_highest_priority_action(context_id)
    
    def get_all_actions(self) -> Dict[str, List[ContextAction]]:
        """
        Get all actions for all contexts.
        
        Returns:
            Dictionary mapping context IDs to lists of actions
        """
        if not self.action_planner:
            return {}
            
        return self.action_planner.get_all_actions()
    
    def get_critical_actions(self) -> List[ContextAction]:
        """
        Get all critical priority actions.
        
        Returns:
            List of critical actions
        """
        if not self.action_planner:
            return []
            
        return self.action_planner.get_critical_actions()
    
    def get_actionable_now(self) -> List[ContextAction]:
        """
        Get actions that should be taken now.
        
        Returns:
            List of actions that should be taken now
        """
        if not self.action_planner:
            return []
            
        return self.action_planner.get_actionable_now()
    
    async def mark_action_applied(self, action_id: str):
        """
        Mark an action as having been applied.
        
        Args:
            action_id: Action identifier
        """
        if not self.action_planner:
            return
            
        await self.action_planner.mark_action_applied(action_id)
    
    # High-Level Dashboard Methods
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status summary.
        
        Returns:
            Dictionary with system status information
        """
        # Get context health distribution
        health_distribution = self.get_health_distribution()
        
        # Get counts
        active_contexts = len(self.get_all_context_states())
        critical_contexts = len(self.get_critical_contexts())
        
        # Predictive data
        critical_predictions = len(self.get_critical_predictions()) if self.predictive_engine else 0
        
        # Action data
        pending_actions = sum(len(actions) for actions in self.get_all_actions().values()) if self.action_planner else 0
        critical_actions = len(self.get_critical_actions()) if self.action_planner else 0
        actionable_now = len(self.get_actionable_now()) if self.action_planner else 0
        
        # Component status
        components_status = {
            "context_observer": self.context_observer.is_running,
            "predictive_engine": self.predictive_engine.is_running if self.predictive_engine else False,
            "action_planner": self.action_planner.is_running if self.action_planner else False
        }
        
        return {
            "timestamp": datetime.now(),
            "active_contexts": active_contexts,
            "health_distribution": {str(k): v for k, v in health_distribution.items()},
            "critical_contexts": critical_contexts,
            "critical_predictions": critical_predictions,
            "pending_actions": pending_actions,
            "critical_actions": critical_actions,
            "actionable_now": actionable_now,
            "components_status": components_status,
            "system_running": self.is_running,
            "fastmcp_available": fastmcp_available
        }
    
    def get_context_dashboard(self, context_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a specific context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Dictionary with context dashboard information
        """
        # Get current state
        state = self.get_context_state(context_id)
        if not state:
            return {"error": f"Context {context_id} not found"}
        
        # Get recent history (last 10 records)
        history = self.get_context_history(context_id, 10)
        
        # Get prediction
        prediction = self.get_prediction(context_id)
        
        # Get actions
        actions = self.get_actions(context_id)
        
        # Additional health metrics
        health_trend = "stable"
        if len(history) >= 2:
            last_score = history[-1].health_score
            prev_score = history[-2].health_score
            if last_score - prev_score > 0.1:
                health_trend = "improving"
            elif prev_score - last_score > 0.1:
                health_trend = "degrading"
        
        return {
            "timestamp": datetime.now(),
            "context_id": context_id,
            "state": state.model_dump() if state else None,
            "history": [h.model_dump() for h in history],
            "prediction": prediction.model_dump() if prediction else None,
            "actions": [a.model_dump() for a in actions],
            "health_trend": health_trend,
            "summary": {
                "health": str(state.health),
                "health_score": state.health_score,
                "token_utilization": state.metrics.token_utilization,
                "repetition_score": state.metrics.repetition_score,
                "age_minutes": (datetime.now() - state.creation_time).total_seconds() / 60.0
            }
        }
    
    # MCP Request Processing
    
    def get_mcp_capabilities(self) -> List[MCPCapability]:
        """
        Get all MCP capabilities from Apollo.
        
        Returns:
            List of MCP capabilities
        """
        if not fastmcp_available:
            return []
            
        return get_capabilities(self)
    
    def get_mcp_tools(self) -> List[MCPTool]:
        """
        Get all MCP tools from Apollo.
        
        Returns:
            List of MCP tools
        """
        if not fastmcp_available:
            return []
            
        return get_tools()
    
    async def process_fastmcp_request(self, request: MCPRequest) -> MCPResponse:
        """
        Process a FastMCP request.
        
        Args:
            request: The FastMCP request
            
        Returns:
            MCPResponse object
        """
        if not fastmcp_available:
            return MCPResponse(
                status="error",
                error="FastMCP is not available",
                result=None
            )
            
        try:
            # Get the tool name from the request
            tool_name = request.tool
            
            # Get available tools
            tools = self.get_mcp_tools()
            tool_names = {tool.name: tool for tool in tools}
            
            # Check if the requested tool exists
            if tool_name not in tool_names:
                return MCPResponse(
                    status="error",
                    error=f"Tool '{tool_name}' not found",
                    result=None
                )
                
            # Find the actual tool implementation by loading the right module
            # This is a simplified example - in reality, you would use a more robust approach
            tool_impl = None
            
            if tool_name.startswith("apollo_observe_context"):
                from apollo.core.mcp.tools import observe_context
                tool_impl = observe_context
            elif tool_name.startswith("apollo_list_contexts"):
                from apollo.core.mcp.tools import list_contexts
                tool_impl = list_contexts
            elif tool_name.startswith("apollo_get_context_details"):
                from apollo.core.mcp.tools import get_context_details
                tool_impl = get_context_details
            elif tool_name.startswith("apollo_get_context_health"):
                from apollo.core.mcp.tools import get_context_health
                tool_impl = get_context_health
            elif tool_name.startswith("apollo_allocate_budget"):
                from apollo.core.mcp.tools import allocate_budget
                tool_impl = allocate_budget
            elif tool_name.startswith("apollo_check_budget"):
                from apollo.core.mcp.tools import check_budget
                tool_impl = check_budget
            elif tool_name.startswith("apollo_check_protocol_compliance"):
                from apollo.core.mcp.tools import check_protocol_compliance
                tool_impl = check_protocol_compliance
            elif tool_name.startswith("apollo_list_protocol_violations"):
                from apollo.core.mcp.tools import list_protocol_violations
                tool_impl = list_protocol_violations
            elif tool_name.startswith("apollo_list_actions"):
                from apollo.core.mcp.tools import list_actions
                tool_impl = list_actions
            elif tool_name.startswith("apollo_get_critical_actions"):
                from apollo.core.mcp.tools import get_critical_actions
                tool_impl = get_critical_actions
            elif tool_name.startswith("apollo_get_prediction"):
                from apollo.core.mcp.tools import get_prediction
                tool_impl = get_prediction
            elif tool_name.startswith("apollo_get_predictions_by_health"):
                from apollo.core.mcp.tools import get_predictions_by_health
                tool_impl = get_predictions_by_health
            
            if not tool_impl:
                return MCPResponse(
                    status="error",
                    error=f"Tool implementation for '{tool_name}' not found",
                    result=None
                )
                
            # Call the tool with the request parameters
            # Add self as the first parameter since these tools expect the apollo_manager
            result = await tool_impl(self, **request.parameters)
            
            # Return the response
            return MCPResponse(
                status="success",
                error=None,
                result=result
            )
                
        except Exception as e:
            logger.error(f"Error processing FastMCP request: {e}")
            return MCPResponse(
                status="error",
                error=f"Error processing request: {str(e)}",
                result=None
            )
    
    async def process_mcp_request(
        self,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an MCP request.
        
        Args:
            content: Request content
            context: Optional context information
            
        Returns:
            MCP response
        """
        try:
            # Extract request information
            request_type = content.get("type", "unknown")
            request_data = content.get("data", {})
            
            # Initialize response
            response = {
                "content": {},
                "context": context.copy() if context else {}
            }
            
            # Handle different request types
            if request_type == "action_planning":
                # Process action planning request
                if self.action_planner:
                    goal = request_data.get("goal", "")
                    if goal:
                        plan = await self.action_planner.create_plan(
                            goal=goal,
                            context=context or {},
                            max_steps=request_data.get("max_steps", 5)
                        )
                        
                        response["content"] = {
                            "plan": plan,
                            "goal": goal
                        }
                else:
                    response["content"] = {"error": "Action planner is not enabled"}
                    
            elif request_type == "context_analysis":
                # Process context analysis request
                if self.context_observer:
                    analysis = await self.context_observer.analyze_context(
                        context=context or {},
                        focus_areas=request_data.get("focus_areas")
                    )
                    
                    response["content"] = {
                        "analysis": analysis
                    }
                else:
                    response["content"] = {"error": "Context observer is not enabled"}
                    
            elif request_type == "prediction":
                # Process prediction request
                if self.predictive_engine:
                    if request_data.get("predict_action", False):
                        prediction = await self.predictive_engine.predict_next_action(
                            context=context or {},
                            history=request_data.get("history", [])
                        )
                    else:
                        prediction = await self.predictive_engine.predict_outcome(
                            action=request_data.get("action", {}),
                            context=context or {}
                        )
                        
                    response["content"] = {
                        "prediction": prediction
                    }
                else:
                    response["content"] = {"error": "Predictive engine is not enabled"}
                    
            elif request_type == "message":
                # Process message request
                if self.message_handler:
                    message = request_data.get("message", {})
                    if request_data.get("analyze", False):
                        result = await self.message_handler.analyze_message(
                            message=message,
                            context=context
                        )
                        response["content"] = {
                            "analysis": result
                        }
                    else:
                        response_text = await self.message_handler.generate_response(
                            message=message,
                            context=context or {},
                            response_type=request_data.get("response_type", "chat")
                        )
                        
                        response["content"] = {
                            "response": response_text
                        }
                else:
                    response["content"] = {"error": "Message handler is not enabled"}
                    
            elif request_type == "protocol":
                # Process protocol request
                if self.protocol_enforcer:
                    message = request_data.get("message", {})
                    protocol_name = request_data.get("protocol_name", "default")
                    
                    if request_data.get("validate", True):
                        result = await self.protocol_enforcer.validate_message(
                            message=message,
                            protocol_name=protocol_name
                        )
                        
                        response["content"] = {
                            "validation": result
                        }
                    else:
                        result = await self.protocol_enforcer.enforce_protocol(
                            message=message,
                            protocol_name=protocol_name
                        )
                        
                        response["content"] = {
                            "enforced_message": result.get("message"),
                            "changes": result.get("changes", [])
                        }
                else:
                    response["content"] = {"error": "Protocol enforcer is not enabled"}
                    
            elif request_type == "budget":
                # Process budget request
                if self.token_budget:
                    if request_data.get("allocate", False):
                        allocation = await self.token_budget.allocate(
                            task=request_data.get("task", {}),
                            context_size=request_data.get("context_size", 0),
                            model_name=request_data.get("model_name", "default")
                        )
                        
                        response["content"] = {
                            "allocation": allocation
                        }
                    else:
                        result = await self.token_budget.optimize_context(
                            context=context or {},
                            max_tokens=request_data.get("max_tokens", 1000)
                        )
                        
                        response["content"] = {
                            "optimized_context": result.get("context"),
                            "tokens": {
                                "original": result.get("original_tokens", 0),
                                "optimized": result.get("optimized_tokens", 0)
                            }
                        }
                        
                        # Update context with optimized context
                        response["context"] = result.get("context", {})
                else:
                    response["content"] = {"error": "Token budget is not enabled"}
                    
            else:
                # Unknown request type
                response["content"] = {
                    "error": f"Unknown request type: {request_type}"
                }
                
            # Add metadata
            response["metadata"] = {
                "timestamp": time.time(),
                "request_type": request_type,
                "component": "apollo.mcp"
            }
                
            return response
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return {
                "content": {"error": f"Error processing MCP request: {e}"},
                "context": context or {}
            }