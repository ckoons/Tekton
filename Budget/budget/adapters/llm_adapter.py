"""
LLM Adapter for Budget Component

Provides a simplified interface for using LLMs within the Budget component.
Adapts to available LLM clients in the Tekton ecosystem.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Cached LLM client instance
_llm_client = None

class LLMAdapter:
    """
    Adapter for making LLM API calls from the Budget component.
    
    Supports:
    - Hermes LLM Client (preferred)
    - Tekton LLM Client
    - Direct API calls to OpenAI, Anthropic, etc.
    """
    
    def __init__(self):
        """Initialize the LLM adapter."""
        self.client = None
        self.client_type = None
        debug_log.info("llm_adapter", "LLM Adapter initialized")
    
    async def initialize(self):
        """
        Initialize the LLM client by trying different available clients.
        
        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        debug_log.info("llm_adapter", "Initializing LLM client")
        
        # Try Hermes LLM client first
        if await self._try_hermes_client():
            self.client_type = "hermes"
            debug_log.info("llm_adapter", "Using Hermes LLM client")
            return True
        
        # Try Tekton LLM client next
        if await self._try_tekton_client():
            self.client_type = "tekton"
            debug_log.info("llm_adapter", "Using Tekton LLM client")
            return True
        
        # Try direct API clients last
        if await self._try_direct_api():
            self.client_type = "direct"
            debug_log.info("llm_adapter", "Using direct API client")
            return True
        
        debug_log.error("llm_adapter", "Failed to initialize any LLM client")
        return False
    
    async def _try_hermes_client(self) -> bool:
        """
        Try to initialize the Hermes LLM client.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Import the Hermes client
            from budget.utils.hermes_helper import get_hermes_client
            
            hermes_client = await get_hermes_client()
            if hermes_client:
                # Create a wrapper for the LLM service
                self.client = hermes_client
                return True
            return False
        except Exception as e:
            debug_log.info("llm_adapter", f"Hermes client not available: {str(e)}")
            return False
    
    async def _try_tekton_client(self) -> bool:
        """
        Try to initialize the Tekton LLM client.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to import the Tekton LLM client
            sys.path.append(os.path.abspath(os.path.join(parent_dir, "tekton-llm-client")))
            from tekton_llm_client import Client as TektonClient
            
            # Use environment variable for the server URL
            server_url = os.environ.get("TEKTON_LLM_SERVER", "http://localhost:8000")
            
            # Initialize the client
            self.client = TektonClient(server_url)
            
            # Test the client
            models = await self.client.list_models()
            if models:
                return True
            
            debug_log.warn("llm_adapter", "Tekton LLM client initialized but no models available")
            return False
            
        except Exception as e:
            debug_log.info("llm_adapter", f"Tekton LLM client not available: {str(e)}")
            return False
    
    async def _try_direct_api(self) -> bool:
        """
        Try to initialize direct API clients.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to import OpenAI
            import openai
            
            # Check if API key is set
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                debug_log.info("llm_adapter", "OpenAI API key not set")
                return False
            
            # Initialize the client
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            
            # Test the client
            try:
                models = self.client.models.list()
                if models:
                    return True
            except Exception as e:
                debug_log.warn("llm_adapter", f"OpenAI client test failed: {str(e)}")
                return False
                
        except Exception as e:
            debug_log.info("llm_adapter", f"Direct API client not available: {str(e)}")
            return False
    
    async def complete(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the LLM.
        
        Args:
            model: The model to use
            prompt: The prompt to send to the model
            system: Optional system message (for chat models)
            temperature: Randomness parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Dict[str, Any]: The model's response
        """
        if not self.client:
            debug_log.error("llm_adapter", "LLM client not initialized")
            return {"error": "LLM client not initialized"}
        
        debug_log.info("llm_adapter", f"Generating completion with model: {model}")
        
        try:
            if self.client_type == "hermes":
                return await self._complete_hermes(model, prompt, system, temperature, max_tokens, stop, **kwargs)
            elif self.client_type == "tekton":
                return await self._complete_tekton(model, prompt, system, temperature, max_tokens, stop, **kwargs)
            elif self.client_type == "direct":
                return await self._complete_direct(model, prompt, system, temperature, max_tokens, stop, **kwargs)
            else:
                debug_log.error("llm_adapter", "Unknown client type")
                return {"error": "Unknown client type"}
        except Exception as e:
            debug_log.error("llm_adapter", f"Error generating completion: {str(e)}")
            return {"error": str(e)}
    
    async def _complete_hermes(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the Hermes LLM client.
        
        Args:
            model: The model to use
            prompt: The prompt to send to the model
            system: Optional system message (for chat models)
            temperature: Randomness parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Dict[str, Any]: The model's response
        """
        try:
            # Call the Hermes LLM service
            request = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }
            
            if max_tokens:
                request["max_tokens"] = max_tokens
            if stop:
                request["stop"] = stop
            
            # Add any additional parameters
            for key, value in kwargs.items():
                request[key] = value
            
            # Make the request
            response = await self.client.llm.chat(request)
            
            return {
                "model": model,
                "content": response["choices"][0]["message"]["content"],
                "finish_reason": response["choices"][0]["finish_reason"],
                "usage": response.get("usage", {})
            }
        except Exception as e:
            debug_log.error("llm_adapter", f"Error with Hermes LLM client: {str(e)}")
            raise
    
    async def _complete_tekton(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the Tekton LLM client.
        
        Args:
            model: The model to use
            prompt: The prompt to send to the model
            system: Optional system message (for chat models)
            temperature: Randomness parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Dict[str, Any]: The model's response
        """
        try:
            messages = []
            
            # Add system message if provided
            if system:
                messages.append({"role": "system", "content": system})
            
            # Add user message
            messages.append({"role": "user", "content": prompt})
            
            # Build parameters
            params = {
                "temperature": temperature
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            if stop:
                params["stop"] = stop
            
            # Add any additional parameters
            for key, value in kwargs.items():
                params[key] = value
            
            # Make the request
            response = await self.client.chat(
                model=model,
                messages=messages,
                **params
            )
            
            return {
                "model": model,
                "content": response["choices"][0]["message"]["content"],
                "finish_reason": response["choices"][0]["finish_reason"],
                "usage": response.get("usage", {})
            }
        except Exception as e:
            debug_log.error("llm_adapter", f"Error with Tekton LLM client: {str(e)}")
            raise
    
    async def _complete_direct(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using direct API access.
        
        Args:
            model: The model to use
            prompt: The prompt to send to the model
            system: Optional system message (for chat models)
            temperature: Randomness parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop: Optional list of stop sequences
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Dict[str, Any]: The model's response
        """
        try:
            # Build messages
            messages = []
            
            # Add system message if provided
            if system:
                messages.append({"role": "system", "content": system})
            
            # Add user message
            messages.append({"role": "user", "content": prompt})
            
            # Build parameters
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            if stop:
                params["stop"] = stop
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in params:
                    params[key] = value
            
            # Make the request
            response = self.client.chat.completions.create(**params)
            
            return {
                "model": model,
                "content": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            debug_log.error("llm_adapter", f"Error with direct API: {str(e)}")
            raise

# Factory function to get/create LLM client
async def get_llm_client():
    """
    Get a cached LLM client or create a new one.
    
    Returns:
        LLMAdapter: The LLM adapter instance
    """
    global _llm_client
    
    if _llm_client is not None:
        return _llm_client
    
    # Create and initialize a new client
    client = LLMAdapter()
    success = await client.initialize()
    
    if success:
        _llm_client = client
        return client
    else:
        debug_log.error("llm_adapter", "Failed to initialize LLM client")
        return None