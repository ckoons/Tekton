"""
MCP Endpoints - Model Context Protocol API for Athena.

This module provides FastAPI endpoints for Athena's MCP implementation, 
allowing other components to interact with Athena's knowledge graph capabilities.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from pydantic import BaseModel, Field

# Import FastMCP integration
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        mcp_processor,
        MCPClient
    )
    from tekton.mcp.fastmcp.schema import (
        ToolSchema,
        ProcessorSchema,
        MessageSchema,
        ResponseSchema,
        MCPRequest,
        MCPResponse,
        MCPCapability,
        MCPTool
    )
    from tekton.mcp.fastmcp.adapters import adapt_tool, adapt_processor
    from tekton.mcp.fastmcp.exceptions import MCPProcessingError
    from tekton.mcp.fastmcp.utils.endpoints import (
        create_mcp_router,
        add_standard_mcp_endpoints
    )
    fastmcp_available = True
except ImportError:
    fastmcp_available = False

# Get Athena engine and dependencies
from athena.api.dependencies import get_knowledge_engine
from athena.core.engine import KnowledgeEngine
from athena.core.entity_manager import EntityManager
from athena.core.query_engine import QueryEngine

# Import Athena MCP tools
from athena.core.mcp import (
    get_all_tools,
    get_all_capabilities
)

logger = logging.getLogger(__name__)

# Create router
mcp_router = create_mcp_router(
    prefix="/mcp",
    tags=["mcp"]
)

# Legacy Pydantic models for backward compatibility
class AthenaMCPRequest(BaseModel):
    """Request model for Athena MCP API."""
    content: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    
class AthenaMCPResponse(BaseModel):
    """Response model for Athena MCP API."""
    content: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Legacy MCP endpoint for backward compatibility
@mcp_router.post("/process", response_model=AthenaMCPResponse)
async def process_message(
    request: AthenaMCPRequest,
    knowledge_engine: KnowledgeEngine = Depends(get_knowledge_engine)
) -> AthenaMCPResponse:
    """
    Process an MCP request through Athena.
    
    This endpoint accepts MCP requests and processes them using Athena's knowledge graph capabilities.
    """
    try:
        # Initialize the entity manager and query engine
        entity_manager = EntityManager(knowledge_engine)
        query_engine = QueryEngine(knowledge_engine)
        
        # Simple request processing based on content type
        content_type = request.content.get("type", "unknown")
        content = request.content.get("content", {})
        context = request.context or {}
        
        result = {}
        
        if content_type == "entity_search":
            # Process entity search request
            query = content.get("query", "")
            entity_type = content.get("entity_type")
            limit = content.get("limit", 10)
            
            entities = await knowledge_engine.search_entities(
                query, 
                entity_type=entity_type,
                limit=limit
            )
            
            result = {
                "entities": [entity.dict() for entity in entities],
                "count": len(entities)
            }
            
        elif content_type == "knowledge_query":
            # Process knowledge query request
            question = content.get("question", "")
            mode = content.get("mode", "hybrid")
            
            from tekton.core.query.modes import QueryMode, QueryParameters
            
            # Map mode string to QueryMode enum
            mode_map = {
                "naive": QueryMode.NAIVE,
                "local": QueryMode.LOCAL,
                "global": QueryMode.GLOBAL,
                "hybrid": QueryMode.HYBRID,
                "mix": QueryMode.MIX
            }
            
            query_mode = mode_map.get(mode.lower(), QueryMode.HYBRID)
            
            parameters = QueryParameters(
                mode=query_mode,
                max_results=content.get("max_results", 10),
                max_entities=content.get("max_entities", 5),
                relationship_depth=content.get("relationship_depth", 3)
            )
            
            query_result = await query_engine.query(question, parameters)
            result = query_result
            
        else:
            # Return error for unknown content type
            result = {
                "error": f"Unknown content type: {content_type}"
            }
        
        # Create response
        return AthenaMCPResponse(
            content=result,
            context=context,
            metadata={
                "processed_by": "athena.mcp",
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing MCP request: {e}")

# FastMCP endpoints - these functions will be called by add_standard_mcp_endpoints

async def get_capabilities_func(engine: KnowledgeEngine):
    """Get Athena MCP capabilities."""
    return get_all_capabilities(engine)

async def get_tools_func(engine: KnowledgeEngine):
    """Get Athena MCP tools."""
    return get_all_tools(engine)

async def process_request_func(engine: KnowledgeEngine, request: MCPRequest):
    """Process an MCP request."""
    # Make sure the engine is initialized
    if not engine.is_initialized:
        await engine.initialize()
    
    # Create necessary components
    entity_manager = EntityManager(engine)
    query_engine = QueryEngine(engine)
    
    try:
        # Check if tool is supported
        tool_name = request.tool
        
        # Define a mapping of tool names to handler functions
        tool_handlers = {
            # Entity Management Tools
            "SearchEntities": entity_search_handler,
            "GetEntityById": get_entity_handler,
            "GetEntityRelationships": get_relationships_handler,
            "FindEntityPaths": find_paths_handler,
            "MergeEntities": merge_entities_handler,
            
            # Query Tools
            "QueryKnowledgeGraph": query_handler,
            "NaiveQuery": naive_query_handler,
            "LocalQuery": local_query_handler,
            "GlobalQuery": global_query_handler,
            "HybridQuery": hybrid_query_handler
        }
        
        # Check if tool is supported
        if tool_name not in tool_handlers:
            return MCPResponse(
                status="error",
                error=f"Unsupported tool: {tool_name}",
                result=None
            )
            
        # Call the appropriate handler
        handler = tool_handlers[tool_name]
        result = await handler(engine, entity_manager, query_engine, request)
        
        return MCPResponse(
            status="success",
            result=result,
            error=None
        )
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}")
        return MCPResponse(
            status="error",
            error=f"Error processing request: {str(e)}",
            result=None
        )

# Define handler functions for each tool

async def entity_search_handler(engine, entity_manager, query_engine, request):
    """Handle SearchEntities tool requests."""
    params = request.parameters
    
    # Extract parameters
    query = params.get("query", "")
    entity_type = params.get("entity_type")
    limit = params.get("limit", 10)
    min_confidence = params.get("min_confidence", 0.5)
    
    # Search for entities
    entities = await engine.search_entities(
        query, 
        entity_type=entity_type,
        limit=limit,
        min_confidence=min_confidence
    )
    
    # Format results
    results = []
    for entity in entities:
        results.append({
            "id": entity.entity_id,
            "name": entity.name,
            "type": entity.entity_type,
            "confidence": entity.confidence,
            "properties": entity.properties,
            "aliases": entity.aliases
        })
        
    return {
        "query": query,
        "entity_type": entity_type,
        "count": len(results),
        "entities": results
    }

async def get_entity_handler(engine, entity_manager, query_engine, request):
    """Handle GetEntityById tool requests."""
    params = request.parameters
    
    # Extract parameters
    entity_id = params.get("entity_id", "")
    
    # Get entity
    entity = await engine.get_entity(entity_id)
    
    if not entity:
        return {
            "error": f"Entity with ID '{entity_id}' not found"
        }
        
    # Format result
    return {
        "id": entity.entity_id,
        "name": entity.name,
        "type": entity.entity_type,
        "confidence": entity.confidence,
        "properties": entity.properties,
        "aliases": entity.aliases,
        "source": entity.source
    }

async def get_relationships_handler(engine, entity_manager, query_engine, request):
    """Handle GetEntityRelationships tool requests."""
    params = request.parameters
    
    # Extract parameters
    entity_id = params.get("entity_id", "")
    direction = params.get("direction", "both")
    relationship_type = params.get("relationship_type")
    limit = params.get("limit", 10)
    
    # Get entity relationships
    relationships = await engine.get_entity_relationships(
        entity_id, 
        direction=direction,
        relationship_type=relationship_type,
        limit=limit
    )
    
    # Format results
    results = []
    for rel, connected_entity in relationships:
        results.append({
            "relationship_id": rel.relationship_id,
            "relationship_type": rel.relationship_type,
            "source_id": rel.source_id,
            "target_id": rel.target_id,
            "properties": rel.properties,
            "confidence": rel.confidence,
            "connected_entity": {
                "id": connected_entity.entity_id,
                "name": connected_entity.name,
                "type": connected_entity.entity_type
            }
        })
        
    return {
        "entity_id": entity_id,
        "direction": direction,
        "relationship_type": relationship_type,
        "count": len(results),
        "relationships": results
    }

async def find_paths_handler(engine, entity_manager, query_engine, request):
    """Handle FindEntityPaths tool requests."""
    params = request.parameters
    
    # Extract parameters
    source_id = params.get("source_id", "")
    target_id = params.get("target_id", "")
    max_depth = params.get("max_depth", 3)
    relationship_types = params.get("relationship_types")
    
    # Find paths
    paths = await engine.find_paths(
        source_id, 
        target_id,
        max_depth=max_depth,
        relationship_types=relationship_types
    )
    
    # Format results
    formatted_paths = []
    for path in paths:
        formatted_path = []
        
        for i, item in enumerate(path):
            if i % 2 == 0:  # Entity
                entity = item
                formatted_path.append({
                    "type": "entity",
                    "id": entity.entity_id,
                    "name": entity.name,
                    "entity_type": entity.entity_type
                })
            else:  # Relationship
                relationship = item
                formatted_path.append({
                    "type": "relationship",
                    "id": relationship.relationship_id,
                    "relationship_type": relationship.relationship_type,
                    "source_id": relationship.source_id,
                    "target_id": relationship.target_id
                })
                
        formatted_paths.append(formatted_path)
        
    return {
        "source_id": source_id,
        "target_id": target_id,
        "max_depth": max_depth,
        "relationship_types": relationship_types,
        "count": len(formatted_paths),
        "paths": formatted_paths
    }

async def merge_entities_handler(engine, entity_manager, query_engine, request):
    """Handle MergeEntities tool requests."""
    params = request.parameters
    
    # Extract parameters
    source_entities = params.get("source_entities", [])
    target_entity_name = params.get("target_entity_name", "")
    target_entity_type = params.get("target_entity_type")
    merge_strategies = params.get("merge_strategies")
    
    # Merge entities
    merged_entity = await entity_manager.merge_entities(
        source_entities=source_entities,
        target_entity_name=target_entity_name,
        target_entity_type=target_entity_type,
        merge_strategies=merge_strategies
    )
    
    if not merged_entity:
        return {
            "error": "Failed to merge entities",
            "success": False
        }
        
    # Format result
    return {
        "source_entities": source_entities,
        "target_entity": {
            "id": merged_entity.entity_id,
            "name": merged_entity.name,
            "type": merged_entity.entity_type,
            "confidence": merged_entity.confidence,
            "properties": merged_entity.properties,
            "aliases": merged_entity.aliases
        },
        "success": True
    }

async def query_handler(engine, entity_manager, query_engine, request):
    """Handle QueryKnowledgeGraph tool requests."""
    params = request.parameters
    
    # Extract parameters
    question = params.get("question", "")
    mode = params.get("mode", "hybrid")
    max_results = params.get("max_results", 10)
    max_entities = params.get("max_entities", 5)
    relationship_depth = params.get("relationship_depth", 3)
    
    # Create query parameters
    from tekton.core.query.modes import QueryMode, QueryParameters
    
    # Map mode string to QueryMode enum
    mode_map = {
        "naive": QueryMode.NAIVE,
        "local": QueryMode.LOCAL,
        "global": QueryMode.GLOBAL,
        "hybrid": QueryMode.HYBRID,
        "mix": QueryMode.MIX
    }
    
    query_mode = mode_map.get(mode.lower(), QueryMode.HYBRID)
    
    parameters = QueryParameters(
        mode=query_mode,
        max_results=max_results,
        max_entities=max_entities,
        relationship_depth=relationship_depth
    )
    
    # Execute query
    results = await query_engine.query(question, parameters)
    
    return {
        "question": question,
        "mode": mode,
        "results": results,
        "context_text": results.get("context_text", ""),
        "results_count": results.get("results_count", 0)
    }

async def naive_query_handler(engine, entity_manager, query_engine, request):
    """Handle NaiveQuery tool requests."""
    params = request.parameters
    
    # Extract parameters
    question = params.get("question", "")
    max_results = params.get("max_results", 10)
    
    # Forward to query_handler with mode=naive
    modified_request = MCPRequest(
        client_id=request.client_id,
        tool="QueryKnowledgeGraph",
        parameters={
            "question": question,
            "mode": "naive",
            "max_results": max_results
        }
    )
    
    return await query_handler(engine, entity_manager, query_engine, modified_request)

async def local_query_handler(engine, entity_manager, query_engine, request):
    """Handle LocalQuery tool requests."""
    params = request.parameters
    
    # Extract parameters
    question = params.get("question", "")
    max_results = params.get("max_results", 10)
    max_entities = params.get("max_entities", 5)
    
    # Forward to query_handler with mode=local
    modified_request = MCPRequest(
        client_id=request.client_id,
        tool="QueryKnowledgeGraph",
        parameters={
            "question": question,
            "mode": "local",
            "max_results": max_results,
            "max_entities": max_entities
        }
    )
    
    return await query_handler(engine, entity_manager, query_engine, modified_request)

async def global_query_handler(engine, entity_manager, query_engine, request):
    """Handle GlobalQuery tool requests."""
    params = request.parameters
    
    # Extract parameters
    question = params.get("question", "")
    max_results = params.get("max_results", 10)
    max_entities = params.get("max_entities", 5)
    relationship_depth = params.get("relationship_depth", 3)
    
    # Forward to query_handler with mode=global
    modified_request = MCPRequest(
        client_id=request.client_id,
        tool="QueryKnowledgeGraph",
        parameters={
            "question": question,
            "mode": "global",
            "max_results": max_results,
            "max_entities": max_entities,
            "relationship_depth": relationship_depth
        }
    )
    
    return await query_handler(engine, entity_manager, query_engine, modified_request)

async def hybrid_query_handler(engine, entity_manager, query_engine, request):
    """Handle HybridQuery tool requests."""
    params = request.parameters
    
    # Extract parameters
    question = params.get("question", "")
    max_results = params.get("max_results", 10)
    max_entities = params.get("max_entities", 5)
    relationship_depth = params.get("relationship_depth", 3)
    
    # Forward to query_handler with mode=hybrid
    modified_request = MCPRequest(
        client_id=request.client_id,
        tool="QueryKnowledgeGraph",
        parameters={
            "question": question,
            "mode": "hybrid",
            "max_results": max_results,
            "max_entities": max_entities,
            "relationship_depth": relationship_depth
        }
    )
    
    return await query_handler(engine, entity_manager, query_engine, modified_request)

# Add standard MCP endpoints if FastMCP is available
if fastmcp_available:
    try:
        # Add standard MCP endpoints to the router
        add_standard_mcp_endpoints(
            router=mcp_router,
            get_capabilities_func=get_capabilities_func,
            get_tools_func=get_tools_func,
            process_request_func=process_request_func,
            component_manager_dependency=get_knowledge_engine
        )
        
        logger.info("Added FastMCP endpoints to Athena API")
    except Exception as e:
        logger.error(f"Error adding FastMCP endpoints: {e}")