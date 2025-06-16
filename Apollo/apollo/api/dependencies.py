"""
Apollo API Dependencies.

This module provides dependency injection functions for FastAPI routes
to access shared resources like the ApolloManager.
"""

from typing import Optional
from fastapi import Depends, HTTPException, Request, status

# from shared.debug.debug_utils import debug_log, log_function
# Fallback debug utilities
class DebugLog:
    def __getattr__(self, name):
        def dummy_log(*args, **kwargs):
            pass
        return dummy_log
debug_log = DebugLog()

def log_function(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
from apollo.core.apollo_manager import ApolloManager

@log_function()
def get_apollo_manager(request: Request) -> ApolloManager:
    """
    Get the Apollo Manager instance from the application state.
    
    This function is used as a FastAPI dependency to inject the Apollo Manager
    into route handlers. It ensures the manager exists and is properly initialized.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Apollo Manager instance
        
    Raises:
        HTTPException: If the Apollo Manager is not initialized
    """
    if not hasattr(request.app.state, "apollo_manager") or not request.app.state.apollo_manager:
        debug_log.error("apollo", "Apollo Manager not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Apollo Manager not initialized"
        )
    
    # Get the Apollo Manager from app state
    apollo_manager = request.app.state.apollo_manager
    debug_log.debug("apollo", "Retrieved Apollo Manager from app state")
    
    return apollo_manager