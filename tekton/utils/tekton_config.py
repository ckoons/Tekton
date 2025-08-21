"""
Tekton Configuration Management

This module provides a standardized way to handle configuration for Tekton components.
It supports loading from environment variables, config files, and default values with
type validation and schema checking.

Usage:
    from tekton.utils.tekton_config import TektonConfig, config_from_env

    # Using the class-based interface
    config = TektonConfig("mycomponent")
    config.load_defaults({
        "port": 8000,
        "log_level": "INFO",
    })
    config.load_from_env()
    port = config.get("port")
    
    # Using the function-based interface
    port = config_from_env("MYCOMPONENT_PORT", default=8000, value_type=int)
"""

import os
from shared.env import TektonEnviron
import sys
import json
import yaml
import logging
from pathlib import Path
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TypeVar, Type, cast, Callable, Set, Tuple

# Set up logger
logger = logging.getLogger(__name__)

# Type variable for generic type constraints
T = TypeVar('T')


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigNotFoundError(Exception):
    """Raised when a required configuration file is not found."""
    pass


class ConfigParseError(Exception):
    """Raised when configuration parsing fails."""
    pass


class ConfigValueType(Enum):
    """Supported configuration value types."""
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    

class TektonConfig:
    """
    Configuration management for Tekton components.
    
    This class provides a unified interface for loading and accessing
    configuration from different sources with validation.
    """
    
    def __init__(
        self,
        component_id: str,
        config_file: Optional[str] = None,
        env_prefix: Optional[str] = None,
        auto_load: bool = True
    ):
        """
        Initialize configuration manager.
        
        Args:
            component_id: Component identifier (used for logging and defaults)
            config_file: Optional path to a config file (JSON or YAML)
            env_prefix: Prefix for environment variables (defaults to component_id.upper())
            auto_load: Whether to automatically load config from env and file
        """
        self.component_id = component_id
        self.config_file = config_file
        self.env_prefix = env_prefix or component_id.upper()
        self.config_data: Dict[str, Any] = {}
        self.schema: Dict[str, Dict[str, Any]] = {}
        
        if auto_load:
            # Load configuration in priority order: defaults -> file -> env
            self._load_defaults()
            
            if config_file:
                self.load_from_file(config_file)
                
            self.load_from_env()
    
    def _load_defaults(self) -> None:
        """Load default configuration based on component ID."""
        # Common defaults for all components
        common_defaults = {
            "log_level": "INFO",
            "debug": False,
        }
        
        # Component-specific defaults based on component_id
        component_defaults: Dict[str, Any] = {}
        
        # Standard port assignments from Single Port Architecture
        port_defaults = {
            "engram": 8000,
            "hermes": 8001,
            "ergon": 8002,
            "rhetor": 8003,
            "terma": 8004,
            "athena": 8005,
            "prometheus": 8006,
            "harmonia": 8007,
            "telos": 8008,
            "synthesis": 8009,
            "tekton_core": 8010,
            "hephaestus": 8080
        }
        
        # Set port if component is in standard list
        if self.component_id.lower() in port_defaults:
            component_defaults["port"] = port_defaults[self.component_id.lower()]
        
        # Merge defaults into config data
        self.config_data.update(common_defaults)
        self.config_data.update(component_defaults)
    
    def set_schema(self, schema: Dict[str, Dict[str, Any]]) -> None:
        """
        Set configuration schema with validation rules.
        
        Args:
            schema: Dictionary mapping config keys to their validation schema
                   Example: {"port": {"type": "int", "required": True, "min": 1024, "max": 65535}}
        """
        self.schema = schema
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file (JSON or YAML).
        
        Args:
            file_path: Path to the configuration file
            
        Raises:
            ConfigNotFoundError: If file does not exist
            ConfigParseError: If file parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise ConfigNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Parse based on file extension
                if file_path.endswith('.json'):
                    loaded_data = json.loads(content)
                elif file_path.endswith(('.yml', '.yaml')):
                    loaded_data = yaml.safe_load(content)
                else:
                    # Try JSON first, then YAML
                    try:
                        loaded_data = json.loads(content)
                    except json.JSONDecodeError:
                        loaded_data = yaml.safe_load(content)
                
                # Ensure we have a dictionary
                if not isinstance(loaded_data, dict):
                    raise ConfigParseError(
                        f"Configuration file must contain a dictionary, got {type(loaded_data)}")
                
                # Update config data with loaded values
                self.config_data.update(loaded_data)
                logger.debug(f"Loaded configuration from {file_path}")
                
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigParseError(f"Failed to parse configuration file {file_path}: {e}")
        except Exception as e:
            raise ConfigParseError(f"Error loading configuration from {file_path}: {e}")
    
    def load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        Environment variables are expected to be in the format PREFIX_KEY.
        For example, with prefix "MYCOMPONENT", environment variable
        "MYCOMPONENT_PORT" will set the "port" config key.
        """
        prefix = f"{self.env_prefix}_"
        loaded = False
        
        # Load all environment variables with the specified prefix
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert env var name to config key (e.g., MYCOMPONENT_PORT -> port)
                config_key = key[len(prefix):].lower()
                
                # Skip empty keys
                if not config_key:
                    continue
                
                # Parse value based on schema or guess type
                if config_key in self.schema and "type" in self.schema[config_key]:
                    value_type = self.schema[config_key]["type"]
                    parsed_value = self._parse_value(value, value_type)
                else:
                    # Guess type if not in schema
                    parsed_value = self._guess_value_type(value)
                
                # Set config value
                self.config_data[config_key] = parsed_value
                loaded = True
        
        if loaded:
            logger.debug(f"Loaded configuration from environment variables with prefix {prefix}")
    
    def load_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Load default values for configuration.
        
        Args:
            defaults: Dictionary of default configuration values
        """
        # Only set values that aren't already set
        for key, value in defaults.items():
            if key not in self.config_data:
                self.config_data[key] = value
                
        logger.debug("Loaded default configuration values")
    
    def _parse_value(self, value: str, value_type: str) -> Any:
        """
        Parse a string value into the specified type.
        
        Args:
            value: String value to parse
            value_type: Type to parse to (string, int, float, bool, list, dict)
            
        Returns:
            Parsed value
            
        Raises:
            ConfigValidationError: If parsing fails
        """
        try:
            if value_type == "string" or value_type == str:
                return value
            elif value_type == "int" or value_type == int:
                return int(value)
            elif value_type == "float" or value_type == float:
                return float(value)
            elif value_type == "bool" or value_type == bool:
                return value.lower() in ("true", "yes", "1", "y", "t")
            elif value_type == "list" or value_type == list:
                import ast
                return ast.literal_eval(value)
            elif value_type == "dict" or value_type == dict:
                import ast
                return ast.literal_eval(value)
            else:
                raise ConfigValidationError(f"Unsupported value type: {value_type}")
        except (ValueError, SyntaxError) as e:
            raise ConfigValidationError(f"Failed to parse value '{value}' as {value_type}: {e}")
    
    def _guess_value_type(self, value: str) -> Any:
        """
        Guess and convert the type of a string value.
        
        Args:
            value: String value to parse
            
        Returns:
            Parsed value with guessed type
        """
        # Check for boolean values
        if value.lower() in ("true", "false", "yes", "no", "y", "n", "t", "f"):
            return value.lower() in ("true", "yes", "y", "t", "1")
        
        # Check for integer
        try:
            int_val = int(value)
            return int_val
        except ValueError:
            pass
        
        # Check for float
        try:
            float_val = float(value)
            return float_val
        except ValueError:
            pass
        
        # Check for list or dict
        if (value.startswith("[") and value.endswith("]")) or (value.startswith("{") and value.endswith("}")):
            try:
                import ast
                return ast.literal_eval(value)
            except (SyntaxError, ValueError):
                pass
        
        # Default to string
        return value
    
    def get(self, key: str, default: Optional[T] = None) -> T:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
            
        Raises:
            KeyError: If key is not found and no default provided
            ConfigValidationError: If validation fails
        """
        # Check if key exists in config data
        if key in self.config_data:
            value = self.config_data[key]
            
            # Validate if schema is defined
            if key in self.schema:
                value = self._validate_value(key, value, self.schema[key])
                
            # Cast to expected type from default if provided
            if default is not None and value is not None:
                try:
                    # This is a best-effort conversion, might fail for complex types
                    if isinstance(default, (int, float, bool, str)):
                        return type(default)(value)  # type: ignore
                except (ValueError, TypeError):
                    pass
                
            return cast(T, value)
        
        # Check if key has a default in schema
        if key in self.schema and "default" in self.schema[key]:
            return cast(T, self.schema[key]["default"])
        
        # Use provided default or raise error
        if default is not None:
            return default
            
        # Required key missing
        if key in self.schema and self.schema[key].get("required", False):
            raise KeyError(f"Required configuration key not found: {key}")
            
        # Non-required key missing with no default
        raise KeyError(f"Configuration key not found: {key}")
    
    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """
        Get an integer configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Integer configuration value
            
        Raises:
            ConfigValidationError: If value is not an integer
        """
        value = self.get(key, default)
        
        if not isinstance(value, int):
            try:
                return int(value)  # type: ignore
            except (ValueError, TypeError):
                raise ConfigValidationError(f"Expected integer for key {key}, got {type(value)}")
                
        return value
    
    def get_float(self, key: str, default: Optional[float] = None) -> float:
        """
        Get a float configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Float configuration value
            
        Raises:
            ConfigValidationError: If value is not a float
        """
        value = self.get(key, default)
        
        if not isinstance(value, (float, int)):
            try:
                return float(value)  # type: ignore
            except (ValueError, TypeError):
                raise ConfigValidationError(f"Expected float for key {key}, got {type(value)}")
                
        return float(value)
    
    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """
        Get a boolean configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Boolean configuration value
            
        Raises:
            ConfigValidationError: If value cannot be converted to boolean
        """
        value = self.get(key, default)
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "y", "t")
        
        raise ConfigValidationError(f"Cannot convert value for key {key} to boolean: {value}")
    
    def get_str(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a string configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            String configuration value
        """
        value = self.get(key, default)
        return str(value)
    
    def get_list(self, key: str, default: Optional[List[Any]] = None) -> List[Any]:
        """
        Get a list configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            List configuration value
            
        Raises:
            ConfigValidationError: If value is not a list
        """
        value = self.get(key, default)
        
        if not isinstance(value, list):
            raise ConfigValidationError(f"Expected list for key {key}, got {type(value)}")
            
        return value
    
    def get_dict(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a dictionary configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Dictionary configuration value
            
        Raises:
            ConfigValidationError: If value is not a dictionary
        """
        value = self.get(key, default)
        
        if not isinstance(value, dict):
            raise ConfigValidationError(f"Expected dictionary for key {key}, got {type(value)}")
            
        return value
    
    def _validate_value(self, key: str, value: Any, schema: Dict[str, Any]) -> Any:
        """
        Validate a configuration value against its schema.
        
        Args:
            key: Configuration key
            value: Value to validate
            schema: Validation schema
            
        Returns:
            Validated value (may be converted to correct type)
            
        Raises:
            ConfigValidationError: If validation fails
        """
        # Check type
        if "type" in schema:
            value_type = schema["type"]
            
            # String type validation
            if value_type in ("string", str):
                if not isinstance(value, str):
                    value = str(value)
                    
                # Check min/max length
                if "min_length" in schema and len(value) < schema["min_length"]:
                    raise ConfigValidationError(
                        f"Value for {key} is too short (min length: {schema['min_length']})")
                    
                if "max_length" in schema and len(value) > schema["max_length"]:
                    raise ConfigValidationError(
                        f"Value for {key} is too long (max length: {schema['max_length']})")
                    
            # Numeric type validation
            elif value_type in ("int", int):
                if not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        raise ConfigValidationError(f"Expected integer for key {key}, got {type(value)}")
                        
                # Check min/max value
                if "min" in schema and value < schema["min"]:
                    raise ConfigValidationError(
                        f"Value for {key} is too small (min: {schema['min']})")
                    
                if "max" in schema and value > schema["max"]:
                    raise ConfigValidationError(
                        f"Value for {key} is too large (max: {schema['max']})")
                    
            elif value_type in ("float", float):
                if not isinstance(value, (float, int)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        raise ConfigValidationError(f"Expected float for key {key}, got {type(value)}")
                        
                # Check min/max value
                if "min" in schema and value < schema["min"]:
                    raise ConfigValidationError(
                        f"Value for {key} is too small (min: {schema['min']})")
                    
                if "max" in schema and value > schema["max"]:
                    raise ConfigValidationError(
                        f"Value for {key} is too large (max: {schema['max']})")
                    
            # Boolean type validation
            elif value_type in ("bool", bool):
                if not isinstance(value, bool):
                    if isinstance(value, str):
                        value = value.lower() in ("true", "yes", "1", "y", "t")
                    else:
                        try:
                            value = bool(value)
                        except (ValueError, TypeError):
                            raise ConfigValidationError(f"Expected boolean for key {key}, got {type(value)}")
                            
            # List type validation
            elif value_type in ("list", list):
                if not isinstance(value, list):
                    raise ConfigValidationError(f"Expected list for key {key}, got {type(value)}")
                    
                # Check min/max length
                if "min_length" in schema and len(value) < schema["min_length"]:
                    raise ConfigValidationError(
                        f"List for {key} is too short (min length: {schema['min_length']})")
                    
                if "max_length" in schema and len(value) > schema["max_length"]:
                    raise ConfigValidationError(
                        f"List for {key} is too long (max length: {schema['max_length']})")
                    
                # Check items if specified
                if "items" in schema and value:
                    item_schema = schema["items"]
                    for i, item in enumerate(value):
                        try:
                            # Create a temporary schema for the item
                            temp_item_schema = {"item": item_schema}
                            self._validate_value(f"{key}[{i}]", item, temp_item_schema)
                        except ConfigValidationError as e:
                            raise ConfigValidationError(f"Invalid item in list {key} at index {i}: {e}")
                            
            # Dict type validation
            elif value_type in ("dict", dict):
                if not isinstance(value, dict):
                    raise ConfigValidationError(f"Expected dictionary for key {key}, got {type(value)}")
                    
                # Check required keys
                if "required_keys" in schema:
                    missing_keys = set(schema["required_keys"]) - set(value.keys())
                    if missing_keys:
                        raise ConfigValidationError(
                            f"Dictionary for {key} missing required keys: {', '.join(missing_keys)}")
                            
                # Check properties if specified
                if "properties" in schema:
                    for prop_key, prop_schema in schema["properties"].items():
                        if prop_key in value:
                            try:
                                value[prop_key] = self._validate_value(
                                    f"{key}.{prop_key}", value[prop_key], prop_schema)
                            except ConfigValidationError as e:
                                raise ConfigValidationError(
                                    f"Invalid property {prop_key} in dictionary {key}: {e}")
                                    
        # Check enum values
        if "enum" in schema and value not in schema["enum"]:
            raise ConfigValidationError(
                f"Value for {key} must be one of: {', '.join(map(str, schema['enum']))}")
                
        # Check custom validation function
        if "validator" in schema and callable(schema["validator"]):
            try:
                result = schema["validator"](value)
                if result is not True:
                    raise ConfigValidationError(f"Validation failed for {key}: {result}")
            except Exception as e:
                if isinstance(e, ConfigValidationError):
                    raise
                raise ConfigValidationError(f"Validation error for {key}: {e}")
                
        return value
    
    def validate(self) -> List[str]:
        """
        Validate all configuration values against their schema.
        
        Returns:
            List of validation error messages (empty if validation successful)
        """
        errors = []
        
        # Check all schema keys
        for key, schema in self.schema.items():
            # Skip non-required keys that are not present
            if key not in self.config_data and not schema.get("required", False):
                continue
                
            try:
                # Get value with validation
                self.get(key)
            except (KeyError, ConfigValidationError) as e:
                errors.append(str(e))
                
        return errors
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Get all configuration values as a dictionary.
        
        Returns:
            Dictionary of all configuration values
        """
        return self.config_data.copy()
    
    def update(self, values: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            values: Dictionary of configuration values to update
        """
        for key, value in values.items():
            self.config_data[key] = value


# Convenience functions

def config_from_env(
    env_var: str,
    default: Optional[T] = None,
    value_type: Optional[Type] = None,
    required: bool = False
) -> T:
    """
    Get a configuration value from an environment variable.
    
    Args:
        env_var: Environment variable name
        default: Default value if not found
        value_type: Type to convert value to
        required: Whether the environment variable is required
        
    Returns:
        Environment variable value (converted if value_type specified)
        
    Raises:
        ConfigValidationError: If required and not found, or conversion fails
    """
    # Check if environment variable exists
    value = TektonEnviron.get(env_var)
    
    if value is None:
        if required:
            raise ConfigValidationError(f"Required environment variable not found: {env_var}")
        return cast(T, default)
    
    # No conversion needed for strings or if no type specified
    if value_type is None or value_type == str:
        return cast(T, value if value is not None else default)
    
    # Convert to specified type
    try:
        if value_type == int:
            return cast(T, int(value))
        elif value_type == float:
            return cast(T, float(value))
        elif value_type == bool:
            return cast(T, value.lower() in ("true", "yes", "1", "y", "t"))
        elif value_type == list:
            import ast
            return cast(T, ast.literal_eval(value))
        elif value_type == dict:
            import ast
            return cast(T, ast.literal_eval(value))
        else:
            # Try to use the type's constructor
            return cast(T, value_type(value))
    except (ValueError, SyntaxError, TypeError) as e:
        raise ConfigValidationError(f"Failed to convert {env_var} to {value_type.__name__}: {e}")


def load_config_file(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from a file (JSON or YAML).
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        Loaded configuration as a dictionary
        
    Raises:
        ConfigNotFoundError: If file does not exist
        ConfigParseError: If file parsing fails
    """
    path = Path(file_path)
    if not path.exists():
        raise ConfigNotFoundError(f"Configuration file not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Parse based on file extension
            if file_path.endswith('.json'):
                return json.loads(content)
            elif file_path.endswith(('.yml', '.yaml')):
                return yaml.safe_load(content)
            else:
                # Try JSON first, then YAML
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return yaml.safe_load(content)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise ConfigParseError(f"Failed to parse configuration file {file_path}: {e}")
    except Exception as e:
        raise ConfigParseError(f"Error loading configuration from {file_path}: {e}")


def get_component_port(component_id: str, default: Optional[int] = None) -> int:
    """
    Get the port for a component based on standardized port assignments.
    
    Args:
        component_id: Component identifier (e.g., "hermes", "engram")
        default: Default port if not found in environment or standard assignments
        
    Returns:
        Port number
        
    Raises:
        ConfigValidationError: If port cannot be determined
    """
    # First check environment variable
    env_var = f"{component_id.upper()}_PORT"
    port_str = TektonEnviron.get(env_var)
    
    if port_str:
        try:
            return int(port_str)
        except ValueError:
            raise ConfigValidationError(f"Invalid port in environment variable {env_var}: {port_str}")
    
    # Check standard port assignments
    port_assignments = {
        "engram": 8000,
        "hermes": 8001,
        "ergon": 8002,
        "rhetor": 8003,
        "terma": 8004,
        "athena": 8005,
        "prometheus": 8006,
        "harmonia": 8007,
        "telos": 8008,
        "synthesis": 8009,
        "tekton_core": 8010,
        "hephaestus": 8080
    }
    
    if component_id.lower() in port_assignments:
        return port_assignments[component_id.lower()]
    
    # Use provided default or raise error
    if default is not None:
        return default
    
    raise ConfigValidationError(f"Could not determine port for component: {component_id}")


# Create a global config registry for components to share configuration
_config_registry: Dict[str, TektonConfig] = {}

def register_config(component_id: str, config: TektonConfig) -> None:
    """
    Register a component configuration in the global registry.
    
    Args:
        component_id: Component identifier
        config: Configuration instance
    """
    _config_registry[component_id] = config

def get_config(component_id: str) -> Optional[TektonConfig]:
    """
    Get a component configuration from the global registry.
    
    Args:
        component_id: Component identifier
        
    Returns:
        Configuration instance or None if not found
    """
    return _config_registry.get(component_id)