"""
LLM Client for managing LLM providers and routing requests.

This module provides a unified interface for interacting with various LLM providers.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from datetime import datetime

# Import and apply the registry fix
from .registry_fix import apply_fix
apply_fix()  # Add missing load_from_directory method

# Import enhanced LLM client features
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings, get_env
)
from landmarks import architecture_decision, performance_boundary, integration_point

logger = logging.getLogger(__name__)

@architecture_decision(
    title="Multi-provider LLM abstraction",
    rationale="Support multiple LLM providers (Anthropic, OpenAI, Ollama) with fallback and unified interface",
    alternatives=["Single provider", "Direct API calls", "External gateway service"],
    decision_date="2024-02-15"
)
@integration_point(
    title="LLM provider connections",
    target_component="Anthropic API",
    protocol="REST/WebSocket",
    data_flow="Prompts → Provider selection → LLM API → Responses"
)
class LLMClient:
    """Client for managing and interacting with LLM providers"""
    
    def __init__(self, default_provider=None, default_model=None):
        """
        Initialize the LLM client.
        
        Args:
            default_provider: Default provider ID to use (e.g., "anthropic")
            default_model: Default model ID to use (provider-specific)
        """
        self.providers = {}
        self.default_provider_id = default_provider or get_env("LLM_PROVIDER", "anthropic")
        self.default_model = default_model or get_env("LLM_MODEL", None)
        self.provider_defaults = {
            "anthropic": "claude-3-sonnet-20240229",
            "openai": "gpt-4o",
            "ollama": "llama3",
            "simulated": "simulated-standard"
        }
        
        # Initialize prompt template registry
        self.prompt_registry = PromptTemplateRegistry()
        
        # Load default templates if directory exists
        templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        if os.path.exists(templates_dir):
            self.prompt_registry.load_from_directory(templates_dir)
    
    async def initialize(self):
        """Initialize all providers."""
        await self._load_providers()
        
        # Set default provider based on availability
        if not self.default_provider_id or self.default_provider_id not in self.providers:
            # Try to find an available provider in this order: anthropic, openai, ollama, simulated
            for provider_id in ["anthropic", "openai", "ollama", "simulated"]:
                if provider_id in self.providers and self.providers[provider_id].is_available():
                    self.default_provider_id = provider_id
                    logger.info(f"Set default provider to {provider_id}")
                    break
        
        # If no default model specified, use the provider's default
        if not self.default_model and self.default_provider_id:
            self.default_model = self.provider_defaults.get(
                self.default_provider_id, 
                self.providers[self.default_provider_id].default_model
            )
            logger.info(f"Set default model to {self.default_model}")
    
    async def _load_providers(self):
        """Load and initialize all available providers."""
        # Import all providers
        from ..models.providers.anthropic import AnthropicProvider
        from ..models.providers.openai import OpenAIProvider
        from ..models.providers.ollama import OllamaProvider
        from ..models.providers.simulated import SimulatedProvider
        
        # Create instances
        providers = {
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider(),
            "ollama": OllamaProvider(),
            "simulated": SimulatedProvider()
        }
        
        # Initialize providers in parallel with timeout
        initialization_tasks = []
        for name, provider in providers.items():
            async def init_with_timeout(p, n):
                try:
                    await asyncio.wait_for(p.initialize(), timeout=5.0)
                    logger.info(f"Provider {n} initialized successfully")
                except asyncio.TimeoutError:
                    logger.warning(f"Provider {n} initialization timed out")
                except Exception as e:
                    logger.warning(f"Provider {n} initialization failed: {e}")
            
            initialization_tasks.append(init_with_timeout(provider, name))
        
        await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        # Store the providers
        self.providers = providers
        
        # Log available providers
        available_providers = [
            provider_id for provider_id, provider in self.providers.items() 
            if provider.is_available()
        ]
        logger.info(f"Available providers: {available_providers}")
    
    @property
    def is_initialized(self):
        """Check if the LLM client has been initialized with providers."""
        return bool(self.providers) and (
            self.default_provider_id is None or 
            self.default_provider_id in self.providers
        )
    
    def get_provider(self, provider_id=None):
        """
        Get a provider by ID.
        
        Args:
            provider_id: Provider ID (defaults to default_provider_id)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider not found
        """
        provider_id = provider_id or self.default_provider_id
        
        if not provider_id or provider_id not in self.providers:
            raise ValueError(f"Provider {provider_id} not found")
        
        return self.providers[provider_id]
    
    def get_all_providers(self):
        """
        Get information about all providers.
        
        Returns:
            Dictionary mapping provider IDs to provider info
        """
        result = {}
        
        for provider_id, provider in self.providers.items():
            result[provider_id] = {
                "name": provider.display_name,
                "available": provider.is_available(),
                "models": provider.get_available_models()
            }
        
        return result
    
    def render_prompt(self, template_name, **kwargs):
        """Render a prompt template with variables.
        
        Args:
            template_name: Name of the template to render
            **kwargs: Variables to render the template with
            
        Returns:
            Rendered prompt string
        """
        return self.prompt_registry.render(template_name, **kwargs)
    
    def register_template(self, template_data):
        """Register a prompt template.
        
        Args:
            template_data: Template data as a dictionary with name, template, and description
        """
        self.prompt_registry.register(template_data)
    
    async def complete(
        self,
        message: str,
        context_id: str,
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a message with an LLM.
        
        Args:
            message: User message
            context_id: Context ID for tracking conversation
            system_prompt: Optional system prompt
            provider_id: Provider ID to use (defaults to default_provider_id)
            model_id: Model ID to use (defaults to provider's default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        fallback_provider_id = options.get("fallback_provider")
        
        try:
            # Get the provider
            provider = self.get_provider(provider_id)
            
            # Get the model
            model = model_id or self.default_model or provider.default_model
            
            # Complete the message
            response = await provider.complete(
                message=message,
                system_prompt=system_prompt,
                model=model,
                streaming=streaming,
                options=options
            )
            
            # Add context info to the response
            response["context"] = context_id
            
            return response
            
        except Exception as e:
            logger.error(f"Error completing message: {e}")
            
            # Try fallback if available
            if fallback_provider_id and fallback_provider_id != provider_id:
                logger.info(f"Attempting fallback to {fallback_provider_id}")
                try:
                    fallback_provider = self.get_provider(fallback_provider_id)
                    fallback_model = options.get("fallback_model") or fallback_provider.default_model
                    
                    # Complete with fallback
                    response = await fallback_provider.complete(
                        message=message,
                        system_prompt=system_prompt,
                        model=fallback_model,
                        streaming=streaming,
                        options=options
                    )
                    
                    # Add context info
                    response["context"] = context_id
                    response["fallback"] = True
                    
                    return response
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback failed: {fallback_error}")
            
            # Return error response
            return {
                "error": str(e),
                "context": context_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def stream_completion(
        self,
        message: str,
        context_id: str,
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        transform=None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a completion from an LLM.
        
        Args:
            message: User message
            context_id: Context ID for tracking conversation
            system_prompt: Optional system prompt
            provider_id: Provider ID to use (defaults to default_provider_id)
            model_id: Model ID to use (defaults to provider's default)
            options: Additional options for the LLM
            transform: Optional transformation function to apply to each chunk
            
        Yields:
            Dictionaries with response chunks
        """
        options = options or {}
        fallback_provider_id = options.get("fallback_provider")
        
        try:
            # Get the provider
            provider = self.get_provider(provider_id)
            
            # Get the model
            model = model_id or self.default_model or provider.default_model
            
            # Use the StreamHandler for managing the stream
            stream = provider.stream(
                message=message,
                system_prompt=system_prompt,
                model=model,
                options=options
            )
            
            handler = StreamHandler()
            
            # Process the stream with custom handlers
            async for chunk in handler.process_stream_with_context(
                stream,
                transform=transform,
                context={
                    "context_id": context_id,
                    "model": model,
                    "provider": provider.provider_id,
                    "timestamp": lambda: datetime.now().isoformat(),
                }
            ):
                yield chunk
            
        except Exception as e:
            logger.error(f"Error streaming completion: {e}")
            
            # Try fallback if available
            if fallback_provider_id and fallback_provider_id != provider_id:
                logger.info(f"Attempting fallback to {fallback_provider_id}")
                try:
                    fallback_provider = self.get_provider(fallback_provider_id)
                    fallback_model = options.get("fallback_model") or fallback_provider.default_model
                    
                    # Stream with fallback using StreamHandler
                    stream = fallback_provider.stream(
                        message=message,
                        system_prompt=system_prompt,
                        model=fallback_model,
                        options=options
                    )
                    
                    handler = StreamHandler()
                    
                    # Process the stream with custom handlers
                    async for chunk in handler.process_stream_with_context(
                        stream,
                        transform=transform,
                        context={
                            "context_id": context_id,
                            "model": fallback_model,
                            "provider": fallback_provider.provider_id,
                            "fallback": True,
                            "timestamp": lambda: datetime.now().isoformat(),
                        }
                    ):
                        yield chunk
                        
                    return
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback streaming failed: {fallback_error}")
            
            # Return error response
            yield {
                "error": str(e),
                "context": context_id,
                "timestamp": datetime.now().isoformat(),
                "done": True
            }
    
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        context_id: str,
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        streaming: bool = False,
        options: Optional[Dict[str, Any]] = None,
        parse_json_response: bool = False
    ) -> Dict[str, Any]:
        """
        Complete a chat conversation with an LLM.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            context_id: Context ID for tracking conversation
            system_prompt: Optional system prompt
            provider_id: Provider ID to use (defaults to default_provider_id)
            model_id: Model ID to use (defaults to provider's default)
            streaming: Whether to stream the response
            options: Additional options for the LLM
            parse_json_response: Whether to parse the response as JSON
            
        Returns:
            Dictionary with response data
        """
        options = options or {}
        fallback_provider_id = options.get("fallback_provider")
        
        try:
            # Get the provider
            provider = self.get_provider(provider_id)
            
            # Get the model
            model = model_id or self.default_model or provider.default_model
            
            # Complete the chat
            response = await provider.chat_complete(
                messages=messages,
                system_prompt=system_prompt,
                model=model,
                streaming=streaming,
                options=options
            )
            
            # Add context info
            response["context"] = context_id
            
            # Parse JSON if requested
            if parse_json_response and "content" in response:
                try:
                    response["parsed_content"] = parse_json(response["content"])
                except Exception as e:
                    logger.warning(f"Failed to parse JSON response: {e}")
                    response["parsing_error"] = str(e)
            
            return response
            
        except Exception as e:
            logger.error(f"Error completing chat: {e}")
            
            # Try fallback if available
            if fallback_provider_id and fallback_provider_id != provider_id:
                logger.info(f"Attempting fallback to {fallback_provider_id}")
                try:
                    fallback_provider = self.get_provider(fallback_provider_id)
                    fallback_model = options.get("fallback_model") or fallback_provider.default_model
                    
                    # Complete with fallback
                    response = await fallback_provider.chat_complete(
                        messages=messages,
                        system_prompt=system_prompt,
                        model=fallback_model,
                        streaming=streaming,
                        options=options
                    )
                    
                    # Add context info
                    response["context"] = context_id
                    response["fallback"] = True
                    
                    # Parse JSON if requested
                    if parse_json_response and "content" in response:
                        try:
                            response["parsed_content"] = parse_json(response["content"])
                        except Exception as parse_e:
                            logger.warning(f"Failed to parse JSON response: {parse_e}")
                            response["parsing_error"] = str(parse_e)
                    
                    return response
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback failed: {fallback_error}")
            
            # Return error response
            return {
                "error": str(e),
                "context": context_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        context_id: str,
        system_prompt: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        transform=None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a chat completion from an LLM.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            context_id: Context ID for tracking conversation
            system_prompt: Optional system prompt
            provider_id: Provider ID to use (defaults to default_provider_id)
            model_id: Model ID to use (defaults to provider's default)
            options: Additional options for the LLM
            transform: Optional transformation function to apply to each chunk
            
        Yields:
            Dictionaries with response chunks
        """
        options = options or {}
        fallback_provider_id = options.get("fallback_provider")
        
        try:
            # Get the provider
            provider = self.get_provider(provider_id)
            
            # Get the model
            model = model_id or self.default_model or provider.default_model
            
            # Stream the chat completion using the StreamHandler
            stream = provider.chat_stream(
                messages=messages,
                system_prompt=system_prompt,
                model=model,
                options=options
            )
            
            handler = StreamHandler()
            
            # Process the stream with custom handlers
            async for chunk in handler.process_stream_with_context(
                stream,
                transform=transform,
                context={
                    "context_id": context_id,
                    "model": model,
                    "provider": provider.provider_id,
                    "timestamp": lambda: datetime.now().isoformat(),
                }
            ):
                yield chunk
            
        except Exception as e:
            logger.error(f"Error streaming chat: {e}")
            
            # Try fallback if available
            if fallback_provider_id and fallback_provider_id != provider_id:
                logger.info(f"Attempting fallback to {fallback_provider_id}")
                try:
                    fallback_provider = self.get_provider(fallback_provider_id)
                    fallback_model = options.get("fallback_model") or fallback_provider.default_model
                    
                    # Stream with fallback using StreamHandler
                    stream = fallback_provider.chat_stream(
                        messages=messages,
                        system_prompt=system_prompt,
                        model=fallback_model,
                        options=options
                    )
                    
                    handler = StreamHandler()
                    
                    # Process the stream with custom handlers
                    async for chunk in handler.process_stream_with_context(
                        stream,
                        transform=transform,
                        context={
                            "context_id": context_id,
                            "model": fallback_model,
                            "provider": fallback_provider.provider_id,
                            "fallback": True,
                            "timestamp": lambda: datetime.now().isoformat(),
                        }
                    ):
                        yield chunk
                    
                    return
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback streaming failed: {fallback_error}")
            
            # Return error response
            yield {
                "error": str(e),
                "context": context_id,
                "timestamp": datetime.now().isoformat(),
                "done": True
            }