"""
Enhanced LLM Adapter for Ergon using the tekton-llm-client.

This module provides a unified interface for integrating with Large Language Models
using the tekton-llm-client library, which standardizes LLM interactions across 
all Tekton components.
"""

import json
import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable
from pathlib import Path

from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, get_env
)

logger = logging.getLogger(__name__)

class LLMAdapter:
    """
    Enhanced LLM Adapter for Ergon using the tekton-llm-client library.
    
    This adapter provides a consistent interface for LLM operations across Tekton
    components, with features like template management, structured output parsing,
    and streaming support.
    """
    
    def __init__(
        self,
        adapter_url: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        templates_directory: Optional[str] = None
    ):
        """
        Initialize the LLM Adapter.
        
        Args:
            adapter_url: URL for the LLM adapter service
            model: Default model to use
            provider: LLM provider to use
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
            templates_directory: Path to prompt templates directory
        """
        # Get environment variables or set defaults
        rhetor_port = get_env("RHETOR_PORT", "8003")
        default_adapter_url = f"http://localhost:{rhetor_port}"
        
        self.adapter_url = adapter_url or get_env("LLM_ADAPTER_URL", default_adapter_url)
        self.provider = provider or get_env("LLM_PROVIDER", "anthropic")
        self.model = model or get_env("LLM_MODEL", "claude-3-haiku-20240307")
        
        # Initialize client settings
        self.client_settings = ClientSettings(
            component_id="ergon.agent",
            base_url=self.adapter_url,
            provider_id=self.provider,
            model_id=self.model,
            timeout=120,
            max_retries=3,
            use_fallback=True
        )
        
        # Initialize LLM settings
        self.llm_settings = LLMSettings(
            temperature=temperature,
            max_tokens=max_tokens or 1500,
            top_p=0.95
        )
        
        # Create LLM client (will be initialized on first use)
        self.llm_client = None
        
        # Initialize template registry
        self.template_registry = PromptTemplateRegistry(load_defaults=False)
        
        # Set templates directory
        self.templates_directory = templates_directory
        
        # Load templates
        self._load_templates()
        
        logger.info(f"LLM Adapter initialized with URL: {self.adapter_url}")
    
    def _load_templates(self):
        """Load prompt templates from files and register default templates."""
        # Try to load templates from standard locations if not specified
        template_dirs = []
        
        if self.templates_directory:
            template_dirs.append(self.templates_directory)
        
        # Standard locations to check for templates
        standard_dirs = [
            "./prompt_templates",
            "./templates",
            "./ergon/prompt_templates",
            "./ergon/templates"
        ]
        template_dirs.extend(standard_dirs)
        
        # Try to load templates from directories
        templates_loaded = False
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                try:
                    for filename in os.listdir(template_dir):
                        if filename.endswith(('.json', '.yaml', '.yml')) and not filename.startswith('README'):
                            template_path = os.path.join(template_dir, filename)
                            try:
                                template = load_template(template_path)
                                if template:
                                    self.template_registry.register(template)
                                    logger.info(f"Loaded template '{template.name}' from {template_path}")
                                    templates_loaded = True
                            except Exception as e:
                                logger.warning(f"Failed to load template '{template_path}': {e}")
                    
                    if templates_loaded:
                        logger.info(f"Loaded templates from {template_dir}")
                except Exception as e:
                    logger.warning(f"Error loading templates from {template_dir}: {e}")
        
        # Register built-in templates if none were loaded from files
        if not templates_loaded:
            self._register_default_templates()
    
    def _register_default_templates(self):
        """Register default prompt templates for Ergon."""
        # Agent task execution template
        self.template_registry.register(PromptTemplate(
            name="agent_task_execution",
            template="""
            You are an intelligent agent tasked with executing the following:
            
            Task: {{ task_description }}
            
            {% if context %}
            Context:
            {{ context }}
            {% endif %}
            
            {% if constraints %}
            Constraints:
            {{ constraints }}
            {% endif %}
            
            {% if tools %}
            Available tools:
            {{ tools }}
            {% endif %}
            
            Please respond with a detailed plan to accomplish this task and then execute it step by step.
            Think through the problem carefully before acting. 
            
            Your response should include:
            1. Your analysis of the task
            2. A step-by-step plan
            3. Execution of each step
            4. A summary of what was accomplished
            """,
            description="Template for autonomous agent task execution"
        ))
        
        # Memory query template
        self.template_registry.register(PromptTemplate(
            name="memory_query",
            template="""
            You are assisting with retrieving and organizing relevant information from a memory database.
            
            Query: {{ query }}
            
            {% if retrieved_memories %}
            Retrieved memories:
            {{ retrieved_memories }}
            {% endif %}
            
            {% if context %}
            Additional context:
            {{ context }}
            {% endif %}
            
            Please analyze these memories and respond to the query by:
            1. Summarizing the most relevant information
            2. Organizing it in a coherent structure
            3. Identifying any gaps or inconsistencies
            4. Providing a clear answer to the original query
            """,
            description="Template for querying and synthesizing information from memory"
        ))
        
        # Workflow planning template
        self.template_registry.register(PromptTemplate(
            name="workflow_planning",
            template="""
            You are designing a workflow to accomplish a specific goal.
            
            Goal: {{ goal }}
            
            {% if available_agents %}
            Available agents:
            {{ available_agents }}
            {% endif %}
            
            {% if constraints %}
            Constraints:
            {{ constraints }}
            {% endif %}
            
            {% if context %}
            Additional context:
            {{ context }}
            {% endif %}
            
            Please create a detailed workflow plan that includes:
            1. A sequence of steps to achieve the goal
            2. Assignment of agents to each step
            3. Input and output specifications for each step
            4. Error handling and contingency plans
            5. Success criteria for the overall workflow
            
            Your workflow should be efficient, robust, and take advantage of the strengths of each available agent.
            """,
            description="Template for planning multi-agent workflows"
        ))
        
        # Agent coordination template
        self.template_registry.register(PromptTemplate(
            name="agent_coordination",
            template="""
            You are coordinating multiple agents to work together on a complex task.
            
            Task: {{ task_description }}
            
            Agents:
            {{ agents }}
            
            {% if previous_steps %}
            Previous steps completed:
            {{ previous_steps }}
            {% endif %}
            
            {% if current_state %}
            Current state:
            {{ current_state }}
            {% endif %}
            
            Please determine:
            1. Which agent should perform the next step
            2. What specific action they should take
            3. What information they need
            4. How their output should be used by other agents
            
            Provide clear instructions that can be passed to the selected agent.
            """,
            description="Template for coordinating multiple agents on a task"
        ))
        
        # System prompts
        self.template_registry.register(PromptTemplate(
            name="system_agent_execution",
            template="""
            You are an intelligent agent in the Ergon system, a multi-agent framework for autonomous task execution.
            You can process complex instructions, reason through problems, and execute tasks efficiently.
            You should follow constraints carefully, use tools appropriately, and provide clear explanations of your thought process.
            Your goal is to complete the assigned task completely and correctly while documenting your approach.
            """
        ))
        
        self.template_registry.register(PromptTemplate(
            name="system_workflow_planning",
            template="""
            You are a workflow planning specialist in the Ergon system.
            Your role is to design efficient workflows that coordinate multiple agents to achieve complex goals.
            Consider the strengths and limitations of different agents, ensure proper data flow between steps,
            and create robust processes that handle errors gracefully.
            """
        ))
        
        logger.info("Registered default templates for Ergon")
    
    async def _get_client(self) -> TektonLLMClient:
        """
        Get or initialize the LLM client.
        
        Returns:
            Initialized TektonLLMClient
        """
        if self.llm_client is None:
            self.llm_client = TektonLLMClient(
                settings=self.client_settings,
                llm_settings=self.llm_settings
            )
            await self.llm_client.initialize()
        return self.llm_client
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate from
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            model: Optional model override
            stream: Whether to stream the response
            
        Returns:
            Generated text or async generator for streaming
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if overrides are provided
            settings = None
            if temperature is not None or max_tokens is not None or model is not None:
                settings = LLMSettings(
                    temperature=temperature if temperature is not None else self.llm_settings.temperature,
                    max_tokens=max_tokens if max_tokens is not None else self.llm_settings.max_tokens,
                    model=model if model is not None else self.model,
                    provider=self.provider
                )
            
            # Generate with streaming if requested
            if stream:
                response_stream = await client.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    settings=settings,
                    streaming=True
                )
                return response_stream
            
            # Regular generation
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            if stream:
                # Return a streaming error
                async def error_stream():
                    yield f"Error generating response: {str(e)}"
                return error_stream()
            
            return f"Error generating response: {str(e)}"
    
    async def generate_with_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        system_template_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text using a prompt template.
        
        Args:
            template_name: Name of the template to use
            variables: Dictionary of variables for the template
            system_template_name: Optional name of system prompt template
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            model: Optional model override
            stream: Whether to stream the response
            
        Returns:
            Generated text or async generator for streaming
        """
        try:
            # Get templates
            template = self.template_registry.get_template(template_name)
            if not template:
                raise ValueError(f"Template not found: {template_name}")
            
            system_prompt = None
            if system_template_name:
                system_template = self.template_registry.get_template(system_template_name)
                if system_template:
                    system_prompt = system_template.format()
                else:
                    logger.warning(f"System template not found: {system_template_name}")
            
            # Format prompt with variables
            prompt = template.format(**variables)
            
            # Generate response
            return await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model,
                stream=stream
            )
            
        except Exception as e:
            logger.error(f"Template generation error: {str(e)}")
            if stream:
                # Return a streaming error
                async def error_stream():
                    yield f"Error generating with template: {str(e)}"
                return error_stream()
            
            return f"Error generating with template: {str(e)}"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Chat with messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            model: Optional model override
            stream: Whether to stream the response
            
        Returns:
            Generated text or async generator for streaming
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if overrides are provided
            settings = None
            if temperature is not None or max_tokens is not None or model is not None:
                settings = LLMSettings(
                    temperature=temperature if temperature is not None else self.llm_settings.temperature,
                    max_tokens=max_tokens if max_tokens is not None else self.llm_settings.max_tokens,
                    model=model if model is not None else self.model,
                    provider=self.provider
                )
            
            # Extract the system prompt from messages if present and not explicitly provided
            if not system_prompt:
                for message in messages:
                    if message["role"] == "system":
                        system_prompt = message["content"]
                        # Remove system message from the messages list
                        messages = [m for m in messages if m["role"] != "system"]
                        break
            
            # Get the most recent user message as the prompt
            user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    user_message = message["content"]
                    break
            
            if not user_message:
                user_message = messages[-1]["content"]
            
            # Generate with streaming if requested
            if stream:
                response_stream = await client.generate_text(
                    prompt=user_message,
                    system_prompt=system_prompt,
                    settings=settings,
                    streaming=True,
                    chat_history=[m for m in messages if m["role"] != "user"]
                )
                return response_stream
            
            # Regular generation
            response = await client.generate_text(
                prompt=user_message,
                system_prompt=system_prompt,
                settings=settings,
                chat_history=[m for m in messages if m["role"] != "user"]
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM chat error: {str(e)}")
            if stream:
                # Return a streaming error
                async def error_stream():
                    yield f"Error in chat: {str(e)}"
                return error_stream()
            
            return f"Error in chat: {str(e)}"
    
    async def parse_structured_output(
        self,
        prompt: str,
        output_format: Union[str, Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured output from a prompt.
        
        Args:
            prompt: The prompt to generate from
            output_format: JSON schema or format name for output structure
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Structured output as a dictionary
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if overrides are provided
            settings = None
            if temperature is not None or model is not None:
                settings = LLMSettings(
                    temperature=temperature if temperature is not None else self.llm_settings.temperature,
                    max_tokens=self.llm_settings.max_tokens,
                    model=model if model is not None else self.model,
                    provider=self.provider
                )
            
            # Create output parser
            parser = StructuredOutputParser(output_format)
            
            # Modify the prompt to include the output format instructions
            formatted_prompt = parser.format_prompt(prompt)
            
            # Generate response
            response = await client.generate_text(
                prompt=formatted_prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Parse the response
            parsed_output = parser.parse(response.content)
            return parsed_output
            
        except Exception as e:
            logger.error(f"Structured output generation error: {str(e)}")
            return {"error": str(e)}
    
    async def execute_agent_task(
        self,
        task_description: str,
        context: Optional[str] = None,
        constraints: Optional[str] = None,
        tools: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Execute a task using an LLM agent.
        
        Args:
            task_description: Description of the task to execute
            context: Optional additional context
            constraints: Optional constraints on execution
            tools: Optional description of available tools
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Agent's response with task execution
        """
        variables = {
            "task_description": task_description,
            "context": context,
            "constraints": constraints,
            "tools": tools
        }
        
        return await self.generate_with_template(
            template_name="agent_task_execution",
            variables=variables,
            system_template_name="system_agent_execution",
            temperature=temperature or 0.7,  # Higher temperature for creative problem-solving
            model=model,
            stream=False
        )
    
    async def plan_workflow(
        self,
        goal: str,
        available_agents: Optional[str] = None,
        constraints: Optional[str] = None,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Plan a workflow to achieve a goal.
        
        Args:
            goal: The goal to achieve
            available_agents: Optional description of available agents
            constraints: Optional constraints on the workflow
            context: Optional additional context
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Workflow plan
        """
        variables = {
            "goal": goal,
            "available_agents": available_agents,
            "constraints": constraints,
            "context": context
        }
        
        return await self.generate_with_template(
            template_name="workflow_planning",
            variables=variables,
            system_template_name="system_workflow_planning",
            temperature=temperature or 0.4,  # Lower temperature for more focused planning
            model=model,
            stream=False
        )
    
    async def query_memory(
        self,
        query: str,
        retrieved_memories: Optional[str] = None,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Query and synthesize information from memory.
        
        Args:
            query: The query to answer
            retrieved_memories: Optional retrieved memories to analyze
            context: Optional additional context
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Synthesized response to the query
        """
        variables = {
            "query": query,
            "retrieved_memories": retrieved_memories,
            "context": context
        }
        
        return await self.generate_with_template(
            template_name="memory_query",
            variables=variables,
            temperature=temperature or 0.3,  # Lower temperature for factual synthesis
            model=model,
            stream=False
        )
    
    async def coordinate_agents(
        self,
        task_description: str,
        agents: str,
        previous_steps: Optional[str] = None,
        current_state: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Coordinate multiple agents on a task.
        
        Args:
            task_description: Description of the overall task
            agents: Description of available agents
            previous_steps: Optional description of steps already completed
            current_state: Optional description of current state
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Coordination instructions
        """
        variables = {
            "task_description": task_description,
            "agents": agents,
            "previous_steps": previous_steps,
            "current_state": current_state
        }
        
        return await self.generate_with_template(
            template_name="agent_coordination",
            variables=variables,
            temperature=temperature or 0.5,
            model=model,
            stream=False
        )
    
    async def get_available_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available models from the LLM adapter.
        
        Returns:
            Dictionary of available models by provider
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Get models information
            providers_info = await client.get_providers()
            
            # Parse and return the result
            result = {}
            if hasattr(providers_info, 'providers'):
                for provider_id, provider_info in providers_info.providers.items():
                    models = []
                    for model_id, model_info in provider_info.get("models", {}).items():
                        models.append({
                            "id": model_id,
                            "name": model_info.get("name", model_id),
                            "context_length": model_info.get("context_length", 8192),
                            "capabilities": model_info.get("capabilities", [])
                        })
                    result[provider_id] = models
            else:
                # Handle alternative response format
                for provider in providers_info:
                    provider_id = provider.get("id")
                    if provider_id:
                        models = []
                        for model in provider.get("models", []):
                            models.append({
                                "id": model.get("id", ""),
                                "name": model.get("name", model.get("id", "")),
                                "context_length": model.get("context_length", 8192),
                                "capabilities": model.get("capabilities", [])
                            })
                        result[provider_id] = models
            
            return result
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            # Return fallback information
            return {
                "anthropic": [
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_length": 200000},
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_length": 200000},
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context_length": 200000}
                ],
                "openai": [
                    {"id": "gpt-4", "name": "GPT-4", "context_length": 8192},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 16384}
                ]
            }