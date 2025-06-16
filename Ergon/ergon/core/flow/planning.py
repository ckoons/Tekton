"""
Planning flow implementation for Ergon.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio

from ergon.core.flow.base import BaseFlow
from ergon.core.flow.tools import PlanningTool, PLANNING_SYSTEM_PROMPT, NEXT_STEP_PROMPT
from ergon.core.flow.types import Plan, PlanStep, StepStatus, FlowType
from ergon.utils.config.settings import settings

logger = logging.getLogger(__name__)


class PlanningFlow(BaseFlow):
    """Flow that uses a planning approach for execution"""
    
    def __init__(self, agents: Dict[str, Any], max_steps: int = 30, **kwargs):
        """
        Initialize the planning flow
        
        Args:
            agents: Dictionary of agents to use in the flow, keyed by name
            max_steps: Maximum number of execution steps
            **kwargs: Additional flow-specific arguments
        """
        super().__init__(agents, **kwargs)
        self.flow_type = FlowType.PLANNING
        self.max_steps = max_steps
        self.planning_tool = PlanningTool()
        
    async def execute(self, input_text: str) -> str:
        """
        Execute the flow with the given input
        
        Args:
            input_text: Input text to process
            
        Returns:
            Flow execution result
        """
        logger.info(f"Executing planning flow with input: {input_text[:100]}...")
        
        # Create initial plan
        plan = await self._create_initial_plan(input_text)
        if not plan:
            return "Failed to create a plan. Please try again with a more specific task."
            
        # Execute steps
        step_count = 0
        plan_summary = self.format_plan(plan)
        logger.info(f"Created plan:\n{plan_summary}")
        
        while step_count < self.max_steps:
            # Get current step
            current_step = plan.get_current_step()
            if not current_step:
                # No more steps to execute
                logger.info("Plan completed. All steps executed.")
                break
                
            # Mark step as in progress
            current_step.status = StepStatus.IN_PROGRESS
            
            # Get executor for step
            try:
                executor = self.get_executor(current_step)
            except ValueError as e:
                logger.error(f"Failed to get executor for step {current_step.index}: {str(e)}")
                current_step.status = StepStatus.FAILED
                current_step.note = f"Failed to get executor: {str(e)}"
                continue
                
            # Execute step
            logger.info(f"Executing step {current_step.index + 1}: {current_step.description}")
            
            # Create step-specific prompt with plan context
            step_prompt = NEXT_STEP_PROMPT.format(
                plan=self.format_plan(plan),
                step_number=current_step.index + 1,
                step_description=current_step.description
            )
            step_prompt += f"\nInput: {input_text}"
            
            try:
                # Run the executor with the step prompt
                result = await executor.run(step_prompt)
                
                # Mark step as completed
                current_step.status = StepStatus.COMPLETED
                current_step.note = result
                
                logger.info(f"Step {current_step.index + 1} completed successfully")
            except Exception as e:
                logger.error(f"Failed to execute step {current_step.index + 1}: {str(e)}")
                current_step.status = StepStatus.FAILED
                current_step.note = f"Execution failed: {str(e)}"
                
            # Increment step count
            step_count += 1
            
        # Create final summary
        completed_steps = len([s for s in plan.steps if s.status == StepStatus.COMPLETED])
        total_steps = len(plan.steps)
        
        if completed_steps == total_steps:
            status_message = "✅ All steps completed successfully!"
        elif step_count >= self.max_steps:
            status_message = f"⚠️ Maximum step count ({self.max_steps}) reached before completing the plan."
        else:
            status_message = f"⚠️ Plan execution stopped with {completed_steps}/{total_steps} steps completed."
            
        # Generate final report
        summary = f"# Plan Execution Summary\n\n"
        summary += f"{status_message}\n\n"
        summary += self.format_plan(plan)
        summary += "\n\n## Results\n\n"
        
        for step in sorted(plan.steps, key=lambda s: s.index):
            summary += f"### Step {step.index + 1}: {step.description}\n"
            if step.status == StepStatus.COMPLETED and step.note:
                summary += f"**Result**: {step.note}\n\n"
            elif step.status == StepStatus.FAILED and step.note:
                summary += f"**Error**: {step.note}\n\n"
            else:
                summary += f"**Status**: {step.status}\n\n"
                
        logger.info(f"Plan execution completed: {completed_steps}/{total_steps} steps")
        return summary
    
    async def _create_initial_plan(self, input_text: str) -> Optional[Plan]:
        """
        Create an initial plan from the input text
        
        Args:
            input_text: Input text to process
            
        Returns:
            The created plan or None if failed
        """
        logger.info("Creating initial plan...")
        
        # Try to extract plan from existing primary agent if available
        if self.agents:
            primary_agent = list(self.agents.values())[0]
            
            # Create messages for the agent
            messages = [
                {"role": "system", "content": PLANNING_SYSTEM_PROMPT},
                {"role": "user", "content": f"Create a plan for the following task:\n\n{input_text}"}
            ]
            
            try:
                # Use the agent's LLM client to get a response
                plan_response = await primary_agent.llm_client.acomplete(messages)
                
                # Try to parse the plan from the response
                plan_data = self._parse_plan_from_text(plan_response)
                if plan_data:
                    title, steps = plan_data
                    
                    # Create the plan
                    return self.planning_tool.create_plan(title, steps)
            except Exception as e:
                logger.error(f"Failed to create plan using primary agent: {str(e)}")
                
        # Fallback: Create a simple plan
        logger.warning("Using fallback plan creation...")
        title = f"Plan for: {input_text[:50]}..."
        steps = [{"description": f"Complete the task: {input_text}"}]
        
        return self.planning_tool.create_plan(title, steps)
        
    def _parse_plan_from_text(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """
        Parse a plan from text
        
        Args:
            text: Text to parse
            
        Returns:
            Tuple of (title, steps) if successful, None otherwise
        """
        # Try to extract plan title
        title_match = re.search(r"(?:Plan title:|Title:|#\s*Plan:)\s*(.*?)(?:\n|$)", text, re.IGNORECASE)
        if not title_match:
            title_match = re.search(r"^(?:\d+\.\s*)?([^\n]+)", text)
            
        title = title_match.group(1).strip() if title_match else "Untitled Plan"
        
        # Try to extract steps
        steps = []
        
        # Look for numbered steps
        step_matches = re.findall(r"(?:Step\s*\d+:|(?:\d+)\.\s+)(.*?)(?=(?:Step\s*\d+:|(?:\d+)\.\s+)|$)", text, re.DOTALL)
        
        if step_matches:
            # Process and clean up each step
            for step_text in step_matches:
                step_text = step_text.strip()
                if step_text:
                    # Split into multiple lines if needed
                    lines = step_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('-'):
                            steps.append(line)
                            break
        else:
            # Try to find bulleted lists or plain text paragraphs
            paragraphs = re.split(r'\n\s*\n', text)
            for para in paragraphs:
                if para.strip() and para.strip() != title:
                    # Look for bulleted items
                    bullets = re.findall(r"(?:[-*]\s+)(.*?)(?:\n|$)", para)
                    if bullets:
                        steps.extend([b.strip() for b in bullets if b.strip()])
                    else:
                        # Just add the paragraph as a step
                        steps.append(para.strip())
                        
        # Ensure we have at least one step
        if not steps:
            steps = [f"Complete the task: {title}"]
            
        return title, steps