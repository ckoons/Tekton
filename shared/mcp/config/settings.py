"""
MCP configuration settings.

This module provides configuration management for MCP implementations.
"""

import os
from shared.env import TektonEnviron
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from shared.utils.env_config import get_component_config


class MCPConfig(BaseModel):
    """Configuration for MCP services."""
    
    # Component identification
    component_name: str = Field(..., description="Name of the component")
    component_version: str = Field("0.1.0", description="Component version")
    component_description: str = Field("", description="Component description")
    
    # Hermes connection
    hermes_url: Optional[str] = Field(None, description="URL of Hermes MCP aggregator")
    hermes_timeout: int = Field(30, description="Timeout for Hermes requests in seconds")
    auto_register: bool = Field(True, description="Auto-register with Hermes on startup")
    
    # Tool settings
    enable_default_tools: bool = Field(True, description="Enable default system tools")
    tool_prefix: Optional[str] = Field(None, description="Prefix for tool names")
    
    # Context settings
    max_contexts: int = Field(100, description="Maximum number of contexts to maintain")
    context_ttl: Optional[int] = Field(None, description="Context TTL in seconds")
    
    # Performance settings
    max_concurrent_tools: int = Field(10, description="Maximum concurrent tool executions")
    tool_timeout: int = Field(60, description="Default tool execution timeout in seconds")
    
    # Security settings
    require_auth: bool = Field(False, description="Require authentication for tool execution")
    allowed_origins: List[str] = Field(["*"], description="Allowed CORS origins")
    
    @classmethod
    def from_env(cls, component_name: str) -> "MCPConfig":
        """
        Create MCP config from environment variables.
        
        Args:
            component_name: Name of the component
            
        Returns:
            MCPConfig instance
        """
        # Get component config
        config = get_component_config()
        
        # Get Hermes URL from config or environment
        hermes_port = getattr(config.hermes, "port", 8001) if hasattr(config, "hermes") else 8001
        hermes_host = TektonEnviron.get("HERMES_HOST", "localhost")
        hermes_url = f"http://{hermes_host}:{hermes_port}"
        
        # Build MCP config
        return cls(
            component_name=component_name,
            component_version=TektonEnviron.get(f"{component_name.upper()}_VERSION", "0.1.0"),
            component_description=TektonEnviron.get(f"{component_name.upper()}_DESCRIPTION", ""),
            hermes_url=TektonEnviron.get("HERMES_URL", hermes_url),
            hermes_timeout=int(TektonEnviron.get("MCP_HERMES_TIMEOUT", "30")),
            auto_register=TektonEnviron.get("MCP_AUTO_REGISTER", "true").lower() == "true",
            enable_default_tools=TektonEnviron.get("MCP_ENABLE_DEFAULT_TOOLS", "true").lower() == "true",
            tool_prefix=TektonEnviron.get("MCP_TOOL_PREFIX"),
            max_contexts=int(TektonEnviron.get("MCP_MAX_CONTEXTS", "100")),
            context_ttl=int(TektonEnviron.get("MCP_CONTEXT_TTL")) if TektonEnviron.get("MCP_CONTEXT_TTL") else None,
            max_concurrent_tools=int(TektonEnviron.get("MCP_MAX_CONCURRENT_TOOLS", "10")),
            tool_timeout=int(TektonEnviron.get("MCP_TOOL_TIMEOUT", "60")),
            require_auth=TektonEnviron.get("MCP_REQUIRE_AUTH", "false").lower() == "true",
            allowed_origins=TektonEnviron.get("MCP_ALLOWED_ORIGINS", "*").split(",")
        )
    
    def get_tool_name(self, name: str) -> str:
        """
        Get the full tool name with prefix if configured.
        
        Args:
            name: Base tool name
            
        Returns:
            Full tool name
        """
        if self.tool_prefix:
            return f"{self.tool_prefix}.{name}"
        return f"{self.component_name}.{name}"
    
    def to_env_dict(self) -> Dict[str, str]:
        """
        Convert config to environment variable dictionary.
        
        Returns:
            Dictionary of environment variables
        """
        env_vars = {
            f"{self.component_name.upper()}_VERSION": self.component_version,
            f"{self.component_name.upper()}_DESCRIPTION": self.component_description,
        }
        
        if self.hermes_url:
            env_vars["HERMES_URL"] = self.hermes_url
        
        env_vars.update({
            "MCP_HERMES_TIMEOUT": str(self.hermes_timeout),
            "MCP_AUTO_REGISTER": "true" if self.auto_register else "false",
            "MCP_ENABLE_DEFAULT_TOOLS": "true" if self.enable_default_tools else "false",
            "MCP_MAX_CONTEXTS": str(self.max_contexts),
            "MCP_MAX_CONCURRENT_TOOLS": str(self.max_concurrent_tools),
            "MCP_TOOL_TIMEOUT": str(self.tool_timeout),
            "MCP_REQUIRE_AUTH": "true" if self.require_auth else "false",
            "MCP_ALLOWED_ORIGINS": ",".join(self.allowed_origins)
        })
        
        if self.tool_prefix:
            env_vars["MCP_TOOL_PREFIX"] = self.tool_prefix
        
        if self.context_ttl:
            env_vars["MCP_CONTEXT_TTL"] = str(self.context_ttl)
        
        return env_vars