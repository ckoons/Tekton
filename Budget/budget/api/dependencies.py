"""
Budget API Dependencies

This module defines dependencies for the Budget API endpoints, such as
authentication, pagination, and common parameters.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, Header, Query, Path, Security
from fastapi.security import APIKeyHeader

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
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

# Define security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
authorization_header = APIKeyHeader(name="Authorization", auto_error=False)

# Authentication and Authorization

@log_function()
async def get_authenticated_user(
    api_key: Optional[str] = Security(api_key_header),
    authorization: Optional[str] = Security(authorization_header)
) -> Dict[str, Any]:
    """
    Authenticate the user based on API key or Bearer token.
    
    Args:
        api_key: The API key from the X-API-Key header
        authorization: The Bearer token from the Authorization header
        
    Returns:
        A dictionary containing user information
    
    Raises:
        HTTPException: If authentication fails
    """
    debug_log.debug("budget_api", "Authentication attempt")
    
    # For development, accept all authentication
    # In production, this would validate against a proper auth system
    if os.getenv("BUDGET_API_REQUIRE_AUTH", "false").lower() == "true":
        if not api_key and not authorization:
            debug_log.warn("budget_api", "Authentication failed: No credentials provided")
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    # For now, return a simple user info dictionary
    # In production, this would contain actual user information
    user_info = {
        "user_id": "default-user",
        "roles": ["user"],
        "component": "budget"
    }
    
    debug_log.info("budget_api", f"Authentication successful for user {user_info['user_id']}")
    return user_info

# Pagination

@log_function()
async def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
) -> Dict[str, int]:
    """
    Get pagination parameters.
    
    Args:
        page: The page number (1-indexed)
        limit: The number of items per page
        
    Returns:
        A dictionary containing pagination parameters
    """
    debug_log.debug("budget_api", f"Pagination params: page={page}, limit={limit}")
    return {
        "page": page,
        "limit": limit,
        "offset": (page - 1) * limit
    }

# Common Path Parameters

@log_function()
async def budget_id_param(
    budget_id: str = Path(..., description="Budget ID")
) -> str:
    """Validate and return the budget ID."""
    debug_log.debug("budget_api", f"Budget ID param: {budget_id}")
    return budget_id

@log_function()
async def policy_id_param(
    policy_id: str = Path(..., description="Policy ID")
) -> str:
    """Validate and return the policy ID."""
    debug_log.debug("budget_api", f"Policy ID param: {policy_id}")
    return policy_id

@log_function()
async def allocation_id_param(
    allocation_id: str = Path(..., description="Allocation ID")
) -> str:
    """Validate and return the allocation ID."""
    debug_log.debug("budget_api", f"Allocation ID param: {allocation_id}")
    return allocation_id

@log_function()
async def record_id_param(
    record_id: str = Path(..., description="Record ID")
) -> str:
    """Validate and return the record ID."""
    debug_log.debug("budget_api", f"Record ID param: {record_id}")
    return record_id

@log_function()
async def alert_id_param(
    alert_id: str = Path(..., description="Alert ID")
) -> str:
    """Validate and return the alert ID."""
    debug_log.debug("budget_api", f"Alert ID param: {alert_id}")
    return alert_id