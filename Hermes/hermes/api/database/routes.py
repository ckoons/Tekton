"""
Database API Routes - REST API endpoints for Hermes Database Services.

This module defines the FastAPI routes for accessing database services,
providing a RESTful interface to the various database types.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import Dict, List, Any, Optional, Union
import logging

from hermes.core.database.manager import DatabaseManager
from hermes.core.database.database_types import DatabaseType, DatabaseBackend
from hermes.api.database.models import (
    VectorStoreRequest,
    VectorSearchRequest,
    VectorDeleteRequest,
    KeyValueSetRequest,
    KeyValueDeleteRequest,
    GraphAddNodeRequest,
    GraphAddRelationshipRequest,
    GraphQueryRequest,
    DocumentInsertRequest,
    DocumentFindRequest,
    DocumentUpdateRequest,
    CacheSetRequest,
    SqlExecuteRequest
)

# Configure logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/database", tags=["database"])

# Dependency for getting database manager
async def get_database_manager():
    """Get a database manager instance."""
    from hermes.api.app import app
    
    if not hasattr(app.state, "database_manager"):
        # Initialize database manager
        app.state.database_manager = DatabaseManager()
    
    return app.state.database_manager

# Vector database endpoints

@router.post("/vector/{namespace}/store", 
           summary="Store vectors in the database",
           description="Store vectors with optional metadata and IDs")
async def vector_store(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: VectorStoreRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Store vectors in the database."""
    try:
        # Get vector database adapter
        adapter = await db_manager.get_vector_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Store vectors
        result = await adapter.store(
            vectors=request.vectors,
            metadatas=request.metadatas,
            ids=request.ids
        )
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error storing vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vector/{namespace}/search", 
           summary="Search for similar vectors",
           description="Search for vectors similar to the query vector")
async def vector_search(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: VectorSearchRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Search for similar vectors."""
    try:
        # Get vector database adapter
        adapter = await db_manager.get_vector_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Search for similar vectors
        results = await adapter.search(
            query_vector=request.query_vector,
            top_k=request.top_k,
            filter=request.filter
        )
        
        return results
    except Exception as e:
        logger.error(f"Error searching vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vector/{namespace}/delete", 
             summary="Delete vectors",
             description="Delete vectors by their IDs")
async def vector_delete(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: VectorDeleteRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Delete vectors by ID."""
    try:
        # Get vector database adapter
        adapter = await db_manager.get_vector_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Delete vectors
        result = await adapter.delete(ids=request.ids)
        
        return {"success": result}
    except Exception as e:
        logger.error(f"Error deleting vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Key-value database endpoints

@router.put("/kv/{namespace}/{key}", 
          summary="Set a key-value pair",
          description="Store a value with the specified key")
async def kv_set(
    namespace: str = Path(..., description="Namespace for data isolation"),
    key: str = Path(..., description="Key to set"),
    request: KeyValueSetRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Set a key-value pair."""
    try:
        # Get key-value database adapter
        adapter = await db_manager.get_key_value_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Set key-value pair
        result = await adapter.set(
            key=key,
            value=request.value,
            ttl=request.ttl
        )
        
        return {"success": result}
    except Exception as e:
        logger.error(f"Error setting key-value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kv/{namespace}/{key}", 
          summary="Get a value by key",
          description="Retrieve the value associated with the specified key")
async def kv_get(
    namespace: str = Path(..., description="Namespace for data isolation"),
    key: str = Path(..., description="Key to get"),
    backend: Optional[str] = Query(None, description="Specific backend to use"),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Get a value by key."""
    try:
        # Get key-value database adapter
        adapter = await db_manager.get_key_value_db(
            namespace=namespace,
            backend=backend
        )
        
        # Get value
        value = await adapter.get(key=key)
        
        return {"value": value}
    except Exception as e:
        logger.error(f"Error getting key-value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/kv/{namespace}/{key}", 
             summary="Delete a key-value pair",
             description="Delete the key-value pair with the specified key")
async def kv_delete(
    namespace: str = Path(..., description="Namespace for data isolation"),
    key: str = Path(..., description="Key to delete"),
    request: KeyValueDeleteRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Delete a key-value pair."""
    try:
        # Get key-value database adapter
        adapter = await db_manager.get_key_value_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Delete key
        result = await adapter.delete(key=key)
        
        return {"success": result}
    except Exception as e:
        logger.error(f"Error deleting key-value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Graph database endpoints

@router.post("/graph/{namespace}/node", 
           summary="Add a node to the graph",
           description="Create a new node with the specified labels and properties")
async def graph_add_node(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: GraphAddNodeRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Add a node to the graph."""
    try:
        # Get graph database adapter
        adapter = await db_manager.get_graph_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Add node
        result = await adapter.add_node(
            node_id=request.node_id,
            labels=request.labels,
            properties=request.properties
        )
        
        return {"success": result, "node_id": request.node_id}
    except Exception as e:
        logger.error(f"Error adding node: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/graph/{namespace}/relationship", 
           summary="Add a relationship between nodes",
           description="Create a new relationship between two nodes")
async def graph_add_relationship(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: GraphAddRelationshipRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Add a relationship between nodes."""
    try:
        # Get graph database adapter
        adapter = await db_manager.get_graph_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Add relationship
        result = await adapter.add_relationship(
            source_id=request.source_id,
            target_id=request.target_id,
            rel_type=request.type,
            properties=request.properties
        )
        
        return {"success": result}
    except Exception as e:
        logger.error(f"Error adding relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/graph/{namespace}/query", 
           summary="Execute a graph query",
           description="Run a query on the graph database (e.g., Cypher for Neo4j)")
async def graph_query(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: GraphQueryRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Execute a graph query."""
    try:
        # Get graph database adapter
        adapter = await db_manager.get_graph_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Execute query
        results = await adapter.query(
            query=request.query,
            parameters=request.parameters
        )
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Error executing graph query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Document database endpoints

@router.post("/document/{namespace}/{collection}", 
           summary="Insert a document",
           description="Insert a new document into the specified collection")
async def document_insert(
    namespace: str = Path(..., description="Namespace for data isolation"),
    collection: str = Path(..., description="Collection to insert into"),
    request: DocumentInsertRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Insert a document."""
    try:
        # Get document database adapter
        adapter = await db_manager.get_document_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Insert document
        doc_id = await adapter.insert(
            collection=collection,
            document=request.document
        )
        
        return {"success": bool(doc_id), "document_id": doc_id}
    except Exception as e:
        logger.error(f"Error inserting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document/{namespace}/{collection}/find", 
           summary="Find documents",
           description="Find documents matching the specified query")
async def document_find(
    namespace: str = Path(..., description="Namespace for data isolation"),
    collection: str = Path(..., description="Collection to search in"),
    request: DocumentFindRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Find documents matching a query."""
    try:
        # Get document database adapter
        adapter = await db_manager.get_document_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Find documents
        documents = await adapter.find(
            collection=collection,
            query=request.query,
            limit=request.limit
        )
        
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error finding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/document/{namespace}/{collection}", 
          summary="Update documents",
          description="Update documents matching the specified query")
async def document_update(
    namespace: str = Path(..., description="Namespace for data isolation"),
    collection: str = Path(..., description="Collection to update in"),
    request: DocumentUpdateRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Update documents matching a query."""
    try:
        # Get document database adapter
        adapter = await db_manager.get_document_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Update documents
        result = await adapter.update(
            collection=collection,
            query=request.query,
            update=request.update
        )
        
        return {"success": result.get("success", False), "count": result.get("count", 0)}
    except Exception as e:
        logger.error(f"Error updating documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cache database endpoints

@router.put("/cache/{namespace}/{key}", 
          summary="Set a cache value",
          description="Store a value in the cache with the specified key")
async def cache_set(
    namespace: str = Path(..., description="Namespace for data isolation"),
    key: str = Path(..., description="Key to set"),
    request: CacheSetRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Set a cache value."""
    try:
        # Get cache database adapter
        adapter = await db_manager.get_cache_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Set cache value
        result = await adapter.set(
            key=key,
            value=request.value,
            ttl=request.ttl
        )
        
        return {"success": result}
    except Exception as e:
        logger.error(f"Error setting cache value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/{namespace}/{key}", 
          summary="Get a cache value",
          description="Retrieve a value from the cache by key")
async def cache_get(
    namespace: str = Path(..., description="Namespace for data isolation"),
    key: str = Path(..., description="Key to get"),
    backend: Optional[str] = Query(None, description="Specific backend to use"),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Get a cache value."""
    try:
        # Get cache database adapter
        adapter = await db_manager.get_cache_db(
            namespace=namespace,
            backend=backend
        )
        
        # Get cache value
        value = await adapter.get(key=key)
        
        return {"value": value}
    except Exception as e:
        logger.error(f"Error getting cache value: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Relational database endpoints

@router.post("/relation/{namespace}/query", 
           summary="Execute SQL query",
           description="Run an SQL query on the relational database")
async def sql_execute(
    namespace: str = Path(..., description="Namespace for data isolation"),
    request: SqlExecuteRequest = Body(...),
    db_manager: DatabaseManager = Depends(get_database_manager)
):
    """Execute an SQL query."""
    try:
        # Get relational database adapter
        adapter = await db_manager.get_relational_db(
            namespace=namespace,
            backend=request.backend
        )
        
        # Execute query
        results = await adapter.execute(
            query=request.query,
            parameters=request.parameters
        )
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise HTTPException(status_code=500, detail=str(e))