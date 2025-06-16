"""
MCP Handlers - Request handlers for the database MCP adapter.

This module contains the request handlers for different database types,
processing requests from the MCP adapter.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from hermes.core.database.manager import DatabaseManager
from hermes.core.database.database_types import DatabaseType, DatabaseBackend

# Configure logger
logger = logging.getLogger("hermes.database.mcp_handlers")


async def handle_vector_request(
    database_manager: DatabaseManager,
    capability: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle vector database requests.
    
    Args:
        database_manager: Database manager instance
        capability: Capability name
        parameters: Request parameters
        
    Returns:
        Response dictionary
    """
    # Extract common parameters
    namespace = parameters.get("namespace", "default")
    backend = parameters.get("backend")
    
    # Get vector database adapter
    adapter = await database_manager.get_vector_db(
        namespace=namespace,
        backend=backend
    )
    
    # Handle specific vector operations
    if capability == "vector_store":
        vectors = parameters.get("vectors")
        metadatas = parameters.get("metadatas")
        ids = parameters.get("ids")
        
        if not vectors:
            return {"error": "Missing required parameter: vectors"}
        
        result = await adapter.store(
            vectors=vectors,
            metadatas=metadatas,
            ids=ids
        )
        
        return {"success": True, "result": result}
        
    elif capability == "vector_search":
        query_vector = parameters.get("query_vector")
        top_k = parameters.get("top_k", 5)
        filter_dict = parameters.get("filter")
        
        if not query_vector:
            return {"error": "Missing required parameter: query_vector"}
        
        results = await adapter.search(
            query_vector=query_vector,
            top_k=top_k,
            filter=filter_dict
        )
        
        return results
        
    elif capability == "vector_delete":
        ids = parameters.get("ids")
        
        if not ids:
            return {"error": "Missing required parameter: ids"}
        
        result = await adapter.delete(ids=ids)
        
        return {"success": result}
        
    else:
        return {"error": f"Unknown vector capability: {capability}"}


async def handle_key_value_request(
    database_manager: DatabaseManager,
    capability: str, 
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle key-value database requests.
    
    Args:
        database_manager: Database manager instance
        capability: Capability name
        parameters: Request parameters
        
    Returns:
        Response dictionary
    """
    # Extract common parameters
    namespace = parameters.get("namespace", "default")
    backend = parameters.get("backend")
    
    # Get key-value database adapter
    adapter = await database_manager.get_key_value_db(
        namespace=namespace,
        backend=backend
    )
    
    # Handle specific key-value operations
    if capability == "kv_set":
        key = parameters.get("key")
        value = parameters.get("value")
        ttl = parameters.get("ttl")
        
        if not key:
            return {"error": "Missing required parameter: key"}
        if value is None:
            return {"error": "Missing required parameter: value"}
        
        result = await adapter.set(
            key=key,
            value=value,
            ttl=ttl
        )
        
        return {"success": result}
        
    elif capability == "kv_get":
        key = parameters.get("key")
        
        if not key:
            return {"error": "Missing required parameter: key"}
        
        value = await adapter.get(key=key)
        
        return {"value": value}
        
    elif capability == "kv_delete":
        key = parameters.get("key")
        
        if not key:
            return {"error": "Missing required parameter: key"}
        
        result = await adapter.delete(key=key)
        
        return {"success": result}
        
    else:
        return {"error": f"Unknown key-value capability: {capability}"}


async def handle_graph_request(
    database_manager: DatabaseManager,
    capability: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle graph database requests.
    
    Args:
        database_manager: Database manager instance
        capability: Capability name
        parameters: Request parameters
        
    Returns:
        Response dictionary
    """
    # Extract common parameters
    namespace = parameters.get("namespace", "default")
    backend = parameters.get("backend")
    
    # Get graph database adapter
    adapter = await database_manager.get_graph_db(
        namespace=namespace,
        backend=backend
    )
    
    # Handle specific graph operations
    if capability == "graph_add_node":
        node_id = parameters.get("node_id")
        labels = parameters.get("labels", [])
        properties = parameters.get("properties", {})
        
        if not node_id:
            return {"error": "Missing required parameter: node_id"}
        
        result = await adapter.add_node(
            node_id=node_id,
            labels=labels,
            properties=properties
        )
        
        return {"success": result, "node_id": node_id}
        
    elif capability == "graph_add_relationship":
        source_id = parameters.get("source_id")
        target_id = parameters.get("target_id")
        rel_type = parameters.get("type")
        properties = parameters.get("properties", {})
        
        if not source_id:
            return {"error": "Missing required parameter: source_id"}
        if not target_id:
            return {"error": "Missing required parameter: target_id"}
        if not rel_type:
            return {"error": "Missing required parameter: type"}
        
        result = await adapter.add_relationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            properties=properties
        )
        
        return {"success": result}
        
    elif capability == "graph_query":
        query = parameters.get("query")
        query_params = parameters.get("parameters", {})
        
        if not query:
            return {"error": "Missing required parameter: query"}
        
        results = await adapter.query(
            query=query,
            parameters=query_params
        )
        
        return {"results": results}
        
    else:
        return {"error": f"Unknown graph capability: {capability}"}


async def handle_document_request(
    database_manager: DatabaseManager,
    capability: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle document database requests.
    
    Args:
        database_manager: Database manager instance
        capability: Capability name
        parameters: Request parameters
        
    Returns:
        Response dictionary
    """
    # Extract common parameters
    namespace = parameters.get("namespace", "default")
    backend = parameters.get("backend")
    
    # Get document database adapter
    adapter = await database_manager.get_document_db(
        namespace=namespace,
        backend=backend
    )
    
    # Handle specific document operations
    if capability == "document_insert":
        collection = parameters.get("collection")
        document = parameters.get("document")
        
        if not collection:
            return {"error": "Missing required parameter: collection"}
        if not document:
            return {"error": "Missing required parameter: document"}
        
        doc_id = await adapter.insert(
            collection=collection,
            document=document
        )
        
        return {"success": bool(doc_id), "document_id": doc_id}
        
    elif capability == "document_find":
        collection = parameters.get("collection")
        query = parameters.get("query", {})
        limit = parameters.get("limit", 10)
        
        if not collection:
            return {"error": "Missing required parameter: collection"}
        
        documents = await adapter.find(
            collection=collection,
            query=query,
            limit=limit
        )
        
        return {"documents": documents}
        
    elif capability == "document_update":
        collection = parameters.get("collection")
        query = parameters.get("query", {})
        update = parameters.get("update")
        
        if not collection:
            return {"error": "Missing required parameter: collection"}
        if not update:
            return {"error": "Missing required parameter: update"}
        
        result = await adapter.update(
            collection=collection,
            query=query,
            update=update
        )
        
        return {"success": result.get("success", False), "count": result.get("count", 0)}
        
    else:
        return {"error": f"Unknown document capability: {capability}"}


async def handle_cache_request(
    database_manager: DatabaseManager,
    capability: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle cache database requests.
    
    Args:
        database_manager: Database manager instance
        capability: Capability name
        parameters: Request parameters
        
    Returns:
        Response dictionary
    """
    # Extract common parameters
    namespace = parameters.get("namespace", "default")
    backend = parameters.get("backend")
    
    # Get cache database adapter
    adapter = await database_manager.get_cache_db(
        namespace=namespace,
        backend=backend
    )
    
    # Handle specific cache operations
    if capability == "cache_set":
        key = parameters.get("key")
        value = parameters.get("value")
        ttl = parameters.get("ttl", 3600)
        
        if not key:
            return {"error": "Missing required parameter: key"}
        if value is None:
            return {"error": "Missing required parameter: value"}
        
        result = await adapter.set(
            key=key,
            value=value,
            ttl=ttl
        )
        
        return {"success": result}
        
    elif capability == "cache_get":
        key = parameters.get("key")
        
        if not key:
            return {"error": "Missing required parameter: key"}
        
        value = await adapter.get(key=key)
        
        return {"value": value}
        
    else:
        return {"error": f"Unknown cache capability: {capability}"}


async def handle_relational_request(
    database_manager: DatabaseManager,
    capability: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle relational database requests.
    
    Args:
        database_manager: Database manager instance
        capability: Capability name
        parameters: Request parameters
        
    Returns:
        Response dictionary
    """
    # Extract common parameters
    namespace = parameters.get("namespace", "default")
    backend = parameters.get("backend")
    
    # Get relational database adapter
    adapter = await database_manager.get_relational_db(
        namespace=namespace,
        backend=backend
    )
    
    # Handle specific relational operations
    if capability == "sql_execute":
        query = parameters.get("query")
        query_params = parameters.get("parameters", [])
        
        if not query:
            return {"error": "Missing required parameter: query"}
        
        results = await adapter.execute(
            query=query,
            parameters=query_params
        )
        
        return {"results": results}
        
    else:
        return {"error": f"Unknown relational capability: {capability}"}