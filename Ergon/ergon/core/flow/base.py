"""
Base flow interface for Ergon.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from ergon.core.flow.types import FlowType, Plan, PlanStep, StepStatus

logger = logging.getLogger(__name__)


class BaseFlow(ABC):
    """Base interface for flows"""
    
    def __init__(self, agents: Dict[str, Any], **kwargs):
        """
        Initialize the flow
        
        Args:
            agents: Dictionary of agents to use in the flow, keyed by name
            **kwargs: Additional flow-specific arguments
        """
        self.agents = agents
        self.flow_type = None
        
    @abstractmethod
    async def execute(self, input_text: str) -> str:
        """
        Execute the flow with the given input
        
        Args:
            input_text: Input text to process
            
        Returns:
            Flow execution result
        """
        pass
    
    def get_executor(self, step: PlanStep) -> Any:
        """
        Get an agent to execute a step
        
        Args:
            step: The step to execute
            
        Returns:
            Agent to execute the step
        """
        # Try to extract agent type from step description using regex
        # Example formats: [BROWSER], [CODE], [SEARCH]
        if not step.agent_type:
            pattern = r'\[([A-Z_]+)\]'
            match = re.search(pattern, step.description)
            if match:
                step.agent_type = match.group(1).lower()
                
        # Use agent type if available
        if step.agent_type and step.agent_type.lower() in self.agents:
            return self.agents[step.agent_type.lower()]
            
        # Otherwise, use the default agent (first in the list)
        if self.agents:
            return list(self.agents.values())[0]
            
        # No agents available
        raise ValueError("No agents available to execute step")
        
    def format_plan(self, plan: Plan) -> str:
        """
        Format plan for display
        
        Args:
            plan: Plan to format
            
        Returns:
            Formatted plan string
        """
        status_markers = {
            StepStatus.NOT_STARTED: "[ ]",
            StepStatus.IN_PROGRESS: "[→]",
            StepStatus.COMPLETED: "[✓]",
            StepStatus.BLOCKED: "[!]",
            StepStatus.FAILED: "[✗]"
        }
        
        lines = [f"Plan: {plan.title} (ID: {plan.plan_id})"]
        lines.append("-" * 50)
        
        for step in sorted(plan.steps, key=lambda s: s.index):
            marker = status_markers.get(step.status, "[ ]")
            lines.append(f"{marker} Step {step.index + 1}: {step.description}")
            if step.note:
                lines.append(f"    Note: {step.note}")
                
        lines.append("-" * 50)
        progress = plan.get_progress()
        lines.append(f"Progress: {progress['completed']}/{progress['total']} steps completed ({progress['percent_complete']:.1f}%)")
        
        return "\n".join(lines)