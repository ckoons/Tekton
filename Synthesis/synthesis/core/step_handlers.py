#!/usr/bin/env python3
"""
Synthesis Step Handlers

This module handles execution of different step types for Synthesis.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Dict, List, Any, Optional, Callable

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from synthesis.core.execution_models import ExecutionContext, ExecutionResult
from synthesis.core.condition_evaluator import evaluate_condition
from synthesis.core.loop_handlers import handle_loop_step

# Configure logging
logger = logging.getLogger("synthesis.core.step_handlers")


async def handle_command_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle a command execution step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with command output
    """
    import subprocess
    
    # Get command and arguments
    command = parameters.get("command")
    if not command:
        return ExecutionResult(
            success=False,
            message="No command specified",
            errors=["No command specified"]
        )
        
    # Get shell flag
    shell = parameters.get("shell", True)
    
    # Get working directory
    cwd = parameters.get("cwd")
    
    # Get environment variables
    env_vars = parameters.get("env")
    
    # Process environment variables with variable substitution
    if env_vars:
        processed_env = os.environ.copy()
        for key, value in env_vars.items():
            # Handle variable substitution from context
            if isinstance(value, str) and "$" in value:
                for var_name, var_value in context.variables.items():
                    if isinstance(var_value, (str, int, float, bool)):
                        placeholder = f"${var_name}"
                        value = value.replace(placeholder, str(var_value))
            processed_env[key] = value
    else:
        processed_env = None
    
    # Get timeout
    timeout = parameters.get("timeout", 60)
    
    try:
        # Execute command
        logger.info(f"Executing command: {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=shell,
            cwd=cwd,
            env=processed_env
        )
        
        # Wait for command to complete with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # Decode output
            stdout_str = stdout.decode("utf-8").strip() if stdout else ""
            stderr_str = stderr.decode("utf-8").strip() if stderr else ""
            
            # Check return code
            if process.returncode == 0:
                return ExecutionResult(
                    success=True,
                    data={
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                        "return_code": process.returncode
                    },
                    message=f"Command executed successfully"
                )
            else:
                return ExecutionResult(
                    success=False,
                    data={
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                        "return_code": process.returncode
                    },
                    message=f"Command failed with return code {process.returncode}",
                    errors=[f"Command failed with return code {process.returncode}", stderr_str]
                )
                
        except asyncio.TimeoutError:
            # Kill the process on timeout
            process.kill()
            return ExecutionResult(
                success=False,
                message=f"Command timed out after {timeout}s",
                errors=[f"Command timed out after {timeout}s"]
            )
            
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error executing command: {e}",
            errors=[str(e)]
        )
        

async def handle_function_step(parameters: Dict[str, Any], 
                           context: ExecutionContext, 
                           function_registry: Optional[Dict[str, Callable]] = None) -> ExecutionResult:
    """
    Handle a function execution step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        function_registry: Optional function registry
        
    Returns:
        ExecutionResult with function output
    """
    # Get function reference
    function_name = parameters.get("function")
    if not function_name:
        return ExecutionResult(
            success=False,
            message="No function specified",
            errors=["No function specified"]
        )
        
    # Get function arguments
    args = parameters.get("args", [])
    kwargs = parameters.get("kwargs", {})
    
    # Perform variable substitution in args and kwargs
    processed_args = []
    for arg in args:
        if isinstance(arg, str) and "$" in arg:
            for var_name, var_value in context.variables.items():
                if isinstance(var_value, (str, int, float, bool)):
                    placeholder = f"${var_name}"
                    arg = arg.replace(placeholder, str(var_value))
        processed_args.append(arg)
    
    processed_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, str) and "$" in v:
            for var_name, var_value in context.variables.items():
                if isinstance(var_value, (str, int, float, bool)):
                    placeholder = f"${var_name}"
                    v = v.replace(placeholder, str(var_value))
        processed_kwargs[k] = v
    
    # Add context to kwargs if required
    if parameters.get("include_context", False):
        processed_kwargs["context"] = context
        
    try:
        # Get function reference
        if function_registry:
            function = function_registry.get(function_name)
            if not function:
                return ExecutionResult(
                    success=False,
                    message=f"Function {function_name} not found",
                    errors=[f"Function {function_name} not found"]
                )
        else:
            return ExecutionResult(
                success=False,
                message="Function registry not available",
                errors=["Function registry not available"]
            )
            
        # Execute function
        logger.info(f"Executing function: {function_name}")
        result = function(*processed_args, **processed_kwargs)
        
        # Handle async functions
        if asyncio.iscoroutine(result):
            result = await result
            
        return ExecutionResult(
            success=True,
            data={"result": result},
            message=f"Function executed successfully"
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error executing function: {e}",
            errors=[str(e)]
        )
        

async def handle_api_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle an API request step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with API response
    """
    try:
        import aiohttp
        
        # Get request parameters
        url = parameters.get("url")
        if not url:
            return ExecutionResult(
                success=False,
                message="No URL specified",
                errors=["No URL specified"]
            )
            
        # Process URL with variable substitution
        if "$" in url:
            for var_name, var_value in context.variables.items():
                if isinstance(var_value, (str, int, float, bool)):
                    placeholder = f"${var_name}"
                    url = url.replace(placeholder, str(var_value))
            
        method = parameters.get("method", "GET").upper()
        headers = parameters.get("headers", {})
        params = parameters.get("params", {})
        data = parameters.get("data")
        json_data = parameters.get("json")
        timeout = parameters.get("timeout", 30)
        
        # Process headers, params, data with variable substitution
        for key, value in list(headers.items()):
            if isinstance(value, str) and "$" in value:
                for var_name, var_value in context.variables.items():
                    if isinstance(var_value, (str, int, float, bool)):
                        placeholder = f"${var_name}"
                        headers[key] = value.replace(placeholder, str(var_value))
        
        for key, value in list(params.items()):
            if isinstance(value, str) and "$" in value:
                for var_name, var_value in context.variables.items():
                    if isinstance(var_value, (str, int, float, bool)):
                        placeholder = f"${var_name}"
                        params[key] = value.replace(placeholder, str(var_value))
        
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, str) and "$" in value:
                    for var_name, var_value in context.variables.items():
                        if isinstance(var_value, (str, int, float, bool)):
                            placeholder = f"${var_name}"
                            data[key] = value.replace(placeholder, str(var_value))
        
        if isinstance(json_data, dict):
            for key, value in list(json_data.items()):
                if isinstance(value, str) and "$" in value:
                    for var_name, var_value in context.variables.items():
                        if isinstance(var_value, (str, int, float, bool)):
                            placeholder = f"${var_name}"
                            json_data[key] = value.replace(placeholder, str(var_value))
        
        # Execute request
        logger.info(f"Executing API request: {method} {url}")
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                # Read response
                status = response.status
                response_text = await response.text()
                
                # Try to parse as JSON
                try:
                    import json
                    response_data = json.loads(response_text)
                except:
                    response_data = response_text
                    
                # Check if request was successful
                success = 200 <= status < 400
                
                return ExecutionResult(
                    success=success,
                    data={
                        "status": status,
                        "headers": dict(response.headers),
                        "data": response_data
                    },
                    message=f"API request {'succeeded' if success else 'failed'} with status {status}",
                    errors=[f"API request failed with status {status}"] if not success else None
                )
                
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error executing API request: {e}",
            errors=[str(e)]
        )
        

async def handle_condition_step(parameters: Dict[str, Any], 
                             context: ExecutionContext, 
                             execute_step_callback) -> ExecutionResult:
    """
    Handle a conditional execution step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        execute_step_callback: Callback to execute a step
        
    Returns:
        ExecutionResult with condition result
    """
    # Get condition
    condition = parameters.get("condition")
    if not condition:
        return ExecutionResult(
            success=False,
            message="No condition specified",
            errors=["No condition specified"]
        )
        
    # Get then/else steps
    then_steps = parameters.get("then", [])
    else_steps = parameters.get("else", [])
    
    try:
        # Evaluate condition
        condition_result = await evaluate_condition(condition, context)
        
        # Execute then or else steps
        if condition_result:
            logger.info(f"Condition {condition} evaluated to True, executing 'then' steps")
            steps_to_execute = then_steps
        else:
            logger.info(f"Condition {condition} evaluated to False, executing 'else' steps")
            steps_to_execute = else_steps
            
        # Execute steps
        results = []
        for step in steps_to_execute:
            result = await execute_step_callback(step, context)
            results.append({
                "step_id": step.get("id", f"step-{len(results)}"),
                "success": result.success,
                "data": result.data
            })
            
            # Stop on failure if specified
            if not result.success and parameters.get("stop_on_failure", True):
                break
                
        return ExecutionResult(
            success=all(result["success"] for result in results),
            data={
                "condition_result": condition_result,
                "results": results
            },
            message=f"Conditional execution completed"
        )
        
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error executing conditional step: {e}",
            errors=[str(e)]
        )


async def handle_subprocess_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle a subprocess execution step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with subprocess results
    """
    # Get subprocess steps
    steps = parameters.get("steps", [])
    if not steps:
        return ExecutionResult(
            success=False,
            message="No steps specified for subprocess",
            errors=["No steps specified for subprocess"]
        )
    
    # Create subprocess context (copy of parent context)
    subprocess_context = ExecutionContext(
        plan_id=context.plan_id,
        variables=context.variables.copy()
    )
    
    # Add subprocess-specific variables
    subprocess_context.variables["parent_context_id"] = context.context_id
    
    # Process input parameters
    inputs = parameters.get("inputs", {})
    for input_name, input_source in inputs.items():
        if input_source in context.variables:
            subprocess_context.variables[input_name] = context.variables[input_source]
    
    try:
        # Create and initialize a new execution engine
        from synthesis.core.execution_engine import ExecutionEngine
        engine = ExecutionEngine()
        
        # Define execution plan for subprocess
        from synthesis.core.execution_models import ExecutionPlan
        subprocess_plan = ExecutionPlan(
            name=parameters.get("name", "Subprocess"),
            description=parameters.get("description", "Subprocess execution"),
            steps=steps,
            metadata={"parent_context_id": context.context_id}
        )
        
        # Execute subprocess plan
        execution_id = await engine.execute_plan(subprocess_plan, subprocess_context)
        
        # Wait for completion if specified
        if parameters.get("wait_for_completion", True):
            while True:
                status = await engine.get_execution_status(execution_id)
                if status["status"] in (
                    "completed", "failed", "cancelled", "not_found"
                ):
                    break
                await asyncio.sleep(0.5)
                
            # Get final status
            status = await engine.get_execution_status(execution_id)
            success = status["status"] == "completed"
            
            # Get results
            if "execution_history" in engine.__dict__ and execution_id in engine.execution_history:
                subprocess_results = engine.execution_history[execution_id].get("results", [])
                result_data = {
                    "execution_id": execution_id,
                    "status": status["status"],
                    "results": subprocess_results
                }
                
                # Process outputs
                if success and parameters.get("outputs"):
                    for output_name, output_target in parameters.get("outputs", {}).items():
                        if output_name in subprocess_context.variables:
                            context.variables[output_target] = subprocess_context.variables[output_name]
                
                return ExecutionResult(
                    success=success,
                    data=result_data,
                    message=f"Subprocess execution {'completed successfully' if success else 'failed'}"
                )
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Failed to retrieve subprocess results",
                    errors=[f"Subprocess execution history not found for {execution_id}"]
                )
        else:
            # Return immediately with execution ID
            return ExecutionResult(
                success=True,
                data={"execution_id": execution_id},
                message=f"Subprocess execution started with ID {execution_id}"
            )
    
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error executing subprocess: {e}",
            errors=[str(e)]
        )


async def handle_notify_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle a notification step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with notification status
    """
    # Get notification parameters
    channel = parameters.get("channel")
    if not channel:
        return ExecutionResult(
            success=False,
            message="No notification channel specified",
            errors=["No notification channel specified"]
        )
    
    message = parameters.get("message", "")
    if "$" in message:
        # Process variable substitution
        for var_name, var_value in context.variables.items():
            if isinstance(var_value, (str, int, float, bool)):
                placeholder = f"${var_name}"
                message = message.replace(placeholder, str(var_value))
    
    # Get notification data
    data = parameters.get("data", {})
    
    try:
        # For WebSocket notifications
        if channel == "websocket":
            try:
                # Import event system
                from synthesis.core.events import EventManager
                event_manager = EventManager.get_instance()
                
                # Create event data
                event_data = {
                    "type": "notification",
                    "message": message,
                    "context_id": context.context_id,
                    "timestamp": context.variables.get("current_timestamp", None),
                    **data
                }
                
                # Send event
                await event_manager.emit("notification", event_data)
                
                return ExecutionResult(
                    success=True,
                    data={"channel": channel, "message": message},
                    message=f"Notification sent to WebSocket clients"
                )
            except ImportError:
                logger.warning("Event system not available, WebSocket notification failed")
                return ExecutionResult(
                    success=False,
                    message="Event system not available",
                    errors=["Event system not available for WebSocket notifications"]
                )
        
        # For HTTP notifications (webhook)
        elif channel == "webhook":
            webhook_url = parameters.get("webhook_url")
            if not webhook_url:
                return ExecutionResult(
                    success=False,
                    message="No webhook URL specified",
                    errors=["No webhook URL specified for webhook notification"]
                )
            
            # Prepare notification payload
            payload = {
                "message": message,
                "context_id": context.context_id,
                "timestamp": context.variables.get("current_timestamp", None),
                **data
            }
            
            # Send HTTP request
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=payload) as response:
                        status = response.status
                        success = 200 <= status < 300
                        
                        return ExecutionResult(
                            success=success,
                            data={"channel": channel, "status": status, "url": webhook_url},
                            message=f"Webhook notification {'sent successfully' if success else 'failed'}"
                        )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    message=f"Webhook notification failed: {e}",
                    errors=[str(e)]
                )
        
        # For log notifications
        elif channel == "log":
            log_level = parameters.get("log_level", "info").lower()
            
            # Determine logging level
            level_map = {
                "debug": logging.DEBUG,
                "info": logging.INFO,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL
            }
            level = level_map.get(log_level, logging.INFO)
            
            # Log the message
            logger.log(level, f"Notification: {message}")
            
            return ExecutionResult(
                success=True,
                data={"channel": channel, "level": log_level, "message": message},
                message=f"Log notification sent at level {log_level}"
            )
        
        # Unsupported notification channel
        else:
            return ExecutionResult(
                success=False,
                message=f"Unsupported notification channel: {channel}",
                errors=[f"Unsupported notification channel: {channel}"]
            )
    
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error sending notification: {e}",
            errors=[str(e)]
        )


async def handle_wait_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle a wait step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with wait status
    """
    # Get wait duration
    duration = parameters.get("duration", 1)
    
    # Check for variable substitution
    if isinstance(duration, str) and "$" in duration:
        for var_name, var_value in context.variables.items():
            if isinstance(var_value, (int, float)):
                placeholder = f"${var_name}"
                if placeholder == duration:
                    duration = var_value
                    break
    
    # Convert to float if string
    if isinstance(duration, str):
        try:
            duration = float(duration)
        except ValueError:
            return ExecutionResult(
                success=False,
                message=f"Invalid wait duration: {duration}",
                errors=[f"Invalid wait duration: {duration}"]
            )
    
    # Ensure positive duration
    duration = max(0, float(duration))
    
    logger.info(f"Waiting for {duration} seconds")
    await asyncio.sleep(duration)
    
    return ExecutionResult(
        success=True,
        message=f"Waited for {duration} seconds",
        data={"duration": duration}
    )


async def handle_variable_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle variable manipulation step.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with variable operation status
    """
    # Get operation type
    operation = parameters.get("operation", "set")
    
    # Get variable name
    name = parameters.get("name")
    if not name:
        return ExecutionResult(
            success=False,
            message="No variable name specified",
            errors=["No variable name specified"]
        )
        
    try:
        if operation == "set":
            # Set variable
            value = parameters.get("value")
            
            # Handle variable substitution if string
            if isinstance(value, str) and "$" in value:
                for var_name, var_value in context.variables.items():
                    if isinstance(var_value, (str, int, float, bool)):
                        placeholder = f"${var_name}"
                        value = value.replace(placeholder, str(var_value))
            
            context.variables[name] = value
            return ExecutionResult(
                success=True,
                message=f"Variable {name} set",
                data={"name": name, "value": value}
            )
            
        elif operation == "delete":
            # Delete variable
            if name in context.variables:
                del context.variables[name]
            return ExecutionResult(
                success=True,
                message=f"Variable {name} deleted",
                data={"name": name}
            )
            
        elif operation == "increment":
            # Increment variable
            increment = parameters.get("value", 1)
            
            # Handle variable substitution if string
            if isinstance(increment, str) and "$" in increment:
                for var_name, var_value in context.variables.items():
                    if isinstance(var_value, (int, float)):
                        placeholder = f"${var_name}"
                        if placeholder == increment:
                            increment = var_value
                            break
            
            # Convert to number if string
            if isinstance(increment, str):
                try:
                    increment = float(increment)
                    if increment.is_integer():
                        increment = int(increment)
                except ValueError:
                    return ExecutionResult(
                        success=False,
                        message=f"Invalid increment value: {increment}",
                        errors=[f"Invalid increment value: {increment}"]
                    )
            
            # Perform increment
            if name in context.variables:
                if not isinstance(context.variables[name], (int, float)):
                    try:
                        context.variables[name] = float(context.variables[name])
                        if context.variables[name].is_integer():
                            context.variables[name] = int(context.variables[name])
                    except (ValueError, TypeError):
                        return ExecutionResult(
                            success=False,
                            message=f"Cannot increment non-numeric variable {name}",
                            errors=[f"Cannot increment non-numeric variable {name}"]
                        )
                context.variables[name] += increment
            else:
                context.variables[name] = increment
                
            return ExecutionResult(
                success=True,
                message=f"Variable {name} incremented",
                data={"name": name, "value": context.variables[name]}
            )
            
        elif operation == "append":
            # Append to list variable
            value = parameters.get("value")
            
            # Handle variable substitution if string
            if isinstance(value, str) and "$" in value:
                for var_name, var_value in context.variables.items():
                    if isinstance(var_value, (str, int, float, bool)):
                        placeholder = f"${var_name}"
                        value = value.replace(placeholder, str(var_value))
            
            # Check if variable exists
            if name not in context.variables:
                context.variables[name] = []
            
            # Check if variable is a list
            if not isinstance(context.variables[name], list):
                context.variables[name] = [context.variables[name]]
            
            # Append value
            context.variables[name].append(value)
            
            return ExecutionResult(
                success=True,
                message=f"Value appended to variable {name}",
                data={"name": name, "value": value, "list": context.variables[name]}
            )
            
        elif operation == "merge":
            # Merge dictionaries
            value = parameters.get("value", {})
            
            # Handle variable substitution if string values in dict
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, str) and "$" in v:
                        for var_name, var_value in context.variables.items():
                            if isinstance(var_value, (str, int, float, bool)):
                                placeholder = f"${var_name}"
                                value[k] = v.replace(placeholder, str(var_value))
            
            # Check if variable exists
            if name not in context.variables:
                context.variables[name] = {}
            
            # Check if variable is a dict
            if not isinstance(context.variables[name], dict):
                return ExecutionResult(
                    success=False,
                    message=f"Cannot merge with non-dictionary variable {name}",
                    errors=[f"Cannot merge with non-dictionary variable {name}"]
                )
            
            # Merge dictionaries
            context.variables[name].update(value)
            
            return ExecutionResult(
                success=True,
                message=f"Values merged into variable {name}",
                data={"name": name, "merged": value, "result": context.variables[name]}
            )
            
        else:
            return ExecutionResult(
                success=False,
                message=f"Unsupported variable operation: {operation}",
                errors=[f"Unsupported variable operation: {operation}"]
            )
            
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error manipulating variable: {e}",
            errors=[str(e)]
        )


async def handle_llm_step(parameters: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
    """
    Handle an LLM processing step using tekton-llm-client.
    
    Args:
        parameters: Step parameters
        context: Execution context
        
    Returns:
        ExecutionResult with LLM response
    """
    try:
        # Get required parameters
        prompt = parameters.get("prompt")
        if not prompt:
            return ExecutionResult(
                success=False,
                message="Missing required parameter: prompt",
                errors=["Missing required parameter: prompt"]
            )
        
        # Get optional parameters
        system_prompt = parameters.get("system_prompt", "You are a helpful assistant.")
        model = parameters.get("model")
        temperature = parameters.get("temperature", 0.7)
        max_tokens = parameters.get("max_tokens", 1000)
        store_variable = parameters.get("store_variable")
        streaming = parameters.get("streaming", False)
        
        # Handle variable substitution in prompts
        if isinstance(prompt, str) and "$" in prompt:
            for var_name, var_value in context.variables.items():
                if isinstance(var_value, (str, int, float, bool)):
                    placeholder = f"${var_name}"
                    prompt = prompt.replace(placeholder, str(var_value))
        
        if isinstance(system_prompt, str) and "$" in system_prompt:
            for var_name, var_value in context.variables.items():
                if isinstance(var_value, (str, int, float, bool)):
                    placeholder = f"${var_name}"
                    system_prompt = system_prompt.replace(placeholder, str(var_value))
        
        # Get the LLM adapter
        llm_adapter = await get_llm_adapter()
        
        # Check if we need to use chat interface
        mode = parameters.get("mode", "chat")
        
        if mode == "enhance_plan":
            # Generate enhanced execution plan
            plan_data = parameters.get("plan", {})
            result = await llm_adapter.enhance_execution_plan(plan_data)
            
            # Store result in variable if specified
            if store_variable:
                context.variables[store_variable] = result
            
            return ExecutionResult(
                success=True,
                message="Successfully enhanced execution plan",
                data={"plan": result}
            )
            
        elif mode == "analyze_result":
            # Analyze execution result
            execution_id = parameters.get("execution_id", "unknown")
            result_data = parameters.get("result", {})
            plan_data = parameters.get("plan", {})
            
            analysis = await llm_adapter.analyze_execution_result(
                execution_id=execution_id,
                result=result_data,
                plan=plan_data
            )
            
            # Store result in variable if specified
            if store_variable:
                context.variables[store_variable] = analysis
            
            return ExecutionResult(
                success=True,
                message="Successfully analyzed execution result",
                data={"analysis": analysis}
            )
            
        elif mode == "generate_command":
            # Generate dynamic command
            instruction = parameters.get("instruction", prompt)
            
            command = await llm_adapter.generate_dynamic_command(
                context=context.variables,
                instruction=instruction
            )
            
            # Store result in variable if specified
            if store_variable:
                context.variables[store_variable] = command
            
            return ExecutionResult(
                success=True,
                message="Successfully generated command",
                data={"command": command}
            )
            
        else:  # Default chat mode
            # Initialize LLM client
            if not await llm_adapter.ensure_initialized():
                return ExecutionResult(
                    success=False,
                    message="Failed to initialize LLM client",
                    errors=["Failed to initialize LLM client"]
                )
            
            # Create messages for chat
            from tekton_llm_client.models import ChatMessage, ChatRole, ChatCompletionOptions
            
            messages = [
                ChatMessage(
                    role=ChatRole.SYSTEM,
                    content=system_prompt
                ),
                ChatMessage(
                    role=ChatRole.USER,
                    content=prompt
                )
            ]
            
            # Add additional context if provided
            context_data = parameters.get("context_data")
            if context_data:
                if isinstance(context_data, str) and context_data.startswith("$"):
                    var_name = context_data[1:]
                    if var_name in context.variables:
                        context_data = context.variables[var_name]
                
                if context_data:
                    # Insert context before user message
                    messages.insert(1, ChatMessage(
                        role=ChatRole.USER,
                        content=f"Context information:\n{json.dumps(context_data, indent=2)}"
                    ))
            
            # Set options
            options = ChatCompletionOptions(
                temperature=temperature,
                max_tokens=max_tokens,
                stream=streaming
            )
            
            try:
                # Handle streaming if needed
                if streaming:
                    # For streaming, we'll collect chunks and return the full response
                    full_response = ""
                    event_emitter = context.get_event_emitter()
                    
                    if event_emitter:
                        # If we have an event emitter, send events for each chunk
                        async for chunk in llm_adapter.client.stream_chat_completion(messages=messages, options=options):
                            content = chunk.choices[0].delta.content
                            if content:
                                full_response += content
                                # Emit event with chunk
                                await event_emitter.emit("llm_response_chunk", {
                                    "content": content,
                                    "done": False
                                })
                        
                        # Emit final event
                        await event_emitter.emit("llm_response_chunk", {
                            "content": "",
                            "done": True,
                            "full_response": full_response
                        })
                    else:
                        # No event emitter, just collect chunks
                        async for chunk in llm_adapter.client.stream_chat_completion(messages=messages, options=options):
                            content = chunk.choices[0].delta.content
                            if content:
                                full_response += content
                    
                    # Store result in variable if specified
                    if store_variable:
                        context.variables[store_variable] = full_response
                    
                    return ExecutionResult(
                        success=True,
                        message="Successfully streamed LLM response",
                        data={"response": full_response}
                    )
                    
                else:
                    # Non-streaming response
                    response = await llm_adapter.client.chat_completion(messages=messages, options=options)
                    content = response.choices[0].message.content
                    
                    # Store result in variable if specified
                    if store_variable:
                        context.variables[store_variable] = content
                    
                    return ExecutionResult(
                        success=True,
                        message="Successfully received LLM response",
                        data={
                            "response": content,
                            "model": response.model,
                            "usage": response.usage._asdict() if response.usage else None
                        }
                    )
                    
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    message=f"Error in LLM request: {e}",
                    errors=[str(e)]
                )
                
    except Exception as e:
        return ExecutionResult(
            success=False,
            message=f"Error handling LLM step: {e}",
            errors=[str(e)]
        )