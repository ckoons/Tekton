"""
Athena Relationship Module

Provides relationship management capabilities for the knowledge graph.
"""

import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class Relationship:
    """
    Represents an edge in the knowledge graph.
    
    Relationships connect entities and provide structured knowledge about
    how entities relate to each other.
    """
    
    def __init__(self, 
                relationship_id: Optional[str] = None,
                relationship_type: str = "generic",
                source_id: str = "",
                target_id: str = "",
                properties: Dict[str, Any] = None,
                confidence: float = 1.0,
                source: str = "system"):
        """
        Initialize a new relationship.
        
        Args:
            relationship_id: Unique identifier (UUID string)
            relationship_type: Type of relationship (employs, contains, etc.)
            source_id: Entity ID of the source entity
            target_id: Entity ID of the target entity
            properties: Dictionary of key-value properties
            confidence: Confidence score (0.0 to 1.0)
            source: Source of the relationship information
        """
        self.relationship_id = relationship_id or str(uuid.uuid4())
        self.relationship_type = relationship_type
        self.source_id = source_id
        self.target_id = target_id
        self.properties = properties or {}
        self.confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
        self.source = source
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        self.is_directional = True  # Most relationships are directional
        
    def add_property(self, key: str, value: Any, confidence: float = 1.0) -> None:
        """
        Add or update a property for this relationship.
        
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
    
    def set_bidirectional(self, is_bidirectional: bool = True) -> None:
        """
        Set whether this relationship is bidirectional.
        
        Args:
            is_bidirectional: True if the relationship is bidirectional
        """
        self.is_directional = not is_bidirectional
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert relationship to a dictionary representation.
        
        Returns:
            Dictionary representation of the relationship
        """
        return {
            "relationship_id": self.relationship_id,
            "relationship_type": self.relationship_type,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "properties": self.properties,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_directional": self.is_directional
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """
        Create a relationship from a dictionary representation.
        
        Args:
            data: Dictionary representation of a relationship
            
        Returns:
            Relationship instance
        """
        relationship = cls(
            relationship_id=data.get("relationship_id"),
            relationship_type=data.get("relationship_type", "generic"),
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            properties=data.get("properties", {}),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "system")
        )
        
        relationship.created_at = data.get("created_at", relationship.created_at)
        relationship.updated_at = data.get("updated_at", relationship.updated_at)
        relationship.is_directional = data.get("is_directional", True)
        
        return relationship
        
    def __str__(self) -> str:
        return f"Relationship(id={self.relationship_id}, type={self.relationship_type}, source={self.source_id}, target={self.target_id})"
        
    def __repr__(self) -> str:
        return self.__str__()