"""
Sophia API Server

This module implements the Sophia API server using FastAPI with Single Port Architecture,
providing HTTP and WebSocket endpoints for accessing Sophia's capabilities.
"""

import os
import sys
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utilities
from shared.utils.global_config import GlobalConfig

# Import shared API utilities
from shared.api.documentation import get_openapi_configuration
from shared.api.endpoints import create_ready_endpoint, create_discovery_endpoint, EndpointInfo
from shared.api.routers import create_standard_routers, mount_standard_routers

# Component configuration
COMPONENT_NAME = "sophia"
COMPONENT_VERSION = "0.1.0"
COMPONENT_DESCRIPTION = "Machine learning and continuous improvement system for Tekton ecosystem"

# Global variables for delayed initialization
logger = None
component = None


# Create FastAPI app with OpenAPI configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION
    )
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create standard routers
routers = create_standard_routers(COMPONENT_NAME)

# Add infrastructure endpoints
@routers.root.get("/ready")
async def ready():
    """Readiness check endpoint."""
    # Check if all engines are initialized
    all_initialized = component.check_all_engines_initialized() if component else False
    
    ready_check = create_ready_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        start_time=time.time(),
        readiness_check=lambda: all_initialized
    )
    return await ready_check()


@routers.root.get("/discovery")
async def discovery():
    """Service discovery endpoint."""
    discovery_check = create_discovery_endpoint(
        component_name=COMPONENT_NAME,
        component_version=COMPONENT_VERSION,
        component_description=COMPONENT_DESCRIPTION,
        endpoints=[
            EndpointInfo(path="/health", method="GET", description="Health check"),
            EndpointInfo(path="/ready", method="GET", description="Readiness check"),
            EndpointInfo(path="/discovery", method="GET", description="Service discovery"),
            EndpointInfo(path="/api/v1/metrics", method="*", description="Metrics management"),
            EndpointInfo(path="/api/v1/experiments", method="*", description="Experiment management"),
            EndpointInfo(path="/api/v1/recommendations", method="*", description="Recommendation system"),
            EndpointInfo(path="/api/v1/intelligence", method="*", description="Intelligence measurement"),
            EndpointInfo(path="/api/v1/research", method="*", description="Research project management"),
            EndpointInfo(path="/api/v1/components", method="*", description="Component management"),
            EndpointInfo(path="/api/v1/analytics", method="*", description="Advanced analytics"),
            EndpointInfo(path="/ws", method="WS", description="WebSocket connection")
        ],
        capabilities=component.get_capabilities() if component else [],
        dependencies={
            "hermes": "http://localhost:8001"
        },
        metadata=component.get_metadata() if component else {}
    )
    return await discovery_check()


@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    global_config = GlobalConfig.get_instance()
    port = global_config.config.sophia.port
    
    # Get component status
    if component:
        component_status = component.get_component_status()
        health_status = "healthy" if component.initialized else "degraded"
    else:
        component_status = {}
        health_status = "degraded"
    
    return {
        "status": health_status,
        "component": COMPONENT_NAME,
        "version": COMPONENT_VERSION,
        "port": port,
        "registered": component.global_config.is_registered_with_hermes if component else False,
        "engines": component_status
    }


# WebSocket manager will be imported when needed

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication using tekton_url standards."""
    from sophia.core.realtime_manager import get_websocket_manager
    websocket_manager = get_websocket_manager()
    client_id = None
    
    try:
        # Accept connection and get client ID
        client_id = await websocket_manager.connect(websocket)
        
        # Add to component's active connections for backward compatibility
        if component:
            component.active_connections.append(websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message based on type
            message_type = data.get("type")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
            
            elif message_type == "subscribe":
                # Handle subscription to specific event types using WebSocket manager
                event_types = data.get("event_types", [])
                await websocket_manager.subscribe_to_events(websocket, event_types)
                
                await websocket.send_json({
                    "type": "subscribed",
                    "event_types": event_types,
                    "client_id": client_id,
                    "timestamp": time.time()
                })
            
            elif message_type == "unsubscribe":
                # Handle unsubscription from event types
                event_types = data.get("event_types", [])
                if hasattr(websocket, "subscriptions"):
                    websocket.subscriptions.difference_update(event_types)
                
                await websocket.send_json({
                    "type": "unsubscribed",
                    "event_types": event_types,
                    "timestamp": time.time()
                })
            
            elif message_type == "experiment_monitor":
                # Handle experiment monitoring subscription using WebSocket manager
                experiment_id = data.get("experiment_id")
                if experiment_id:
                    await websocket_manager.monitor_experiment(websocket, experiment_id)
                    
                    # Send current experiment status if framework is available
                    if component and hasattr(component, 'experiment_framework') and component.experiment_framework:
                        try:
                            status = await component.experiment_framework.get_experiment_status(experiment_id)
                            await websocket.send_json({
                                "type": "experiment_status",
                                "experiment_id": experiment_id,
                                "status": status,
                                "timestamp": time.time()
                            })
                        except Exception as e:
                            logger.warning(f"Could not get experiment status: {e}")
                            await websocket.send_json({
                                "type": "experiment_monitor_started",
                                "experiment_id": experiment_id,
                                "timestamp": time.time()
                            })
            
            elif message_type == "metrics_stream":
                # Handle real-time metrics streaming using WebSocket manager
                metric_filter = data.get("filter", {})
                await websocket_manager.subscribe_to_metrics(websocket, metric_filter)
                
                await websocket.send_json({
                    "type": "metrics_stream_started",
                    "filter": metric_filter,
                    "timestamp": time.time()
                })
            
            elif message_type == "theory_validation":
                # Handle theory validation event subscription using WebSocket manager
                validation_types = data.get("validation_types", [])
                await websocket_manager.subscribe_to_theory_validation(websocket, validation_types)
                
                await websocket.send_json({
                    "type": "theory_validation_subscribed",
                    "validation_types": validation_types,
                    "timestamp": time.time()
                })
            
            elif message_type == "connection_stats":
                # Handle request for connection statistics
                stats = await websocket_manager.get_connection_stats()
                await websocket.send_json({
                    "type": "connection_stats",
                    "data": stats,
                    "timestamp": time.time()
                })
            
            elif message_type == "metric":
                # Handle real-time metric submission
                if component and component.metrics_engine:
                    metric_data = data.get("data", {})
                    await component.metrics_engine.record_metric(
                        metric_id=metric_data.get("metric_id"),
                        value=metric_data.get("value"),
                        source=metric_data.get("source"),
                        timestamp=metric_data.get("timestamp"),
                        context=metric_data.get("context"),
                        tags=metric_data.get("tags")
                    )
                    await websocket.send_json({
                        "type": "metric_received",
                        "timestamp": time.time()
                    })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": time.time()
                })
    
    except WebSocketDisconnect:
        # Handle disconnection using WebSocket manager
        websocket_manager.disconnect(websocket)
        # Remove from component's active connections for backward compatibility
        if component and websocket in component.active_connections:
            component.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        # Handle error disconnection using WebSocket manager
        websocket_manager.disconnect(websocket)
        if component and websocket in component.active_connections:
            component.active_connections.remove(websocket)


# Endpoint routers will be loaded during startup

# Mount standard routers
mount_standard_routers(app, routers)

@app.on_event("startup")
async def startup_event():
    """Component startup callback."""
    import sys
    print("=== SOPHIA STARTUP EVENT CALLED ===", file=sys.stderr)
    print("=== SOPHIA STARTUP EVENT CALLED ===", flush=True)
    with open("/tmp/sophia_startup.txt", "w") as f:
        f.write("SOPHIA STARTUP EVENT WAS CALLED!\n")
    # Re-enable background initialization
    asyncio.create_task(delayed_initialization())

async def delayed_initialization():
    """Perform delayed initialization after uvicorn startup completes."""
    global component, logger
    try:
        # Wait 10 seconds to allow uvicorn to complete its startup sequence
        print("Waiting for uvicorn startup to complete...")
        await asyncio.sleep(10)
        
        # Now do delayed initialization
        print("Initializing logging and component...")
        
        # Set up logging
        from shared.utils.logging_setup import setup_component_logging
        logger = setup_component_logging("sophia")
        logger.info("Sophia delayed initialization started")
        
        # Import and create component
        logger.info("Creating Sophia component...")
        from sophia.core.sophia_component import SophiaComponent
        component = SophiaComponent()
        logger.info("Sophia component created successfully")
        
        # Load endpoint routers now that component is available
        logger.info("Loading endpoint routers...")
        from sophia.api.endpoints import (
            metrics,
            experiments,
            recommendations,
            intelligence,
            research,
            components,
            analytics
        )
        logger.info("Endpoint modules imported successfully")
        
        # Include endpoint routers
        logger.info("Registering endpoint routers...")
        routers.v1.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
        routers.v1.include_router(experiments.router, prefix="/experiments", tags=["Experiments"])
        routers.v1.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
        routers.v1.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
        routers.v1.include_router(research.router, prefix="/research", tags=["Research"])
        routers.v1.include_router(components.router, prefix="/components", tags=["Components"])
        routers.v1.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
        logger.info("All endpoint routers registered successfully")
        
        # Import and include MCP router
        try:
            from sophia.api.fastmcp_endpoints import mcp_router
            app.include_router(mcp_router)
            logger.info("FastMCP router registered successfully")
        except ImportError:
            logger.warning("FastMCP endpoints not available")
        
        # Use the proper full initialization
        logger.info("Starting full component initialization...")
        
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        logger.info("Component initialization completed")
        
        logger.info("All engines should now be running")
        return  # Exit before MCP bridge initialization
        
        logger.info("Starting component initialization...")
        await component.initialize(
            capabilities=component.get_capabilities(),
            metadata=component.get_metadata()
        )
        logger.info("Component initialization completed")
        
        # Initialize MCP bridge after component startup
        logger.info("Initializing MCP bridge...")
        await component.initialize_mcp_bridge()
        logger.info("MCP bridge initialization completed")
        
        # Include custom MCP routes
        try:
            from sophia.core.mcp.hermes_bridge import get_mcp_routes
            mcp_routes = get_mcp_routes()
            if mcp_routes:
                app.include_router(mcp_routes, prefix="/mcp", tags=["MCP"])
                logger.info("Custom MCP routes registered successfully")
        except Exception as e:
            logger.debug(f"MCP routes not available: {e}")
        
        logger.info(f"Sophia API server started successfully")
    except Exception as e:
        error_msg = f"Failed to start Sophia: {e}"
        if logger:
            logger.error(error_msg)
            logger.exception("Full traceback:")
        else:
            print(error_msg)
            import traceback
            traceback.print_exc()
        # Re-raise to ensure the task failure is visible
        raise

# Custom MCP routes will be loaded during startup


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global component, logger
    print("=== SOPHIA SHUTDOWN INITIATED ===", file=sys.stderr)
    print("=== SOPHIA SHUTDOWN INITIATED ===", flush=True)
    
    if logger:
        logger.info("=== SOPHIA SHUTDOWN INITIATED ===")
        logger.info("Sophia shutting down...")
    
    try:
        if component:
            print("Cleaning up component resources...")
            if logger:
                logger.info("Cleaning up component resources...")
            # Cleanup component resources
            await component.cleanup()
            print("Sophia component cleaned up successfully")
            if logger:
                logger.info("Sophia component cleaned up successfully")
        else:
            print("No component instance to cleanup")
            if logger:
                logger.warning("No component instance to cleanup")
    except Exception as e:
        print(f"Error during Sophia shutdown: {e}")
        if logger:
            logger.error(f"Error during Sophia shutdown: {e}")
    finally:
        print("=== SOPHIA SHUTDOWN COMPLETE ===")
        if logger:
            logger.info("=== SOPHIA SHUTDOWN COMPLETE ===")


if __name__ == "__main__":
    import uvicorn
    
    global_config = GlobalConfig.get_instance()
    port = global_config.config.sophia.port
    
    print(f"Starting Sophia on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)