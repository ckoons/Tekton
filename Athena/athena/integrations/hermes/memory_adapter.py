"""
Hermes Integration - Knowledge to Memory Adapter

Provides integration between Athena's knowledge graph and Hermes memory systems.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple

from ...core.entity import Entity
from ...core.relationship import Relationship
from ...core.engine import get_knowledge_engine

logger = logging.getLogger("athena.integrations.hermes.memory_adapter")

class HermesKnowledgeAdapter:
    """
    Knowledge adapter for integrating with Hermes memory system.
    
    Enables fact verification and knowledge-grounded memory operations
    through integration with Hermes memory systems.
    """
    
    def __init__(self, component_id: str = "athena.knowledge"):
        """
        Initialize the adapter.
        
        Args:
            component_id: Component identifier for Hermes
        """
        self.component_id = component_id
        self.engine = None
        
    async def initialize(self):
        """Initialize the adapter."""
        self.engine = await get_knowledge_engine()
        if not self.engine.is_initialized:
            await self.engine.initialize()
    
    async def verify_fact(self, fact: str, confidence_threshold: float = 0.7) -> Tuple[bool, Optional[Entity]]:
        """
        Verify a fact against the knowledge graph.
        
        Args:
            fact: Fact to verify (as a string)
            confidence_threshold: Confidence threshold for verification
            
        Returns:
            Tuple of (is_verified, supporting_entity)
        """
        if not self.engine:
            await self.initialize()
        
        # Extract key terms from the fact
        terms = fact.split()
        relevant_terms = [term for term in terms if len(term) > 3]
        
        # Search for entities matching these terms
        matching_entities = []
        for term in relevant_terms:
            entities = await self.engine.search_entities(term, limit=5)
            matching_entities.extend(entities)
        
        # Check if any entity supports this fact with sufficient confidence
        for entity in matching_entities:
            # Check properties for matching information
            for prop_key, prop_data in entity.properties.items():
                prop_value = prop_data.get("value", "")
                confidence = prop_data.get("confidence", 0.0)
                
                if (isinstance(prop_value, str) and 
                    prop_value.lower() in fact.lower() and 
                    confidence >= confidence_threshold):
                    return True, entity
        
        return False, None
        
    async def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Text to extract entities from
            entity_types: Optional list of entity types to extract
            
        Returns:
            List of extracted entities
        """
        if not self.engine:
            await self.initialize()
        
        # Extract relevant terms from text
        # This is a simple implementation; a real system would use NER
        words = text.split()
        potential_entities = [word for word in words if word[0].isupper() and len(word) > 3]
        
        # Search for these potential entities in the knowledge graph
        found_entities = []
        for potential_entity in potential_entities:
            # Search for this term
            entities = await self.engine.search_entities(potential_entity, limit=3)
            
            # Filter by entity type if specified
            if entity_types:
                entities = [e for e in entities if e.entity_type in entity_types]
                
            found_entities.extend(entities)
            
        return found_entities
        
    async def enrich_memory(self, memory_content: str) -> Dict[str, Any]:
        """
        Enrich memory with knowledge from the graph.
        
        Args:
            memory_content: Memory content to enrich
            
        Returns:
            Enriched memory with knowledge metadata
        """
        if not self.engine:
            await self.initialize()
        
        # Extract entities from memory
        entities = await self.extract_entities(memory_content)
        
        # Find relationships between extracted entities
        relationships = []
        entity_ids = [entity.entity_id for entity in entities]
        
        for i, source_id in enumerate(entity_ids):
            for target_id in entity_ids[i+1:]:
                # Find paths between these entities
                paths = await self.engine.find_path(source_id, target_id, max_depth=2)
                
                for path in paths:
                    # Extract relationships from the path
                    for item in path:
                        if isinstance(item, Relationship):
                            relationships.append(item)
        
        # Build knowledge enrichment
        enrichment = {
            "entities": [entity.to_dict() for entity in entities],
            "relationships": [rel.to_dict() for rel in relationships],
            "knowledge_graph_integrated": True,
            "enrichment_timestamp": asyncio.get_event_loop().time()
        }
        
        return enrichment
        
    async def get_related_knowledge(self, entity_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Get knowledge related to a specific entity.
        
        Args:
            entity_id: Entity ID to get related knowledge for
            max_depth: Maximum depth of relationship traversal
            
        Returns:
            Dictionary of related entities and relationships
        """
        if not self.engine:
            await self.initialize()
        
        # Get the entity
        entity = await self.engine.get_entity(entity_id)
        if not entity:
            return {"error": f"Entity {entity_id} not found"}
        
        # Get direct relationships
        direct_relationships = await self.engine.get_entity_relationships(entity_id)
        
        # Convert to serializable format
        related_entities = []
        relationships = []
        
        for rel, related_entity in direct_relationships:
            related_entities.append(related_entity.to_dict())
            relationships.append(rel.to_dict())
            
            # Get second-degree relationships if depth > 1
            if max_depth > 1:
                secondary_relationships = await self.engine.get_entity_relationships(related_entity.entity_id)
                
                for sec_rel, sec_entity in secondary_relationships:
                    # Don't include the original entity
                    if sec_entity.entity_id != entity_id:
                        related_entities.append(sec_entity.to_dict())
                        relationships.append(sec_rel.to_dict())
        
        # Create the knowledge object
        knowledge = {
            "entity": entity.to_dict(),
            "related_entities": related_entities,
            "relationships": relationships
        }
        
        return knowledge