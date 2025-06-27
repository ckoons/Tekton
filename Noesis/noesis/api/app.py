"""Noesis FastAPI Application - Discovery System"""

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
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop

config = get_component_config()
NOESIS_PORT = config.noesis.port
HERMES_URL = os.environ.get("HERMES_URL", f"http://localhost:{config.hermes.port}")
RHETOR_URL = os.environ.get("RHETOR_URL", f"http://localhost:{config.rhetor.port}")

# Component version
COMPONENT_VERSION = "0.1.0"

app = FastAPI(
    title="Noesis - Discovery System",
    description="Pattern discovery and insight generation for the Tekton ecosystem",
    version=COMPONENT_VERSION
)

# Global registration instance
hermes_registration: Optional[HermesRegistration] = None

class DiscoveryChatRequest(BaseModel):
    """Request model for discovery chat"""
    query: str
    search_scope: Optional[str] = "all"  # all, components, patterns, insights
    context: Optional[Dict] = None

class DiscoveryChatResponse(BaseModel):
    """Response model for discovery chat"""
    discoveries: List[str]
    insights: Optional[List[str]] = None
    timestamp: datetime
    metadata: Optional[Dict] = None

class TeamChatRequest(BaseModel):
    """Request model for team chat"""
    message: str
    from_component: str = "noesis"
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
        "component": "Noesis",
        "version": "0.1.0",
        "status": "active",
        "role": "Discovery System",
        "description": "I discover patterns and generate insights across the Tekton ecosystem"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Hermes registration"""
    return {
        "status": "healthy",
        "component": "noesis",
        "version": COMPONENT_VERSION,
        "timestamp": datetime.now().isoformat(),
        "port": NOESIS_PORT,
        "capabilities": [
            "discovery_chat",
            "team_chat",
            "pattern_recognition",
            "insight_generation"
        ]
    }

@app.post("/api/discovery-chat", response_model=DiscoveryChatResponse)
async def discovery_chat(request: DiscoveryChatRequest):
    """Handle discovery chat queries - pattern and insight discovery"""
    try:
        # For now, return a placeholder response
        # TODO: Integrate with actual discovery engine when implemented
        response = DiscoveryChatResponse(
            discoveries=[
                f"Searching for patterns related to: '{request.query}'",
                "Discovery system is in placeholder mode"
            ],
            insights=[
                "Noesis will provide deep insights once fully integrated"
            ],
            timestamp=datetime.now(),
            metadata={
                "search_scope": request.search_scope,
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
                "from": "noesis",
                "message": f"Noesis acknowledges: '{request.message}'",
                "timestamp": datetime.now().isoformat()
            }],
            timestamp=datetime.now()
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get detailed status of Noesis"""
    return {
        "component": "noesis",
        "status": "active",
        "ai_enabled": os.environ.get("TEKTON_REGISTER_AI", "false").lower() == "true",
        "discovery_mode": "placeholder",
        "last_activity": datetime.now().isoformat(),
        "capabilities": {
            "discovery_chat": True,
            "team_chat": True,
            "pattern_recognition": False,  # Not yet implemented
            "insight_generation": False     # Not yet implemented
        }
    }

@app.on_event("startup")
async def startup_event():
    """Register with Hermes on startup"""
    print(f"Noesis starting on port {NOESIS_PORT}")
    
    # Register with Hermes
    global hermes_registration
    hermes_registration = HermesRegistration(HERMES_URL)
    
    registration_success = await hermes_registration.register_component(
        component_name="noesis",
        port=NOESIS_PORT,
        version=COMPONENT_VERSION,
        capabilities=[
            "discovery_chat",
            "team_chat",
            "pattern_recognition", 
            "insight_generation"
        ],
        metadata={
            "description": "Discovery System",
            "type": "discovery_ai",
            "responsibilities": [
                "Discovers patterns across system components",
                "Generates insights from system behavior",
                "Identifies optimization opportunities",
                "Provides discovery-based chat interface"
            ]
        }
    )
    
    if registration_success:
        print(f"✅ Noesis registered with Hermes")
        # Start heartbeat loop
        asyncio.create_task(heartbeat_loop(hermes_registration, "noesis"))
    else:
        print(f"⚠️ Failed to register with Hermes")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Noesis shutting down...")
    if hermes_registration:
        await hermes_registration.deregister("noesis")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=NOESIS_PORT)