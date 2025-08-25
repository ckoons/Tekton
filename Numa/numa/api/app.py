"""Numa FastAPI Application - Platform CI Mentor (Refactored)"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
import httpx

# Landmark imports
from landmarks import (
    architecture_decision,
    state_checkpoint,
    api_contract,
    integration_point,
    danger_zone
)

from shared.env import TektonEnviron
from shared.urls import hermes_url, rhetor_url, numa_url
from shared.ai.simple_ai import ai_send
from shared.workflow.endpoint_template import create_workflow_endpoint
from shared.api.chat_command_endpoint import add_chat_command_endpoint
from numa.core.numa_component import NumaComponent

# Component instance
numa_component = NumaComponent()

async def startup_callback():
    """Initialize Numa during startup."""
    # Initialize the component (registers with Hermes, etc.)
    await numa_component.initialize(
        capabilities=numa_component.get_capabilities(),
        metadata=numa_component.get_metadata()
    )

# Create FastAPI app using StandardComponentBase
app = numa_component.create_app(startup_callback=startup_callback)

# Include standardized workflow endpoint
workflow_router = create_workflow_endpoint("numa")
app.include_router(workflow_router)

# Add chat command endpoint for [command] support
add_chat_command_endpoint(app, "numa")

class CompanionChatRequest(BaseModel):
    """Request model for companion chat"""
    message: str
    user_id: Optional[str] = "default"
    context: Optional[Dict] = None

class CompanionChatResponse(BaseModel):
    """Response model for companion chat"""
    response: str
    timestamp: datetime
    metadata: Optional[Dict] = None

class TeamChatRequest(BaseModel):
    """Request model for team chat"""
    message: str
    from_component: str = "numa"
    to_components: Optional[List[str]] = None
    broadcast: bool = False

class TeamChatResponse(BaseModel):
    """Response model for team chat"""
    responses: List[Dict]
    timestamp: datetime

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "component": numa_component.component_name,
        "version": numa_component.version,
        "status": "active",
        "role": "Platform CI Mentor",
        "description": "I oversee and guide the entire Tekton ecosystem"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Hermes registration"""
    return numa_component.get_health_status()

@app.post("/api/companion-chat", response_model=CompanionChatResponse)
@api_contract(
    title="Companion Chat API",
    endpoint="/api/companion-chat",
    method="POST",
    request_schema={"message": "string", "user_id": "string", "context": "object"}
)
@state_checkpoint(
    title="User Context Management",
    state_type="user_session",
    persistence=False,
    consistency_requirements="Maintain conversation context within session",
    recovery_strategy="Start fresh conversation on session loss"
)
async def companion_chat(request: CompanionChatRequest):
    """Handle companion chat messages - direct interaction with user"""
    try:
        # Get CI configuration from environment
        ai_host = TektonEnviron.get("NUMA_AI_HOST", "localhost")
        ai_port = int(TektonEnviron.get("NUMA_AI_PORT", "45016"))
        
        # Send to numa-ci socket
        ai_response = await ai_send("numa-ci", request.message, ai_host, ai_port)
        
        if ai_response and ai_response != "AI_NOT_RUNNING":
            response_text = ai_response
            ai_mode = "ai"
        else:
            # Fallback response when CI not available
            response_text = f"Numa acknowledges: '{request.message}'. As the platform mentor, I'm here to help guide you through the Tekton ecosystem."
            ai_mode = "fallback"
        
        response = CompanionChatResponse(
            response=response_text,
            timestamp=datetime.now(),
            metadata={
                "user_id": request.user_id,
                "mode": ai_mode
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/team-chat", response_model=TeamChatResponse)
@api_contract(
    title="Team Chat API",
    endpoint="/api/team-chat",
    method="POST",
    request_schema={"message": "string", "from_component": "string", "to_components": "list", "broadcast": "bool"}
)
@integration_point(
    title="Cross-Component Communication Hub",
    target_component="Rhetor",
    protocol="HTTP REST API",
    data_flow="Numa -> Rhetor -> Target components -> Responses"
)
async def team_chat(request: TeamChatRequest):
    """Handle team chat messages - communication with other CIs"""
    try:
        # Route through Rhetor's team chat system
        async with httpx.AsyncClient() as client:
            rhetor_response = await client.post(
                f"{rhetor_url()}/api/team-chat",
                json={
                    "from_component": request.from_component,
                    "message": request.message,
                    "to_components": request.to_components,
                    "broadcast": request.broadcast
                },
                timeout=30.0
            )
            
            if rhetor_response.status_code == 200:
                data = rhetor_response.json()
                return TeamChatResponse(
                    responses=data.get("responses", []),
                    timestamp=datetime.now()
                )
            else:
                # Fallback response if Rhetor is unavailable
                return TeamChatResponse(
                    responses=[{
                        "from": "numa",
                        "message": f"Numa acknowledged message: '{request.message}' (Rhetor unavailable)",
                        "timestamp": datetime.now().isoformat()
                    }],
                    timestamp=datetime.now()
                )
    except httpx.RequestError:
        # Fallback response on connection error
        return TeamChatResponse(
            responses=[{
                "from": "numa",
                "message": f"Numa acknowledged message: '{request.message}' (Network error)",
                "timestamp": datetime.now().isoformat()
            }],
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get detailed status of Numa"""
    # Query connected components from Hermes
    connected_components = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{hermes_url()}/api/v1/registry/components")
            if response.status_code == 200:
                components = response.json()
                connected_components = [comp["name"] for comp in components if comp.get("status") == "healthy"]
    except:
        pass  # Continue with empty list if Hermes is unavailable
    
    return {
        "component": numa_component.component_name,
        "status": "active",
        "ai_enabled": True,
        "connected_components": connected_components,
        "last_activity": datetime.now().isoformat(),
        "capabilities": numa_component.get_capabilities()
    }


# Startup and shutdown events are handled by StandardComponentBase
# The component will automatically register with Hermes on startup
# and deregister on shutdown

if __name__ == "__main__":
    import uvicorn
    from shared.utils.env_config import get_component_config
    
    config = get_component_config()
    port = config.numa.port
    
    uvicorn.run(app, host="0.0.0.0", port=port)
