"""
Settings management utilities for Tekton LLM Client.

This module provides utilities for managing configuration settings from
files and default values.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, TypeVar, Type, cast
from pydantic import BaseModel, Field, ConfigDict

from .environment import (
    get_env, get_env_bool, get_env_int, get_env_float, 
    get_env_list, get_env_dict
)

try:
    from shared.urls import rhetor_url as get_rhetor_url
except ImportError:
    get_rhetor_url = None

logger = logging.getLogger(__name__)

class LLMSettings(BaseModel):
    """Settings for LLM configuration."""
    
    # Provider and model settings
    provider: str = Field(default="anthropic", description="Default LLM provider")
    model: Optional[str] = Field(default=None, description="Default model for the provider")
    
    # Connection settings
    rhetor_url: str = Field(
        default_factory=lambda: get_rhetor_url("") if get_rhetor_url else "http://localhost:8003",
        description="URL for the Rhetor service"
    )
    timeout: int = Field(default=120, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries for failed requests")
    retry_delay: int = Field(default=1000, description="Base delay between retries in milliseconds")
    use_fallback: bool = Field(default=True, description="Whether to use fallback when Rhetor is unavailable")
    auth_token: Optional[str] = Field(default=None, description="Authentication token for Rhetor API")

    # Generation settings
    temperature: float = Field(default=0.7, description="Temperature for text generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum number of tokens to generate")
    stop_sequences: Optional[List[str]] = Field(default=None, description="Sequences that stop generation")
    top_p: Optional[float] = Field(default=None, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(default=None, description="Top-k sampling parameter")
    presence_penalty: Optional[float] = Field(default=None, description="Presence penalty parameter")
    frequency_penalty: Optional[float] = Field(default=None, description="Frequency penalty parameter")
    
    # System settings
    templates_dir: Optional[str] = Field(default=None, description="Directory for prompt templates")
    fallback_provider: Optional[str] = Field(default=None, description="Fallback provider to use")
    fallback_model: Optional[str] = Field(default=None, description="Fallback model to use")
    
    model_config = ConfigDict(extra='allow', env_prefix='TEKTON_LLM_')

class ClientSettings(BaseModel):
    """Settings for Tekton LLM Client."""
    
    # Client identification
    component_id: str = Field(..., description="ID of the component using the client")
    version: str = Field(default="0.1.0", description="Version of the settings")
    
    # LLM settings
    llm: LLMSettings = Field(default_factory=LLMSettings, description="LLM configuration settings")
    
    # Component-specific settings
    context_id: Optional[str] = Field(default=None, description="Context ID for tracking conversations")
    additional_options: Dict[str, Any] = Field(default_factory=dict, description="Additional component-specific options")
    
    model_config = ConfigDict(extra='allow')

def load_settings(
    component_id: str,
    file_path: Optional[str] = None,
    load_from_env: bool = True
) -> ClientSettings:
    """
    Load settings from a file and/or environment variables.
    
    Args:
        component_id: ID of the component using the client
        file_path: Path to a JSON file with settings
        load_from_env: Whether to load settings from environment variables
        
    Returns:
        ClientSettings object with merged settings
    """
    # Start with default settings
    settings = get_default_settings(component_id)
    
    # Load from file if specified
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                file_settings = json.load(f)
                
            # Merge with existing settings
            settings = ClientSettings(**{**settings.model_dump(), **file_settings})
            
        except Exception as e:
            logger.error(f"Error loading settings from {file_path}: {str(e)}")
    
    # Load from environment variables if requested
    if load_from_env:
        env_settings = _load_settings_from_env()
        
        # Merge with existing settings
        if env_settings:
            # Convert env_settings to a nested dictionary structure
            nested_settings = {}
            
            for key, value in env_settings.items():
                if key.startswith("llm_"):
                    # Handle LLM settings
                    llm_key = key[4:]  # Remove the "llm_" prefix
                    if "llm" not in nested_settings:
                        nested_settings["llm"] = {}
                    nested_settings["llm"][llm_key] = value
                else:
                    # Handle top-level settings
                    nested_settings[key] = value
            
            # Override the component_id
            nested_settings["component_id"] = component_id
            
            # Merge the settings
            current_dict = settings.model_dump()
            merged_dict = _deep_merge(current_dict, nested_settings)
            
            # Create a new settings object
            settings = ClientSettings(**merged_dict)
    
    return settings

def save_settings(settings: ClientSettings, file_path: str) -> bool:
    """
    Save settings to a file.
    
    Args:
        settings: Settings object to save
        file_path: Path to a JSON file to save to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(settings.model_dump(), f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving settings to {file_path}: {str(e)}")
        return False

def get_default_settings(component_id: str) -> ClientSettings:
    """
    Get default settings for a component.
    
    Args:
        component_id: ID of the component
        
    Returns:
        ClientSettings object with default settings
    """
    return ClientSettings(
        component_id=component_id,
        llm=LLMSettings(),
        context_id=component_id
    )

def _load_settings_from_env() -> Dict[str, Any]:
    """
    Load settings from environment variables.
    
    Returns:
        Dictionary of settings from environment variables
    """
    settings = {}
    
    # Load LLM provider settings
    provider = get_env("PROVIDER")
    if provider:
        settings["llm_provider"] = provider
        
    model = get_env("MODEL")
    if model:
        settings["llm_model"] = model
    
    # Load connection settings
    rhetor_url = get_env("RHETOR_URL")
    if rhetor_url:
        settings["llm_rhetor_url"] = rhetor_url
        
    timeout = get_env_int("TIMEOUT")
    if timeout is not None:
        settings["llm_timeout"] = timeout
        
    max_retries = get_env_int("MAX_RETRIES")
    if max_retries is not None:
        settings["llm_max_retries"] = max_retries
        
    use_fallback = get_env_bool("USE_FALLBACK")
    if use_fallback is not None:
        settings["llm_use_fallback"] = use_fallback
        
    auth_token = get_env("AUTH_TOKEN")
    if auth_token:
        settings["llm_auth_token"] = auth_token
    
    # Load generation settings
    temperature = get_env_float("TEMPERATURE")
    if temperature is not None:
        settings["llm_temperature"] = temperature
        
    max_tokens = get_env_int("MAX_TOKENS")
    if max_tokens is not None:
        settings["llm_max_tokens"] = max_tokens
        
    stop_sequences = get_env_list("STOP_SEQUENCES")
    if stop_sequences is not None:
        settings["llm_stop_sequences"] = stop_sequences
    
    # Load system settings
    templates_dir = get_env("TEMPLATES_DIR")
    if templates_dir:
        settings["llm_templates_dir"] = templates_dir
        
    fallback_provider = get_env("FALLBACK_PROVIDER")
    if fallback_provider:
        settings["llm_fallback_provider"] = fallback_provider
        
    fallback_model = get_env("FALLBACK_MODEL")
    if fallback_model:
        settings["llm_fallback_model"] = fallback_model
    
    return settings

def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge in (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _deep_merge(result[key], value)
        else:
            # Otherwise, use the value from dict2
            result[key] = value
            
    return result