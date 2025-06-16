"""
Athena API Models for LLM Integration

Provides Pydantic models for LLM-powered knowledge graph operations.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import Field
from pydantic import ConfigDict
from tekton.models import TektonBaseModel
from datetime import datetime

from athena.core.entity import Entity
from athena.core.relationship import Relationship

class KnowledgeContextRequest(TektonBaseModel):
    """Request model for retrieving knowledge context."""
    
    query: str = Field(..., description="The query to get knowledge context for")
    max_entities: Optional[int] = Field(5, description="Maximum number of entities to include")
    min_confidence: Optional[float] = Field(0.7, description="Minimum confidence threshold for relevance")


class KnowledgeContextResponse(TektonBaseModel):
    """Response model for knowledge context."""
    
    query: str = Field(..., description="The original query")
    entities: List[Entity] = Field(default_factory=list, description="Relevant entities")
    relationships: List[Relationship] = Field(default_factory=list, description="Relevant relationships")
    context: Dict[str, Any] = Field(default_factory=dict, description="Structured context for LLM")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Removed old Config class



class KnowledgeChatRequest(TektonBaseModel):
    """Request model for knowledge-enhanced chat."""
    
    query: str = Field(..., description="The user's query")
    max_entities: Optional[int] = Field(5, description="Maximum number of entities to include")
    min_confidence: Optional[float] = Field(0.7, description="Minimum confidence threshold for relevance")
    model: Optional[str] = Field(None, description="LLM model to use")
    provider: Optional[str] = Field(None, description="LLM provider to use")


class KnowledgeChatResponse(TektonBaseModel):
    """Response model for knowledge-enhanced chat."""
    
    query: str = Field(..., description="The original query")
    answer: str = Field(..., description="The LLM-generated answer")
    entities: List[Entity] = Field(default_factory=list, description="Entities mentioned in the answer")
    context_entities: List[Entity] = Field(default_factory=list, description="All context entities")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Removed old Config class



class EntityExtractionRequest(TektonBaseModel):
    """Request model for entity extraction."""
    
    text: str = Field(..., description="The text to extract entities from")
    entity_types: Optional[List[str]] = Field(None, description="Types of entities to extract")
    model: Optional[str] = Field(None, description="LLM model to use")
    provider: Optional[str] = Field(None, description="LLM provider to use")


class EntityExtractionResponse(TektonBaseModel):
    """Response model for entity extraction."""
    
    text: str = Field(..., description="The original text")
    entities: List[Entity] = Field(default_factory=list, description="Extracted entities")
    raw_extraction: Dict[str, Any] = Field(default_factory=dict, description="Raw extraction result")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Removed old Config class



class RelationshipInferenceRequest(TektonBaseModel):
    """Request model for relationship inference."""
    
    entity_ids: List[str] = Field(..., description="IDs of entities to infer relationships between")
    relationship_types: Optional[List[str]] = Field(None, description="Types of relationships to infer")
    model: Optional[str] = Field(None, description="LLM model to use")
    provider: Optional[str] = Field(None, description="LLM provider to use")


class RelationshipInferenceResponse(TektonBaseModel):
    """Response model for relationship inference."""
    
    entity_ids: List[str] = Field(..., description="The original entity IDs")
    relationships: List[Relationship] = Field(default_factory=list, description="Inferred relationships")
    raw_inference: Dict[str, Any] = Field(default_factory=dict, description="Raw inference result")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Removed old Config class



class QueryTranslationRequest(TektonBaseModel):
    """Request model for natural language query translation."""
    
    query: str = Field(..., description="The natural language query to translate")
    model: Optional[str] = Field(None, description="LLM model to use")
    provider: Optional[str] = Field(None, description="LLM provider to use")


class QueryTranslationResponse(TektonBaseModel):
    """Response model for query translation."""
    
    natural_query: str = Field(..., description="The original natural language query")
    cypher_query: str = Field(..., description="The translated Cypher query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    explanation: str = Field("", description="Explanation of the query translation")