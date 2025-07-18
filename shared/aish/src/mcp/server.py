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
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import yaml

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
from message_handler import MessageHandler
from core.shell import AIShell
from forwarding.forwarding_registry import ForwardingRegistry

# Setup logging
logger = logging.getLogger(__name__)

# Initialize components
message_handler = MessageHandler()
ai_shell = AIShell()
forwarding_registry = ForwardingRegistry()


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
                "list-ais": {
                    "description": "List available AI specialists",
                    "parameters": {}
                },
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
                }
            }
        }
    }


@mcp_router.post("/tools/send-message")
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
                # For now, we'll send the full response as a single chunk
                # In future, we can integrate with actual streaming AI responses
                response = message_handler.send(ai_name, message)
                
                # Send as Server-Sent Events format
                yield f"data: {json.dumps({'chunk': response, 'done': False})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response to {ai_name}: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        # Regular non-streaming response
        try:
            response = message_handler.send(ai_name, message)
            return {"response": response}
        except Exception as e:
            logger.error(f"Error sending message to {ai_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@mcp_router.post("/tools/team-chat")
async def team_chat(request: Request):
    """
    Broadcast message to all AIs
    """
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Missing message")
    
    try:
        # Use MessageHandler to broadcast and get responses
        responses = message_handler.broadcast(message)
        
        # Format responses for the UI
        formatted_responses = []
        for ai_name, response in responses.items():
            if not response.startswith('ERROR:'):
                formatted_responses.append({
                    "specialist_id": ai_name,
                    "content": response,
                    "socket_id": ai_name
                })
        
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
        # Use the hardcoded list from AIShell._get_hardcoded_ais()
        ai_names = ['engram', 'hermes', 'ergon', 'rhetor', 'terma', 'athena',
                    'prometheus', 'harmonia', 'telos', 'synthesis', 'tekton_core',
                    'metis', 'apollo', 'penia', 'sophia', 'noesis', 'numa', 'hephaestus']
        
        # Return in a structured format
        ais = [{"name": name, "status": "available"} for name in ai_names]
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


# Health check endpoint
@mcp_router.get("/health")
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