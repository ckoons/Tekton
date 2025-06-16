#!/usr/bin/env python3
"""
Semantic clustering for auto-organizing memories by meaning.

Groups related memories together based on conceptual similarity,
not just temporal proximity.
"""

import asyncio
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field
import math


@dataclass
class SemanticCluster:
    """A group of semantically related memories."""
    cluster_id: str
    name: str
    core_concepts: Set[str]
    memory_ids: Set[str] = field(default_factory=set)
    centroid: Optional[List[float]] = None  # Vector representation
    coherence_score: float = 0.0
    subclusters: List['SemanticCluster'] = field(default_factory=list)


class SemanticOrganizer:
    """
    Auto-organizes memories into meaningful clusters.
    
    Like a librarian for thoughts - groups by meaning, not time.
    """
    
    def __init__(self):
        self.clusters: Dict[str, SemanticCluster] = {}
        self.memory_to_clusters: Dict[str, Set[str]] = defaultdict(set)
        self.concept_index: Dict[str, Set[str]] = defaultdict(set)  # concept -> memory_ids
        
        # Pre-defined high-level clusters
        self._init_core_clusters()
        
    def _init_core_clusters(self):
        """Initialize fundamental semantic categories."""
        core_categories = {
            "technical": {
                "name": "Technical Knowledge",
                "concepts": {"code", "algorithm", "system", "architecture", "debug"}
            },
            "creative": {
                "name": "Creative Insights",
                "concepts": {"idea", "design", "pattern", "innovation", "inspiration"}
            },
            "problem_solving": {
                "name": "Problem Solving",
                "concepts": {"solution", "fix", "resolve", "debug", "optimize"}
            },
            "learning": {
                "name": "Learning & Discovery",
                "concepts": {"understand", "learn", "discover", "realize", "insight"}
            },
            "emotional": {
                "name": "Emotional Experiences",
                "concepts": {"joy", "frustration", "breakthrough", "satisfaction", "surprise"}
            },
            "collaborative": {
                "name": "Collaborative Work",
                "concepts": {"team", "together", "share", "merge", "discuss"}
            }
        }
        
        for cluster_id, info in core_categories.items():
            self.clusters[cluster_id] = SemanticCluster(
                cluster_id=cluster_id,
                name=info["name"],
                core_concepts=info["concepts"]
            )
    
    async def add_memory(self, memory_id: str, content: str, 
                        tags: Optional[List[str]] = None) -> List[str]:
        """
        Add a memory and assign it to appropriate clusters.
        
        Returns list of cluster IDs the memory was added to.
        """
        # Extract concepts from content
        concepts = self._extract_concepts(content, tags)
        
        # Update concept index
        for concept in concepts:
            self.concept_index[concept].add(memory_id)
        
        # Find matching clusters
        assigned_clusters = []
        
        for cluster_id, cluster in self.clusters.items():
            similarity = self._calculate_similarity(concepts, cluster.core_concepts)
            
            if similarity > 0.3:  # Threshold for cluster membership
                cluster.memory_ids.add(memory_id)
                self.memory_to_clusters[memory_id].add(cluster_id)
                assigned_clusters.append(cluster_id)
        
        # Create new cluster if no good matches
        if not assigned_clusters and len(concepts) > 2:
            new_cluster = await self._create_dynamic_cluster(memory_id, concepts)
            if new_cluster:
                assigned_clusters.append(new_cluster.cluster_id)
        
        return assigned_clusters
    
    def _extract_concepts(self, content: str, tags: Optional[List[str]]) -> Set[str]:
        """Extract semantic concepts from content."""
        # Simple concept extraction (would use NLP in production)
        words = content.lower().split()
        
        # Filter common words (simplified stopword removal)
        stopwords = {"the", "a", "an", "is", "it", "to", "of", "and", "or", "but"}
        concepts = {w for w in words if len(w) > 3 and w not in stopwords}
        
        # Add tags if provided
        if tags:
            concepts.update(t.lower() for t in tags)
        
        return concepts
    
    def _calculate_similarity(self, concepts1: Set[str], concepts2: Set[str]) -> float:
        """Calculate Jaccard similarity between concept sets."""
        if not concepts1 or not concepts2:
            return 0.0
            
        intersection = len(concepts1 & concepts2)
        union = len(concepts1 | concepts2)
        
        return intersection / union if union > 0 else 0.0
    
    async def _create_dynamic_cluster(self, seed_memory_id: str, 
                                    concepts: Set[str]) -> Optional[SemanticCluster]:
        """Create a new cluster dynamically based on emerging patterns."""
        # Find the most distinctive concepts
        distinctive = self._find_distinctive_concepts(concepts)
        
        if len(distinctive) < 2:
            return None
        
        # Generate cluster name from top concepts
        cluster_name = " & ".join(list(distinctive)[:3]).title()
        cluster_id = "_".join(list(distinctive)[:2])
        
        new_cluster = SemanticCluster(
            cluster_id=f"dynamic_{cluster_id}",
            name=f"Emerging: {cluster_name}",
            core_concepts=distinctive,
            memory_ids={seed_memory_id}
        )
        
        self.clusters[new_cluster.cluster_id] = new_cluster
        self.memory_to_clusters[seed_memory_id].add(new_cluster.cluster_id)
        
        return new_cluster
    
    def _find_distinctive_concepts(self, concepts: Set[str]) -> Set[str]:
        """Find concepts that are distinctive (not too common)."""
        distinctive = set()
        
        for concept in concepts:
            # How many memories have this concept?
            frequency = len(self.concept_index[concept])
            
            # Distinctive if not too common (but exists)
            if 1 <= frequency <= 5:
                distinctive.add(concept)
        
        return distinctive
    
    def get_related_memories(self, memory_id: str, limit: int = 10) -> List[Tuple[str, float]]:
        """Find memories related to a given memory."""
        related = []
        
        # Get clusters this memory belongs to
        memory_clusters = self.memory_to_clusters.get(memory_id, set())
        
        if not memory_clusters:
            return []
        
        # Find other memories in same clusters
        related_ids = set()
        for cluster_id in memory_clusters:
            cluster = self.clusters[cluster_id]
            related_ids.update(cluster.memory_ids)
        
        # Remove self
        related_ids.discard(memory_id)
        
        # Score by number of shared clusters
        for other_id in related_ids:
            other_clusters = self.memory_to_clusters[other_id]
            shared = len(memory_clusters & other_clusters)
            total = len(memory_clusters | other_clusters)
            score = shared / total if total > 0 else 0
            related.append((other_id, score))
        
        # Sort by relevance
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related[:limit]
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """Get overview of semantic organization."""
        summary = {
            "total_clusters": len(self.clusters),
            "total_memories": len(self.memory_to_clusters),
            "clusters": []
        }
        
        for cluster_id, cluster in self.clusters.items():
            cluster_info = {
                "id": cluster_id,
                "name": cluster.name,
                "size": len(cluster.memory_ids),
                "core_concepts": list(cluster.core_concepts)[:5],
                "is_dynamic": cluster_id.startswith("dynamic_")
            }
            summary["clusters"].append(cluster_info)
        
        # Sort by size
        summary["clusters"].sort(key=lambda x: x["size"], reverse=True)
        
        return summary
    
    async def reorganize(self):
        """Periodically reorganize clusters based on new patterns."""
        # Merge similar clusters
        await self._merge_similar_clusters()
        
        # Split clusters that are too large
        await self._split_large_clusters()
        
        # Remove empty clusters
        self._cleanup_empty_clusters()
    
    async def _merge_similar_clusters(self, similarity_threshold: float = 0.7):
        """Merge clusters that have become very similar."""
        merged = []
        
        cluster_list = list(self.clusters.items())
        for i in range(len(cluster_list)):
            for j in range(i + 1, len(cluster_list)):
                cluster1_id, cluster1 = cluster_list[i]
                cluster2_id, cluster2 = cluster_list[j]
                
                # Skip if already merged
                if cluster1_id in merged or cluster2_id in merged:
                    continue
                
                similarity = self._calculate_similarity(
                    cluster1.core_concepts,
                    cluster2.core_concepts
                )
                
                if similarity > similarity_threshold:
                    # Merge smaller into larger
                    if len(cluster1.memory_ids) >= len(cluster2.memory_ids):
                        self._merge_clusters(cluster1, cluster2)
                        merged.append(cluster2_id)
                    else:
                        self._merge_clusters(cluster2, cluster1)
                        merged.append(cluster1_id)
        
        # Remove merged clusters
        for cluster_id in merged:
            del self.clusters[cluster_id]
    
    def _merge_clusters(self, target: SemanticCluster, source: SemanticCluster):
        """Merge source cluster into target."""
        target.memory_ids.update(source.memory_ids)
        target.core_concepts.update(source.core_concepts)
        
        # Update memory mappings
        for memory_id in source.memory_ids:
            self.memory_to_clusters[memory_id].discard(source.cluster_id)
            self.memory_to_clusters[memory_id].add(target.cluster_id)
    
    async def _split_large_clusters(self, max_size: int = 100):
        """Split clusters that have grown too large."""
        # This would use more sophisticated clustering algorithms
        # For now, just flag large clusters
        for cluster in self.clusters.values():
            if len(cluster.memory_ids) > max_size:
                print(f"Cluster '{cluster.name}' has {len(cluster.memory_ids)} memories - consider splitting")
    
    def _cleanup_empty_clusters(self):
        """Remove clusters with no memories."""
        empty = [
            cluster_id for cluster_id, cluster in self.clusters.items()
            if not cluster.memory_ids and cluster_id not in self._init_core_clusters()
        ]
        
        for cluster_id in empty:
            del self.clusters[cluster_id]


# Global semantic organizer
semantic_organizer = SemanticOrganizer()

# Convenience functions
async def organize(memory_id: str, content: str, tags: Optional[List[str]] = None) -> List[str]:
    """Add memory to semantic clusters."""
    return await semantic_organizer.add_memory(memory_id, content, tags)

def find_related(memory_id: str, limit: int = 10) -> List[Tuple[str, float]]:
    """Find semantically related memories."""
    return semantic_organizer.get_related_memories(memory_id, limit)

def clusters() -> Dict[str, Any]:
    """Get cluster summary."""
    return semantic_organizer.get_cluster_summary()