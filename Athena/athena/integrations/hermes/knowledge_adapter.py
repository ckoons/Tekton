"""
Hermes Integration - Knowledge Adapter

Provides integration between Athena's knowledge graph and external components
through the Hermes registration protocol and database services.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

# Add Tekton root to path for shared imports
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)

from shared.utils.env_config import get_component_config

from ...core.entity import Entity
from ...core.relationship import Relationship
from ...core.engine import get_knowledge_engine

# Import Hermes utilities if available
try:
    from hermes.utils.registration_helper import register_component, unregister_component
    from hermes.utils.database_helper import DatabaseClient
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False

logger = logging.getLogger("athena.integrations.hermes.knowledge_adapter")

class HermesKnowledgeAdapter:
    """
    Knowledge adapter for integrating with the Hermes ecosystem.
    
    Provides a standard interface for other components to access
    Athena's knowledge graph functionality.
    """
    
    def __init__(self, 
                component_id: str = "athena.knowledge",
                hermes_url: Optional[str] = None,
                auto_register: bool = True):
        """
        Initialize the adapter.
        
        Args:
            component_id: Component identifier for Hermes
            hermes_url: URL of the Hermes server (None for env var)
            auto_register: Whether to auto-register with Hermes
        """
        self.component_id = component_id
        self.hermes_url = hermes_url or os.getenv("HERMES_URL", "http://localhost:8000")
        self.auto_register = auto_register
        self.engine = None
        self.is_registered = False
        
    async def initialize(self):
        """Initialize the adapter and register with Hermes if enabled."""
        # Initialize the knowledge engine
        self.engine = await get_knowledge_engine()
        if not self.engine.is_initialized:
            await self.engine.initialize()
            
        # Register with Hermes if available and auto-register is enabled
        if HERMES_AVAILABLE and self.auto_register:
            try:
                await self.register_with_hermes()
            except Exception as e:
                logger.error(f"Failed to register with Hermes: {e}")
    
    async def register_with_hermes(self) -> bool:
        """
        Register this component with Hermes.
        
        Returns:
            True if registration successful
        """
        if not HERMES_AVAILABLE:
            logger.warning("Hermes integration not available")
            return False
            
        try:
            # Get component port from environment or use default
            config = get_component_config()
            component_port = config.athena.port if hasattr(config, 'athena') else int(os.environ.get("ATHENA_PORT"))
            
            # Define the component information
            component_info = {
                "name": "athena",
                "display_name": "Athena Knowledge Graph",
                "description": "Knowledge graph system for entity and relationship management",
                "version": "0.1.0",
                "capabilities": [
                    {
                        "type": "knowledge_graph",
                        "description": "Entity and relationship management in a graph database",
                        "endpoints": [
                            {
                                "path": "/api/entities",
                                "description": "Entity management endpoints",
                                "methods": ["GET", "POST", "PUT", "DELETE"]
                            },
                            {
                                "path": "/api/relationships",
                                "description": "Relationship management endpoints",
                                "methods": ["GET", "POST", "PUT", "DELETE"]
                            },
                            {
                                "path": "/api/query",
                                "description": "Knowledge graph query endpoints",
                                "methods": ["POST"]
                            },
                            {
                                "path": "/api/extraction",
                                "description": "Entity extraction endpoints",
                                "methods": ["POST"]
                            }
                        ]
                    },
                    {
                        "type": "llm_enhancement",
                        "description": "Enhanced LLM responses using knowledge graph",
                        "endpoints": [
                            {
                                "path": "/api/llm/chat",
                                "description": "Knowledge-enhanced chat",
                                "methods": ["POST"]
                            },
                            {
                                "path": "/api/llm/knowledge/enhance",
                                "description": "Knowledge enhancement for LLM prompts",
                                "methods": ["POST"]
                            }
                        ]
                    },
                    {
                        "type": "visualization",
                        "description": "Knowledge graph visualization endpoints",
                        "endpoints": [
                            {
                                "path": "/api/visualization/graph",
                                "description": "Get graph visualization data",
                                "methods": ["GET"]
                            },
                            {
                                "path": "/api/visualization/subgraph/{entity_id}",
                                "description": "Get subgraph around an entity",
                                "methods": ["GET"]
                            }
                        ]
                    },
                    {
                        "type": "ui_component",
                        "description": "Knowledge graph visualization and interaction UI component",
                        "component_path": "/ui/athena-component.html",
                        "component_name": "athena-component"
                    }
                ],
                "dependencies": [
                    {
                        "component": "engram",
                        "required": False,
                        "features": ["memory_retrieval", "memory_storage"]
                    },
                    {
                        "component": "rhetor",
                        "required": True,
                        "features": ["llm_inference"]
                    }
                ],
                "api_url": f"http://localhost:{component_port}",
                "ui": {
                    "icon": "/images/icon.jpg",
                    "color": "#4a86e8",
                    "order": 5
                }
            }
            
            # Register with Hermes
            success = await register_component(
                component_id=self.component_id,
                hermes_url=self.hermes_url,
                component_info=component_info
            )
            
            if success:
                logger.info(f"Registered with Hermes as {self.component_id}")
                self.is_registered = True
            else:
                logger.error("Failed to register with Hermes")
                
            return success
            
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False
            
    async def unregister_from_hermes(self) -> bool:
        """
        Unregister this component from Hermes.
        
        Returns:
            True if unregistration successful
        """
        if not HERMES_AVAILABLE or not self.is_registered:
            return False
            
        try:
            # Unregister from Hermes
            success = await unregister_component(
                component_id=self.component_id,
                hermes_url=self.hermes_url
            )
            
            if success:
                logger.info(f"Unregistered from Hermes: {self.component_id}")
                self.is_registered = False
            else:
                logger.error("Failed to unregister from Hermes")
                
            return success
            
        except Exception as e:
            logger.error(f"Error unregistering from Hermes: {e}")
            return False
    
    async def add_entity(self, 
                      entity_type: str, 
                      name: str, 
                      properties: Dict[str, Any] = None,
                      confidence: float = 1.0,
                      source: str = "system") -> str:
        """
        Add a new entity to the knowledge graph.
        
        Args:
            entity_type: Type of entity (person, organization, etc.)
            name: Name of the entity
            properties: Additional properties for the entity
            confidence: Confidence in this entity (0.0 to 1.0)
            source: Source of the entity information
            
        Returns:
            Entity ID
        """
        if not self.engine:
            await self.initialize()
            
        # Create entity object
        entity = Entity(
            entity_type=entity_type,
            name=name,
            properties=properties or {},
            confidence=confidence,
            source=source
        )
        
        # Add to knowledge graph
        entity_id = await self.engine.add_entity(entity)
        return entity_id
    
    async def add_relationship(self,
                            source_id: str,
                            relationship_type: str,
                            target_id: str,
                            properties: Dict[str, Any] = None,
                            confidence: float = 1.0,
                            source: str = "system") -> str:
        """
        Add a new relationship to the knowledge graph.
        
        Args:
            source_id: Source entity ID
            relationship_type: Type of relationship
            target_id: Target entity ID
            properties: Additional properties for the relationship
            confidence: Confidence in this relationship (0.0 to 1.0)
            source: Source of the relationship information
            
        Returns:
            Relationship ID
        """
        if not self.engine:
            await self.initialize()
            
        # Create relationship object
        relationship = Relationship(
            relationship_type=relationship_type,
            source_id=source_id,
            target_id=target_id,
            properties=properties or {},
            confidence=confidence,
            source=source
        )
        
        # Add to knowledge graph
        relationship_id = await self.engine.add_relationship(relationship)
        return relationship_id
    
    async def verify_fact(self, fact: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Verify a fact against the knowledge graph.
        
        Args:
            fact: Fact to verify (as a string)
            confidence_threshold: Confidence threshold for verification
            
        Returns:
            Verification result with supporting evidence
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
                if isinstance(prop_data, dict):
                    prop_value = prop_data.get("value", "")
                    confidence = prop_data.get("confidence", 0.0)
                else:
                    prop_value = prop_data
                    confidence = 1.0
                
                if (isinstance(prop_value, str) and 
                    prop_value.lower() in fact.lower() and 
                    confidence >= confidence_threshold):
                    return {
                        "verified": True,
                        "confidence": confidence,
                        "supporting_entity": entity.to_dict(),
                        "property": prop_key,
                        "property_value": prop_value
                    }
        
        return {
            "verified": False,
            "confidence": 0.0,
            "reason": "No supporting evidence found"
        }
    
    async def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw Cypher query against the knowledge graph.
        
        Args:
            cypher_query: Cypher query string
            params: Query parameters
            
        Returns:
            Query results
        """
        if not self.engine:
            await self.initialize()
            
        results = await self.engine.execute_query(cypher_query, params or {})
        return results
    
    async def find_connections(self, entity_name: str, target_name: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Find connections between two entities by name.
        
        Args:
            entity_name: Source entity name
            target_name: Target entity name
            max_depth: Maximum path length
            
        Returns:
            List of paths connecting the entities
        """
        if not self.engine:
            await self.initialize()
            
        # Find source and target entities by name
        source_entities = await self.engine.search_entities(entity_name, limit=3)
        target_entities = await self.engine.search_entities(target_name, limit=3)
        
        if not source_entities or not target_entities:
            return []
            
        # Find paths between each pair
        paths = []
        for source in source_entities:
            for target in target_entities:
                # Don't search for paths to self
                if source.entity_id == target.entity_id:
                    continue
                    
                # Find paths
                found_paths = await self.engine.find_path(source.entity_id, target.entity_id, max_depth)
                
                if found_paths:
                    # Convert paths to serializable format
                    for path in found_paths:
                        serialized_path = []
                        for item in path:
                            if isinstance(item, Entity):
                                serialized_path.append({"type": "entity", "data": item.to_dict()})
                            elif isinstance(item, Relationship):
                                serialized_path.append({"type": "relationship", "data": item.to_dict()})
                        paths.append(serialized_path)
        
        return paths
    
    async def get_entity_graph(self, entity_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get a subgraph centered on a specific entity.
        
        Args:
            entity_id: Center entity ID
            depth: Depth of relationships to include
            
        Returns:
            Entity graph with nodes and edges
        """
        if not self.engine:
            await self.initialize()
            
        # Get the center entity
        center_entity = await self.engine.get_entity(entity_id)
        if not center_entity:
            return {"error": f"Entity {entity_id} not found"}
            
        # Initialize the graph
        nodes = [center_entity.to_dict()]
        edges = []
        visited_ids = {entity_id}
        
        # Process current depth level
        current_ids = {entity_id}
        
        # For each depth level
        for _ in range(depth):
            next_ids = set()
            
            # Process each ID at this level
            for current_id in current_ids:
                # Get relationships for this entity
                relationships = await self.engine.get_entity_relationships(current_id)
                
                for rel, related_entity in relationships:
                    # Add the relationship
                    edges.append(rel.to_dict())
                    
                    # If we haven't seen this entity before, add it
                    if related_entity.entity_id not in visited_ids:
                        nodes.append(related_entity.to_dict())
                        visited_ids.add(related_entity.entity_id)
                        next_ids.add(related_entity.entity_id)
            
            # Set up the next level
            current_ids = next_ids
        
        return {
            "nodes": nodes,
            "edges": edges,
            "center": entity_id
        }
    
    async def shutdown(self):
        """Shut down the adapter and unregister from Hermes."""
        if self.is_registered:
            await self.unregister_from_hermes()
            
        if self.engine and self.engine.is_initialized:
            await self.engine.shutdown()