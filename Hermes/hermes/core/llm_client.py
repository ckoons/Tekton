"""
Enhanced LLM Client for Hermes using Rhetor.

This module provides a unified interface for integrating with Large Language Models
using the Rhetor service, which standardizes LLM interactions across 
all Tekton components.
"""

import os
from shared.env import TektonEnviron
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable, Tuple
from pathlib import Path

from shared.rhetor_client import RhetorClient

# Create compatibility classes
class PromptTemplateRegistry:
    def __init__(self):
        self.templates = {}
    
    def load_from_directory(self, path):
        pass
        
    def register(self, name, template):
        self.templates[name] = template
        
    def get(self, name):
        return self.templates.get(name)
        
class PromptTemplate:
    def __init__(self, template, variables=None):
        self.template = template
        self.variables = variables or []
        
    def render(self, **kwargs):
        return self.template.format(**kwargs)
        
class JSONParser:
    def parse(self, text):
        try:
            return json.loads(text)
        except:
            return None
            
class StreamHandler:
    def __init__(self):
        pass
        
    async def handle(self, stream):
        result = []
        async for chunk in stream:
            result.append(chunk)
        return ''.join(result)
        
class StructuredOutputParser:
    def __init__(self, format_type):
        self.format_type = format_type
        
    def parse(self, text):
        if self.format_type == "json":
            try:
                return json.loads(text)
            except:
                return {"raw": text}
        return text
        
class OutputFormat:
    JSON = "json"
    TEXT = "text"
    LIST = "list"
    
def get_env(key, default=None):
    return TektonEnviron.get(key, default)

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Enhanced LLM Client for Hermes using Rhetor.
    
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
            adapter_url: URL for the LLM adapter service (ignored, uses Rhetor)
            model: Default model to use (ignored, Rhetor handles this)
            provider: Default provider to use (ignored, Rhetor handles this)
            temperature: Default temperature for text generation
            max_tokens: Default max tokens for text generation
            templates_directory: Directory containing prompt templates
        """
        # Use Rhetor client
        self.client = RhetorClient(component="hermes")
        
        # Store defaults
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens or 2000
        
        # Initialize template registry
        self.template_registry = PromptTemplateRegistry()
        
        # Load templates if directory specified
        if templates_directory and os.path.exists(templates_directory):
            self.template_registry.load_from_directory(templates_directory)
            
        # Load default templates
        self._load_default_templates()
        
        # JSON parser
        self.json_parser = JSONParser()
        
        # Stream handler
        self.stream_handler = StreamHandler()
        
        logger.info(f"Initialized Hermes LLM Client using Rhetor")
    
    def _load_default_templates(self):
        """Load default prompt templates."""
        # Message analysis template
        self.template_registry.register(
            "message_analysis",
            PromptTemplate(
                "Analyze the following message:\n\n{message_content}\n\n"
                "Provide analysis including: intent, entities, sentiment, and suggested actions.",
                variables=["message_content"]
            )
        )
        
        # Service discovery template
        self.template_registry.register(
            "service_discovery",
            PromptTemplate(
                "Based on the following request: {request}\n\n"
                "Available services: {services}\n\n"
                "Determine which service(s) should handle this request and explain why.",
                variables=["request", "services"]
            )
        )
        
        # Response generation template
        self.template_registry.register(
            "response_generation",
            PromptTemplate(
                "Generate a response to the following:\n"
                "User Message: {user_message}\n"
                "Context: {context}\n"
                "Service Response: {service_response}\n\n"
                "Create a helpful and clear response.",
                variables=["user_message", "context", "service_response"]
            )
        )
        
        # Error explanation template
        self.template_registry.register(
            "error_explanation",
            PromptTemplate(
                "Explain the following error in user-friendly terms:\n"
                "Error: {error_message}\n"
                "Context: {error_context}\n\n"
                "Provide a clear explanation and suggest solutions if possible.",
                variables=["error_message", "error_context"]
            )
        )
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text or async generator if streaming
        """
        # Combine system and user prompts
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
        # Use provided values or defaults
        temp = temperature if temperature is not None else self.default_temperature
        tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Generate using Rhetor
        response = await self.client.generate(
            prompt=full_prompt,
            capability="chat",
            temperature=temp,
            max_tokens=tokens
        )
        
        if stream:
            # Simulate streaming for compatibility
            async def stream_generator():
                for chunk in response.split():
                    yield chunk + " "
                    await asyncio.sleep(0.01)
            return stream_generator()
        
        return response
    
    async def analyze_message(
        self,
        message_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a message for intent, entities, sentiment, etc.
        
        Args:
            message_content: The message to analyze
            context: Optional context information
            
        Returns:
            Analysis results including intent, entities, sentiment
        """
        # Get the message analysis template
        template = self.template_registry.get("message_analysis")
        
        # Render the template
        prompt = template.render(message_content=message_content)
        
        # Add context if provided
        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        # Generate analysis
        response = await self.client.generate(
            prompt=prompt,
            capability="reasoning",
            temperature=0.3,
            max_tokens=1500
        )
        
        # Try to parse as JSON
        result = self.json_parser.parse(response)
        if result:
            return result
            
        # Fallback to structured extraction
        return {
            "raw_analysis": response,
            "intent": "unknown",
            "entities": [],
            "sentiment": "neutral",
            "confidence": 0.5
        }
    
    async def determine_service(
        self,
        request: str,
        available_services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Determine which service(s) should handle a request.
        
        Args:
            request: The user request
            available_services: List of available services with their capabilities
            
        Returns:
            Service selection with reasoning
        """
        # Get the service discovery template
        template = self.template_registry.get("service_discovery")
        
        # Format services list
        services_str = json.dumps(available_services, indent=2)
        
        # Render the template
        prompt = template.render(request=request, services=services_str)
        
        # Generate analysis
        response = await self.client.generate(
            prompt=prompt,
            capability="reasoning",
            temperature=0.2,
            max_tokens=1000
        )
        
        # Try to parse as JSON
        result = self.json_parser.parse(response)
        if result:
            return result
            
        # Fallback response
        return {
            "selected_services": [],
            "reasoning": response,
            "confidence": 0.5
        }
    
    async def generate_response(
        self,
        user_message: str,
        service_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a user-friendly response based on service output.
        
        Args:
            user_message: Original user message
            service_response: Response from the service
            context: Optional context information
            
        Returns:
            User-friendly response
        """
        # Get the response generation template
        template = self.template_registry.get("response_generation")
        
        # Format context
        context_str = json.dumps(context, indent=2) if context else "No additional context"
        
        # Render the template
        prompt = template.render(
            user_message=user_message,
            context=context_str,
            service_response=service_response
        )
        
        # Generate response
        response = await self.client.generate(
            prompt=prompt,
            capability="chat",
            temperature=0.7,
            max_tokens=1500
        )
        
        return response
    
    async def explain_error(
        self,
        error_message: str,
        error_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a user-friendly explanation of an error.
        
        Args:
            error_message: The error message
            error_context: Optional context about the error
            
        Returns:
            User-friendly error explanation
        """
        # Get the error explanation template
        template = self.template_registry.get("error_explanation")
        
        # Format context
        context_str = json.dumps(error_context, indent=2) if error_context else "No additional context"
        
        # Render the template
        prompt = template.render(
            error_message=error_message,
            error_context=context_str
        )
        
        # Generate explanation
        response = await self.client.generate(
            prompt=prompt,
            capability="chat",
            temperature=0.6,
            max_tokens=1000
        )
        
        return response
    
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        General chat interface.
        
        Args:
            message: User message
            conversation_history: Optional conversation history
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Chat response
        """
        # Build conversation context
        prompt = message
        if conversation_history:
            history_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            prompt = f"Conversation history:\n{history_str}\n\nUser: {message}"
        
        # Use provided values or defaults
        temp = temperature if temperature is not None else self.default_temperature
        tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Generate response
        response = await self.client.chat(
            message=prompt,
            temperature=temp,
            max_tokens=tokens
        )
        
        return response
    
    async def extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text response.
        
        Args:
            text: Text that may contain JSON
            
        Returns:
            Extracted JSON object or None
        """
        # Try direct parsing
        result = self.json_parser.parse(text)
        if result:
            return result
            
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            json_str = text.split("```json", 1)[1]
            json_str = json_str.split("```", 1)[0]
            result = self.json_parser.parse(json_str.strip())
            if result:
                return result
                
        # Try to find JSON-like content
        import re
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text)
        for match in matches:
            result = self.json_parser.parse(match)
            if result:
                return result
                
        return None
    
    async def shutdown(self):
        """Shutdown the client."""
        # Rhetor client doesn't need explicit shutdown
        logger.info("Hermes LLM Client shutdown")

# Convenience function for creating client
async def create_llm_client(**kwargs) -> LLMClient:
    """
    Create and return an LLM client.
    
    Args:
        **kwargs: Arguments to pass to LLMClient constructor
        
    Returns:
        Initialized LLMClient
    """
    return LLMClient(**kwargs)