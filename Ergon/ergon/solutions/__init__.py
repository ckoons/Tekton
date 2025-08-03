"""
Ergon Solutions Package
======================

This package contains all the reusable solutions in Ergon's registry.
"""

from .codebase_indexer import create_indexer_solution, CodebaseIndexer
from .rag_solution import create_rag_solution, RAGEngine
from .cache_rag import create_cache_rag_solution, CacheRAGEngine
from .companion_intelligence import create_companion_intelligence_solution, CompanionIntelligence

# Registry of all available solutions
SOLUTION_REGISTRY = [
    create_indexer_solution(),
    create_rag_solution(),
    create_cache_rag_solution(),
    create_companion_intelligence_solution()
]

__all__ = [
    'CodebaseIndexer',
    'RAGEngine', 
    'CacheRAGEngine',
    'CompanionIntelligence',
    'SOLUTION_REGISTRY'
]