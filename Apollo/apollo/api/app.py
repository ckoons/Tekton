"""FastAPI application for Apollo"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

# Add parent directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Add Tekton root to path for shared imports
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn

# Import Apollo components
from ..core.apollo_component import ApolloComponent
from ..api.routes import api_router, ws_router, metrics_router
from ..api.endpoints.mcp import mcp_router

# Use shared logging setup
from shared.utils.logging_setup import setup_component_logging
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop

logger = setup_component_logging("apollo")

# Models
class HealthResponse(BaseModel):
    """Model for health response"""
    status: str
    uptime: float
    version: str
    component_name: str

# Lifespan handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    global apollo_component, hermes_registration
    
    # Startup
    apollo_component = ApolloComponent()
    await apollo_component.initialize(
        capabilities=[
            "predictive_intelligence",
            "attention_management",
            "context_monitoring",
            "action_planning",
            "protocol_enforcement",
            "token_budgeting"
        ],
        metadata={
            "description": "Predictive Intelligence and Attention Management",
            "type": "ai_component",
            "responsibilities": [
                "Monitor context health across all CIs",
                "Predict future states and issues",
                "Plan optimal actions for system health",
                "Enforce protocols and budgets"
            ]
        }
    )
    logger.info("Apollo component initialized")
    
    # Register with Hermes
    from shared.urls import hermes_url
    hermes_registration = HermesRegistration(hermes_url())
    
    from tekton.utils.port_config import get_apollo_port
    port = get_apollo_port()
    
    registration_success = await hermes_registration.register_component(
        component_name="apollo",
        port=port,
        version=VERSION,
        capabilities=[
            "predictive_intelligence",
            "attention_management",
            "context_monitoring",
            "action_planning"
        ],
        metadata={
            "description": "Predictive Intelligence Component",
            "type": "ai_component"
        }
    )
    
    if registration_success:
        logger.info("✅ Apollo registered with Hermes")
        # Start heartbeat loop
        asyncio.create_task(heartbeat_loop(hermes_registration, "apollo"))
    else:
        logger.warning("⚠️ Failed to register with Hermes")
    
    # Store component in app state for access in routes
    app.state.apollo_manager = apollo_component.apollo_manager
    
    yield
    
    # Shutdown
    if apollo_component:
        await apollo_component.shutdown()
        logger.info("Apollo component cleaned up")
    if hermes_registration:
        await hermes_registration.deregister("apollo")

# Application
app = FastAPI(
    title="Apollo API", 
    description="Predictive Intelligence and Attention Management for Tekton",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(api_router, prefix="/api", tags=["api"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])
app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
app.include_router(mcp_router, prefix="/mcp", tags=["mcp"])

# Application startup time
START_TIME = time.time()
VERSION = "1.0.0"

# Global instances
apollo_component: Optional[ApolloComponent] = None
hermes_registration: Optional[HermesRegistration] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Apollo API", "version": VERSION}

@app.get("/health", response_model=HealthResponse)
@api_contract(
    title="Health Check API",
    endpoint="/health",
    method="GET",
    response_schema={"status": "str", "uptime": "float", "version": "str", "component_name": "str"}
)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - START_TIME
    
    return {
        "status": "healthy",
        "uptime": uptime,
        "version": VERSION,
        "component_name": "apollo"
    }

# Server startup function
async def start_server(host: str = "0.0.0.0", port: int = None):
    """Start the Apollo API server
    
    Args:
        host: Host to bind to
        port: Port to bind the API server to (defaults to Apollo's standard port)
    """
    import uvicorn
    
    # Set default port using centralized config
    if port is None:
        from tekton.utils.port_config import get_apollo_port
        port = get_apollo_port()
        logger.info(f"Using Apollo port: {port}")
    
    logger.info(f"Starting Apollo API on {host}:{port}")
    
    # Start the FastAPI server
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    """Run the server when executed directly"""
    import sys
    
    # Get port from command line if provided
    port = None
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    
    # Run the server
    asyncio.run(start_server(port=port))