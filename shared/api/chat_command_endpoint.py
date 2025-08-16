"""
Unified chat command endpoint for all Tekton components.
Handles [command] execution from Hephaestus UI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from aish.src.handlers.chat_command_handler import handle_chat_command, get_handler
from aish.src.registry.ci_registry import get_registry


class ChatCommandRequest(BaseModel):
    """Request model for chat command execution"""
    type: str  # 'aish', 'shell', 'forward', 'unforward'
    command: str
    context: Dict[str, Any] = {}


class ChatCommandResponse(BaseModel):
    """Response model for chat command execution"""
    type: str  # 'system', 'error'
    output: str
    error: bool = False
    metadata: Dict[str, Any] = {}


def create_chat_command_router(component_name: str) -> APIRouter:
    """
    Create a chat command router for a component.
    
    Args:
        component_name: Name of the component (e.g., 'numa', 'apollo')
    
    Returns:
        FastAPI APIRouter with chat command endpoint
    """
    router = APIRouter()
    
    @router.post("/api/chat/command", response_model=ChatCommandResponse)
    async def execute_chat_command(request: ChatCommandRequest):
        """Execute command from chat interface"""
        try:
            # Add component to context
            request.context['component'] = component_name
            
            # Special handling for Claude escalation
            if request.type == 'escalate' and request.command.startswith('claude'):
                return await handle_claude_escalation(
                    component_name, 
                    request.command, 
                    request.context
                )
            
            # Execute command through handler
            result = await handle_chat_command(
                request.type,
                request.command,
                request.context
            )
            
            return ChatCommandResponse(**result)
            
        except Exception as e:
            return ChatCommandResponse(
                type="error",
                output=f"Command execution failed: {str(e)}",
                error=True
            )
    
    @router.get("/api/chat/forward-status")
    async def get_forward_status():
        """Get current forward status for this component"""
        try:
            registry = get_registry()
            ci_name = f"{component_name}-ci"
            
            # Check if this CI is forwarded
            forward_state = registry.get_forward_state(ci_name)
            
            if forward_state:
                return {
                    "forwarded": True,
                    "model": forward_state.get('model'),
                    "args": forward_state.get('args'),
                    "started": forward_state.get('started')
                }
            else:
                return {
                    "forwarded": False,
                    "model": "default"
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router


async def handle_claude_escalation(component_name: str, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Claude model escalation for a component.
    
    Args:
        component_name: Component requesting escalation
        command: Claude command (e.g., 'claude', 'claude-opus')
        context: Request context
    
    Returns:
        Response dict with escalation status
    """
    import subprocess
    import asyncio
    
    try:
        # Parse Claude variant
        if command == 'claude':
            claude_cmd = ['claude', '--print']
        elif command == 'claude-opus':
            claude_cmd = ['claude', '--model', 'claude-3-opus-20240229', '--print']
        elif command == 'claude-sonnet':
            claude_cmd = ['claude', '--model', 'claude-3-sonnet-20240229', '--print']
        elif command == 'claude-haiku':
            claude_cmd = ['claude', '--model', 'claude-3-haiku-20240307', '--print']
        else:
            claude_cmd = ['claude', '--print']
        
        # Check if Claude is available
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True)
            if result.returncode != 0:
                # Claude not available, fall back to notification
                return {
                    "type": "system",
                    "output": f"Claude not available, using default model for {component_name}",
                    "error": False,
                    "metadata": {"fallback": True}
                }
        except:
            pass
        
        # Set forward state temporarily
        registry = get_registry()
        ci_name = f"{component_name}-ci"
        registry.set_forward_state(ci_name, "claude", " ".join(claude_cmd))
        
        return {
            "type": "system",
            "output": f"Escalated to Claude for {component_name}",
            "error": False,
            "metadata": {"escalated": True, "model": command}
        }
        
    except Exception as e:
        return {
            "type": "error",
            "output": f"Failed to escalate to Claude: {str(e)}",
            "error": True
        }


def add_chat_command_endpoint(app, component_name: str):
    """
    Add chat command endpoint to an existing FastAPI app.
    
    Args:
        app: FastAPI application instance
        component_name: Name of the component
    """
    router = create_chat_command_router(component_name)
    app.include_router(router)