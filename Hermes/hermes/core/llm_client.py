"""
Enhanced LLM Client for Hermes using the tekton-llm-client.

This module provides a unified interface for integrating with Large Language Models
using the tekton-llm-client library, which standardizes LLM interactions across 
all Tekton components.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable, Tuple
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

class LLMClient:
    """
    Enhanced LLM Client for Hermes using the tekton-llm-client library.
    
    This client provides a standardized interface for interacting with LLMs
    for message analysis, service analysis, and general chat capabilities.
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
        Initialize the LLM Client.
        
        Args:
            adapter_url: URL for the LLM adapter service
            model: Default model to use
            provider: LLM provider to use
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
            templates_directory: Path to prompt templates directory
        """
        # Get environment variables or set defaults
        try:
            from shared.urls import rhetor_url
            default_adapter_url = rhetor_url("")
        except ImportError:
            # Fallback to standard Tekton default port
            rhetor_port = TektonEnviron.get("RHETOR_PORT", "8003")
            default_adapter_url = f"http://localhost:{rhetor_port}"
        
        self.adapter_url = adapter_url or TektonEnviron.get("LLM_ADAPTER_URL", default_adapter_url)
        self.provider = provider or TektonEnviron.get("LLM_PROVIDER", "anthropic")
        # Model selection handled by Rhetor based on component and capability
        self.model = model  # Will be determined by Rhetor
        
        # Initialize client settings
        self.client_settings = ClientSettings(
            component_id="hermes.core",
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
        
        logger.info(f"Hermes LLM Client initialized with URL: {self.adapter_url}")
    
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
            "./hermes/prompt_templates",
            "./hermes/templates"
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
        """Register default prompt templates for Hermes."""
        # Message analysis template
        self.template_registry.register(PromptTemplate(
            name="message_analysis",
            template="""
            Analyze the following message that was sent through the Hermes message bus.
            Extract key information such as:
            1. Message purpose - What is the goal of this message?
            2. Components involved - Which components are mentioned or interacting?
            3. Data contents - What key data is being transmitted?
            4. Priority - How urgent or important does this message appear to be?
            
            Provide a brief summary of what this message is trying to accomplish in the system.
            
            Message:
            {{ message_content }}
            """,
            description="Template for analyzing messages sent through the Hermes bus"
        ))
        
        # Service analysis template
        self.template_registry.register(PromptTemplate(
            name="service_analysis",
            template="""
            Analyze the following service registration in the Tekton platform.
            Extract key information such as:
            1. Service capabilities - What functionality does this service provide?
            2. Dependencies - What other services might this service depend on?
            3. Integration points - How would other services interact with this one?
            4. Potential use cases - What problems does this service solve?
            
            Provide a brief summary of this service's role in the system.
            
            Service Data:
            {{ service_data }}
            """,
            description="Template for analyzing service registrations"
        ))
        
        # System prompts
        self.template_registry.register(PromptTemplate(
            name="system_message_analysis",
            template="""
            You are a message analysis specialist for the Hermes message bus system.
            Your role is to understand and classify messages being transmitted between
            components in the Tekton platform. Focus on extracting key information,
            identifying the purpose of messages, and determining which components are involved.
            Be concise and focus on the practical information that would help a developer
            understand message flow.
            """
        ))
        
        self.template_registry.register(PromptTemplate(
            name="system_service_analysis",
            template="""
            You are a service architecture specialist for the Hermes service discovery system.
            Your role is to analyze service registrations and understand their capabilities,
            dependencies, and integration points. Focus on the practical aspects of how a
            service fits into the overall system architecture, what functionality it provides,
            and how other services might interact with it.
            """
        ))
        
        self.template_registry.register(PromptTemplate(
            name="system_hermes_assistant",
            template="""
            You are a helpful assistant for the Hermes component in the Tekton platform.
            Hermes provides message bus and service discovery capabilities for the Tekton system.
            You can help users understand how Hermes works, how services register and communicate,
            and provide debugging assistance for message routing and service discovery issues.
            """
        ))
        
        logger.info("Registered default templates for Hermes")
    
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
    
    async def get_available_providers(self) -> Dict[str, Any]:
        """
        Get available LLM providers.
        
        Returns:
            Dict of available providers and their models
        """
        try:
            client = await self._get_client()
            providers_info = await client.get_providers()
            
            # Convert to a more usable format
            result = {}
            if hasattr(providers_info, 'providers'):
                for provider_id, provider_info in providers_info.providers.items():
                    provider_data = {
                        "available": True,
                        "models": []
                    }
                    
                    for model_id, model_info in provider_info.get("models", {}).items():
                        provider_data["models"].append({
                            "id": model_id,
                            "name": model_info.get("name", model_id),
                            "context_length": model_info.get("context_length", 8192)
                        })
                    
                    result[provider_id] = provider_data
            else:
                # Handle alternative format
                for provider in providers_info:
                    provider_id = provider.get("id")
                    if provider_id:
                        provider_data = {
                            "available": True,
                            "models": []
                        }
                        
                        for model in provider.get("models", []):
                            provider_data["models"].append({
                                "id": model.get("id"),
                                "name": model.get("name", model.get("id")),
                                "context_length": model.get("context_length", 8192)
                            })
                        
                        result[provider_id] = provider_data
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            
            # Return default providers if the API call fails
            return {
                self.provider: {
                    "available": True,
                    "models": [
                        {"id": self.model, "name": "Default Model"},
                        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
                        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
                    ]
                }
            }
    
    def get_current_provider_and_model(self) -> Tuple[str, str]:
        """
        Get the current provider and model.
        
        Returns:
            Tuple of (provider_id, model_id)
        """
        return (self.provider, self.model)
    
    def set_provider_and_model(self, provider_id: str, model_id: str) -> None:
        """
        Set the provider and model to use.
        
        Args:
            provider_id: Provider ID
            model_id: Model ID
        """
        self.provider = provider_id
        self.model = model_id
        
        # Update client settings with new provider and model
        if self.client_settings:
            self.client_settings.provider_id = provider_id
            self.client_settings.model_id = model_id
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
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
            provider: Optional provider override
            stream: Whether to stream the response
            
        Returns:
            Generated text or async generator for streaming
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if overrides are provided
            settings = None
            if any(x is not None for x in [temperature, max_tokens, model, provider]):
                settings = LLMSettings(
                    temperature=temperature if temperature is not None else self.llm_settings.temperature,
                    max_tokens=max_tokens if max_tokens is not None else self.llm_settings.max_tokens,
                    model=model if model is not None else self.model,
                    provider=provider if provider is not None else self.provider
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
        provider: Optional[str] = None,
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
            provider: Optional provider override
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
                provider=provider,
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
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None
    ) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
        """
        Send a chat message to the LLM.
        
        Args:
            message: User message
            chat_history: Optional chat history for context
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            model: Optional model override
            provider: Optional provider override
            stream: Whether to stream the response
            callback: Optional callback function for streaming
            
        Returns:
            If stream=False, returns a dictionary with the response
            If stream=True, returns an async generator for streaming
        """
        try:
            # Get LLM client
            client = await self._get_client()
            
            # Create custom settings if overrides are provided
            settings = None
            if any(x is not None for x in [temperature, max_tokens, model, provider]):
                settings = LLMSettings(
                    temperature=temperature if temperature is not None else self.llm_settings.temperature,
                    max_tokens=max_tokens if max_tokens is not None else self.llm_settings.max_tokens,
                    model=model if model is not None else self.model,
                    provider=provider if provider is not None else self.provider
                )
            
            # Use default system prompt if not provided
            if not system_prompt:
                system_template = self.template_registry.get_template("system_hermes_assistant")
                if system_template:
                    system_prompt = system_template.format()
            
            # Prepare messages
            messages = []
            if chat_history:
                messages.extend(chat_history)
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Generate with streaming if requested
            if stream:
                if callback:
                    # Create a wrapper to handle the stream
                    async def handle_stream():
                        try:
                            async for chunk in client.generate_chat(
                                messages=messages,
                                system_prompt=system_prompt,
                                settings=settings,
                                streaming=True
                            ):
                                if chunk:
                                    callback(chunk)
                                    yield chunk
                        except Exception as e:
                            error_msg = f"Error in streaming: {str(e)}"
                            logger.error(error_msg)
                            callback(error_msg)
                            yield error_msg
                    
                    return handle_stream()
                else:
                    # Return the raw stream
                    return client.generate_chat(
                        messages=messages,
                        system_prompt=system_prompt,
                        settings=settings,
                        streaming=True
                    )
            
            # Regular chat generation
            response = await client.generate_chat(
                messages=messages,
                system_prompt=system_prompt,
                settings=settings
            )
            
            return {
                "message": response.content,
                "success": True,
                "model": response.model,
                "provider": response.provider
            }
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            if stream:
                # Return a streaming error
                async def error_stream():
                    error_msg = f"Error in chat: {str(e)}"
                    if callback:
                        callback(error_msg)
                    yield error_msg
                return error_stream()
            
            return {
                "message": f"I encountered an error: {str(e)}. Please try again later.",
                "success": False
            }
    
    async def streaming_chat(
        self, 
        message: str, 
        callback: Callable[[Any], None],
        chat_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None
    ):
        """
        Send a chat message with streaming response.
        
        Args:
            message: User message
            callback: Callback function for streaming chunks
            chat_history: Optional chat history
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            model: Optional model override
            provider: Optional provider override
        """
        async for chunk in await self.chat(
            message=message,
            chat_history=chat_history,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            provider=provider,
            stream=True,
            callback=callback
        ):
            # The streaming is handled by the callback
            pass
    
    async def analyze_message(
        self, 
        message_content: str, 
        message_type: str = "standard",
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a message using LLM.
        
        Args:
            message_content: Message content
            message_type: Type of message (standard, log, registration, etc.)
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Analysis results
        """
        try:
            # Use template to analyze message
            response = await self.generate_with_template(
                template_name="message_analysis",
                variables={"message_content": message_content},
                system_template_name="system_message_analysis",
                temperature=temperature or 0.3,  # Lower temperature for analysis
                model=model,
                stream=False
            )
            
            # Parse the response
            return self._parse_message_analysis(response)
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return {
                "purpose": "Unknown",
                "components": [],
                "data_summary": "Error in analysis",
                "priority": "Unknown",
                "summary": f"Error analyzing message: {str(e)}",
                "full_analysis": ""
            }
    
    async def analyze_service(
        self, 
        service_data: Dict[str, Any],
        temperature: Optional[float] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a service registration using LLM.
        
        Args:
            service_data: Service registration data
            temperature: Optional temperature override
            model: Optional model override
            
        Returns:
            Analysis results
        """
        try:
            # Convert service data to JSON string for template
            service_data_str = json.dumps(service_data, indent=2)
            
            # Use template to analyze service
            response = await self.generate_with_template(
                template_name="service_analysis",
                variables={"service_data": service_data_str},
                system_template_name="system_service_analysis",
                temperature=temperature or 0.3,  # Lower temperature for analysis
                model=model,
                stream=False
            )
            
            # Parse the response
            return self._parse_service_analysis(response)
            
        except Exception as e:
            logger.error(f"Error analyzing service: {e}")
            return {
                "capabilities": [],
                "dependencies": [],
                "integration_points": [],
                "use_cases": [],
                "summary": f"Error analyzing service: {str(e)}",
                "full_analysis": ""
            }
    
    def _parse_message_analysis(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM message analysis response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed analysis
        """
        # Extract key information using basic parsing
        # More sophisticated implementations could use structured outputs
        
        # Extract message purpose
        purpose = "Unknown"
        for line in response.split("\n"):
            if "purpose" in line.lower() or "goal" in line.lower():
                if ":" in line:
                    purpose = line.split(":", 1)[1].strip()
                    break
        
        # Extract components
        components = []
        components_section = False
        for line in response.split("\n"):
            if "components" in line.lower() and ":" in line:
                components_section = True
                components_text = line.split(":", 1)[1].strip()
                if components_text:
                    components = [c.strip() for c in components_text.split(",")]
                continue
            
            if components_section and line.strip():
                if ":" in line and not line.strip().startswith("-"):  # New section
                    components_section = False
                elif line.strip().startswith("-"):
                    comp = line.strip()[1:].strip()
                    if comp:
                        components.append(comp)
        
        # Extract data summary
        data_summary = "Unknown"
        for line in response.split("\n"):
            if "data" in line.lower() and "content" in line.lower() and ":" in line:
                data_summary = line.split(":", 1)[1].strip()
                break
        
        # Extract priority
        priority = "Unknown"
        for line in response.split("\n"):
            if "priority" in line.lower() and ":" in line:
                priority = line.split(":", 1)[1].strip()
                break
        
        # Extract summary
        summary = ""
        summary_section = False
        for line in response.split("\n"):
            if "summary" in line.lower() and ":" in line:
                summary_section = True
                summary = line.split(":", 1)[1].strip()
                continue
            
            if summary_section and line.strip():
                if ":" in line and any(kw in line.lower() for kw in ["purpose", "components", "data", "priority"]):
                    summary_section = False
                else:
                    summary += " " + line.strip()
        
        if not summary:
            # If we couldn't find an explicit summary, use the last paragraph
            paragraphs = [p for p in response.split("\n\n") if p.strip()]
            if paragraphs:
                summary = paragraphs[-1].strip()
        
        return {
            "purpose": purpose,
            "components": components,
            "data_summary": data_summary,
            "priority": priority,
            "summary": summary,
            "full_analysis": response
        }
    
    def _parse_service_analysis(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM service analysis response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed analysis
        """
        # Extract capabilities, dependencies, etc. using basic parsing
        capabilities = []
        dependencies = []
        integration_points = []
        use_cases = []
        summary = ""
        
        current_section = None
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            if "capabilities" in line.lower() and ":" in line:
                current_section = "capabilities"
                continue
            elif "dependencies" in line.lower() and ":" in line:
                current_section = "dependencies"
                continue
            elif "integration" in line.lower() and ":" in line:
                current_section = "integration_points"
                continue
            elif "use case" in line.lower() and ":" in line:
                current_section = "use_cases"
                continue
            elif "summary" in line.lower() and ":" in line:
                current_section = "summary"
                summary = line.split(":", 1)[1].strip()
                continue
            
            if current_section == "capabilities" and line.startswith("-"):
                capabilities.append(line[1:].strip())
            elif current_section == "dependencies" and line.startswith("-"):
                dependencies.append(line[1:].strip())
            elif current_section == "integration_points" and line.startswith("-"):
                integration_points.append(line[1:].strip())
            elif current_section == "use_cases" and line.startswith("-"):
                use_cases.append(line[1:].strip())
            elif current_section == "summary":
                summary += " " + line
        
        if not summary:
            # If we couldn't find an explicit summary, use the last paragraph
            paragraphs = [p for p in response.split("\n\n") if p.strip()]
            if paragraphs:
                summary = paragraphs[-1].strip()
        
        return {
            "capabilities": capabilities,
            "dependencies": dependencies,
            "integration_points": integration_points,
            "use_cases": use_cases,
            "summary": summary,
            "full_analysis": response
        }