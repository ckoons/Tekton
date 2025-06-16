"""
API models for Athena.

These models define the request and response data structures for the API.
"""

from .entity import (
    EntityCreate,
    EntityResponse,
    EntityUpdate,
    EntitySearchResult,
    EntityMergeRequest,
    EntityMergeResponse
)

from .query import (
    QueryRequest,
    QueryResponse
)

__all__ = [
    "EntityCreate",
    "EntityResponse",
    "EntityUpdate",
    "EntitySearchResult",
    "EntityMergeRequest",
    "EntityMergeResponse",
    "QueryRequest",
    "QueryResponse"
]