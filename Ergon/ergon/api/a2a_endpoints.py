"""
A2A endpoints for Ergon API.

This module provides REST API endpoints for A2A functionality in Ergon.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Union

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from fastapi.responses import JSONResponse

from ..core.a2a_client import A2AClient
from ..utils.tekton_integration import get_component_port

# Setup logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(tags=["a2a"])

# Create shared A2A client
a2a_client = A2AClient(
    agent_id="ergon-api",
    agent_name="Ergon API Agent",
    capabilities=["agent_management", "workflow_execution", "task_processing"],
    supported_methods=["ergon.agent.create", "ergon.workflow.execute", "ergon.task.process"]
)

# Initialize client when module loads
@router.on_event("startup")
async def initialize_a2a_client():
    """Initialize the A2A client on startup."""
    await a2a_client.initialize()
    await a2a_client.register()

@router.on_event("shutdown")
async def close_a2a_client():
    """Close the A2A client on shutdown."""
    await a2a_client.close()

@router.post("/register")
async def register_agent(
    agent_data: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Register an agent with the A2A service.
    
    Args:
        agent_data: Agent data for registration
        
    Returns:
        Registration result
    """
    try:
        # Extract agent details
        agent_id = agent_data.get("agent_id", f"ergon-agent-{uuid.uuid4()}")
        agent_name = agent_data.get("agent_name", "Ergon Agent")
        agent_version = agent_data.get("agent_version", "0.1.0")
        capabilities = agent_data.get("capabilities", ["task_execution", "workflow_management"])
        metadata = agent_data.get("metadata", {})
        
        # Create a new A2A client for this agent
        agent_client = A2AClient(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_version=agent_version,
            capabilities=capabilities
        )
        
        # Initialize and register the client
        await agent_client.initialize()
        registered = await agent_client.register()
        
        # Close the client after registration
        await agent_client.close()
        
        if registered:
            return {"success": True, "agent_id": agent_id}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to register agent"}
            )
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Registration error: {str(e)}"}
        )

@router.get("/agents")
async def discover_agents(
    capabilities: Optional[List[str]] = Query(None, description="Required capabilities"),
) -> List[Dict[str, Any]]:
    """
    Discover agents with specific capabilities.
    
    Args:
        capabilities: List of required capabilities
        
    Returns:
        List of discovered agents
    """
    try:
        agents = await a2a_client.discover_agents(capabilities)
        return agents
    except Exception as e:
        logger.error(f"Error discovering agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error discovering agents: {str(e)}"
        )

@router.post("/messages/forward")
async def forward_message(
    message_data: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Forward a message to another agent via A2A.
    
    Args:
        message_data: Message data containing agent_id, method, and params
        
    Returns:
        Forwarding result
    """
    try:
        # Extract forwarding details
        agent_id = message_data.get("agent_id")
        method = message_data.get("method")
        params = message_data.get("params", {})
        
        if not agent_id or not method:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "agent_id and method are required"}
            )
        
        # Forward the message
        result = await a2a_client.forward_to_agent(
            agent_id=agent_id,
            method=method,
            params=params
        )
        
        if result:
            return {
                "success": True,
                "result": result
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to forward message"}
            )
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Message forwarding error: {str(e)}"}
        )

@router.post("/tasks/create")
async def create_task(
    task_data: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Create a task for other agents.
    
    Args:
        task_data: Task data
        
    Returns:
        Task creation result
    """
    try:
        # Extract task details
        name = task_data.get("name", "Unnamed Task")
        description = task_data.get("description")
        input_data = task_data.get("input_data", {})
        priority = task_data.get("priority", "normal")
        
        # Create the task
        task_result = await a2a_client.create_task(
            name=name,
            description=description,
            input_data=input_data,
            priority=priority
        )
        
        if task_result:
            return {"success": True, "task_id": task_result.get("id")}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to create task"}
            )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Task creation error: {str(e)}"}
        )

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str = Path(..., description="Task ID to retrieve"),
) -> Dict[str, Any]:
    """
    Get a task by ID.
    
    Args:
        task_id: ID of the task to retrieve
        
    Returns:
        Task details
    """
    try:
        task = await a2a_client.get_task(task_id)
        if task:
            return task
        else:
            return JSONResponse(
                status_code=404,
                content={"error": f"Task with ID {task_id} not found"}
            )
    except Exception as e:
        logger.error(f"Error retrieving task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task: {str(e)}"
        )

@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str = Path(..., description="Task ID to complete"),
    result: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Complete a task.
    
    Args:
        task_id: ID of the task to complete
        result: Task result containing output_data and message
        
    Returns:
        Task completion result
    """
    try:
        output_data = result.get("output_data")
        message = result.get("message")
        
        success = await a2a_client.complete_task(
            task_id=task_id,
            output_data=output_data,
            message=message
        )
        if success:
            return {"success": True, "task_id": task_id}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to complete task"}
            )
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Task completion error: {str(e)}"}
        )

@router.post("/channels/subscribe")
async def subscribe_to_channel(
    channel_data: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Subscribe to a message channel.
    
    Args:
        channel_data: Channel subscription data
        
    Returns:
        Subscription result
    """
    try:
        channel = channel_data.get("channel")
        if not channel:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "channel is required"}
            )
        
        success = await a2a_client.subscribe_to_channel(channel)
        
        if success:
            return {"success": True, "channel": channel}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to subscribe to channel"}
            )
    except Exception as e:
        logger.error(f"Error subscribing to channel: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Channel subscription error: {str(e)}"}
        )

@router.post("/channels/publish")
async def publish_to_channel(
    channel_data: Dict[str, Any] = Body(...),
) -> Dict[str, Any]:
    """
    Publish a message to a channel.
    
    Args:
        channel_data: Channel publish data
        
    Returns:
        Publish result
    """
    try:
        channel = channel_data.get("channel")
        message = channel_data.get("message", {})
        
        if not channel:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "channel is required"}
            )
        
        success = await a2a_client.publish_to_channel(channel, message)
        
        if success:
            return {"success": True, "channel": channel}
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to publish to channel"}
            )
    except Exception as e:
        logger.error(f"Error publishing to channel: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Channel publish error: {str(e)}"}
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Check A2A client health.
    
    Returns:
        Health status
    """
    # Perform a simple check by trying to discover agents
    try:
        if not a2a_client.registered:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "A2A client not registered"
                }
            )
            
        # Try to send heartbeat as a health check
        heartbeat_success = await a2a_client.heartbeat()
        
        return {
            "status": "ok" if heartbeat_success else "degraded",
            "agent_id": a2a_client.agent_id,
            "agent_name": a2a_client.agent_name,
            "hermes_url": a2a_client.hermes_url,
            "registered": a2a_client.registered,
            "heartbeat": heartbeat_success
        }
    except Exception as e:
        logger.error(f"A2A health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": f"A2A health check failed: {str(e)}"
            }
        )