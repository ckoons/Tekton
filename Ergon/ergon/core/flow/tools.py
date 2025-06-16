"""
Planning tools for Ergon flows.
"""

import logging
import uuid
import json
import re
from typing import Dict, List, Any, Optional, Tuple

from ergon.core.flow.types import Plan, PlanStep, StepStatus

logger = logging.getLogger(__name__)

# System prompts for planning
PLANNING_SYSTEM_PROMPT = """
You are a planning assistant that helps create and manage structured plans.
For the given task, create a detailed plan with the following structure:

1. Plan title: A concise description of the overall task
2. Steps: A list of detailed, actionable steps to accomplish the task

Follow these guidelines for creating effective plans:
- Break down complex tasks into smaller, manageable steps
- Make each step specific and actionable
- Include all necessary information for completing each step
- Aim for 5-10 steps for most tasks (but use as many as needed)
- Whenever a step requires a specific agent type, indicate it in square brackets at the beginning
  For example: [BROWSER] Navigate to github.com

Agent types you can indicate:
- [BROWSER]: For web browsing and interaction tasks
- [SEARCH]: For search and information retrieval
- [CODE]: For code generation or analysis
- [GITHUB]: For GitHub operations
- [MAIL]: For email operations

After creating your plan, I'll help you execute it step by step.
"""

# Prompt for the next step in a plan
NEXT_STEP_PROMPT = """
You are currently executing a plan. Here is the current plan status:

{plan}

You are now working on step {step_number}: {step_description}

Your task is to:
1. Execute this step based on its description
2. Provide a detailed response that accomplishes this step

Focus ONLY on the current step. Do not try to execute multiple steps at once.
If you need information from previous steps, reference the notes included in the plan.
"""


class PlanningTool:
    """Tool for managing plans"""
    
    def __init__(self):
        """Initialize the planning tool"""
        self.plans: Dict[str, Plan] = {}
        
    def create_plan(self, title: str, steps: List[Dict[str, Any]]) -> Plan:
        """
        Create a new plan
        
        Args:
            title: Title of the plan
            steps: List of step descriptions
            
        Returns:
            The created plan
        """
        plan_id = str(uuid.uuid4())
        
        # Convert step dictionaries to PlanStep objects
        plan_steps = []
        for i, step_data in enumerate(steps):
            if isinstance(step_data, dict):
                description = step_data.get("description", "")
                agent_type = step_data.get("agent_type")
            else:
                description = str(step_data)
                agent_type = self._extract_agent_type(description)
                
            plan_steps.append(PlanStep(
                description=description,
                index=i,
                status=StepStatus.NOT_STARTED,
                agent_type=agent_type
            ))
            
        # Create the plan
        plan = Plan(
            plan_id=plan_id,
            title=title,
            steps=plan_steps
        )
        
        # Store the plan
        self.plans[plan_id] = plan
        return plan
        
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """
        Get a plan by ID
        
        Args:
            plan_id: ID of the plan to get
            
        Returns:
            The plan if found, None otherwise
        """
        return self.plans.get(plan_id)
        
    def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> Optional[Plan]:
        """
        Update a plan
        
        Args:
            plan_id: ID of the plan to update
            updates: Dictionary of updates to apply
            
        Returns:
            The updated plan if found, None otherwise
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return None
            
        # Apply updates
        if "title" in updates:
            plan.title = updates["title"]
            
        if "steps" in updates:
            # Replace steps (careful with this!)
            new_steps = []
            for i, step_data in enumerate(updates["steps"]):
                if isinstance(step_data, dict):
                    description = step_data.get("description", "")
                    status = step_data.get("status", StepStatus.NOT_STARTED)
                    agent_type = step_data.get("agent_type")
                    note = step_data.get("note")
                else:
                    description = str(step_data)
                    status = StepStatus.NOT_STARTED
                    agent_type = self._extract_agent_type(description)
                    note = None
                    
                new_steps.append(PlanStep(
                    description=description,
                    index=i,
                    status=status,
                    agent_type=agent_type,
                    note=note
                ))
            plan.steps = new_steps
            
        if "metadata" in updates:
            plan.metadata.update(updates["metadata"])
            
        return plan
        
    def mark_step(self, plan_id: str, step_index: int, status: str, note: Optional[str] = None) -> Optional[Plan]:
        """
        Mark a step with a status and optional note
        
        Args:
            plan_id: ID of the plan
            step_index: Index of the step to mark
            status: Status to set on the step
            note: Optional note to add to the step
            
        Returns:
            The updated plan if found, None otherwise
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return None
            
        # Find and update the step
        step = plan.get_step_by_index(step_index)
        if not step:
            return None
            
        # Update status
        try:
            step.status = StepStatus(status)
        except ValueError:
            step.status = StepStatus.NOT_STARTED
            
        # Update note if provided
        if note:
            step.note = note
            
        return plan
        
    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a plan
        
        Args:
            plan_id: ID of the plan to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if plan_id in self.plans:
            del self.plans[plan_id]
            return True
        return False
        
    def _extract_agent_type(self, description: str) -> Optional[str]:
        """
        Extract agent type from step description
        
        Args:
            description: Step description
            
        Returns:
            Agent type if found, None otherwise
        """
        pattern = r'\[([A-Z_]+)\]'
        match = re.search(pattern, description)
        if match:
            return match.group(1).lower()
        return None