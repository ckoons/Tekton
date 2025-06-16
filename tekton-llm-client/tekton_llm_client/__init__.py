"""
Tekton LLM Client - A unified client library for LLM integration in Tekton components.

This package provides a standardized way to interact with LLMs through the Rhetor component,
along with utilities for prompt templates, response parsing, and configuration.
"""

from .client import TektonLLMClient
from .ws_client import TektonLLMWebSocketClient
from .exceptions import TektonLLMError, ConnectionError, TimeoutError, AuthenticationError

# Import new modules
from .prompt_templates import PromptTemplateRegistry, PromptTemplate, load_template
from .response_handlers import (
    JSONParser, parse_json, extract_json,
    StreamHandler, collect_stream, stream_to_string,
    StructuredOutputParser, OutputFormat, FormatError
)
from .config import (
    get_env, get_env_bool, get_env_int, get_env_float, 
    get_env_list, get_env_dict, set_env, has_env,
    LLMSettings, ClientSettings, load_settings, 
    save_settings, get_default_settings
)

# Aliases for backward compatibility
Client = TektonLLMClient

__version__ = '0.2.0'
__all__ = [
    # Core clients
    'TektonLLMClient', 'TektonLLMWebSocketClient', 'Client',
    
    # Exceptions
    'TektonLLMError', 'ConnectionError', 'TimeoutError', 'AuthenticationError', 'FormatError',
    
    # Prompt templates
    'PromptTemplateRegistry', 'PromptTemplate', 'load_template',
    
    # Response handlers
    'JSONParser', 'parse_json', 'extract_json',
    'StreamHandler', 'collect_stream', 'stream_to_string',
    'StructuredOutputParser', 'OutputFormat',
    
    # Configuration
    'get_env', 'get_env_bool', 'get_env_int', 'get_env_float',
    'get_env_list', 'get_env_dict', 'set_env', 'has_env',
    'LLMSettings', 'ClientSettings', 'load_settings',
    'save_settings', 'get_default_settings'
]