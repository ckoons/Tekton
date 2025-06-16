"""
Standardized shutdown endpoint for Tekton components.

This module provides a reusable shutdown endpoint implementation that can be
added to any FastAPI-based Tekton component to enable graceful HTTP-based shutdown.
"""
import asyncio
import logging
import os
import sys
import signal
from typing import Optional, Callable, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

logger = logging.getLogger(__name__)


def create_shutdown_router(
    component_name: str,
    cleanup_tasks: Optional[List[Callable]] = None,
    shutdown_delay: float = 0.5
) -> APIRouter:
    """
    Create a shutdown router with standardized endpoints.
    
    Args:
        component_name: Name of the component
        cleanup_tasks: Optional list of async cleanup functions to run before shutdown
        shutdown_delay: Delay in seconds before process termination (default: 0.5)
        
    Returns:
        FastAPI router with shutdown endpoints
    """
    router = APIRouter(tags=["shutdown"])
    
    async def perform_shutdown():
        """Execute shutdown sequence."""
        logger.info(f"[{component_name}] Initiating graceful shutdown...")
        
        # Run cleanup tasks if provided
        if cleanup_tasks:
            logger.info(f"[{component_name}] Running {len(cleanup_tasks)} cleanup tasks...")
            for task in cleanup_tasks:
                try:
                    if asyncio.iscoroutinefunction(task):
                        await task()
                    else:
                        task()
                    logger.info(f"[{component_name}] Cleanup task {task.__name__} completed")
                except Exception as e:
                    logger.error(f"[{component_name}] Error in cleanup task {task.__name__}: {e}")
        
        # Give time for response to be sent
        await asyncio.sleep(shutdown_delay)
        
        # Exit the process
        logger.info(f"[{component_name}] Exiting process...")
        # Use os._exit to ensure immediate termination
        os._exit(0)
    
    @router.post("/shutdown")
    async def shutdown():
        """
        Graceful shutdown endpoint.
        
        Initiates a graceful shutdown of the component by:
        1. Running any registered cleanup tasks
        2. Waiting briefly for the response to be sent
        3. Terminating the process
        
        Returns:
            JSONResponse confirming shutdown initiation
        """
        logger.info(f"[{component_name}] Shutdown requested via HTTP endpoint")
        
        # Schedule shutdown to run after response is sent
        asyncio.create_task(perform_shutdown())
        
        return JSONResponse(
            status_code=202,  # Accepted
            content={
                "status": "accepted",
                "message": f"{component_name} shutdown initiated",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @router.post("/api/shutdown")
    async def api_shutdown():
        """Alternative shutdown endpoint at /api/shutdown."""
        return await shutdown()
    
    @router.get("/shutdown/status")
    async def shutdown_status():
        """
        Check if component supports graceful shutdown.
        
        Returns:
            Status information about shutdown support
        """
        return {
            "shutdown_supported": True,
            "component": component_name,
            "endpoints": ["/shutdown", "/api/shutdown"],
            "method": "POST",
            "cleanup_tasks": len(cleanup_tasks) if cleanup_tasks else 0
        }
    
    return router


def add_shutdown_endpoint_to_app(
    app,
    component_name: str,
    cleanup_tasks: Optional[List[Callable]] = None
):
    """
    Add shutdown endpoints to an existing FastAPI app.
    
    This is a convenience function that creates and includes the shutdown router.
    
    Args:
        app: FastAPI application instance
        component_name: Name of the component
        cleanup_tasks: Optional list of async cleanup functions
        
    Example:
        ```python
        from fastapi import FastAPI
        from shared.utils.shutdown_endpoint import add_shutdown_endpoint_to_app
        
        app = FastAPI()
        
        async def cleanup_database():
            # Cleanup database connections
            pass
            
        async def cleanup_cache():
            # Cleanup cache
            pass
        
        add_shutdown_endpoint_to_app(
            app, 
            "mycomponent",
            cleanup_tasks=[cleanup_database, cleanup_cache]
        )
        ```
    """
    shutdown_router = create_shutdown_router(component_name, cleanup_tasks)
    app.include_router(shutdown_router)
    logger.info(f"[{component_name}] Added shutdown endpoints: /shutdown, /api/shutdown")