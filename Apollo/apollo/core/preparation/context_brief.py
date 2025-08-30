"""
Apollo Context Brief System
Provides intelligent, token-aware Context Briefs to CIs with memory landmarks
Part of Apollo's Preparation service for information architecture
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, asdict
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Import landmarks with fallback
try:
    from landmarks import (
        memory_landmark,
        decision_landmark,
        insight_landmark,
        error_landmark
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def memory_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def decision_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def insight_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def error_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Memory type enum
class MemoryType(str, Enum):
    DECISION = "decision"
    INSIGHT = "insight"
    CONTEXT = "context"
    PLAN = "plan"
    ERROR = "error"
    
# CI type enum
class CIType(str, Enum):
    GREEK = "greek"
    TERMINAL = "terminal"
    PROJECT = "project"
    UNKNOWN = "unknown"
    GREEK_CHORUS = "greek"  # Alias for compatibility

@dataclass
class MemoryStatistics:
    """Statistics about the memory catalog"""
    total_memories: int
    total_tokens: int
    by_type: Dict[str, int]
    by_ci: Dict[str, int]
    by_ci_type: Dict[str, int]
    oldest_memory: Optional[datetime]
    newest_memory: Optional[datetime]
    avg_priority: float
    last_cleanup: Optional[datetime] = None

@dataclass
class MemoryItem:
    """Individual memory item with metadata"""
    id: str
    timestamp: datetime
    ci_source: str
    ci_type: CIType
    type: MemoryType
    summary: str  # 50 chars max
    content: str
    tokens: int
    relevance_tags: List[str]
    priority: int  # 0-10
    expires: Optional[datetime] = None
    references: List[str] = None  # Other memory IDs
    relevance_score: float = 0.0  # Calculated at retrieval time
    
    def __post_init__(self):
        # Ensure summary is max 50 chars
        if len(self.summary) > 50:
            self.summary = self.summary[:47] + "..."
        
        # Initialize references as empty list if None
        if self.references is None:
            self.references = []
            
        # Set default expiration if not provided
        if self.expires is None:
            self.expires = datetime.now() + timedelta(days=7)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['expires'] = self.expires.isoformat() if self.expires else None
        data['type'] = self.type.value
        data['ci_type'] = self.ci_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['expires'] = datetime.fromisoformat(data['expires']) if data.get('expires') else None
        data['type'] = MemoryType(data['type'])
        data['ci_type'] = CIType(data.get('ci_type', 'unknown'))
        return cls(**data)


@memory_landmark(
    title="Context Brief Manager",
    description="Apollo's central system for preparing Context Briefs",
    namespace="apollo"
)
class ContextBriefManager:
    """
    Apollo's Context Brief Manager
    Prepares token-aware Context Briefs with memory landmarks for all CIs
    """
    
    def __init__(self, storage_dir: Optional[Path] = None, enable_landmarks: bool = True):
        """
        Initialize the context brief manager
        
        Args:
            storage_dir: Directory for storing memory files
            enable_landmarks: Whether to create graph landmarks
        """
        if storage_dir is None:
            try:
                from shared.env import TektonEnviron
                tekton_root = Path(TektonEnviron.get('TEKTON_ROOT', '.'))
                storage_dir = tekton_root / '.tekton' / 'memory'
            except ImportError:
                # Fallback for Apollo
                apollo_root = Path(__file__).parent.parent.parent
                storage_dir = apollo_root / 'data' / 'preparation'
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_memories_per_ci = 1000
        self.default_expiration_days = 7
        self.max_injection_tokens = 2000
        
        # In-memory storage
        self.memories = []
        self.has_changes = False
        self.storage_path = self.storage_dir / "catalog.json"
        
        # Cache for frequently accessed memories
        self._cache = {}
        self._cache_timestamp = {}
        
        # Landmark manager integration
        self.enable_landmarks = enable_landmarks
        self.landmark_manager = None
        if enable_landmarks:
            try:
                from .landmark_manager import LandmarkManager
                self.landmark_manager = LandmarkManager(storage_dir=self.storage_dir.parent / 'landmarks')
                logger.info("Landmark manager initialized")
            except ImportError as e:
                logger.warning(f"Landmark manager not available: {e}")
                self.enable_landmarks = False
        
        logger.info(f"Context Brief manager initialized at {self.storage_dir}")
    
    def _get_catalog_path(self, ci_name: str = None) -> Path:
        """Get path to catalog file for a specific CI or global"""
        if ci_name:
            return self.storage_dir / f"catalog_{ci_name}.json"
        else:
            return self.storage_dir / "catalog_global.json"
    
    def _load_catalog(self, ci_name: str = None) -> Dict[str, Any]:
        """Load catalog from disk"""
        catalog_path = self._get_catalog_path(ci_name)
        
        if catalog_path.exists():
            try:
                with open(catalog_path, 'r') as f:
                    data = json.load(f)
                    # Convert memory items from dict
                    if 'memories' in data:
                        data['memories'] = [
                            MemoryItem.from_dict(m) if isinstance(m, dict) else m
                            for m in data['memories']
                        ]
                    return data
            except Exception as e:
                logger.error(f"Failed to load catalog from {catalog_path}: {e}")
                return self._empty_catalog(ci_name)
        else:
            return self._empty_catalog(ci_name)
    
    def _save_catalog(self, catalog: Dict[str, Any], ci_name: str = None):
        """Save catalog to disk"""
        catalog_path = self._get_catalog_path(ci_name)
        
        try:
            # Convert memory items to dict for JSON
            save_data = catalog.copy()
            if 'memories' in save_data:
                save_data['memories'] = [
                    m.to_dict() if isinstance(m, MemoryItem) else m
                    for m in save_data['memories']
                ]
            
            save_data['last_updated'] = datetime.now().isoformat()
            
            with open(catalog_path, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            logger.debug(f"Saved catalog to {catalog_path}")
        except Exception as e:
            logger.error(f"Failed to save catalog to {catalog_path}: {e}")
    
    def _empty_catalog(self, ci_name: str = None) -> Dict[str, Any]:
        """Create empty catalog structure"""
        return {
            "version": "1.0.0",
            "ci_name": ci_name or "global",
            "last_updated": datetime.now().isoformat(),
            "memories": [],
            "statistics": {
                "total_memories": 0,
                "total_tokens": 0,
                "oldest_memory": None,
                "last_cleanup": datetime.now().isoformat()
            }
        }
    
    def _generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}_{content[:100]}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"mem_{int(datetime.now().timestamp())}_{hash_value}"
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        TODO: Use tiktoken for accurate counting
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _detect_ci_type(self, ci_name: str) -> CIType:
        """Detect CI type from name"""
        # Greek Chorus CIs
        greek_chorus = [
            'apollo', 'athena', 'engram', 'ergon', 'harmonia', 'hermes',
            'metis', 'noesis', 'numa', 'penia', 'prometheus', 'rhetor',
            'sophia', 'synthesis', 'tekton', 'telos', 'terma'
        ]
        
        ci_base = ci_name.replace('-ci', '').replace('_', '-')
        
        if ci_base in greek_chorus:
            return CIType.GREEK
        elif ci_name.endswith('-ci'):
            # Check if it's a terminal or project
            # TODO: Query CI registry for accurate type
            if 'term' in ci_name or ci_name.startswith(('ami', 'andi')):
                return CIType.TERMINAL
            else:
                return CIType.PROJECT
        else:
            return CIType.UNKNOWN
    
    # CRUD Operations
    
    def add_memory(self, memory: MemoryItem) -> None:
        """
        Add an existing memory item to the catalog
        
        Args:
            memory: MemoryItem to add
        """
        self.memories.append(memory)
        self.has_changes = True
        
        # Create landmark if enabled
        if self.enable_landmarks and self.landmark_manager:
            try:
                landmark_id = self.landmark_manager.create_landmark(memory)
                logger.debug(f"Created landmark {landmark_id} for memory {memory.id}")
            except Exception as e:
                logger.error(f"Failed to create landmark: {e}")
    
    def save(self) -> None:
        """Save memories to disk"""
        catalog_data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "memories": [self._memory_to_dict(m) for m in self.memories],
            "statistics": {
                "total_memories": len(self.memories),
                "total_tokens": sum(m.tokens for m in self.memories),
                "oldest_memory": min((m.timestamp for m in self.memories), default=None),
                "newest_memory": max((m.timestamp for m in self.memories), default=None)
            }
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(catalog_data, f, indent=2, default=str)
        
        self.has_changes = False
        logger.info(f"Saved {len(self.memories)} memories to {self.storage_path}")
    
    def load(self) -> None:
        """Load memories from disk"""
        if not self.storage_path.exists():
            logger.info("No catalog file found, starting fresh")
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                catalog_data = json.load(f)
            
            self.memories = []
            for mem_dict in catalog_data.get('memories', []):
                memory = self._dict_to_memory(mem_dict)
                if memory:
                    self.memories.append(memory)
            
            logger.info(f"Loaded {len(self.memories)} memories from {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
    
    def _memory_to_dict(self, memory: MemoryItem) -> dict:
        """Convert MemoryItem to dictionary for JSON serialization"""
        return {
            "id": memory.id,
            "timestamp": memory.timestamp.isoformat() if isinstance(memory.timestamp, datetime) else memory.timestamp,
            "ci_source": memory.ci_source,
            "ci_type": memory.ci_type.value if hasattr(memory.ci_type, 'value') else memory.ci_type,
            "type": memory.type.value if hasattr(memory.type, 'value') else memory.type,
            "summary": memory.summary,
            "content": memory.content,
            "tokens": memory.tokens,
            "relevance_tags": memory.relevance_tags,
            "priority": memory.priority,
            "expires": memory.expires.isoformat() if memory.expires else None,
            "references": memory.references or [],
            "relevance_score": memory.relevance_score
        }
    
    def _dict_to_memory(self, data: dict) -> Optional[MemoryItem]:
        """Convert dictionary to MemoryItem"""
        try:
            return MemoryItem(
                id=data["id"],
                timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"],
                ci_source=data["ci_source"],
                ci_type=CIType(data["ci_type"]) if isinstance(data["ci_type"], str) else data["ci_type"],
                type=MemoryType(data["type"]) if isinstance(data["type"], str) else data["type"],
                summary=data["summary"],
                content=data["content"],
                tokens=data["tokens"],
                relevance_tags=data.get("relevance_tags", []),
                priority=data.get("priority", 5),
                expires=datetime.fromisoformat(data["expires"]) if data.get("expires") else None,
                references=data.get("references", []),
                relevance_score=data.get("relevance_score", 0.0)
            )
        except Exception as e:
            logger.error(f"Failed to deserialize memory: {e}")
            return None
    
    def store(self, ci_name: str, memory_type: MemoryType, summary: str, 
              content: str, tags: List[str] = None, priority: int = 5,
              expires_days: int = None) -> MemoryItem:
        """
        Store a new memory item
        
        Args:
            ci_name: Source CI name
            memory_type: Type of memory (decision, insight, etc.)
            summary: Brief summary (max 50 chars)
            content: Full memory content
            tags: Relevance tags for searching
            priority: Priority 0-10 (default 5)
            expires_days: Days until expiration (default 7)
            
        Returns:
            Created MemoryItem
        """
        # Create memory item
        memory = MemoryItem(
            id=self._generate_memory_id(content),
            timestamp=datetime.now(),
            ci_source=ci_name,
            ci_type=self._detect_ci_type(ci_name),
            type=memory_type,
            summary=summary[:50],
            content=content,
            tokens=self._count_tokens(content),
            relevance_tags=tags or [],
            priority=min(max(priority, 0), 10),  # Clamp to 0-10
            expires=datetime.now() + timedelta(days=expires_days or self.default_expiration_days)
        )
        
        # Load catalog
        catalog = self._load_catalog(ci_name)
        
        # Add memory
        catalog['memories'].append(memory)
        
        # Update statistics
        catalog['statistics']['total_memories'] = len(catalog['memories'])
        catalog['statistics']['total_tokens'] = sum(m.tokens for m in catalog['memories'])
        
        # Enforce max memories limit
        if len(catalog['memories']) > self.max_memories_per_ci:
            # Remove oldest low-priority memories
            catalog['memories'].sort(key=lambda m: (m.priority, m.timestamp))
            catalog['memories'] = catalog['memories'][-self.max_memories_per_ci:]
        
        # Save catalog
        self._save_catalog(catalog, ci_name)
        
        # Also add to global catalog
        global_catalog = self._load_catalog()
        global_catalog['memories'].append(memory)
        self._save_catalog(global_catalog)
        
        logger.info(f"Stored memory {memory.id} for {ci_name}")
        return memory
    
    def get(self, memory_id: str, ci_name: str = None) -> Optional[MemoryItem]:
        """Get a specific memory by ID"""
        catalog = self._load_catalog(ci_name)
        
        for memory in catalog['memories']:
            if memory.id == memory_id:
                return memory
        
        # Try global catalog if not found
        if ci_name:
            global_catalog = self._load_catalog()
            for memory in global_catalog['memories']:
                if memory.id == memory_id:
                    return memory
        
        return None
    
    def search(self, query: str = None) -> List[MemoryItem]:
        """
        Search memories by text query
        
        Args:
            query: Text to search in content, summary and tags
            
        Returns:
            List of matching memories
        """
        if not query:
            return self.memories.copy()
        
        query_lower = query.lower()
        results = []
        
        for memory in self.memories:
            if (query_lower in memory.summary.lower() or 
                query_lower in memory.content.lower() or
                any(query_lower in tag.lower() for tag in memory.relevance_tags)):
                results.append(memory)
        
        return results
    
    def filter_by_type(self, memory_type: MemoryType) -> List[MemoryItem]:
        """Filter memories by type"""
        return [m for m in self.memories if m.type == memory_type]
    
    def filter_by_ci(self, ci_name: str) -> List[MemoryItem]:
        """Filter memories by CI source"""
        return [m for m in self.memories if m.ci_source == ci_name]
    
    def filter_by_ci_type(self, ci_type: CIType) -> List[MemoryItem]:
        """Filter memories by CI type"""
        return [m for m in self.memories if m.ci_type == ci_type]
    
    def filter_by_tags(self, tags: List[str]) -> List[MemoryItem]:
        """Filter memories by tags (any match)"""
        return [m for m in self.memories 
                if any(tag in m.relevance_tags for tag in tags)]
    
    def update_relevance_scores(self, context: dict) -> None:
        """
        Update relevance scores for all memories based on context
        
        Args:
            context: Dictionary with 'message' and 'ci_name' keys
        """
        import math
        
        for memory in self.memories:
            score = 0.0
            
            # Recency factor (exponential decay)
            age_hours = (datetime.now() - memory.timestamp).total_seconds() / 3600
            recency_score = math.exp(-age_hours / 168)  # 1 week half-life
            score += recency_score * 0.3
            
            # Context match factor
            if 'message' in context:
                context_lower = context['message'].lower()
                keyword_matches = sum(1 for tag in memory.relevance_tags 
                                     if tag.lower() in context_lower)
                if memory.summary.lower() in context_lower:
                    keyword_matches += 2
                tag_score = min(keyword_matches / 5, 1.0)
                score += tag_score * 0.4
            
            # CI affinity factor
            if 'ci_name' in context and memory.ci_source == context['ci_name']:
                score += 0.2
            
            # Priority override
            score += (memory.priority / 10) * 0.1
            
            memory.relevance_score = min(score, 1.0)
    
    def get_most_relevant(self, limit: int = 10) -> List[MemoryItem]:
        """
        Get the most relevant memories based on current scores
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of most relevant memories
        """
        sorted_memories = sorted(self.memories, 
                                key=lambda m: m.relevance_score, 
                                reverse=True)
        return sorted_memories[:limit]
    
    def pack_memories(self, max_tokens: int = None) -> List[MemoryItem]:
        """
        Pack memories within token budget, prioritizing by relevance
        
        Args:
            max_tokens: Maximum token budget (default 2000)
            
        Returns:
            List of memories that fit within budget
        """
        max_tokens = max_tokens or self.max_injection_tokens
        
        # Sort by relevance
        sorted_memories = sorted(self.memories,
                                key=lambda m: m.relevance_score,
                                reverse=True)
        
        selected = []
        token_count = 0
        
        for memory in sorted_memories:
            if token_count + memory.tokens <= max_tokens:
                selected.append(memory)
                token_count += memory.tokens
            elif token_count + self._count_tokens(memory.summary) <= max_tokens:
                # Include just summary if full content doesn't fit
                summary_memory = MemoryItem(
                    id=memory.id,
                    timestamp=memory.timestamp,
                    ci_source=memory.ci_source,
                    ci_type=memory.ci_type,
                    type=memory.type,
                    summary=memory.summary,
                    content=memory.summary,  # Just summary
                    tokens=self._count_tokens(memory.summary),
                    relevance_tags=memory.relevance_tags,
                    priority=memory.priority,
                    expires=memory.expires,
                    references=memory.references,
                    relevance_score=memory.relevance_score
                )
                selected.append(summary_memory)
                token_count += summary_memory.tokens
        
        return selected
    
    def expire_old_memories(self) -> int:
        """
        Remove expired memories
        
        Returns:
            Number of memories expired
        """
        now = datetime.now()
        original_count = len(self.memories)
        
        # Keep non-expired or high-priority permanent memories
        self.memories = [
            m for m in self.memories
            if (not m.expires or m.expires > now or m.priority >= 8)
        ]
        
        removed = original_count - len(self.memories)
        
        if removed > 0:
            self.has_changes = True
            logger.info(f"Expired {removed} old memories")
        
        return removed
    
    def analyze_relationships(self) -> int:
        """
        Analyze memories and create landmark relationships
        
        Returns:
            Number of relationships created
        """
        if not self.enable_landmarks or not self.landmark_manager:
            return 0
        
        try:
            # Find relationships between memories
            relationships = self.landmark_manager.find_relationships(self.memories)
            
            # Create relationship entries
            created = 0
            for source_id, target_id, rel_type in relationships:
                try:
                    self.landmark_manager.create_relationship(source_id, target_id, rel_type)
                    created += 1
                except Exception as e:
                    logger.error(f"Failed to create relationship: {e}")
            
            logger.info(f"Created {created} landmark relationships")
            return created
            
        except Exception as e:
            logger.error(f"Failed to analyze relationships: {e}")
            return 0
    
    def get_landmarks(self, ci_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get landmarks for a CI or all landmarks
        
        Args:
            ci_name: Optional CI filter
            
        Returns:
            List of landmark dictionaries
        """
        if not self.enable_landmarks or not self.landmark_manager:
            return []
        
        if ci_name:
            return self.landmark_manager.get_landmarks_for_ci(ci_name)
        else:
            return list(self.landmark_manager.landmarks.values())
    
    def get_statistics(self) -> MemoryStatistics:
        """Get memory statistics"""
        if not self.memories:
            return MemoryStatistics(
                total_memories=0,
                total_tokens=0,
                by_type={},
                by_ci={},
                by_ci_type={},
                oldest_memory=None,
                newest_memory=None,
                avg_priority=0.0
            )
        
        # Calculate type distribution
        by_type = {}
        for memory in self.memories:
            type_key = memory.type.value if hasattr(memory.type, 'value') else str(memory.type)
            by_type[type_key] = by_type.get(type_key, 0) + 1
        
        # Calculate CI distribution
        by_ci = {}
        for memory in self.memories:
            by_ci[memory.ci_source] = by_ci.get(memory.ci_source, 0) + 1
        
        # Calculate CI type distribution
        by_ci_type = {}
        for memory in self.memories:
            type_key = memory.ci_type.value if hasattr(memory.ci_type, 'value') else str(memory.ci_type)
            by_ci_type[type_key] = by_ci_type.get(type_key, 0) + 1
        
        return MemoryStatistics(
            total_memories=len(self.memories),
            total_tokens=sum(m.tokens for m in self.memories),
            by_type=by_type,
            by_ci=by_ci,
            by_ci_type=by_ci_type,
            oldest_memory=min((m.timestamp for m in self.memories), default=None),
            newest_memory=max((m.timestamp for m in self.memories), default=None),
            avg_priority=sum(m.priority for m in self.memories) / len(self.memories) if self.memories else 0.0
        )


# Singleton instance
_catalog: Optional[ContextBriefManager] = None


def get_context_brief_manager() -> ContextBriefManager:
    """Get or create the global context brief manager instance"""
    global _catalog
    if _catalog is None:
        _catalog = ContextBriefManager()
    return _catalog

# Backwards compatibility
def get_memory_catalog():
    """Deprecated: Use get_context_brief_manager instead"""
    return get_context_brief_manager()