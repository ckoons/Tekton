"""
LLM Adapter for Harmonia using the tekton-llm-client.

This module provides a unified interface for working with Large Language Models
in Harmonia, primarily for workflow generation, expression evaluation, and
template filling.
"""

import os
import json
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
    LLM Adapter for Harmonia using the standardized tekton-llm-client library.
    
    This adapter provides a unified interface for LLM operations related to
    workflow engine functionality, including template processing, expression
    evaluation, and workflow generation.
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
        Initialize the Harmonia LLM Adapter.
        
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
            component_id="harmonia.workflow",
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
        
        logger.info(f"Harmonia LLM Adapter initialized with URL: {self.adapter_url}")
    
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
            "./harmonia/prompt_templates",
            "./harmonia/templates"
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
        """Register default prompt templates for Harmonia."""
        # Workflow creation template
        self.template_registry.register(PromptTemplate(
            name="workflow_creation",
            template="""
            You are tasked with creating a workflow template to accomplish a specific goal.
            
            Goal: {{ goal }}
            
            {% if components %}
            Available components:
            {{ components }}
            {% endif %}
            
            {% if constraints %}
            Constraints:
            {{ constraints }}
            {% endif %}
            
            {% if context %}
            Additional context:
            {{ context }}
            {% endif %}
            
            Please create a detailed workflow definition that includes:
            1. A sequence of steps with clear input and output specifications
            2. Any conditional logic required (if/else statements, loops)
            3. Error handling and fallback mechanisms
            4. Clear success criteria
            
            Your response should be a structured workflow definition that can be translated into Harmonia's workflow format.
            """,
            description="Template for creating workflow definitions"
        ))
        
        # Expression evaluation template
        self.template_registry.register(PromptTemplate(
            name="expression_evaluation",
            template="""
            You need to evaluate the following expression based on the current state:
            
            Expression: {{ expression }}
            
            Current state:
            {{ state }}
            
            {% if context %}
            Additional context:
            {{ context }}
            {% endif %}
            
            The expression may contain variables, logical operators, and functions.
            Variables in the expression are referenced using the ${variable_name} syntax.
            
            Please evaluate this expression by:
            1. Replacing variables with their values from the current state
            2. Performing any logical operations
            3. Applying any functions
            
            Return the final result of the evaluation along with your reasoning.
            """,
            description="Template for evaluating expressions with state variables"
        ))
        
        # State transition template
        self.template_registry.register(PromptTemplate(
            name="state_transition",
            template="""
            You need to determine how to update the workflow state based on a completed step.
            
            Current state:
            {{ current_state }}
            
            Step that completed:
            {{ completed_step }}
            
            Step output:
            {{ step_output }}
            
            {% if next_steps %}
            Potential next steps:
            {{ next_steps }}
            {% endif %}
            
            Please determine:
            1. How the state should be updated based on the completed step's output
            2. Which step(s) should be executed next
            3. Any conditions that should be evaluated
            
            Return your recommendations for state updates and next steps in a clear, structured format.
            """,
            description="Template for determining state transitions in workflows"
        ))
        
        # Template expansion template
        self.template_registry.register(PromptTemplate(
            name="template_expansion",
            template="""
            You need to expand a template by filling in variables from the current state.
            
            Template:
            {{ template }}
            
            Current state:
            {{ state }}
            
            {% if functions %}
            Available functions:
            {{ functions }}
            {% endif %}
            
            Template variables are indicated using the ${variable_name} syntax.
            These should be replaced with their corresponding values from the state.
            
            Some template variables may include function calls like ${functionName(param1, param2)}.
            For these, apply the function to the parameters and use the result.
            
            Please return the expanded template with all variables and functions replaced with their values.
            """,
            description="Template for expanding templates with state variables and functions"
        ))
        
        # Troubleshooting template
        self.template_registry.register(PromptTemplate(
            name="workflow_troubleshooting",
            template="""
            You need to troubleshoot a workflow that has encountered an issue.
            
            Workflow definition:
            {{ workflow }}
            
            Current state:
            {{ state }}
            
            Error details:
            {{ error }}
            
            {% if execution_history %}
            Execution history:
            {{ execution_history }}
            {% endif %}
            
            Please analyze this workflow issue and provide:
            1. A diagnosis of what is likely causing the error
            2. Recommendations for resolving the issue
            3. Suggestions for preventing similar issues in the future
            
            Focus on practical solutions that would help a workflow developer fix the problem.
            """,
            description="Template for troubleshooting workflow execution issues"
        ))
        
        # System prompts
        self.template_registry.register(PromptTemplate(
            name="system_workflow_creation",
            template="""
            You are a workflow design specialist in the Harmonia system. 
            Your role is to create efficient, robust workflow definitions that accomplish specific goals.
            Focus on creating precise, well-structured workflows with clear steps, appropriate error handling,
            and optimal component usage. Use conditional logic where appropriate to handle different scenarios.
            """
        ))
        
        self.template_registry.register(PromptTemplate(
            name="system_expression_evaluation",
            template="""
            You are an expression evaluation specialist in the Harmonia system.
            Your role is to accurately evaluate expressions involving variables, logical operators, and functions
            based on the current state of a workflow execution. Be precise in your evaluation and show your reasoning
            step by step. Variables are referenced using ${variable_name} syntax.
            """
        ))
        
        self.template_registry.register(PromptTemplate(
            name="system_state_transition",
            template="""
            You are a state management specialist in the Harmonia system.
            Your role is to determine appropriate state transitions in workflows based on completed steps and their outputs.
            Focus on maintaining state consistency, ensuring proper data flow between steps, and selecting
            appropriate next steps based on conditions and the current state.
            """
        ))
        
        logger.info("Registered default templates for Harmonia")
    
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
    
    async def create_workflow(
        self,
        goal: str,
        components: Optional[str] = None,
        constraints: Optional[str] = None,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Create a workflow definition to accomplish a goal.
        
        Args:
            goal: The goal the workflow should accomplish
            components: Optional description of available components
            constraints: Optional constraints on the workflow
            context: Optional additional context
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Generated workflow definition
        """
        variables = {
            "goal": goal,
            "components": components,
            "constraints": constraints,
            "context": context
        }
        
        return await self.generate_with_template(
            template_name="workflow_creation",
            variables=variables,
            system_template_name="system_workflow_creation",
            temperature=temperature or 0.5,
            model=model,
            stream=False
        )
    
    async def evaluate_expression(
        self,
        expression: str,
        state: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Evaluate an expression based on the current state.
        
        Args:
            expression: The expression to evaluate
            state: Current state as a string
            context: Optional additional context
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Evaluation result
        """
        variables = {
            "expression": expression,
            "state": state,
            "context": context
        }
        
        return await self.generate_with_template(
            template_name="expression_evaluation",
            variables=variables,
            system_template_name="system_expression_evaluation",
            temperature=temperature or 0.3,  # Lower temperature for more precise evaluation
            model=model,
            stream=False
        )
    
    async def determine_state_transition(
        self,
        current_state: str,
        completed_step: str,
        step_output: str,
        next_steps: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Determine how to update state after a step completes.
        
        Args:
            current_state: Current workflow state
            completed_step: Step that just completed
            step_output: Output from the completed step
            next_steps: Optional potential next steps
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Recommendations for state updates and next steps
        """
        variables = {
            "current_state": current_state,
            "completed_step": completed_step,
            "step_output": step_output,
            "next_steps": next_steps
        }
        
        return await self.generate_with_template(
            template_name="state_transition",
            variables=variables,
            system_template_name="system_state_transition",
            temperature=temperature or 0.4,
            model=model,
            stream=False
        )
    
    async def expand_template(
        self,
        template: str,
        state: str,
        functions: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Expand a template by filling in variables from state.
        
        Args:
            template: Template to expand
            state: Current state as a string
            functions: Optional available functions
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Expanded template
        """
        variables = {
            "template": template,
            "state": state,
            "functions": functions
        }
        
        return await self.generate_with_template(
            template_name="template_expansion",
            variables=variables,
            temperature=temperature or 0.2,  # Very low temperature for precise template expansion
            model=model,
            stream=False
        )
    
    async def troubleshoot_workflow(
        self,
        workflow: str,
        state: str,
        error: str,
        execution_history: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Troubleshoot a workflow execution issue.
        
        Args:
            workflow: Workflow definition
            state: Current state
            error: Error details
            execution_history: Optional execution history
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Troubleshooting analysis and recommendations
        """
        variables = {
            "workflow": workflow,
            "state": state,
            "error": error,
            "execution_history": execution_history
        }
        
        return await self.generate_with_template(
            template_name="workflow_troubleshooting",
            variables=variables,
            temperature=temperature or 0.6,
            model=model,
            stream=False
        )
    
    async def generate_json_workflow(
        self,
        goal: str,
        components: Optional[str] = None,
        constraints: Optional[str] = None,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a workflow definition in JSON format.
        
        Args:
            goal: The goal the workflow should accomplish
            components: Optional description of available components
            constraints: Optional constraints on the workflow
            context: Optional additional context
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Workflow definition as a JSON object
        """
        # Define the expected JSON schema for workflows
        workflow_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "component": {"type": "string"},
                            "inputs": {"type": "object"},
                            "outputs": {"type": "object"},
                            "conditions": {"type": "object"}
                        }
                    }
                },
                "initialState": {"type": "object"},
                "transitions": {"type": "object"}
            }
        }
        
        # Create a prompt for workflow generation
        prompt = f"""
        Please create a workflow definition in JSON format to accomplish the following goal:
        
        {goal}
        
        """
        
        if components:
            prompt += f"""
            Available components:
            {components}
            
            """
        
        if constraints:
            prompt += f"""
            Constraints:
            {constraints}
            
            """
        
        if context:
            prompt += f"""
            Additional context:
            {context}
            
            """
        
        # Generate structured JSON output
        return await self.parse_structured_output(
            prompt=prompt,
            output_format=workflow_schema,
            system_prompt="You are a workflow design specialist. Create well-structured, efficient workflow definitions in JSON format that follow Harmonia's workflow structure.",
            temperature=temperature or 0.4,
            model=model
        )