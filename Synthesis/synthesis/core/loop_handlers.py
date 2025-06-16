#!/usr/bin/env python3
"""
Synthesis Loop Handlers

This module handles loop execution for Synthesis.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable

from synthesis.core.execution_models import ExecutionContext, ExecutionResult
from synthesis.core.condition_evaluator import evaluate_condition

# Configure logging
logger = logging.getLogger("synthesis.core.loop_handlers")


async def handle_loop_step(parameters: Dict[str, Any], 
                        steps: List[Dict[str, Any]],
                        context: ExecutionContext,
                        execute_step_callback) -> ExecutionResult:
    """
    Handle a loop execution step.
    
    Args:
        parameters: Step parameters
        steps: Steps to execute in the loop
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with loop results
    """
    # Get loop type
    loop_type = parameters.get("type", "for")
    
    # Get loop steps
    if not steps:
        return ExecutionResult(
            success=True,
            message="No steps to execute in loop",
            data={"iterations": 0}
        )
        
    try:
        if loop_type == "for":
            # Process for loop
            return await handle_for_loop(parameters, steps, context, execute_step_callback)
        elif loop_type == "while":
            # Process while loop
            return await handle_while_loop(parameters, steps, context, execute_step_callback)
        elif loop_type == "foreach":
            # Process foreach loop (iterates over map/dict)
            return await handle_foreach_loop(parameters, steps, context, execute_step_callback)
        elif loop_type == "count":
            # Process count loop (simple counter)
            return await handle_count_loop(parameters, steps, context, execute_step_callback)
        elif loop_type == "parallel":
            # Process parallel loop
            return await handle_parallel_loop(parameters, steps, context, execute_step_callback)
        else:
            return ExecutionResult(
                success=False,
                message=f"Unsupported loop type: {loop_type}",
                errors=[f"Unsupported loop type: {loop_type}"]
            )
            
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error executing loop: {e}",
            errors=[str(e)]
        )


async def handle_for_loop(parameters: Dict[str, Any], 
                       steps: List[Dict[str, Any]], 
                       context: ExecutionContext, 
                       execute_step_callback) -> ExecutionResult:
    """
    Handle a for loop.
    
    Args:
        parameters: Loop parameters
        steps: Steps to execute in each iteration
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with loop results
    """
    # Get iterable
    iterable = parameters.get("iterable")
    if not iterable:
        return ExecutionResult(
            success=False,
            message="No iterable specified for for loop",
            errors=["No iterable specified for for loop"]
        )
        
    # Get item variable name
    item_var = parameters.get("item_var", "item")
    
    # Get max iterations
    max_iterations = parameters.get("max_iterations", 100)
    
    # Process the iterable
    if isinstance(iterable, str) and "$" in iterable:
        # Check for variable substitution
        for var_name, var_value in context.variables.items():
            placeholder = f"${var_name}"
            if placeholder == iterable and isinstance(var_value, (list, tuple)):
                items = var_value
                break
        else:
            # If no direct match, try as a variable name
            items_name = iterable.replace("$", "")
            if items_name in context.variables and isinstance(context.variables[items_name], (list, tuple)):
                items = context.variables[items_name]
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Invalid iterable variable: {iterable}",
                    errors=[f"Invalid iterable variable: {iterable}"]
                )
    elif isinstance(iterable, str) and iterable in context.variables:
        # Get iterable from context variables
        items = context.variables[iterable]
        if not isinstance(items, (list, tuple)):
            return ExecutionResult(
                success=False,
                message=f"Variable {iterable} is not iterable",
                errors=[f"Variable {iterable} is not iterable (type: {type(items).__name__})"]
            )
    elif isinstance(iterable, (list, tuple)):
        # Use provided list directly
        items = iterable
    else:
        return ExecutionResult(
            success=False,
            message=f"Invalid iterable: {iterable}",
            errors=[f"Invalid iterable: {iterable}"]
        )
        
    # Limit iterations
    items = items[:max_iterations]
    
    # Execute loop
    results = []
    for index, item in enumerate(items):
        # Add loop variables to context
        context.variables[item_var] = item
        context.variables["loop_index"] = index
        context.variables["loop_count"] = len(items)
        context.variables["loop_first"] = index == 0
        context.variables["loop_last"] = index == len(items) - 1
        
        # Execute steps
        iteration_results = []
        for step in steps:
            result = await execute_step_callback(step, context)
            iteration_results.append({
                "step_id": step.get("id", f"step-{len(iteration_results)}"),
                "success": result.success,
                "data": result.data
            })
            
            # Stop on failure if specified
            if not result.success and parameters.get("stop_on_failure", True):
                break
                
        # Add iteration results
        results.append({
            "index": index,
            "item": item,
            "success": all(result["success"] for result in iteration_results),
            "results": iteration_results
        })
        
        # Stop loop on failure if specified
        if not results[-1]["success"] and parameters.get("break_on_failure", False):
            break
            
    # Clean up loop variables
    for var in [item_var, "loop_index", "loop_count", "loop_first", "loop_last"]:
        if var in context.variables:
            del context.variables[var]
            
    return ExecutionResult(
        success=all(result["success"] for result in results),
        data={
            "iterations": len(results),
            "results": results
        },
        message=f"For loop completed with {len(results)} iterations"
    )


async def handle_while_loop(parameters: Dict[str, Any], 
                         steps: List[Dict[str, Any]], 
                         context: ExecutionContext, 
                         execute_step_callback) -> ExecutionResult:
    """
    Handle a while loop.
    
    Args:
        parameters: Loop parameters
        steps: Steps to execute in each iteration
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with loop results
    """
    # Get condition
    condition = parameters.get("condition")
    if not condition:
        return ExecutionResult(
            success=False,
            message="No condition specified for while loop",
            errors=["No condition specified for while loop"]
        )
        
    # Get max iterations
    max_iterations = parameters.get("max_iterations", 100)
    
    # Execute loop
    results = []
    iteration = 0
    
    while iteration < max_iterations:
        # Evaluate condition
        condition_result = await evaluate_condition(condition, context)
        
        # Stop if condition is false
        if not condition_result:
            break
            
        # Add loop variables to context
        context.variables["loop_iteration"] = iteration
        
        # Execute steps
        iteration_results = []
        for step in steps:
            result = await execute_step_callback(step, context)
            iteration_results.append({
                "step_id": step.get("id", f"step-{len(iteration_results)}"),
                "success": result.success,
                "data": result.data
            })
            
            # Stop on failure if specified
            if not result.success and parameters.get("stop_on_failure", True):
                break
                
        # Add iteration results
        results.append({
            "iteration": iteration,
            "success": all(result["success"] for result in iteration_results),
            "results": iteration_results
        })
        
        # Stop loop on failure if specified
        if not results[-1]["success"] and parameters.get("break_on_failure", False):
            break
            
        # Increment iteration counter
        iteration += 1
        
    # Clean up loop variables
    if "loop_iteration" in context.variables:
        del context.variables["loop_iteration"]
        
    return ExecutionResult(
        success=all(result["success"] for result in results),
        data={
            "iterations": len(results),
            "results": results
        },
        message=f"While loop completed with {len(results)} iterations"
    )


async def handle_foreach_loop(parameters: Dict[str, Any], 
                           steps: List[Dict[str, Any]], 
                           context: ExecutionContext, 
                           execute_step_callback) -> ExecutionResult:
    """
    Handle a foreach loop (iterates over dictionary/map).
    
    Args:
        parameters: Loop parameters
        steps: Steps to execute in each iteration
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with loop results
    """
    # Get map/dict
    dict_name = parameters.get("dict")
    if not dict_name:
        return ExecutionResult(
            success=False,
            message="No dictionary specified for foreach loop",
            errors=["No dictionary specified for foreach loop"]
        )
        
    # Get key and value variable names
    key_var = parameters.get("key_var", "key")
    value_var = parameters.get("value_var", "value")
    
    # Get max iterations
    max_iterations = parameters.get("max_iterations", 100)
    
    # Get the dictionary
    if isinstance(dict_name, str) and "$" in dict_name:
        # Check for variable substitution
        for var_name, var_value in context.variables.items():
            placeholder = f"${var_name}"
            if placeholder == dict_name and isinstance(var_value, dict):
                dictionary = var_value
                break
        else:
            # If no direct match, try as a variable name
            dict_var_name = dict_name.replace("$", "")
            if dict_var_name in context.variables and isinstance(context.variables[dict_var_name], dict):
                dictionary = context.variables[dict_var_name]
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Invalid dictionary variable: {dict_name}",
                    errors=[f"Invalid dictionary variable: {dict_name}"]
                )
    elif isinstance(dict_name, str) and dict_name in context.variables:
        # Get dictionary from context variables
        dictionary = context.variables[dict_name]
        if not isinstance(dictionary, dict):
            return ExecutionResult(
                success=False,
                message=f"Variable {dict_name} is not a dictionary",
                errors=[f"Variable {dict_name} is not a dictionary (type: {type(dictionary).__name__})"]
            )
    elif isinstance(dict_name, dict):
        # Use provided dict directly
        dictionary = dict_name
    else:
        return ExecutionResult(
            success=False,
            message=f"Invalid dictionary: {dict_name}",
            errors=[f"Invalid dictionary: {dict_name}"]
        )
        
    # Get items
    items = list(dictionary.items())[:max_iterations]
    
    # Execute loop
    results = []
    for index, (key, value) in enumerate(items):
        # Add loop variables to context
        context.variables[key_var] = key
        context.variables[value_var] = value
        context.variables["loop_index"] = index
        context.variables["loop_count"] = len(items)
        context.variables["loop_first"] = index == 0
        context.variables["loop_last"] = index == len(items) - 1
        
        # Execute steps
        iteration_results = []
        for step in steps:
            result = await execute_step_callback(step, context)
            iteration_results.append({
                "step_id": step.get("id", f"step-{len(iteration_results)}"),
                "success": result.success,
                "data": result.data
            })
            
            # Stop on failure if specified
            if not result.success and parameters.get("stop_on_failure", True):
                break
                
        # Add iteration results
        results.append({
            "index": index,
            "key": key,
            "value": value,
            "success": all(result["success"] for result in iteration_results),
            "results": iteration_results
        })
        
        # Stop loop on failure if specified
        if not results[-1]["success"] and parameters.get("break_on_failure", False):
            break
            
    # Clean up loop variables
    for var in [key_var, value_var, "loop_index", "loop_count", "loop_first", "loop_last"]:
        if var in context.variables:
            del context.variables[var]
            
    return ExecutionResult(
        success=all(result["success"] for result in results),
        data={
            "iterations": len(results),
            "results": results
        },
        message=f"Foreach loop completed with {len(results)} iterations"
    )


async def handle_count_loop(parameters: Dict[str, Any], 
                         steps: List[Dict[str, Any]], 
                         context: ExecutionContext, 
                         execute_step_callback) -> ExecutionResult:
    """
    Handle a count loop (simple counter).
    
    Args:
        parameters: Loop parameters
        steps: Steps to execute in each iteration
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with loop results
    """
    # Get count parameters
    start = parameters.get("start", 0)
    end = parameters.get("end", 10)
    step = parameters.get("step", 1)
    
    # Get counter variable name
    counter_var = parameters.get("counter_var", "i")
    
    # Process parameters with variable substitution
    for param_name in ["start", "end", "step"]:
        param_value = parameters.get(param_name)
        if isinstance(param_value, str) and "$" in param_value:
            for var_name, var_value in context.variables.items():
                if isinstance(var_value, (int, float)):
                    placeholder = f"${var_name}"
                    if placeholder == param_value:
                        if param_name == "start":
                            start = var_value
                        elif param_name == "end":
                            end = var_value
                        elif param_name == "step":
                            step = var_value
                        break
    
    # Convert to numbers if strings
    for param_name, param_value in [("start", start), ("end", end), ("step", step)]:
        if isinstance(param_value, str):
            try:
                value = float(param_value)
                if value.is_integer():
                    value = int(value)
                
                if param_name == "start":
                    start = value
                elif param_name == "end":
                    end = value
                elif param_name == "step":
                    step = value
            except ValueError:
                return ExecutionResult(
                    success=False,
                    message=f"Invalid {param_name} value: {param_value}",
                    errors=[f"Invalid {param_name} value: {param_value}"]
                )
    
    # Get max iterations
    max_iterations = parameters.get("max_iterations", 100)
    
    # Generate range
    if step > 0:
        counter_range = range(start, end + 1, step)
    else:
        counter_range = range(start, end - 1, step)
        
    # Limit iterations
    if len(counter_range) > max_iterations:
        counter_range = list(counter_range)[:max_iterations]
    
    # Execute loop
    results = []
    total_iterations = len(counter_range)
    
    for index, counter in enumerate(counter_range):
        # Add loop variables to context
        context.variables[counter_var] = counter
        context.variables["loop_index"] = index
        context.variables["loop_count"] = total_iterations
        context.variables["loop_first"] = index == 0
        context.variables["loop_last"] = index == total_iterations - 1
        
        # Execute steps
        iteration_results = []
        for step_data in steps:
            result = await execute_step_callback(step_data, context)
            iteration_results.append({
                "step_id": step_data.get("id", f"step-{len(iteration_results)}"),
                "success": result.success,
                "data": result.data
            })
            
            # Stop on failure if specified
            if not result.success and parameters.get("stop_on_failure", True):
                break
                
        # Add iteration results
        results.append({
            "index": index,
            "counter": counter,
            "success": all(result["success"] for result in iteration_results),
            "results": iteration_results
        })
        
        # Stop loop on failure if specified
        if not results[-1]["success"] and parameters.get("break_on_failure", False):
            break
            
    # Clean up loop variables
    for var in [counter_var, "loop_index", "loop_count", "loop_first", "loop_last"]:
        if var in context.variables:
            del context.variables[var]
            
    return ExecutionResult(
        success=all(result["success"] for result in results),
        data={
            "iterations": len(results),
            "results": results
        },
        message=f"Count loop completed with {len(results)} iterations"
    )


async def handle_parallel_loop(parameters: Dict[str, Any], 
                            steps: List[Dict[str, Any]], 
                            context: ExecutionContext, 
                            execute_step_callback) -> ExecutionResult:
    """
    Handle a parallel loop (concurrent execution).
    
    Args:
        parameters: Loop parameters
        steps: Steps to execute in parallel
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with loop results
    """
    # Get concurrency parameters
    max_concurrency = parameters.get("max_concurrency", 5)
    
    # Get iterable
    iterable = parameters.get("iterable")
    if not iterable:
        # If no iterable, just run steps in parallel
        return await _handle_parallel_steps(steps, context, execute_step_callback, max_concurrency)
        
    # Get item variable name
    item_var = parameters.get("item_var", "item")
    
    # Process the iterable
    if isinstance(iterable, str) and "$" in iterable:
        # Check for variable substitution
        for var_name, var_value in context.variables.items():
            placeholder = f"${var_name}"
            if placeholder == iterable and isinstance(var_value, (list, tuple)):
                items = var_value
                break
        else:
            # If no direct match, try as a variable name
            items_name = iterable.replace("$", "")
            if items_name in context.variables and isinstance(context.variables[items_name], (list, tuple)):
                items = context.variables[items_name]
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Invalid iterable variable: {iterable}",
                    errors=[f"Invalid iterable variable: {iterable}"]
                )
    elif isinstance(iterable, str) and iterable in context.variables:
        # Get iterable from context variables
        items = context.variables[iterable]
        if not isinstance(items, (list, tuple)):
            return ExecutionResult(
                success=False,
                message=f"Variable {iterable} is not iterable",
                errors=[f"Variable {iterable} is not iterable (type: {type(items).__name__})"]
            )
    elif isinstance(iterable, (list, tuple)):
        # Use provided list directly
        items = iterable
    else:
        return ExecutionResult(
            success=False,
            message=f"Invalid iterable: {iterable}",
            errors=[f"Invalid iterable: {iterable}"]
        )
    
    # Get max iterations
    max_iterations = parameters.get("max_iterations", 100)
    
    # Limit iterations
    if len(items) > max_iterations:
        items = items[:max_iterations]
    
    # Create tasks for each item
    tasks = []
    results = {}
    
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def process_item(index, item):
        async with semaphore:
            # Create a copy of the context for this task
            task_context = ExecutionContext(
                context_id=f"{context.context_id}:parallel:{index}",
                plan_id=context.plan_id,
                variables=context.variables.copy()
            )
            
            # Add loop variables to context
            task_context.variables[item_var] = item
            task_context.variables["loop_index"] = index
            task_context.variables["loop_count"] = len(items)
            task_context.variables["loop_first"] = index == 0
            task_context.variables["loop_last"] = index == len(items) - 1
            
            # Execute steps
            iteration_results = []
            for step in steps:
                result = await execute_step_callback(step, task_context)
                iteration_results.append({
                    "step_id": step.get("id", f"step-{len(iteration_results)}"),
                    "success": result.success,
                    "data": result.data
                })
                
                # Stop on failure if specified
                if not result.success and parameters.get("stop_on_failure", True):
                    break
            
            # Return results
            return {
                "index": index,
                "item": item,
                "success": all(result["success"] for result in iteration_results),
                "results": iteration_results
            }
    
    # Create tasks for each item
    for index, item in enumerate(items):
        task = asyncio.create_task(process_item(index, item))
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Sort results by index
    results = sorted(results, key=lambda x: x["index"])
    
    return ExecutionResult(
        success=all(result["success"] for result in results),
        data={
            "iterations": len(results),
            "results": results
        },
        message=f"Parallel loop completed with {len(results)} iterations"
    )


async def _handle_parallel_steps(steps: List[Dict[str, Any]],
                              context: ExecutionContext,
                              execute_step_callback,
                              max_concurrency: int = 5) -> ExecutionResult:
    """
    Handle parallel execution of steps.
    
    Args:
        steps: Steps to execute in parallel
        context: Execution context
        execute_step_callback: Callback to execute a step
        max_concurrency: Maximum number of concurrent tasks
        
    Returns:
        ExecutionResult with parallel execution results
    """
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def execute_step(step, index):
        async with semaphore:
            # Create a copy of the context for this task
            task_context = ExecutionContext(
                context_id=f"{context.context_id}:parallel_step:{index}",
                plan_id=context.plan_id,
                variables=context.variables.copy()
            )
            
            # Execute step
            result = await execute_step_callback(step, task_context)
            
            # Return result with step info
            return {
                "step_id": step.get("id", f"step-{index}"),
                "index": index,
                "success": result.success,
                "data": result.data,
                "message": result.message,
                "errors": result.errors
            }
    
    # Create tasks for each step
    tasks = []
    for index, step in enumerate(steps):
        task = asyncio.create_task(execute_step(step, index))
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Sort results by index
    results = sorted(results, key=lambda x: x["index"])
    
    return ExecutionResult(
        success=all(result["success"] for result in results),
        data={
            "steps": len(results),
            "results": results
        },
        message=f"Parallel step execution completed with {len(results)} steps"
    )