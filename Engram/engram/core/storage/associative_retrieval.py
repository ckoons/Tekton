"""
ESR Associative Retrieval - Cross-backend context assembly for cognitive memory.

This module implements associative retrieval that searches across all backends
and assembles coherent context from different database types.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger("engram.storage.associative")


@dataclass
class MemoryFragment:
    """Represents a fragment of memory from any backend."""
    key: str
    content: Any
    source_backend: str
    relevance_score: float
    metadata: Dict[str, Any]
    retrieved_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'key': self.key,
            'content': self.content,
            'source': self.source_backend,
            'relevance': self.relevance_score,
            'metadata': self.metadata,
            'retrieved_at': self.retrieved_at.isoformat()
        }


class RelevanceScorer:
    """Scores relevance of memory fragments to queries."""
    
    @staticmethod
    def score_text_similarity(query: str, content: str) -> float:
        """
        Simple text similarity scoring.
        
        Args:
            query: Query string
            content: Content to score
            
        Returns:
            Similarity score (0-1)
        """
        if not query or not content:
            return 0.0
        
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Exact match
        if query_lower == content_lower:
            return 1.0
        
        # Contains query
        if query_lower in content_lower:
            return 0.8
        
        # Word overlap
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words & content_words)
        return min(overlap / len(query_words), 1.0) * 0.6
    
    @staticmethod
    def score_metadata_match(query_metadata: Dict[str, Any], 
                           content_metadata: Dict[str, Any]) -> float:
        """
        Score based on metadata matching.
        
        Args:
            query_metadata: Query metadata
            content_metadata: Content metadata
            
        Returns:
            Metadata match score (0-1)
        """
        if not query_metadata or not content_metadata:
            return 0.0
        
        score = 0.0
        matches = 0
        
        for key, value in query_metadata.items():
            if key in content_metadata:
                if content_metadata[key] == value:
                    matches += 1
        
        if query_metadata:
            score = matches / len(query_metadata)
        
        return score
    
    @staticmethod
    def score_temporal_relevance(query_time: datetime, 
                                content_time: datetime,
                                decay_hours: float = 24.0) -> float:
        """
        Score based on temporal proximity.
        
        Args:
            query_time: Time of query
            content_time: Time content was created/accessed
            decay_hours: Hours for relevance to decay by half
            
        Returns:
            Temporal relevance score (0-1)
        """
        if not content_time:
            return 0.5  # Neutral score if no time info
        
        time_diff = abs((query_time - content_time).total_seconds() / 3600)
        
        # Exponential decay
        score = np.exp(-time_diff / decay_hours)
        
        return float(score)
    
    @staticmethod
    def combine_scores(scores: Dict[str, float], weights: Dict[str, float] = None) -> float:
        """
        Combine multiple relevance scores.
        
        Args:
            scores: Dictionary of score types to scores
            weights: Optional weights for each score type
            
        Returns:
            Combined score (0-1)
        """
        if not scores:
            return 0.0
        
        default_weights = {
            'text': 0.4,
            'metadata': 0.2,
            'temporal': 0.2,
            'semantic': 0.2
        }
        
        weights = weights or default_weights
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for score_type, score in scores.items():
            weight = weights.get(score_type, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        
        return 0.0


class ContextMerger:
    """Merges memory fragments into coherent context."""
    
    @staticmethod
    def merge_fragments(fragments: List[MemoryFragment],
                       merge_strategy: str = 'ranked') -> Dict[str, Any]:
        """
        Merge memory fragments into unified context.
        
        Args:
            fragments: List of memory fragments
            merge_strategy: Strategy for merging ('ranked', 'grouped', 'narrative')
            
        Returns:
            Merged context
        """
        if not fragments:
            return {'status': 'no_memories', 'context': {}}
        
        if merge_strategy == 'ranked':
            return ContextMerger._merge_ranked(fragments)
        elif merge_strategy == 'grouped':
            return ContextMerger._merge_grouped(fragments)
        elif merge_strategy == 'narrative':
            return ContextMerger._merge_narrative(fragments)
        else:
            return ContextMerger._merge_ranked(fragments)
    
    @staticmethod
    def _merge_ranked(fragments: List[MemoryFragment]) -> Dict[str, Any]:
        """Merge by relevance ranking."""
        # Sort by relevance
        sorted_fragments = sorted(fragments, key=lambda f: f.relevance_score, reverse=True)
        
        context = {
            'primary_memories': [],
            'supporting_memories': [],
            'metadata': {}
        }
        
        # Top memories are primary
        for i, fragment in enumerate(sorted_fragments):
            memory_dict = fragment.to_dict()
            
            if i < 3:  # Top 3 are primary
                context['primary_memories'].append(memory_dict)
            else:
                context['supporting_memories'].append(memory_dict)
            
            # Merge metadata
            if fragment.metadata:
                for key, value in fragment.metadata.items():
                    if key not in context['metadata']:
                        context['metadata'][key] = []
                    if value not in context['metadata'][key]:
                        context['metadata'][key].append(value)
        
        return context
    
    @staticmethod
    def _merge_grouped(fragments: List[MemoryFragment]) -> Dict[str, Any]:
        """Merge by grouping similar memories."""
        # Group by source backend
        groups = {}
        for fragment in fragments:
            source = fragment.source_backend
            if source not in groups:
                groups[source] = []
            groups[source].append(fragment.to_dict())
        
        context = {
            'memory_groups': groups,
            'summary': {
                'total_memories': len(fragments),
                'sources': list(groups.keys()),
                'avg_relevance': np.mean([f.relevance_score for f in fragments])
            }
        }
        
        return context
    
    @staticmethod
    def _merge_narrative(fragments: List[MemoryFragment]) -> Dict[str, Any]:
        """Merge into narrative structure."""
        # Sort by time if available, otherwise by relevance
        try:
            sorted_fragments = sorted(fragments, key=lambda f: f.retrieved_at)
        except:
            sorted_fragments = sorted(fragments, key=lambda f: f.relevance_score, reverse=True)
        
        narrative = {
            'timeline': [],
            'themes': {},
            'connections': []
        }
        
        for fragment in sorted_fragments:
            # Add to timeline
            narrative['timeline'].append({
                'content': fragment.content,
                'time': fragment.retrieved_at.isoformat() if fragment.retrieved_at else None,
                'relevance': fragment.relevance_score
            })
            
            # Extract themes (simplified)
            if isinstance(fragment.content, str):
                words = fragment.content.lower().split()
                for word in words:
                    if len(word) > 5:  # Simple theme extraction
                        if word not in narrative['themes']:
                            narrative['themes'][word] = 0
                        narrative['themes'][word] += 1
        
        # Keep top themes
        if narrative['themes']:
            top_themes = sorted(narrative['themes'].items(), key=lambda x: x[1], reverse=True)[:5]
            narrative['themes'] = dict(top_themes)
        
        return narrative


class AssociativeRetrieval:
    """
    Implements associative retrieval across multiple backends.
    
    Enables finding related memories regardless of storage location.
    """
    
    def __init__(self, 
                 backends: Dict[str, Any],
                 scorer: Optional[RelevanceScorer] = None,
                 merger: Optional[ContextMerger] = None):
        """
        Initialize associative retrieval.
        
        Args:
            backends: Dictionary of backend name to backend instance
            scorer: Relevance scorer (uses default if None)
            merger: Context merger (uses default if None)
        """
        self.backends = backends
        self.scorer = scorer or RelevanceScorer()
        self.merger = merger or ContextMerger()
        
        # Cache for recent queries
        self.query_cache = {}
        self.cache_size = 100
        
        logger.info(f"Associative retrieval initialized with {len(backends)} backends")
    
    async def recall_similar(self,
                           query: str,
                           query_type: str = 'semantic',
                           metadata_filter: Optional[Dict[str, Any]] = None,
                           limit: int = 20,
                           ci_id: str = None) -> Dict[str, Any]:
        """
        Recall similar memories across all backends.
        
        Args:
            query: Query string
            query_type: Type of query ('semantic', 'exact', 'pattern')
            metadata_filter: Optional metadata filters
            limit: Maximum memories to retrieve
            ci_id: ID of CI recalling
            
        Returns:
            Assembled context from similar memories
        """
        # Check cache
        cache_key = f"{query}:{query_type}:{json.dumps(metadata_filter or {})}"
        if cache_key in self.query_cache:
            logger.debug(f"Cache hit for query: {query}")
            return self.query_cache[cache_key]
        
        # Gather fragments from all backends
        fragments = await self._gather_fragments(
            query, query_type, metadata_filter, limit
        )
        
        # Score relevance
        scored_fragments = self._score_fragments(
            fragments, query, metadata_filter
        )
        
        # Filter by score threshold
        threshold = 0.1  # Minimum relevance
        relevant_fragments = [f for f in scored_fragments if f.relevance_score >= threshold]
        
        # Sort and limit
        relevant_fragments.sort(key=lambda f: f.relevance_score, reverse=True)
        relevant_fragments = relevant_fragments[:limit]
        
        # Merge into context
        context = self.merger.merge_fragments(relevant_fragments)
        
        # Add query metadata
        context['query'] = {
            'text': query,
            'type': query_type,
            'filters': metadata_filter,
            'ci_id': ci_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache result
        self._update_cache(cache_key, context)
        
        logger.info(f"Recalled {len(relevant_fragments)} similar memories for query: {query}")
        
        return context
    
    async def _gather_fragments(self,
                               query: str,
                               query_type: str,
                               metadata_filter: Optional[Dict[str, Any]],
                               limit: int) -> List[MemoryFragment]:
        """Gather memory fragments from all backends."""
        fragments = []
        
        # Create tasks for parallel retrieval
        tasks = []
        for backend_name, backend in self.backends.items():
            task = self._retrieve_from_backend(
                backend_name, backend, query, query_type, metadata_filter, limit
            )
            tasks.append(task)
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Backend retrieval error: {result}")
            elif result:
                fragments.extend(result)
        
        return fragments
    
    async def _retrieve_from_backend(self,
                                    backend_name: str,
                                    backend: Any,
                                    query: str,
                                    query_type: str,
                                    metadata_filter: Optional[Dict[str, Any]],
                                    limit: int) -> List[MemoryFragment]:
        """Retrieve from a single backend."""
        fragments = []
        
        try:
            if backend_name == 'sql' and hasattr(backend, 'execute'):
                # SQL search
                sql_query = "SELECT * FROM memories WHERE content LIKE ? LIMIT ?"
                results = await backend.execute(sql_query, [f"%{query}%", limit])
                
                for row in results:
                    fragment = MemoryFragment(
                        key=row['key'],
                        content=json.loads(row['content']),
                        source_backend='sql',
                        relevance_score=0.0,  # Will be scored later
                        metadata={},
                        retrieved_at=datetime.now()
                    )
                    fragments.append(fragment)
            
            elif backend_name == 'document' and hasattr(backend, 'find'):
                # Document search
                doc_query = {'content': {'$regex': query}}
                if metadata_filter:
                    doc_query.update(metadata_filter)
                
                results = await backend.find(doc_query, limit=limit)
                
                for doc in results:
                    fragment = MemoryFragment(
                        key=doc.get('_id', ''),
                        content=doc.get('content'),
                        source_backend='document',
                        relevance_score=0.0,
                        metadata=doc.get('metadata', {}),
                        retrieved_at=datetime.now()
                    )
                    fragments.append(fragment)
            
            elif backend_name == 'vector' and hasattr(backend, 'search'):
                # Vector similarity search
                # Would need proper vector search implementation
                pass
            
            elif backend_name == 'graph' and hasattr(backend, 'search'):
                # Graph traversal search
                # Would need proper graph search implementation
                pass
            
            elif backend_name == 'kv' and hasattr(backend, 'get'):
                # Key-value can't really search, skip
                pass
            
        except Exception as e:
            logger.error(f"Error retrieving from {backend_name}: {e}")
        
        return fragments
    
    def _score_fragments(self,
                        fragments: List[MemoryFragment],
                        query: str,
                        metadata_filter: Optional[Dict[str, Any]]) -> List[MemoryFragment]:
        """Score fragments for relevance."""
        query_time = datetime.now()
        
        for fragment in fragments:
            scores = {}
            
            # Text similarity
            content_str = json.dumps(fragment.content) if isinstance(fragment.content, dict) else str(fragment.content)
            scores['text'] = self.scorer.score_text_similarity(query, content_str)
            
            # Metadata match
            if metadata_filter and fragment.metadata:
                scores['metadata'] = self.scorer.score_metadata_match(metadata_filter, fragment.metadata)
            
            # Temporal relevance (if we have time info)
            if fragment.retrieved_at:
                scores['temporal'] = self.scorer.score_temporal_relevance(query_time, fragment.retrieved_at)
            
            # Combine scores
            fragment.relevance_score = self.scorer.combine_scores(scores)
        
        return fragments
    
    def _update_cache(self, key: str, value: Any):
        """Update query cache with LRU eviction."""
        self.query_cache[key] = value
        
        # Evict oldest if cache too large
        if len(self.query_cache) > self.cache_size:
            # Simple FIFO eviction (could be improved to LRU)
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
    
    async def build_context(self,
                          task: str,
                          ci_id: str = None,
                          max_memories: int = 50) -> Dict[str, Any]:
        """
        Build comprehensive context for a task.
        
        Args:
            task: Task description
            ci_id: ID of CI requesting context
            max_memories: Maximum memories to include
            
        Returns:
            Assembled context for task
        """
        # Multi-query approach for comprehensive context
        queries = [
            (task, 'semantic'),  # Main task
            (task.split()[0] if task.split() else task, 'pattern'),  # First word
            (task, 'exact')  # Exact matches
        ]
        
        all_fragments = []
        seen_keys = set()
        
        for query, query_type in queries:
            context = await self.recall_similar(
                query, query_type, None, max_memories // len(queries), ci_id
            )
            
            # Extract fragments from context
            for memory in context.get('primary_memories', []):
                if memory['key'] not in seen_keys:
                    fragment = MemoryFragment(
                        key=memory['key'],
                        content=memory['content'],
                        source_backend=memory['source'],
                        relevance_score=memory['relevance'],
                        metadata=memory.get('metadata', {}),
                        retrieved_at=datetime.fromisoformat(memory['retrieved_at'])
                    )
                    all_fragments.append(fragment)
                    seen_keys.add(memory['key'])
        
        # Build comprehensive context
        comprehensive_context = self.merger.merge_fragments(all_fragments, 'narrative')
        comprehensive_context['task'] = task
        comprehensive_context['ci_id'] = ci_id
        
        return comprehensive_context