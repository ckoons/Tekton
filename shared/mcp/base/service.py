"""
Base MCP Service implementation for Tekton components.

This provides a standardized way for components to implement MCP support.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import asyncio

from tekton.models import TektonBaseModel

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Unified MCP service base",
    rationale="Standardized base class for all Tekton components to implement MCP protocol support",
    alternatives_considered=["Component-specific MCP implementations", "External MCP proxy", "Direct API exposure"])
@integration_point(
    title="MCP protocol implementation",
    target_component="All Tekton components",
    protocol="Internal API",
    data_flow="Component → MCPService → Tool registration → Hermes aggregation → External clients"
)
class MCPService(ABC):
    """
    Base class for implementing MCP services in Tekton components.
    
    This class provides the foundation for components to expose their
    functionality through the MCP protocol.
    """
    
    def __init__(
        self,
        component_name: str,
        component_version: str = "0.1.0",
        hermes_url: Optional[str] = None
    ):
        """
        Initialize the MCP service.
        
        Args:
            component_name: Name of the component
            component_version: Version of the component
            hermes_url: URL of Hermes MCP aggregator (optional)
        """
        self.component_name = component_name
        self.component_version = component_version
        self.hermes_url = hermes_url
        
        # Tool registry
        self.tools: Dict[str, Dict[str, Any]] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Contexts
        self.contexts: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Initializing MCP service for {component_name} v{component_version}")
    
    async def initialize(self):
        """Initialize the MCP service and register default tools."""
        logger.info(f"Initializing MCP service for {self.component_name}")
        
        # Register default tools
        await self.register_default_tools()
        
        # Register with Hermes if URL provided
        if self.hermes_url:
            await self.register_with_hermes()
        
        logger.info(f"MCP service initialized for {self.component_name}")
    
    @abstractmethod
    async def register_default_tools(self):
        """
        Register default tools for this component.
        
        This method should be implemented by each component to register
        their specific tools.
        """
        pass
    
    async def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a tool with the MCP service.
        
        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON Schema for tool input
            handler: Async function to handle tool execution
            tags: Optional tags for categorization
            metadata: Optional additional metadata
            
        Returns:
            Tool ID
        """
        tool_id = f"{self.component_name}.{name}"
        
        tool_spec = {
            "id": tool_id,
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "tags": tags or [],
            "metadata": metadata or {},
            "component": self.component_name,
            "version": self.component_version
        }
        
        self.tools[tool_id] = {
            "spec": tool_spec,
            "handler": handler
        }
        
        logger.info(f"Registered tool: {name} ({tool_id})")
        return tool_id
    
    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered tool.
        
        Args:
            tool_id: Tool ID
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        if tool_id not in self.tools:
            return {
                "success": False,
                "error": f"Tool {tool_id} not found"
            }
        
        tool = self.tools[tool_id]
        handler = tool["handler"]
        
        try:
            # Execute the tool handler
            result = await handler(parameters, context)
            
            return {
                "success": True,
                "result": result,
                "tool_id": tool_id
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_id": tool_id
            }
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an MCP message.
        
        Args:
            message: MCP message to process
            
        Returns:
            Processing result
        """
        message_type = message.get("type", "unknown")
        
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            return await handler(message)
        else:
            return {
                "success": False,
                "error": f"Unknown message type: {message_type}"
            }
    
    def register_message_handler(
        self,
        message_type: str,
        handler: Callable
    ):
        """
        Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Async function to handle the message
        """
        self.message_handlers[message_type] = handler
        logger.info(f"Registered message handler for type: {message_type}")
    
    @state_checkpoint(
        title="MCP context management",
        state_type="memory",
        persistence=False,
        consistency_requirements="Context data must be thread-safe for concurrent access",
        recovery_strategy="Contexts are ephemeral, recreated on restart"
    )
    async def create_context(
        self,
        context_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new context.
        
        Args:
            context_id: Optional context ID (generated if not provided)
            data: Initial context data
            metadata: Context metadata
            
        Returns:
            Context ID
        """
        if not context_id:
            context_id = f"{self.component_name}-ctx-{len(self.contexts)}"
        
        self.contexts[context_id] = {
            "id": context_id,
            "data": data or {},
            "metadata": metadata or {},
            "component": self.component_name
        }
        
        logger.info(f"Created context: {context_id}")
        return context_id
    
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing context.
        
        Args:
            context_id: Context ID
            updates: Updates to apply
            
        Returns:
            Success status
        """
        if context_id not in self.contexts:
            logger.error(f"Context not found: {context_id}")
            return False
        
        context = self.contexts[context_id]
        context["data"].update(updates)
        
        logger.info(f"Updated context: {context_id}")
        return True
    
    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get a context by ID."""
        return self.contexts.get(context_id)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        return [tool["spec"] for tool in self.tools.values()]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP capabilities for this service."""
        return {
            "version": "mcp/1.0",
            "component": self.component_name,
            "component_version": self.component_version,
            "tools": len(self.tools),
            "message_types": list(self.message_handlers.keys()),
            "contexts": len(self.contexts),
            "features": self.get_features()
        }
    
    def get_features(self) -> List[str]:
        """
        Get list of supported features.
        
        Override this method to specify component-specific features.
        """
        return ["tools", "contexts", "messages"]
    
    async def register_with_hermes(self):
        """Register this MCP service with Hermes."""
        if not self.hermes_url:
            logger.warning("No Hermes URL provided, skipping registration")
            return
        
        # This will be implemented when we create the client
        logger.info(f"Would register with Hermes at {self.hermes_url}")
    
    async def shutdown(self):
        """Shutdown the MCP service."""
        logger.info(f"Shutting down MCP service for {self.component_name}")
        # Cleanup resources if needed