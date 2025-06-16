"""
Simplified Prometheus/Epimethius API Application

This module defines a simplified FastAPI application for the Prometheus/Epimethius Planning System.
It implements the Single Port Architecture pattern with path-based routing.
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prometheus.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI application lifespan events.
    
    Args:
        app: FastAPI application
    """
    # Startup: Initialize components
    logger.info("Starting simplified Prometheus/Epimethius API...")
    
    try:
        # Initialize engines (will be implemented in future PRs)
        logger.info("Initialization complete")
        yield
    finally:
        # Cleanup: Shutdown components
        logger.info("Shutting down Prometheus/Epimethius API...")
        logger.info("Cleanup complete")


def create_app() -> FastAPI:
    """
    Create the FastAPI application.
    
    Returns:
        FastAPI application
    """
    # Use standardized port configuration
    from tekton.utils.port_config import get_prometheus_port
    port = get_prometheus_port()
    
    # Create the FastAPI application
    app = FastAPI(
        title="Prometheus/Epimethius Planning System API",
        description="API for the Prometheus/Epimethius Planning System",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (customize as needed)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    # Root router for API endpoints (simplified)
    router = APIRouter(prefix="/api", tags=["prometheus"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": "Prometheus/Epimethius Planning System API",
            "version": "0.1.0",
            "status": "online",
            "docs_url": f"http://localhost:{port}/docs"
        }
    
    # Health check endpoint (following Tekton Single Port Architecture standard)
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": "0.1.0",
            "port": port,
            "component": "prometheus"
        }
    
    # Example API endpoint
    @router.get("/status")
    async def get_status():
        return {
            "status": "success",
            "message": "Prometheus service status",
            "data": {
                "status": "running",
                "version": "0.1.0",
                "component": "prometheus"
            }
        }
    
    # Include router in main app
    app.include_router(router)
    
    return app


# Create the application instance
app = create_app()


# Run the application if this module is executed directly
if __name__ == "__main__":
    import uvicorn
    
    from tekton.utils.port_config import get_prometheus_port
    port = get_prometheus_port()
    
    print(f"Starting simplified Prometheus on port {port}...")
    
    # Start server
    uvicorn.run(
        "prometheus.api.fixed_app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )