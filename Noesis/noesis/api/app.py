"""Noesis FastAPI Application - Discovery System"""

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
    performance_boundary
)

# Get configuration from environment - NO HARDCODED DEFAULTS
import sys
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop

config = get_component_config()
NOESIS_PORT = config.noesis.port
# Use tekton_url for proper URL construction
from shared.urls import tekton_url
from shared.env import TektonEnviron
HERMES_URL = TektonEnviron.get("HERMES_URL", tekton_url("hermes"))
RHETOR_URL = TektonEnviron.get("RHETOR_URL", tekton_url("rhetor"))

# Component version
COMPONENT_VERSION = "0.1.0"

app = FastAPI(
    title="Noesis - Discovery System",
    description="Pattern discovery and insight generation for the Tekton ecosystem",
    version=COMPONENT_VERSION
)

# Import and include analysis endpoints
from .analysis_endpoints import router as analysis_router
from .sophia_endpoints import router as sophia_router
from .streaming_endpoints import streaming_router
app.include_router(analysis_router)
app.include_router(sophia_router)
app.include_router(streaming_router)

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

# Global component instance for dependency injection
noesis_component = None

async def get_component_instance():
    """Get the Noesis component instance for API endpoints"""
    global noesis_component
    if noesis_component is None:
        # Initialize component if not already done
        from noesis.core.noesis_component import NoesisComponent
        noesis_component = NoesisComponent()
        await noesis_component.init()
    return noesis_component

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
            "insight_generation",
            "theoretical_analysis",
            "manifold_analysis",
            "dynamics_modeling",
            "catastrophe_detection"
        ]
    }

@app.post("/api/discovery-chat", response_model=DiscoveryChatResponse)
@api_contract(
    title="Discovery Chat API",
    endpoint="/api/discovery-chat",
    method="POST",
    request_schema={"query": "string", "search_scope": "string", "context": "object"},
    response_schema={"discoveries": "list", "insights": "list", "timestamp": "datetime", "metadata": "object"}
)
@performance_boundary(
    title="Pattern Recognition Performance",
    sla="<1s for basic queries, <5s for complex analysis",
    optimization_notes="Uses caching for discovered patterns and incremental updates",
    metrics={"target_latency": "1s", "max_latency": "5s"}
)
async def discovery_chat(request: DiscoveryChatRequest):
    """Handle discovery chat queries - pattern and insight discovery"""
    try:
        # Get Noesis component instance for analysis
        noesis_component = await get_component_instance()
        if not noesis_component:
            raise HTTPException(status_code=503, detail="Noesis component not available")
        
        # Check if AI is available
        from shared.ai.simple_ai import ai_send
        
        # Create a discovery-focused prompt
        prompt = f"[Discovery Query - Scope: {request.search_scope}] {request.query}"
        
        # Send to noesis-ai on port 45015
        ai_response = await ai_send("noesis-ai", prompt, "localhost", 45015)
        
        discoveries = []
        insights = []
        
        if ai_response and ai_response != "AI_NOT_RUNNING":
            # Parse AI response for discoveries and insights
            discoveries = [ai_response]
            
            # Use theoretical framework for additional insights
            if hasattr(noesis_component, 'theoretical_framework'):
                try:
                    # Generate theoretical insights based on the query
                    theoretical_insights = await noesis_component.generate_theoretical_insights(
                        request.query, request.search_scope, request.context
                    )
                    if theoretical_insights:
                        insights.extend(theoretical_insights)
                except Exception as e:
                    logger.warning(f"Failed to generate theoretical insights: {e}")
                    
            mode = "ai_with_analysis"
        else:
            # No fallback - require AI to be running
            raise HTTPException(
                status_code=503, 
                detail="Noesis AI is not available. Please ensure the AI specialist is running on port 45015."
            )
            
        response = DiscoveryChatResponse(
            discoveries=discoveries,
            insights=insights,
            timestamp=datetime.now(),
            metadata={
                "search_scope": request.search_scope,
                "mode": mode,
                "ai_port": 45015
            }
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/team-chat", response_model=TeamChatResponse)
@api_contract(
    title="Team Chat API",
    endpoint="/api/team-chat",
    method="POST",
    request_schema={"message": "string", "from_component": "string", "to_components": "list", "broadcast": "bool"}
)
async def team_chat(request: TeamChatRequest):
    """Handle team chat messages - communication with other AIs"""
    try:
        import httpx
        
        responses = []
        
        # Route through Rhetor's team chat system
        try:
            async with httpx.AsyncClient() as client:
                rhetor_response = await client.post(
                    f"{RHETOR_URL}/api/team-chat",
                    json={
                        "message": request.message,
                        "from_component": request.from_component,
                        "to_components": request.to_components,
                        "broadcast": request.broadcast
                    },
                    timeout=10.0
                )
                
                if rhetor_response.status_code == 200:
                    rhetor_data = rhetor_response.json()
                    if "responses" in rhetor_data:
                        responses.extend(rhetor_data["responses"])
                else:
                    logger.warning(f"Rhetor team chat failed: {rhetor_response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to connect to Rhetor team chat: {e}")
            
        # Add Noesis's own response
        noesis_component = await get_component_instance()
        if noesis_component:
            try:
                # Generate a discovery-oriented response using Noesis AI
                from shared.ai.simple_ai import ai_send
                ai_response = await ai_send(
                    "noesis-ai", 
                    f"Team chat message: {request.message}. Respond from Noesis discovery perspective.", 
                    "localhost", 
                    45015
                )
                
                if ai_response and ai_response != "AI_NOT_RUNNING":
                    noesis_response = ai_response
                else:
                    noesis_response = f"Noesis discovery system analyzing: '{request.message}'"
                    
            except Exception as e:
                logger.warning(f"Noesis AI response failed: {e}")
                noesis_response = f"Noesis acknowledging team message: '{request.message}'"
        else:
            noesis_response = f"Noesis system acknowledging: '{request.message}'"
            
        responses.append({
            "from": "noesis",
            "message": noesis_response,
            "timestamp": datetime.now().isoformat(),
            "component_type": "discovery_system"
        })
        
        response = TeamChatResponse(
            responses=responses,
            timestamp=datetime.now()
        )
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get detailed status of Noesis"""
    try:
        # Check AI availability
        from shared.ai.simple_ai import ai_send
        ai_response = await ai_send("noesis-ai", "health check", "localhost", 45015)
        ai_available = ai_response and ai_response != "AI_NOT_RUNNING"
        
        # Check component availability
        noesis_component = await get_component_instance()
        component_available = noesis_component is not None
        
        # Determine discovery mode based on availability
        if ai_available and component_available:
            discovery_mode = "full_analysis"
        elif ai_available:
            discovery_mode = "ai_only"
        elif component_available:
            discovery_mode = "component_only"
        else:
            discovery_mode = "limited"
            
        # Check theoretical framework capabilities
        theoretical_capabilities = {}
        if component_available and hasattr(noesis_component, 'theoretical_framework'):
            framework = noesis_component.theoretical_framework
            theoretical_capabilities = {
                "manifold_analysis": hasattr(framework, 'manifold_analyzer'),
                "dynamics_modeling": hasattr(framework, 'dynamics_analyzer'),
                "catastrophe_detection": hasattr(framework, 'catastrophe_analyzer'),
                "synthesis_analysis": hasattr(framework, 'synthesis_analyzer')
            }
        else:
            theoretical_capabilities = {
                "manifold_analysis": False,
                "dynamics_modeling": False,
                "catastrophe_detection": False,
                "synthesis_analysis": False
            }
        
        return {
            "component": "noesis",
            "status": "active",
            "ai_enabled": ai_available,
            "ai_port": 45015,
            "component_available": component_available,
            "discovery_mode": discovery_mode,
            "last_activity": datetime.now().isoformat(),
            "capabilities": {
                "discovery_chat": ai_available,
                "team_chat": True,  # Always available (with fallback)
                "pattern_recognition": ai_available and component_available,
                "insight_generation": ai_available and component_available,
                **theoretical_capabilities
            },
            "integrations": {
                "rhetor_team_chat": True,
                "engram_streaming": component_available,
                "sophia_bridge": component_available
            }
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "component": "noesis",
            "status": "error",
            "error": str(e),
            "ai_enabled": False,
            "discovery_mode": "error",
            "last_activity": datetime.now().isoformat()
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
    print(f"Noesis starting on port {NOESIS_PORT}")
    
    # Initialize Noesis component
    global noesis_component
    try:
        await get_component_instance()
        print("✅ Noesis component initialized")
    except Exception as e:
        print(f"⚠️ Warning: Noesis component initialization failed: {e}")
    
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
            "insight_generation",
            "theoretical_analysis",
            "manifold_analysis",
            "dynamics_modeling",
            "catastrophe_detection",
            "engram_streaming",
            "memory_analysis",
            "real_time_insights"
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
    
    # Cleanup component
    global noesis_component
    if noesis_component:
        try:
            await noesis_component.shutdown()
            print("✅ Noesis component shut down")
        except Exception as e:
            print(f"⚠️ Warning: Error during component shutdown: {e}")
    
    # Deregister from Hermes
    if hermes_registration:
        await hermes_registration.deregister("noesis")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=NOESIS_PORT)