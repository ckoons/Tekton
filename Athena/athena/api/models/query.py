"""
Query models for Athena API.

These models define the request and response data structures for query operations.
"""

from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import Field
from tekton.models import TektonBaseModel

from tekton.core.query.modes import QueryMode

class QueryRequest(TektonBaseModel):
    """Request model for query execution."""
    question: str = Field(..., description="The query to execute")
    mode: QueryMode = Field(
        default=QueryMode.HYBRID, 
        description="Retrieval mode to use for this query"
    )
    response_type: str = Field(
        default="Multiple Paragraphs",
        description="Response format type"
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return"
    )
    similarity_threshold: float = Field(
        default=0.2,
        description="Minimum similarity threshold for vector search"
    )
    max_tokens_per_chunk: int = Field(
        default=4000,
        description="Maximum tokens per text chunk"
    )
    max_tokens_entity_context: int = Field(
        default=4000,
        description="Maximum tokens for entity descriptions"
    )
    max_tokens_relationship_context: int = Field(
        default=4000,
        description="Maximum tokens for relationship descriptions"
    )
    relationship_depth: int = Field(
        default=2,
        description="Maximum traversal depth for relationship queries"
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous conversation context"
    )
    only_return_context: bool = Field(
        default=False,
        description="If True, only returns context without generating a response"
    )
    include_raw_results: bool = Field(
        default=False,
        description="If True, includes raw results in the response"
    )

class QueryResponse(TektonBaseModel):
    """Response model for query execution."""
    question: str = Field(..., description="Original query")
    mode: str = Field(..., description="Retrieval mode used")
    answer: str = Field("", description="Generated answer")
    context: str = Field("", description="Retrieved context")
    results_count: int = Field(0, description="Number of results")
    raw_results: Optional[Dict[str, Any]] = Field(
        None, 
        description="Raw query results (if requested)"
    )