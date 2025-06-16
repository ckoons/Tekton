"""
Athena Entity Module

Provides entity management capabilities for the knowledge graph.
"""

import uuid
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime

class Entity:
    """
    Represents a node in the knowledge graph.
    
    Entities are the primary unit of knowledge in Athena, representing
    people, concepts, objects, etc.
    """
    
    def __init__(self, 
                entity_id: Optional[str] = None, 
                entity_type: str = "generic", 
                name: str = "", 
                properties: Dict[str, Any] = None,
                confidence: float = 1.0,
                source: str = "system"):
        """
        Initialize a new entity.
        
        Args:
            entity_id: Unique identifier (UUID string)
            entity_type: Type of entity (person, organization, concept, etc.)
            name: Human-readable name or label
            properties: Dictionary of key-value properties
            confidence: Confidence score (0.0 to 1.0)
            source: Source of the entity information
        """
        self.entity_id = entity_id or str(uuid.uuid4())
        self.entity_type = entity_type
        self.name = name
        self.properties = properties or {}
        self.confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
        self.source = source
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.aliases: Set[str] = set()
        if name:
            self.aliases.add(name.lower())
            
    def add_alias(self, alias: str) -> None:
        """
        Add an alias/alternative name for this entity.
        
        Args:
            alias: Alternative name
        """
        if alias and alias.strip():
            self.aliases.add(alias.lower().strip())
            
    def add_property(self, key: str, value: Any, confidence: float = 1.0) -> None:
        """
        Add or update a property for this entity.
        
        Args:
            key: Property name
            value: Property value
            confidence: Confidence in this property (0.0 to 1.0)
        """
        self.properties[key] = {
            "value": value,
            "confidence": max(0.0, min(1.0, confidence)),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow().isoformat()
        
    def get_property(self, key: str) -> Optional[Any]:
        """
        Get a property value.
        
        Args:
            key: Property name
            
        Returns:
            Property value or None if not found
        """
        prop = self.properties.get(key)
        return prop["value"] if prop else None
        
    def get_property_with_confidence(self, key: str) -> Tuple[Optional[Any], float]:
        """
        Get a property value with its confidence score.
        
        Args:
            key: Property name
            
        Returns:
            Tuple of (value, confidence) or (None, 0.0) if not found
        """
        prop = self.properties.get(key)
        return (prop["value"], prop["confidence"]) if prop else (None, 0.0)
        
    def update_name(self, name: str) -> None:
        """
        Update the entity's primary name.
        
        Args:
            name: New name
        """
        if name and name.strip():
            old_name = self.name
            self.name = name.strip()
            self.aliases.add(name.lower().strip())
            if old_name:
                self.aliases.add(old_name.lower())
            self.updated_at = datetime.utcnow().isoformat()
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to a dictionary representation.
        
        Returns:
            Dictionary representation of the entity
        """
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "properties": self.properties,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "aliases": list(self.aliases)
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """
        Create an entity from a dictionary representation.
        
        Args:
            data: Dictionary representation of an entity
            
        Returns:
            Entity instance
        """
        entity = cls(
            entity_id=data.get("entity_id"),
            entity_type=data.get("entity_type", "generic"),
            name=data.get("name", ""),
            properties=data.get("properties", {}),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "system")
        )
        
        entity.created_at = data.get("created_at", entity.created_at)
        entity.updated_at = data.get("updated_at", entity.updated_at)
        
        # Add aliases
        for alias in data.get("aliases", []):
            entity.add_alias(alias)
            
        return entity
        
    def __str__(self) -> str:
        return f"Entity(id={self.entity_id}, type={self.entity_type}, name={self.name})"
        
    def __repr__(self) -> str:
        return self.__str__()