"""Component information tool implementation."""

from typing import Dict, Any, Optional, List

from ..base.tool import MCPTool


class ComponentInfoTool(MCPTool):
    """Tool for getting component information."""
    
    name = "component_info"
    description = "Get information about the component"
    tags = ["system", "info", "metadata"]
    
    def __init__(
        self,
        component_name: str,
        component_version: str,
        component_description: str,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the component info tool.
        
        Args:
            component_name: Name of the component
            component_version: Version of the component
            component_description: Description of the component
            capabilities: List of component capabilities
            metadata: Additional metadata
        """
        self.component_name = component_name
        self.component_version = component_version
        self.component_description = component_description
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        super().__init__()
    
    async def execute(self, include_capabilities: bool = True) -> Dict[str, Any]:
        """
        Get component information.
        
        Args:
            include_capabilities: Whether to include capabilities list
            
        Returns:
            Component information
        """
        info = {
            "name": self.component_name,
            "version": self.component_version,
            "description": self.component_description
        }
        
        if include_capabilities:
            info["capabilities"] = self.capabilities
        
        # Add any additional metadata
        if self.metadata:
            info["metadata"] = self.metadata
        
        return info
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for the component info tool."""
        return {
            "type": "object",
            "properties": {
                "include_capabilities": {
                    "type": "boolean",
                    "description": "Whether to include the capabilities list",
                    "default": True
                }
            },
            "required": []
        }