"""
FastMCP tool definitions for Ergon.

This module defines FastMCP tools for Ergon's core functionality:
- Agent management tools
- Workflow management tools
- Task management tools
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

# Check if FastMCP is available
try:
    from tekton.mcp.fastmcp import mcp_tool, mcp_capability
    fastmcp_available = True
except ImportError:
    fastmcp_available = False
    # Define dummy decorators
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def mcp_capability(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# We'll use forward references for the Ergon types to avoid circular imports
from ..a2a_client import A2AClient

logger = logging.getLogger(__name__)

# =====================
# Agent Management Tools
# =====================

@mcp_capability(
    name="agent_management",
    description="Agent creation, updating, and management",
    modality="autonomous"
)
@mcp_tool(
    name="CreateAgent",
    description="Create a new autonomous agent",
    tags=["agent", "creation"],
    category="agent_management"
)
async def create_agent(
    agent_name: str,
    agent_description: Optional[str] = None,
    capabilities: Optional[Dict[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Create a new autonomous agent.
    
    Args:
        agent_name: Human-readable name for the agent
        agent_description: Optional description of the agent's purpose
        capabilities: Dictionary of capability types to capability names
        metadata: Additional metadata for the agent
        a2a_client: A2A client instance (injected)
        
    Returns:
        Created agent information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Generate a unique agent ID
        agent_id = f"agent-{uuid.uuid4()}"
        
        # Default empty capabilities if not provided
        if not capabilities:
            capabilities = {"processing": []}
        
        # Default empty metadata if not provided
        if not metadata:
            metadata = {}
        
        # Add agent creation timestamp
        metadata["created_at"] = datetime.utcnow().isoformat()
        
        # Create a new A2A client for this agent
        agent_client = A2AClient(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_description=agent_description,
            capabilities=capabilities,
            metadata=metadata
        )
        
        # Initialize and register the client
        await agent_client.initialize()
        registered = await agent_client.register()
        
        # Close the client after registration
        await agent_client.close()
        
        if registered:
            return {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "capabilities": capabilities,
                "metadata": metadata,
                "status": "registered"
            }
        else:
            return {"error": "Failed to register agent"}
    
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return {"error": f"Error creating agent: {str(e)}"}


@mcp_capability(
    name="agent_management",
    description="Agent creation, updating, and management",
    modality="autonomous"
)
@mcp_tool(
    name="UpdateAgent",
    description="Update an existing agent",
    tags=["agent", "update"],
    category="agent_management"
)
async def update_agent(
    agent_id: str,
    agent_name: Optional[str] = None,
    agent_description: Optional[str] = None,
    capabilities: Optional[Dict[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Update an existing agent.
    
    Args:
        agent_id: Agent identifier
        agent_name: Updated human-readable name for the agent
        agent_description: Updated description of the agent's purpose
        capabilities: Updated dictionary of capability types to capability names
        metadata: Updated additional metadata for the agent
        a2a_client: A2A client instance (injected)
        
    Returns:
        Updated agent information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Find agent by ID
        agents = await a2a_client.discover_agents()
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        
        if not agent:
            return {"error": f"Agent with ID {agent_id} not found"}
        
        # Update agent data
        updated_agent = {
            "agent_id": agent_id,
            "agent_name": agent_name or agent.get("agent_name", ""),
            "agent_description": agent_description or agent.get("agent_description", ""),
            "capabilities": capabilities or agent.get("capabilities", {}),
            "metadata": {**(agent.get("metadata", {})), **(metadata or {})}
        }
        
        # Add update timestamp
        updated_agent["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        # Create a new A2A client for this agent
        agent_client = A2AClient(
            agent_id=agent_id,
            agent_name=updated_agent["agent_name"],
            agent_description=updated_agent["agent_description"],
            capabilities=updated_agent["capabilities"],
            metadata=updated_agent["metadata"]
        )
        
        # Initialize and register the client (which updates the registration)
        await agent_client.initialize()
        registered = await agent_client.register()
        
        # Close the client after registration
        await agent_client.close()
        
        if registered:
            return {
                **updated_agent,
                "status": "updated"
            }
        else:
            return {"error": "Failed to update agent"}
    
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        return {"error": f"Error updating agent: {str(e)}"}


@mcp_capability(
    name="agent_management",
    description="Agent creation, updating, and management",
    modality="autonomous"
)
@mcp_tool(
    name="DeleteAgent",
    description="Delete an existing agent",
    tags=["agent", "delete"],
    category="agent_management"
)
async def delete_agent(
    agent_id: str,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Delete an existing agent.
    
    Args:
        agent_id: Agent identifier
        a2a_client: A2A client instance (injected)
        
    Returns:
        Deletion status
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Create a client with the agent ID to unregister
        agent_client = A2AClient(
            agent_id=agent_id,
            agent_name="Agent to delete"
        )
        
        # Initialize and unregister the client
        await agent_client.initialize()
        unregistered = await agent_client.unregister()
        
        # Close the client after unregistration
        await agent_client.close()
        
        if unregistered:
            return {
                "agent_id": agent_id,
                "status": "deleted"
            }
        else:
            return {"error": "Failed to delete agent"}
    
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        return {"error": f"Error deleting agent: {str(e)}"}


@mcp_capability(
    name="agent_management",
    description="Agent creation, updating, and management",
    modality="autonomous"
)
@mcp_tool(
    name="GetAgent",
    description="Get information about an agent",
    tags=["agent", "query"],
    category="agent_management"
)
async def get_agent(
    agent_id: str,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Get information about an agent.
    
    Args:
        agent_id: Agent identifier
        a2a_client: A2A client instance (injected)
        
    Returns:
        Agent information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Find agent by ID
        agents = await a2a_client.discover_agents()
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)
        
        if not agent:
            return {"error": f"Agent with ID {agent_id} not found"}
        
        return agent
    
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        return {"error": f"Error getting agent: {str(e)}"}


@mcp_capability(
    name="agent_management",
    description="Agent creation, updating, and management",
    modality="autonomous"
)
@mcp_tool(
    name="ListAgents",
    description="List all registered agents",
    tags=["agent", "query"],
    category="agent_management"
)
async def list_agents(
    capabilities: Optional[List[str]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    List all registered agents, optionally filtered by capabilities.
    
    Args:
        capabilities: Optional list of required capabilities to filter by
        a2a_client: A2A client instance (injected)
        
    Returns:
        List of registered agents
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Find agents, optionally filtered by capabilities
        agents = await a2a_client.discover_agents(capabilities)
        
        return {
            "agents": agents,
            "count": len(agents)
        }
    
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {"error": f"Error listing agents: {str(e)}"}


# =====================
# Workflow Management Tools
# =====================

@mcp_capability(
    name="workflow_management",
    description="Workflow creation, execution, and monitoring",
    modality="orchestration"
)
@mcp_tool(
    name="CreateWorkflow",
    description="Create a new workflow definition",
    tags=["workflow", "creation"],
    category="workflow_management"
)
async def create_workflow(
    name: str,
    tasks: Dict[str, Dict[str, Any]],
    description: Optional[str] = None,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Create a new workflow definition.
    
    Args:
        name: Workflow name
        tasks: Dictionary of task definitions
        description: Optional workflow description
        input_schema: Optional schema for workflow inputs
        output_schema: Optional schema for workflow outputs
        metadata: Optional workflow metadata
        a2a_client: A2A client instance (injected)
        
    Returns:
        Created workflow information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Generate a unique workflow ID
        workflow_id = f"workflow-{uuid.uuid4()}"
        
        # Default empty schemas if not provided
        if not input_schema:
            input_schema = {}
        
        if not output_schema:
            output_schema = {}
        
        # Default empty metadata if not provided
        if not metadata:
            metadata = {}
        
        # Add workflow creation timestamp
        metadata["created_at"] = datetime.utcnow().isoformat()
        
        # Create workflow definition
        workflow = {
            "workflow_id": workflow_id,
            "name": name,
            "description": description or "",
            "tasks": tasks,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "metadata": metadata
        }
        
        # Send message to register workflow
        message_id = await a2a_client.send_message(
            recipients=["workflow-registry"],
            content=workflow,
            message_type="request",
            intent="register_workflow"
        )
        
        if message_id:
            return {
                "workflow_id": workflow_id,
                "message_id": message_id,
                "status": "registered"
            }
        else:
            return {"error": "Failed to register workflow"}
    
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return {"error": f"Error creating workflow: {str(e)}"}


@mcp_capability(
    name="workflow_management",
    description="Workflow creation, execution, and monitoring",
    modality="orchestration"
)
@mcp_tool(
    name="UpdateWorkflow",
    description="Update an existing workflow definition",
    tags=["workflow", "update"],
    category="workflow_management"
)
async def update_workflow(
    workflow_id: str,
    name: Optional[str] = None,
    tasks: Optional[Dict[str, Dict[str, Any]]] = None,
    description: Optional[str] = None,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Update an existing workflow definition.
    
    Args:
        workflow_id: Workflow identifier
        name: Updated workflow name
        tasks: Updated dictionary of task definitions
        description: Updated workflow description
        input_schema: Updated schema for workflow inputs
        output_schema: Updated schema for workflow outputs
        metadata: Updated workflow metadata
        a2a_client: A2A client instance (injected)
        
    Returns:
        Updated workflow information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Send message to get workflow
        get_message_id = await a2a_client.send_message(
            recipients=["workflow-registry"],
            content={"workflow_id": workflow_id},
            message_type="request",
            intent="get_workflow"
        )
        
        if not get_message_id:
            return {"error": "Failed to retrieve workflow"}
        
        # Get response (simplified for this example)
        # In a real implementation, we would listen for the response
        workflow = {
            "workflow_id": workflow_id,
            "name": "Existing workflow",
            "description": "",
            "tasks": {},
            "input_schema": {},
            "output_schema": {},
            "metadata": {}
        }
        
        # Update workflow with provided values
        if name:
            workflow["name"] = name
        
        if tasks:
            workflow["tasks"] = tasks
        
        if description:
            workflow["description"] = description
        
        if input_schema:
            workflow["input_schema"] = input_schema
        
        if output_schema:
            workflow["output_schema"] = output_schema
        
        if metadata:
            workflow["metadata"] = {**workflow["metadata"], **metadata}
        
        # Add update timestamp
        workflow["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        # Send message to update workflow
        message_id = await a2a_client.send_message(
            recipients=["workflow-registry"],
            content=workflow,
            message_type="request",
            intent="update_workflow"
        )
        
        if message_id:
            return {
                "workflow_id": workflow_id,
                "message_id": message_id,
                "status": "updated"
            }
        else:
            return {"error": "Failed to update workflow"}
    
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        return {"error": f"Error updating workflow: {str(e)}"}


@mcp_capability(
    name="workflow_management",
    description="Workflow creation, execution, and monitoring",
    modality="orchestration"
)
@mcp_tool(
    name="ExecuteWorkflow",
    description="Execute a workflow with input parameters",
    tags=["workflow", "execution"],
    category="workflow_management"
)
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    execution_options: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Execute a workflow with input parameters.
    
    Args:
        workflow_id: Workflow identifier
        input_data: Input data for the workflow
        execution_options: Optional execution options
        a2a_client: A2A client instance (injected)
        
    Returns:
        Execution information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Generate a unique execution ID
        execution_id = f"execution-{uuid.uuid4()}"
        
        # Default empty execution options if not provided
        if not execution_options:
            execution_options = {}
        
        # Create execution request
        execution_request = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "input_data": input_data,
            "execution_options": execution_options,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send message to execute workflow
        message_id = await a2a_client.send_message(
            recipients=["workflow-executor"],
            content=execution_request,
            message_type="request",
            intent="execute_workflow"
        )
        
        if message_id:
            return {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "message_id": message_id,
                "status": "started"
            }
        else:
            return {"error": "Failed to start workflow execution"}
    
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return {"error": f"Error executing workflow: {str(e)}"}


@mcp_capability(
    name="workflow_management",
    description="Workflow creation, execution, and monitoring",
    modality="orchestration"
)
@mcp_tool(
    name="GetWorkflowStatus",
    description="Get status of a workflow execution",
    tags=["workflow", "status"],
    category="workflow_management"
)
async def get_workflow_status(
    execution_id: str,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Get status of a workflow execution.
    
    Args:
        execution_id: Execution identifier
        a2a_client: A2A client instance (injected)
        
    Returns:
        Execution status
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Send message to get execution status
        message_id = await a2a_client.send_message(
            recipients=["workflow-executor"],
            content={"execution_id": execution_id},
            message_type="request",
            intent="get_execution_status"
        )
        
        if not message_id:
            return {"error": "Failed to retrieve execution status"}
        
        # Get response (simplified for this example)
        # In a real implementation, we would listen for the response
        return {
            "execution_id": execution_id,
            "status": "running",
            "progress": 0.5,
            "tasks_completed": 2,
            "tasks_total": 4,
            "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "message_id": message_id
        }
    
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return {"error": f"Error getting workflow status: {str(e)}"}


# =====================
# Task Management Tools
# =====================

@mcp_capability(
    name="task_management",
    description="Task creation, assignment, and status updates",
    modality="orchestration"
)
@mcp_tool(
    name="CreateTask",
    description="Create a new task for an agent",
    tags=["task", "creation"],
    category="task_management"
)
async def create_task(
    name: str,
    description: str,
    required_capabilities: List[str],
    parameters: Dict[str, Any],
    deadline: Optional[str] = None,
    priority: str = "normal",
    preferred_agent: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Create a new task for an agent.
    
    Args:
        name: Task name
        description: Task description
        required_capabilities: Required capabilities for task execution
        parameters: Task parameters
        deadline: Optional deadline for task completion (ISO 8601 format)
        priority: Task priority (low, normal, high, critical)
        preferred_agent: Optional preferred agent ID
        metadata: Optional task metadata
        a2a_client: A2A client instance (injected)
        
    Returns:
        Created task information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Create task using A2A client
        task_id = await a2a_client.create_task(
            name=name,
            description=description,
            required_capabilities=required_capabilities,
            parameters=parameters,
            deadline=deadline,
            priority=priority,
            preferred_agent=preferred_agent,
            metadata=metadata or {}
        )
        
        if task_id:
            return {
                "task_id": task_id,
                "name": name,
                "status": "created"
            }
        else:
            return {"error": "Failed to create task"}
    
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {"error": f"Error creating task: {str(e)}"}


@mcp_capability(
    name="task_management",
    description="Task creation, assignment, and status updates",
    modality="orchestration"
)
@mcp_tool(
    name="AssignTask",
    description="Assign a task to a specific agent",
    tags=["task", "assignment"],
    category="task_management"
)
async def assign_task(
    task_id: str,
    agent_id: str,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Assign a task to a specific agent.
    
    Args:
        task_id: Task identifier
        agent_id: Agent identifier
        a2a_client: A2A client instance (injected)
        
    Returns:
        Assignment status
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Send message to assign task
        message_id = await a2a_client.send_message(
            recipients=["task-manager"],
            content={
                "task_id": task_id,
                "agent_id": agent_id,
                "operation": "assign"
            },
            message_type="request",
            intent="assign_task"
        )
        
        if message_id:
            return {
                "task_id": task_id,
                "agent_id": agent_id,
                "message_id": message_id,
                "status": "assigned"
            }
        else:
            return {"error": "Failed to assign task"}
    
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        return {"error": f"Error assigning task: {str(e)}"}


@mcp_capability(
    name="task_management",
    description="Task creation, assignment, and status updates",
    modality="orchestration"
)
@mcp_tool(
    name="UpdateTaskStatus",
    description="Update the status of a task",
    tags=["task", "status"],
    category="task_management"
)
async def update_task_status(
    task_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Update the status of a task.
    
    Args:
        task_id: Task identifier
        status: New task status (pending, assigned, in_progress, completed, failed, cancelled)
        result: Optional task result data
        a2a_client: A2A client instance (injected)
        
    Returns:
        Update status
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Send message to update task status
        message_id = await a2a_client.send_message(
            recipients=["task-manager"],
            content={
                "task_id": task_id,
                "status": status,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            },
            message_type="request",
            intent="update_task_status"
        )
        
        if message_id:
            return {
                "task_id": task_id,
                "status": status,
                "message_id": message_id,
                "updated": True
            }
        else:
            return {"error": "Failed to update task status"}
    
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        return {"error": f"Error updating task status: {str(e)}"}


@mcp_capability(
    name="task_management",
    description="Task creation, assignment, and status updates",
    modality="orchestration"
)
@mcp_tool(
    name="GetTask",
    description="Get information about a task",
    tags=["task", "query"],
    category="task_management"
)
async def get_task(
    task_id: str,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    Get information about a task.
    
    Args:
        task_id: Task identifier
        a2a_client: A2A client instance (injected)
        
    Returns:
        Task information
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Get task using A2A client
        task = await a2a_client.get_task(task_id)
        
        if task:
            return task
        else:
            return {"error": f"Task with ID {task_id} not found"}
    
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return {"error": f"Error getting task: {str(e)}"}


@mcp_capability(
    name="task_management",
    description="Task creation, assignment, and status updates",
    modality="orchestration"
)
@mcp_tool(
    name="ListTasks",
    description="List tasks with optional filtering",
    tags=["task", "query"],
    category="task_management"
)
async def list_tasks(
    status: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    """
    List tasks with optional filtering.
    
    Args:
        status: Optional status filter
        agent_id: Optional agent ID filter
        limit: Maximum number of tasks to return
        offset: Offset for pagination
        a2a_client: A2A client instance (injected)
        
    Returns:
        List of tasks
    """
    if not a2a_client:
        logger.error("A2A client not provided")
        return {"error": "A2A client not provided"}
    
    try:
        # Send message to list tasks
        message_id = await a2a_client.send_message(
            recipients=["task-manager"],
            content={
                "status": status,
                "agent_id": agent_id,
                "limit": limit,
                "offset": offset
            },
            message_type="request",
            intent="list_tasks"
        )
        
        if not message_id:
            return {"error": "Failed to list tasks"}
        
        # Get response (simplified for this example)
        # In a real implementation, we would listen for the response
        return {
            "tasks": [
                {
                    "task_id": f"task-{uuid.uuid4()}",
                    "name": "Example Task",
                    "status": status or "pending",
                    "agent_id": agent_id,
                    "created_at": datetime.utcnow().isoformat()
                }
                for _ in range(min(5, limit))  # Example with 5 tasks or limit, whichever is smaller
            ],
            "total": 5,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return {"error": f"Error listing tasks: {str(e)}"}


# =====================
# Tool Registration
# =====================

async def register_tools(
    a2a_client: Optional[A2AClient] = None,
    skip_tools: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Register all tools with the MCP service.
    
    Args:
        a2a_client: A2A client to use for registration
        skip_tools: List of tool names to skip
        
    Returns:
        Registration results
    """
    # Get all tools defined in this module
    tools = [
        create_agent, update_agent, delete_agent, get_agent, list_agents,
        create_workflow, update_workflow, execute_workflow, get_workflow_status,
        create_task, assign_task, update_task_status, get_task, list_tasks
    ]
    
    # Filter tools to skip if provided
    if skip_tools:
        tools = [tool for tool in tools if tool.__name__ not in skip_tools]
    
    # Create dependencies dict for injecting into tool handlers
    deps = {}
    if a2a_client:
        deps["a2a_client"] = a2a_client
    
    # Register tools with dependencies
    from tekton.mcp.fastmcp.utils.tooling import create_tool_registry, register_tools as register_tools_util
    registry = create_tool_registry("ergon")
    
    # Create a simple component manager with dependencies
    component_manager = type('ComponentManager', (), deps)()
    
    # Register all tools
    await register_tools_util(registry, tools, component_manager)
    
    results = [{"success": True, "tool": tool.__name__} for tool in tools]
    
    return {
        "registered": len([r for r in results if r.get("success")]),
        "failed": len([r for r in results if not r.get("success")]),
        "results": results
    }


def get_all_tools(a2a_client=None):
    """Get all Ergon MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    tools = []
    
    # Agent management tools
    tools.append(create_agent._mcp_tool_meta.to_dict())
    tools.append(update_agent._mcp_tool_meta.to_dict())
    tools.append(delete_agent._mcp_tool_meta.to_dict())
    tools.append(get_agent._mcp_tool_meta.to_dict())
    tools.append(list_agents._mcp_tool_meta.to_dict())
    
    # Workflow management tools
    tools.append(create_workflow._mcp_tool_meta.to_dict())
    tools.append(update_workflow._mcp_tool_meta.to_dict())
    tools.append(execute_workflow._mcp_tool_meta.to_dict())
    tools.append(get_workflow_status._mcp_tool_meta.to_dict())
    
    # Task management tools
    tools.append(create_task._mcp_tool_meta.to_dict())
    tools.append(assign_task._mcp_tool_meta.to_dict())
    tools.append(update_task_status._mcp_tool_meta.to_dict())
    tools.append(get_task._mcp_tool_meta.to_dict())
    tools.append(list_tasks._mcp_tool_meta.to_dict())
    
    logger.info(f"get_all_tools returning {len(tools)} Ergon MCP tools")
    return tools