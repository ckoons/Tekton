"""
Environment variable utilities for Tekton LLM Client.

This module provides utilities for managing environment variables
used by the Tekton LLM Client.
"""

import os
from shared.env import TektonEnviron
import json
import logging
from typing import Dict, List, Any, Optional, Union, TypeVar, Type, cast

logger = logging.getLogger(__name__)

# Environment variable prefix for Tekton LLM client
ENV_PREFIX = "TEKTON_LLM_"

def get_env(
    key: str, 
    default: Optional[str] = None,
    required: bool = False,
    use_prefix: bool = True
) -> Optional[str]:
    """
    Get a value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        use_prefix: Whether to add the Tekton prefix
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required and not found
    """
    if use_prefix and not key.startswith(ENV_PREFIX):
        key = f"{ENV_PREFIX}{key}"
        
    value = TektonEnviron.get(key)
    
    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' not found")
        return default
        
    return value

def get_env_bool(
    key: str, 
    default: Optional[bool] = None,
    required: bool = False,
    use_prefix: bool = True
) -> Optional[bool]:
    """
    Get a boolean value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        use_prefix: Whether to add the Tekton prefix
        
    Returns:
        Boolean value of environment variable or default
    """
    value = get_env(key, default=None, required=required, use_prefix=use_prefix)
    
    if value is None:
        return default
        
    return value.lower() in ('true', 'yes', '1', 'y', 'on')

def get_env_int(
    key: str, 
    default: Optional[int] = None,
    required: bool = False,
    use_prefix: bool = True
) -> Optional[int]:
    """
    Get an integer value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        use_prefix: Whether to add the Tekton prefix
        
    Returns:
        Integer value of environment variable or default
    """
    value = get_env(key, default=None, required=required, use_prefix=use_prefix)
    
    if value is None:
        return default
        
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Environment variable '{key}' is not a valid integer: {value}")
        return default

def get_env_float(
    key: str, 
    default: Optional[float] = None,
    required: bool = False,
    use_prefix: bool = True
) -> Optional[float]:
    """
    Get a float value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        use_prefix: Whether to add the Tekton prefix
        
    Returns:
        Float value of environment variable or default
    """
    value = get_env(key, default=None, required=required, use_prefix=use_prefix)
    
    if value is None:
        return default
        
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Environment variable '{key}' is not a valid float: {value}")
        return default

def get_env_list(
    key: str, 
    default: Optional[List[str]] = None,
    required: bool = False,
    use_prefix: bool = True,
    separator: str = ","
) -> Optional[List[str]]:
    """
    Get a list value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        use_prefix: Whether to add the Tekton prefix
        separator: Separator for splitting the string
        
    Returns:
        List value of environment variable or default
    """
    value = get_env(key, default=None, required=required, use_prefix=use_prefix)
    
    if value is None:
        return default
        
    if not value.strip():
        return []
        
    return [item.strip() for item in value.split(separator)]

def get_env_dict(
    key: str, 
    default: Optional[Dict[str, Any]] = None,
    required: bool = False,
    use_prefix: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get a dictionary value from environment variables.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        use_prefix: Whether to add the Tekton prefix
        
    Returns:
        Dictionary value of environment variable or default
    """
    value = get_env(key, default=None, required=required, use_prefix=use_prefix)
    
    if value is None:
        return default
        
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        logger.warning(f"Environment variable '{key}' is not valid JSON: {value}")
        return default

def set_env(key: str, value: Any, use_prefix: bool = True) -> None:
    """
    Set an environment variable.
    
    Args:
        key: Environment variable name
        value: Value to set
        use_prefix: Whether to add the Tekton prefix
    """
    if use_prefix and not key.startswith(ENV_PREFIX):
        key = f"{ENV_PREFIX}{key}"
        
    # Convert value to string
    if value is None:
        str_value = ""
    elif isinstance(value, (dict, list)):
        str_value = json.dumps(value)
    else:
        str_value = str(value)
        
    TektonEnviron.set(key, str_value)

def has_env(key: str, use_prefix: bool = True) -> bool:
    """
    Check if an environment variable exists.
    
    Args:
        key: Environment variable name
        use_prefix: Whether to add the Tekton prefix
        
    Returns:
        True if environment variable exists, False otherwise
    """
    if use_prefix and not key.startswith(ENV_PREFIX):
        key = f"{ENV_PREFIX}{key}"
        
    return key in os.environ