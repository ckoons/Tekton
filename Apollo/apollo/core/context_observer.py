"""
Context Observer Module for Apollo.

This module is responsible for monitoring context usage metrics from Rhetor,
tracking token consumption rates, and identifying patterns that might indicate
performance issues or context degradation.
"""

import os
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
import uuid

# Try to import landmarks if available
try:
    from landmarks import (
        architecture_decision,
        state_checkpoint,
        integration_point,
        performance_boundary,
        danger_zone
    )
except ImportError:
    # Create no-op decorators if landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator

from apollo.models.context import (
    ContextMetrics,
    ContextState,
    ContextHistoryRecord,
    ContextHealth,
    ContextAction
)
from apollo.core.interfaces.rhetor import RhetorInterface

# Configure logging
logger = logging.getLogger(__name__)


class ContextObserver:
    """
    Monitors and analyzes LLM context usage across Tekton components.
    
    This class is responsible for collecting context metrics from Rhetor,
    calculating health scores, and maintaining historical data for trend analysis.
    """
    
    def __init__(
        self,
        rhetor_interface: Optional[RhetorInterface] = None,
        history_limit: int = 100,
        polling_interval: float = 5.0,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Context Observer.
        
        Args:
            rhetor_interface: Interface for communicating with Rhetor
            history_limit: Maximum number of historical records to keep per context
            polling_interval: Interval in seconds for polling metrics
            data_dir: Directory for storing context data
        """
        self.rhetor_interface = rhetor_interface or RhetorInterface()
        self.history_limit = history_limit
        self.polling_interval = polling_interval
        
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            # Use $TEKTON_DATA_DIR/apollo/context_data by default
            default_data_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'apollo', 'context_data'
            )
            self.data_dir = default_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Active contexts being monitored
        self.active_contexts: Dict[str, ContextState] = {}
        
        # Historical data for each context
        self.context_history: Dict[str, List[ContextHistoryRecord]] = {}
        
        # Callbacks for context events
        self.callbacks: Dict[str, List[Callable]] = {
            "on_metrics_update": [],
            "on_health_change": [],
            "on_context_created": [],
            "on_context_closed": []
        }
        
        # For monitoring task
        self.monitoring_task = None
        self.is_running = False
    
    @integration_point(
        title="Context Monitoring Start",
        description="Begins real-time context monitoring from Rhetor",
        target_component="Rhetor",
        protocol="HTTP API polling",
        data_flow="Rhetor metrics → Context Observer → Apollo predictions",
        integration_date="2025-01-25"
    )
    async def start(self):
        """Start the context monitoring process."""
        if self.is_running:
            logger.warning("Context monitoring is already running")
            return
        
        self.is_running = True
        
        # Start the monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Context monitoring started")
    
    async def stop(self):
        """Stop the context monitoring process."""
        if not self.is_running:
            logger.warning("Context monitoring is not running")
            return
        
        self.is_running = False
        
        # Cancel the monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            
        logger.info("Context monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop that polls for metrics periodically."""
        try:
            while self.is_running:
                await self._collect_metrics()
                await asyncio.sleep(self.polling_interval)
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.is_running = False
            raise
    
    async def _collect_metrics(self):
        """Collect metrics from Rhetor for all active contexts."""
        try:
            # Get active contexts from Rhetor
            active_sessions = await self.rhetor_interface.get_active_sessions()
            
            # Log the response for debugging
            logger.debug(f"Active sessions from Rhetor: {active_sessions}")
            
            # Update our context records
            for session in active_sessions:
                # Check if session has context_id key
                if "context_id" not in session:
                    logger.warning(f"Session missing context_id: {session}")
                    continue
                    
                context_id = session["context_id"]
                
                # Create metrics object
                metrics = ContextMetrics(
                    input_tokens=session.get("input_tokens", 0),
                    output_tokens=session.get("output_tokens", 0),
                    total_tokens=session.get("total_tokens", 0),
                    max_tokens=session.get("max_tokens", 4000),
                    token_utilization=session.get("token_utilization", 0.0),
                    input_token_rate=session.get("input_token_rate", 0.0),
                    output_token_rate=session.get("output_token_rate", 0.0),
                    token_rate_change=session.get("token_rate_change", 0.0),
                    repetition_score=session.get("repetition_score", 0.0),
                    self_reference_score=session.get("self_reference_score", 0.0),
                    coherence_score=session.get("coherence_score", 1.0),
                    latency=session.get("latency", 0.0),
                    processing_time=session.get("processing_time", 0.0),
                    timestamp=datetime.now()
                )
                
                # Calculate health score
                health_score = self._calculate_health_score(metrics)
                health = self._determine_health_status(health_score)
                
                # If this is a new context
                if context_id not in self.active_contexts:
                    # Create new context state
                    context_state = ContextState(
                        context_id=context_id,
                        component_id=session.get("component", "unknown"),
                        provider=session.get("provider", "unknown"),
                        model=session.get("model", "unknown"),
                        task_type=session.get("task_type", "unknown"),
                        metrics=metrics,
                        health=health,
                        health_score=health_score,
                        creation_time=datetime.now(),
                        last_updated=datetime.now(),
                        metadata=session.get("metadata", {})
                    )
                    
                    # Add to active contexts
                    self.active_contexts[context_id] = context_state
                    
                    # Initialize history
                    self.context_history[context_id] = []
                    
                    # Trigger callbacks
                    await self._trigger_callbacks("on_context_created", context_state)
                    
                else:
                    # Update existing context
                    context_state = self.active_contexts[context_id]
                    
                    # Check for health change
                    previous_health = context_state.health
                    
                    # Update the state
                    context_state.metrics = metrics
                    context_state.health = health
                    context_state.health_score = health_score
                    context_state.last_updated = datetime.now()
                    
                    # Trigger metrics update callback
                    await self._trigger_callbacks("on_metrics_update", context_state)
                    
                    # Trigger health change callback if health changed
                    if previous_health != health:
                        await self._trigger_callbacks("on_health_change", context_state, previous_health)
                
                # Add to history
                history_record = ContextHistoryRecord(
                    context_id=context_id,
                    metrics=metrics,
                    health=health,
                    health_score=health_score,
                    timestamp=datetime.now()
                )
                
                self.context_history[context_id].append(history_record)
                
                # Trim history if needed
                if len(self.context_history[context_id]) > self.history_limit:
                    self.context_history[context_id] = self.context_history[context_id][-self.history_limit:]
            
            # Check for closed contexts
            active_context_ids = [s.get("context_id") for s in active_sessions if "context_id" in s]
            closed_contexts = [
                context_id for context_id in self.active_contexts
                if context_id not in active_context_ids
            ]
            
            # Handle closed contexts
            for context_id in closed_contexts:
                context_state = self.active_contexts[context_id]
                await self._trigger_callbacks("on_context_closed", context_state)
                
                # Remove from active contexts
                del self.active_contexts[context_id]
                
                # Save history to disk
                await self._save_context_history(context_id)
        
        except Exception as e:
            logger.error(f"Error collecting context metrics: {e}")
    
    def _calculate_health_score(self, metrics: ContextMetrics) -> float:
        """
        Calculate a health score for the context based on metrics.
        
        Args:
            metrics: Context metrics
            
        Returns:
            Health score between 0.0 and 1.0 (higher is better)
        """
        # Base score starts at 1.0 (perfect health)
        score = 1.0
        
        # Factor 1: Token utilization (penalize high utilization)
        if metrics.token_utilization > 0.85:
            # Exponential penalty as we approach max tokens
            penalty = ((metrics.token_utilization - 0.85) / 0.15) ** 2 * 0.4
            score -= penalty
        
        # Factor 2: Repetition (penalize high repetition)
        if metrics.repetition_score > 0.2:
            # Linear penalty based on repetition
            penalty = metrics.repetition_score * 0.5
            score -= penalty
        
        # Factor 3: Self-reference (penalize high self-reference)
        if metrics.self_reference_score > 0.15:
            # Linear penalty based on self-reference
            penalty = metrics.self_reference_score * 0.3
            score -= penalty
        
        # Factor 4: Coherence (penalize low coherence)
        if metrics.coherence_score < 0.8:
            # Linear penalty based on lack of coherence
            penalty = (0.8 - metrics.coherence_score) * 0.4
            score -= penalty
        
        # Factor 5: Latency trends (penalize increasing latency)
        if metrics.token_rate_change < -0.2:
            # Slowing down significantly
            penalty = min(abs(metrics.token_rate_change) * 0.2, 0.2)
            score -= penalty
        
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, score))
    
    def _determine_health_status(self, health_score: float) -> ContextHealth:
        """
        Determine the health status category based on the health score.
        
        Args:
            health_score: Numerical health score between 0.0 and 1.0
            
        Returns:
            ContextHealth enum value
        """
        if health_score >= 0.9:
            return ContextHealth.EXCELLENT
        elif health_score >= 0.75:
            return ContextHealth.GOOD
        elif health_score >= 0.6:
            return ContextHealth.FAIR
        elif health_score >= 0.4:
            return ContextHealth.POOR
        else:
            return ContextHealth.CRITICAL
    
    async def _save_context_history(self, context_id: str):
        """
        Save context history to disk.
        
        Args:
            context_id: Context identifier
        """
        try:
            if context_id not in self.context_history:
                return
            
            # Prepare data for saving
            history_data = [record.model_dump() for record in self.context_history[context_id]]
            
            # Create filename
            safe_id = context_id.replace("/", "_").replace(":", "_")
            filename = os.path.join(self.data_dir, f"{safe_id}_{int(time.time())}.json")
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(history_data, f, indent=2, default=str)
                
            logger.info(f"Saved context history for {context_id} to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving context history for {context_id}: {e}")
    
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
    
    def get_context_state(self, context_id: str) -> Optional[ContextState]:
        """
        Get the current state of a context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            ContextState or None if not found
        """
        return self.active_contexts.get(context_id)
    
    def get_all_context_states(self) -> List[ContextState]:
        """
        Get states for all active contexts.
        
        Returns:
            List of ContextState objects
        """
        return list(self.active_contexts.values())
    
    def get_context_history(self, context_id: str, limit: int = None) -> List[ContextHistoryRecord]:
        """
        Get history for a specific context.
        
        Args:
            context_id: Context identifier
            limit: Maximum number of records to return (newest first)
            
        Returns:
            List of ContextHistoryRecord objects
        """
        if context_id not in self.context_history:
            return []
            
        history = self.context_history[context_id]
        
        if limit:
            history = history[-limit:]
            
        return history
    
    def get_health_distribution(self) -> Dict[ContextHealth, int]:
        """
        Get distribution of context health across all active contexts.
        
        Returns:
            Dictionary mapping health status to count
        """
        distribution = {status: 0 for status in ContextHealth}
        
        for context in self.active_contexts.values():
            distribution[context.health] += 1
            
        return distribution
    
    def get_critical_contexts(self) -> List[ContextState]:
        """
        Get contexts with critical health status.
        
        Returns:
            List of ContextState objects with critical health
        """
        return [
            context for context in self.active_contexts.values()
            if context.health == ContextHealth.CRITICAL
        ]
    
    async def suggest_action(self, context_id: str) -> Optional[ContextAction]:
        """
        Suggest an action for a context based on its health.
        
        This is a simple heuristic-based action suggestion that will be replaced
        by more sophisticated logic in the Action Planner.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Suggested ContextAction or None
        """
        if context_id not in self.active_contexts:
            return None
            
        context = self.active_contexts[context_id]
        
        # Critical health: suggest a reset
        if context.health == ContextHealth.CRITICAL:
            return ContextAction(
                context_id=context_id,
                action_type="reset",
                priority=10,
                reason="Context health is critical",
                parameters={}
            )
            
        # Poor health: suggest a compression
        elif context.health == ContextHealth.POOR:
            return ContextAction(
                context_id=context_id,
                action_type="compress",
                priority=7,
                reason="Context health is poor",
                parameters={"level": "aggressive"}
            )
            
        # Fair health with high token utilization: suggest a light compression
        elif context.health == ContextHealth.FAIR and context.metrics.token_utilization > 0.8:
            return ContextAction(
                context_id=context_id,
                action_type="compress",
                priority=5,
                reason="High token utilization",
                parameters={"level": "light"}
            )
            
        # Otherwise, no action needed
        return None