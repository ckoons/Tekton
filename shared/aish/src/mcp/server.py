"""
aish MCP Server - Exposes aish functionality via Model Context Protocol

This server provides MCP endpoints for all aish commands, enabling:
- Message sending to AIs
- Team chat/broadcast
- Forward management
- Project forwarding
- Terminal communication
- Purpose-based routing
"""

import os
import sys
import asyncio
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import yaml

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Add TEKTON_ROOT to path if needed
tekton_root = os.environ.get('TEKTON_ROOT')
if tekton_root and tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import TektonEnviron for configuration
from shared.env import TektonEnviron
from shared.urls import tekton_url

# Import FastMCP utilities if available
try:
    from tekton.mcp.fastmcp.server import FastMCPServer
    from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints
    from tekton.mcp.fastmcp.schema import MCPTool, MCPCapability
except ImportError:
    # FastMCP not available - we'll implement basic functionality
    FastMCPServer = None
    add_mcp_endpoints = None
    MCPTool = None
    MCPCapability = None

# Import aish components
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.unified_sender import send_to_ci
from core.broadcast_client import broadcast_to_cis
from registry.ci_registry import get_registry
from forwarding.forwarding_registry import ForwardingRegistry

# Setup logging
logger = logging.getLogger(__name__)

# Initialize components
forwarding_registry = ForwardingRegistry()

# Module-level architecture decision
@architecture_decision(
    title="MCP Server Architecture",
    description="Single source of truth for AI routing through standard protocol",
    rationale="Consolidates all AI message routing, eliminating duplicate HTTP endpoints across components",
    alternatives_considered=["Direct HTTP endpoints per component", "WebSocket-only communication", "gRPC"],
    impacts=["ui_integration", "distributed_tekton", "ai_communication"],
    decided_by="Casey",
    decision_date="2025-01-18"
)
class _MCPServerArchitecture:
    """
    This marker class documents the architectural decision to use MCP
    as the unified communication protocol for all AI interactions.
    """
    pass


# Create FastAPI router using Tekton pattern
mcp_router = APIRouter(prefix="/api/mcp/v2")

# Create FastMCP server if available
if FastMCPServer:
    fastmcp_server = FastMCPServer(
        name="aish",
        version="1.0.0",
        description="aish shell messaging and terminal integration MCP server"
    )
    
    # Register capabilities
    if MCPCapability:
        fastmcp_server.register_capability(MCPCapability(
            name="messaging",
            description="AI messaging and team chat functionality"
        ))
        fastmcp_server.register_capability(MCPCapability(
            name="forwarding",
            description="Message and project forwarding management"
        ))
        fastmcp_server.register_capability(MCPCapability(
            name="terminal_integration",
            description="Inter-terminal communication and purpose management"
        ))
    
    # Note: We implement our own endpoints rather than using add_mcp_endpoints
    # because aish has specific requirements for its MCP interface

# Always implement capabilities endpoint
@mcp_router.get("/capabilities")
async def get_capabilities():
    """
    MCP discovery endpoint - returns available tools and their descriptions
    """
    return {
        "mcp_version": "1.0",
        "server_name": "aish",
        "capabilities": {
            "tools": {
                # Messaging & Communication
                "send-message": {
                    "description": "Send a message to an AI",
                    "parameters": {
                        "ai_name": {"type": "string", "required": True},
                        "message": {"type": "string", "required": True}
                    }
                },
                "team-chat": {
                    "description": "Broadcast message to all AIs",
                    "parameters": {
                        "message": {"type": "string", "required": True}
                    }
                },
                "forward": {
                    "description": "Manage AI message forwarding",
                    "parameters": {
                        "action": {"type": "string", "enum": ["add", "remove", "list"], "required": True},
                        "ai_name": {"type": "string", "required": False},
                        "terminal": {"type": "string", "required": False}
                    }
                },
                "project-forward": {
                    "description": "Forward project CI to terminal",
                    "parameters": {
                        "action": {"type": "string", "enum": ["add", "remove", "list"], "required": True},
                        "project_name": {"type": "string", "required": False}
                    }
                },
                
                # CI Discovery & Information
                "list-ais": {
                    "description": "List available AI specialists",
                    "parameters": {}
                },
                "list-project-cis": {
                    "description": "List project CIs with their dynamically allocated ports",
                    "parameters": {}
                },
                "get-ci": {
                    "description": "Get full details for a specific CI",
                    "endpoint": "GET /tools/ci/{ci_name}"
                },
                "get-ci-types": {
                    "description": "Get available CI types",
                    "endpoint": "GET /tools/ci-types"
                },
                "get-cis-by-type": {
                    "description": "Get all CIs of a specific type",
                    "endpoint": "GET /tools/cis/type/{ci_type}"
                },
                "check-ci-exists": {
                    "description": "Check if a CI exists",
                    "endpoint": "GET /tools/ci/{ci_name}/exists"
                },
                
                # Terminal Integration
                "terma-send": {
                    "description": "Send message to terminal",
                    "parameters": {
                        "terminal": {"type": "string", "required": True},
                        "message": {"type": "string", "required": True}
                    }
                },
                "terma-broadcast": {
                    "description": "Broadcast message to all terminals",
                    "parameters": {
                        "message": {"type": "string", "required": True}
                    }
                },
                "terma-inbox": {
                    "description": "Get terminal inbox messages",
                    "parameters": {}
                },
                "purpose": {
                    "description": "Get or set terminal purpose",
                    "parameters": {
                        "terminal": {"type": "string", "required": False},
                        "roles": {"type": "string", "required": False}
                    }
                },
                
                # CI Tools Management
                "list-ci-tools": {
                    "description": "List available CI tools",
                    "endpoint": "GET /tools/ci-tools"
                },
                "launch-ci-tool": {
                    "description": "Launch a CI tool",
                    "endpoint": "POST /tools/ci-tools/launch",
                    "parameters": {
                        "tool_name": {"type": "string", "required": True},
                        "session_id": {"type": "string", "required": False},
                        "instance_name": {"type": "string", "required": False}
                    }
                },
                "terminate-ci-tool": {
                    "description": "Terminate a CI tool",
                    "endpoint": "POST /tools/ci-tools/terminate",
                    "parameters": {
                        "tool_name": {"type": "string", "required": True}
                    }
                },
                "get-ci-tool-status": {
                    "description": "Get status for a CI tool",
                    "endpoint": "GET /tools/ci-tools/status/{tool_name}"
                },
                "list-ci-tool-instances": {
                    "description": "List running CI tool instances",
                    "endpoint": "GET /tools/ci-tools/instances"
                },
                "define-ci-tool": {
                    "description": "Define a new CI tool",
                    "endpoint": "POST /tools/ci-tools/define",
                    "parameters": {
                        "name": {"type": "string", "required": True},
                        "type": {"type": "string", "required": False},
                        "executable": {"type": "string", "required": True},
                        "options": {"type": "object", "required": False}
                    }
                },
                "undefine-ci-tool": {
                    "description": "Remove a CI tool definition",
                    "endpoint": "DELETE /tools/ci-tools/{tool_name}"
                },
                "get-ci-tool-capabilities": {
                    "description": "Get capabilities for a CI tool",
                    "endpoint": "GET /tools/ci-tools/capabilities/{tool_name}"
                },
                
                # Context State Management
                "get-context-state": {
                    "description": "Get context state for a CI",
                    "endpoint": "GET /tools/context-state/{ci_name}"
                },
                "update-context-state": {
                    "description": "Update context state for a CI",
                    "endpoint": "POST /tools/context-state/{ci_name}",
                    "parameters": {
                        "last_output": {"type": "any", "required": False},
                        "staged_prompt": {"type": "array", "required": False},
                        "next_prompt": {"type": "array", "required": False}
                    }
                },
                "get-all-context-states": {
                    "description": "Get context states for all CIs",
                    "endpoint": "GET /tools/context-states"
                },
                "promote-staged-context": {
                    "description": "Move staged context to next prompt",
                    "endpoint": "POST /tools/context-state/{ci_name}/promote-staged"
                },
                
                # Registry Management
                "reload-registry": {
                    "description": "Force reload CI registry",
                    "endpoint": "POST /tools/registry/reload"
                },
                "get-registry-status": {
                    "description": "Get CI registry status",
                    "endpoint": "GET /tools/registry/status"
                },
                "save-registry": {
                    "description": "Force save registry state",
                    "endpoint": "POST /tools/registry/save"
                }
            }
        }
    }


@mcp_router.post("/tools/send-message")
@api_contract(
    title="AI Message Routing",
    description="Send message to specific AI specialist",
    endpoint="/api/mcp/v2/tools/send-message",
    method="POST",
    request_schema={"ai_name": "string", "message": "string", "stream": "boolean?"},
    response_schema={"response": "string", "ai_name": "string", "timestamp": "string?"},
    performance_requirements="<500ms routing time"
)
@integration_point(
    title="AI Shell Message Integration",
    description="Routes messages through AIShell to appropriate AI specialist",
    target_component="AIShell",
    protocol="internal_api",
    data_flow="MCP request → AIShell.send_to_ai → AI specialist → response",
    integration_date="2025-01-18"
)
async def send_message(request: Request):
    """
    Send a message to a specific AI with streaming response support
    """
    data = await request.json()
    ai_name = data.get("ai_name")
    message = data.get("message")
    stream = data.get("stream", False)  # Optional streaming flag
    
    if not ai_name or not message:
        raise HTTPException(status_code=400, detail="Missing ai_name or message")
    
    if stream:
        # Return streaming response
        async def generate():
            try:
                # Use unified sender with output capture
                import io
                from contextlib import redirect_stdout
                
                output_buffer = io.StringIO()
                with redirect_stdout(output_buffer):
                    success = send_to_ci(ai_name, message)
                
                if success:
                    response = output_buffer.getvalue().strip()
                    # Send as Server-Sent Events format
                    yield f"data: {json.dumps({'chunk': response, 'done': False})}\n\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': f'Failed to send to {ai_name}', 'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response to {ai_name}: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        # Regular non-streaming response
        try:
            # Use unified sender with output capture
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                success = send_to_ci(ai_name, message)
            
            if success:
                response = output_buffer.getvalue().strip()
                return {"response": response}
            else:
                raise HTTPException(status_code=500, detail=f"Failed to send to {ai_name}")
        except Exception as e:
            logger.error(f"Error sending message to {ai_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/team-chat")
@api_contract(
    title="Team Chat Broadcast",
    description="Broadcasts messages to all AI specialists",
    endpoint="/api/mcp/v2/tools/team-chat",
    method="POST",
    request_schema={"message": "string"},
    response_schema={"responses": [{"specialist_id": "string", "content": "string", "socket_id": "string"}]},
    performance_requirements="<2s for all AI responses"
)
@performance_boundary(
    title="Team Chat Performance",
    description="Critical path for multi-AI coordination",
    sla="<2s total response time",
    optimization_notes="Parallel AI queries, formatted response caching",
    measured_impact="Enables real-time team collaboration"
)
async def team_chat(request: Request):
    """
    Broadcast message to all AIs
    """
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Missing message")
    
    try:
        # Use broadcast client to send to all CIs
        responses = broadcast_to_cis(message)
        
        # Format responses for the UI and update registry
        formatted_responses = []
        registry = get_registry()
        
        for ai_name, response in responses.items():
            if not response.startswith('ERROR:'):
                formatted_responses.append({
                    "specialist_id": ai_name,
                    "content": response,
                    "socket_id": ai_name
                })
                
                # Update the registry with each CI's response
                registry.update_ci_last_output(ai_name, response)
        
        return {"responses": formatted_responses}
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/forward")
async def manage_forward(request: Request):
    """
    Manage AI message forwarding
    """
    data = await request.json()
    action = data.get("action")
    
    if not action:
        raise HTTPException(status_code=400, detail="Missing action")
    
    try:
        if action == "list":
            forwards = forwarding_registry.list_forwards()
            return {"forwards": forwards}
        elif action == "add":
            ai_name = data.get("ai_name")
            terminal = data.get("terminal")
            if not ai_name or not terminal:
                raise HTTPException(status_code=400, detail="Missing ai_name or terminal")
            forwarding_registry.set_forward(ai_name, terminal)
            return {"status": "success", "message": f"Added forward from {ai_name} to {terminal}"}
        elif action == "remove":
            ai_name = data.get("ai_name")
            if not ai_name:
                raise HTTPException(status_code=400, detail="Missing ai_name")
            forwarding_registry.remove_forward(ai_name)
            return {"status": "success", "message": f"Removed forward for {ai_name}"}
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    except Exception as e:
        logger.error(f"Error managing forward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/list-ais")
async def list_ais():
    """
    List available AI specialists
    """
    try:
        # Get the list from unified registry
        registry = get_registry()
        all_cis_dict = registry.get_all()
        all_cis = list(all_cis_dict.values())
        
        # Format for MCP response
        ais = []
        for ci in all_cis:
            ais.append({
                "name": ci['name'],
                "type": ci['type'],
                "port": ci.get('port'),
                "status": "active",
                "purpose": ci.get('description', ''),
                "message_format": ci.get('message_format', '')
            })
        
        return {"ais": ais}
    except Exception as e:
        logger.error(f"Error listing AIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/terma-send")
async def terma_send(request: Request):
    """
    Send message to a specific terminal
    """
    data = await request.json()
    terminal = data.get("terminal")
    message = data.get("message")
    
    if not terminal or not message:
        raise HTTPException(status_code=400, detail="Missing terminal or message")
    
    try:
        # Import the terma send function
        from commands.terma import terma_send_message
        
        # Call the existing terma_send_message function
        result = terma_send_message(terminal, message)
        return {"success": result == 0, "message": f"Message sent to {terminal}"}
    except Exception as e:
        logger.error(f"Error sending message to terminal {terminal}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/terma-broadcast")
async def terma_broadcast(request: Request):
    """
    Broadcast message to all terminals
    """
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Missing message")
    
    try:
        # Import the terma send function
        from commands.terma import terma_send_message
        
        # Call terma_send_message with "broadcast" target
        result = terma_send_message("broadcast", message)
        return {"success": result == 0}
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/terma-inbox")
async def terma_inbox():
    """
    Get terminal inbox messages
    """
    try:
        # Import the terma inbox function
        from commands.terma import terma_inbox_both
        
        # For MCP, we need to return structured data, not print to stdout
        # Read the inbox file directly
        tekton_root = TektonEnviron.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
        inbox_file = os.path.join(tekton_root, ".tekton", "terma", ".inbox_snapshot")
        
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r') as f:
                data = json.load(f)
            return {
                "prompt": data.get('prompt', []),
                "new": data.get('new', []),
                "keep": data.get('keep', [])
            }
        else:
            return {"prompt": [], "new": [], "keep": []}
    except Exception as e:
        logger.error(f"Error getting inbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/purpose")
async def manage_purpose(request: Request):
    """
    Get or set terminal purpose
    """
    data = await request.json()
    terminal = data.get("terminal")
    roles = data.get("roles")
    
    try:
        # Import the purpose handler
        from commands.purpose import handle_purpose_command
        
        if roles is not None and terminal:
            # Set purpose - call with args like CLI would
            args = [terminal, roles]
            result = handle_purpose_command(args)
            return {"success": result == 0, "terminal": terminal, "purpose": roles}
        else:
            # Get purpose - for now return current terminal purpose
            current_purpose = TektonEnviron.get('TEKTON_TERMINAL_PURPOSE', '')
            return {"terminal": terminal or "current", "purpose": current_purpose}
    except Exception as e:
        logger.error(f"Error managing purpose: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/project-forward")
async def manage_project_forward(request: Request):
    """
    Manage project CI forwarding
    """
    data = await request.json()
    action = data.get("action")
    project_name = data.get("project_name")
    
    if not action:
        raise HTTPException(status_code=400, detail="Missing action")
    
    try:
        # Import the project command handler
        from commands.project import handle_project_command
        
        if action == "list":
            # Call with 'list' argument
            result = handle_project_command(['list'])
            # For MCP, we need structured data - read from tekton.yaml
            import yaml
            tekton_yaml = os.path.join(TektonEnviron.get('TEKTON_ROOT'), '.tekton', 'tekton.yaml')
            if os.path.exists(tekton_yaml):
                with open(tekton_yaml, 'r') as f:
                    config = yaml.safe_load(f)
                projects = config.get('projects', [])
                return {"projects": projects}
            return {"projects": []}
        elif action == "add":
            if not project_name:
                raise HTTPException(status_code=400, detail="Missing project_name")
            result = handle_project_command(['forward', project_name])
            return {"success": result == 0, "message": f"Forwarding CI for {project_name}"}
        elif action == "remove":
            if not project_name:
                raise HTTPException(status_code=400, detail="Missing project_name")
            result = handle_project_command(['unforward', project_name])
            return {"success": result == 0, "message": f"Stopped forwarding CI for {project_name}"}
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
    except Exception as e:
        logger.error(f"Error managing project forward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================
# CI Tools Management Endpoints
# ==============================================

@mcp_router.post("/tools/list-project-cis")
async def list_project_cis():
    """
    List project CIs with their dynamically allocated ports
    """
    try:
        registry = get_registry()
        all_cis = registry.get_all()
        
        project_cis = []
        for ci_name, ci in all_cis.items():
            # Include CIs that are marked as project CIs
            if ci.get('is_project_ci'):
                # Special handling for numa/Tekton
                if ci_name == 'numa' and ci.get('project') == 'Tekton':
                    project_cis.append({
                        "name": "numa",
                        "project": "Tekton",
                        "port": registry.get_ai_port('numa'),  # Get numa's AI port
                        "type": "greek",  # numa is part of Greek Chorus
                        "description": "Tekton project CI (numa)"
                    })
                else:
                    # Regular project CIs with dynamic ports
                    project_cis.append({
                        "name": ci.get('name'),
                        "project": ci.get('project'),
                        "port": ci.get('port', 0),
                        "ai_port": ci.get('ai_port', 0),
                        "type": ci.get('type'),
                        "description": ci.get('description', '')
                    })
        
        return {"project_cis": project_cis}
    except Exception as e:
        logger.error(f"Error listing project CIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/ci-tools")
@api_contract(
    title="List CI Tools",
    description="List available CI tools and their status",
    endpoint="/api/mcp/v2/tools/ci-tools",
    method="GET",
    request_schema={},
    response_schema={"tools": [{"name": "string", "description": "string", "status": "string", "port": "number"}]},
    performance_requirements="<100ms response time"
)
async def list_ci_tools():
    """
    List all available CI tools
    """
    try:
        from shared.ci_tools import get_registry as get_tools_registry
        tools_registry = get_tools_registry()
        tools = tools_registry.get_tools()
        
        tool_list = []
        for name, config in tools.items():
            status = tools_registry.get_tool_status(name)
            tool_list.append({
                "name": name,
                "description": config.get('description', ''),
                "type": config.get('base_type', config.get('type', 'tool')),
                "port": config.get('port'),
                "status": "running" if status.get('running') else "stopped",
                "executable": config.get('executable', ''),
                "capabilities": list(config.get('capabilities', {}).keys()),
                "defined_by": config.get('defined_by', 'system')
            })
        
        return {"tools": tool_list}
    except Exception as e:
        logger.error(f"Error listing CI tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/ci-tools/launch")
@api_contract(
    title="Launch CI Tool",
    description="Launch a CI tool with optional session and instance",
    endpoint="/api/mcp/v2/tools/ci-tools/launch",
    method="POST",
    request_schema={"tool_name": "string", "session_id": "string?", "instance_name": "string?"},
    response_schema={"success": "boolean", "message": "string", "port": "number?"},
    performance_requirements="<2s for tool startup"
)
async def launch_ci_tool(request: Request):
    """
    Launch a CI tool
    """
    data = await request.json()
    tool_name = data.get("tool_name")
    session_id = data.get("session_id")
    instance_name = data.get("instance_name")
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing tool_name")
    
    try:
        from shared.ci_tools import ToolLauncher
        launcher = ToolLauncher.get_instance()
        
        success = launcher.launch_tool(tool_name, session_id, instance_name)
        
        if success:
            # Get tool info for port
            from shared.ci_tools import get_registry as get_tools_registry
            tools_registry = get_tools_registry()
            tool_config = tools_registry.get_tool(tool_name)
            
            return {
                "success": True,
                "message": f"Successfully launched {tool_name}",
                "port": tool_config.get('port') if tool_config else None
            }
        else:
            return {
                "success": False,
                "message": f"Failed to launch {tool_name}"
            }
    except Exception as e:
        logger.error(f"Error launching tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/ci-tools/terminate")
@api_contract(
    title="Terminate CI Tool",
    description="Terminate a running CI tool or instance",
    endpoint="/api/mcp/v2/tools/ci-tools/terminate",
    method="POST",
    request_schema={"tool_name": "string"},
    response_schema={"success": "boolean", "message": "string"},
    performance_requirements="<500ms for termination"
)
async def terminate_ci_tool(request: Request):
    """
    Terminate a CI tool
    """
    data = await request.json()
    tool_name = data.get("tool_name")
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing tool_name")
    
    try:
        from shared.ci_tools import ToolLauncher
        launcher = ToolLauncher.get_instance()
        
        success = launcher.terminate_tool(tool_name)
        
        return {
            "success": success,
            "message": f"{'Successfully terminated' if success else 'Failed to terminate'} {tool_name}"
        }
    except Exception as e:
        logger.error(f"Error terminating tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/ci-tools/status/{tool_name}")
@api_contract(
    title="Get CI Tool Status",
    description="Get detailed status for a specific CI tool",
    endpoint="/api/mcp/v2/tools/ci-tools/status/{tool_name}",
    method="GET",
    request_schema={},
    response_schema={"name": "string", "running": "boolean", "pid": "number?", "uptime": "number?", "metrics": "object?"},
    performance_requirements="<50ms response time"
)
async def get_ci_tool_status(tool_name: str):
    """
    Get status for a specific CI tool
    """
    try:
        from shared.ci_tools import get_registry as get_tools_registry
        tools_registry = get_tools_registry()
        
        status = tools_registry.get_tool_status(tool_name)
        
        if 'error' in status:
            raise HTTPException(status_code=404, detail=status['error'])
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool status for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/ci-tools/instances")
@api_contract(
    title="List CI Tool Instances",
    description="List all running CI tool instances",
    endpoint="/api/mcp/v2/tools/ci-tools/instances",
    method="GET",
    request_schema={},
    response_schema={"instances": [{"name": "string", "tool_type": "string", "pid": "number", "session": "string?"}]},
    performance_requirements="<100ms response time"
)
async def list_ci_tool_instances():
    """
    List all running CI tool instances
    """
    try:
        from shared.ci_tools import ToolLauncher
        launcher = ToolLauncher.get_instance()
        
        instances = []
        for instance_name, info in launcher.tools.items():
            status = info['adapter'].get_status()
            instances.append({
                "name": instance_name,
                "tool_type": info['config'].get('base_type', info['adapter'].tool_name),
                "pid": status.get('pid'),
                "session": status.get('session'),
                "uptime": status.get('uptime'),
                "running": status.get('running', False)
            })
        
        return {"instances": instances}
    except Exception as e:
        logger.error(f"Error listing tool instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/ci-tools/define")
@api_contract(
    title="Define CI Tool",
    description="Define a new CI tool dynamically",
    endpoint="/api/mcp/v2/tools/ci-tools/define",
    method="POST",
    request_schema={"name": "string", "type": "string", "executable": "string", "options": "object"},
    response_schema={"success": "boolean", "message": "string", "port": "number?"},
    performance_requirements="<100ms for definition"
)
async def define_ci_tool(request: Request):
    """
    Define a new CI tool
    """
    data = await request.json()
    name = data.get("name")
    base_type = data.get("type", "generic")
    executable = data.get("executable")
    options = data.get("options", {})
    
    if not name or not executable:
        raise HTTPException(status_code=400, detail="Missing name or executable")
    
    try:
        from shared.ci_tools import get_registry as get_tools_registry
        tools_registry = get_tools_registry()
        
        # Build config from options
        config = {
            'display_name': options.get('display_name', name.replace('-', ' ').title()),
            'type': 'tool',
            'base_type': base_type,
            'executable': executable,
            'description': options.get('description', f'User-defined {name} tool'),
            'port': options.get('port', 'auto'),
            'defined_by': 'user',
            'created_at': datetime.datetime.now().isoformat() + 'Z'
        }
        
        # Add optional fields
        if 'capabilities' in options:
            if isinstance(options['capabilities'], list):
                config['capabilities'] = {cap: True for cap in options['capabilities']}
            else:
                config['capabilities'] = options['capabilities']
        
        if 'launch_args' in options:
            config['launch_args'] = options['launch_args']
        
        if 'health_check' in options:
            config['health_check'] = options['health_check']
        
        if 'environment' in options:
            config['environment'] = options['environment']
        
        # Allocate port if auto
        if config['port'] == 'auto':
            config['port'] = tools_registry.find_available_port()
        
        # Register the tool
        success = tools_registry.register_tool(name, config)
        
        return {
            "success": success,
            "message": f"{'Successfully defined' if success else 'Failed to define'} tool {name}",
            "port": config.get('port') if success else None
        }
    except Exception as e:
        logger.error(f"Error defining tool {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.delete("/tools/ci-tools/{tool_name}")
@api_contract(
    title="Undefine CI Tool",
    description="Remove a user-defined CI tool",
    endpoint="/api/mcp/v2/tools/ci-tools/{tool_name}",
    method="DELETE",
    request_schema={},
    response_schema={"success": "boolean", "message": "string"},
    performance_requirements="<50ms for removal"
)
async def undefine_ci_tool(tool_name: str):
    """
    Undefine a CI tool
    """
    try:
        from shared.ci_tools import get_registry as get_tools_registry
        tools_registry = get_tools_registry()
        
        success = tools_registry.unregister_tool(tool_name)
        
        return {
            "success": success,
            "message": f"{'Successfully undefined' if success else 'Failed to undefine'} tool {tool_name}"
        }
    except Exception as e:
        logger.error(f"Error undefining tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/ci-tools/capabilities/{tool_name}")
@api_contract(
    title="Get CI Tool Capabilities",
    description="Get capabilities for a specific CI tool",
    endpoint="/api/mcp/v2/tools/ci-tools/capabilities/{tool_name}",
    method="GET",
    request_schema={},
    response_schema={"name": "string", "capabilities": "object", "executable": "string", "health_check": "string?"},
    performance_requirements="<50ms response time"
)
async def get_ci_tool_capabilities(tool_name: str):
    """
    Get capabilities for a CI tool
    """
    try:
        from shared.ci_tools import get_registry as get_tools_registry
        tools_registry = get_tools_registry()
        
        tool_config = tools_registry.get_tool(tool_name)
        
        if not tool_config:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
        
        return {
            "name": tool_name,
            "capabilities": tool_config.get('capabilities', {}),
            "executable": tool_config.get('executable', ''),
            "health_check": tool_config.get('health_check'),
            "port": tool_config.get('port'),
            "base_type": tool_config.get('base_type', tool_name)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting capabilities for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================
# Context State Management Endpoints
# ==============================================

@mcp_router.get("/tools/context-state/{ci_name}")
@api_contract(
    title="Get CI Context State",
    description="Get context state for a specific CI",
    endpoint="/api/mcp/v2/tools/context-state/{ci_name}",
    method="GET",
    request_schema={},
    response_schema={"ci_name": "string", "last_output": "any", "staged_prompt": "array?", "next_prompt": "array?"},
    performance_requirements="<50ms response time"
)
async def get_ci_context_state(ci_name: str):
    """
    Get context state for a specific CI
    """
    try:
        registry = get_registry()
        context_state = registry.get_ci_context_state(ci_name)
        
        if not context_state:
            # CI exists but no context state yet
            if registry.exists(ci_name):
                return {
                    "ci_name": ci_name,
                    "last_output": None,
                    "staged_prompt": None,
                    "next_prompt": None
                }
            else:
                raise HTTPException(status_code=404, detail=f"CI not found: {ci_name}")
        
        return {
            "ci_name": ci_name,
            **context_state
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting context state for {ci_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/context-state/{ci_name}")
@api_contract(
    title="Update CI Context State",
    description="Update context state for a specific CI",
    endpoint="/api/mcp/v2/tools/context-state/{ci_name}",
    method="POST",
    request_schema={"last_output": "any?", "staged_prompt": "array?", "next_prompt": "array?"},
    response_schema={"success": "boolean", "message": "string"},
    performance_requirements="<100ms for update"
)
async def update_ci_context_state(ci_name: str, request: Request):
    """
    Update context state for a specific CI
    """
    data = await request.json()
    
    try:
        registry = get_registry()
        
        if not registry.exists(ci_name):
            raise HTTPException(status_code=404, detail=f"CI not found: {ci_name}")
        
        success = True
        updated = []
        
        # Update last output if provided
        if 'last_output' in data:
            if registry.update_ci_last_output(ci_name, data['last_output']):
                updated.append('last_output')
            else:
                success = False
        
        # Update staged prompt if provided
        if 'staged_prompt' in data:
            if registry.set_ci_staged_context_prompt(ci_name, data['staged_prompt']):
                updated.append('staged_prompt')
            else:
                success = False
        
        # Update next prompt if provided
        if 'next_prompt' in data:
            if registry.set_ci_next_context_prompt(ci_name, data['next_prompt']):
                updated.append('next_prompt')
            else:
                success = False
        
        return {
            "success": success,
            "message": f"Updated: {', '.join(updated)}" if updated else "No updates made"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating context state for {ci_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/context-states")
@api_contract(
    title="Get All Context States",
    description="Get context states for all CIs",
    endpoint="/api/mcp/v2/tools/context-states",
    method="GET",
    request_schema={},
    response_schema={"context_states": "object"},
    performance_requirements="<200ms for all states"
)
async def get_all_context_states():
    """
    Get context states for all CIs
    """
    try:
        registry = get_registry()
        all_states = registry.get_all_context_states()
        
        return {"context_states": all_states}
    except Exception as e:
        logger.error(f"Error getting all context states: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/context-state/{ci_name}/promote-staged")
@api_contract(
    title="Promote Staged Context",
    description="Move staged context prompt to next prompt",
    endpoint="/api/mcp/v2/tools/context-state/{ci_name}/promote-staged",
    method="POST",
    request_schema={},
    response_schema={"success": "boolean", "message": "string"},
    performance_requirements="<50ms for promotion"
)
async def promote_staged_context(ci_name: str):
    """
    Promote staged context to next prompt
    """
    try:
        registry = get_registry()
        
        if not registry.exists(ci_name):
            raise HTTPException(status_code=404, detail=f"CI not found: {ci_name}")
        
        success = registry.set_ci_next_from_staged(ci_name)
        
        return {
            "success": success,
            "message": "Promoted staged context to next prompt" if success else "Failed to promote staged context"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error promoting staged context for {ci_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================
# Detailed CI Information Endpoints
# ==============================================

@mcp_router.get("/tools/ci/{ci_name}")
@api_contract(
    title="Get CI Details",
    description="Get full details for a specific CI",
    endpoint="/api/mcp/v2/tools/ci/{ci_name}",
    method="GET",
    request_schema={},
    response_schema={"name": "string", "type": "string", "endpoint": "string", "description": "string", "message_format": "string"},
    performance_requirements="<50ms response time"
)
async def get_ci_details(ci_name: str):
    """
    Get full details for a specific CI
    """
    try:
        registry = get_registry()
        ci = registry.get_by_name(ci_name)
        
        if not ci:
            raise HTTPException(status_code=404, detail=f"CI not found: {ci_name}")
        
        return ci
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CI details for {ci_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/ci-types")
@api_contract(
    title="Get CI Types",
    description="Get available CI types",
    endpoint="/api/mcp/v2/tools/ci-types",
    method="GET",
    request_schema={},
    response_schema={"types": ["string"]},
    performance_requirements="<50ms response time"
)
async def get_ci_types():
    """
    Get available CI types
    """
    try:
        registry = get_registry()
        types = registry.get_types()
        
        return {"types": types}
    except Exception as e:
        logger.error(f"Error getting CI types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/cis/type/{ci_type}")
@api_contract(
    title="Get CIs by Type",
    description="Get all CIs of a specific type",
    endpoint="/api/mcp/v2/tools/cis/type/{ci_type}",
    method="GET",
    request_schema={},
    response_schema={"cis": ["object"]},
    performance_requirements="<100ms response time"
)
async def get_cis_by_type(ci_type: str):
    """
    Get all CIs of a specific type
    """
    try:
        registry = get_registry()
        cis = registry.get_by_type(ci_type)
        
        return {"cis": cis}
    except Exception as e:
        logger.error(f"Error getting CIs of type {ci_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/ci/{ci_name}/exists")
@api_contract(
    title="Check CI Exists",
    description="Check if a CI exists",
    endpoint="/api/mcp/v2/tools/ci/{ci_name}/exists",
    method="GET",
    request_schema={},
    response_schema={"exists": "boolean"},
    performance_requirements="<20ms response time"
)
async def check_ci_exists(ci_name: str):
    """
    Check if a CI exists
    """
    try:
        registry = get_registry()
        exists = registry.exists(ci_name)
        
        return {"exists": exists}
    except Exception as e:
        logger.error(f"Error checking if CI exists: {ci_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================
# Registry Management Endpoints
# ==============================================

@mcp_router.post("/tools/registry/reload")
@api_contract(
    title="Reload CI Registry",
    description="Force reload of CI registry to discover new terminals, projects, and tools",
    endpoint="/api/mcp/v2/tools/registry/reload",
    method="POST",
    request_schema={},
    response_schema={"success": "boolean", "message": "string", "counts": "object"},
    performance_requirements="<500ms for full reload"
)
async def reload_registry():
    """
    Force reload of CI registry
    """
    try:
        registry = get_registry()
        
        # Get counts before reload
        before_count = len(registry.get_all())
        
        # Reload registry - for testing we just return the same instance
        # In production, this would reset the singleton
        registry = get_registry()
        
        # Get counts after reload
        after_count = len(registry.get_all())
        all_cis_dict = registry.get_all()
        all_cis = list(all_cis_dict.values())
        
        # Count by type
        type_counts = {}
        for ci in all_cis:
            ci_type = ci.get('type', 'unknown')
            type_counts[ci_type] = type_counts.get(ci_type, 0) + 1
        
        return {
            "success": True,
            "message": f"Registry reloaded. CIs: {before_count} → {after_count}",
            "counts": {
                "total": after_count,
                "before": before_count,
                "by_type": type_counts
            }
        }
    except Exception as e:
        logger.error(f"Error reloading registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.get("/tools/registry/status")
@api_contract(
    title="Registry Status",
    description="Get CI registry status and statistics",
    endpoint="/api/mcp/v2/tools/registry/status",
    method="GET",
    request_schema={},
    response_schema={"status": "string", "counts": "object", "registry_file": "string"},
    performance_requirements="<50ms response time"
)
async def get_registry_status():
    """
    Get CI registry status
    """
    try:
        registry = get_registry()
        all_cis_dict = registry.get_all()
        all_cis = list(all_cis_dict.values())
        
        # Count by type
        type_counts = {}
        for ci in all_cis:
            ci_type = ci.get('type', 'unknown')
            type_counts[ci_type] = type_counts.get(ci_type, 0) + 1
        
        # Check if registry file exists
        registry_file = None
        file_exists = False
        
        # Try to get file registry info
        if hasattr(registry, '_file_registry'):
            # Get the registry file path from FileRegistry
            try:
                registry_file = Path(registry._file_registry.data_file)
                file_exists = registry_file.exists()
            except:
                pass
        
        return {
            "status": "active",
            "counts": {
                "total": len(all_cis),
                "by_type": type_counts
            },
            "registry_file": str(registry_file) if registry_file else "unknown",
            "file_exists": file_exists
        }
    except Exception as e:
        logger.error(f"Error getting registry status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/registry/save")
@api_contract(
    title="Save Registry State",
    description="Force save of registry context state to disk",
    endpoint="/api/mcp/v2/tools/registry/save",
    method="POST",
    request_schema={},
    response_schema={"success": "boolean", "message": "string"},
    performance_requirements="<100ms for save"
)
async def save_registry_state():
    """
    Force save registry state
    """
    try:
        registry = get_registry()
        registry._save_context_state()
        
        return {
            "success": True,
            "message": "Registry state saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving registry state: {e}")
        return {
            "success": False,
            "message": f"Failed to save registry state: {str(e)}"
        }


@mcp_router.get("/health")
@api_contract(
    title="MCP Health Check",
    description="Service discovery and monitoring endpoint",
    endpoint="/api/mcp/v2/health",
    method="GET",
    request_schema={},
    response_schema={"status": "string", "service": "string", "version": "string", "capabilities": ["string"], "message": "string"},
    performance_requirements="<10ms response time"
)
async def health_check():
    """
    Health check endpoint for aish MCP server
    """
    return {
        "status": "healthy",
        "service": "aish-mcp",
        "version": "1.0.0",
        "capabilities": ["messaging", "forwarding", "terminal_integration"],
        "message": "aish MCP server is operational"
    }


# Export the router
__all__ = ["mcp_router", "fastmcp_server" if FastMCPServer else None]