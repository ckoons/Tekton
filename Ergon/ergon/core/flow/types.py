"""
Flow type definitions for Ergon.
"""

from enum import Enum
from typing import Dict, List, Any, Optional


class StepStatus(str, Enum):
    """Status of a step in a plan"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class FlowType(str, Enum):
    """Type of flow to execute"""
    SIMPLE = "simple"  # Direct agent execution
    PLANNING = "planning"  # LLM-based planning
    PARALLEL = "parallel"  # Parallel execution of agents


class PlanStep:
    """A step in a plan"""
    
    def __init__(
        self,
        description: str,
        index: int,
        status: StepStatus = StepStatus.NOT_STARTED,
        agent_type: Optional[str] = None,
        note: Optional[str] = None
    ):
        self.description = description
        self.index = index
        self.status = status
        self.agent_type = agent_type
        self.note = note
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            "description": self.description,
            "index": self.index,
            "status": self.status,
            "agent_type": self.agent_type,
            "note": self.note
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanStep":
        """Create step from dictionary"""
        return cls(
            description=data["description"],
            index=data["index"],
            status=StepStatus(data.get("status", "not_started")),
            agent_type=data.get("agent_type"),
            note=data.get("note")
        )


class Plan:
    """A plan consisting of multiple steps"""
    
    def __init__(
        self,
        plan_id: str,
        title: str,
        steps: List[PlanStep],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.plan_id = plan_id
        self.title = title
        self.steps = steps
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plan":
        """Create plan from dictionary"""
        return cls(
            plan_id=data["plan_id"],
            title=data["title"],
            steps=[PlanStep.from_dict(step) for step in data["steps"]],
            metadata=data.get("metadata", {})
        )
        
    def get_step_by_index(self, index: int) -> Optional[PlanStep]:
        """Get step by index"""
        for step in self.steps:
            if step.index == index:
                return step
        return None
        
    def get_current_step(self) -> Optional[PlanStep]:
        """Get the current active step"""
        # First look for in-progress steps
        for step in self.steps:
            if step.status == StepStatus.IN_PROGRESS:
                return step
                
        # Then look for not-started steps
        for step in self.steps:
            if step.status == StepStatus.NOT_STARTED:
                return step
                
        # No active steps
        return None
        
    def get_progress(self) -> Dict[str, Any]:
        """Get plan progress statistics"""
        total = len(self.steps)
        completed = len([s for s in self.steps if s.status == StepStatus.COMPLETED])
        in_progress = len([s for s in self.steps if s.status == StepStatus.IN_PROGRESS])
        blocked = len([s for s in self.steps if s.status == StepStatus.BLOCKED])
        not_started = len([s for s in self.steps if s.status == StepStatus.NOT_STARTED])
        failed = len([s for s in self.steps if s.status == StepStatus.FAILED])
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "not_started": not_started,
            "failed": failed,
            "percent_complete": (completed / total) * 100 if total > 0 else 0
        }
        
    def update_step_status(self, index: int, status: StepStatus, note: Optional[str] = None) -> bool:
        """Update the status of a step"""
        step = self.get_step_by_index(index)
        if step:
            step.status = status
            if note:
                step.note = note
            return True
        return False