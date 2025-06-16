"""
Registration Types - Type definitions for the Unified Registration Protocol.

This module provides type definitions and common structures used in
the Unified Registration Protocol implementation.
"""

from typing import Dict, List, Any, Optional, Callable, TypedDict, Union

# Registration Data Types
class TokenData(TypedDict):
    """Type definition for token data."""
    component_id: str
    token_id: str
    iat: int       # Issued at timestamp
    exp: int       # Expiration timestamp

class TokenPayload(TypedDict):
    """Type definition for complete token structure."""
    payload: TokenData
    signature: str

class ComponentData(TypedDict):
    """Type definition for component registration data."""
    component_id: str
    name: str
    version: str
    type: str
    endpoint: str
    capabilities: List[str]
    metadata: Dict[str, Any]

class HeartbeatData(TypedDict):
    """Type definition for heartbeat data."""
    component_id: str
    token: str
    timestamp: float
    status: Dict[str, Any]

class RegistrationResponse(TypedDict):
    """Type definition for registration response data."""
    success: bool
    token: Optional[str]
    error: Optional[str]