"""
Standard query modes and parameters for Tekton components.

Inspired by LightRAG's query modes, this module provides a standardized
way to specify different retrieval strategies across Tekton components.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable

class QueryMode(str, Enum):
    """
    Standard query modes across Tekton components.
    
    Based on LightRAG's query modes:
    - NAIVE: Basic keyword search without advanced knowledge graph integration
    - LOCAL: Entity-focused retrieval that prioritizes relevant entities
    - GLOBAL: Relationship-focused retrieval for understanding connections
    - HYBRID: Combination of LOCAL and GLOBAL modes
    - MIX: Fully integrated graph and vector search (most advanced)
    """
    NAIVE = "naive"    # Basic context retrieval
    LOCAL = "local"    # Entity-focused retrieval
    GLOBAL = "global"  # Relationship-focused retrieval
    HYBRID = "hybrid"  # Combined local and global
    MIX = "mix"        # Integrated graph and vector

@dataclass
class QueryParameters:
    """
    Standardized query parameters for Tekton's RAG capabilities.
    
    Provides a unified interface for specifying retrieval behavior
    across different Tekton components. Adapts LightRAG's query
    parameters to Tekton's architecture.
    """
    
    mode: QueryMode = QueryMode.HYBRID
    """Retrieval mode to use for this query."""
    
    response_type: str = "Multiple Paragraphs"
    """
    Response format type.
    Options include: 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points'
    """
    
    stream: bool = False
    """If True, enables streaming response generation."""
    
    # Result limits
    max_results: int = 10
    """Maximum number of results to return."""
    
    max_tokens_per_chunk: int = 4000
    """Maximum tokens per text chunk in the retrieved context."""
    
    max_tokens_entity_context: int = 4000
    """Maximum tokens for entity descriptions in local retrieval."""
    
    max_tokens_relationship_context: int = 4000
    """Maximum tokens for relationship descriptions in global retrieval."""
    
    # Entity retrieval parameters
    entity_confidence_threshold: float = 0.7
    """Minimum confidence threshold for entity matching."""
    
    max_entities: int = 20
    """Maximum number of entities to retrieve in LOCAL mode."""
    
    # Relationship retrieval parameters
    max_relationships: int = 40
    """Maximum number of relationships to retrieve in GLOBAL mode."""
    
    relationship_depth: int = 2
    """Maximum traversal depth for relationship queries."""
    
    # Vector search parameters
    similarity_threshold: float = 0.2
    """Minimum similarity threshold for vector search."""
    
    rerank_results: bool = True
    """If True, reranks results using a cross-attention model."""
    
    # Context and filtering
    filter_ids: Optional[List[str]] = None
    """Optional IDs to filter the search results."""
    
    high_level_keywords: List[str] = field(default_factory=list)
    """High-level keywords to prioritize in retrieval."""
    
    low_level_keywords: List[str] = field(default_factory=list)
    """Low-level keywords to refine retrieval focus."""
    
    # Model parameters
    model_override: Optional[str] = None
    """Optional model name to override the default."""
    
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    """Additional parameters for the LLM."""
    
    # Conversation context
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    """Previous conversation context in the format [{'role': 'user|assistant', 'content': 'message'}]."""
    
    history_turns: int = 3
    """Number of conversation turns to consider for context."""
    
    # Output control
    only_return_context: bool = False
    """If True, only returns the retrieved context without generating a response."""
    
    only_return_prompt: bool = False
    """If True, only returns the generated prompt without executing it."""