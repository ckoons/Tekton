#!/usr/bin/env python3
"""
LLM Adapter for Engram Memory System

This module implements an adapter for interacting with the Tekton LLM service,
providing a unified interface for LLM capabilities across the system using
the enhanced tekton-llm-client features.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable

# Import enhanced tekton-llm-client features
from tekton_llm_client import (
    TektonLLMClient,
    PromptTemplateRegistry, PromptTemplate, load_template,
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat,
    ClientSettings, LLMSettings, load_settings, get_env
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.llm_adapter")

class LLMAdapter:
    """
    Client for interacting with LLMs through the Tekton LLM Adapter.
    
    This class provides a unified interface for LLM operations, using the
    enhanced tekton-llm-client features for template management, streaming,
    and response handling.
    """
    
    def __init__(self, adapter_url: Optional[str] = None):
        """
        Initialize the LLM Adapter client.
        
        Args:
            adapter_url: URL for the LLM adapter service
        """
        # Load client settings from environment or config
        rhetor_port = get_env("RHETOR_PORT", "8003")
        default_adapter_url = f"http://localhost:{rhetor_port}"
        
        self.adapter_url = adapter_url or get_env("LLM_ADAPTER_URL", default_adapter_url)
        self.default_provider = get_env("LLM_PROVIDER", "anthropic")
        self.default_model = get_env("LLM_MODEL", "claude-3-haiku-20240307")
        
        # Initialize client settings
        self.client_settings = ClientSettings(
            component_id="engram.memory",
            base_url=self.adapter_url,
            provider_id=self.default_provider,
            model_id=self.default_model,
            timeout=120,
            max_retries=3,
            use_fallback=True
        )
        
        # Initialize LLM settings
        self.llm_settings = LLMSettings(
            temperature=0.7,
            max_tokens=1500,
            top_p=0.95
        )
        
        # Create LLM client (will be initialized on first use)
        self.llm_client = None
        
        # Initialize template registry
        self.template_registry = PromptTemplateRegistry(load_defaults=False)
        
        # Load prompt templates
        self._load_templates()
        
        logger.info(f"LLM Adapter initialized with URL: {self.adapter_url}")
    
    def _load_templates(self):
        """Load prompt templates for Engram"""
        # First try to load from standard locations
        standard_dirs = [
            "./prompt_templates",
            "./templates",
            "./engram/prompt_templates",
            "./engram/templates"
        ]
        
        # Try to load templates from directories
        for template_dir in standard_dirs:
            if os.path.exists(template_dir):
                # Load templates from directory using load_template utility
                try:
                    for filename in os.listdir(template_dir):
                        if filename.endswith(('.json', '.yaml', '.yml')) and not filename.startswith('README'):
                            template_path = os.path.join(template_dir, filename)
                            template_name = os.path.splitext(filename)[0]
                            try:
                                template = load_template(template_path)
                                if template:
                                    self.template_registry.register(template)
                                    logger.info(f"Loaded template '{template_name}' from {template_path}")
                            except Exception as e:
                                logger.warning(f"Failed to load template '{template_name}': {e}")
                    logger.info(f"Loaded templates from {template_dir}")
                except Exception as e:
                    logger.warning(f"Error loading templates from {template_dir}: {e}")
        
        # Add core templates
        self.template_registry.register({
            "name": "memory_analysis",
            "template": "Please analyze the following content:\n\n{{ content }}\n\n{{ context_prompt }}",
            "description": "Analysis of memory content"
        })
        
        self.template_registry.register({
            "name": "memory_categorization",
            "template": "Categorize this content:\n\n{{ content }}",
            "description": "Categorization of memory content"
        })
        
        self.template_registry.register({
            "name": "memory_summarization",
            "template": "Summarize these related memories:\n\n{{ memories }}",
            "description": "Summarization of related memories"
        })
        
        # System prompt templates
        self.template_registry.register({
            "name": "system_memory_analysis",
            "template": """
            You are an AI assistant helping to analyze and structure memory content.
            Extract key information, entities, and relationships from the provided text.
            Focus on identifying important concepts, facts, and potential connections to existing knowledge.
            """,
            "description": "System prompt for memory analysis"
        })
        
        self.template_registry.register({
            "name": "system_memory_categorization",
            "template": """
            You are an AI assistant that categorizes content into predefined categories.
            The available categories are: {{ categories_list }}
            Analyze the provided content and assign it to the most appropriate category.
            Return ONLY the category name without explanation or additional text.
            """,
            "description": "System prompt for memory categorization"
        })
        
        self.template_registry.register({
            "name": "system_memory_summarization",
            "template": """
            You are an AI assistant tasked with summarizing multiple related memories.
            Create a concise summary that captures the key information across all provided memories.
            Focus on identifying patterns, core facts, and essential information.
            """,
            "description": "System prompt for memory summarization"
        })
    
    async def _get_client(self) -> TektonLLMClient:
        """
        Get or initialize the LLM client
        
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
    
    async def chat(self, 
                  messages: List[Dict[str, str]],
                  model: Optional[str] = None,
                  temperature: float = 0.7,
                  max_tokens: Optional[int] = None,
                  stream: bool = False,
                  system_prompt: Optional[str] = None) -> Union[str, AsyncGenerator[str, None]]:
        """
        Send a chat request to the LLM adapter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: LLM model to use (defaults to configured default)
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            system_prompt: Optional system prompt
            
        Returns:
            If stream=False, returns the complete response as a string
            If stream=True, returns an async generator yielding response chunks
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Update settings with provided parameters
            custom_settings = LLMSettings(
                temperature=temperature,
                max_tokens=max_tokens or self.llm_settings.max_tokens,
                model=model or self.default_model,
                provider=self.default_provider
            )
            
            # Extract the last user message
            user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    user_message = message["content"]
                    break
            
            if not user_message:
                # Default to the last message if no user message is found
                user_message = messages[-1]["content"]
            
            # Determine system prompt to use
            chat_system_prompt = system_prompt
            if not chat_system_prompt:
                for message in messages:
                    if message["role"] == "system":
                        chat_system_prompt = message["content"]
                        break
            
            # If streaming is requested, use streaming approach
            if stream:
                return self._stream_chat(user_message, chat_system_prompt, custom_settings)
            
            # Regular chat request
            response = await client.generate_text(
                prompt=user_message,
                system_prompt=chat_system_prompt,
                settings=custom_settings
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM request exception: {str(e)}")
            return self._get_fallback_response()
    
    async def _stream_chat(self, 
                         prompt: str,
                         system_prompt: Optional[str],
                         custom_settings: LLMSettings) -> AsyncGenerator[str, None]:
        """
        Stream a chat response from the LLM adapter.
        
        Args:
            prompt: The prompt to send
            system_prompt: Optional system prompt
            custom_settings: LLM settings to use
            
        Yields:
            Response chunks as they arrive
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create a custom stream handler
            async def stream_callback(chunk: str) -> None:
                yield chunk
            
            # Create the stream generator
            async def generate_stream():
                try:
                    # Start streaming
                    response_stream = await client.generate_text(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        settings=custom_settings,
                        streaming=True
                    )
                    
                    # Process the stream manually
                    async for chunk in response_stream:
                        if hasattr(chunk, 'chunk') and chunk.chunk:
                            yield chunk.chunk
                            
                except Exception as e:
                    logger.error(f"Error in streaming: {str(e)}")
                    yield f"Error: {str(e)}"
            
            # Return the generator
            return generate_stream()
            
        except Exception as e:
            logger.error(f"Stream setup error: {str(e)}")
            async def error_generator():
                yield self._get_fallback_response()
            return error_generator()
    
    async def analyze_memory(self, 
                           content: str, 
                           context: Optional[str] = None, 
                           model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze text using the LLM adapter to extract insights for memory.
        
        Args:
            content: The text content to analyze
            context: Optional additional context
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Create context prompt if context is provided
            context_prompt = ""
            if context:
                context_prompt = f"Consider this additional context:\n\n{context}"
            
            # Render templates using the registry
            prompt = self.template_registry.render(
                "memory_analysis", 
                content=content,
                context_prompt=context_prompt
            )
            
            system_prompt = self.template_registry.render("system_memory_analysis")
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = None
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.3,  # Lower temperature for analysis tasks
                    max_tokens=2000  # Higher token limit for detailed analysis
                )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            return {
                "analysis": response.content,
                "success": True,
                "model": response.model,
                "provider": response.provider
            }
        except Exception as e:
            logger.error(f"Memory analysis error: {str(e)}")
            return {
                "analysis": "",
                "success": False,
                "error": str(e)
            }
    
    async def categorize_memory(self, 
                              content: str, 
                              categories: List[str],
                              model: Optional[str] = None) -> Dict[str, Any]:
        """
        Categorize memory content using the LLM adapter.
        
        Args:
            content: The text content to categorize
            categories: List of available categories
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Dictionary with categorization results
        """
        try:
            # Format categories list
            categories_list = ", ".join(categories)
            
            # Render templates using the registry
            prompt = self.template_registry.render(
                "memory_categorization", 
                content=content
            )
            
            system_prompt = self.template_registry.render(
                "system_memory_categorization", 
                categories_list=categories_list
            )
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings
            settings = LLMSettings(
                model=model or self.default_model,
                temperature=0.3,  # Lower temperature for categorization
                max_tokens=100  # Small token limit for category names
            )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            # Clean up response to get just the category
            response_text = response.content.strip()
            if response_text in categories:
                category = response_text
            else:
                # If exact match not found, try to extract from response
                for cat in categories:
                    if cat.lower() in response_text.lower():
                        category = cat
                        break
                else:
                    # Default to first category if no match
                    category = categories[0]
                    
            return {
                "category": category,
                "success": True,
                "model": response.model,
                "provider": response.provider
            }
        except Exception as e:
            logger.error(f"Memory categorization error: {str(e)}")
            return {
                "category": categories[0],
                "success": False,
                "error": str(e)
            }
    
    async def summarize_memories(self, 
                               memories: List[str], 
                               model: Optional[str] = None) -> str:
        """
        Summarize a collection of memories.
        
        Args:
            memories: List of memory contents to summarize
            model: LLM model to use (defaults to configured default)
            
        Returns:
            Summarized text
        """
        if not memories:
            return ""
            
        try:
            # Combine memories
            combined_memories = "\n\n".join(memories)
            
            # Render templates using the registry
            prompt = self.template_registry.render(
                "memory_summarization", 
                memories=combined_memories
            )
            
            system_prompt = self.template_registry.render("system_memory_summarization")
            
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if model is provided
            settings = None
            if model:
                settings = LLMSettings(
                    model=model,
                    temperature=0.5,
                    max_tokens=1000
                )
            
            # Call LLM and get response
            response = await client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                settings=settings
            )
            
            return response.content
        except Exception as e:
            logger.error(f"Memory summarization error: {str(e)}")
            return f"Error summarizing memories: {str(e)}"
    
    def _get_fallback_response(self) -> str:
        """
        Provide a fallback response when the LLM service is unavailable.
        
        Returns:
            A helpful error message
        """
        return (
            "I apologize, but I'm currently unable to connect to the LLM service. "
            "This could be due to network issues or the service being offline. "
            "Basic memory operations will continue to work, but advanced analysis "
            "and generation capabilities may be limited. Please try again later or "
            "contact your administrator if the problem persists."
        )
    
    async def get_available_models(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get the list of available models from the LLM adapter.
        
        Returns:
            Dictionary mapping providers to their available models
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Get providers information using enhanced client
            providers_info = await client.get_providers()
            
            # Convert to the expected format
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
            logger.error(f"Error getting models: {str(e)}")
            # Return fallback models
            return {
                "anthropic": [
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_length": 200000},
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_length": 200000}
                ],
                "openai": [
                    {"id": "gpt-4", "name": "GPT-4", "context_length": 8192},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 16384}
                ]
            }