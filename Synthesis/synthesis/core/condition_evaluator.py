#!/usr/bin/env python3
"""
Synthesis Condition Evaluator

This module handles condition evaluation for Synthesis execution steps.
"""

import logging
from typing import Dict, Any

from synthesis.core.execution_models import ExecutionContext

# Configure logging
logger = logging.getLogger("synthesis.core.condition_evaluator")


async def evaluate_condition(condition: str, context: ExecutionContext) -> bool:
    """
    Evaluate a condition expression.
    
    Args:
        condition: Condition expression
        context: Execution context
        
    Returns:
        Boolean result of the condition
    """
    # This is a simplified implementation
    # In a real implementation, we would use a proper expression evaluator
    # that can access context variables and handle complex conditions
    
    # Check if condition is a path/key in the context variables
    parts = condition.split(".")
    if parts[0] in context.variables:
        value = context.variables[parts[0]]
        
        # Navigate nested structure
        for part in parts[1:]:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return False
                
        # Convert to boolean
        return bool(value)
        
    # Simple built-in conditions
    if condition == "true":
        return True
    elif condition == "false":
        return False
        
    # Execute as Python code (CAUTION: This is potentially dangerous!)
    # In a real implementation, we would use a safer approach
    try:
        # Create local variables from context
        locals_dict = {"context": context, **context.variables}
        
        # Execute condition
        result = eval(condition, {"__builtins__": {}}, locals_dict)
        return bool(result)
    except Exception as e:
        logger.error(f"Error evaluating condition '{condition}': {e}")
        return False