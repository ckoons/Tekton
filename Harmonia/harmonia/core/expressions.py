"""
Expression evaluation for Harmonia.

This module provides functions for evaluating expressions in workflow
definitions, including parameter substitution and conditional expressions.
"""

import logging
import re
import json
from copy import deepcopy
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logger
logger = logging.getLogger(__name__)

# Expression syntax patterns
PARAM_PATTERN = r"\${(param\.[^}]+)}"
ENV_PATTERN = r"\${(env\.[^}]+)}"
TASK_PATTERN = r"\${(tasks\.[^}]+)}"
CONTEXT_PATTERN = r"\${(context\.[^}]+)}"
EXPR_PATTERN = r"\${(expr\.[^}]+)}"
COMBINED_PATTERN = r"\${([^}]+)}"


def evaluate_expression(
    expression: str,
    context: Dict[str, Any],
    safe_mode: bool = True
) -> Any:
    """
    Evaluate an expression within a given context.
    
    Args:
        expression: Expression to evaluate
        context: Context containing variables
        safe_mode: Whether to restrict evaluation to simple expressions
        
    Returns:
        Result of the expression evaluation
    """
    if not expression or not isinstance(expression, str):
        return expression
    
    # Check if the entire string is an expression
    if expression.startswith("${") and expression.endswith("}"):
        # Extract the expression without the ${} wrapper
        expr = expression[2:-1]
        
        # Handle different expression types
        if expr.startswith("param."):
            param_name = expr[6:]
            return get_nested_value(context.get("params", {}), param_name)
            
        elif expr.startswith("env."):
            env_name = expr[4:]
            return get_nested_value(context.get("env", {}), env_name)
            
        elif expr.startswith("tasks."):
            task_path = expr[6:]
            return get_nested_value(context.get("tasks", {}), task_path)
            
        elif expr.startswith("context."):
            context_path = expr[8:]
            return get_nested_value(context, context_path)
            
        elif expr.startswith("expr."):
            if safe_mode:
                logger.warning(f"Expression evaluation not allowed in safe mode: {expr}")
                return expression
            
            # This is potentially unsafe and should be used with caution
            expr_body = expr[5:]
            try:
                # Create a restricted environment for evaluation
                env = {**context}
                result = eval(expr_body, {"__builtins__": {}}, env)
                return result
            except Exception as e:
                logger.error(f"Error evaluating expression: {expr_body} - {e}")
                return expression
        
        # If no specific prefix, try to find the key in the context
        return get_nested_value(context, expr, expression)
    
    # Check if the string contains embedded expressions
    matches = re.findall(COMBINED_PATTERN, expression)
    if not matches:
        return expression
    
    # Replace all expressions in the string
    result = expression
    for match in matches:
        # Recursively evaluate the embedded expression
        replacement = evaluate_expression(f"${{{match}}}", context, safe_mode)
        if replacement is not None:
            result = result.replace(f"${{{match}}}", str(replacement))
    
    return result


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a value from a nested dictionary using a dot-separated path.
    
    Args:
        data: Dictionary to extract value from
        path: Dot-separated path to the value
        default: Default value if path not found
        
    Returns:
        Value at the path or default
    """
    if not data:
        return default
    
    parts = path.split(".")
    current = data
    
    for part in parts:
        # Handle array indexing
        if "[" in part and part.endswith("]"):
            name, index_str = part.split("[", 1)
            index = int(index_str[:-1])
            
            if not isinstance(current, dict) or name not in current:
                return default
            
            current = current[name]
            
            if not isinstance(current, list) or index >= len(current):
                return default
            
            current = current[index]
        else:
            if not isinstance(current, dict) or part not in current:
                return default
            
            current = current[part]
    
    return current


def substitute_parameters(
    data: Any,
    params: Dict[str, Any],
    env: Dict[str, Any] = None,
    tasks: Dict[str, Any] = None,
    context: Dict[str, Any] = None
) -> Any:
    """
    Recursively substitute parameters in a data structure.
    
    Args:
        data: Data structure to process
        params: Parameter values
        env: Environment variables
        tasks: Task results
        context: Additional context
        
    Returns:
        Processed data structure with substitutions
    """
    # Create the evaluation context
    eval_context = {
        "params": params,
        "env": env or {},
        "tasks": tasks or {},
        **(context or {})
    }
    
    # Deep copy to avoid modifying the original
    data_copy = deepcopy(data)
    return _substitute_recursive(data_copy, eval_context)


def _substitute_recursive(data: Any, context: Dict[str, Any]) -> Any:
    """Recursively process data structure for parameter substitution."""
    if isinstance(data, str):
        return evaluate_expression(data, context)
    
    elif isinstance(data, dict):
        return {k: _substitute_recursive(v, context) for k, v in data.items()}
    
    elif isinstance(data, list):
        return [_substitute_recursive(item, context) for item in data]
    
    else:
        return data


def evaluate_condition(
    condition: Union[str, Dict[str, Any]],
    context: Dict[str, Any]
) -> bool:
    """
    Evaluate a condition expression or object.
    
    Args:
        condition: Condition to evaluate (string expression or condition object)
        context: Context for evaluation
        
    Returns:
        Boolean result of condition evaluation
    """
    if isinstance(condition, str):
        result = evaluate_expression(condition, context, safe_mode=False)
        return bool(result)
    
    elif isinstance(condition, dict):
        if "expr" in condition:
            # Simple expression
            return bool(evaluate_expression(condition["expr"], context, safe_mode=False))
        
        elif "and" in condition:
            # AND condition
            sub_conditions = condition["and"]
            return all(evaluate_condition(c, context) for c in sub_conditions)
        
        elif "or" in condition:
            # OR condition
            sub_conditions = condition["or"]
            return any(evaluate_condition(c, context) for c in sub_conditions)
        
        elif "not" in condition:
            # NOT condition
            sub_condition = condition["not"]
            return not evaluate_condition(sub_condition, context)
        
        elif "eq" in condition:
            # Equality condition
            left = evaluate_expression(condition["eq"][0], context)
            right = evaluate_expression(condition["eq"][1], context)
            return left == right
        
        elif "neq" in condition:
            # Inequality condition
            left = evaluate_expression(condition["neq"][0], context)
            right = evaluate_expression(condition["neq"][1], context)
            return left != right
        
        elif "gt" in condition:
            # Greater than condition
            left = evaluate_expression(condition["gt"][0], context)
            right = evaluate_expression(condition["gt"][1], context)
            return left > right
        
        elif "gte" in condition:
            # Greater than or equal condition
            left = evaluate_expression(condition["gte"][0], context)
            right = evaluate_expression(condition["gte"][1], context)
            return left >= right
        
        elif "lt" in condition:
            # Less than condition
            left = evaluate_expression(condition["lt"][0], context)
            right = evaluate_expression(condition["lt"][1], context)
            return left < right
        
        elif "lte" in condition:
            # Less than or equal condition
            left = evaluate_expression(condition["lte"][0], context)
            right = evaluate_expression(condition["lte"][1], context)
            return left <= right
        
        elif "in" in condition:
            # Containment condition
            item = evaluate_expression(condition["in"][0], context)
            container = evaluate_expression(condition["in"][1], context)
            return item in container
        
        elif "contains" in condition:
            # Collection containment condition
            container = evaluate_expression(condition["contains"][0], context)
            item = evaluate_expression(condition["contains"][1], context)
            return item in container
        
        else:
            logger.warning(f"Unknown condition type: {condition}")
            return False
    
    else:
        # For any other type, convert to boolean
        return bool(condition)