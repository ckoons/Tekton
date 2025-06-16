"""
JSON-RPC Method Definitions and Dispatcher for A2A Protocol v2

Defines standard A2A methods and provides a dispatcher for handling them.
"""

from typing import Dict, List, Any, Callable, Optional, Union
import inspect
import logging

from .jsonrpc import JSONRPCRequest, JSONRPCResponse, create_error_response, create_success_response
from .errors import MethodNotFoundError, InvalidParamsError, InternalError
from .agent import AgentCard, AgentRegistry, AgentStatus
from .task import Task, TaskManager, TaskState
from .discovery import DiscoveryService, AgentQuery

logger = logging.getLogger(__name__)


class MethodDispatcher:
    """
    Dispatcher for JSON-RPC methods in the A2A protocol.
    
    Handles method registration, parameter validation, and execution.
    """
    
    def __init__(self):
        self._methods: Dict[str, Callable] = {}
        self._method_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_method(
        self,
        name: str,
        handler: Callable,
        description: Optional[str] = None,
        params_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a method handler"""
        self._methods[name] = handler
        self._method_metadata[name] = {
            "description": description or handler.__doc__,
            "params_schema": params_schema,
            "handler": handler.__name__
        }
    
    def register_class_methods(self, instance: Any, prefix: str = "") -> None:
        """Register all public methods from a class instance"""
        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if not name.startswith("_"):
                method_name = f"{prefix}.{name}" if prefix else name
                self.register_method(method_name, method)
    
    async def dispatch(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Dispatch a JSON-RPC request to the appropriate handler"""
        method_name = request.method
        
        # Check if method exists
        if method_name not in self._methods:
            return create_error_response(
                request.id,
                MethodNotFoundError(method_name).code,
                f"Method '{method_name}' not found"
            )
        
        handler = self._methods[method_name]
        
        try:
            # Extract parameters
            params = request.params or {}
            
            # Call handler based on parameter type
            if isinstance(params, dict):
                result = await self._call_with_kwargs(handler, params)
            elif isinstance(params, list):
                result = await self._call_with_args(handler, params)
            else:
                raise InvalidParamsError("Parameters must be dict or list")
            
            return create_success_response(request.id, result)
            
        except InvalidParamsError as e:
            return create_error_response(request.id, e.code, e.message, e.data)
        except Exception as e:
            logger.error(f"Error in method {method_name}: {e}", exc_info=True)
            return create_error_response(
                request.id,
                InternalError().code,
                "Internal error",
                str(e)
            )
    
    async def _call_with_kwargs(self, handler: Callable, params: Dict[str, Any]) -> Any:
        """Call handler with keyword arguments"""
        # Check if handler is async
        if inspect.iscoroutinefunction(handler):
            return await handler(**params)
        else:
            return handler(**params)
    
    async def _call_with_args(self, handler: Callable, params: List[Any]) -> Any:
        """Call handler with positional arguments"""
        # Check if handler is async
        if inspect.iscoroutinefunction(handler):
            return await handler(*params)
        else:
            return handler(*params)
    
    def list_methods(self) -> List[Dict[str, Any]]:
        """List all registered methods with metadata"""
        return [
            {
                "name": name,
                "description": meta["description"],
                "params_schema": meta["params_schema"]
            }
            for name, meta in self._method_metadata.items()
        ]


class StandardA2AMethods:
    """
    Standard A2A protocol methods implementation.
    
    Provides core functionality for agent management, task handling, and discovery.
    """
    
    def __init__(
        self,
        agent_registry: AgentRegistry,
        task_manager: TaskManager,
        discovery_service: DiscoveryService
    ):
        self.agent_registry = agent_registry
        self.task_manager = task_manager
        self.discovery_service = discovery_service
    
    # Agent Management Methods
    
    async def agent_register(self, agent_card: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent in the system"""
        # If no ID provided, use the create factory method
        if 'id' not in agent_card:
            agent = AgentCard.create(**agent_card)
        else:
            agent = AgentCard(**agent_card)
        
        self.agent_registry.register(agent)
        return {"success": True, "agent_id": agent.id}
    
    async def agent_unregister(self, agent_id: str) -> Dict[str, Any]:
        """Unregister an agent from the system"""
        agent = self.agent_registry.unregister(agent_id)
        return {
            "success": agent is not None,
            "message": "Agent unregistered" if agent else "Agent not found"
        }
    
    async def agent_heartbeat(self, agent_id: str) -> Dict[str, Any]:
        """Update agent heartbeat"""
        success = self.agent_registry.update_heartbeat(agent_id)
        return {"success": success}
    
    async def agent_update_status(
        self,
        agent_id: str,
        status: str
    ) -> Dict[str, Any]:
        """Update agent status"""
        agent_status = AgentStatus(status)
        success = self.agent_registry.update_status(agent_id, agent_status)
        return {"success": success}
    
    async def agent_get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        agent = self.agent_registry.get(agent_id)
        return agent.model_dump() if agent else None
    
    async def agent_list(self) -> Dict[str, Any]:
        """List all online agents"""
        agents = self.agent_registry.list_online()
        return {"agents": [agent.model_dump() for agent in agents]}
    
    # Discovery Methods
    
    async def discovery_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query for agents based on criteria"""
        agent_query = AgentQuery(**query)
        result = self.discovery_service.discover(agent_query)
        return result.model_dump()
    
    async def discovery_find_for_method(self, method: str) -> Optional[Dict[str, Any]]:
        """Find best agent for a specific method"""
        agent = self.discovery_service.find_agent_for_method(method)
        return agent.model_dump() if agent else None
    
    async def discovery_find_for_capability(
        self,
        capability: str
    ) -> List[Dict[str, Any]]:
        """Find agents with specific capability"""
        agents = self.discovery_service.find_agents_for_capability(capability)
        return [agent.model_dump() for agent in agents]
    
    async def discovery_capability_map(self) -> Dict[str, List[str]]:
        """Get capability to agent mapping"""
        return self.discovery_service.get_capability_map()
    
    async def discovery_method_map(self) -> Dict[str, List[str]]:
        """Get method to agent mapping"""
        return self.discovery_service.get_method_map()
    
    # Task Management Methods
    
    async def task_create(
        self,
        name: str,
        created_by: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new task"""
        # If created_by not provided, use "system" or extract from context
        if created_by is None:
            created_by = kwargs.pop('agent_id', 'system')
        
        task = self.task_manager.create_task(name, created_by, **kwargs)
        return {"task_id": task.id, "task": task.model_dump()}
    
    async def task_assign(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """Assign task to an agent"""
        task = self.task_manager.assign_task(task_id, agent_id)
        return task.model_dump()
    
    async def task_update_state(
        self,
        task_id: str,
        state: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task state"""
        task_state = TaskState(state)
        task = self.task_manager.update_task_state(task_id, task_state, message)
        return task.model_dump()
    
    async def task_update_progress(
        self,
        task_id: str,
        progress: float,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update task progress"""
        task = self.task_manager.update_task_progress(task_id, progress, message)
        return task.model_dump()
    
    async def task_complete(
        self,
        task_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete a task"""
        task = self.task_manager.complete_task(task_id, output_data, message)
        return task.model_dump()
    
    async def task_fail(
        self,
        task_id: str,
        error_data: Dict[str, Any],
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fail a task"""
        task = self.task_manager.fail_task(task_id, error_data, message)
        return task.model_dump()
    
    async def task_cancel(
        self,
        task_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel a task"""
        task = self.task_manager.cancel_task(task_id, reason)
        return task.model_dump()
    
    async def task_get(self, task_id: str) -> Dict[str, Any]:
        """Get task information"""
        task = self.task_manager.get_task(task_id)
        return task.model_dump()
    
    async def task_list(
        self,
        agent_id: Optional[str] = None,
        state: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filters"""
        task_state = TaskState(state) if state else None
        tasks = self.task_manager.list_tasks(agent_id, task_state, created_by)
        return [task.model_dump() for task in tasks]


def create_standard_dispatcher(
    agent_registry: AgentRegistry,
    task_manager: TaskManager,
    discovery_service: DiscoveryService
) -> MethodDispatcher:
    """Create a dispatcher with standard A2A methods registered"""
    dispatcher = MethodDispatcher()
    
    # Create standard methods instance
    methods = StandardA2AMethods(agent_registry, task_manager, discovery_service)
    
    # Register agent methods
    dispatcher.register_method("agent.register", methods.agent_register)
    dispatcher.register_method("agent.unregister", methods.agent_unregister)
    dispatcher.register_method("agent.heartbeat", methods.agent_heartbeat)
    dispatcher.register_method("agent.update_status", methods.agent_update_status)
    dispatcher.register_method("agent.get", methods.agent_get)
    dispatcher.register_method("agent.list", methods.agent_list)
    
    # Register discovery methods
    dispatcher.register_method("discovery.query", methods.discovery_query)
    dispatcher.register_method("discovery.find_for_method", methods.discovery_find_for_method)
    dispatcher.register_method("discovery.find_for_capability", methods.discovery_find_for_capability)
    dispatcher.register_method("discovery.capability_map", methods.discovery_capability_map)
    dispatcher.register_method("discovery.method_map", methods.discovery_method_map)
    
    # Register task methods
    dispatcher.register_method("task.create", methods.task_create)
    dispatcher.register_method("task.assign", methods.task_assign)
    dispatcher.register_method("task.update_state", methods.task_update_state)
    dispatcher.register_method("task.update_progress", methods.task_update_progress)
    dispatcher.register_method("task.complete", methods.task_complete)
    dispatcher.register_method("task.fail", methods.task_fail)
    dispatcher.register_method("task.cancel", methods.task_cancel)
    dispatcher.register_method("task.get", methods.task_get)
    dispatcher.register_method("task.list", methods.task_list)
    
    return dispatcher