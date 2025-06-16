"""
MCP Service - Hermes integration for Multimodal Cognitive Protocol.

This module provides a service for multimodal information processing,
enabling components to handle and process multimodal content.
"""

import time
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Set

from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus
from hermes.core.registration import RegistrationManager
from hermes.core.mcp.tool_executor import ToolExecutor

# Import FastMCP integration if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        mcp_processor,
        mcp_context,
        adapt_tool,
        adapt_processor,
        adapt_context,
        MCPClient,
        register_component
    )
    
    # Import schemas
    from tekton.mcp.fastmcp.schema import (
        ToolSchema,
        ProcessorSchema,
        CapabilitySchema,
        ContextSchema,
        MessageSchema,
        ResponseSchema,
        ContentSchema
    )
    
    fastmcp_available = True
except ImportError:
    fastmcp_available = False

# Import tool registry
from hermes.core.mcp.tools import (
    register_system_tools,
    register_database_tools,
    register_messaging_tools
)

# Import adapters
from hermes.core.mcp.adapters import (
    adapt_legacy_service
)

logger = logging.getLogger(__name__)

class MCPService:
    """
    Service for multimodal information processing in Hermes.
    
    This class provides a service for multimodal information processing,
    enabling components to handle and process multimodal content.
    """
    
    def __init__(
        self,
        service_registry: ServiceRegistry,
        message_bus: MessageBus,
        registration_manager: Optional[RegistrationManager] = None,
        database_manager: Optional[Any] = None
    ):
        """
        Initialize the MCP service.
        
        Args:
            service_registry: Service registry to use
            message_bus: Message bus to use
            registration_manager: Optional registration manager to use
            database_manager: Optional database manager to use
        """
        self.service_registry = service_registry
        self.message_bus = message_bus
        self.registration_manager = registration_manager
        
        # Store database manager for FastMCP tools
        self._database_manager = database_manager
        
        # Internal state
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.processors: Dict[str, Dict[str, Any]] = {}
        
        # Initialize tool executor
        self.tool_executor = ToolExecutor()
        self.tool_executor.set_dependencies(
            service_registry=self.service_registry,
            database_manager=database_manager,
            message_bus=self.message_bus
        )
        
        # Initialize channels
        self._channels_initialized = False
        
        logger.info("MCP service initialized")
    
    async def initialize(self):
        """Initialize the service and set up channels."""
        if self._channels_initialized:
            logger.info("MCP service already initialized, skipping")
            return
            
        try:
            logger.info("Initializing MCP service channels")
            
            # Check if message bus is available
            if not self.message_bus:
                logger.error("Message bus not available for MCP service initialization")
                return
                
            # Create tools channel
            await self.message_bus.create_channel(
                'mcp.tools',
                description='Channel for MCP tools'
            )
            
            # Create context channel
            await self.message_bus.create_channel(
                'mcp.contexts',
                description='Channel for MCP contexts'
            )
            
            # Create processor channel
            await self.message_bus.create_channel(
                'mcp.processors',
                description='Channel for MCP processors'
            )
            
            # Subscribe to channels (unified interface handles async callbacks)
            self.message_bus.subscribe(
                'mcp.tools',
                self._handle_tool_message
            )

            self.message_bus.subscribe(
                'mcp.contexts',
                self._handle_context_message
            )

            self.message_bus.subscribe(
                'mcp.processors',
                self._handle_processor_message
            )
            
            # Register FastMCP tools if available
            if fastmcp_available:
                logger.info("Registering FastMCP tools")
                
                # Get database manager if available
                database_manager = getattr(self, "_database_manager", None)
                
                # Register system tools
                await register_system_tools(
                    service_registry=self.service_registry,
                    tool_registry=self
                )
                
                # Register database tools if database manager is available
                if database_manager:
                    await register_database_tools(
                        database_manager=database_manager,
                        tool_registry=self
                    )
                    
                # Register messaging tools
                await register_messaging_tools(
                    message_bus=self.message_bus,
                    tool_registry=self
                )
                
                # Adapt legacy service tools and processors
                adapted_result = await adapt_legacy_service(self)
                if adapted_result:
                    logger.info(f"Legacy service adaptation complete: {len(adapted_result.get('tools', []))} tools, {len(adapted_result.get('processors', []))} processors")
                
                logger.info("FastMCP tools registered successfully")
            else:
                logger.warning("FastMCP not available, using legacy MCP implementation")
            
            self._channels_initialized = True
            logger.info("MCP service channels initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MCP service: {e}")
            # Don't re-raise to allow service to still be used even if channel initialization fails
            # This allows the service to work even if the message bus is not available
            self._channels_initialized = False
    
    async def register_tool(self, tool_spec: Dict[str, Any]) -> str:
        """
        Register a tool with the MCP service.
        
        Args:
            tool_spec: Tool specification
            
        Returns:
            Tool ID
        """
        # Validate tool specification
        required_fields = ["name", "description", "schema"]
        for field in required_fields:
            if field not in tool_spec:
                logger.error(f"Tool specification missing required field: {field}")
                return ""
        
        # Generate tool ID if not provided
        tool_id = tool_spec.get("id") or f"tool-{uuid.uuid4()}"
        
        # Add registration metadata
        tool_spec["id"] = tool_id
        tool_spec["registered_at"] = time.time()
        
        # Store tool
        self.tools[tool_id] = tool_spec
        
        # Register with service registry if available
        if self.registration_manager:
            # Create a serializable version of tool_spec for metadata
            serializable_spec = {
                "id": tool_id,
                "name": tool_spec["name"],
                "description": tool_spec["description"],
                "schema": tool_spec.get("schema", {}),
                "tags": tool_spec.get("tags", []),
                "version": tool_spec.get("version"),
                "endpoint": tool_spec.get("endpoint"),
                "metadata": tool_spec.get("metadata", {})
            }
            
            self.registration_manager.register_component(
                component_id=f"mcp.tool.{tool_id}",
                name=tool_spec["name"],
                version=tool_spec.get("version", "1.0.0"),
                component_type="mcp_tool",
                endpoint="",
                capabilities=tool_spec.get("tags", []),
                metadata={
                    "mcp_tool": True,
                    "tool_spec": serializable_spec
                }
            )
        
        # Publish tool registration event (remove function for serialization)
        publishable_spec = {k: v for k, v in tool_spec.items() if k != 'function'}
        self.message_bus.publish(
            'mcp.tools',
            {
                'type': 'tool_registered',
                'tool_id': tool_id,
                'tool_spec': publishable_spec
            }
        )
        
        logger.info(f"Tool registered: {tool_spec['name']} ({tool_id})")
        return tool_id
    
    async def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool from the MCP service.
        
        Args:
            tool_id: Tool ID to unregister
            
        Returns:
            True if unregistration successful
        """
        if tool_id not in self.tools:
            logger.warning(f"Tool not found: {tool_id}")
            return False
            
        # Remove tool
        tool = self.tools.pop(tool_id)
        
        # Unregister from service registry if available
        if self.registration_manager:
            self.registration_manager.unregister_component(
                component_id=f"mcp.tool.{tool_id}",
                token_str=""  # Token not used here
            )
        
        # Publish tool unregistration event
        self.message_bus.publish(
            'mcp.tools',
            {
                'type': 'tool_unregistered',
                'tool_id': tool_id
            }
        )
        
        logger.info(f"Tool unregistered: {tool_id}")
        return True
    
    async def register_processor(self, processor_spec: Dict[str, Any]) -> str:
        """
        Register a processor with the MCP service.
        
        Args:
            processor_spec: Processor specification
            
        Returns:
            Processor ID
        """
        # Validate processor specification
        required_fields = ["name", "description", "capabilities"]
        for field in required_fields:
            if field not in processor_spec:
                logger.error(f"Processor specification missing required field: {field}")
                return ""
        
        # Generate processor ID if not provided
        processor_id = processor_spec.get("id") or f"processor-{uuid.uuid4()}"
        
        # Add registration metadata
        processor_spec["id"] = processor_id
        processor_spec["registered_at"] = time.time()
        
        # Store processor
        self.processors[processor_id] = processor_spec
        
        # Register with service registry if available
        if self.registration_manager:
            self.registration_manager.register_component(
                component_id=f"mcp.processor.{processor_id}",
                name=processor_spec["name"],
                version=processor_spec.get("version", "1.0.0"),
                component_type="mcp_processor",
                endpoint=processor_spec.get("endpoint", ""),
                capabilities=processor_spec.get("capabilities", []),
                metadata={
                    "mcp_processor": True,
                    "processor_spec": processor_spec
                }
            )
        
        # Publish processor registration event
        self.message_bus.publish(
            'mcp.processors',
            {
                'type': 'processor_registered',
                'processor_id': processor_id,
                'processor_spec': processor_spec
            }
        )
        
        logger.info(f"Processor registered: {processor_spec['name']} ({processor_id})")
        return processor_id
    
    async def create_context(
        self,
        data: Dict[str, Any],
        source: Dict[str, Any],
        context_id: Optional[str] = None
    ) -> str:
        """
        Create a new context.
        
        Args:
            data: Context data
            source: Context source information
            context_id: Optional ID for the context
            
        Returns:
            Context ID
        """
        # Generate context ID if not provided
        context_id = context_id or f"ctx-{uuid.uuid4()}"
        
        # Create context
        context = {
            "id": context_id,
            "data": data,
            "source": source,
            "created_at": time.time(),
            "updated_at": time.time(),
            "history": [
                {
                    "operation": "created",
                    "timestamp": time.time(),
                    "source": source
                }
            ]
        }
        
        # Store context
        self.contexts[context_id] = context
        
        # Publish context creation event
        self.message_bus.publish(
            'mcp.contexts',
            {
                'type': 'context_created',
                'context_id': context_id,
                'context': context
            }
        )
        
        logger.info(f"Context created: {context_id}")
        return context_id
    
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any],
        source: Dict[str, Any],
        operation: str = "update"
    ) -> bool:
        """
        Update a context.
        
        Args:
            context_id: ID of the context to update
            updates: Updates to apply
            source: Update source information
            operation: Update operation type
            
        Returns:
            True if update successful
        """
        if context_id not in self.contexts:
            logger.warning(f"Context not found: {context_id}")
            return False
            
        context = self.contexts[context_id]
        
        # Deep merge updates into context data
        context["data"] = self._deep_merge(context["data"], updates)
        context["updated_at"] = time.time()
        
        # Add history entry
        context["history"].append({
            "operation": operation,
            "timestamp": time.time(),
            "source": source,
            "keys": list(updates.keys())
        })
        
        # Publish context update event
        self.message_bus.publish(
            'mcp.contexts',
            {
                'type': 'context_updated',
                'context_id': context_id,
                'updates': updates,
                'operation': operation
            }
        )
        
        logger.info(f"Context updated: {context_id}")
        return True
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an MCP message.
        
        Args:
            message: MCP message to process
            
        Returns:
            Processing result
        """
        # Validate message
        required_fields = ["id", "version", "source", "content"]
        for field in required_fields:
            if field not in message:
                logger.error(f"MCP message missing required field: {field}")
                return {
                    "error": f"Missing required field: {field}"
                }
        
        # Find appropriate processor
        processors = await self._find_processors_for_message(message)
        
        if not processors:
            logger.warning("No suitable processor found for message")
            return {
                "error": "No suitable processor found for message"
            }
            
        # Select first processor (in a more sophisticated implementation,
        # we would select based on capabilities, load, etc.)
        processor_id = processors[0]
        processor = self.processors[processor_id]
        
        # Check if processor has an endpoint
        endpoint = processor.get("endpoint")
        if not endpoint:
            logger.warning(f"Processor {processor_id} has no endpoint")
            return {
                "error": f"Processor {processor_id} has no endpoint"
            }
            
        # In a real implementation, we would send the message to the processor
        # For now, just simulate processing
        
        # Create processing result
        result = {
            "id": f"response-{message['id']}",
            "version": message["version"],
            "timestamp": time.time(),
            "source": {
                "component": "mcp.service",
                "processor": processor_id
            },
            "destination": message.get("source", {}),
            "context": message.get("context", {}),
            "content": [
                {
                    "type": "text",
                    "format": "text/plain",
                    "data": "Message processed by MCP service",
                    "metadata": {
                        "role": "assistant"
                    }
                }
            ],
            "processed_by": processor_id
        }
        
        logger.info(f"Message {message['id']} processed by {processor_id}")
        return result
    
    async def execute_tool(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Tool execution result
        """
        if tool_id not in self.tools:
            logger.warning(f"Tool not found: {tool_id}")
            return {
                "success": False,
                "error": f"Tool not found: {tool_id}"
            }
            
        tool = self.tools[tool_id]
        
        # Check if this is a Hermes system tool and handle directly
        tool_name = tool.get("name", "")
        if tool_name in ["GetComponentStatus", "ListComponents", "QueryVectorDatabase", 
                         "StoreVectorData", "PublishMessage", "CreateChannel"]:
            # Import and execute the tool directly
            from hermes.core.mcp.tools import (
                get_component_status, list_components, query_vector_database,
                store_vector_data, publish_message, create_channel
            )
            
            tool_map = {
                "GetComponentStatus": get_component_status,
                "ListComponents": list_components,
                "QueryVectorDatabase": query_vector_database,
                "StoreVectorData": store_vector_data,
                "PublishMessage": publish_message,
                "CreateChannel": create_channel
            }
            
            handler = tool_map.get(tool_name)
            if handler:
                # Inject dependencies
                injected_params = parameters.copy()
                if tool_name in ["GetComponentStatus", "ListComponents"]:
                    injected_params["service_registry"] = self.service_registry
                elif tool_name in ["QueryVectorDatabase", "StoreVectorData"]:
                    injected_params["database_manager"] = self._database_manager
                elif tool_name in ["PublishMessage", "CreateChannel"]:
                    injected_params["message_bus"] = self.message_bus
                    
                # Execute the handler
                try:
                    result_data = await handler(**injected_params)
                    result = {
                        "success": True,
                        "tool_id": tool_id,
                        "tool_name": tool_name,
                        "result": result_data,
                        "execution_time": 0.1
                    }
                except Exception as e:
                    logger.error(f"Error executing Hermes tool {tool_name}: {e}")
                    result = {
                        "success": False,
                        "error": str(e)
                    }
            else:
                result = {
                    "success": False,
                    "error": f"Handler not found for Hermes tool: {tool_name}"
                }
        else:
            # Use tool executor for other tools
            result = await self.tool_executor.execute_tool(tool_id, tool, parameters)
        
        # Publish tool execution event
        self.message_bus.publish(
            'mcp.tools',
            {
                'type': 'tool_executed',
                'tool_id': tool_id,
                'parameters': parameters,
                'result': result
            }
        )
        
        logger.info(f"Tool executed: {tool_id}")
        return result
    
    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a tool.
        
        Args:
            tool_id: Tool ID to retrieve
            
        Returns:
            Tool information or None if not found
        """
        tool = self.tools.get(tool_id)
        if not tool:
            return None
            
        # Return only serializable fields to avoid recursion errors
        return {
            "id": tool.get("id"),
            "name": tool.get("name"),
            "description": tool.get("description"),
            "schema": tool.get("schema", {}),
            "tags": tool.get("tags", []),
            "version": tool.get("version"),
            "endpoint": tool.get("endpoint"),
            "metadata": tool.get("metadata", {}),
            "registered_at": tool.get("registered_at")
        }
    
    async def get_processor(self, processor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a processor.
        
        Args:
            processor_id: Processor ID to retrieve
            
        Returns:
            Processor information or None if not found
        """
        processor = self.processors.get(processor_id)
        return processor.copy() if processor else None
    
    async def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a context.
        
        Args:
            context_id: Context ID to retrieve
            
        Returns:
            Context or None if not found
        """
        context = self.contexts.get(context_id)
        return context.copy() if context else None
    
    async def _find_processors_for_message(self, message: Dict[str, Any]) -> List[str]:
        """
        Find processors that can handle a message.
        
        Args:
            message: MCP message
            
        Returns:
            List of processor IDs
        """
        matching_processors = []
        
        # Get message content types
        content_types = set()
        for content_item in message.get("content", []):
            content_type = content_item.get("type")
            if content_type:
                content_types.add(content_type)
                
        # Get requested capabilities
        requested_capabilities = message.get("processing", {}).get("capabilities_required", [])
        
        # Find processors with matching capabilities
        for processor_id, processor in self.processors.items():
            capabilities = processor.get("capabilities", [])
            
            # Check if processor supports all required content types
            supports_content_types = all(
                content_type in capabilities for content_type in content_types
            )
            
            # Check if processor has all requested capabilities
            has_capabilities = all(
                capability in capabilities for capability in requested_capabilities
            )
            
            if supports_content_types and has_capabilities:
                matching_processors.append(processor_id)
        
        return matching_processors
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            updates: Updates to apply
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Replace or add value
                result[key] = value
                
        return result
    
    async def _handle_tool_message(self, message: Dict[str, Any]):
        """
        Handle tool messages.
        
        Args:
            message: Tool message
        """
        message_type = message.get('type')
        
        if message_type == 'register_tool':
            # Register tool
            tool_spec = message.get('tool_spec')
            if tool_spec:
                await self.register_tool(tool_spec)
                
        elif message_type == 'unregister_tool':
            # Unregister tool
            tool_id = message.get('tool_id')
            if tool_id:
                await self.unregister_tool(tool_id)
                
        elif message_type == 'execute_tool':
            # Execute tool
            tool_id = message.get('tool_id')
            parameters = message.get('parameters')
            if tool_id and parameters:
                await self.execute_tool(tool_id, parameters, message.get('context'))
    
    async def _handle_context_message(self, message: Dict[str, Any]):
        """
        Handle context messages.
        
        Args:
            message: Context message
        """
        message_type = message.get('type')
        
        if message_type == 'create_context':
            # Create context
            data = message.get('data')
            source = message.get('source')
            if data and source:
                await self.create_context(
                    data=data,
                    source=source,
                    context_id=message.get('context_id')
                )
                
        elif message_type == 'update_context':
            # Update context
            context_id = message.get('context_id')
            updates = message.get('updates')
            source = message.get('source')
            if context_id and updates and source:
                await self.update_context(
                    context_id=context_id,
                    updates=updates,
                    source=source,
                    operation=message.get('operation', 'update')
                )
    
    async def _handle_processor_message(self, message: Dict[str, Any]):
        """
        Handle processor messages.
        
        Args:
            message: Processor message
        """
        message_type = message.get('type')
        
        if message_type == 'register_processor':
            # Register processor
            processor_spec = message.get('processor_spec')
            if processor_spec:
                await self.register_processor(processor_spec)
                
        elif message_type == 'process_message':
            # Process message
            mcp_message = message.get('message')
            if mcp_message:
                result = await self.process_message(mcp_message)
                
                # Publish processing result
                self.message_bus.publish(
                    'mcp.processors',
                    {
                        'type': 'message_processed',
                        'message_id': mcp_message.get('id'),
                        'result': result
                    }
                )