#!/usr/bin/env python3
"""
Synthesis Execution Step

This module defines the ExecutionStep class for executing individual steps.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union

from synthesis.core.execution_models import (
    ExecutionStage, ExecutionStatus, 
    ExecutionPriority, ExecutionResult,
    ExecutionPlan, ExecutionContext
)
from synthesis.core.step_handlers import (
    handle_command_step, handle_function_step, handle_api_step,
    handle_condition_step, handle_loop_step, handle_subprocess_step,
    handle_notify_step, handle_wait_step, handle_variable_step,
    handle_llm_step
)
from synthesis.core.loop_handlers import handle_loop_step

# Configure logging
logger = logging.getLogger("synthesis.core.execution_step")


class ExecutionStep:
    """Step executor for a single plan step."""
    
    def __init__(self, 
                step_data: Dict[str, Any],
                context: ExecutionContext,
                callbacks: Optional[Dict[str, Callable]] = None):
        """
        Initialize execution step.
        
        Args:
            step_data: Step definition and parameters
            context: Execution context
            callbacks: Optional callback functions
        """
        self.step_data = step_data
        self.context = context
        self.callbacks = callbacks or {}
        self.step_id = step_data.get("id") or f"step-{len(context.results)}"
        self.step_type = step_data.get("type", "unknown")
        self.parameters = step_data.get("parameters", {})
        self.dependencies = step_data.get("dependencies", [])
        self.timeout = step_data.get("timeout", 60)  # Default: 60 seconds
        
    async def execute(self) -> ExecutionResult:
        """
        Execute the step.
        
        Returns:
            ExecutionResult with execution status
        """
        # Record start time
        start_time = time.time()
        
        # Check if step type is supported
        if self.step_type not in self._get_step_handlers():
            logger.error(f"Unsupported step type: {self.step_type}")
            return ExecutionResult(
                success=False,
                message=f"Unsupported step type: {self.step_type}",
                errors=[f"Unsupported step type: {self.step_type}"]
            )
        
        try:
            # Get step handler
            handler = self._get_step_handlers()[self.step_type]
            
            # Execute step with timeout
            try:
                # Call the before_step callback if provided
                if "before_step" in self.callbacks:
                    await self.callbacks["before_step"](self.step_id, self.step_type, self.context)
                
                # Execute the step with timeout
                result = await asyncio.wait_for(
                    self._execute_handler(handler),
                    timeout=self.timeout
                )
                
                # Call the after_step callback if provided
                if "after_step" in self.callbacks:
                    await self.callbacks["after_step"](
                        self.step_id, self.step_type, result, self.context
                    )
                
                # Record execution time
                execution_time = time.time() - start_time
                logger.info(f"Step {self.step_id} ({self.step_type}) completed in {execution_time:.2f}s")
                
                # Add execution time to result data
                if isinstance(result, ExecutionResult):
                    result.data["execution_time"] = execution_time
                    return result
                else:
                    # If handler didn't return ExecutionResult, wrap it
                    return ExecutionResult(
                        success=True,
                        data={"result": result, "execution_time": execution_time},
                        message=f"Step {self.step_id} ({self.step_type}) completed successfully"
                    )
                    
            except asyncio.TimeoutError:
                logger.error(f"Step {self.step_id} ({self.step_type}) timed out after {self.timeout}s")
                
                # Call the error callback if provided
                if "on_error" in self.callbacks:
                    await self.callbacks["on_error"](
                        self.step_id, self.step_type, "timeout", self.context
                    )
                
                return ExecutionResult(
                    success=False,
                    message=f"Step {self.step_id} ({self.step_type}) timed out after {self.timeout}s",
                    errors=[f"Step execution timed out after {self.timeout}s"]
                )
                
        except Exception as e:
            logger.exception(f"Error executing step {self.step_id} ({self.step_type}): {e}")
            
            # Call the error callback if provided
            if "on_error" in self.callbacks:
                await self.callbacks["on_error"](
                    self.step_id, self.step_type, str(e), self.context
                )
            
            return ExecutionResult(
                success=False,
                message=f"Error executing step {self.step_id} ({self.step_type}): {e}",
                errors=[str(e)]
            )
    
    async def _execute_handler(self, handler: Callable) -> ExecutionResult:
        """
        Execute the step handler with appropriate arguments.
        
        Args:
            handler: Step handler function
            
        Returns:
            ExecutionResult from the handler
        """
        if self.step_type == "function":
            # Pass function registry callback
            function_registry = self.callbacks.get("function_registry", {})
            return await handler(self.parameters, self.context, function_registry)
        elif self.step_type == "condition":
            # Pass execute_step callback for nested execution
            return await handler(self.parameters, self.context, self._execute_nested_step)
        elif self.step_type == "loop":
            # Handle loop steps
            steps = self.parameters.get("steps", [])
            return await handle_loop_step(self.parameters, steps, self.context, self._execute_nested_step)
        else:
            # Default execution
            return await handler(self.parameters, self.context)
    
    async def _execute_nested_step(self, step_data: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """
        Execute a nested step.
        
        Args:
            step_data: Step data
            context: Execution context
            
        Returns:
            ExecutionResult from the nested step
        """
        step = ExecutionStep(step_data, context, self.callbacks)
        return await step.execute()
    
    def _get_step_handlers(self) -> Dict[str, Callable]:
        """
        Get step type handlers.
        
        Returns:
            Dictionary mapping step types to handler functions
        """
        return {
            "command": handle_command_step,
            "function": handle_function_step,
            "api": handle_api_step,
            "condition": handle_condition_step,
            "loop": handle_loop_step,
            "subprocess": handle_subprocess_step,
            "notify": handle_notify_step,
            "wait": handle_wait_step,
            "variable": handle_variable_step,
            "llm": handle_llm_step,
        }