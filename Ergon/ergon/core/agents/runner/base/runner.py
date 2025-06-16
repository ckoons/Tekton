"""
Base agent runner implementation.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple, AsyncGenerator

from ergon.core.database.engine import get_db_session
from ergon.core.database.models import Agent, AgentExecution, AgentMessage, AgentTool
from ergon.core.llm.client import LLMClient
from ergon.utils.config.settings import settings

from ..utils.environment import setup_agent_environment, cleanup_agent_environment
from ..utils.logging import log_agent_start, log_agent_success, log_agent_error
from ..memory.operations import add_memory_context_to_messages, store_conversation
from ..memory.service import close_memory_service
from ..execution.timeout import run_with_timeout
from ..execution.streaming import stream_response
from ..execution.db import (
    record_execution_error, record_execution_success, 
    record_assistant_message, record_tool_call, record_tool_result
)
from ..tools.loader import load_agent_tools
from ..tools.mock import mock_tool_calling
from ..tools.registry import register_special_tools
from ..handlers.browser import handle_browser_direct_workflow
from ..handlers.github import handle_github_agent
from ..handlers.mail import setup_mail_agent
from .exceptions import AgentException, AgentTimeoutException

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))

class AgentRunner:
    """
    Runner for executing AI agents.
    
    This class is responsible for running existing AI agents and
    handling their interactions.
    """
    
    def __init__(
        self,
        agent: Agent,
        execution_id: Optional[int] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        timeout: Optional[int] = None,
        timeout_action: str = "log"
    ):
        """
        Initialize the agent runner.
        
        Args:
            agent: Agent to run
            execution_id: Optional execution ID for tracking
            model_name: Optional model name override
            temperature: Temperature for LLM
            timeout: Optional timeout in seconds for agent execution
            timeout_action: Action to take on timeout ('log', 'alarm', or 'kill')
        """
        self.agent = agent
        self.execution_id = execution_id
        self.model_name = model_name or agent.model_name
        self.temperature = temperature
        self.timeout = timeout
        self.timeout_action = timeout_action.lower() if timeout_action else "log"
        
        # Validate timeout action
        if self.timeout_action not in ["log", "alarm", "kill"]:
            logger.warning(f"Invalid timeout action '{timeout_action}'. Using 'log' instead.")
            self.timeout_action = "log"
        
        # Initialize LLM client
        self.llm_client = LLMClient(model_name=self.model_name, temperature=self.temperature)
        
        # Create working directory if it doesn't exist
        self.working_dir = setup_agent_environment(self.agent)
        
        # Check if agent is a special type
        self.agent_type = getattr(self.agent, 'type', None)
        
        # Check if mail agent
        self.is_mail_agent = setup_mail_agent(self.agent.name)
    
    async def run(self, input_text: str) -> str:
        """
        Run the agent with the given input.
        
        Args:
            input_text: Input to send to the agent
        
        Returns:
            Agent's response
        """
        start_time = datetime.now()
        
        # Log agent execution with name for better traceability
        log_agent_start(self.agent.name, self.agent.id, self.timeout)
        
        try:
            if self.timeout:
                # Run with timeout
                try:
                    return await run_with_timeout(
                        agent_func=self.arun,
                        input_text=input_text,
                        agent_name=self.agent.name,
                        agent_id=self.agent.id,
                        timeout=self.timeout,
                        timeout_action=self.timeout_action,
                        execution_id=self.execution_id,
                        on_timeout=record_execution_error
                    )
                except asyncio.TimeoutError:
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    error_msg = f"Agent '{self.agent.name}' execution timed out after {elapsed_time:.2f} seconds (timeout: {self.timeout}s)"
                    
                    # Log the timeout with agent name
                    logger.warning(error_msg)
                    
                    # Record the timeout in the database if execution_id is provided
                    record_execution_error(self.execution_id, error_msg)
                    
                    # Return appropriate message based on timeout action
                    if self.timeout_action == "alarm":
                        return f"⚠️ TIMEOUT ALARM: {error_msg}"
                    elif self.timeout_action == "kill":
                        return f"❌ EXECUTION TERMINATED: {error_msg}"
                    else:  # "log"
                        return f"I wasn't able to complete the task in the allowed time. {error_msg}"
            else:
                # Run without timeout - use direct await as we're likely already in an async context
                response = await self.arun(input_text)
                
                # Log successful completion with timing
                elapsed_time = (datetime.now() - start_time).total_seconds()
                log_agent_success(self.agent.name, self.agent.id, elapsed_time)
                
                return response
        except Exception as e:
            # Handle other exceptions with agent name
            elapsed_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error in agent '{self.agent.name}' after {elapsed_time:.2f} seconds: {str(e)}"
            
            # Log the error
            log_agent_error(self.agent.name, self.agent.id, str(e), elapsed_time)
            
            # Record the error
            record_execution_error(self.execution_id, error_msg)
            
            return f"I encountered an error while processing your request: {str(e)}"
        finally:
            # Close memory service if needed
            await close_memory_service(self.agent.id)
    
    async def arun(self, input_text: str) -> str:
        """
        Run the agent with the given input asynchronously.
        
        Args:
            input_text: Input to send to the agent
        
        Returns:
            Agent's response
        """
        # Check for greeting or memory-related queries for Nexus agents - use simple completion
        if ((self.agent_type == "nexus" or "nexus" in self.agent.name.lower()) and 
            (any(greeting in input_text.lower() for greeting in ["hello", "hi", "hey", "greetings", "who are you"]) or
             any(memory_term in input_text.lower() for memory_term in ["remember", "memory", "recall", "forgot", "know about me", "know about us"]))):
            logger.info("Nexus agent greeting or memory query detected, using simple completion")
            return await self._run_simple(input_text)
            
        # Check if agent has tools
        with get_db_session() as db:
            tools = db.query(AgentTool).filter(AgentTool.agent_id == self.agent.id).all()
        
        if tools:
            # Agent has tools, use function calling
            return await self._run_with_tools(input_text, tools)
        else:
            # Simple agent, just use completion
            return await self._run_simple(input_text)
    
    async def _run_simple(self, input_text: str) -> str:
        """Run a simple agent without tools."""
        # Prepare messages
        messages = [
            {"role": "system", "content": self.agent.system_prompt},
            {"role": "user", "content": input_text}
        ]
        
        # Add memory context if agent supports it
        messages = await add_memory_context_to_messages(
            agent_id=self.agent.id,
            messages=messages,
            input_text=input_text,
            agent_type=self.agent_type
        )
        
        # Get response from LLM
        response = await self.llm_client.acomplete(messages)
        
        # Store in memory if agent supports it
        await store_conversation(
            agent_id=self.agent.id,
            user_input=input_text,
            assistant_output=response,
            agent_type=self.agent_type
        )
        
        # Record in database if execution_id provided
        record_assistant_message(self.execution_id, response)
        
        # Mark execution as successful
        record_execution_success(self.execution_id)
        
        return response
    
    async def _run_with_tools(self, input_text: str, tools: List[AgentTool]) -> str:
        """Run an agent with tools."""
        # Load tool functions
        tool_funcs = load_agent_tools(self.agent.id, self.working_dir)
        
        # Register special tools
        tool_funcs = await register_special_tools(
            agent_type=self.agent_type,
            agent_id=self.agent.id,
            agent_name=self.agent.name,
            tools_dict=tool_funcs
        )
        
        # Handle GitHub agent (or other agents with non-LLM implementation)
        if "github" in self.agent.name.lower():
            github_response = handle_github_agent(input_text, tool_funcs)
            if github_response:
                return github_response
        
        # Handle browser agent direct workflow
        if self.agent_type == "browser":
            browser_response = await handle_browser_direct_workflow(input_text, tool_funcs)
            if browser_response:
                return browser_response
        
        # Standard LLM-based agent path
        # Prepare tool definitions for the LLM
        tool_definitions = []
        for tool in tools:
            try:
                tool_def = json.loads(tool.function_def)
                tool_definitions.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool_def
                    }
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse tool definition for {tool.name}: {str(e)}")
        
        # OpenAI-style messages with tool calling
        messages = [
            {"role": "system", "content": self.agent.system_prompt},
            {"role": "user", "content": input_text}
        ]
        
        # Add memory context if agent supports it
        messages = await add_memory_context_to_messages(
            agent_id=self.agent.id,
            messages=messages,
            input_text=input_text,
            agent_type=self.agent_type
        )
        
        # Simulate a conversation with tools
        for _ in range(5):  # Maximum 5 tool calls per conversation
            try:
                # Get response from LLM that may include a tool call
                response = await mock_tool_calling(
                    self.llm_client,
                    messages,
                    tool_definitions,
                    input_text
                )
                
                # Check if response includes a tool call
                if "function_call" in response:
                    function_call = response["function_call"]
                    tool_name = function_call["name"]
                    tool_arguments = json.loads(function_call["arguments"])
                    
                    # Record tool call in database
                    record_tool_call(self.execution_id, tool_name, tool_arguments)
                    
                    # Execute tool if available
                    if tool_name in tool_funcs:
                        # Call the tool function - handle both async and sync functions
                        tool_func = tool_funcs[tool_name]
                        if asyncio.iscoroutinefunction(tool_func):
                            tool_result = await tool_func(**tool_arguments)
                        else:
                            # Handle synchronous function
                            tool_result = tool_func(**tool_arguments)
                    else:
                        tool_result = f"Tool {tool_name} not found"
                    
                    # Record tool result in database
                    record_tool_result(self.execution_id, tool_name, tool_result)
                    
                    # Add tool result to messages
                    # Convert tool result to string if it's a dict or list
                    if isinstance(tool_result, (dict, list)):
                        messages.append({
                            "role": "function",
                            "name": tool_name,
                            "content": json.dumps(tool_result)
                        })
                    else:
                        messages.append({
                            "role": "function",
                            "name": tool_name,
                            "content": str(tool_result)
                        })
                else:
                    # Final response without tool call
                    record_assistant_message(self.execution_id, response["content"])
                    
                    # Store in memory if agent supports it
                    await store_conversation(
                        agent_id=self.agent.id,
                        user_input=input_text,
                        assistant_output=response["content"],
                        agent_type=self.agent_type
                    )
                    
                    # Mark execution as successful
                    record_execution_success(self.execution_id)
                    
                    return response["content"]
            
            except Exception as e:
                logger.error(f"Error in agent tool execution: {str(e)}")
                return f"Error executing agent: {str(e)}"
        
        # If we reach here, we've hit the maximum number of tool calls
        logger.warning(f"Maximum tool calls reached. Tool calls made: {len(messages) - 2}")
        for i, msg in enumerate(messages[2:]):
            logger.warning(f"Tool call {i+1}: {json.dumps(msg)}")
        
        # Even for error cases, store in memory if this is a Nexus agent
        error_message = "I've made too many tool calls without reaching a conclusion. Please try a more specific query."
        
        # Store error in memory
        await store_conversation(
            agent_id=self.agent.id,
            user_input=input_text,
            assistant_output=error_message,
            agent_type=self.agent_type
        )
        
        return error_message
    
    async def arun_stream(self, input_text: str) -> AsyncGenerator[str, None]:
        """
        Run the agent with streaming response.
        
        Args:
            input_text: Input to send to the agent
        
        Yields:
            Chunks of the agent's response
        """
        # Simple streaming implementation
        messages = [
            {"role": "system", "content": self.agent.system_prompt},
            {"role": "user", "content": input_text}
        ]
        
        # Add memory context if agent supports it
        messages = await add_memory_context_to_messages(
            agent_id=self.agent.id,
            messages=messages,
            input_text=input_text,
            agent_type=self.agent_type
        )
        
        # Stream the response
        async for chunk in stream_response(self.llm_client, messages, self.execution_id):
            yield chunk
        
        # Store in memory if agent supports it (use the last chunk as the full response)
        if hasattr(self, '_last_chunk'):
            await store_conversation(
                agent_id=self.agent.id,
                user_input=input_text,
                assistant_output=self._last_chunk,
                agent_type=self.agent_type
            )
    
    async def cleanup(self):
        """Clean up agent resources."""
        # Close memory service
        await close_memory_service(self.agent.id)
        
        # Remove temporary directory
        cleanup_agent_environment(self.working_dir)