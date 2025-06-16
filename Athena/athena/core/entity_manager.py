"""
Entity Manager Module for Athena

Provides advanced entity management capabilities including entity merging
and relationship management inspired by LightRAG.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Literal
from datetime import datetime

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

from .entity import Entity
from .relationship import Relationship
from .engine import KnowledgeEngine

# Import MCP tools for registration
from .mcp import register_entity_tools

logger = logging.getLogger("athena.entity_manager")

class EntityMergeStrategy:
    """Merge strategy constants for entity field merging."""
    KEEP_FIRST = "keep_first"
    KEEP_SECOND = "keep_second"
    KEEP_LONGER = "keep_longer"
    CONCATENATE = "concatenate"
    JOIN_UNIQUE = "join_unique"  
    MAX_CONFIDENCE = "max_confidence"
    JOIN_PROPERTIES = "join_properties"

class EntityManager:
    """
    Advanced entity management service.
    
    Handles sophisticated entity operations including:
    - Entity merging with configurable strategies
    - Entity disambiguation 
    - Entity relationship maintenance
    - Entity versioning with temporal validity
    
    Inspired by LightRAG's entity management capabilities to provide
    a more sophisticated knowledge graph management system.
    """
    
    def __init__(self, engine: KnowledgeEngine):
        """
        Initialize the entity manager.
        
        Args:
            engine: Reference to the knowledge engine
        """
        self.engine = engine
        self.tool_registry = None
        
        # Initialize FastMCP tool registry if available
        if fastmcp_available:
            self.tool_registry = ToolRegistry(component_name="athena")
            
    async def initialize_mcp(self) -> None:
        """Initialize MCP integration for the entity manager."""
        if fastmcp_available and self.tool_registry:
            try:
                # Register entity management tools
                await register_entity_tools(self, self.tool_registry)
                logger.info("Registered MCP entity management tools")
            except Exception as e:
                logger.error(f"Error registering MCP entity tools: {e}")
        
    async def merge_entities(
        self,
        source_entities: List[str],
        target_entity_name: str,
        target_entity_type: Optional[str] = None,
        merge_strategies: Optional[Dict[str, str]] = None
    ) -> Optional[Entity]:
        """
        Merge multiple entities into a single entity.
        
        Args:
            source_entities: List of entity IDs or names to merge
            target_entity_name: Name for the merged entity
            target_entity_type: Optional type for the merged entity
            merge_strategies: Field-specific merge strategies
            
        Returns:
            Merged entity or None if operation failed
        """
        if not self.engine.is_initialized:
            await self.engine.initialize()
            
        # Default merge strategies
        default_strategies = {
            "name": EntityMergeStrategy.KEEP_FIRST,
            "properties": EntityMergeStrategy.JOIN_PROPERTIES,
            "aliases": EntityMergeStrategy.JOIN_UNIQUE,
            "confidence": EntityMergeStrategy.MAX_CONFIDENCE,
        }
        
        if merge_strategies:
            # Override defaults with provided strategies
            for field, strategy in merge_strategies.items():
                default_strategies[field] = strategy
                
        # Resolve entities (could be IDs or names)
        entity_objects: List[Entity] = []
        for entity_ref in source_entities:
            entity = await self._resolve_entity(entity_ref)
            if entity:
                entity_objects.append(entity)
                
        if not entity_objects:
            logger.error("No valid source entities found for merging")
            return None
            
        # Create merged entity
        merged_entity = await self._perform_merge(
            entity_objects, 
            target_entity_name,
            target_entity_type,
            default_strategies
        )
        
        if not merged_entity:
            logger.error("Failed to create merged entity")
            return None
            
        # Update relationships
        await self._migrate_relationships(entity_objects, merged_entity)
        
        # Delete source entities
        for entity in entity_objects:
            await self.engine.delete_entity(entity.entity_id)
            
        logger.info(f"Successfully merged {len(entity_objects)} entities into {merged_entity.name}")
        return merged_entity
        
    async def _resolve_entity(self, entity_ref: str) -> Optional[Entity]:
        """
        Resolve entity by ID or name.
        
        Args:
            entity_ref: Entity ID or name
            
        Returns:
            Entity object or None if not found
        """
        # Try direct ID lookup
        entity = await self.engine.get_entity(entity_ref)
        if entity:
            return entity
            
        # Try name-based search
        entities = await self.engine.search_entities(entity_ref, limit=1)
        if entities:
            return entities[0]
            
        logger.warning(f"Could not resolve entity: {entity_ref}")
        return None
        
    async def _perform_merge(
        self,
        entities: List[Entity],
        target_name: str,
        target_type: Optional[str],
        strategies: Dict[str, str]
    ) -> Optional[Entity]:
        """
        Perform the actual entity merging.
        
        Args:
            entities: List of entities to merge
            target_name: Name for the merged entity
            target_type: Type for the merged entity (optional)
            strategies: Field-specific merge strategies
            
        Returns:
            Merged entity or None if operation failed
        """
        if not entities:
            return None
            
        # Use type of first entity if not specified
        entity_type = target_type or entities[0].entity_type
        
        # Start with a new entity
        merged_entity = Entity(
            name=target_name,
            entity_type=entity_type,
            confidence=1.0,
            source="merged"
        )
        
        # Collect all properties, aliases, etc.
        all_properties = {}
        all_aliases = set()
        max_confidence = 0.0
        
        # Process all source entities
        for entity in entities:
            # Handle properties based on strategy
            if strategies.get("properties") == EntityMergeStrategy.JOIN_PROPERTIES:
                # Merge properties, keeping the higher confidence ones
                for key, prop in entity.properties.items():
                    if key not in all_properties or prop["confidence"] > all_properties[key]["confidence"]:
                        all_properties[key] = prop
            
            # Add aliases
            for alias in entity.aliases:
                if alias != target_name.lower():  # Don't add the new name as an alias
                    all_aliases.add(alias)
                    
            # Track highest confidence
            if entity.confidence > max_confidence:
                max_confidence = entity.confidence
                
        # Apply collected data to merged entity
        merged_entity.properties = all_properties
        
        # Add all aliases
        for alias in all_aliases:
            merged_entity.add_alias(alias)
            
        # Set highest confidence if using that strategy
        if strategies.get("confidence") == EntityMergeStrategy.MAX_CONFIDENCE:
            merged_entity.confidence = max_confidence
            
        # Add the entity to the knowledge graph
        merged_id = await self.engine.add_entity(merged_entity)
        
        # Retrieve the created entity
        created_entity = await self.engine.get_entity(merged_id)
        return created_entity
            
    async def _migrate_relationships(
        self,
        source_entities: List[Entity],
        target_entity: Entity
    ) -> None:
        """
        Migrate relationships from source entities to target entity.
        
        Args:
            source_entities: Source entities to migrate relationships from
            target_entity: Target entity to migrate relationships to
        """
        # Get all relationships for each source entity
        deduplication_set = set()
        
        for source_entity in source_entities:
            # Get all relationships for this entity
            relationships = await self.engine.get_entity_relationships(source_entity.entity_id)
            
            # Process each relationship
            for relationship, connected_entity in relationships:
                # Skip if this is a relationship to another source entity (will be deleted)
                if connected_entity.entity_id in [e.entity_id for e in source_entities]:
                    continue
                    
                # Create a unique key to prevent duplicate relationships
                is_outgoing = relationship.source_id == source_entity.entity_id
                
                if is_outgoing:
                    # This is an outgoing relationship
                    rel_key = f"{target_entity.entity_id}|{relationship.relationship_type}|{connected_entity.entity_id}"
                    if rel_key in deduplication_set:
                        continue
                        
                    # Create new outgoing relationship
                    new_rel = Relationship(
                        source_id=target_entity.entity_id,
                        target_id=connected_entity.entity_id,
                        relationship_type=relationship.relationship_type,
                        properties=relationship.properties.copy(),
                        confidence=relationship.confidence,
                        source=relationship.source
                    )
                else:
                    # This is an incoming relationship
                    rel_key = f"{connected_entity.entity_id}|{relationship.relationship_type}|{target_entity.entity_id}"
                    if rel_key in deduplication_set:
                        continue
                        
                    # Create new incoming relationship
                    new_rel = Relationship(
                        source_id=connected_entity.entity_id,
                        target_id=target_entity.entity_id,
                        relationship_type=relationship.relationship_type,
                        properties=relationship.properties.copy(),
                        confidence=relationship.confidence,
                        source=relationship.source
                    )
                    
                # Add to deduplication set and create the new relationship
                deduplication_set.add(rel_key)
                await self.engine.add_relationship(new_rel)
                
        logger.info(f"Migrated {len(deduplication_set)} unique relationships to target entity {target_entity.name}")
        
    async def find_duplicate_entities(
        self, 
        entity_type: Optional[str] = None,
        confidence_threshold: float = 0.7,
        max_results: int = 100
    ) -> List[List[Entity]]:
        """
        Find potential duplicate entities in the knowledge graph.
        
        Args:
            entity_type: Optional entity type to restrict search to
            confidence_threshold: Minimum confidence for entity matching
            max_results: Maximum number of duplicate groups to return
            
        Returns:
            List of entity groups that are potential duplicates
        """
        # This is a placeholder for future implementation
        # This would use vector similarity, name similarity, and property overlap
        # to identify potential duplicate entities
        return []
        
    async def get_entity_versions(
        self,
        entity_id: str
    ) -> List[Entity]:
        """
        Get all temporal versions of an entity.
        
        Args:
            entity_id: Entity ID to get versions for
            
        Returns:
            List of entity versions ordered by valid_from date
        """
        # This is a placeholder for future implementation
        # This would return all temporal versions of an entity
        return []