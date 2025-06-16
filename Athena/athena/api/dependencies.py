"""
API Dependencies - Dependency injection for FastAPI routes

This module provides functions for dependency injection in FastAPI routes.
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends

from athena.core.engine import KnowledgeEngine
from athena.core.entity_manager import EntityManager
from athena.core.query_engine import QueryEngine

# Global knowledge engine instance
knowledge_engine = None


# Helper to get client ID from request
async def get_client_id(x_client_id: Optional[str] = Header(None)) -> str:
    """Get client ID from header or use default."""
    return x_client_id or "default"


# Helper to get knowledge engine
async def get_knowledge_engine() -> KnowledgeEngine:
    """Get knowledge engine instance."""
    if knowledge_engine is None:
        raise HTTPException(status_code=500, detail="Knowledge engine not initialized")
    return knowledge_engine


# Helper to get entity manager
async def get_entity_manager() -> EntityManager:
    """Get entity manager from knowledge engine."""
    engine = await get_knowledge_engine()
    return engine.entity_manager


# Helper to get query engine
async def get_query_engine() -> QueryEngine:
    """Get query engine from knowledge engine."""
    engine = await get_knowledge_engine()
    return engine.query_engine