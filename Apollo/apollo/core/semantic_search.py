#!/usr/bin/env python3
"""
Semantic Memory Search for Apollo

Provides both local (fast) and external (high-quality) semantic search.
This enables natural memory retrieval based on meaning, not just keywords.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import math

logger = logging.getLogger(__name__)


class SemanticMemorySearch:
    """
    Semantic search for memories using dual approach:
    1. Local: Fast, private, good enough for most queries
    2. External: Higher quality for critical decisions
    """

    def __init__(self):
        """Initialize semantic search system."""
        self.use_external = False  # Start with local only
        self.confidence_threshold = 0.7  # When to use external

    async def search(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        max_results: int = 10,
        use_external: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories semantically.

        Args:
            query: Search query
            memories: List of memories to search
            max_results: Maximum results to return
            use_external: Force external search (None = auto-decide)

        Returns:
            Ranked list of relevant memories
        """
        if not memories:
            return []

        # Decide search strategy
        if use_external is None:
            use_external = self._should_use_external(query, memories)

        if use_external:
            # Use external high-quality search
            return await self._external_semantic_search(query, memories, max_results)
        else:
            # Use local fast search
            return self._local_semantic_search(query, memories, max_results)

    def _should_use_external(self, query: str, memories: List[Dict]) -> bool:
        """
        Decide if we need external search.

        Use external for:
        - High-stakes queries (bug fixes, critical decisions)
        - Low confidence from local search
        - Explicit quality requests
        """
        query_lower = query.lower()

        # High-stakes keywords
        critical_terms = [
            'bug', 'fix', 'error', 'crash', 'security', 'critical',
            'production', 'urgent', 'important', 'careful', 'precise'
        ]

        for term in critical_terms:
            if term in query_lower:
                logger.info(f"Using external search due to critical term: {term}")
                return True

        # Check query complexity
        if len(query.split()) > 20:
            logger.info("Using external search due to complex query")
            return True

        return False

    def _local_semantic_search(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Fast local semantic search using TF-IDF and cosine similarity.

        This is good enough for most queries and keeps data private.
        """
        # Tokenize query
        query_tokens = self._tokenize(query.lower())

        # Score each memory
        scored_memories = []
        for memory in memories:
            content = str(memory.get('content', ''))
            score = self._calculate_similarity(query_tokens, content)

            # Add metadata boost
            if 'relevance' in memory:
                score *= (1 + memory['relevance'])

            scored_memories.append((score, memory))

        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored_memories[:max_results]]

    async def _external_semantic_search(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        High-quality external semantic search.

        Would use embeddings API or external service.
        For now, falls back to enhanced local search.
        """
        try:
            # TODO: Integrate with external embedding service
            # For now, use enhanced local search with better preprocessing
            logger.info("External search not configured, using enhanced local")

            # Preprocess for better quality
            query = self._enhance_query(query)

            # Use local search with enhancements
            results = self._local_semantic_search(query, memories, max_results * 2)

            # Rerank based on semantic clusters
            return self._rerank_by_clusters(query, results, max_results)

        except Exception as e:
            logger.error(f"External search failed: {e}, falling back to local")
            return self._local_semantic_search(query, memories, max_results)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for similarity calculation."""
        # Remove punctuation and split
        tokens = re.findall(r'\b\w+\b', text.lower())

        # Remove stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'with', 'from', 'by', 'of', 'as', 'is',
            'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'it', 'its'
        }

        return [t for t in tokens if t not in stopwords and len(t) > 2]

    def _calculate_similarity(self, query_tokens: List[str], content: str) -> float:
        """
        Calculate similarity between query and content.

        Uses TF-IDF-like scoring with cosine similarity.
        """
        if not query_tokens or not content:
            return 0.0

        content_tokens = self._tokenize(content.lower())
        if not content_tokens:
            return 0.0

        # Calculate term frequency
        query_freq = Counter(query_tokens)
        content_freq = Counter(content_tokens)

        # Find common terms
        common_terms = set(query_tokens) & set(content_tokens)
        if not common_terms:
            return 0.0

        # Calculate similarity score
        score = 0.0
        query_norm = 0.0
        content_norm = 0.0

        for term in set(query_tokens) | set(content_tokens):
            q_count = query_freq.get(term, 0)
            c_count = content_freq.get(term, 0)

            # TF-IDF weight (simplified - no global IDF)
            q_weight = math.log(1 + q_count)
            c_weight = math.log(1 + c_count)

            score += q_weight * c_weight
            query_norm += q_weight ** 2
            content_norm += c_weight ** 2

        # Normalize (cosine similarity)
        if query_norm > 0 and content_norm > 0:
            score = score / (math.sqrt(query_norm) * math.sqrt(content_norm))

        return score

    def _enhance_query(self, query: str) -> str:
        """
        Enhance query for better semantic matching.

        Adds synonyms and related terms.
        """
        enhancements = {
            'bug': 'bug error issue problem defect fault',
            'fix': 'fix repair resolve solve patch correct',
            'memory': 'memory recall remember storage engram',
            'test': 'test verify validate check confirm',
            'implement': 'implement create build develop make construct'
        }

        enhanced = query
        for key, synonyms in enhancements.items():
            if key in query.lower():
                enhanced += f" {synonyms}"

        return enhanced

    def _rerank_by_clusters(
        self,
        query: str,
        results: List[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Rerank results by semantic clusters.

        Groups similar memories and selects diverse results.
        """
        if len(results) <= max_results:
            return results

        # Simple clustering by content similarity
        clusters = []
        for memory in results:
            # Find best matching cluster
            best_cluster = None
            best_similarity = 0.0

            for cluster in clusters:
                # Compare with cluster representative
                rep = cluster[0]
                sim = self._calculate_similarity(
                    self._tokenize(str(memory.get('content', ''))),
                    str(rep.get('content', ''))
                )

                if sim > 0.7 and sim > best_similarity:
                    best_cluster = cluster
                    best_similarity = sim

            if best_cluster:
                best_cluster.append(memory)
            else:
                clusters.append([memory])

        # Select from clusters for diversity
        reranked = []
        cluster_index = 0

        while len(reranked) < max_results and clusters:
            if cluster_index >= len(clusters):
                cluster_index = 0

            cluster = clusters[cluster_index]
            if cluster:
                reranked.append(cluster.pop(0))
                if not cluster:
                    clusters.pop(cluster_index)
                else:
                    cluster_index += 1
            else:
                cluster_index += 1

        return reranked[:max_results]


# Singleton instance
_semantic_search = SemanticMemorySearch()


async def semantic_memory_search(
    query: str,
    memories: List[Dict[str, Any]],
    max_results: int = 10,
    use_external: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Public interface for semantic memory search.

    Args:
        query: Search query
        memories: Memories to search
        max_results: Maximum results
        use_external: Force external search

    Returns:
        Ranked list of relevant memories
    """
    return await _semantic_search.search(query, memories, max_results, use_external)