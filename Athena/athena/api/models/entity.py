"""
Entity models for Athena API.

These models define the request and response data structures for entity operations.
"""

from typing import Dict, List, Any, Optional, Set, Union
from pydantic import Field
from tekton.models import TektonBaseModel
from datetime import datetime

from athena.core.entity import Entity

class EntityBase(TektonBaseModel):
    """Base model for entity data."""
    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Entity type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Entity properties")
    
class EntityCreate(EntityBase):
    """Request model for entity creation."""
    confidence: float = Field(default=1.0, description="Confidence score (0.0 to 1.0)")
    source: str = Field(default="api", description="Source of the entity")
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    
    def to_domain_entity(self, entity_id: Optional[str] = None) -> Entity:
        """Convert API model to domain entity."""
        entity = Entity(
            entity_id=entity_id,
            name=self.name,
            entity_type=self.entity_type,
            properties=self.properties,
            confidence=self.confidence,
            source=self.source
        )
        
        # Add aliases
        for alias in self.aliases:
            entity.add_alias(alias)
            
        return entity

class EntityUpdate(EntityBase):
    """Request model for entity updates."""
    confidence: Optional[float] = Field(None, description="Confidence score (0.0 to 1.0)")
    source: Optional[str] = Field(None, description="Source of the entity")
    aliases: Optional[List[str]] = Field(None, description="Alternative names")

class EntityResponse(EntityBase):
    """Response model for entity data."""
    entity_id: str = Field(..., description="Unique entity ID")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    source: str = Field(..., description="Source of the entity")
    aliases: List[str] = Field(..., description="Alternative names")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    @classmethod
    def from_domain_entity(cls, entity: Entity) -> "EntityResponse":
        """Convert domain entity to API response model."""
        return cls(
            entity_id=entity.entity_id,
            name=entity.name,
            entity_type=entity.entity_type,
            properties=entity.properties,
            confidence=entity.confidence,
            source=entity.source,
            aliases=list(entity.aliases),
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

class EntitySearchResult(TektonBaseModel):
    """Search result for entities."""
    results: List[EntityResponse] = Field(..., description="List of matching entities")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")

class EntityMergeRequest(TektonBaseModel):
    """Request for merging entities."""
    source_entities: List[str] = Field(
        ..., 
        description="List of entity IDs or names to merge"
    )
    target_entity_name: str = Field(
        ..., 
        description="Name for the merged entity"
    )
    target_entity_type: Optional[str] = Field(
        None, 
        description="Type for the merged entity"
    )
    merge_strategies: Optional[Dict[str, str]] = Field(
        None, 
        description="Field-specific merge strategies"
    )

class EntityMergeResponse(EntityResponse):
    """Response after merging entities."""
    merged_entity_count: int = Field(..., description="Number of entities merged")
    source_entities: List[str] = Field(..., description="List of original entity IDs")