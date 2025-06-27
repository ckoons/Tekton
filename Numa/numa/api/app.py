"""Numa FastAPI Application - Platform AI Mentor"""

import os
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Get configuration from environment - NO HARDCODED DEFAULTS
import sys
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

config = get_component_config()
NUMA_PORT = config.numa.port
HERMES_URL = os.environ.get("HERMES_URL", f"http://localhost:{config.hermes.port}")
RHETOR_URL = os.environ.get("RHETOR_URL", f"http://localhost:{config.rhetor.port}")

app = FastAPI(
    title="Numa - Platform AI Mentor",
    description="Platform-wide AI mentor that oversees and guides the Tekton ecosystem",
    version="0.1.0"
)

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
async def companion_chat(request: CompanionChatRequest):
    """Handle companion chat messages - direct interaction with user"""
    try:
        # For now, return a placeholder response
        # TODO: Integrate with actual AI when TEKTON_REGISTER_AI is enabled
        response = CompanionChatResponse(
            response=f"Numa acknowledges: '{request.message}'. As the platform mentor, I'm here to help guide you through the Tekton ecosystem.",
            timestamp=datetime.now(),
            metadata={
                "user_id": request.user_id,
                "mode": "placeholder"
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/team-chat", response_model=TeamChatResponse)
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
        "ai_enabled": os.environ.get("TEKTON_REGISTER_AI", "false").lower() == "true",
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
async def startup_event():
    """Register with Hermes on startup"""
    print(f"Numa starting on port {NUMA_PORT}")
    
    # Register with Hermes
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            registration_data = {
                "name": "numa",
                "port": NUMA_PORT,
                "health_endpoint": "/health",
                "description": "Platform AI Mentor",
                "capabilities": [
                    "companion_chat",
                    "team_chat",
                    "platform_guidance",
                    "component_mentoring"
                ]
            }
            response = await client.post(
                f"{HERMES_URL}/api/register",
                json=registration_data
            )
            if response.status_code == 200:
                print(f"✅ Numa registered with Hermes")
            else:
                print(f"⚠️ Failed to register with Hermes: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not register with Hermes: {e}")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Numa shutting down...")
    
    # Deregister from Hermes
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{HERMES_URL}/api/components/numa"
            )
            if response.status_code == 200:
                print("✅ Numa deregistered from Hermes")
    except Exception as e:
        print(f"⚠️ Could not deregister from Hermes: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=NUMA_PORT)