"""
Apollo MCP Preparation Tools
Provides MCP tools for Context Brief preparation and memory management
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Configure logging
logger = logging.getLogger(__name__)

# Import FastMCP
try:
    from fastmcp import mcp_tool
    fastmcp_available = True
except ImportError:
    logger.warning("FastMCP not available, using fallback")
    fastmcp_available = False
    
    # Fallback decorator
    def mcp_tool(**kwargs):
        def decorator(func):
            return func
        return decorator

# Import preparation components
import sys
from pathlib import Path
apollo_root = Path(__file__).parent.parent
sys.path.insert(0, str(apollo_root))

from core.preparation.context_brief import (
    ContextBriefManager, MemoryItem, MemoryType, CIType
)
from core.preparation.brief_presenter import BriefPresenter
from core.preparation.memory_extractor import MemoryExtractor
from core.preparation.landmark_manager import LandmarkManager

# Initialize managers
brief_manager = None
presenter = None
extractor = None

def initialize_preparation():
    """Initialize preparation components"""
    global brief_manager, presenter, extractor
    
    if not brief_manager:
        # Use Apollo data directory
        storage_dir = apollo_root / "data" / "preparation"
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        brief_manager = ContextBriefManager(storage_dir=storage_dir)
        presenter = BriefPresenter(catalog=brief_manager)
        extractor = MemoryExtractor(catalog=brief_manager)
        
        logger.info("Preparation components initialized")

# MCP Tools

@mcp_tool(
    name="get_context_brief",
    description="Get prepared Context Brief for a CI with relevant memories",
    input_schema={
        "type": "object",
        "properties": {
            "ci_name": {
                "type": "string",
                "description": "Name of the CI requesting the brief"
            },
            "message": {
                "type": "string", 
                "description": "Current message for context relevance"
            },
            "max_tokens": {
                "type": "integer",
                "description": "Maximum token budget (default 2000)",
                "default": 2000
            },
            "include_landmarks": {
                "type": "boolean",
                "description": "Include landmark references",
                "default": True
            }
        },
        "required": ["ci_name", "message"]
    }
)
async def get_context_brief(
    ci_name: str,
    message: str,
    max_tokens: int = 2000,
    include_landmarks: bool = True
) -> Dict[str, Any]:
    """
    Get prepared Context Brief for a CI
    
    Returns formatted context with relevant memories and landmarks
    """
    initialize_preparation()
    
    try:
        # Get formatted memory context
        brief = presenter.get_memory_context(
            ci_name=ci_name,
            message=message,
            max_tokens=max_tokens
        )
        
        # Update relevance scores
        brief_manager.update_relevance_scores({
            'ci_name': ci_name,
            'message': message
        })
        
        # Get packed memories
        memories = brief_manager.pack_memories(max_tokens - 100)
        
        # Format response
        response = {
            "brief": brief,
            "memories": presenter.format_for_api(memories),
            "token_count": sum(m.tokens for m in memories)
        }
        
        # Add landmarks if requested
        if include_landmarks:
            landmarks = []
            for memory in memories[:5]:  # Top 5 as landmarks
                landmarks.append({
                    "id": f"lmk_{memory.type.value}_{memory.id}",
                    "type": memory.type.value,
                    "summary": memory.summary,
                    "timestamp": memory.timestamp.isoformat() if hasattr(memory.timestamp, 'isoformat') else str(memory.timestamp)
                })
            response["landmarks"] = landmarks
        
        logger.info(f"Prepared Context Brief for {ci_name}: {response['token_count']} tokens")
        return response
        
    except Exception as e:
        logger.error(f"Failed to prepare Context Brief: {e}")
        return {
            "error": str(e),
            "brief": "",
            "memories": [],
            "token_count": 0
        }


@mcp_tool(
    name="store_memory",
    description="Store a new memory landmark in Apollo's catalog",
    input_schema={
        "type": "object",
        "properties": {
            "ci_source": {
                "type": "string",
                "description": "CI that generated this memory"
            },
            "type": {
                "type": "string",
                "enum": ["decision", "insight", "context", "plan", "error"],
                "description": "Type of memory"
            },
            "summary": {
                "type": "string",
                "description": "Brief summary (max 50 chars)"
            },
            "content": {
                "type": "string",
                "description": "Full memory content"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Relevance tags",
                "default": []
            },
            "priority": {
                "type": "integer",
                "minimum": 0,
                "maximum": 10,
                "description": "Priority 0-10",
                "default": 5
            }
        },
        "required": ["ci_source", "type", "summary", "content"]
    }
)
async def store_memory(
    ci_source: str,
    type: str,
    summary: str,
    content: str,
    tags: List[str] = None,
    priority: int = 5
) -> Dict[str, Any]:
    """
    Store a new memory in Apollo's catalog
    
    Creates a memory item and landmark node
    """
    initialize_preparation()
    
    try:
        # Convert type string to enum
        memory_type = MemoryType(type)
        
        # Store using manager
        memory = brief_manager.store(
            ci_name=ci_source,
            memory_type=memory_type,
            summary=summary,
            content=content,
            tags=tags or [],
            priority=priority
        )
        
        # Save catalog
        brief_manager.save()
        
        # Create landmark ID
        landmark_id = f"lmk_{type}_{memory.id}"
        
        logger.info(f"Stored memory {memory.id} as landmark {landmark_id}")
        
        return {
            "memory_id": memory.id,
            "landmark_id": landmark_id,
            "status": "stored",
            "namespace": "apollo"
        }
        
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }


@mcp_tool(
    name="search_memories",
    description="Search Apollo's memory catalog",
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query text"
            },
            "ci_filter": {
                "type": "string",
                "description": "Filter by CI source"
            },
            "type_filter": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["decision", "insight", "context", "plan", "error"]
                },
                "description": "Filter by memory types"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results",
                "default": 10
            }
        }
    }
)
async def search_memories(
    query: str = None,
    ci_filter: str = None,
    type_filter: List[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search memories in Apollo's catalog
    
    Returns matching memories with landmarks
    """
    initialize_preparation()
    
    try:
        # Start with all memories or search
        if query:
            results = brief_manager.search(query)
        else:
            results = brief_manager.memories.copy()
        
        # Apply CI filter
        if ci_filter:
            results = [m for m in results if m.ci_source == ci_filter]
        
        # Apply type filter
        if type_filter:
            type_enums = [MemoryType(t) for t in type_filter]
            results = [m for m in results if m.type in type_enums]
        
        # Sort and limit
        results = sorted(results, key=lambda m: (m.priority, m.timestamp), reverse=True)
        results = results[:limit]
        
        # Create landmarks
        landmarks = []
        for memory in results:
            landmarks.append({
                "id": f"lmk_{memory.type.value}_{memory.id}",
                "type": memory.type.value,
                "summary": memory.summary
            })
        
        return {
            "memories": presenter.format_for_api(results),
            "landmarks": landmarks,
            "total_count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        return {
            "error": str(e),
            "memories": [],
            "landmarks": [],
            "total_count": 0
        }


@mcp_tool(
    name="extract_memories",
    description="Extract memories from a CI exchange",
    input_schema={
        "type": "object",
        "properties": {
            "ci_name": {
                "type": "string",
                "description": "Name of the CI"
            },
            "user_message": {
                "type": "string",
                "description": "User's input message"
            },
            "ci_response": {
                "type": "string",
                "description": "CI's response"
            },
            "auto_store": {
                "type": "boolean",
                "description": "Automatically store extracted memories",
                "default": True
            }
        },
        "required": ["ci_name", "ci_response"]
    }
)
async def extract_memories(
    ci_name: str,
    ci_response: str,
    user_message: str = "",
    auto_store: bool = True
) -> Dict[str, Any]:
    """
    Extract memories from a CI exchange
    
    Uses pattern matching to identify decisions, insights, errors, etc.
    """
    initialize_preparation()
    
    try:
        # Extract memories
        memories = extractor.extract_from_exchange(
            ci_name=ci_name,
            user_message=user_message,
            ci_response=ci_response
        )
        
        # Store if requested
        stored_ids = []
        if auto_store and memories:
            stored_count = extractor.store_memories(memories)
            stored_ids = [m.id for m in memories[:stored_count]]
            logger.info(f"Stored {stored_count} extracted memories")
        
        # Format response
        return {
            "extracted_count": len(memories),
            "stored_count": len(stored_ids),
            "memories": presenter.format_for_api(memories),
            "stored_ids": stored_ids
        }
        
    except Exception as e:
        logger.error(f"Failed to extract memories: {e}")
        return {
            "error": str(e),
            "extracted_count": 0,
            "stored_count": 0,
            "memories": []
        }


@mcp_tool(
    name="get_memory_statistics",
    description="Get statistics about Apollo's memory catalog",
    input_schema={
        "type": "object",
        "properties": {
            "ci_name": {
                "type": "string",
                "description": "Optional CI filter"
            }
        }
    }
)
async def get_memory_statistics(ci_name: str = None) -> Dict[str, Any]:
    """
    Get memory catalog statistics
    
    Returns counts, distributions, and metrics
    """
    initialize_preparation()
    
    try:
        if ci_name:
            # Get CI-specific stats
            summary = presenter.get_memory_summary(ci_name)
            return summary
        else:
            # Get global stats
            stats = brief_manager.get_statistics()
            return {
                "total_memories": stats.total_memories,
                "total_tokens": stats.total_tokens,
                "by_type": stats.by_type,
                "by_ci": stats.by_ci,
                "by_ci_type": stats.by_ci_type,
                "oldest_memory": stats.oldest_memory.isoformat() if stats.oldest_memory else None,
                "newest_memory": stats.newest_memory.isoformat() if stats.newest_memory else None,
                "avg_priority": stats.avg_priority
            }
            
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return {
            "error": str(e),
            "total_memories": 0
        }


@mcp_tool(
    name="get_landmarks",
    description="Get memory landmarks from Apollo's knowledge graph",
    input_schema={
        "type": "object",
        "properties": {
            "ci_name": {
                "type": "string",
                "description": "Optional CI filter"
            },
            "landmark_id": {
                "type": "string",
                "description": "Get specific landmark by ID"
            },
            "include_relationships": {
                "type": "boolean",
                "description": "Include related landmarks",
                "default": False
            }
        }
    }
)
async def get_landmarks(
    ci_name: str = None,
    landmark_id: str = None,
    include_relationships: bool = False
) -> Dict[str, Any]:
    """
    Get memory landmarks from knowledge graph
    
    Returns landmarks with optional relationships
    """
    initialize_preparation()
    
    try:
        if landmark_id and brief_manager.landmark_manager:
            # Get specific landmark
            landmark = brief_manager.landmark_manager.get_landmark(landmark_id)
            if not landmark:
                return {"error": f"Landmark {landmark_id} not found"}
            
            result = {"landmark": landmark}
            
            if include_relationships:
                related = brief_manager.landmark_manager.get_related_landmarks(landmark_id)
                result["related"] = related
            
            return result
        
        else:
            # Get multiple landmarks
            landmarks = brief_manager.get_landmarks(ci_name)
            
            return {
                "landmarks": landmarks,
                "count": len(landmarks),
                "namespace": "apollo"
            }
            
    except Exception as e:
        logger.error(f"Failed to get landmarks: {e}")
        return {
            "error": str(e),
            "landmarks": []
        }


@mcp_tool(
    name="analyze_memory_relationships",
    description="Analyze and create relationships between memory landmarks",
    input_schema={
        "type": "object",
        "properties": {
            "create_relationships": {
                "type": "boolean",
                "description": "Actually create the relationships",
                "default": True
            }
        }
    }
)
async def analyze_memory_relationships(create_relationships: bool = True) -> Dict[str, Any]:
    """
    Analyze memories and create landmark relationships
    
    Finds temporal and causal relationships
    """
    initialize_preparation()
    
    try:
        if create_relationships:
            created = brief_manager.analyze_relationships()
            return {
                "relationships_created": created,
                "status": "completed"
            }
        else:
            # Just analyze without creating
            if brief_manager.landmark_manager:
                relationships = brief_manager.landmark_manager.find_relationships(brief_manager.memories)
                return {
                    "potential_relationships": len(relationships),
                    "status": "analyzed"
                }
            else:
                return {
                    "error": "Landmark manager not available",
                    "status": "failed"
                }
                
    except Exception as e:
        logger.error(f"Failed to analyze relationships: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }


# Tool registration
def get_preparation_tools():
    """Get all preparation MCP tools"""
    return [
        get_context_brief,
        store_memory,
        search_memories,
        extract_memories,
        get_memory_statistics,
        get_landmarks,
        analyze_memory_relationships
    ]


# Export for MCP registration
__all__ = [
    'get_context_brief',
    'store_memory', 
    'search_memories',
    'extract_memories',
    'get_memory_statistics',
    'get_preparation_tools'
]