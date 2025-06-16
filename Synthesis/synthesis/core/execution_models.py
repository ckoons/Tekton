#!/usr/bin/env python3
"""
Synthesis Execution Models

This module defines the data models and enums used by the Synthesis execution engine.
"""

import uuid
import time
from typing import Dict, List, Any, Optional, Union


class ExecutionStage:
    """Execution stages for tracking progress."""
    PLANNING = "planning"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    COMPLETION = "completion"


class ExecutionStatus:
    """Execution status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionPriority:
    """Execution priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class ExecutionResult:
    """Container for execution results."""
    
    def __init__(self, 
                success: bool, 
                data: Optional[Dict[str, Any]] = None,
                message: Optional[str] = None,
                errors: Optional[List[str]] = None):
        """
        Initialize execution result.
        
        Args:
            success: Whether the execution was successful
            data: Result data
            message: Optional message
            errors: Optional list of errors
        """
        self.success = success
        self.data = data or {}
        self.message = message
        self.errors = errors or []
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "errors": self.errors,
            "timestamp": self.timestamp
        }


class ExecutionPlan:
    """Represents a plan to be executed."""
    
    def __init__(self, 
                plan_id: Optional[str] = None,
                name: Optional[str] = None,
                description: Optional[str] = None,
                steps: Optional[List[Dict[str, Any]]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                priority: int = ExecutionPriority.NORMAL):
        """
        Initialize execution plan.
        
        Args:
            plan_id: Unique identifier
            name: Plan name
            description: Plan description
            steps: Execution steps
            metadata: Additional metadata
            priority: Execution priority
        """
        self.plan_id = plan_id or str(uuid.uuid4())
        self.name = name or f"Plan-{self.plan_id[:8]}"
        self.description = description
        self.steps = steps or []
        self.metadata = metadata or {}
        self.priority = priority
        self.created_at = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "metadata": self.metadata,
            "priority": self.priority,
            "created_at": self.created_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionPlan':
        """Create from dictionary."""
        plan = cls(
            plan_id=data.get("plan_id"),
            name=data.get("name"),
            description=data.get("description"),
            steps=data.get("steps", []),
            metadata=data.get("metadata", {}),
            priority=data.get("priority", ExecutionPriority.NORMAL)
        )
        if "created_at" in data:
            plan.created_at = data["created_at"]
        return plan


class ExecutionContext:
    """Execution context for a plan."""
    
    def __init__(self, 
                context_id: Optional[str] = None,
                plan_id: Optional[str] = None,
                status: str = ExecutionStatus.PENDING,
                current_stage: str = ExecutionStage.PLANNING,
                current_step: int = 0,
                variables: Optional[Dict[str, Any]] = None,
                results: Optional[List[Dict[str, Any]]] = None,
                errors: Optional[List[str]] = None,
                start_time: Optional[float] = None,
                end_time: Optional[float] = None):
        """
        Initialize execution context.
        
        Args:
            context_id: Unique identifier
            plan_id: Associated plan ID
            status: Current status
            current_stage: Current execution stage
            current_step: Index of current step
            variables: Context variables
            results: Step execution results
            errors: Execution errors
            start_time: Execution start time
            end_time: Execution end time
        """
        self.context_id = context_id or str(uuid.uuid4())
        self.plan_id = plan_id
        self.status = status
        self.current_stage = current_stage
        self.current_step = current_step
        self.variables = variables or {}
        self.results = results or []
        self.errors = errors or []
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "context_id": self.context_id,
            "plan_id": self.plan_id,
            "status": self.status,
            "current_stage": self.current_stage,
            "current_step": self.current_step,
            "variables": self.variables,
            "results": self.results,
            "errors": self.errors,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "created_at": self.created_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionContext':
        """Create from dictionary."""
        context = cls(
            context_id=data.get("context_id"),
            plan_id=data.get("plan_id"),
            status=data.get("status", ExecutionStatus.PENDING),
            current_stage=data.get("current_stage", ExecutionStage.PLANNING),
            current_step=data.get("current_step", 0),
            variables=data.get("variables", {}),
            results=data.get("results", []),
            errors=data.get("errors", []),
            start_time=data.get("start_time"),
            end_time=data.get("end_time")
        )
        if "created_at" in data:
            context.created_at = data["created_at"]
        return context