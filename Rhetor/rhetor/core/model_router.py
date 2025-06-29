"""
Model router for selecting appropriate LLM models based on task requirements.

This module provides a router that selects the optimal LLM model for different tasks,
with budget awareness to control costs.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Support both old and new LLM clients during migration
try:
    from .llm_client_unified import LLMClient
except ImportError:
    from .llm_client import LLMClient
from .budget_manager import BudgetManager

logger = logging.getLogger(__name__)

class ModelRouter:
    """Routes LLM requests to the appropriate model based on task requirements and budget constraints"""
    
    def __init__(self, llm_client: LLMClient, budget_manager: Optional[BudgetManager] = None):
        """
        Initialize the model router.
        
        Args:
            llm_client: LLM client instance
            budget_manager: Optional budget manager for cost-aware routing
        """
        self.llm_client = llm_client
        self.task_configs = self._load_task_configs()
        self.budget_manager = budget_manager or BudgetManager()
        
    def _load_task_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load task configuration for model routing.
        Supports both old provider-based and new role-based configs.
        
        Returns:
            Dictionary of task configurations
        """
        # Check for unified config first, then fall back to old config
        config_dir = Path(__file__).parent.parent / "config"
        unified_config = config_dir / "tasks_unified.json"
        old_config = config_dir / "tasks.json"
        
        config_file = os.environ.get("RHETOR_TASK_CONFIG")
        if not config_file:
            # Prefer unified config if it exists
            if unified_config.exists():
                config_file = str(unified_config)
            else:
                config_file = str(old_config)
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    configs = json.load(f)
                    logger.info(f"Loaded task configurations from {config_file}")
                    return configs
        except Exception as e:
            logger.warning(f"Error loading task config from {config_file}: {e}")
        
        # Default configurations if file not found
        return {
            "code": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "options": {
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "fallback_provider": "openai",
                    "fallback_model": "gpt-4-turbo"
                }
            },
            "planning": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "fallback_provider": "openai",
                    "fallback_model": "gpt-4o"
                }
            },
            "reasoning": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "options": {
                    "temperature": 0.5,
                    "max_tokens": 4000,
                    "fallback_provider": "openai",
                    "fallback_model": "gpt-4o"
                }
            },
            "chat": {
                "provider": "anthropic",
                "model": "claude-3-haiku-20240307",
                "options": {
                    "temperature": 0.8,
                    "max_tokens": 2000,
                    "fallback_provider": "openai",
                    "fallback_model": "gpt-3.5-turbo"
                }
            },
            "default": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "fallback_provider": "openai",
                    "fallback_model": "gpt-4o"
                }
            }
        }
    
    def get_config_for_task(
        self, 
        task_type: str = "default", 
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the appropriate model configuration for a task.
        Supports both old provider-based and new role-based configs.
        
        Args:
            task_type: Type of task (code, planning, reasoning, chat, etc.)
            component: Optional component name for component-specific config
            
        Returns:
            Dictionary with model configuration
        """
        # Look for component-specific configuration first
        if component:
            # Try component_task (e.g., "ergon_code")
            component_key = f"{component}_{task_type}"
            if component_key in self.task_configs:
                return self.task_configs[component_key]
            
            # Try component (e.g., "ergon")
            if component in self.task_configs:
                return self.task_configs[component]
        
        # Try task type (e.g., "code")
        if task_type in self.task_configs:
            return self.task_configs[task_type]
        
        # Fall back to default
        return self.task_configs["default"]
    
    async def route_request(
        self,
        message: str,
        context_id: str,
        task_type: str = "default",
        component: Optional[str] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = False,
        override_config: Optional[Dict[str, Any]] = None
    ):
        """
        Route a request to the appropriate model with budget awareness.
        
        Args:
            message: User message
            context_id: Context ID for tracking conversation
            task_type: Type of task (code, planning, reasoning, chat, etc.)
            component: Optional component name for component-specific config
            system_prompt: Optional system prompt
            streaming: Whether to stream the response
            override_config: Optional configuration overrides
            
        Returns:
            Response from the LLM
        """
        # Get the configuration
        config = self.get_config_for_task(task_type, component)
        
        # Apply overrides if provided
        if override_config:
            # Deep merge options
            if "options" in override_config and "options" in config:
                merged_options = {**config["options"], **override_config.get("options", {})}
                override_config["options"] = merged_options
            
            # Merge the rest
            config = {**config, **override_config}
        
        # Get the configuration - handle both old and new formats
        if "role" in config:
            # New role-based format
            role = config.get("role", "general")
            provider_id = None  # Let the unified client decide
            model_id = None  # Let the unified client decide
            options = config.get("options", {})
            # Add role and task_type to options for unified client
            options["role"] = role
            options["task_type"] = task_type
        else:
            # Old provider-based format
            provider_id = config.get("provider")
            model_id = config.get("model")
            options = config.get("options", {})
        
        # Budget awareness - check if this model is within budget and get alternatives if needed
        budget_warnings = []
        component_id = component or context_id.split(":")[0] if ":" in context_id else "unknown"
        
        # Only apply budget awareness if not explicitly bypassed via options
        if not options.get("bypass_budget", False):
            # Input for cost estimation is message + system prompt if any
            input_text = message
            if system_prompt:
                input_text = system_prompt + "\n\n" + message
                
            # Get budget-aware provider and model
            provider_id, model_id, budget_warnings = self.budget_manager.route_with_budget_awareness(
                input_text=input_text,
                task_type=task_type,
                default_provider=provider_id,
                default_model=model_id,
                component=component_id
            )
            
            # Log any budget warnings
            for warning in budget_warnings:
                logger.warning(f"Budget warning: {warning}")
                
            # Add budget warnings to options for return to client
            if budget_warnings:
                options["budget_warnings"] = budget_warnings
        
        # Record the completion in budget tracker after request finishes
        async def track_completion(response):
            if "message" in response and not response.get("error"):
                self.budget_manager.record_completion(
                    provider=provider_id,
                    model=model_id,
                    input_text=message,
                    output_text=response["message"],
                    component=component_id,
                    task_type=task_type,
                    metadata={
                        "context_id": context_id,
                        "streaming": streaming,
                        "system_prompt_length": len(system_prompt) if system_prompt else 0,
                    }
                )
            return response
        
        if streaming:
            # For streaming, we can't track completion here, it happens in the API layer
            return self.llm_client.stream_completion(
                message=message,
                context_id=context_id,
                system_prompt=system_prompt,
                provider_id=provider_id,
                model_id=model_id,
                options=options
            )
        else:
            # For non-streaming, track completion and cost
            response = await self.llm_client.complete(
                message=message,
                context_id=context_id,
                system_prompt=system_prompt,
                provider_id=provider_id,
                model_id=model_id,
                streaming=streaming,
                options=options
            )
            
            # Track completion after request is done
            return await track_completion(response)
    
    async def route_chat_request(
        self,
        messages: List[Dict[str, str]],
        context_id: str,
        task_type: str = "default",
        component: Optional[str] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = False,
        override_config: Optional[Dict[str, Any]] = None
    ):
        """
        Route a chat request to the appropriate model with budget awareness.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            context_id: Context ID for tracking conversation
            task_type: Type of task (code, planning, reasoning, chat, etc.)
            component: Optional component name for component-specific config
            system_prompt: Optional system prompt
            streaming: Whether to stream the response
            override_config: Optional configuration overrides
            
        Returns:
            Response from the LLM
        """
        # Get the configuration
        config = self.get_config_for_task(task_type, component)
        
        # Apply overrides if provided
        if override_config:
            # Deep merge options
            if "options" in override_config and "options" in config:
                merged_options = {**config["options"], **override_config.get("options", {})}
                override_config["options"] = merged_options
            
            # Merge the rest
            config = {**config, **override_config}
        
        # Get the configuration - handle both old and new formats
        if "role" in config:
            # New role-based format
            role = config.get("role", "general")
            provider_id = None  # Let the unified client decide
            model_id = None  # Let the unified client decide
            options = config.get("options", {})
            # Add role and task_type to options for unified client
            options["role"] = role
            options["task_type"] = task_type
        else:
            # Old provider-based format
            provider_id = config.get("provider")
            model_id = config.get("model")
            options = config.get("options", {})
        
        # Budget awareness - check if this model is within budget and get alternatives if needed
        budget_warnings = []
        component_id = component or context_id.split(":")[0] if ":" in context_id else "unknown"
        
        # Only apply budget awareness if not explicitly bypassed via options
        if not options.get("bypass_budget", False):
            # Convert messages to a single string for cost estimation
            combined_input = ""
            if system_prompt:
                combined_input += system_prompt + "\n\n"
                
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                combined_input += f"{role}: {content}\n"
                
            # Get budget-aware provider and model
            provider_id, model_id, budget_warnings = self.budget_manager.route_with_budget_awareness(
                input_text=combined_input,
                task_type=task_type,
                default_provider=provider_id,
                default_model=model_id,
                component=component_id
            )
            
            # Log any budget warnings
            for warning in budget_warnings:
                logger.warning(f"Budget warning: {warning}")
                
            # Add budget warnings to options for return to client
            if budget_warnings:
                options["budget_warnings"] = budget_warnings
        
        # Record the completion in budget tracker after request finishes
        async def track_completion(response):
            if "message" in response and not response.get("error"):
                # For chat completion, we use the combined messages as input
                combined_input = ""
                for message in messages:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    combined_input += f"{role}: {content}\n"
                
                self.budget_manager.record_completion(
                    provider=provider_id,
                    model=model_id,
                    input_text=combined_input,
                    output_text=response["message"],
                    component=component_id,
                    task_type=task_type,
                    metadata={
                        "context_id": context_id,
                        "streaming": streaming,
                        "message_count": len(messages),
                        "system_prompt_length": len(system_prompt) if system_prompt else 0,
                    }
                )
            return response
        
        if streaming:
            # For streaming, we can't track completion here, it happens in the API layer
            return self.llm_client.chat_stream(
                messages=messages,
                context_id=context_id,
                system_prompt=system_prompt,
                provider_id=provider_id,
                model_id=model_id,
                options=options
            )
        else:
            # For non-streaming, track completion and cost
            response = await self.llm_client.chat_complete(
                messages=messages,
                context_id=context_id,
                system_prompt=system_prompt,
                provider_id=provider_id,
                model_id=model_id,
                streaming=streaming,
                options=options
            )
            
            # Track completion after request is done
            return await track_completion(response)