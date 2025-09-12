"""
Working Memory Buffer for active thoughts.

Provides temporary storage for active cognitive processes before
consolidation to long-term memory.
"""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Deque, Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger("engram.experience.working_memory")


class ThoughtState(Enum):
    """States of a thought in working memory."""
    ACTIVE = "active"       # Currently being processed
    REHEARSING = "rehearsing"  # Being reinforced
    CONSOLIDATING = "consolidating"  # Moving to long-term
    DECAYING = "decaying"   # Fading from attention
    FORGOTTEN = "forgotten"  # Removed from working memory


@dataclass
class ThoughtBuffer:
    """A single thought in working memory."""
    
    thought_id: str
    content: Any
    
    state: ThoughtState = ThoughtState.ACTIVE
    
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    
    attention_weight: float = 1.0  # How much attention this has
    decay_rate: float = 0.1  # How quickly it fades
    
    associations: Set[str] = field(default_factory=set)  # Related thought IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def access(self):
        """Record an access to this thought."""
        self.last_accessed = datetime.now()
        self.access_count += 1
        self.attention_weight = min(1.0, self.attention_weight + 0.2)
        
        # Frequent access moves to rehearsing
        if self.access_count > 3 and self.state == ThoughtState.ACTIVE:
            self.state = ThoughtState.REHEARSING
    
    def decay(self, time_elapsed: float):
        """Apply temporal decay."""
        # Decay based on time since last access (in seconds)
        decay_amount = self.decay_rate * (time_elapsed / 60.0)  # Per minute
        self.attention_weight = max(0.0, self.attention_weight - decay_amount)
        
        # Update state based on attention
        if self.attention_weight < 0.2:
            self.state = ThoughtState.DECAYING
        elif self.attention_weight < 0.05:
            self.state = ThoughtState.FORGOTTEN
    
    def should_consolidate(self) -> bool:
        """Check if thought should be consolidated to long-term memory."""
        # Consolidate if rehearsed enough or explicitly marked
        return (
            self.state == ThoughtState.REHEARSING and 
            self.access_count >= 5
        ) or self.state == ThoughtState.CONSOLIDATING
    
    def associate_with(self, other_id: str):
        """Create association with another thought."""
        self.associations.add(other_id)


class WorkingMemory:
    """
    Working memory system for active cognitive processing.
    
    Implements the 7±2 item limit and temporal decay.
    """
    
    def __init__(self, 
                 capacity: int = 7,
                 chunk_size: int = 3,
                 decay_interval: float = 30.0):  # seconds
        """
        Initialize working memory.
        
        Args:
            capacity: Maximum number of active thoughts (7±2 rule)
            chunk_size: Size of chunks for grouping related thoughts
            decay_interval: How often to apply decay (seconds)
        """
        self.capacity = capacity
        self.chunk_size = chunk_size
        self.decay_interval = decay_interval
        
        self.thoughts: Dict[str, ThoughtBuffer] = {}
        self.attention_queue: Deque[str] = deque(maxlen=capacity)
        
        self.chunks: Dict[str, List[str]] = {}  # Grouped thoughts
        self.consolidation_queue: List[str] = []
        
        self._decay_task = None
        self._consolidation_callback = None
        
        logger.info(f"Working memory initialized with capacity {capacity}")
    
    async def add_thought(self, 
                         content: Any,
                         thought_id: Optional[str] = None,
                         metadata: Optional[Dict] = None) -> str:
        """Add a thought to working memory."""
        if thought_id is None:
            import uuid
            thought_id = str(uuid.uuid4())[:8]
        
        # Check capacity
        if len(self.thoughts) >= self.capacity:
            await self._make_room()
        
        # Create thought buffer
        thought = ThoughtBuffer(
            thought_id=thought_id,
            content=content,
            metadata=metadata or {}
        )
        
        self.thoughts[thought_id] = thought
        self.attention_queue.append(thought_id)
        
        logger.debug(f"Added thought {thought_id} to working memory")
        return thought_id
    
    async def access_thought(self, thought_id: str) -> Optional[Any]:
        """Access a thought, reinforcing it."""
        if thought_id not in self.thoughts:
            return None
        
        thought = self.thoughts[thought_id]
        thought.access()
        
        # Move to front of attention queue
        if thought_id in self.attention_queue:
            self.attention_queue.remove(thought_id)
        self.attention_queue.append(thought_id)
        
        # Check if ready for consolidation
        if thought.should_consolidate():
            await self._mark_for_consolidation(thought_id)
        
        return thought.content
    
    async def rehearse(self, thought_ids: List[str]):
        """Rehearse multiple thoughts together (maintenance rehearsal)."""
        for thought_id in thought_ids:
            if thought_id in self.thoughts:
                thought = self.thoughts[thought_id]
                thought.state = ThoughtState.REHEARSING
                thought.attention_weight = min(1.0, thought.attention_weight + 0.3)
                
                # Create associations between rehearsed thoughts
                for other_id in thought_ids:
                    if other_id != thought_id:
                        thought.associate_with(other_id)
        
        logger.debug(f"Rehearsed {len(thought_ids)} thoughts together")
    
    async def chunk_thoughts(self, thought_ids: List[str], chunk_label: str):
        """Group related thoughts into a chunk."""
        if len(thought_ids) > self.chunk_size * 2:
            logger.warning(f"Chunk size {len(thought_ids)} exceeds recommended limit")
        
        self.chunks[chunk_label] = thought_ids
        
        # Create strong associations within chunk
        for thought_id in thought_ids:
            if thought_id in self.thoughts:
                thought = self.thoughts[thought_id]
                for other_id in thought_ids:
                    if other_id != thought_id:
                        thought.associate_with(other_id)
                
                # Chunking reduces memory load
                thought.attention_weight *= 0.7
        
        logger.debug(f"Created chunk '{chunk_label}' with {len(thought_ids)} thoughts")
    
    async def get_associated(self, thought_id: str) -> List[str]:
        """Get thoughts associated with a given thought."""
        if thought_id not in self.thoughts:
            return []
        
        thought = self.thoughts[thought_id]
        associated = list(thought.associations)
        
        # Also check chunks
        for chunk_label, chunk_thoughts in self.chunks.items():
            if thought_id in chunk_thoughts:
                associated.extend([t for t in chunk_thoughts if t != thought_id])
        
        return list(set(associated))  # Remove duplicates
    
    def get_active_thoughts(self) -> List[ThoughtBuffer]:
        """Get all active thoughts sorted by attention weight."""
        active = [
            thought for thought in self.thoughts.values()
            if thought.state in [ThoughtState.ACTIVE, ThoughtState.REHEARSING]
        ]
        return sorted(active, key=lambda t: t.attention_weight, reverse=True)
    
    async def _make_room(self):
        """Make room in working memory by removing least important thoughts."""
        # Sort by attention weight and recency
        thoughts_list = list(self.thoughts.values())
        thoughts_list.sort(
            key=lambda t: (t.attention_weight, -t.access_count, t.last_accessed)
        )
        
        # Remove least important thoughts
        to_remove = thoughts_list[:len(thoughts_list) - self.capacity + 1]
        
        for thought in to_remove:
            # Mark for consolidation if important enough
            if thought.access_count >= 2 or thought.state == ThoughtState.REHEARSING:
                await self._mark_for_consolidation(thought.thought_id)
            
            # Remove from working memory
            del self.thoughts[thought.thought_id]
            if thought.thought_id in self.attention_queue:
                self.attention_queue.remove(thought.thought_id)
            
            logger.debug(f"Removed thought {thought.thought_id} from working memory")
    
    async def _mark_for_consolidation(self, thought_id: str):
        """Mark a thought for consolidation to long-term memory."""
        if thought_id not in self.thoughts:
            return
        
        thought = self.thoughts[thought_id]
        thought.state = ThoughtState.CONSOLIDATING
        self.consolidation_queue.append(thought_id)
        
        # Trigger consolidation callback if set
        if self._consolidation_callback:
            await self._consolidation_callback(thought)
        
        logger.debug(f"Marked thought {thought_id} for consolidation")
    
    async def consolidate_all(self) -> List[ThoughtBuffer]:
        """Consolidate all thoughts marked for consolidation."""
        consolidated = []
        
        for thought_id in self.consolidation_queue[:]:
            if thought_id in self.thoughts:
                thought = self.thoughts[thought_id]
                consolidated.append(thought)
                
                # Remove from working memory after consolidation
                del self.thoughts[thought_id]
                if thought_id in self.attention_queue:
                    self.attention_queue.remove(thought_id)
                
                self.consolidation_queue.remove(thought_id)
        
        logger.info(f"Consolidated {len(consolidated)} thoughts to long-term memory")
        return consolidated
    
    async def apply_decay(self):
        """Apply temporal decay to all thoughts."""
        now = datetime.now()
        forgotten = []
        
        for thought_id, thought in self.thoughts.items():
            time_elapsed = (now - thought.last_accessed).total_seconds()
            thought.decay(time_elapsed)
            
            if thought.state == ThoughtState.FORGOTTEN:
                forgotten.append(thought_id)
        
        # Remove forgotten thoughts
        for thought_id in forgotten:
            del self.thoughts[thought_id]
            if thought_id in self.attention_queue:
                self.attention_queue.remove(thought_id)
        
        if forgotten:
            logger.debug(f"Forgot {len(forgotten)} decayed thoughts")
    
    async def start_decay_process(self):
        """Start automatic decay process."""
        async def decay_loop():
            while True:
                await asyncio.sleep(self.decay_interval)
                await self.apply_decay()
        
        self._decay_task = asyncio.create_task(decay_loop())
        logger.info("Started working memory decay process")
    
    def stop_decay_process(self):
        """Stop the decay process."""
        if self._decay_task:
            self._decay_task.cancel()
            self._decay_task = None
    
    def set_consolidation_callback(self, callback):
        """Set callback for when thoughts are ready for consolidation."""
        self._consolidation_callback = callback
    
    def get_capacity_usage(self) -> float:
        """Get current capacity usage (0.0 to 1.0)."""
        return len(self.thoughts) / self.capacity
    
    def is_overloaded(self) -> bool:
        """Check if working memory is overloaded."""
        return len(self.thoughts) >= self.capacity
    
    async def clear(self):
        """Clear working memory (with optional consolidation)."""
        # Consolidate important thoughts first
        await self.consolidate_all()
        
        # Clear remaining thoughts
        self.thoughts.clear()
        self.attention_queue.clear()
        self.chunks.clear()
        
        logger.info("Cleared working memory")