"""
Athena Query Engine

Enhanced query engine for Athena that implements various retrieval modes
inspired by LightRAG's multi-modal query capabilities.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Set, Tuple

# Import FastMCP integration if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    from tekton.mcp.fastmcp.utils.tooling import ToolRegistry
    fastmcp_available = True
except ImportError:
    fastmcp_available = False

from tekton.core.query.modes import QueryMode, QueryParameters

from .engine import KnowledgeEngine
from .entity import Entity
from .relationship import Relationship

# Import MCP tools for registration
from .mcp import register_query_tools

logger = logging.getLogger("athena.query_engine")

class QueryEngine:
    """
    Enhanced query engine for Athena knowledge graph.
    
    Provides multiple retrieval strategies inspired by LightRAG:
    - Naive: Simple keyword-based search
    - Local: Entity-focused retrieval
    - Global: Relationship-focused retrieval
    - Hybrid: Combined entity and relationship retrieval
    - Mix: Integrated graph and vector retrieval
    """
    
    def __init__(self, engine: KnowledgeEngine):
        """
        Initialize the query engine.
        
        Args:
            engine: Reference to the knowledge engine
        """
        self.engine = engine
        self.tool_registry = None
        
        # Initialize FastMCP tool registry if available
        if fastmcp_available:
            self.tool_registry = ToolRegistry(component_name="athena")
            
    async def initialize_mcp(self) -> None:
        """Initialize MCP integration for the query engine."""
        if fastmcp_available and self.tool_registry:
            try:
                # Register query tools
                await register_query_tools(self, self.tool_registry)
                logger.info("Registered MCP query tools")
            except Exception as e:
                logger.error(f"Error registering MCP query tools: {e}")
        
    async def query(self, question: str, parameters: QueryParameters = None) -> Dict[str, Any]:
        """
        Execute a query using the specified retrieval mode.
        
        Args:
            question: The query to execute
            parameters: Query parameters including mode, limits, etc.
            
        Returns:
            Results dictionary with retrieved context and/or generated response
        """
        if parameters is None:
            parameters = QueryParameters()
            
        if not self.engine.is_initialized:
            await self.engine.initialize()
            
        # Select query strategy based on mode
        if parameters.mode == QueryMode.NAIVE:
            return await self._naive_query(question, parameters)
        elif parameters.mode == QueryMode.LOCAL:
            return await self._local_query(question, parameters)
        elif parameters.mode == QueryMode.GLOBAL:
            return await self._global_query(question, parameters)
        elif parameters.mode == QueryMode.HYBRID:
            return await self._hybrid_query(question, parameters)
        elif parameters.mode == QueryMode.MIX:
            return await self._mix_query(question, parameters)
        else:
            raise ValueError(f"Unsupported query mode: {parameters.mode}")
    
    async def _naive_query(self, question: str, parameters: QueryParameters) -> Dict[str, Any]:
        """
        Simple keyword-based search without advanced knowledge graph integration.
        
        This mode performs basic keyword matching against entity names and descriptions,
        without considering relationships or graph structure.
        
        Args:
            question: The query text
            parameters: Query parameters
            
        Returns:
            Results dictionary
        """
        # Extract keywords from question (simple implementation)
        keywords = [word.lower() for word in question.split() if len(word) > 3]
        
        # Find entities matching keywords
        matching_entities = []
        
        # Search for each keyword
        for keyword in keywords:
            entities = await self.engine.search_entities(
                keyword, 
                limit=parameters.max_entities
            )
            matching_entities.extend(entities)
            
        # Deduplicate
        unique_entities = {}
        for entity in matching_entities:
            if entity.entity_id not in unique_entities:
                unique_entities[entity.entity_id] = entity
                
        # Format the results
        context_items = []
        for entity_id, entity in unique_entities.items():
            context_items.append({
                "id": entity_id,
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.get_property("description") or "",
                "source": entity.source
            })
            
        # Sort by relevance (simple implementation)
        context_items.sort(key=lambda x: len(x["description"]), reverse=True)
        
        # Limit to max results
        context_items = context_items[:parameters.max_results]
        
        # Format the response
        return {
            "query": question,
            "mode": "naive",
            "context": context_items,
            "context_text": "\n\n".join([f"{item['name']}: {item['description']}" for item in context_items]),
            "results_count": len(context_items)
        }
    
    async def _local_query(self, question: str, parameters: QueryParameters) -> Dict[str, Any]:
        """
        Entity-focused retrieval that prioritizes relevant entities.
        
        This mode focuses on finding the most relevant entities and their direct properties,
        without extensively exploring relationships between entities.
        
        Args:
            question: The query text
            parameters: Query parameters
            
        Returns:
            Results dictionary
        """
        # Start by finding relevant entities
        entities = await self.engine.search_entities(
            question, 
            limit=parameters.max_entities
        )
        
        # Get properties and direct relationships for these entities
        context_items = []
        entity_relationships = {}
        
        for entity in entities:
            # Get direct relationships
            relationships = await self.engine.get_entity_relationships(
                entity.entity_id,
                direction="both"
            )
            
            # Store relationship data
            entity_relationships[entity.entity_id] = [
                {
                    "relationship_id": rel.relationship_id,
                    "relationship_type": rel.relationship_type,
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "properties": rel.properties,
                    "connected_entity": {
                        "entity_id": connected.entity_id,
                        "name": connected.name,
                        "entity_type": connected.entity_type
                    }
                }
                for rel, connected in relationships[:10]  # Limit relationships per entity
            ]
            
            # Add entity data
            context_items.append({
                "id": entity.entity_id,
                "name": entity.name,
                "type": entity.entity_type,
                "properties": entity.properties,
                "confidence": entity.confidence,
                "relationship_count": len(relationships)
            })
            
        # Rank entities by relevance (basic implementation)
        # Consider factors like number of relationships, property richness, etc.
        context_items.sort(key=lambda x: (x["confidence"], x["relationship_count"]), reverse=True)
        
        # Limit to max results
        context_items = context_items[:parameters.max_results]
        
        # Format context text for model consumption
        context_text = ""
        for item in context_items:
            context_text += f"--- Entity: {item['name']} (Type: {item['type']}) ---\n"
            
            # Add properties
            for prop_name, prop_data in item.get("properties", {}).items():
                if isinstance(prop_data, dict) and "value" in prop_data:
                    prop_value = prop_data["value"]
                    context_text += f"{prop_name}: {prop_value}\n"
                else:
                    context_text += f"{prop_name}: {prop_data}\n"
                    
            # Add key relationships
            if item["id"] in entity_relationships:
                relationship_text = []
                for rel in entity_relationships[item["id"]][:5]:  # Limit to 5 relationships per entity
                    connected_name = rel["connected_entity"]["name"]
                    rel_type = rel["relationship_type"]
                    
                    if rel["source_id"] == item["id"]:
                        relationship_text.append(f"- {rel_type} -> {connected_name}")
                    else:
                        relationship_text.append(f"- {connected_name} -> {rel_type} -> This Entity")
                        
                if relationship_text:
                    context_text += "Relationships:\n" + "\n".join(relationship_text) + "\n"
                    
            context_text += "\n"
            
        return {
            "query": question,
            "mode": "local",
            "context": context_items,
            "context_text": context_text,
            "relationships": entity_relationships,
            "results_count": len(context_items)
        }
        
    async def _global_query(self, question: str, parameters: QueryParameters) -> Dict[str, Any]:
        """
        Relationship-focused retrieval for understanding connections.
        
        This mode prioritizes relationship paths and network structure
        over individual entity attributes.
        
        Args:
            question: The query text
            parameters: Query parameters
            
        Returns:
            Results dictionary
        """
        # First, find entry point entities
        entry_entities = await self.engine.search_entities(
            question, 
            limit=min(5, parameters.max_entities)  # Limit entry points
        )
        
        if not entry_entities:
            return {
                "query": question,
                "mode": "global",
                "context": [],
                "context_text": "No relevant entities found.",
                "results_count": 0
            }
            
        # Collect paths between entities
        paths = []
        
        # For each pair of entities, find paths
        for i in range(len(entry_entities)):
            for j in range(i+1, len(entry_entities)):
                source = entry_entities[i]
                target = entry_entities[j]
                
                # Find paths between these entities
                entity_paths = await self.engine.find_paths(
                    source.entity_id,
                    target.entity_id,
                    max_depth=parameters.relationship_depth
                )
                
                if entity_paths:
                    paths.extend(entity_paths)
                    
        # If we found no paths, try extending from each entry entity individually
        if not paths:
            for entity in entry_entities:
                # Get direct relationships for this entity
                relationships = await self.engine.get_entity_relationships(
                    entity.entity_id,
                    direction="both"
                )
                
                # Convert to path format
                for relationship, connected_entity in relationships[:parameters.max_relationships // len(entry_entities)]:
                    # Create a simple path with just one relationship
                    if relationship.source_id == entity.entity_id:
                        path = [entity, relationship, connected_entity]
                    else:
                        path = [connected_entity, relationship, entity]
                        
                    paths.append(path)
                    
        # Process paths to extract unique entities and relationships
        unique_entities = {}
        unique_relationships = {}
        
        for path in paths:
            # Extract entities and relationships from the path
            for i, item in enumerate(path):
                if i % 2 == 0:  # Entity
                    entity = item
                    unique_entities[entity.entity_id] = entity
                else:  # Relationship
                    relationship = item
                    unique_relationships[relationship.relationship_id] = relationship
                    
        # Format entities and relationships
        formatted_entities = {
            entity_id: {
                "id": entity_id,
                "name": entity.name,
                "type": entity.entity_type,
                "properties": entity.properties
            }
            for entity_id, entity in unique_entities.items()
        }
        
        formatted_relationships = {
            rel_id: {
                "id": rel_id,
                "type": rel.relationship_type,
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "properties": rel.properties
            }
            for rel_id, rel in unique_relationships.items()
        }
        
        # Format paths for output
        formatted_paths = []
        
        for path in paths[:parameters.max_results]:
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
                        "relationship_type": relationship.relationship_type
                    })
                    
            formatted_paths.append(formatted_path)
            
        # Format context text for model consumption
        context_text = "Global Knowledge Graph Relationships:\n\n"
        
        for i, path in enumerate(formatted_paths):
            path_text = "Path " + str(i+1) + ": "
            
            for j, node in enumerate(path):
                if node["type"] == "entity":
                    path_text += node["name"]
                else:  # relationship
                    path_text += f" --[{node['relationship_type']}]--> "
                    
            context_text += path_text + "\n\n"
            
            # Add more detailed info about the entities in this path
            for node in path:
                if node["type"] == "entity":
                    entity_id = node["id"]
                    entity = unique_entities.get(entity_id)
                    
                    if entity:
                        context_text += f"Entity: {entity.name}\n"
                        context_text += f"Type: {entity.entity_type}\n"
                        
                        # Add key properties
                        for prop_name, prop_data in entity.properties.items():
                            if isinstance(prop_data, dict) and "value" in prop_data:
                                prop_value = prop_data["value"]
                                context_text += f"- {prop_name}: {prop_value}\n"
                            else:
                                context_text += f"- {prop_name}: {prop_data}\n"
                                
                        context_text += "\n"
                
            context_text += "---\n\n"
            
        return {
            "query": question,
            "mode": "global",
            "entities": formatted_entities,
            "relationships": formatted_relationships,
            "paths": formatted_paths,
            "context_text": context_text,
            "results_count": len(formatted_paths)
        }
        
    async def _hybrid_query(self, question: str, parameters: QueryParameters) -> Dict[str, Any]:
        """
        Combined entity and relationship retrieval.
        
        This mode balances both LOCAL and GLOBAL approaches, giving a more
        comprehensive view of the knowledge graph.
        
        Args:
            question: The query text
            parameters: Query parameters
            
        Returns:
            Results dictionary
        """
        # Run both local and global queries in parallel
        local_params = QueryParameters(
            mode=QueryMode.LOCAL,
            max_entities=parameters.max_entities // 2,
            max_results=parameters.max_results // 2
        )
        
        global_params = QueryParameters(
            mode=QueryMode.GLOBAL,
            max_entities=parameters.max_entities // 2,
            relationship_depth=parameters.relationship_depth,
            max_results=parameters.max_results // 2
        )
        
        # Execute both queries in parallel
        local_results, global_results = await asyncio.gather(
            self._local_query(question, local_params),
            self._global_query(question, global_params)
        )
        
        # Combine the context texts
        context_text = "--- Entity Information ---\n\n"
        context_text += local_results.get("context_text", "")
        context_text += "\n\n--- Relationship Paths ---\n\n"
        context_text += global_results.get("context_text", "")
        
        # Combine the results
        return {
            "query": question,
            "mode": "hybrid",
            "local_results": local_results,
            "global_results": global_results,
            "context_text": context_text,
            "results_count": (
                local_results.get("results_count", 0) + 
                global_results.get("results_count", 0)
            )
        }
        
    async def _mix_query(self, question: str, parameters: QueryParameters) -> Dict[str, Any]:
        """
        Integrated graph and vector retrieval (most advanced mode).
        
        This mode combines graph traversal with vector similarity search
        for a comprehensive retrieval strategy.
        
        Args:
            question: The query text
            parameters: Query parameters
            
        Returns:
            Results dictionary
        """
        # Use the hybrid approach for graph-based retrieval
        hybrid_results = await self._hybrid_query(question, parameters)
        
        # Integrate vector search if available
        try:
            from tekton.core.vector_store import get_vector_store
            
            # Get vector store
            vector_store = None
            
            # Placeholder for vector store initialization
            # In a full implementation, you would:
            # 1. Get an embedding for the question
            # 2. Search the vector store for similar items
            # 3. Integrate those results with the graph search results
            
            # Since we don't have the implementation yet, just return the hybrid results
            hybrid_results["mode"] = "mix"
            return hybrid_results
            
        except ImportError:
            # If vector search isn't available, fall back to hybrid results
            logger.warning("Vector search not available, falling back to hybrid mode")
            hybrid_results["mode"] = "mix (fallback to hybrid)"
            return hybrid_results