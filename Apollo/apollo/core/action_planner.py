"""
Action Planner Module for Apollo.

This module is responsible for determining appropriate corrective actions
based on current context states and predictions. It uses rule-based decision
making to generate actions with appropriate priorities and timing.
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Set
import uuid
from enum import Enum

from apollo.models.context import (
    ContextMetrics,
    ContextState,
    ContextPrediction,
    ContextHealth,
    ContextAction
)
from apollo.core.context_observer import ContextObserver
from apollo.core.predictive_engine import PredictiveEngine

# Try to import landmarks
try:
    from landmarks import architecture_decision, danger_zone, performance_boundary
except ImportError:
    # Define no-op decorators if landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Configure logging
logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions that can be taken on a context."""
    REFRESH = "refresh"  # Refresh the context with new information
    COMPRESS = "compress"  # Compress the context to reduce token usage
    SUMMARIZE = "summarize"  # Summarize parts of the context
    PRUNE = "prune"  # Remove less important parts of the context
    RESET = "reset"  # Reset the context completely
    TIER_CHANGE = "tier_change"  # Change to a different model tier
    PARAMETER_ADJUST = "parameter_adjust"  # Adjust model parameters
    NOTIFY = "notify"  # Notify a component or user


class ActionPriority(int, Enum):
    """Priority levels for actions."""
    LOW = 3
    MEDIUM = 5
    HIGH = 7
    CRITICAL = 10


class ActionRule:
    """Base class for action rules."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the action rule.
        
        Args:
            name: Rule name
            description: Rule description
        """
        self.name = name
        self.description = description
    
    async def evaluate(
        self, 
        context_id: str, 
        current_state: Optional[ContextState],
        prediction: Optional[ContextPrediction]
    ) -> Optional[ContextAction]:
        """
        Evaluate whether to generate an action for a context.
        
        Args:
            context_id: Context identifier
            current_state: Current context state (may be None)
            prediction: Predicted future state (may be None)
            
        Returns:
            Action to take or None
        """
        raise NotImplementedError("Action rules must implement evaluate method")


class TokenUtilizationActionRule(ActionRule):
    """Rule for handling high token utilization."""
    
    def __init__(self):
        """Initialize the token utilization action rule."""
        super().__init__(
            name="token_utilization",
            description="Generates actions to address high token utilization"
        )
    
    async def evaluate(
        self, 
        context_id: str, 
        current_state: Optional[ContextState],
        prediction: Optional[ContextPrediction]
    ) -> Optional[ContextAction]:
        """Evaluate based on current and predicted token utilization."""
        # Skip if no current state
        if not current_state:
            return None
        
        # Check current utilization
        current_utilization = current_state.metrics.token_utilization
        
        # Check predicted utilization
        predicted_utilization = None
        if prediction:
            predicted_utilization = prediction.predicted_metrics.token_utilization
        
        # Critical: Current utilization > 95% - Immediate reset needed
        if current_utilization > 0.95:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.RESET,
                priority=ActionPriority.CRITICAL,
                reason="Token utilization critically high (>95%)",
                parameters={},
                suggested_time=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=5)
            )
        
        # High: Current utilization > 85% - Strong compression needed
        elif current_utilization > 0.85:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.COMPRESS,
                priority=ActionPriority.HIGH,
                reason="Token utilization high (>85%)",
                parameters={"level": "aggressive"},
                suggested_time=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=15)
            )
        
        # Medium: Current utilization > 75% AND predicted to exceed 90%
        elif current_utilization > 0.75 and predicted_utilization and predicted_utilization > 0.9:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.COMPRESS,
                priority=ActionPriority.MEDIUM,
                reason="Token utilization (>75%) predicted to become critical",
                parameters={"level": "moderate"},
                suggested_time=datetime.now() + timedelta(seconds=30),
                expires_at=datetime.now() + timedelta(minutes=30)
            )
        
        # Low: Current utilization > 70% AND predicted to exceed 80%
        elif current_utilization > 0.7 and predicted_utilization and predicted_utilization > 0.8:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.COMPRESS,
                priority=ActionPriority.LOW,
                reason="Token utilization growing, preemptive compression recommended",
                parameters={"level": "light"},
                suggested_time=datetime.now() + timedelta(minutes=1),
                expires_at=datetime.now() + timedelta(minutes=60)
            )
        
        return None


class RepetitionActionRule(ActionRule):
    """Rule for handling repetition issues."""
    
    def __init__(self):
        """Initialize the repetition action rule."""
        super().__init__(
            name="repetition",
            description="Generates actions to address repetition issues"
        )
    
    async def evaluate(
        self, 
        context_id: str, 
        current_state: Optional[ContextState],
        prediction: Optional[ContextPrediction]
    ) -> Optional[ContextAction]:
        """Evaluate based on current and predicted repetition scores."""
        # Skip if no current state
        if not current_state:
            return None
        
        # Check current repetition
        current_repetition = current_state.metrics.repetition_score
        
        # Check predicted repetition
        predicted_repetition = None
        if prediction:
            predicted_repetition = prediction.predicted_metrics.repetition_score
        
        # Critical: Current repetition > 0.5 - Context is severely degraded
        if current_repetition > 0.5:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.RESET,
                priority=ActionPriority.HIGH,
                reason="Severe repetition detected (>50%)",
                parameters={},
                suggested_time=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=5)
            )
        
        # High: Current repetition > 0.3 - Need immediate pruning
        elif current_repetition > 0.3:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.PRUNE,
                priority=ActionPriority.HIGH,
                reason="High repetition detected (>30%)",
                parameters={"target": "repetitive_sections"},
                suggested_time=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=10)
            )
        
        # Medium: Current repetition > 0.2 AND predicted to increase
        elif current_repetition > 0.2 and predicted_repetition and predicted_repetition > current_repetition + 0.1:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.SUMMARIZE,
                priority=ActionPriority.MEDIUM,
                reason="Repetition increasing, intervention recommended",
                parameters={},
                suggested_time=datetime.now() + timedelta(seconds=30),
                expires_at=datetime.now() + timedelta(minutes=20)
            )
        
        return None


class PerformanceActionRule(ActionRule):
    """Rule for handling performance issues."""
    
    def __init__(self):
        """Initialize the performance action rule."""
        super().__init__(
            name="performance",
            description="Generates actions to address performance issues"
        )
    
    async def evaluate(
        self, 
        context_id: str, 
        current_state: Optional[ContextState],
        prediction: Optional[ContextPrediction]
    ) -> Optional[ContextAction]:
        """Evaluate based on current and predicted performance metrics."""
        # Skip if no current state
        if not current_state:
            return None
        
        # Check current metrics
        current_token_rate = current_state.metrics.output_token_rate
        current_latency = current_state.metrics.latency
        
        # Check for severe performance degradation
        if current_token_rate < 1.0 and current_token_rate > 0.0 and current_latency > 5.0:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.TIER_CHANGE,
                priority=ActionPriority.HIGH,
                reason="Severe performance degradation",
                parameters={"suggested_tier": "LOCAL_LIGHTWEIGHT"},
                suggested_time=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=5)
            )
        
        # Check for moderate performance issues
        elif current_token_rate < 3.0 and current_token_rate > 0.0 and current_latency > 3.0:
            # If context is large, compress it
            if current_state.metrics.token_utilization > 0.7:
                return ContextAction(
                    context_id=context_id,
                    action_type=ActionType.COMPRESS,
                    priority=ActionPriority.MEDIUM,
                    reason="Performance degradation with large context",
                    parameters={"level": "moderate"},
                    suggested_time=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=15)
                )
            # Otherwise adjust parameters
            else:
                return ContextAction(
                    context_id=context_id,
                    action_type=ActionType.PARAMETER_ADJUST,
                    priority=ActionPriority.MEDIUM,
                    reason="Performance degradation",
                    parameters={
                        "temperature": 0.7,  # Lower temperature for more focused generation
                        "top_p": 0.9  # Slightly more deterministic
                    },
                    suggested_time=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=30)
                )
        
        # Check predicted performance from prediction
        if prediction:
            predicted_token_rate = prediction.predicted_metrics.output_token_rate
            predicted_latency = prediction.predicted_metrics.latency
            
            # Predicted severe performance degradation
            if predicted_token_rate < 1.0 and predicted_token_rate > 0.0 and predicted_latency > 5.0:
                return ContextAction(
                    context_id=context_id,
                    action_type=ActionType.REFRESH,
                    priority=ActionPriority.MEDIUM,
                    reason="Predicted performance degradation",
                    parameters={},
                    suggested_time=datetime.now() + timedelta(seconds=30),
                    expires_at=datetime.now() + timedelta(minutes=10)
                )
        
        return None


class HealthActionRule(ActionRule):
    """Rule for handling general health issues."""
    
    def __init__(self):
        """Initialize the health action rule."""
        super().__init__(
            name="health",
            description="Generates actions based on overall context health"
        )
    
    async def evaluate(
        self, 
        context_id: str, 
        current_state: Optional[ContextState],
        prediction: Optional[ContextPrediction]
    ) -> Optional[ContextAction]:
        """Evaluate based on current and predicted health status."""
        # Skip if no current state
        if not current_state:
            return None
        
        # Check current health
        current_health = current_state.health
        current_health_score = current_state.health_score
        
        # Check predicted health
        predicted_health = None
        predicted_health_score = None
        if prediction:
            predicted_health = prediction.predicted_health
            predicted_health_score = prediction.predicted_health_score
        
        # Critical current health
        if current_health == ContextHealth.CRITICAL:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.RESET,
                priority=ActionPriority.CRITICAL,
                reason="Critical context health",
                parameters={},
                suggested_time=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=5)
            )
        
        # Poor current health
        elif current_health == ContextHealth.POOR:
            # For high token utilization, compress
            if current_state.metrics.token_utilization > 0.8:
                return ContextAction(
                    context_id=context_id,
                    action_type=ActionType.COMPRESS,
                    priority=ActionPriority.HIGH,
                    reason="Poor context health with high token utilization",
                    parameters={"level": "aggressive"},
                    suggested_time=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=10)
                )
            # For high repetition, prune
            elif current_state.metrics.repetition_score > 0.3:
                return ContextAction(
                    context_id=context_id,
                    action_type=ActionType.PRUNE,
                    priority=ActionPriority.HIGH,
                    reason="Poor context health with high repetition",
                    parameters={"target": "repetitive_sections"},
                    suggested_time=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=10)
                )
            # Default action for poor health
            else:
                return ContextAction(
                    context_id=context_id,
                    action_type=ActionType.REFRESH,
                    priority=ActionPriority.HIGH,
                    reason="Poor context health",
                    parameters={},
                    suggested_time=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=10)
                )
        
        # Fair health but predicted to degrade
        elif current_health == ContextHealth.FAIR and predicted_health in [ContextHealth.POOR, ContextHealth.CRITICAL]:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.REFRESH,
                priority=ActionPriority.MEDIUM,
                reason="Context health predicted to degrade",
                parameters={},
                suggested_time=datetime.now() + timedelta(minutes=1),
                expires_at=datetime.now() + timedelta(minutes=20)
            )
        
        # Good health but predicted significant degradation
        elif current_health == ContextHealth.GOOD and predicted_health == ContextHealth.CRITICAL:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.NOTIFY,
                priority=ActionPriority.LOW,
                reason="Context health predicted to degrade significantly",
                parameters={"message": "Consider refreshing context soon"},
                suggested_time=datetime.now() + timedelta(minutes=2),
                expires_at=datetime.now() + timedelta(minutes=30)
            )
        
        return None


class PreventiveActionRule(ActionRule):
    """Rule for preventive maintenance on long-running contexts."""
    
    def __init__(self):
        """Initialize the preventive action rule."""
        super().__init__(
            name="preventive",
            description="Generates preventive actions for long-running contexts"
        )
    
    async def evaluate(
        self, 
        context_id: str, 
        current_state: Optional[ContextState],
        prediction: Optional[ContextPrediction]
    ) -> Optional[ContextAction]:
        """Evaluate based on context age and complexity."""
        # Skip if no current state
        if not current_state:
            return None
        
        # Calculate context age
        now = datetime.now()
        context_age = (now - current_state.creation_time).total_seconds() / 60.0  # in minutes
        
        # Context is large (>60% utilized) and old (>60 minutes)
        if current_state.metrics.token_utilization > 0.6 and context_age > 60:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.REFRESH,
                priority=ActionPriority.LOW,
                reason="Preventive maintenance for long-running context",
                parameters={},
                suggested_time=datetime.now() + timedelta(minutes=5),
                expires_at=datetime.now() + timedelta(hours=1)
            )
        
        # Context has been running for 3+ hours
        elif context_age > 180:
            return ContextAction(
                context_id=context_id,
                action_type=ActionType.NOTIFY,
                priority=ActionPriority.LOW,
                reason="Long-running context detected",
                parameters={"message": "Consider refreshing or resetting context"},
                suggested_time=datetime.now() + timedelta(minutes=5),
                expires_at=datetime.now() + timedelta(hours=2)
            )
        
        return None


@architecture_decision(
    title="Rule-based action planning",
    rationale="Deterministic rules provide predictable, debuggable behavior for critical context management",
    alternatives_considered=["ML-based planning", "Reinforcement learning", "Static thresholds"],
    impacts=["predictability", "maintainability", "flexibility"],
    decided_by="team"
)
@danger_zone(
    title="Complex planning logic",
    risk_level="high",
    risks=["Action loops", "Resource exhaustion", "Conflicting actions"],
    mitigation="Priority system, action expiration, max actions per context",
    review_required=True
)
class ActionPlanner:
    """
    Action planner for Apollo that determines appropriate corrective actions.
    
    This class uses rule-based decision making to generate actions based on 
    current context states and predictions about future states. It prioritizes
    actions and determines appropriate timing for interventions.
    """
    
    def __init__(
        self,
        context_observer: Optional[ContextObserver] = None,
        predictive_engine: Optional[PredictiveEngine] = None,
        planning_interval: float = 10.0,
        max_actions_per_context: int = 5,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Action Planner.
        
        Args:
            context_observer: Observer for context metrics
            predictive_engine: Engine for context predictions
            planning_interval: Interval for planning actions in seconds
            max_actions_per_context: Maximum actions to keep per context
            data_dir: Directory for storing action data
        """
        self.context_observer = context_observer
        self.predictive_engine = predictive_engine
        self.planning_interval = planning_interval
        self.max_actions_per_context = max_actions_per_context
        
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo/action_data by default
            default_data_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo', 'action_data'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize action rules
        self.action_rules: List[ActionRule] = [
            TokenUtilizationActionRule(),
            RepetitionActionRule(),
            PerformanceActionRule(),
            HealthActionRule(),
            PreventiveActionRule()
        ]
        
        # Store actions by context
        self.actions: Dict[str, List[ContextAction]] = {}
        
        # For task management
        self.planning_task = None
        self.is_running = False
        
        # Track applied actions
        self.applied_actions: Dict[str, List[ContextAction]] = {}
        
        # For action callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "on_action_created": [],
            "on_action_expired": [],
            "on_action_applied": []
        }
    
    async def start(self):
        """Start the action planner."""
        if self.is_running:
            logger.warning("Action planner is already running")
            return
            
        self.is_running = True
        
        # Start the planning task
        self.planning_task = asyncio.create_task(self._planning_loop())
        
        logger.info("Action planner started")
    
    async def stop(self):
        """Stop the action planner."""
        if not self.is_running:
            logger.warning("Action planner is not running")
            return
            
        self.is_running = False
        
        # Cancel the planning task
        if self.planning_task:
            self.planning_task.cancel()
            try:
                await self.planning_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Action planner stopped")
    
    async def _planning_loop(self):
        """Main loop for planning actions periodically."""
        try:
            while self.is_running:
                await self._plan_actions()
                await self._clean_expired_actions()
                await asyncio.sleep(self.planning_interval)
        except asyncio.CancelledError:
            logger.info("Planning loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in planning loop: {e}")
            self.is_running = False
            raise
    
    async def _plan_actions(self):
        """Plan actions for all active contexts."""
        if not self.context_observer:
            logger.warning("No context observer available for planning")
            return
            
        try:
            # Get all active contexts
            active_contexts = self.context_observer.get_all_context_states()
            
            # Get predictions
            predictions = {}
            if self.predictive_engine:
                predictions = self.predictive_engine.get_all_predictions()
            
            # Process each context
            for context in active_contexts:
                context_id = context.context_id
                
                # Get prediction for this context
                prediction = predictions.get(context_id)
                
                # Apply each action rule
                for rule in self.action_rules:
                    try:
                        action = await rule.evaluate(context_id, context, prediction)
                        
                        if action:
                            # Add to actions list for this context
                            if context_id not in self.actions:
                                self.actions[context_id] = []
                                
                            # Check if a similar action already exists
                            similar_exists = False
                            for existing in self.actions[context_id]:
                                if (existing.action_type == action.action_type and 
                                    existing.priority == action.priority):
                                    similar_exists = True
                                    break
                                    
                            if not similar_exists:
                                # Add the action
                                self.actions[context_id].append(action)
                                
                                # Trigger callback
                                await self._trigger_callbacks("on_action_created", action)
                                
                                logger.info(f"Created action {action.action_type} for context {context_id} with priority {action.priority}")
                            
                            # Limit number of actions per context
                            if len(self.actions[context_id]) > self.max_actions_per_context:
                                # Sort by priority (highest first) and keep only the top ones
                                self.actions[context_id].sort(key=lambda a: a.priority, reverse=True)
                                self.actions[context_id] = self.actions[context_id][:self.max_actions_per_context]
                    
                    except Exception as e:
                        logger.error(f"Error applying action rule {rule.name}: {e}")
        
        except Exception as e:
            logger.error(f"Error planning actions: {e}")
    
    async def _clean_expired_actions(self):
        """Remove expired actions."""
        now = datetime.now()
        
        for context_id, context_actions in list(self.actions.items()):
            # Check each action
            for action in context_actions[:]:
                if action.expires_at and action.expires_at < now:
                    # Remove expired action
                    context_actions.remove(action)
                    
                    # Trigger callback
                    await self._trigger_callbacks("on_action_expired", action)
                    
                    logger.info(f"Action {action.action_type} for context {context_id} expired")
            
            # Remove empty contexts
            if not context_actions:
                del self.actions[context_id]
    
    async def _trigger_callbacks(self, event_type: str, *args, **kwargs):
        """
        Trigger registered callbacks for an event.
        
        Args:
            event_type: Type of event
            *args: Arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if event_type not in self.callbacks:
            return
            
        for callback in self.callbacks[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {event_type} callback: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to register for
            callback: Callback function
        """
        if event_type not in self.callbacks:
            logger.warning(f"Unknown event type: {event_type}")
            return
            
        self.callbacks[event_type].append(callback)
        logger.debug(f"Registered callback for {event_type}")
    
    def get_actions(self, context_id: str) -> List[ContextAction]:
        """
        Get all actions for a specific context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            List of actions for the context
        """
        return self.actions.get(context_id, [])
    
    def get_highest_priority_action(self, context_id: str) -> Optional[ContextAction]:
        """
        Get the highest priority action for a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Highest priority action or None
        """
        actions = self.get_actions(context_id)
        
        if not actions:
            return None
            
        # Sort by priority (highest first)
        actions.sort(key=lambda a: a.priority, reverse=True)
        
        return actions[0]
    
    def get_all_actions(self) -> Dict[str, List[ContextAction]]:
        """
        Get all actions for all contexts.
        
        Returns:
            Dictionary mapping context IDs to lists of actions
        """
        return self.actions
    
    def get_critical_actions(self) -> List[ContextAction]:
        """
        Get all critical priority actions.
        
        Returns:
            List of critical actions
        """
        result = []
        
        for context_actions in self.actions.values():
            for action in context_actions:
                if action.priority == ActionPriority.CRITICAL:
                    result.append(action)
                    
        return result
    
    def get_actionable_now(self) -> List[ContextAction]:
        """
        Get actions that should be taken now.
        
        Returns:
            List of actions that should be taken now
        """
        now = datetime.now()
        result = []
        
        for context_actions in self.actions.values():
            for action in context_actions:
                if not action.suggested_time or action.suggested_time <= now:
                    result.append(action)
                    
        # Sort by priority (highest first)
        result.sort(key=lambda a: a.priority, reverse=True)
        
        return result
    
    async def mark_action_applied(self, action_id: str):
        """
        Mark an action as having been applied.
        
        Args:
            action_id: Action identifier
        """
        # Find the action
        for context_id, context_actions in list(self.actions.items()):
            for action in context_actions[:]:
                if action.action_id == action_id:
                    # Remove from pending actions
                    context_actions.remove(action)
                    
                    # Add to applied actions
                    if context_id not in self.applied_actions:
                        self.applied_actions[context_id] = []
                        
                    self.applied_actions[context_id].append(action)
                    
                    # Trigger callback
                    await self._trigger_callbacks("on_action_applied", action)
                    
                    logger.info(f"Action {action.action_type} for context {context_id} applied")
                    
                    # Remove empty contexts
                    if not context_actions:
                        del self.actions[context_id]
                        
                    return
        
        logger.warning(f"Action {action_id} not found")
    
    async def save_action_history(self, context_id: str):
        """
        Save action history for a context to disk.
        
        Args:
            context_id: Context identifier
        """
        try:
            if context_id not in self.applied_actions:
                return
                
            # Prepare data for saving
            action_data = [action.model_dump() for action in self.applied_actions[context_id]]
            
            # Create filename
            safe_id = context_id.replace("/", "_").replace(":", "_")
            filename = os.path.join(self.data_dir, f"{safe_id}_{int(time.time())}.json")
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(action_data, f, indent=2, default=str)
                
            logger.info(f"Saved action history for {context_id} to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving action history for {context_id}: {e}")
    
    def get_action_stats(self) -> Dict[str, int]:
        """
        Get statistics on actions by type.
        
        Returns:
            Dictionary mapping action types to counts
        """
        stats = {action_type: 0 for action_type in ActionType}
        
        # Count pending actions
        for context_actions in self.actions.values():
            for action in context_actions:
                stats[action.action_type] += 1
                
        # Count applied actions
        for context_actions in self.applied_actions.values():
            for action in context_actions:
                stats[action.action_type] += 1
                
        return stats