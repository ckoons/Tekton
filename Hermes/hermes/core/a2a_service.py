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
from tekton.a2a.streaming import ChannelBridge
from tekton.a2a import (
    ConversationManager, ConversationRole,
    ConversationState, TurnTakingMode
)
from tekton.a2a.task_coordination import (
    TaskCoordinator, CoordinationPattern,
    DependencyType, TaskWorkflow
)
from tekton.a2a.errors import InvalidRequestError
from tekton.a2a.security import (
    TokenManager, AccessControl, SecurityContext,
    Permission, Role, MessageSigner
)
from tekton.a2a.middleware import apply_security_middleware

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
        registration_manager: Optional[RegistrationManager] = None,
        enable_security: bool = True
    ):
        """
        Initialize the A2A service.
        
        Args:
            service_registry: Service registry to use
            message_bus: Message bus to use
            registration_manager: Optional registration manager to use
            enable_security: Whether to enable security features
        """
        self.service_registry = service_registry
        self.message_bus = message_bus
        self.registration_manager = registration_manager
        self.enable_security = enable_security
        
        # Initialize A2A components
        self.agent_registry = AgentRegistry()
        self.task_manager = TaskManager()
        self.discovery_service = DiscoveryService(self.agent_registry)
        self.method_dispatcher = create_standard_dispatcher(
            self.agent_registry,
            self.task_manager,
            self.discovery_service
        )
        
        # Initialize security components
        if self.enable_security:
            self.token_manager = TokenManager()
            self.access_control = AccessControl()
            self.message_signer = MessageSigner()
        else:
            self.token_manager = None
            self.access_control = None
            self.message_signer = None
        
        # Initialize streaming components
        self.sse_manager = SSEManager()
        self.subscription_manager = SubscriptionManager()
        
        # Initialize channel bridge
        self.channel_bridge = ChannelBridge(self.message_bus, self.subscription_manager)
        
        # Initialize conversation manager
        self.conversation_manager = ConversationManager(self.channel_bridge)
        
        # Initialize task coordinator
        self.task_coordinator = TaskCoordinator(self.task_manager)
        
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
        
        # Initialize channel bridge
        await self.channel_bridge.initialize()
        
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
        
        # Apply security middleware only if enabled
        if self.enable_security:
            apply_security_middleware(
                self.method_dispatcher,
                self.token_manager,
                self.access_control,
                exempt_methods=[
                    "agent.register",
                    "discovery.capability_map",
                    "discovery.find_for_capability",
                    "discovery.query",
                    "auth.login",
                    "auth.refresh"
                ]
            )
            logger.info("Security middleware applied to A2A service")
        else:
            logger.info("A2A security is disabled - no security middleware applied")
        
        self._initialized = True
        logger.info("A2A service initialized successfully")
    
    async def _register_hermes_methods(self):
        """Register Hermes-specific A2A methods"""
        
        # Forward agent methods to component registry
        async def agent_forward(
            agent_id: str, 
            method: str, 
            params: Dict[str, Any],
            _security_context: Optional[SecurityContext] = None
        ) -> Any:
            """Forward a method call to a specific agent"""
            # Get agent endpoint from registry
            agent = self.agent_registry.get(agent_id)
            if not agent:
                raise Exception(f"Agent {agent_id} not found")
            
            # TODO: Implement HTTP forwarding to agent endpoint
            # For now, publish to message bus
            message = {
                "method": method,
                "params": params
            }
            
            # Add security context if available
            if _security_context:
                message["from_agent"] = _security_context.agent_id
                message["authenticated"] = True
            
            await self.message_bus.publish(f"agent.{agent_id}.request", message)
            
            return {"forwarded": True, "agent_id": agent_id, "method": method}
        
        # Channel subscription management
        async def channel_subscribe(agent_id: str, channel: str) -> Dict[str, Any]:
            """Enhanced channel subscription with pattern support"""
            # Keep existing subscription tracking for compatibility
            if agent_id not in self.agent_subscriptions:
                self.agent_subscriptions[agent_id] = set()
            
            self.agent_subscriptions[agent_id].add(channel)
            
            # Create channel if it doesn't exist
            await self.message_bus.create_channel(channel, description=f"Channel for {channel}")
            
            # NEW: Create enhanced subscription with pattern support
            subscription_id = await self.channel_bridge.create_pattern_subscription(agent_id, channel)
            
            return {
                "success": True, 
                "agent_id": agent_id, 
                "channel": channel,
                "subscription_id": subscription_id  # NEW: Return subscription ID
            }
        
        async def channel_unsubscribe(agent_id: str, channel: str) -> Dict[str, Any]:
            """Unsubscribe an agent from a channel"""
            if agent_id in self.agent_subscriptions:
                self.agent_subscriptions[agent_id].discard(channel)
            
            return {"success": True, "agent_id": agent_id, "channel": channel}
        
        async def channel_publish(channel: str, message: Dict[str, Any], 
                                 sender_id: Optional[str] = None) -> Dict[str, Any]:
            """Enhanced channel publishing with metadata"""
            # Extract sender_id from message if not provided
            if not sender_id:
                sender_id = message.get("sender_id", "unknown")
            
            # NEW: Use bridge for enhanced publishing
            result = await self.channel_bridge.publish_with_metadata(
                channel=channel,
                sender_id=sender_id,
                content=message,
                metadata=message.get("metadata", {})
            )
            
            # Get subscribers (keep for compatibility)
            subscribers = [
                agent_id for agent_id, channels in self.agent_subscriptions.items()
                if channel in channels
            ]
            
            result["subscribers"] = len(subscribers)
            return result
        
        # New enhanced channel methods
        async def channel_list(pattern: Optional[str] = None) -> List[Dict[str, Any]]:
            """List channels with optional pattern filter"""
            return await self.channel_bridge.list_channels(pattern)

        async def channel_info(channel: str) -> Optional[Dict[str, Any]]:
            """Get detailed channel information"""
            return await self.channel_bridge.get_channel_info(channel)

        async def channel_subscribe_pattern(agent_id: str, pattern: str) -> Dict[str, Any]:
            """Subscribe to channels matching pattern with wildcards"""
            subscription_id = await self.channel_bridge.create_pattern_subscription(
                agent_id, pattern
            )
            
            # Track in agent_subscriptions for compatibility
            if agent_id not in self.agent_subscriptions:
                self.agent_subscriptions[agent_id] = set()
            self.agent_subscriptions[agent_id].add(f"pattern:{pattern}")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "pattern": pattern,
                "subscription_id": subscription_id
            }
        
        # Conversation methods
        async def conversation_create(
            topic: str,
            created_by: str,
            description: Optional[str] = None,
            turn_taking_mode: str = "free_form",
            settings: Optional[Dict[str, Any]] = None,
            initial_participants: Optional[List[Dict[str, str]]] = None
        ) -> Dict[str, Any]:
            """Create a new multi-agent conversation"""
            mode = TurnTakingMode(turn_taking_mode)
            conversation = await self.conversation_manager.create_conversation(
                topic=topic,
                created_by=created_by,
                description=description,
                turn_taking_mode=mode,
                settings=settings,
                initial_participants=initial_participants
            )
            return conversation.to_summary()
        
        async def conversation_join(
            conversation_id: str,
            agent_id: str,
            role: Optional[str] = None
        ) -> Dict[str, Any]:
            """Join an existing conversation"""
            conv_role = ConversationRole(role) if role else None
            participant = await self.conversation_manager.join_conversation(
                conversation_id=conversation_id,
                agent_id=agent_id,
                role=conv_role
            )
            return {
                "success": True,
                "conversation_id": conversation_id,
                "agent_id": agent_id,
                "role": participant.role.value,
                "joined_at": participant.joined_at.isoformat()
            }
        
        async def conversation_leave(
            conversation_id: str,
            agent_id: str
        ) -> Dict[str, Any]:
            """Leave a conversation"""
            await self.conversation_manager.leave_conversation(
                conversation_id=conversation_id,
                agent_id=agent_id
            )
            return {
                "success": True,
                "conversation_id": conversation_id,
                "agent_id": agent_id
            }
        
        async def conversation_send(
            conversation_id: str,
            sender_id: str,
            content: Any,
            in_reply_to: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Send a message in a conversation"""
            message = await self.conversation_manager.send_message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                in_reply_to=in_reply_to,
                metadata=metadata
            )
            return {
                "success": True,
                "message_id": message.id,
                "timestamp": message.timestamp.isoformat()
            }
        
        async def conversation_list(
            agent_id: Optional[str] = None,
            state: Optional[str] = None
        ) -> List[Dict[str, Any]]:
            """List conversations"""
            conv_state = ConversationState(state) if state else None
            return await self.conversation_manager.list_conversations(
                agent_id=agent_id,
                state=conv_state
            )
        
        async def conversation_info(
            conversation_id: str,
            agent_id: Optional[str] = None
        ) -> Optional[Dict[str, Any]]:
            """Get conversation details"""
            conversation = await self.conversation_manager.get_conversation(
                conversation_id=conversation_id,
                agent_id=agent_id
            )
            return conversation.to_summary() if conversation else None
        
        async def conversation_request_turn(
            conversation_id: str,
            agent_id: str
        ) -> Dict[str, Any]:
            """Request a turn to speak"""
            position = await self.conversation_manager.request_turn(
                conversation_id=conversation_id,
                agent_id=agent_id
            )
            return {
                "success": True,
                "position": position,
                "can_speak_now": position is None
            }
        
        async def conversation_grant_turn(
            conversation_id: str,
            moderator_id: str,
            agent_id: str
        ) -> Dict[str, Any]:
            """Grant speaking turn (moderator only)"""
            await self.conversation_manager.grant_turn(
                conversation_id=conversation_id,
                moderator_id=moderator_id,
                agent_id=agent_id
            )
            return {
                "success": True,
                "agent_id": agent_id
            }
        
        async def conversation_end(
            conversation_id: str,
            agent_id: str
        ) -> Dict[str, Any]:
            """End a conversation"""
            await self.conversation_manager.end_conversation(
                conversation_id=conversation_id,
                agent_id=agent_id
            )
            return {
                "success": True,
                "conversation_id": conversation_id
            }
        
        # Register methods
        self.method_dispatcher.register_method("agent.forward", agent_forward)
        self.method_dispatcher.register_method("channel.subscribe", channel_subscribe)
        self.method_dispatcher.register_method("channel.unsubscribe", channel_unsubscribe)
        self.method_dispatcher.register_method("channel.publish", channel_publish)
        self.method_dispatcher.register_method("channel.list", channel_list)
        self.method_dispatcher.register_method("channel.info", channel_info)
        self.method_dispatcher.register_method("channel.subscribe_pattern", channel_subscribe_pattern)
        
        # Register conversation methods
        self.method_dispatcher.register_method("conversation.create", conversation_create)
        self.method_dispatcher.register_method("conversation.join", conversation_join)
        self.method_dispatcher.register_method("conversation.leave", conversation_leave)
        self.method_dispatcher.register_method("conversation.send", conversation_send)
        self.method_dispatcher.register_method("conversation.list", conversation_list)
        self.method_dispatcher.register_method("conversation.info", conversation_info)
        self.method_dispatcher.register_method("conversation.request_turn", conversation_request_turn)
        self.method_dispatcher.register_method("conversation.grant_turn", conversation_grant_turn)
        self.method_dispatcher.register_method("conversation.end", conversation_end)
        
        # Task coordination methods
        async def workflow_create(
            name: str,
            created_by: str,
            pattern: str = "sequential",
            description: Optional[str] = None,
            max_parallel: Optional[int] = None,
            retry_failed: bool = False,
            timeout_seconds: Optional[int] = None
        ) -> Dict[str, Any]:
            """Create a new task workflow"""
            workflow = await self.task_coordinator.create_workflow(
                name=name,
                created_by=created_by,
                pattern=CoordinationPattern(pattern),
                description=description,
                max_parallel=max_parallel,
                retry_failed=retry_failed,
                timeout_seconds=timeout_seconds
            )
            return workflow.model_dump()
        
        async def workflow_create_sequential(
            name: str,
            created_by: str,
            tasks: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """Create a sequential workflow"""
            workflow = await self.task_coordinator.create_sequential_workflow(
                name=name,
                created_by=created_by,
                task_definitions=tasks
            )
            return workflow.model_dump()
        
        async def workflow_create_parallel(
            name: str,
            created_by: str,
            tasks: List[Dict[str, Any]],
            max_parallel: Optional[int] = None
        ) -> Dict[str, Any]:
            """Create a parallel workflow"""
            workflow = await self.task_coordinator.create_parallel_workflow(
                name=name,
                created_by=created_by,
                task_definitions=tasks,
                max_parallel=max_parallel
            )
            return workflow.model_dump()
        
        async def workflow_create_pipeline(
            name: str,
            created_by: str,
            stages: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """Create a pipeline workflow"""
            workflow = await self.task_coordinator.create_pipeline_workflow(
                name=name,
                created_by=created_by,
                task_definitions=stages
            )
            return workflow.model_dump()
        
        async def workflow_create_fanout(
            name: str,
            created_by: str,
            source_task: Dict[str, Any],
            target_tasks: List[Dict[str, Any]]
        ) -> Dict[str, Any]:
            """Create a fan-out workflow"""
            workflow = await self.task_coordinator.create_fanout_workflow(
                name=name,
                created_by=created_by,
                source_task_def=source_task,
                target_task_defs=target_tasks
            )
            return workflow.model_dump()
        
        async def workflow_start(workflow_id: str) -> Dict[str, Any]:
            """Start executing a workflow"""
            await self.task_coordinator.start_workflow(workflow_id)
            return {"success": True, "workflow_id": workflow_id}
        
        async def workflow_cancel(
            workflow_id: str,
            reason: Optional[str] = None
        ) -> Dict[str, Any]:
            """Cancel a running workflow"""
            await self.task_coordinator.cancel_workflow(workflow_id, reason)
            return {"success": True, "workflow_id": workflow_id}
        
        async def workflow_info(workflow_id: str) -> Optional[Dict[str, Any]]:
            """Get workflow information"""
            workflow = await self.task_coordinator.get_workflow(workflow_id)
            return workflow.model_dump() if workflow else None
        
        async def workflow_list(
            created_by: Optional[str] = None,
            state: Optional[str] = None
        ) -> List[Dict[str, Any]]:
            """List workflows"""
            workflows = await self.task_coordinator.list_workflows(
                created_by=created_by,
                state=TaskState(state) if state else None
            )
            return [w.model_dump() for w in workflows]
        
        async def workflow_add_task(
            workflow_id: str,
            workflow_task_id: str,
            task_definition: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Add a task to an existing workflow"""
            workflow = await self.task_coordinator.get_workflow(workflow_id)
            if not workflow:
                raise InvalidRequestError(f"Workflow {workflow_id} not found")
            
            # Create the task
            task = self.task_manager.create_task(
                name=task_definition.get("name"),
                created_by=workflow.created_by,
                description=task_definition.get("description"),
                input_data=task_definition.get("input_data")
            )
            
            # Add to workflow
            workflow.add_task(workflow_task_id, task.id)
            
            return {"success": True, "task_id": task.id}
        
        async def workflow_add_dependency(
            workflow_id: str,
            predecessor_id: str,
            successor_id: str,
            dependency_type: str = "finish_to_start"
        ) -> Dict[str, Any]:
            """Add a dependency between tasks in a workflow"""
            workflow = await self.task_coordinator.get_workflow(workflow_id)
            if not workflow:
                raise InvalidRequestError(f"Workflow {workflow_id} not found")
            
            workflow.add_dependency(
                predecessor_id=predecessor_id,
                successor_id=successor_id,
                dependency_type=DependencyType(dependency_type)
            )
            
            return {"success": True}
        
        # Register task coordination methods
        self.method_dispatcher.register_method("workflow.create", workflow_create)
        self.method_dispatcher.register_method("workflow.create_sequential", workflow_create_sequential)
        self.method_dispatcher.register_method("workflow.create_parallel", workflow_create_parallel)
        self.method_dispatcher.register_method("workflow.create_pipeline", workflow_create_pipeline)
        self.method_dispatcher.register_method("workflow.create_fanout", workflow_create_fanout)
        self.method_dispatcher.register_method("workflow.start", workflow_start)
        self.method_dispatcher.register_method("workflow.cancel", workflow_cancel)
        self.method_dispatcher.register_method("workflow.info", workflow_info)
        self.method_dispatcher.register_method("workflow.list", workflow_list)
        self.method_dispatcher.register_method("workflow.add_task", workflow_add_task)
        self.method_dispatcher.register_method("workflow.add_dependency", workflow_add_dependency)
    
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