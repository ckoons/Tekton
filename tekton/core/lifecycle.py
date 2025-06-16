#!/usr/bin/env python3
"""
Component Lifecycle Definitions Module

This module provides core component lifecycle class definitions for the Tekton
component lifecycle management system.
"""

import uuid
import time
import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Callable, Awaitable

logger = logging.getLogger("tekton.lifecycle")

class ComponentState(Enum):
    """
    Enhanced component state enum with fine-grained lifecycle states.
    
    Provides clear distinction between different operational states to avoid deadlocks
    and enable better dependency management.
    """
    UNKNOWN = "unknown"            # State not known or not tracked
    INITIALIZING = "initializing"  # Starting up but not ready for operations
    READY = "ready"                # Fully operational and accepting requests
    ACTIVE = "active"              # Actively processing tasks
    DEGRADED = "degraded"          # Running with limited functionality
    INACTIVE = "inactive"          # Temporarily not accepting new requests
    ERROR = "error"                # Operational error state but recoverable
    FAILED = "failed"              # Failed to start or crashed
    STOPPING = "stopping"          # Graceful shutdown in progress
    RESTARTING = "restarting"      # Temporary unavailable during restart
    
    @classmethod
    def is_active(cls, state):
        """Check if the state is considered active (can serve requests)."""
        return state in [cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value]
    
    @classmethod
    def is_terminal(cls, state):
        """Check if the state is a terminal state."""
        return state in [cls.FAILED.value]
    
    @classmethod
    def is_transitioning(cls, state):
        """Check if the state is a transitional state."""
        return state in [cls.INITIALIZING.value, cls.STOPPING.value, cls.RESTARTING.value]
    
    @classmethod
    def is_degraded(cls, state):
        """Check if the state is a degraded state."""
        return state in [cls.DEGRADED.value, cls.ERROR.value, cls.INACTIVE.value]
    
    @classmethod
    def can_serve_requests(cls, state):
        """Check if the component can serve requests in this state."""
        return state in [cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value]
    
    @classmethod
    def validate_transition(cls, from_state, to_state):
        """
        Validate if a state transition is allowed.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            cls.UNKNOWN.value: [
                cls.INITIALIZING.value, cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value, 
                cls.INACTIVE.value, cls.ERROR.value, cls.FAILED.value, cls.STOPPING.value
            ],
            cls.INITIALIZING.value: [
                cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value, cls.ERROR.value, 
                cls.FAILED.value, cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.READY.value: [
                cls.ACTIVE.value, cls.DEGRADED.value, cls.INACTIVE.value, cls.ERROR.value,
                cls.FAILED.value, cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.ACTIVE.value: [
                cls.READY.value, cls.DEGRADED.value, cls.INACTIVE.value, cls.ERROR.value,
                cls.FAILED.value, cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.DEGRADED.value: [
                cls.READY.value, cls.ACTIVE.value, cls.ERROR.value, cls.INACTIVE.value,
                cls.FAILED.value, cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.INACTIVE.value: [
                cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value, cls.ERROR.value,
                cls.FAILED.value, cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.ERROR.value: [
                cls.READY.value, cls.ACTIVE.value, cls.DEGRADED.value, cls.INACTIVE.value,
                cls.FAILED.value, cls.STOPPING.value, cls.RESTARTING.value
            ],
            cls.FAILED.value: [
                cls.INITIALIZING.value, cls.RESTARTING.value
            ],
            cls.STOPPING.value: [
                cls.UNKNOWN.value, cls.FAILED.value, cls.INACTIVE.value
            ],
            cls.RESTARTING.value: [
                cls.INITIALIZING.value, cls.READY.value, cls.ACTIVE.value, 
                cls.DEGRADED.value, cls.ERROR.value, cls.FAILED.value
            ]
        }
        
        return to_state in valid_transitions.get(from_state, [])
        
    @classmethod
    def get_transition_reasons(cls):
        """
        Get standard transition reasons for state changes.
        
        Returns:
            Dictionary mapping transition types to reason codes
        """
        return {
            "startup": {
                "normal_startup": "Component started normally",
                "fast_startup": "Component started quickly",
                "slow_startup": "Component started slowly",
                "partial_startup": "Component started with limited functionality"
            },
            "degradation": {
                "resource_exhaustion": "Component running out of resources",
                "dependency_failure": "Dependent component is unavailable",
                "throughput_reduction": "Component processing throughput reduced",
                "latency_increase": "Component response time increased",
                "error_rate_increase": "Component error rate exceeded threshold",
                "partial_functionality": "Some component features unavailable"
            },
            "recovery": {
                "self_healing": "Component recovered automatically",
                "dependency_restored": "Required dependency became available",
                "resource_restored": "Resource constraints resolved",
                "manual_intervention": "Manual intervention resolved issues",
                "config_update": "Configuration update resolved issues",
                "restart_recovery": "Component recovered after restart"
            },
            "failure": {
                "initialization_error": "Error during component initialization",
                "critical_dependency": "Critical dependency unavailable",
                "resource_starvation": "Severe resource constraints",
                "internal_error": "Unrecoverable internal error",
                "crash": "Component process crashed",
                "deadlock": "Component deadlocked",
                "config_error": "Invalid configuration",
                "version_mismatch": "Incompatible component versions"
            }
        }


class ReadinessCondition:
    """
    A condition that must be satisfied for a component to be considered ready.
    
    Enables fine-grained tracking of component startup progress and dependency
    satisfaction.
    """
    
    def __init__(self, 
                name: str, 
                check_func: Callable[[], Awaitable[bool]], 
                description: Optional[str] = None,
                timeout: Optional[float] = 60.0):
        """
        Initialize a readiness condition.
        
        Args:
            name: Condition name
            check_func: Async function that returns True if condition is satisfied
            description: Optional description
            timeout: Optional timeout in seconds
        """
        self.name = name
        self.check_func = check_func
        self.description = description or f"Condition: {name}"
        self.timeout = timeout
        self.satisfied = False
        self.last_check_time = 0
        self.last_error = None
    
    async def check(self) -> bool:
        """
        Check if the condition is satisfied.
        
        Returns:
            True if satisfied
        """
        try:
            self.last_check_time = time.time()
            self.satisfied = await self.check_func()
            self.last_error = None
            return self.satisfied
        except Exception as e:
            self.satisfied = False
            self.last_error = str(e)
            logger.error(f"Error checking readiness condition {self.name}: {e}")
            return False


class ComponentRegistration:
    """
    Enhanced component registration with unique instance tracking.
    
    Provides unique identity for component instances across restarts to prevent
    duplicate instances and track component lifecycle.
    """
    
    def __init__(self, 
                component_id: str,
                component_name: str,
                component_type: str,
                instance_uuid: Optional[str] = None,
                version: str = "0.1.0",
                capabilities: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize component registration.
        
        Args:
            component_id: Unique component identifier
            component_name: Human-readable name
            component_type: Type of component
            instance_uuid: Optional instance UUID (generated if None)
            version: Component version
            capabilities: Optional component capabilities
            metadata: Optional metadata
        """
        self.component_id = component_id
        self.component_name = component_name
        self.component_type = component_type
        self.instance_uuid = instance_uuid or str(uuid.uuid4())
        self.version = version
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.start_time = time.time()
        self.state = ComponentState.INITIALIZING.value
        self.state_history = [{
            "state": self.state,
            "timestamp": self.start_time,
            "reason": "initialization",
            "details": "Component registration created"
        }]
        self.readiness_conditions = {}
        self.heartbeat_sequence = 0
        self.health_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "request_latency": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0,
            "uptime": 0.0
        }
        self.recovery_attempts = 0
        self.last_recovery_time = 0
        
    def update_state(self, new_state: str, reason: str = None, details: str = None) -> bool:
        """
        Update component state with validation and history tracking.
        
        Args:
            new_state: New state to transition to
            reason: Reason code for the transition
            details: Additional details about the transition
            
        Returns:
            True if state transition was valid and succeeded
        """
        # Validate state transition
        if not ComponentState.validate_transition(self.state, new_state):
            return False
            
        # Record previous state
        old_state = self.state
        
        # Update state
        self.state = new_state
        
        # Record state change in history
        self.state_history.append({
            "state": new_state,
            "previous_state": old_state,
            "timestamp": time.time(),
            "reason": reason or "manual_update",
            "details": details or f"State changed from {old_state} to {new_state}"
        })
        
        # Limit history size
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
            
        return True
        
    def update_health_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Update component health metrics.
        
        Args:
            metrics: Dictionary of health metrics
        """
        self.health_metrics.update(metrics)
        
        # Calculate uptime
        self.health_metrics["uptime"] = time.time() - self.start_time
        
    def record_recovery_attempt(self, reason: str = None) -> int:
        """
        Record a recovery attempt for this component.
        
        Args:
            reason: Optional reason for recovery
            
        Returns:
            Total number of recovery attempts
        """
        self.recovery_attempts += 1
        self.last_recovery_time = time.time()
        
        # Add to state history
        self.state_history.append({
            "state": self.state,
            "timestamp": self.last_recovery_time,
            "reason": "recovery_attempt",
            "details": reason or f"Recovery attempt #{self.recovery_attempts}",
            "recovery_count": self.recovery_attempts
        })
        
        return self.recovery_attempts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "component_type": self.component_type,
            "instance_uuid": self.instance_uuid,
            "version": self.version,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "start_time": self.start_time,
            "state": self.state,
            "state_history": self.state_history,
            "health_metrics": self.health_metrics,
            "recovery_attempts": self.recovery_attempts,
            "last_recovery_time": self.last_recovery_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentRegistration':
        """Create from dictionary."""
        instance = cls(
            component_id=data.get("component_id"),
            component_name=data.get("component_name"),
            component_type=data.get("component_type"),
            instance_uuid=data.get("instance_uuid"),
            version=data.get("version", "0.1.0"),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {})
        )
        instance.start_time = data.get("start_time", time.time())
        instance.state = data.get("state", ComponentState.INITIALIZING.value)
        instance.state_history = data.get("state_history", [{
            "state": instance.state,
            "timestamp": instance.start_time,
            "reason": "initialization",
            "details": "Component loaded from persistence"
        }])
        instance.health_metrics = data.get("health_metrics", instance.health_metrics)
        instance.recovery_attempts = data.get("recovery_attempts", 0)
        instance.last_recovery_time = data.get("last_recovery_time", 0)
        return instance
        
    def get_state_transition_summary(self) -> Dict[str, Any]:
        """
        Get a summary of state transitions.
        
        Returns:
            Dictionary with state transition statistics
        """
        if not self.state_history:
            return {"transitions": 0}
            
        transitions = len(self.state_history) - 1
        states_visited = set(item["state"] for item in self.state_history)
        current_state_duration = time.time() - self.state_history[-1]["timestamp"]
        
        # Calculate time spent in each state
        state_durations = {}
        for i in range(len(self.state_history)):
            state = self.state_history[i]["state"]
            start_time = self.state_history[i]["timestamp"]
            end_time = self.state_history[i+1]["timestamp"] if i < len(self.state_history) - 1 else time.time()
            
            if state not in state_durations:
                state_durations[state] = 0
                
            state_durations[state] += end_time - start_time
            
        return {
            "transitions": transitions,
            "states_visited": len(states_visited),
            "state_list": list(states_visited),
            "current_state_duration": current_state_duration,
            "state_durations": state_durations,
            "recovery_attempts": self.recovery_attempts
        }


class PersistentMessageQueue:
    """
    Message queue with history for reliable message delivery.
    
    Ensures components don't miss messages during startup or restart by
    maintaining message history and tracking delivered messages.
    """
    
    def __init__(self, topic: str = "default", max_history: int = 100):
        """
        Initialize a persistent message queue.
        
        Args:
            topic: Topic name
            max_history: Maximum number of messages to keep
        """
        self.topic = topic
        self.messages = []
        self.max_history = max_history
        self.subscribers = {}  # Map of subscriber_id to last_msg_id processed
        self.lock = asyncio.Lock()
    
    async def add_message(self, message: Any, sender_id: Optional[str] = None) -> str:
        """
        Add a message to the queue.
        
        Args:
            message: Message content
            sender_id: Optional sender ID
            
        Returns:
            Message ID
        """
        async with self.lock:
            msg_id = str(uuid.uuid4())
            self.messages.append({
                "id": msg_id,
                "sender_id": sender_id,
                "timestamp": time.time(),
                "content": message
            })
            
            # Trim history if needed
            if len(self.messages) > self.max_history:
                self.messages = self.messages[-self.max_history:]
                
            return msg_id
    
    async def get_messages_since(self, subscriber_id: str, last_msg_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages since the last processed message for a subscriber.
        
        Args:
            subscriber_id: Subscriber ID
            last_msg_id: Optional last message ID processed
            
        Returns:
            List of messages
        """
        async with self.lock:
            # If no last message ID, use the one stored for the subscriber
            if not last_msg_id and subscriber_id in self.subscribers:
                last_msg_id = self.subscribers.get(subscriber_id)
                
            # If still no last message ID, return all messages
            if not last_msg_id:
                return self.messages
                
            # Find index of last received message
            for i, msg in enumerate(self.messages):
                if msg["id"] == last_msg_id:
                    # Update subscriber's last message ID
                    if self.messages:
                        self.subscribers[subscriber_id] = self.messages[-1]["id"]
                    return self.messages[i+1:]
                    
            # If message not found, return all (may have been pruned)
            # Update subscriber's last message ID
            if self.messages:
                self.subscribers[subscriber_id] = self.messages[-1]["id"]
            return self.messages