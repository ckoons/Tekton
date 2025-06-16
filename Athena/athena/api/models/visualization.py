"""
Athena API Models for Graph Visualization

Provides Pydantic models for graph visualization requests and responses.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import Field
from pydantic import ConfigDict
from tekton.models import TektonBaseModel
from enum import Enum
from datetime import datetime

from athena.core.entity import Entity
from athena.core.relationship import Relationship

class VisualizationLayout(str, Enum):
    """Graph layout algorithms."""
    
    force_directed = "force-directed"
    circular = "circular"
    hierarchical = "hierarchical"
    radial = "radial"


class GraphVisualizationRequest(TektonBaseModel):
    """Request model for custom graph visualization."""
    
    query: Optional[str] = Field(None, description="Search query for entities")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    relationship_type: Optional[str] = Field(None, description="Filter by relationship type")
    limit: Optional[int] = Field(100, description="Maximum number of entities to include")
    min_confidence: Optional[float] = Field(0.0, description="Minimum confidence threshold")
    center_node_id: Optional[str] = Field(None, description="ID of node to center graph around")
    depth: Optional[int] = Field(1, description="Depth of relationships from center node")
    layout: Optional[VisualizationLayout] = Field(VisualizationLayout.force_directed, description="Graph layout algorithm")


class GraphVisualizationResponse(TektonBaseModel):
    """Response model for graph visualization data."""
    
    entities: List[Entity] = Field(default_factory=list, description="Entities in the visualization")
    relationships: List[Relationship] = Field(default_factory=list, description="Relationships in the visualization")
    layout: VisualizationLayout = Field(VisualizationLayout.force_directed, description="Selected graph layout algorithm")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SubgraphRequest(TektonBaseModel):
    """Request model for subgraph visualization."""
    
    center_entity_id: str = Field(..., description="ID of entity to center subgraph around")
    depth: int = Field(1, description="Depth of relationships to include")
    relationship_type: Optional[str] = Field(None, description="Filter by relationship type")
    min_confidence: float = Field(0.0, description="Minimum confidence threshold")
    layout: VisualizationLayout = Field(VisualizationLayout.force_directed, description="Graph layout algorithm")


class SubgraphResponse(TektonBaseModel):
    """Response model for subgraph visualization."""
    
    center_entity_id: str = Field(..., description="ID of the central entity")
    depth: int = Field(..., description="Depth of relationships included")
    entities: List[Entity] = Field(default_factory=list, description="Entities in the subgraph")
    relationships: List[Relationship] = Field(default_factory=list, description="Relationships in the subgraph")
    layout: VisualizationLayout = Field(VisualizationLayout.force_directed, description="Selected graph layout algorithm")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExportFormat(str, Enum):
    """Export format options."""
    
    json = "json"
    graphml = "graphml"
    cypher = "cypher"
    png = "png"
    svg = "svg"


class ExportRequest(TektonBaseModel):
    """Request model for graph export."""
    
    entities: List[str] = Field(default_factory=list, description="Entity IDs to include in export")
    include_all: bool = Field(False, description="Include all entities in the graph")
    format: ExportFormat = Field(ExportFormat.json, description="Export format")
    include_properties: bool = Field(True, description="Include entity and relationship properties")
    filename: Optional[str] = Field(None, description="Suggested filename for export")