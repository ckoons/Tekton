"""Numa FastAPI Application - Platform AI Mentor"""

import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Landmark imports
from landmarks import (
    architecture_decision,
    state_checkpoint,
    api_contract,
    integration_point,
    danger_zone
)

# Get configuration from environment - NO HARDCODED DEFAULTS
import sys
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop

config = get_component_config()
NUMA_PORT = config.numa.port
HERMES_URL = os.environ.get("HERMES_URL", f"http://localhost:{config.hermes.port}")
RHETOR_URL = os.environ.get("RHETOR_URL", f"http://localhost:{config.rhetor.port}")

# Component version
COMPONENT_VERSION = "0.1.0"

app = FastAPI(
    title="Numa - Platform AI Mentor",
    description="Platform-wide AI mentor that oversees and guides the Tekton ecosystem",
    version=COMPONENT_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global registration instance
hermes_registration: Optional[HermesRegistration] = None

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
        "component": "Numa",
        "version": "0.1.0",
        "status": "active",
        "role": "Platform AI Mentor",
        "description": "I oversee and guide the entire Tekton ecosystem"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Hermes registration"""
    return {
        "status": "healthy",
        "component": "numa",
        "version": COMPONENT_VERSION,
        "timestamp": datetime.now().isoformat(),
        "port": NUMA_PORT,
        "capabilities": [
            "companion_chat",
            "team_chat",
            "platform_guidance",
            "component_mentoring"
        ]
    }

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
        # Check if AI is available
        from shared.ai.simple_ai import ai_send
        
        # Send to numa-ai on port 45016
        ai_response = await ai_send("numa-ai", request.message, "localhost", 45016)
        
        if ai_response and ai_response != "AI_NOT_RUNNING":
            response_text = ai_response
        else:
            # Fallback to placeholder if AI not available
            response_text = f"Numa acknowledges: '{request.message}'. As the platform mentor, I'm here to help guide you through the Tekton ecosystem."
            
        response = CompanionChatResponse(
            response=response_text,
            timestamp=datetime.now(),
            metadata={
                "user_id": request.user_id,
                "mode": "ai" if ai_response != "AI_NOT_RUNNING" else "placeholder"
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
    """Handle team chat messages - communication with other AIs"""
    try:
        # For now, return a placeholder response
        # TODO: Route through Rhetor's team chat system
        response = TeamChatResponse(
            responses=[{
                "from": "numa",
                "message": f"Numa received team message: '{request.message}'",
                "timestamp": datetime.now().isoformat()
            }],
            timestamp=datetime.now()
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get detailed status of Numa"""
    return {
        "component": "numa",
        "status": "active",
        "ai_enabled": True,  # AI is always enabled with fixed ports
        "connected_components": [],  # TODO: Query from Hermes
        "last_activity": datetime.now().isoformat(),
        "capabilities": {
            "companion_chat": True,
            "team_chat": True,
            "platform_monitoring": True,
            "component_mentoring": True
        }
    }

@app.on_event("startup")
@integration_point(
    title="Hermes Service Registration",
    target_component="Hermes",
    protocol="HTTP REST API",
    data_flow="Registration request -> Hermes -> Acknowledgment"
)
async def startup_event():
    """Register with Hermes on startup"""
    print(f"Numa starting on port {NUMA_PORT}")
    
    # Register with Hermes
    global hermes_registration
    hermes_registration = HermesRegistration(HERMES_URL)
    
    registration_success = await hermes_registration.register_component(
        component_name="numa",
        port=NUMA_PORT,
        version=COMPONENT_VERSION,
        capabilities=[
            "companion_chat",
            "team_chat", 
            "platform_guidance",
            "component_mentoring"
        ],
        metadata={
            "description": "Platform AI Mentor",
            "type": "platform_ai",
            "responsibilities": [
                "Provides guidance and mentorship to platform users",
                "Facilitates team communication between components",
                "Monitors overall system health and patterns"
            ]
        }
    )
    
    if registration_success:
        print(f"✅ Numa registered with Hermes")
        # Start heartbeat loop
        asyncio.create_task(heartbeat_loop(hermes_registration, "numa"))
    else:
        print(f"⚠️ Failed to register with Hermes")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Numa shutting down...")
    if hermes_registration:
        await hermes_registration.deregister("numa")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=NUMA_PORT)