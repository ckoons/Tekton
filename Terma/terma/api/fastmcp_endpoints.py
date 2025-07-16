"""
FastMCP endpoints for Terma.

This module provides FastAPI endpoints for MCP (Model Context Protocol) integration,
allowing external systems to interact with Terma's terminal management, LLM integration,
and system integration capabilities.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import asyncio
import os
from datetime import datetime

from tekton.mcp.fastmcp.server import FastMCPServer
from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
from tekton.mcp.fastmcp.exceptions import FastMCPError

# Add landmarks if available
try:
    from landmarks import api_contract, integration_point
except ImportError:
    # Define no-op decorators if landmarks not available
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator

from terma.core.mcp.tools import (
    terminal_management_tools,
    llm_integration_tools,
    system_integration_tools
)
from terma.core.mcp.capabilities import (
    TerminalManagementCapability,
    LLMIntegrationCapability,
    SystemIntegrationCapability
)


class MCPRequest(BaseModel):
    """Request model for MCP tool execution."""
    tool_name: str
    arguments: Dict[str, Any]


class MCPResponse(BaseModel):
    """Response model for MCP tool execution."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Create FastMCP server instance
fastmcp_server = FastMCPServer(
    name="terma",
    version="0.1.0",
    description="Terma Terminal Management, LLM Integration, and System Integration MCP Server"
)

# Register capabilities and tools
fastmcp_server.register_capability(TerminalManagementCapability())
fastmcp_server.register_capability(LLMIntegrationCapability())
fastmcp_server.register_capability(SystemIntegrationCapability())

# Register all tools
for tool in terminal_management_tools + llm_integration_tools + system_integration_tools:
    fastmcp_server.register_tool(tool)


# Create router for MCP endpoints
mcp_router = APIRouter(prefix="/api/mcp/v2")

# Add standard MCP endpoints using shared utilities
add_mcp_endpoints(mcp_router, fastmcp_server)


# Additional Terma-specific MCP endpoints
@mcp_router.get("/terminal-status")
async def get_terminal_status() -> Dict[str, Any]:
    """
    Get overall Terma terminal system status.
    
    Returns:
        Dictionary containing Terma system status and capabilities
    """
    try:
        # Mock terminal status - real implementation would check actual terminal sessions
        return {
            "success": True,
            "status": "operational",
            "service": "terma-terminal-manager",
            "capabilities": [
                "terminal_management",
                "llm_integration", 
                "system_integration"
            ],
            "active_sessions": 3,  # Would query actual session manager
            "mcp_tools": len(terminal_management_tools + llm_integration_tools + system_integration_tools),
            "terminal_engine_status": "ready",
            "websocket_status": "active",
            "llm_adapter_connected": True,
            "message": "Terma terminal management and integration engine is operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get terminal status: {str(e)}")


@mcp_router.post("/execute-terminal-workflow")
async def execute_terminal_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a predefined terminal management workflow.
    
    Args:
        workflow_name: Name of the workflow to execute
        parameters: Parameters for the workflow
        
    Returns:
        Dictionary containing workflow execution results
    """
    try:
        predefined_workflows = {
            "terminal_session_optimization": _execute_session_optimization_workflow,
            "llm_assisted_troubleshooting": _execute_troubleshooting_workflow,
            "multi_component_terminal_integration": _execute_integration_workflow,
            "terminal_performance_analysis": _execute_performance_analysis_workflow
        }
        
        if workflow_name not in predefined_workflows:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow: {workflow_name}. Available workflows: {list(predefined_workflows.keys())}"
            )
        
        workflow_func = predefined_workflows[workflow_name]
        result = await workflow_func(parameters)
        
        return {
            "success": True,
            "workflow_name": workflow_name,
            "execution_result": result,
            "message": f"Workflow '{workflow_name}' executed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@mcp_router.get("/terminal-health")
async def get_terminal_health() -> Dict[str, Any]:
    """
    Get comprehensive Terma terminal system health information.
    
    Returns:
        Dictionary containing detailed health information
    """
    try:
        import random
        from datetime import datetime
        
        # Mock comprehensive health check
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "components": {
                "session_manager": {
                    "status": "active",
                    "active_sessions": random.randint(1, 10),
                    "memory_usage_mb": random.randint(50, 150),
                    "uptime_hours": round(random.uniform(1.0, 100.0), 2)
                },
                "websocket_server": {
                    "status": "active",
                    "active_connections": random.randint(1, 10),
                    "message_rate_per_minute": random.randint(10, 100),
                    "last_heartbeat": datetime.now().isoformat()
                },
                "llm_integration": {
                    "status": "connected",
                    "provider": "llm_adapter",
                    "response_time_ms": random.randint(100, 500),
                    "requests_today": random.randint(50, 500)
                },
                "system_integration": {
                    "status": "active",
                    "connected_components": ["hermes", "hephaestus"],
                    "sync_status": "up_to_date",
                    "last_sync": datetime.now().isoformat()
                }
            },
            "performance_metrics": {
                "cpu_usage_percent": round(random.uniform(1.0, 15.0), 2),
                "memory_usage_percent": round(random.uniform(10.0, 40.0), 2),
                "disk_usage_percent": round(random.uniform(5.0, 25.0), 2),
                "network_throughput_kbps": random.randint(100, 1000)
            },
            "mcp_statistics": {
                "total_tools": len(terminal_management_tools + llm_integration_tools + system_integration_tools),
                "total_capabilities": 3,
                "requests_handled_today": random.randint(100, 1000),
                "average_response_time_ms": random.randint(50, 200)
            }
        }
        
        return {
            "success": True,
            "health": health_data,
            "recommendations": _generate_health_recommendations(health_data),
            "message": "Terminal health check completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@mcp_router.post("/terminal-session-bulk-action")
async def terminal_session_bulk_action(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform bulk actions on multiple terminal sessions.
    
    Args:
        request: Dictionary containing:
            - action: Action to perform on sessions
            - session_filters: Filters to select sessions
            - parameters: Additional parameters for the action
        
    Returns:
        Dictionary containing bulk action results
    """
    try:
        import random
        from datetime import datetime
        import uuid
        
        # Extract parameters from request
        action = request.get("action")
        session_filters = request.get("session_filters", {})
        parameters = request.get("parameters")
        
        if not action:
            raise HTTPException(status_code=400, detail="Action is required")
        
        valid_actions = ["backup", "restart", "optimize", "monitor", "cleanup"]
        if action not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Valid actions: {valid_actions}"
            )
        
        # Mock session selection based on filters
        selected_sessions = []
        num_sessions = random.randint(1, 5)
        
        for i in range(num_sessions):
            session = {
                "session_id": str(uuid.uuid4())[:8],
                "shell_type": random.choice(["bash", "zsh", "fish"]),
                "uptime_minutes": random.randint(5, 120),
                "status": random.choice(["active", "idle", "busy"])
            }
            selected_sessions.append(session)
        
        # Execute bulk action
        action_results = []
        for session in selected_sessions:
            session_result = {
                "session_id": session["session_id"],
                "action": action,
                "status": "completed",
                "execution_time_ms": random.randint(100, 1000),
                "details": _generate_action_details(action, session)
            }
            action_results.append(session_result)
        
        bulk_result = {
            "bulk_action_id": str(uuid.uuid4())[:8],
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "sessions_targeted": len(selected_sessions),
            "sessions_processed": len(action_results),
            "success_rate": 100,  # Mock 100% success
            "total_execution_time_ms": sum(r["execution_time_ms"] for r in action_results),
            "results": action_results
        }
        
        return {
            "success": True,
            "bulk_action": bulk_result,
            "summary": {
                "action": action,
                "sessions_affected": len(selected_sessions),
                "execution_time": f"{bulk_result['total_execution_time_ms']}ms",
                "all_successful": True
            },
            "message": f"Bulk action '{action}' completed on {len(selected_sessions)} sessions"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk action failed: {str(e)}")


@mcp_router.post("/tools/launch_terminal")
@api_contract(
    title="Launch aish Terminal via MCP",
    endpoint="/api/mcp/v2/tools/launch_terminal",
    method="POST",
    request_schema={
        "name": "string (optional)",
        "working_dir": "string (optional)",
        "purpose": "string (optional)",
        "template": "string (optional)"
    },
    response_schema={
        "success": "bool",
        "pid": "int",
        "terminal_app": "string",
        "working_directory": "string",
        "aish_enabled": "bool",
        "message": "string"
    },
    integration_date="2025-07-02"
)
@integration_point(
    title="MCP to Terminal Launcher Bridge",
    target_component="terminal_launcher_impl",
    protocol="Function call",
    data_flow="MCP request → TerminalLauncher → aish-proxy → Native terminal",
    description="Bridges MCP API requests to native terminal launching with aish"
)
async def mcp_launch_terminal(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Launch a terminal with aish integration.
    
    This endpoint allows external systems to launch aish-enabled terminals
    through the MCP interface.
    
    Args:
        request: Dictionary containing:
            - name: Optional terminal name
            - working_dir: Optional working directory (defaults to user home)
            - purpose: Optional AI context/purpose
            - template: Optional template name
            
    Returns:
        Dictionary containing:
            - success: Whether the launch was successful
            - pid: Process ID of the launched terminal
            - terminal_app: The terminal application used
            - message: Status message
    """
    try:
        import logging
        logger = logging.getLogger("terma.mcp")
        logger.info("="*60)
        logger.info(f"MCP LAUNCH TERMINAL REQUEST RECEIVED")
        logger.info(f"Request details: {request}")
        logger.info(f"Request ID: {id(request)}")
        logger.info("="*60)
        
        from terma.core.terminal_launcher_impl import TerminalLauncher, TerminalConfig
        
        # Create launcher instance
        launcher = TerminalLauncher()
        
        # Create config from request
        config = TerminalConfig(
            name=request.get("name", "aish Terminal"),
            working_dir=request.get("working_dir"),  # Will default to home in launcher
            purpose=request.get("purpose"),
            env={
                "TEKTON_ENABLED": "true",
                "AISH_ACTIVE": "1"
            }
        )
        
        # Handle startup command if provided
        startup_cmd = request.get("startup_command")
        if startup_cmd:
            config.env["TERMA_STARTUP_CMD"] = startup_cmd
        
        # Apply template if specified
        template_name = request.get("template")
        if template_name:
            from terma.core.terminal_launcher_impl import TerminalTemplates
            template = TerminalTemplates.get_template(template_name)
            if template:
                # Merge template with provided config
                if not config.name or config.name == "aish Terminal":
                    config.name = template.name
                config.env.update(template.env)
                if not config.purpose and template.purpose:
                    config.purpose = template.purpose
                # Set the template name on the config
                config.template = template_name
        
        # Launch the terminal
        logger.info(f"Calling launcher.launch_terminal with config: name={config.name}")
        pid = launcher.launch_terminal(config)
        logger.info(f"Terminal launched successfully with PID: {pid}")
        logger.info("="*60)
        
        return {
            "success": True,
            "pid": pid,
            "terminal_app": config.app or launcher.get_default_terminal(),
            "working_directory": config.working_dir or os.path.expanduser("~"),
            "aish_enabled": True,
            "message": "Successfully launched aish-enabled terminal"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to launch terminal: {str(e)}"
        )


@mcp_router.get("/terminals/list")
@api_contract(
    title="List Active Terminals",
    endpoint="/api/mcp/v2/terminals/list",
    method="GET",
    response_schema={
        "success": "bool",
        "terminals": "array of terminal objects",
        "count": "int"
    },
    description="Get list of all tracked terminals with their status"
)
async def list_terminals() -> Dict[str, Any]:
    """
    Get list of all active terminals.
    
    Returns:
        Dictionary containing list of terminals with their details
    """
    try:
        from terma.core.terminal_launcher_impl import TerminalLauncher
        
        launcher = TerminalLauncher()
        terminals = launcher.list_terminals()
        
        # Convert TerminalInfo objects to dictionaries
        terminal_list = []
        for term in terminals:
            terminal_dict = {
                "pid": term.pid,
                "name": term.config.name,
                "status": term.status,
                "launched_at": term.launched_at.isoformat(),
                "platform": term.platform,
                "terminal_app": term.terminal_app,
                "working_dir": term.config.working_dir,
                "purpose": term.config.purpose,
                "template": getattr(term.config, 'template', None),
                "terma_id": term.terma_id,  # Include terma_id
                "last_heartbeat": term.last_heartbeat.isoformat() if term.last_heartbeat else None
            }
            terminal_list.append(terminal_dict)
        
        return {
            "success": True,
            "terminals": terminal_list,
            "count": len(terminal_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list terminals: {str(e)}"
        )


@mcp_router.post("/terminals/{pid}/show")
@api_contract(
    title="Show Terminal",
    endpoint="/api/mcp/v2/terminals/{pid}/show",
    method="POST",
    response_schema={
        "success": "bool",
        "message": "string"
    },
    description="Bring a terminal window to the foreground"
)
async def show_terminal(pid: int) -> Dict[str, Any]:
    """
    Bring a terminal to the foreground.
    
    Args:
        pid: Process ID of the terminal
        
    Returns:
        Dictionary with success status
    """
    try:
        from terma.core.terminal_launcher_impl import TerminalLauncher
        
        launcher = TerminalLauncher()
        success = launcher.show_terminal(pid)
        
        if success:
            return {
                "success": True,
                "message": f"Terminal {pid} brought to foreground"
            }
        else:
            return {
                "success": False,
                "message": f"Could not show terminal {pid} (may not exist or not supported on this platform)"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to show terminal: {str(e)}"
        )


@mcp_router.post("/terminals/{pid}/terminate")
@api_contract(
    title="Terminate Terminal",
    endpoint="/api/mcp/v2/terminals/{pid}/terminate",
    method="POST",
    response_schema={
        "success": "bool",
        "message": "string"
    },
    description="Terminate a terminal process"
)
async def terminate_terminal(pid: int) -> Dict[str, Any]:
    """
    Terminate a terminal.
    
    Args:
        pid: Process ID of the terminal
        
    Returns:
        Dictionary with success status
    """
    try:
        from terma.core.terminal_launcher_impl import TerminalLauncher
        
        launcher = TerminalLauncher()
        success = launcher.terminate_terminal(pid)
        
        if success:
            return {
                "success": True,
                "message": f"Terminal {pid} terminated"
            }
        else:
            return {
                "success": False,
                "message": f"Could not terminate terminal {pid} (may not exist)"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to terminate terminal: {str(e)}"
        )


@mcp_router.post("/terminals/heartbeat")
@api_contract(
    title="Terminal Heartbeat",
    endpoint="/api/mcp/v2/terminals/heartbeat",
    method="POST",
    request_schema={
        "terma_id": "string",
        "pid": "int",
        "name": "string",
        "working_dir": "string",
        "terminal_app": "string",
        "aish_version": "string",
        "timestamp": "string (ISO format)"
    },
    response_schema={
        "success": "bool",
        "message": "string"
    },
    description="Receive heartbeat from aish-enabled terminal"
)
async def terminal_heartbeat(heartbeat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Receive heartbeat from aish-enabled terminal.
    
    Heartbeats are sent every 30 seconds by the background thread in aish-proxy.
    This allows Terma to track active terminals even after restart.
    
    Args:
        heartbeat: Dictionary containing terminal status information
        
    Returns:
        Dictionary with success status
    """
    try:
        from terma.core.terminal_launcher_impl import get_terminal_roster
        
        roster = get_terminal_roster()
        roster.update_heartbeat(
            terma_id=heartbeat["terma_id"],
            heartbeat_data=heartbeat
        )
        
        # Check for command results in heartbeat
        if "command_results" in heartbeat and heartbeat["command_results"]:
            if not hasattr(roster, '_command_results'):
                roster._command_results = {}
            
            for result in heartbeat["command_results"]:
                roster._command_results[result["id"]] = result
        
        # Check for pending commands and messages to send back
        response = {
            "success": True,
            "message": "Heartbeat received"
        }
        
        # Collect all pending items
        pending_items = []
        
        # Add commands
        if hasattr(roster, '_command_queue'):
            terma_id = heartbeat["terma_id"]
            if terma_id in roster._command_queue and roster._command_queue[terma_id]:
                pending_items.extend(roster._command_queue[terma_id])
                roster._command_queue[terma_id] = []
        
        # Add messages
        if hasattr(roster, '_message_queue'):
            terma_id = heartbeat["terma_id"]
            if terma_id in roster._message_queue and roster._message_queue[terma_id]:
                pending_items.extend(roster._message_queue[terma_id])
                roster._message_queue[terma_id] = []
        
        # Include in response if any items
        if pending_items:
            response["commands"] = pending_items
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process heartbeat: {str(e)}"
        )


@mcp_router.post("/terminals/command")
@api_contract(
    title="Send Command to Terminal",
    endpoint="/api/mcp/v2/terminals/command",
    method="POST",
    request_schema={
        "terma_id": "string",
        "command": "string"
    },
    response_schema={
        "success": "bool",
        "command_id": "string",
        "message": "string"
    },
    description="Send a command to be executed in a terminal"
)
async def send_terminal_command(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a command to a terminal for execution.
    
    The command will be queued and executed by the heartbeat process.
    Results will be available via the status endpoint.
    
    Args:
        request: Dictionary containing terma_id and command
        
    Returns:
        Dictionary with command_id for tracking
    """
    try:
        import uuid
        from terma.core.terminal_launcher_impl import get_terminal_roster
        
        terma_id = request.get("terma_id")
        command = request.get("command")
        
        if not terma_id or not command:
            raise HTTPException(
                status_code=400,
                detail="Both terma_id and command are required"
            )
        
        roster = get_terminal_roster()
        terminal = roster.get_terminal(terma_id)
        
        if not terminal:
            raise HTTPException(
                status_code=404,
                detail=f"Terminal {terma_id} not found"
            )
        
        # Generate command ID
        command_id = str(uuid.uuid4())[:8]
        
        # Queue command for terminal
        # For now, store in roster (in real implementation, would use proper queue)
        if not hasattr(roster, '_command_queue'):
            roster._command_queue = {}
        if terma_id not in roster._command_queue:
            roster._command_queue[terma_id] = []
        
        roster._command_queue[terma_id].append({
            "id": command_id,
            "command": command,
            "status": "pending",
            "queued_at": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "command_id": command_id,
            "message": f"Command queued for terminal {terma_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send command: {str(e)}"
        )


@mcp_router.get("/terminals/command/{command_id}/status")
@api_contract(
    title="Get Command Status",
    endpoint="/api/mcp/v2/terminals/command/{command_id}/status",
    method="GET",
    response_schema={
        "success": "bool",
        "command_id": "string",
        "completed": "bool",
        "output": "string (optional)",
        "error": "string (optional)"
    },
    description="Check the status and result of a queued command"
)
async def get_command_status(command_id: str) -> Dict[str, Any]:
    """
    Get the status and result of a previously sent command.
    
    Args:
        command_id: The command ID returned from send_terminal_command
        
    Returns:
        Dictionary with command status and output
    """
    try:
        from terma.core.terminal_launcher_impl import get_terminal_roster
        
        roster = get_terminal_roster()
        
        # For now, check results in roster (in real implementation, would use proper storage)
        if not hasattr(roster, '_command_results'):
            roster._command_results = {}
        
        if command_id in roster._command_results:
            result = roster._command_results[command_id]
            return {
                "success": True,
                "command_id": command_id,
                "completed": True,
                "output": result.get("output", ""),
                "error": result.get("error")
            }
        
        # Check if still pending
        if hasattr(roster, '_command_queue'):
            for terma_id, commands in roster._command_queue.items():
                for cmd in commands:
                    if cmd["id"] == command_id:
                        return {
                            "success": True,
                            "command_id": command_id,
                            "completed": False
                        }
        
        # Not found
        return {
            "success": False,
            "command_id": command_id,
            "completed": False,
            "error": "Command not found"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get command status: {str(e)}"
        )


@mcp_router.post("/terminals/route-message")
@api_contract(
    title="Route Inter-Terminal Message",
    endpoint="/api/mcp/v2/terminals/route-message",
    method="POST",
    request_schema={
        "from": {"terma_id": "string", "name": "string"},
        "target": "string (name, @purpose, broadcast, or *)",
        "message": "string",
        "timestamp": "string",
        "type": "string"
    },
    response_schema={
        "success": "bool",
        "delivered_to": "array of terminal names",
        "error": "string (optional)"
    },
    description="Route messages between terminals based on target specification"
)
@integration_point(
    title="Inter-terminal Message Router",
    target_component="ActiveTerminalRoster",
    protocol="In-memory message queue",
    data_flow="Source terminal → Router → Target terminal(s) via heartbeat",
    integration_date="2025-07-09"
)
async def route_terminal_message(msg_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route a message between terminals.
    
    Target can be:
    - Terminal name (e.g., "bob")
    - Multiple names (e.g., "alice,bob")
    - Purpose group (e.g., "@planning")
    - "broadcast" (all except sender)
    - "*" (all including sender)
    
    Args:
        msg_data: Message data with from, target, message, etc.
        
    Returns:
        Dictionary with delivery status
    """
    try:
        from terma.core.terminal_launcher_impl import get_terminal_roster
        
        roster = get_terminal_roster()
        sender_id = msg_data["from"]["terma_id"]
        target = msg_data["target"]
        
        # Get all terminals
        all_terminals = roster.get_terminals()
        
        # Find target terminals
        target_terminals = []
        delivered_to = []
        
        if target == "broadcast":
            # All except sender
            target_terminals = [t for t in all_terminals 
                              if not t.get("terma_id", "").startswith(sender_id[:8])]
        elif target == "*":
            # All including sender
            target_terminals = all_terminals
        elif target.startswith("@"):
            # Purpose-based routing - match any word in purpose
            from shared.aish.src.core.purpose_matcher import match_purpose
            purpose_word = target[1:]  # Remove @ prefix
            matching_names = match_purpose(purpose_word, all_terminals)
            target_terminals = [t for t in all_terminals 
                              if t.get("name", "") in matching_names]
        elif "," in target:
            # Multiple named terminals
            names = [n.strip().lower() for n in target.split(",")]
            target_terminals = [t for t in all_terminals 
                              if t.get("name", "").lower() in names]
        else:
            # Single named terminal
            target_name = target.lower()
            target_terminals = [t for t in all_terminals 
                              if t.get("name", "").lower() == target_name]
        
        # Queue message for each target
        if not hasattr(roster, '_message_queue'):
            roster._message_queue = {}
        
        for term in target_terminals:
            terma_id = term["terma_id"]
            if terma_id not in roster._message_queue:
                roster._message_queue[terma_id] = []
            
            # Format message for display
            formatted_msg = {
                "type": "terminal_message",
                "from": msg_data["from"]["name"],
                "from_id": sender_id[:8],
                "message": msg_data["message"],
                "timestamp": msg_data["timestamp"],
                "routing": target if target.startswith("@") or target in ["broadcast", "*"] else "direct"
            }
            
            roster._message_queue[terma_id].append(formatted_msg)
            delivered_to.append(term["name"])
        
        return {
            "success": True,
            "delivered_to": delivered_to,
            "count": len(delivered_to)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "delivered_to": []
        }


@mcp_router.get("/terminals/{pid}/status")
@api_contract(
    title="Check Terminal Status",
    endpoint="/api/mcp/v2/terminals/{pid}/status",
    method="GET",
    response_schema={
        "success": "bool",
        "pid": "int",
        "running": "bool",
        "status": "string"
    },
    description="Check if a specific terminal is running"
)
async def check_terminal_status(pid: int) -> Dict[str, Any]:
    """
    Check if a specific terminal is running.
    
    Args:
        pid: Process ID of the terminal
        
    Returns:
        Dictionary with terminal status
    """
    try:
        from terma.core.terminal_launcher_impl import TerminalLauncher
        
        launcher = TerminalLauncher()
        is_running = launcher.is_terminal_running(pid)
        
        # Also check if we have info about this terminal
        terminals = launcher.list_terminals()
        terminal_info = next((t for t in terminals if t.pid == pid), None)
        
        return {
            "success": True,
            "pid": pid,
            "running": is_running,
            "status": terminal_info.status if terminal_info else ("running" if is_running else "not_found")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check terminal status: {str(e)}"
        )


@mcp_router.post("/purpose")
async def update_terminal_purpose(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a terminal's purpose.
    
    Request body:
        {
            "terminal": "terminal_name",
            "purpose": "CSV list of purposes"
        }
    """
    try:
        terminal_name = request.get("terminal", "").lower()
        purpose = request.get("purpose", "")
        
        if not terminal_name:
            raise HTTPException(
                status_code=400,
                detail="Terminal name is required"
            )
        
        # Get the roster and find the terminal
        from terma.core.terminal_launcher_impl import get_terminal_roster
        roster = get_terminal_roster()
        terminals = roster.get_terminals()
        
        # Find terminal by name
        updated = False
        terma_id = None
        for term in terminals:
            if term.get("name", "").lower() == terminal_name:
                # Update purpose in the roster
                term["purpose"] = purpose
                terma_id = term.get("terma_id")
                updated = True
                break
        
        if not updated:
            raise HTTPException(
                status_code=404,
                detail=f"Terminal '{terminal_name}' not found"
            )
        
        # Queue a command to update the terminal's environment
        if terma_id:
            # Create command queue if it doesn't exist
            if not hasattr(roster, '_command_queue'):
                roster._command_queue = {}
            
            if terma_id not in roster._command_queue:
                roster._command_queue[terma_id] = []
            
            # Queue export command
            import uuid
            command = {
                "id": str(uuid.uuid4()),
                "command": f"export TEKTON_TERMINAL_PURPOSE='{purpose}'",
                "type": "environment_update"
            }
            roster._command_queue[terma_id].append(command)
            
            # Also queue a message to inform the CI
            if not hasattr(roster, '_message_queue'):
                roster._message_queue = {}
            
            if terma_id not in roster._message_queue:
                roster._message_queue[terma_id] = []
            
            # Create informative message
            message = {
                "type": "terminal_message",
                "from": "Tekton System",
                "from_id": "system",
                "message": f"Your purpose has been updated to: {purpose}",
                "timestamp": datetime.now().isoformat(),
                "routing": "system"
            }
            roster._message_queue[terma_id].append(message)
        
        return {
            "success": True,
            "terminal": terminal_name,
            "purpose": purpose,
            "message": f"Updated purpose for {terminal_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update purpose: {str(e)}"
        )


# ============================================================================
# Predefined Workflow Functions
# ============================================================================

async def _execute_session_optimization_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute terminal session optimization workflow."""
    import random
    from datetime import datetime
    
    workflow_steps = [
        "Analyze current session performance",
        "Identify optimization opportunities", 
        "Apply performance optimizations",
        "Configure optimal terminal settings",
        "Test optimized configuration",
        "Monitor post-optimization performance"
    ]
    
    results = {
        "workflow_id": f"opt-{random.randint(1000, 9999)}",
        "started_at": datetime.now().isoformat(),
        "steps_completed": len(workflow_steps),
        "optimizations_applied": [
            "Increased terminal buffer size to 10000 lines",
            "Enabled session persistence and recovery",
            "Optimized command history settings",
            "Configured optimal shell environment variables"
        ],
        "performance_improvement": {
            "response_time": "-25%",
            "memory_usage": "-15%", 
            "user_experience": "+30%"
        },
        "settings_backup": f"backup-{random.randint(1000, 9999)}"
    }
    
    return results


async def _execute_troubleshooting_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute LLM-assisted troubleshooting workflow."""
    import random
    from datetime import datetime
    
    troubleshooting_steps = [
        "Collect terminal session diagnostics",
        "Analyze error patterns and symptoms",
        "Generate LLM-powered diagnostic insights",
        "Recommend specific remediation actions",
        "Apply automated fixes where possible",
        "Verify issue resolution"
    ]
    
    results = {
        "workflow_id": f"trouble-{random.randint(1000, 9999)}",
        "started_at": datetime.now().isoformat(),
        "issues_detected": random.randint(1, 3),
        "issues_resolved": random.randint(1, 2),
        "llm_insights": [
            "Performance degradation likely due to memory leak in shell process",
            "Command execution timeout suggests network connectivity issues",
            "Error pattern indicates outdated terminal configuration"
        ],
        "remediation_actions": [
            "Restarted affected terminal sessions",
            "Updated terminal configuration files",
            "Applied network connectivity fixes"
        ],
        "resolution_confidence": round(random.uniform(0.85, 0.98), 3)
    }
    
    return results


async def _execute_integration_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute multi-component terminal integration workflow."""
    import random
    from datetime import datetime
    
    integration_components = parameters.get("components", ["hermes", "hephaestus", "engram"])
    
    results = {
        "workflow_id": f"integration-{random.randint(1000, 9999)}",
        "started_at": datetime.now().isoformat(),
        "target_components": integration_components,
        "integrations_established": len(integration_components),
        "integration_details": []
    }
    
    for component in integration_components:
        integration_detail = {
            "component": component,
            "status": "connected",
            "connection_type": _get_connection_type(component),
            "data_sync_enabled": True,
            "heartbeat_interval": "30s",
            "last_health_check": datetime.now().isoformat()
        }
        results["integration_details"].append(integration_detail)
    
    results["overall_health"] = "excellent"
    results["data_flow_active"] = True
    
    return results


async def _execute_performance_analysis_workflow(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute terminal performance analysis workflow."""
    import random
    from datetime import datetime
    
    analysis_duration = parameters.get("duration_minutes", 5)
    
    results = {
        "workflow_id": f"perf-{random.randint(1000, 9999)}",
        "started_at": datetime.now().isoformat(),
        "analysis_duration_minutes": analysis_duration,
        "metrics_collected": {
            "response_time_metrics": {
                "average_ms": random.randint(50, 200),
                "p95_ms": random.randint(200, 500),
                "p99_ms": random.randint(500, 1000)
            },
            "resource_utilization": {
                "cpu_average_percent": round(random.uniform(2.0, 15.0), 2),
                "memory_average_mb": random.randint(50, 200),
                "network_throughput_kbps": random.randint(100, 1000)
            },
            "session_statistics": {
                "total_sessions_analyzed": random.randint(3, 10),
                "active_sessions": random.randint(1, 5),
                "command_execution_rate": random.randint(5, 20)
            }
        },
        "performance_score": round(random.uniform(0.8, 0.95), 3),
        "recommendations": [
            "Consider upgrading terminal buffer size for heavy usage patterns",
            "Enable command caching for frequently used operations",
            "Optimize network settings for better WebSocket performance"
        ]
    }
    
    return results


# ============================================================================
# Helper Functions
# ============================================================================

def _generate_health_recommendations(health_data: Dict[str, Any]) -> List[str]:
    """Generate health-based recommendations."""
    recommendations = []
    
    cpu_usage = health_data.get("performance_metrics", {}).get("cpu_usage_percent", 0)
    memory_usage = health_data.get("performance_metrics", {}).get("memory_usage_percent", 0)
    
    if cpu_usage > 10:
        recommendations.append("Consider optimizing CPU-intensive terminal operations")
    if memory_usage > 30:
        recommendations.append("Monitor memory usage and consider session cleanup")
    
    recommendations.append("Regular health monitoring is recommended")
    recommendations.append("Keep terminal sessions optimized for best performance")
    
    return recommendations


def _generate_action_details(action: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """Generate action-specific details."""
    import random
    
    details = {"session_id": session["session_id"]}
    
    if action == "backup":
        details.update({
            "backup_size_kb": random.randint(100, 1000),
            "backup_location": f"/backups/session-{session['session_id']}.tar.gz",
            "components_backed_up": ["history", "settings", "state"]
        })
    elif action == "restart":
        details.update({
            "previous_uptime_minutes": session["uptime_minutes"],
            "restart_reason": "optimization",
            "new_pid": random.randint(1000, 9999)
        })
    elif action == "optimize":
        details.update({
            "optimizations_applied": ["buffer_size", "history_settings", "performance_tuning"],
            "performance_improvement_percent": random.randint(10, 30)
        })
    elif action == "monitor":
        details.update({
            "monitoring_duration_minutes": 5,
            "metrics_collected": ["cpu", "memory", "responsiveness"],
            "health_score": round(random.uniform(0.8, 0.98), 3)
        })
    elif action == "cleanup":
        details.update({
            "files_cleaned": random.randint(5, 20),
            "space_freed_mb": random.randint(10, 100),
            "cleanup_categories": ["temp_files", "old_logs", "cache"]
        })
    
    return details


def _get_connection_type(component: str) -> str:
    """Get connection type for component integration."""
    connection_types = {
        "hermes": "message_bus",
        "hephaestus": "websocket_bridge",
        "engram": "rest_api",
        "llm_adapter": "http_proxy",
        "budget": "api_integration"
    }
    return connection_types.get(component, "standard_api")


# Export the router
__all__ = ["mcp_router", "fastmcp_server"]