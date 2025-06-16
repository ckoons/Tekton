#!/usr/bin/env python3
"""
Ollama MCP Adapter

This module implements the Multi-Capability Provider (MCP) protocol adapter
for Ollama, allowing it to be used as an MCP service or capability provider.
"""

import asyncio
import json
import logging
import os
import sys
import requests
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram.ollama_mcp_adapter")

# Import Ollama system prompts if available
try:
    from engram.ollama.ollama_system_prompts import (
        get_memory_system_prompt,
        get_communication_system_prompt, 
        get_combined_system_prompt,
        get_model_capabilities
    )
    SYSTEM_PROMPTS_AVAILABLE = True
    logger.info("Loaded ollama_system_prompts from engram.ollama")
except ImportError:
    logger.warning("Ollama system prompts not available, will use default prompts")
    SYSTEM_PROMPTS_AVAILABLE = False

class OllamaMCPAdapter:
    """
    Multi-Capability Provider (MCP) adapter for Ollama.
    
    This class provides an adapter that implements the MCP protocol
    for Ollama's language model services, allowing them to be used within
    an MCP ecosystem.
    """
    
    def __init__(self, host="http://localhost:11434"):
        """
        Initialize the Ollama MCP Adapter.
        
        Args:
            host: The Ollama API host URL
        """
        self.host = host
        self.api_url = f"{host}/api"
        self.capabilities = self._generate_capabilities()
        
        # Check Ollama availability
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                self.available_models = [model["name"] for model in response.json().get("models", [])]
                logger.info(f"Ollama MCP Adapter initialized with {len(self.available_models)} models")
                logger.info(f"Available models: {', '.join(self.available_models[:5])}...")
            else:
                self.available_models = []
                logger.warning(f"Ollama seems to be running but returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.available_models = []
            logger.warning(f"Ollama API not available at {self.host}: {e}")
    
    def _generate_capabilities(self) -> Dict[str, Any]:
        """
        Generate the capability manifest for Ollama's services.
        
        Returns:
            A dictionary describing available capabilities
        """
        return {
            "ollama_generate": {
                "description": "Generate text with an Ollama model",
                "parameters": {
                    "model": {"type": "string", "description": "Ollama model to use"},
                    "prompt": {"type": "string", "description": "The prompt to generate from"},
                    "system": {"type": "string", "description": "System prompt for the model", "optional": True},
                    "template": {"type": "string", "description": "Prompt template to use", "optional": True},
                    "context": {"type": "array", "description": "Context for model generation", "optional": True},
                    "options": {"type": "object", "description": "Additional generation options", "optional": True}
                },
                "returns": {"type": "object", "description": "Generated text result"}
            },
            "ollama_chat": {
                "description": "Chat with an Ollama model",
                "parameters": {
                    "model": {"type": "string", "description": "Ollama model to use"},
                    "messages": {"type": "array", "description": "Array of message objects"},
                    "system": {"type": "string", "description": "System prompt for the chat", "optional": True},
                    "template": {"type": "string", "description": "Prompt template to use", "optional": True},
                    "options": {"type": "object", "description": "Additional generation options", "optional": True},
                    "enable_memory": {"type": "boolean", "description": "Enable Engram memory integration", "optional": True}
                },
                "returns": {"type": "object", "description": "Chat completion result"}
            },
            "ollama_tags": {
                "description": "List available Ollama models",
                "parameters": {},
                "returns": {"type": "object", "description": "List of available models"}
            },
            "ollama_memory_chat": {
                "description": "Chat with an Ollama model with integrated memory",
                "parameters": {
                    "model": {"type": "string", "description": "Ollama model to use"},
                    "messages": {"type": "array", "description": "Array of message objects"},
                    "system": {"type": "string", "description": "System prompt for the chat", "optional": True},
                    "client_id": {"type": "string", "description": "Engram client ID", "optional": True},
                    "memory_prompt_type": {"type": "string", "description": "Type of memory prompt (memory, communication, combined)", "optional": True},
                    "options": {"type": "object", "description": "Additional generation options", "optional": True}
                },
                "returns": {"type": "object", "description": "Chat completion result with memory integration"}
            }
        }
    
    async def get_manifest(self) -> Dict[str, Any]:
        """
        Get the MCP capability manifest.
        
        Returns:
            A dictionary containing the MCP manifest
        """
        return {
            "name": "ollama",
            "version": "1.0.0",
            "description": "Ollama Language Model Services",
            "capabilities": self.capabilities
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request.
        
        Args:
            request: The MCP request dictionary
            
        Returns:
            The response dictionary
        """
        try:
            # Extract request elements
            capability = request.get("capability")
            parameters = request.get("parameters", {})
            
            # Validate request
            if not capability:
                return {"error": "Missing capability in request"}
            
            if capability not in self.capabilities:
                return {"error": f"Unknown capability: {capability}"}
            
            # Route to appropriate handler
            if capability == "ollama_generate":
                return await self._handle_ollama_generate(parameters)
            elif capability == "ollama_chat":
                return await self._handle_ollama_chat(parameters)
            elif capability == "ollama_tags":
                return await self._handle_ollama_tags()
            elif capability == "ollama_memory_chat":
                return await self._handle_ollama_memory_chat(parameters)
            else:
                return {"error": f"Capability {capability} not implemented"}
        
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return {"error": f"Failed to process request: {str(e)}"}
    
    async def _handle_ollama_generate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an Ollama generate capability request.
        
        Args:
            parameters: Request parameters
            
        Returns:
            Result of the Ollama generate operation
        """
        # Extract parameters
        model = parameters.get("model")
        prompt = parameters.get("prompt")
        system = parameters.get("system")
        template = parameters.get("template")
        context = parameters.get("context")
        options = parameters.get("options", {})
        
        # Validate required parameters
        if not model:
            return {"error": "Missing required parameter: model"}
        if not prompt:
            return {"error": "Missing required parameter: prompt"}
        
        # Prepare the request body
        request_body = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        # Add optional parameters if provided
        if system:
            request_body["system"] = system
        if template:
            request_body["template"] = template
        if context:
            request_body["context"] = context
        if options:
            request_body["options"] = options
        
        # Make the API call asynchronously
        try:
            # Use asyncio to run the blocking request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(f"{self.api_url}/generate", json=request_body)
            )
            
            # Check for successful response
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": result.get("response", ""),
                    "model": model,
                    "total_duration": result.get("total_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0)
                }
            else:
                return {"error": f"Ollama API error: {response.status_code} - {response.text}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama generate API: {e}")
            return {"error": f"Failed to call Ollama API: {str(e)}"}
    
    async def _handle_ollama_chat(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an Ollama chat capability request.
        
        Args:
            parameters: Request parameters
            
        Returns:
            Result of the Ollama chat operation
        """
        # Extract parameters
        model = parameters.get("model")
        messages = parameters.get("messages")
        system = parameters.get("system")
        template = parameters.get("template")
        options = parameters.get("options", {})
        enable_memory = parameters.get("enable_memory", False)
        
        # Validate required parameters
        if not model:
            return {"error": "Missing required parameter: model"}
        if not messages:
            return {"error": "Missing required parameter: messages"}
        
        # Check if memory integration is requested but not available
        if enable_memory and not 'engram.cli.quickmem' in sys.modules:
            logger.warning("Memory integration requested but Engram memory not available")
            enable_memory = False
        
        # Prepare the request body
        request_body = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        # Add optional parameters if provided
        if system:
            request_body["system"] = system
        if template:
            request_body["template"] = template
        if options:
            request_body["options"] = options
        
        # Make the API call asynchronously
        try:
            # Use asyncio to run the blocking request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(f"{self.api_url}/chat", json=request_body)
            )
            
            # Check for successful response
            if response.status_code == 200:
                result = response.json()
                
                # If memory integration is enabled, store the conversation
                if enable_memory:
                    try:
                        from engram.cli.quickmem import m, run
                        
                        # Extract the last user message and the model response
                        last_user_msg = None
                        for msg in reversed(messages):
                            if msg.get("role") == "user":
                                last_user_msg = msg.get("content")
                                break
                        
                        model_response = result.get("message", {}).get("content", "")
                        
                        if last_user_msg and model_response:
                            memory_text = f"User asked: '{last_user_msg}' and {model} responded: '{model_response[:100]}...'"
                            await run(m(memory_text))
                            logger.info(f"Stored chat interaction in memory")
                    except Exception as e:
                        logger.error(f"Error storing chat in memory: {e}")
                
                return {
                    "message": result.get("message", {}),
                    "model": model,
                    "total_duration": result.get("total_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0)
                }
            else:
                return {"error": f"Ollama API error: {response.status_code} - {response.text}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama chat API: {e}")
            return {"error": f"Failed to call Ollama API: {str(e)}"}
    
    async def _handle_ollama_tags(self) -> Dict[str, Any]:
        """
        Handle an Ollama tags capability request.
        
        Returns:
            List of available Ollama models
        """
        try:
            # Use asyncio to run the blocking request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(f"{self.api_url}/tags")
            )
            
            # Check for successful response
            if response.status_code == 200:
                result = response.json()
                return {
                    "models": result.get("models", []),
                    "total": len(result.get("models", []))
                }
            else:
                return {"error": f"Ollama API error: {response.status_code} - {response.text}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama tags API: {e}")
            return {"error": f"Failed to call Ollama API: {str(e)}"}
    
    async def _handle_ollama_memory_chat(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an Ollama memory chat capability request.
        
        This integrates Ollama with Engram's memory system for enhanced contextual responses.
        
        Args:
            parameters: Request parameters
            
        Returns:
            Result of the Ollama memory chat operation
        """
        # Extract parameters
        model = parameters.get("model")
        messages = parameters.get("messages", [])
        system = parameters.get("system")
        client_id = parameters.get("client_id", "ollama")
        memory_prompt_type = parameters.get("memory_prompt_type", "combined")
        options = parameters.get("options", {})
        
        # Validate required parameters
        if not model:
            return {"error": "Missing required parameter: model"}
        
        # Import memory functionality
        try:
            from engram.cli.quickmem import m, k, c, v, run
            
            # Import MemoryHandler from ollama/ollama_bridge if available
            try:
                # Import using proper package path
                from engram.ollama.ollama_bridge import MemoryHandler
                memory_handler = MemoryHandler(client_id=client_id)
                logger.info("Successfully loaded MemoryHandler from engram.ollama.ollama_bridge")
            except ImportError:
                logger.warning("MemoryHandler from ollama/ollama_bridge.py not available, using simplified memory integration")
                memory_handler = None
        except ImportError:
            return {"error": "Engram memory system not available"}
        
        # Set up system prompt with memory capabilities if not provided
        if not system and SYSTEM_PROMPTS_AVAILABLE:
            if memory_prompt_type == "memory":
                system = get_memory_system_prompt(model)
            elif memory_prompt_type == "communication":
                system = get_communication_system_prompt(model)
            else:  # default to combined
                system = get_combined_system_prompt(model)
        
        # Enhance user messages with memory context if memory_handler is available
        if memory_handler:
            enhanced_messages = []
            for message in messages:
                if message.get("role") == "user":
                    content = message.get("content", "")
                    enhanced_content = memory_handler.enhance_prompt_with_memory(content)
                    if enhanced_content != content:
                        logger.info("Enhanced user message with memory context")
                        enhanced_messages.append({"role": message.get("role"), "content": enhanced_content})
                    else:
                        enhanced_messages.append(message)
                else:
                    enhanced_messages.append(message)
            messages = enhanced_messages
        
        # Prepare the request body
        request_body = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        # Add optional parameters if provided
        if system:
            request_body["system"] = system
        if options:
            request_body["options"] = options
        
        # Make the API call asynchronously
        try:
            # Use asyncio to run the blocking request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(f"{self.api_url}/chat", json=request_body)
            )
            
            # Check for successful response
            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "")
                
                # Process memory operations in response if memory_handler is available
                if memory_handler:
                    try:
                        cleaned_message, ops = memory_handler.detect_memory_operations(assistant_message)
                        
                        # If operations were detected, use the cleaned message
                        if ops:
                            result["message"]["content"] = cleaned_message
                            result["memory_operations"] = ops
                            
                            logger.info(f"Processed {len(ops)} memory operations in model response")
                    except Exception as e:
                        logger.error(f"Error processing memory operations: {e}")
                
                # Store significant interactions in memory
                try:
                    last_user_msg = None
                    for msg in reversed(messages):
                        if msg.get("role") == "user":
                            last_user_msg = msg.get("content")
                            break
                    
                    if last_user_msg and len(last_user_msg) > 20 and len(assistant_message) > 50:
                        memory_text = f"User asked: '{last_user_msg}' and {model} responded: '{assistant_message[:100]}...'"
                        await run(m(memory_text))
                except Exception as e:
                    logger.error(f"Error storing chat in memory: {e}")
                
                return {
                    "message": result.get("message", {}),
                    "model": model,
                    "total_duration": result.get("total_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                    "memory_enhanced": memory_handler is not None
                }
            else:
                return {"error": f"Ollama API error: {response.status_code} - {response.text}"}
        
        except Exception as e:
            logger.error(f"Error calling Ollama chat API: {e}")
            return {"error": f"Failed to call Ollama API: {str(e)}"}