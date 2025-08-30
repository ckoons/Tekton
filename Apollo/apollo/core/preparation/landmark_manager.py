"""
Apollo Landmark Manager
Manages memory landmarks in Athena's knowledge graph
Creates nodes and relationships for memory items
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Import memory components
from .context_brief import MemoryItem, MemoryType, CIType

# Import landmarks with fallback
try:
    from landmarks import (
        memory_landmark,
        decision_landmark,
        insight_landmark,
        error_landmark
    )
except ImportError:
    def memory_landmark(**kwargs):
        def decorator(func): return func
        return decorator
    def decision_landmark(**kwargs):
        def decorator(func): return func
        return decorator
    def insight_landmark(**kwargs):
        def decorator(func): return func
        return decorator
    def error_landmark(**kwargs):
        def decorator(func): return func
        return decorator


# Relationship types for memory landmarks
class MemoryRelationship:
    """Types of relationships between memory landmarks"""
    CAUSED_BY = "CAUSED_BY"
    LED_TO = "LED_TO"
    RESOLVED_BY = "RESOLVED_BY"
    REFERENCES = "REFERENCES"
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    DURING = "DURING"


@memory_landmark(
    title="Landmark Manager",
    description="Manages memory landmarks in knowledge graph",
    namespace="apollo"
)
class LandmarkManager:
    """
    Manages memory landmarks in Athena's knowledge graph
    Creates Apollo namespace nodes and relationships
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the landmark manager
        
        Args:
            storage_dir: Directory for landmark storage
        """
        if storage_dir is None:
            apollo_root = Path(__file__).parent.parent.parent
            storage_dir = apollo_root / "data" / "landmarks"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Local storage for landmarks (before graph integration)
        self.landmarks_file = self.storage_dir / "landmarks.json"
        self.relationships_file = self.storage_dir / "relationships.json"
        
        # Cache
        self.landmarks = {}
        self.relationships = []
        
        # Load existing data
        self.load()
        
        logger.info(f"Landmark manager initialized at {self.storage_dir}")
    
    def memory_to_landmark(self, memory: MemoryItem) -> Dict[str, Any]:
        """
        Convert a memory item to a landmark node
        
        Args:
            memory: MemoryItem to convert
            
        Returns:
            Landmark node dictionary for graph
        """
        landmark_id = f"lmk_{memory.type.value}_{memory.id}"
        
        landmark = {
            "entity_id": landmark_id,
            "entity_type": "memory_landmark",
            "name": memory.summary,
            "namespace": "apollo",
            "properties": {
                "memory_id": memory.id,
                "memory_type": memory.type.value,
                "summary": memory.summary,
                "content": memory.content,
                "ci_source": memory.ci_source,
                "ci_type": memory.ci_type.value if hasattr(memory.ci_type, 'value') else str(memory.ci_type),
                "timestamp": memory.timestamp.isoformat() if hasattr(memory.timestamp, 'isoformat') else str(memory.timestamp),
                "priority": memory.priority,
                "tags": memory.relevance_tags,
                "token_count": memory.tokens,
                "expires": memory.expires.isoformat() if memory.expires and hasattr(memory.expires, 'isoformat') else None
            },
            "confidence": min(memory.priority / 10.0, 1.0),
            "source": f"apollo:{memory.ci_source}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add type-specific properties
        if memory.type == MemoryType.DECISION:
            landmark["properties"]["landmark_type"] = "decision"
            landmark["properties"]["impacts"] = memory.relevance_tags
        elif memory.type == MemoryType.INSIGHT:
            landmark["properties"]["landmark_type"] = "insight"
        elif memory.type == MemoryType.ERROR:
            landmark["properties"]["landmark_type"] = "error"
            landmark["properties"]["severity"] = "high" if memory.priority >= 7 else "medium"
        elif memory.type == MemoryType.PLAN:
            landmark["properties"]["landmark_type"] = "plan"
            landmark["properties"]["status"] = "pending"
        
        return landmark
    
    def create_landmark(self, memory: MemoryItem) -> str:
        """
        Create a landmark from a memory item
        
        Args:
            memory: MemoryItem to create landmark from
            
        Returns:
            Landmark ID
        """
        landmark = self.memory_to_landmark(memory)
        landmark_id = landmark["entity_id"]
        
        # Store locally
        self.landmarks[landmark_id] = landmark
        
        # Save to disk
        self.save()
        
        logger.info(f"Created landmark {landmark_id} from memory {memory.id}")
        return landmark_id
    
    def create_relationship(self, source_id: str, target_id: str, 
                          relationship_type: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a relationship between landmarks
        
        Args:
            source_id: Source landmark ID
            target_id: Target landmark ID
            relationship_type: Type of relationship
            properties: Additional properties
            
        Returns:
            Relationship ID
        """
        relationship_id = f"rel_{uuid.uuid4().hex[:8]}"
        
        relationship = {
            "relationship_id": relationship_id,
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "namespace": "apollo",
            "properties": properties or {},
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.8
        }
        
        self.relationships.append(relationship)
        self.save()
        
        logger.info(f"Created relationship {relationship_id}: {source_id} -{relationship_type}-> {target_id}")
        return relationship_id
    
    def find_relationships(self, memories: List[MemoryItem]) -> List[Tuple[str, str, str]]:
        """
        Find relationships between memories based on content and timing
        
        Args:
            memories: List of memory items to analyze
            
        Returns:
            List of (source_id, target_id, relationship_type) tuples
        """
        relationships = []
        
        # Sort by timestamp
        sorted_memories = sorted(memories, key=lambda m: m.timestamp)
        
        for i, memory1 in enumerate(sorted_memories):
            landmark1_id = f"lmk_{memory1.type.value}_{memory1.id}"
            
            for memory2 in sorted_memories[i+1:]:
                landmark2_id = f"lmk_{memory2.type.value}_{memory2.id}"
                
                # Temporal relationships
                time_diff = (memory2.timestamp - memory1.timestamp).total_seconds()
                if time_diff < 300:  # Within 5 minutes
                    relationships.append((landmark1_id, landmark2_id, MemoryRelationship.DURING))
                else:
                    relationships.append((landmark1_id, landmark2_id, MemoryRelationship.BEFORE))
                
                # Content-based relationships
                if memory1.type == MemoryType.ERROR and memory2.type == MemoryType.DECISION:
                    # Error might have led to decision
                    if any(tag in memory2.relevance_tags for tag in memory1.relevance_tags):
                        relationships.append((landmark1_id, landmark2_id, MemoryRelationship.LED_TO))
                
                elif memory1.type == MemoryType.INSIGHT and memory2.type == MemoryType.DECISION:
                    # Insight might have caused decision
                    if any(tag in memory2.relevance_tags for tag in memory1.relevance_tags):
                        relationships.append((landmark1_id, landmark2_id, MemoryRelationship.CAUSED_BY))
                
                elif memory1.type == MemoryType.PLAN and memory2.type == MemoryType.ERROR:
                    # Plan might have resolved error
                    if any(tag in memory2.relevance_tags for tag in memory1.relevance_tags):
                        relationships.append((landmark2_id, landmark1_id, MemoryRelationship.RESOLVED_BY))
                
                # Check for references
                if memory1.summary.lower() in memory2.content.lower():
                    relationships.append((landmark2_id, landmark1_id, MemoryRelationship.REFERENCES))
        
        return relationships
    
    def get_landmark(self, landmark_id: str) -> Optional[Dict[str, Any]]:
        """Get a landmark by ID"""
        return self.landmarks.get(landmark_id)
    
    def get_landmarks_for_ci(self, ci_name: str) -> List[Dict[str, Any]]:
        """Get all landmarks for a specific CI"""
        return [
            landmark for landmark in self.landmarks.values()
            if landmark["properties"].get("ci_source") == ci_name
        ]
    
    def get_landmarks_by_type(self, memory_type: MemoryType) -> List[Dict[str, Any]]:
        """Get all landmarks of a specific type"""
        return [
            landmark for landmark in self.landmarks.values()
            if landmark["properties"].get("memory_type") == memory_type.value
        ]
    
    def get_related_landmarks(self, landmark_id: str) -> List[Dict[str, Any]]:
        """Get landmarks related to a specific landmark"""
        related = []
        
        for rel in self.relationships:
            target_id = None
            if rel["source_id"] == landmark_id:
                target_id = rel["target_id"]
            elif rel["target_id"] == landmark_id:
                target_id = rel["source_id"]
            
            if target_id and target_id in self.landmarks:
                related.append(self.landmarks[target_id])
        
        return related
    
    def build_graph_query(self, ci_name: str, context: str) -> str:
        """
        Build a Cypher query for finding relevant landmarks
        
        Args:
            ci_name: CI requesting memories
            context: Current context
            
        Returns:
            Cypher query string (for future Neo4j integration)
        """
        # Extract keywords from context
        keywords = [word.lower() for word in context.split() if len(word) > 3]
        keyword_pattern = '|'.join(keywords[:5])  # Top 5 keywords
        
        query = f"""
        MATCH (m:memory_landmark {{namespace: 'apollo'}})
        WHERE m.ci_source = '{ci_name}' 
           OR ANY(tag IN m.tags WHERE tag =~ '(?i).*({keyword_pattern}).*')
        OPTIONAL MATCH (m)-[r]-(related:memory_landmark)
        RETURN m, r, related
        ORDER BY m.priority DESC, m.timestamp DESC
        LIMIT 20
        """
        
        return query
    
    def save(self):
        """Save landmarks and relationships to disk"""
        # Save landmarks
        with open(self.landmarks_file, 'w') as f:
            json.dump(self.landmarks, f, indent=2, default=str)
        
        # Save relationships
        with open(self.relationships_file, 'w') as f:
            json.dump(self.relationships, f, indent=2, default=str)
        
        logger.debug(f"Saved {len(self.landmarks)} landmarks and {len(self.relationships)} relationships")
    
    def load(self):
        """Load landmarks and relationships from disk"""
        # Load landmarks
        if self.landmarks_file.exists():
            try:
                with open(self.landmarks_file, 'r') as f:
                    self.landmarks = json.load(f)
                logger.info(f"Loaded {len(self.landmarks)} landmarks")
            except Exception as e:
                logger.error(f"Failed to load landmarks: {e}")
                self.landmarks = {}
        
        # Load relationships
        if self.relationships_file.exists():
            try:
                with open(self.relationships_file, 'r') as f:
                    self.relationships = json.load(f)
                logger.info(f"Loaded {len(self.relationships)} relationships")
            except Exception as e:
                logger.error(f"Failed to load relationships: {e}")
                self.relationships = []
    
    def export_for_athena(self) -> Dict[str, Any]:
        """
        Export landmarks and relationships for Athena import
        
        Returns:
            Dictionary with entities and relationships
        """
        return {
            "namespace": "apollo",
            "entities": list(self.landmarks.values()),
            "relationships": self.relationships,
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_landmarks": len(self.landmarks),
                "total_relationships": len(self.relationships)
            }
        }


# Example usage
if __name__ == "__main__":
    from context_brief import MemoryItem
    
    # Create manager
    manager = LandmarkManager()
    
    # Create sample memory
    memory = MemoryItem(
        id="test_001",
        timestamp=datetime.now(),
        ci_source="ergon-ci",
        ci_type=CIType.GREEK,
        type=MemoryType.DECISION,
        summary="Use Redux for state management",
        content="After evaluation, Redux provides the best state management solution",
        tokens=20,
        relevance_tags=["redux", "state", "architecture"],
        priority=8
    )
    
    # Create landmark
    landmark_id = manager.create_landmark(memory)
    print(f"Created landmark: {landmark_id}")
    
    # Get landmark
    landmark = manager.get_landmark(landmark_id)
    print(f"Retrieved landmark: {landmark['name']}")
    
    # Export for Athena
    export = manager.export_for_athena()
    print(f"Export ready: {export['metadata']}")