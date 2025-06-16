"""Configuration management tools."""

from typing import Dict, Any, Optional, Callable
import json

from ..base.tool import MCPTool


class GetConfigTool(MCPTool):
    """Tool for retrieving configuration values."""
    
    name = "get_config"
    description = "Get configuration values for the component"
    tags = ["config", "settings", "system"]
    
    def __init__(
        self,
        config_getter: Callable[[], Dict[str, Any]],
        allowed_keys: Optional[list] = None
    ):
        """
        Initialize the get config tool.
        
        Args:
            config_getter: Function that returns current configuration
            allowed_keys: Optional list of allowed configuration keys
        """
        self.config_getter = config_getter
        self.allowed_keys = allowed_keys
        super().__init__()
    
    async def execute(self, key: Optional[str] = None, format: str = "json") -> Any:
        """
        Get configuration values.
        
        Args:
            key: Optional specific key to retrieve (dot notation supported)
            format: Output format (json, yaml, text)
            
        Returns:
            Configuration value(s)
        """
        # Get current config
        config = self.config_getter()
        
        # Filter by allowed keys if specified
        if self.allowed_keys:
            config = {k: v for k, v in config.items() if k in self.allowed_keys}
        
        # Get specific key if requested
        if key:
            # Support dot notation
            parts = key.split(".")
            value = config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return {
                        "error": f"Key not found: {key}",
                        "available_keys": list(config.keys()) if isinstance(config, dict) else []
                    }
            
            result = {key: value}
        else:
            result = config
        
        # Format output
        if format == "json":
            return result
        elif format == "yaml":
            # Would need to import yaml for this
            return {"error": "YAML format not implemented", "data": result}
        elif format == "text":
            return {"text": json.dumps(result, indent=2)}
        else:
            return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema."""
        schema = {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Configuration key to retrieve (supports dot notation)"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "yaml", "text"],
                    "default": "json",
                    "description": "Output format"
                }
            },
            "required": []
        }
        
        if self.allowed_keys:
            schema["properties"]["key"]["enum"] = self.allowed_keys
        
        return schema


class SetConfigTool(MCPTool):
    """Tool for updating configuration values."""
    
    name = "set_config"
    description = "Update configuration values for the component"
    tags = ["config", "settings", "system", "admin"]
    
    def __init__(
        self,
        config_setter: Callable[[str, Any], bool],
        allowed_keys: Optional[list] = None,
        require_confirmation: bool = True
    ):
        """
        Initialize the set config tool.
        
        Args:
            config_setter: Function to set configuration value (key, value) -> success
            allowed_keys: Optional list of allowed configuration keys
            require_confirmation: Whether to require confirmation
        """
        self.config_setter = config_setter
        self.allowed_keys = allowed_keys
        self.require_confirmation = require_confirmation
        super().__init__()
    
    async def execute(
        self,
        key: str,
        value: Any,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key to set
            value: Value to set
            confirm: Confirmation flag
            
        Returns:
            Operation result
        """
        # Check if key is allowed
        if self.allowed_keys and key not in self.allowed_keys:
            return {
                "success": False,
                "error": f"Key not allowed: {key}",
                "allowed_keys": self.allowed_keys
            }
        
        # Check confirmation
        if self.require_confirmation and not confirm:
            return {
                "success": False,
                "error": "Confirmation required",
                "message": f"Please confirm setting {key} = {value}",
                "action_required": "Set confirm=true to proceed"
            }
        
        # Set the value
        try:
            success = self.config_setter(key, value)
            
            if success:
                return {
                    "success": True,
                    "message": f"Configuration updated: {key} = {value}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update configuration"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating configuration: {str(e)}"
            }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema."""
        schema = {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Configuration key to set"
                },
                "value": {
                    "description": "Value to set (any type)"
                },
                "confirm": {
                    "type": "boolean",
                    "default": False,
                    "description": "Confirmation flag"
                }
            },
            "required": ["key", "value"]
        }
        
        if self.allowed_keys:
            schema["properties"]["key"]["enum"] = self.allowed_keys
        
        return schema