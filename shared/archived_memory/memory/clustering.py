"""
Semantic Clustering for Memory System
Groups related memories for improved retrieval and understanding.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import hashlib
import json
import math

logger = logging.getLogger(__name__)


class ClusterType(Enum):
    """Types of memory clusters."""
    TOPIC = "topic"           # Topical grouping
    TEMPORAL = "temporal"     # Time-based grouping  
    SEMANTIC = "semantic"     # Meaning-based grouping
    RELATIONAL = "relational" # Relationship-based
    CONTEXTUAL = "contextual" # Context-based
    PATTERN = "pattern"       # Pattern-based


@dataclass
class MemoryCluster:
    """Represents a cluster of related memories."""
    id: str
    type: ClusterType
    centroid: Dict[str, Any]  # Representative memory
    members: List[str]         # Memory IDs in cluster
    coherence: float          # Cluster coherence score
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    
    def add_member(self, memory_id: str):
        """Add memory to cluster."""
        if memory_id not in self.members:
            self.members.append(memory_id)
            self.updated_at = datetime.now()
    
    def remove_member(self, memory_id: str):
        """Remove memory from cluster."""
        if memory_id in self.members:
            self.members.remove(memory_id)
            self.updated_at = datetime.now()
    
    def size(self) -> int:
        """Get cluster size."""
        return len(self.members)
    
    def age(self) -> timedelta:
        """Get cluster age."""
        return datetime.now() - self.created_at


class SemanticClusterer:
    """
    Clusters memories based on semantic similarity.
    
    Features:
    - Multiple clustering algorithms
    - Dynamic cluster management
    - Cross-cluster relationships
    - Cluster evolution tracking
    """
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.clusters: Dict[str, MemoryCluster] = {}
        self.memory_to_clusters: Dict[str, Set[str]] = {}
        self.cluster_relationships: Dict[Tuple[str, str], float] = {}
        
        # Clustering parameters
        self.min_cluster_size = 3
        self.max_cluster_size = 50
        self.similarity_threshold = 0.7
        self.coherence_threshold = 0.6
        
    async def cluster_memories(
        self,
        memories: List[Dict[str, Any]],
        cluster_type: ClusterType = ClusterType.SEMANTIC
    ) -> List[MemoryCluster]:
        """
        Cluster a set of memories.
        
        Args:
            memories: List of memory items to cluster
            cluster_type: Type of clustering to perform
        
        Returns:
            List of created clusters
        """
        if not memories:
            return []
        
        # Extract features for clustering
        features = await self._extract_features(memories, cluster_type)
        
        # Perform clustering based on type
        if cluster_type == ClusterType.SEMANTIC:
            clusters = await self._semantic_clustering(memories, features)
        elif cluster_type == ClusterType.TEMPORAL:
            clusters = await self._temporal_clustering(memories, features)
        elif cluster_type == ClusterType.TOPIC:
            clusters = await self._topic_clustering(memories, features)
        elif cluster_type == ClusterType.PATTERN:
            clusters = await self._pattern_clustering(memories, features)
        else:
            clusters = await self._generic_clustering(memories, features)
        
        # Filter and validate clusters
        valid_clusters = self._validate_clusters(clusters)
        
        # Store clusters
        for cluster in valid_clusters:
            self.clusters[cluster.id] = cluster
            for memory_id in cluster.members:
                if memory_id not in self.memory_to_clusters:
                    self.memory_to_clusters[memory_id] = set()
                self.memory_to_clusters[memory_id].add(cluster.id)
        
        # Discover relationships between clusters
        await self._discover_cluster_relationships(valid_clusters)
        
        return valid_clusters
    
    async def _extract_features(
        self,
        memories: List[Dict],
        cluster_type: ClusterType
    ) -> List[Dict]:
        """Extract features for clustering."""
        features = []
        
        for memory in memories:
            if cluster_type == ClusterType.SEMANTIC:
                feature = self._extract_semantic_features(memory)
            elif cluster_type == ClusterType.TEMPORAL:
                feature = self._extract_temporal_features(memory)
            elif cluster_type == ClusterType.TOPIC:
                feature = self._extract_topic_features(memory)
            elif cluster_type == ClusterType.PATTERN:
                feature = self._extract_pattern_features(memory)
            else:
                feature = self._extract_generic_features(memory)
            
            features.append(feature)
        
        return features
    
    async def _semantic_clustering(
        self,
        memories: List[Dict],
        features: List[Dict]
    ) -> List[MemoryCluster]:
        """Perform semantic clustering."""
        clusters = []
        clustered = set()
        
        for i, memory in enumerate(memories):
            if i in clustered:
                continue
            
            # Start new cluster
            cluster_members = [i]
            clustered.add(i)
            
            # Find similar memories
            for j, other_memory in enumerate(memories[i+1:], i+1):
                if j in clustered:
                    continue
                
                similarity = self._calculate_semantic_similarity(
                    features[i],
                    features[j]
                )
                
                if similarity >= self.similarity_threshold:
                    cluster_members.append(j)
                    clustered.add(j)
                
                # Stop if cluster is getting too large
                if len(cluster_members) >= self.max_cluster_size:
                    break
            
            # Create cluster if it meets minimum size
            if len(cluster_members) >= self.min_cluster_size:
                cluster = self._create_cluster(
                    ClusterType.SEMANTIC,
                    [memories[idx] for idx in cluster_members],
                    features[cluster_members[0]]  # Use first as centroid
                )
                clusters.append(cluster)
        
        return clusters
    
    async def _temporal_clustering(
        self,
        memories: List[Dict],
        features: List[Dict]
    ) -> List[MemoryCluster]:
        """Cluster memories by time periods."""
        clusters = []
        
        # Sort by timestamp
        sorted_memories = sorted(
            zip(memories, features),
            key=lambda x: x[1].get('timestamp', 0)
        )
        
        # Group by time windows
        time_window = timedelta(minutes=30)
        current_cluster = []
        cluster_start = None
        
        for memory, feature in sorted_memories:
            timestamp = datetime.fromisoformat(
                feature.get('timestamp', datetime.now().isoformat())
            )
            
            if cluster_start is None:
                cluster_start = timestamp
                current_cluster = [(memory, feature)]
            elif timestamp - cluster_start <= time_window:
                current_cluster.append((memory, feature))
            else:
                # Complete current cluster
                if len(current_cluster) >= self.min_cluster_size:
                    cluster = self._create_cluster(
                        ClusterType.TEMPORAL,
                        [m for m, _ in current_cluster],
                        current_cluster[len(current_cluster)//2][1]  # Middle as centroid
                    )
                    clusters.append(cluster)
                
                # Start new cluster
                cluster_start = timestamp
                current_cluster = [(memory, feature)]
        
        # Don't forget last cluster
        if len(current_cluster) >= self.min_cluster_size:
            cluster = self._create_cluster(
                ClusterType.TEMPORAL,
                [m for m, _ in current_cluster],
                current_cluster[len(current_cluster)//2][1]
            )
            clusters.append(cluster)
        
        return clusters
    
    async def _topic_clustering(
        self,
        memories: List[Dict],
        features: List[Dict]
    ) -> List[MemoryCluster]:
        """Cluster memories by topic."""
        # Extract topics from memories
        topics = {}
        
        for i, (memory, feature) in enumerate(zip(memories, features)):
            topic = self._extract_topic(memory, feature)
            if topic not in topics:
                topics[topic] = []
            topics[topic].append((i, memory, feature))
        
        # Create clusters from topics
        clusters = []
        for topic, items in topics.items():
            if len(items) >= self.min_cluster_size:
                cluster = self._create_cluster(
                    ClusterType.TOPIC,
                    [item[1] for item in items],
                    items[0][2],  # First feature as centroid
                    metadata={'topic': topic}
                )
                clusters.append(cluster)
        
        return clusters
    
    async def _pattern_clustering(
        self,
        memories: List[Dict],
        features: List[Dict]
    ) -> List[MemoryCluster]:
        """Cluster memories by patterns."""
        patterns = self._discover_patterns(memories, features)
        clusters = []
        
        for pattern_id, pattern_info in patterns.items():
            if len(pattern_info['members']) >= self.min_cluster_size:
                cluster = self._create_cluster(
                    ClusterType.PATTERN,
                    [memories[i] for i in pattern_info['members']],
                    pattern_info['pattern'],
                    metadata={'pattern_type': pattern_info['type']}
                )
                clusters.append(cluster)
        
        return clusters
    
    async def _generic_clustering(
        self,
        memories: List[Dict],
        features: List[Dict]
    ) -> List[MemoryCluster]:
        """Generic clustering fallback."""
        # Simple similarity-based clustering
        return await self._semantic_clustering(memories, features)
    
    def _calculate_semantic_similarity(
        self,
        features1: Dict,
        features2: Dict
    ) -> float:
        """Calculate semantic similarity between features."""
        # Simplified cosine similarity on text content
        text1 = str(features1.get('content', ''))
        text2 = str(features2.get('content', ''))
        
        if not text1 or not text2:
            return 0.0
        
        # Simple word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_semantic_features(self, memory: Dict) -> Dict:
        """Extract semantic features from memory."""
        return {
            'content': memory.get('content', ''),
            'type': memory.get('type', ''),
            'timestamp': memory.get('timestamp', datetime.now().isoformat()),
            'keywords': self._extract_keywords(memory)
        }
    
    def _extract_temporal_features(self, memory: Dict) -> Dict:
        """Extract temporal features."""
        return {
            'timestamp': memory.get('timestamp', datetime.now().isoformat()),
            'duration': memory.get('duration', 0),
            'frequency': memory.get('frequency', 1)
        }
    
    def _extract_topic_features(self, memory: Dict) -> Dict:
        """Extract topic features."""
        content = str(memory.get('content', ''))
        return {
            'topic': self._identify_topic(content),
            'subtopics': self._identify_subtopics(content),
            'domain': memory.get('domain', 'general')
        }
    
    def _extract_pattern_features(self, memory: Dict) -> Dict:
        """Extract pattern features."""
        return {
            'pattern_type': self._identify_pattern_type(memory),
            'frequency': memory.get('frequency', 1),
            'confidence': memory.get('confidence', 0.5)
        }
    
    def _extract_generic_features(self, memory: Dict) -> Dict:
        """Extract generic features."""
        return {
            'id': memory.get('id', ''),
            'content': memory.get('content', ''),
            'metadata': memory.get('metadata', {})
        }
    
    def _extract_keywords(self, memory: Dict) -> List[str]:
        """Extract keywords from memory."""
        content = str(memory.get('content', ''))
        # Simple keyword extraction
        words = content.lower().split()
        # Filter common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        return [w for w in words if w not in stopwords and len(w) > 3][:10]
    
    def _extract_topic(self, memory: Dict, features: Dict) -> str:
        """Extract primary topic."""
        return features.get('topic', 'general')
    
    def _identify_topic(self, content: str) -> str:
        """Identify topic from content."""
        # Simplified topic detection
        topics = {
            'technical': ['code', 'function', 'bug', 'error', 'debug'],
            'analysis': ['analyze', 'data', 'metric', 'measure', 'evaluate'],
            'conversation': ['hello', 'thanks', 'please', 'help', 'question'],
            'planning': ['plan', 'strategy', 'goal', 'objective', 'task']
        }
        
        content_lower = content.lower()
        for topic, keywords in topics.items():
            if any(keyword in content_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    def _identify_subtopics(self, content: str) -> List[str]:
        """Identify subtopics."""
        # Placeholder implementation
        return []
    
    def _identify_pattern_type(self, memory: Dict) -> str:
        """Identify pattern type in memory."""
        if 'error' in str(memory.get('content', '')).lower():
            return 'error_pattern'
        elif 'success' in str(memory.get('content', '')).lower():
            return 'success_pattern'
        else:
            return 'general_pattern'
    
    def _discover_patterns(
        self,
        memories: List[Dict],
        features: List[Dict]
    ) -> Dict[str, Dict]:
        """Discover patterns in memories."""
        patterns = {}
        
        # Group by pattern type
        for i, feature in enumerate(features):
            pattern_type = feature.get('pattern_type', 'unknown')
            if pattern_type not in patterns:
                patterns[pattern_type] = {
                    'type': pattern_type,
                    'pattern': feature,
                    'members': []
                }
            patterns[pattern_type]['members'].append(i)
        
        return patterns
    
    def _create_cluster(
        self,
        cluster_type: ClusterType,
        members: List[Dict],
        centroid: Dict,
        metadata: Dict = None
    ) -> MemoryCluster:
        """Create a new cluster."""
        # Generate cluster ID
        cluster_id = self._generate_cluster_id(cluster_type, members)
        
        # Calculate coherence
        coherence = self._calculate_coherence(members)
        
        # Extract member IDs
        member_ids = [m.get('id', str(i)) for i, m in enumerate(members)]
        
        return MemoryCluster(
            id=cluster_id,
            type=cluster_type,
            centroid=centroid,
            members=member_ids,
            coherence=coherence,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {}
        )
    
    def _generate_cluster_id(
        self,
        cluster_type: ClusterType,
        members: List[Dict]
    ) -> str:
        """Generate unique cluster ID."""
        # Create hash from cluster content
        content = f"{cluster_type.value}_{len(members)}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_coherence(self, members: List[Dict]) -> float:
        """Calculate cluster coherence score."""
        if len(members) < 2:
            return 1.0
        
        # Calculate average pairwise similarity
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(members)):
            for j in range(i + 1, min(i + 5, len(members))):  # Sample for efficiency
                features_i = self._extract_semantic_features(members[i])
                features_j = self._extract_semantic_features(members[j])
                similarity = self._calculate_semantic_similarity(features_i, features_j)
                total_similarity += similarity
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0
    
    def _validate_clusters(self, clusters: List[MemoryCluster]) -> List[MemoryCluster]:
        """Validate and filter clusters."""
        valid = []
        
        for cluster in clusters:
            # Check size constraints
            if cluster.size() < self.min_cluster_size:
                continue
            if cluster.size() > self.max_cluster_size:
                # Split large cluster
                # For now, just truncate
                cluster.members = cluster.members[:self.max_cluster_size]
            
            # Check coherence
            if cluster.coherence < self.coherence_threshold:
                logger.warning(
                    f"Cluster {cluster.id} has low coherence: {cluster.coherence:.2f}"
                )
                # Still include but mark
                cluster.metadata['low_coherence'] = True
            
            valid.append(cluster)
        
        return valid
    
    async def _discover_cluster_relationships(
        self,
        clusters: List[MemoryCluster]
    ):
        """Discover relationships between clusters."""
        for i, cluster1 in enumerate(clusters):
            for cluster2 in clusters[i+1:]:
                relationship_strength = self._calculate_cluster_relationship(
                    cluster1,
                    cluster2
                )
                
                if relationship_strength > 0.3:  # Threshold for meaningful relationship
                    self.cluster_relationships[(cluster1.id, cluster2.id)] = relationship_strength
                    self.cluster_relationships[(cluster2.id, cluster1.id)] = relationship_strength
    
    def _calculate_cluster_relationship(
        self,
        cluster1: MemoryCluster,
        cluster2: MemoryCluster
    ) -> float:
        """Calculate relationship strength between clusters."""
        # Compare centroids
        similarity = self._calculate_semantic_similarity(
            cluster1.centroid,
            cluster2.centroid
        )
        
        # Adjust for cluster types
        if cluster1.type == cluster2.type:
            similarity *= 1.2
        
        # Temporal proximity for temporal clusters
        if cluster1.type == ClusterType.TEMPORAL and cluster2.type == ClusterType.TEMPORAL:
            time1 = datetime.fromisoformat(cluster1.centroid.get('timestamp', datetime.now().isoformat()))
            time2 = datetime.fromisoformat(cluster2.centroid.get('timestamp', datetime.now().isoformat()))
            time_diff = abs((time1 - time2).total_seconds())
            if time_diff < 3600:  # Within an hour
                similarity *= 1.5
        
        return min(similarity, 1.0)
    
    async def find_related_clusters(
        self,
        cluster_id: str,
        limit: int = 5
    ) -> List[Tuple[MemoryCluster, float]]:
        """Find clusters related to given cluster."""
        if cluster_id not in self.clusters:
            return []
        
        related = []
        
        for (id1, id2), strength in self.cluster_relationships.items():
            if id1 == cluster_id and id2 in self.clusters:
                related.append((self.clusters[id2], strength))
        
        # Sort by relationship strength
        related.sort(key=lambda x: x[1], reverse=True)
        
        return related[:limit]
    
    async def get_cluster_summary(self, cluster_id: str) -> Dict[str, Any]:
        """Get summary of a cluster."""
        if cluster_id not in self.clusters:
            return {}
        
        cluster = self.clusters[cluster_id]
        related = await self.find_related_clusters(cluster_id, 3)
        
        return {
            'id': cluster.id,
            'type': cluster.type.value,
            'size': cluster.size(),
            'coherence': cluster.coherence,
            'age': str(cluster.age()),
            'metadata': cluster.metadata,
            'related_clusters': [
                {'id': c.id, 'strength': s}
                for c, s in related
            ]
        }
    
    async def merge_clusters(
        self,
        cluster_id1: str,
        cluster_id2: str
    ) -> Optional[MemoryCluster]:
        """Merge two clusters into one."""
        if cluster_id1 not in self.clusters or cluster_id2 not in self.clusters:
            return None
        
        cluster1 = self.clusters[cluster_id1]
        cluster2 = self.clusters[cluster_id2]
        
        # Check if merge makes sense
        relationship = self.cluster_relationships.get((cluster_id1, cluster_id2), 0)
        if relationship < 0.5:
            logger.warning(f"Clusters have weak relationship: {relationship}")
        
        # Create merged cluster
        merged_members = cluster1.members + cluster2.members
        
        # Remove duplicates
        merged_members = list(set(merged_members))
        
        # Choose centroid from larger cluster
        if cluster1.size() >= cluster2.size():
            centroid = cluster1.centroid
            base_cluster = cluster1
        else:
            centroid = cluster2.centroid
            base_cluster = cluster2
        
        # Create new cluster
        merged = MemoryCluster(
            id=self._generate_cluster_id(base_cluster.type, merged_members),
            type=base_cluster.type,
            centroid=centroid,
            members=merged_members[:self.max_cluster_size],  # Respect size limit
            coherence=(cluster1.coherence + cluster2.coherence) / 2,
            created_at=min(cluster1.created_at, cluster2.created_at),
            updated_at=datetime.now(),
            metadata={
                **cluster1.metadata,
                **cluster2.metadata,
                'merged_from': [cluster_id1, cluster_id2]
            }
        )
        
        # Update registries
        del self.clusters[cluster_id1]
        del self.clusters[cluster_id2]
        self.clusters[merged.id] = merged
        
        # Update memory mappings
        for member in merged.members:
            if member in self.memory_to_clusters:
                self.memory_to_clusters[member].discard(cluster_id1)
                self.memory_to_clusters[member].discard(cluster_id2)
                self.memory_to_clusters[member].add(merged.id)
        
        return merged
    
    async def evolve_clusters(self):
        """Evolve clusters over time."""
        # Check for clusters that should be merged
        merge_candidates = []
        
        for (id1, id2), strength in self.cluster_relationships.items():
            if strength > 0.8:  # High relationship strength
                if id1 in self.clusters and id2 in self.clusters:
                    cluster1 = self.clusters[id1]
                    cluster2 = self.clusters[id2]
                    
                    # Check if merge would be beneficial
                    if (cluster1.size() + cluster2.size() <= self.max_cluster_size and
                        cluster1.type == cluster2.type):
                        merge_candidates.append((id1, id2, strength))
        
        # Sort by strength and merge top candidates
        merge_candidates.sort(key=lambda x: x[2], reverse=True)
        merged = set()
        
        for id1, id2, strength in merge_candidates[:3]:  # Limit merges per evolution
            if id1 not in merged and id2 not in merged:
                await self.merge_clusters(id1, id2)
                merged.add(id1)
                merged.add(id2)
        
        # Check for stale clusters
        stale_threshold = timedelta(days=7)
        stale_clusters = []
        
        for cluster_id, cluster in self.clusters.items():
            if cluster.age() > stale_threshold and cluster.size() < self.min_cluster_size * 2:
                stale_clusters.append(cluster_id)
        
        # Archive or remove stale clusters
        for cluster_id in stale_clusters:
            logger.info(f"Archiving stale cluster: {cluster_id}")
            # For now, just mark as stale
            self.clusters[cluster_id].metadata['stale'] = True


# Global clusterer instance
_clusterer: Optional[SemanticClusterer] = None


def get_semantic_clusterer(ci_name: str) -> SemanticClusterer:
    """Get or create semantic clusterer for CI."""
    global _clusterer
    if _clusterer is None:
        _clusterer = SemanticClusterer(ci_name)
    return _clusterer