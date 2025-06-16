"""LLM communication adapter for terminal assistance using enhanced tekton-llm-client"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List, Callable, Awaitable, Tuple

# Import enhanced tekton-llm-client features
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings, get_env
)

from ..utils.logging import setup_logging
from ..utils.config import Config

logger = setup_logging()

class LLMAdapter:
    """LLM adapter for terminal assistance
    
    This adapter handles communication with LLMs through the tekton-llm-client.
    It provides command analysis and terminal assistance functionality.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the LLM adapter
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = Config(config_path)
        
        # Initialize template registry
        self.template_registry = PromptTemplateRegistry()
        
        # Load client settings from environment or config
        self.llm_url = get_env("TEKTON_LLM_URL", self.config.get("llm.adapter_url", "http://localhost:8003"))
        self.provider = get_env("TEKTON_LLM_PROVIDER", self.config.get("llm.provider", "anthropic"))
        self.model = get_env("TEKTON_LLM_MODEL", self.config.get("llm.model", "claude-3-sonnet-20240229"))
        
        # System prompt from config
        self.system_prompt = self.config.get("llm.system_prompt", 
            "You are a terminal assistant that helps users with command-line tasks. "
            "Provide concise explanations and suggestions for terminal commands. "
            "Focus on being helpful, accurate, and security-conscious."
        )
        
        # Initialize client settings
        self.client_settings = ClientSettings(
            component_id="terma.terminal",
            base_url=self.llm_url,
            provider_id=self.provider,
            model_id=self.model,
            timeout=30,
            max_retries=2,
            use_fallback=True
        )
        
        # Initialize LLM settings
        self.llm_settings = LLMSettings(
            temperature=0.7,
            max_tokens=500,
            top_p=0.95
        )
        
        # Create LLM client
        self.llm_client = None  # Will be initialized on first use
        
        # Initialize templates
        self._load_templates()
        
        # Session contexts
        self._session_contexts: Dict[str, List[Dict[str, str]]] = {}
        
    def _load_templates(self):
        """Load prompt templates for Terma"""
        # First try to load from standard locations
        standard_dirs = [
            "./prompt_templates",
            "./templates",
            "./terma/prompt_templates",
            "./terma/templates"
        ]
        
        for template_dir in standard_dirs:
            if os.path.exists(template_dir):
                self.template_registry.load_templates_from_directory(template_dir)
                logger.info(f"Loaded templates from {template_dir}")
        
        # Add core templates
        self.template_registry.register_template(
            "command_analysis",
            PromptTemplate(
                template="Please explain this command concisely: {command}",
                output_format=OutputFormat.TEXT
            )
        )
        
        self.template_registry.register_template(
            "output_analysis",
            PromptTemplate(
                template="Please explain the output of this command: {command}\n\nOutput:\n{output}",
                output_format=OutputFormat.TEXT
            )
        )
        
        self.template_registry.register_template(
            "terminal_help",
            PromptTemplate(
                template="Help me with this terminal task: {task}",
                output_format=OutputFormat.TEXT
            )
        )
        
    async def _get_client(self) -> TektonLLMClient:
        """Get or initialize the LLM client
        
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
    
    def _get_session_context(self, session_id: str) -> List[Dict[str, str]]:
        """Get or create the conversation context for a session
        
        Args:
            session_id: The terminal session ID
            
        Returns:
            The session context as a list of messages
        """
        if session_id not in self._session_contexts:
            # Initialize with system message
            self._session_contexts[session_id] = [
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            ]
        return self._session_contexts[session_id]
    
    def add_message(self, session_id: str, message: str, role: str = "user"):
        """Add a message to the conversation context
        
        Args:
            session_id: The terminal session ID
            message: The message content
            role: The message role (user or assistant)
        """
        context = self._get_session_context(session_id)
        context.append({"role": role, "content": message})
        
        # Keep context at a reasonable size (last 10 messages)
        if len(context) > 11:  # 1 system message + 10 conversation messages
            context = [context[0]] + context[-10:]
            self._session_contexts[session_id] = context
    
    def clear_context(self, session_id: str):
        """Clear the conversation context for a session
        
        Args:
            session_id: The terminal session ID
        """
        if session_id in self._session_contexts:
            # Keep the system message
            system_message = self._session_contexts[session_id][0]
            self._session_contexts[session_id] = [system_message]
    
    def set_provider_and_model(self, provider: str, model: str):
        """Set the LLM provider and model
        
        Args:
            provider: Provider ID (e.g., 'claude', 'openai')
            model: Model ID (e.g., 'claude-3-sonnet-20240229')
        """
        self.provider = provider
        self.model = model
        
        # Update the config
        self.config.set("llm.provider", provider)
        self.config.set("llm.model", model)
        
        # Update client settings
        self.client_settings.provider_id = provider
        self.client_settings.model_id = model
        
        # Reset client to ensure it uses the new settings
        self.llm_client = None
        
        logger.info(f"Set LLM provider to {provider} and model to {model}")
    
    async def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get all available LLM providers and their models
        
        Returns:
            Dict of provider information
        """
        try:
            client = await self._get_client()
            providers = await client.get_providers()
            return providers.providers
        except Exception as e:
            logger.warning(f"Error getting providers from LLM service: {e}")
        
        # Fallback to config
        return self.config.get_all_llm_providers()
    
    def get_current_provider_and_model(self) -> Tuple[str, str]:
        """Get the current provider and model
        
        Returns:
            Tuple of (provider, model)
        """
        return (self.provider, self.model)
    
    async def analyze_command(self, session_id: str, command: str) -> Optional[str]:
        """Analyze a command and provide assistance
        
        Args:
            session_id: The terminal session ID
            command: The command to analyze
            
        Returns:
            The LLM response, or None if an error occurred
        """
        try:
            # Get template
            template = self.template_registry.get_template("command_analysis")
            
            # Format template values
            template_values = {
                "command": command
            }
            
            # Generate prompt
            prompt = template.format(**template_values)
            
            # Add the prompt to the context
            self.add_message(session_id, prompt)
            
            # Get system prompt
            system_prompt = self.system_prompt
            
            # Get LLM client
            client = await self._get_client()
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            # Add the response to the context
            if response.content:
                self.add_message(session_id, response.content, role="assistant")
                
            return response.content
        except Exception as e:
            logger.error(f"Error analyzing command: {e}")
            return f"Error analyzing command: {str(e)}"
    
    async def analyze_output(self, session_id: str, command: str, output: str) -> Optional[str]:
        """Analyze command output and provide assistance
        
        Args:
            session_id: The terminal session ID
            command: The command that was run
            output: The command output
            
        Returns:
            The LLM response, or None if an error occurred
        """
        # Trim output if it's too long
        if len(output) > 4000:
            output = output[:2000] + "...[output truncated]..." + output[-2000:]
            
        try:
            # Get template
            template = self.template_registry.get_template("output_analysis")
            
            # Format template values
            template_values = {
                "command": command,
                "output": output
            }
            
            # Generate prompt
            prompt = template.format(**template_values)
            
            # Add the prompt to the context
            self.add_message(session_id, prompt)
            
            # Get system prompt
            system_prompt = self.system_prompt
            
            # Get LLM client
            client = await self._get_client()
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            # Add the response to the context
            if response.content:
                self.add_message(session_id, response.content, role="assistant")
                
            return response.content
        except Exception as e:
            logger.error(f"Error analyzing output: {e}")
            return f"Error analyzing output: {str(e)}"
            
    async def stream_command_analysis(self, session_id: str, command: str, 
                                     callback: Callable[[str], Awaitable[None]]) -> None:
        """Stream command analysis to a callback
        
        Args:
            session_id: The terminal session ID
            command: The command to analyze
            callback: Async function to call with each chunk of content
        """
        try:
            # Get template
            template = self.template_registry.get_template("command_analysis")
            
            # Format template values
            template_values = {
                "command": command
            }
            
            # Generate prompt
            prompt = template.format(**template_values)
            
            # Add the prompt to the context
            self.add_message(session_id, prompt)
            
            # Get system prompt
            system_prompt = self.system_prompt
            
            # Get LLM client
            client = await self._get_client()
            
            # Create streaming handler
            stream_handler = StreamHandler(callback_fn=callback)
            
            # Call LLM with streaming
            response_stream = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                streaming=True
            )
            
            # Process the stream
            collected_response = await stream_handler.process_stream(response_stream)
            
            # Add the full response to the context
            self.add_message(session_id, collected_response, role="assistant")
            
        except Exception as e:
            logger.error(f"Error streaming command analysis: {e}")
            await callback(f"Error analyzing command: {str(e)}")
            
    async def get_terminal_help(self, session_id: str, task: str) -> Optional[str]:
        """Get help with a terminal task
        
        Args:
            session_id: The terminal session ID
            task: The task to get help with
            
        Returns:
            The LLM response, or None if an error occurred
        """
        try:
            # Get template
            template = self.template_registry.get_template("terminal_help")
            
            # Format template values
            template_values = {
                "task": task
            }
            
            # Generate prompt
            prompt = template.format(**template_values)
            
            # Add the prompt to the context
            self.add_message(session_id, prompt)
            
            # Get system prompt
            system_prompt = self.system_prompt
            
            # Get LLM client
            client = await self._get_client()
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            # Add the response to the context
            if response.content:
                self.add_message(session_id, response.content, role="assistant")
                
            return response.content
        except Exception as e:
            logger.error(f"Error getting terminal help: {e}")
            return f"Error getting terminal help: {str(e)}"