"""
A2A Service - Hermes integration for Agent-to-Agent Communication Protocol v0.2.1

This module provides integration between Hermes's message bus and service registry
with the A2A Protocol v0.2.1 implementation.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from uuid import uuid4

from hermes.core.service_discovery import ServiceRegistry
from hermes.core.message_bus import MessageBus
from hermes.core.registration import RegistrationManager

# Import A2A components from tekton
from tekton.a2a import (
    AgentCard, AgentRegistry, AgentStatus,
    TaskManager, TaskState,
    DiscoveryService,
    JSONRPCRequest, JSONRPCResponse,
    MethodDispatcher, create_standard_dispatcher,
    SSEManager, EventType, TaskEvent, AgentEvent,
    SubscriptionManager,
    websocket_manager
)

logger = logging.getLogger(__name__)


class A2AService:
    """
    Service for agent-to-agent communication in Hermes.
    
    This class bridges Hermes's infrastructure with the A2A Protocol v0.2.1,
    enabling components to communicate using JSON-RPC 2.0.
    """
    
    def __init__(
        self,
        service_registry: ServiceRegistry,
        message_bus: MessageBus,
        registration_manager: Optional[RegistrationManager] = None
    ):
        """
        Initialize the A2A service.
        
        Args:
            service_registry: Service registry to use
            message_bus: Message bus to use
            registration_manager: Optional registration manager to use
        """
        self.service_registry = service_registry
        self.message_bus = message_bus
        self.registration_manager = registration_manager
        
        # Initialize A2A components
        self.agent_registry = AgentRegistry()
        self.task_manager = TaskManager()
        self.discovery_service = DiscoveryService(self.agent_registry)
        self.method_dispatcher = create_standard_dispatcher(
            self.agent_registry,
            self.task_manager,
            self.discovery_service
        )
        
        # Initialize streaming components
        self.sse_manager = SSEManager()
        self.subscription_manager = SubscriptionManager()
        
        # Set up task event callbacks
        self.task_manager.add_event_callback(self._on_task_event)
        
        # Track agent subscriptions
        self.agent_subscriptions: Dict[str, Set[str]] = {}  # agent_id -> set of channels
        
        # Initialize state
        self._initialized = False
        
        logger.info("A2A service initialized with Protocol v0.2.1")
    
    async def initialize(self):
        """Initialize the service and set up channels."""
        if self._initialized:
            return
        
        # Create A2A channels for backwards compatibility
        await self.message_bus.create_channel(
            'a2a.registration',
            description='Channel for agent registration events'
        )
        
        await self.message_bus.create_channel(
            'a2a.tasks',
            description='Channel for task management events'
        )
        
        await self.message_bus.create_channel(
            'a2a.discovery',
            description='Channel for agent discovery events'
        )
        
        # Subscribe to registration events from Hermes registration manager
        if self.registration_manager:
            await self.message_bus.subscribe_async(
                'registration.events',
                self._handle_registration_event
            )
        
        # Register custom Hermes methods
        await self._register_hermes_methods()
        
        self._initialized = True
        logger.info("A2A service initialized successfully")
    
    async def _register_hermes_methods(self):
        """Register Hermes-specific A2A methods"""
        
        # Forward agent methods to component registry
        async def agent_forward(agent_id: str, method: str, params: Dict[str, Any]) -> Any:
            """Forward a method call to a specific agent"""
            # Get agent endpoint from registry
            agent = self.agent_registry.get(agent_id)
            if not agent:
                raise Exception(f"Agent {agent_id} not found")
            
            # TODO: Implement HTTP forwarding to agent endpoint
            # For now, publish to message bus
            await self.message_bus.publish(f"agent.{agent_id}.request", {
                "method": method,
                "params": params
            })
            
            return {"forwarded": True, "agent_id": agent_id, "method": method}
        
        # Channel subscription management
        async def channel_subscribe(agent_id: str, channel: str) -> Dict[str, Any]:
            """Subscribe an agent to a channel"""
            if agent_id not in self.agent_subscriptions:
                self.agent_subscriptions[agent_id] = set()
            
            self.agent_subscriptions[agent_id].add(channel)
            
            # Create channel if it doesn't exist
            await self.message_bus.create_channel(channel, description=f"Channel for {channel}")
            
            return {"success": True, "agent_id": agent_id, "channel": channel}
        
        async def channel_unsubscribe(agent_id: str, channel: str) -> Dict[str, Any]:
            """Unsubscribe an agent from a channel"""
            if agent_id in self.agent_subscriptions:
                self.agent_subscriptions[agent_id].discard(channel)
            
            return {"success": True, "agent_id": agent_id, "channel": channel}
        
        async def channel_publish(channel: str, message: Dict[str, Any]) -> Dict[str, Any]:
            """Publish a message to a channel"""
            await self.message_bus.publish(channel, message)
            
            # Get subscribers
            subscribers = [
                agent_id for agent_id, channels in self.agent_subscriptions.items()
                if channel in channels
            ]
            
            return {
                "success": True,
                "channel": channel,
                "subscribers": len(subscribers)
            }
        
        # Register methods
        self.method_dispatcher.register_method("agent.forward", agent_forward)
        self.method_dispatcher.register_method("channel.subscribe", channel_subscribe)
        self.method_dispatcher.register_method("channel.unsubscribe", channel_unsubscribe)
        self.method_dispatcher.register_method("channel.publish", channel_publish)
    
    async def _handle_registration_event(self, event: Dict[str, Any]):
        """Handle component registration events from Hermes"""
        event_type = event.get("type")
        component_data = event.get("component", {})
        
        # Convert Hermes registration to A2A agent registration
        if event_type == "component_registered":
            # Check if component supports A2A
            capabilities = component_data.get("capabilities", [])
            if "a2a" in capabilities or "agent" in capabilities:
                # Create agent card from component data
                agent_card = AgentCard.create(
                    name=component_data.get("name", "Unknown"),
                    description=component_data.get("metadata", {}).get("description", ""),
                    version=component_data.get("version", "0.1.0"),
                    capabilities=capabilities,
                    supported_methods=component_data.get("supported_methods", []),
                    endpoint=component_data.get("endpoint"),
                    metadata=component_data.get("metadata", {})
                )
                
                # Override ID to match component ID
                agent_card.id = component_data.get("component_id")
                
                # Register in A2A registry
                self.agent_registry.register(agent_card)
                
                # Publish registration event
                await self.message_bus.publish("a2a.registration", {
                    "type": "agent_registered",
                    "agent": agent_card.model_dump()
                })
                
                logger.info(f"Registered component {agent_card.id} as A2A agent")
        
        elif event_type == "component_deregistered":
            component_id = component_data.get("component_id")
            if component_id:
                # Remove from A2A registry
                agent = self.agent_registry.unregister(component_id)
                if agent:
                    # Clean up subscriptions
                    self.agent_subscriptions.pop(component_id, None)
                    
                    # Publish deregistration event
                    await self.message_bus.publish("a2a.registration", {
                        "type": "agent_deregistered",
                        "agent_id": component_id
                    })
                    
                    logger.info(f"Deregistered A2A agent {component_id}")
        
        elif event_type == "component_heartbeat":
            component_id = component_data.get("component_id")
            if component_id:
                # Update agent heartbeat
                self.agent_registry.update_heartbeat(component_id)
    
    def get_dispatcher(self) -> MethodDispatcher:
        """Get the method dispatcher for handling JSON-RPC requests"""
        return self.method_dispatcher
    
    def get_agent_registry(self) -> AgentRegistry:
        """Get the agent registry"""
        return self.agent_registry
    
    def get_task_manager(self) -> TaskManager:
        """Get the task manager"""
        return self.task_manager
    
    def get_discovery_service(self) -> DiscoveryService:
        """Get the discovery service"""
        return self.discovery_service
    
    def get_sse_manager(self) -> SSEManager:
        """Get the SSE manager for streaming"""
        return self.sse_manager
    
    def get_subscription_manager(self) -> SubscriptionManager:
        """Get the subscription manager"""
        return self.subscription_manager
    
    def _on_task_event(
        self,
        event_type: str,
        task: Any,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ) -> None:
        """Handle task events and convert to streaming events"""
        try:
            # Map event types to EventType enum
            event_type_map = {
                "task.created": EventType.TASK_CREATED,
                "task.state_changed": EventType.TASK_STATE_CHANGED,
                "task.progress": EventType.TASK_PROGRESS,
                "task.completed": EventType.TASK_COMPLETED,
                "task.failed": EventType.TASK_FAILED,
                "task.cancelled": EventType.TASK_CANCELLED
            }
            
            stream_event_type = event_type_map.get(event_type)
            if not stream_event_type:
                return
            
            # Create appropriate event
            if event_type == "task.state_changed" and data:
                # Handle task.state as either enum or string
                new_state = data.get("new_state")
                if new_state is None:
                    new_state = task.state.value if hasattr(task.state, 'value') else str(task.state)
                    
                event = TaskEvent.create_state_change(
                    task_id=task.id,
                    old_state=data.get("old_state", "unknown"),
                    new_state=new_state,
                    source="hermes",
                    message=message
                )
            elif event_type == "task.progress" and data:
                event = TaskEvent.create_progress(
                    task_id=task.id,
                    progress=data.get("progress", task.progress),
                    source="hermes",
                    message=message
                )
            else:
                # Generic task event
                event = TaskEvent(
                    id=f"event-{uuid4()}",
                    type=stream_event_type,
                    timestamp=datetime.utcnow(),
                    source="hermes",
                    task_id=task.id,
                    task_name=task.name,
                    agent_id=task.agent_id,
                    data=data or {"state": task.state.value}
                )
            
            # Broadcast to SSE connections
            asyncio.create_task(self.sse_manager.broadcast_event(event))
            
            # Broadcast to WebSocket connections
            asyncio.create_task(websocket_manager.broadcast_event(event))
            
            # Route to subscriptions
            asyncio.create_task(self.subscription_manager.route_event(event))
            
        except Exception as e:
            logger.error(f"Error handling task event: {e}")
    
    async def shutdown(self):
        """Clean up resources on shutdown"""
        # Cancel any running tasks
        tasks_to_cancel = self.task_manager.list_tasks(state=TaskState.RUNNING)
        for task in tasks_to_cancel:
            await self.task_manager.cancel_task(task.id, "Service shutting down")
        
        logger.info("A2A service shut down")
    
    # Backwards compatibility methods
    
    async def register_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Legacy agent registration method"""
        try:
            agent_card = AgentCard(**agent_data)
            self.agent_registry.register(agent_card)
            return True
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Legacy agent unregistration method"""
        agent = self.agent_registry.unregister(agent_id)
        return agent is not None
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Legacy get agent method"""
        agent = self.agent_registry.get(agent_id)
        return agent.model_dump() if agent else None
    
    async def create_task(self, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy task creation method"""
        try:
            task = self.task_manager.create_task(
                name=task_spec.get("name", "Unnamed Task"),
                created_by=task_spec.get("created_by", "system"),
                description=task_spec.get("description"),
                input_data=task_spec.get("parameters"),
                metadata=task_spec.get("metadata", {})
            )
            
            # Auto-assign if preferred agent specified
            preferred_agent = task_spec.get("preferred_agent")
            if preferred_agent:
                self.task_manager.assign_task(task.id, preferred_agent)
            
            return {
                "task_id": task.id,
                "status": task.state.value
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Legacy get task method"""
        try:
            task = self.task_manager.get_task(task_id)
            return task.model_dump()
        except:
            return None