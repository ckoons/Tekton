#!/usr/bin/env python3
"""
Memory strength and decay system.

Memories that aren't accessed fade, frequently accessed ones strengthen.
Based on psychological forgetting curves and reinforcement learning.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import math
from dataclasses import dataclass, field


@dataclass
class MemoryStrength:
    """Track strength and decay of individual memories."""
    memory_id: str
    initial_strength: float = 1.0
    current_strength: float = 1.0
    access_count: int = 0
    creation_time: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    reinforcement_history: List[datetime] = field(default_factory=list)
    emotional_boost: float = 0.0  # From emotional tagging
    importance: int = 3  # 1-5 scale
    
    def reinforce(self, boost: float = 0.1) -> float:
        """Strengthen memory through access."""
        self.access_count += 1
        self.last_accessed = datetime.now()
        self.reinforcement_history.append(self.last_accessed)
        
        # Logarithmic growth - harder to strengthen already strong memories
        max_strength = 2.0 + self.emotional_boost
        growth_rate = boost * (1.0 - (self.current_strength / max_strength))
        self.current_strength = min(max_strength, self.current_strength + growth_rate)
        
        return self.current_strength
    
    def decay(self) -> float:
        """Calculate memory decay based on time and access patterns."""
        now = datetime.now()
        time_since_access = (now - self.last_accessed).total_seconds()
        days_since_access = time_since_access / 86400  # Convert to days
        
        # Ebbinghaus forgetting curve with modifications
        # Base decay rate depends on importance and emotional strength
        base_retention = 0.5 + (self.importance * 0.1) + self.emotional_boost
        
        # Spaced repetition bonus - memories accessed at intervals decay slower
        spacing_bonus = self._calculate_spacing_bonus()
        
        # Calculate retention
        retention = base_retention * math.exp(-days_since_access / (7 * (1 + spacing_bonus)))
        
        # Apply decay
        self.current_strength *= retention
        
        # Minimum strength based on access count
        min_strength = min(0.1 * math.log(self.access_count + 1), 0.3)
        self.current_strength = max(min_strength, self.current_strength)
        
        return self.current_strength
    
    def _calculate_spacing_bonus(self) -> float:
        """Memories accessed at good intervals get bonus."""
        if len(self.reinforcement_history) < 2:
            return 0.0
            
        # Calculate intervals between accesses
        intervals = []
        for i in range(1, len(self.reinforcement_history)):
            interval = (self.reinforcement_history[i] - self.reinforcement_history[i-1]).total_seconds()
            intervals.append(interval)
        
        # Ideal spacing increases: 1 day, 3 days, 1 week, 2 weeks...
        ideal_intervals = [86400, 259200, 604800, 1209600]  # in seconds
        
        # Calculate how well actual intervals match ideal
        spacing_score = 0.0
        for i, interval in enumerate(intervals[:4]):  # Check first 4 intervals
            if i < len(ideal_intervals):
                # Score based on how close to ideal
                ratio = interval / ideal_intervals[i]
                if 0.5 <= ratio <= 2.0:  # Within 50-200% of ideal
                    spacing_score += 0.25
        
        return spacing_score
    
    @property
    def should_archive(self) -> bool:
        """Determine if memory should be moved to cold storage."""
        return (
            self.current_strength < 0.05 and
            self.access_count < 3 and
            (datetime.now() - self.last_accessed).days > 30
        )
    
    @property
    def vitality_score(self) -> float:
        """Combined score of strength, recency, and importance."""
        recency_score = 1.0 / (1.0 + (datetime.now() - self.last_accessed).days)
        access_score = math.log(self.access_count + 1) / 10.0
        
        return (
            self.current_strength * 0.4 +
            recency_score * 0.3 +
            access_score * 0.2 +
            (self.importance / 5.0) * 0.1
        )


class MemoryDecayManager:
    """Manages decay and reinforcement for all memories."""
    
    def __init__(self):
        self.memory_strengths: Dict[str, MemoryStrength] = {}
        self.decay_interval = 3600  # Check every hour
        self._decay_task = None
        
    async def start(self):
        """Start background decay process."""
        self._decay_task = asyncio.create_task(self._decay_loop())
        
    async def stop(self):
        """Stop decay process."""
        if self._decay_task:
            self._decay_task.cancel()
            try:
                await self._decay_task
            except asyncio.CancelledError:
                pass
    
    async def _decay_loop(self):
        """Background process to decay memories."""
        while True:
            try:
                await asyncio.sleep(self.decay_interval)
                await self._process_decay()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in decay loop: {e}")
    
    async def _process_decay(self):
        """Apply decay to all tracked memories."""
        archived = []
        
        for memory_id, strength in self.memory_strengths.items():
            strength.decay()
            
            if strength.should_archive:
                archived.append(memory_id)
        
        # Move to cold storage
        for memory_id in archived:
            await self._archive_memory(memory_id)
            del self.memory_strengths[memory_id]
        
        if archived:
            print(f"Archived {len(archived)} weak memories")
    
    async def _archive_memory(self, memory_id: str):
        """Move memory to cold storage."""
        # This would integrate with Engram's storage
        # For now, just mark as archived
        pass
    
    def track_memory(self, memory_id: str, initial_strength: float = 1.0,
                    importance: int = 3, emotional_boost: float = 0.0):
        """Start tracking a memory's strength."""
        if memory_id not in self.memory_strengths:
            self.memory_strengths[memory_id] = MemoryStrength(
                memory_id=memory_id,
                initial_strength=initial_strength,
                importance=importance,
                emotional_boost=emotional_boost
            )
    
    def reinforce(self, memory_id: str, boost: float = 0.1) -> Optional[float]:
        """Reinforce a memory when accessed."""
        if memory_id in self.memory_strengths:
            return self.memory_strengths[memory_id].reinforce(boost)
        return None
    
    def get_strength(self, memory_id: str) -> Optional[float]:
        """Get current strength of a memory."""
        if memory_id in self.memory_strengths:
            return self.memory_strengths[memory_id].current_strength
        return None
    
    def get_strong_memories(self, threshold: float = 0.7) -> List[str]:
        """Get memories above strength threshold."""
        return [
            memory_id
            for memory_id, strength in self.memory_strengths.items()
            if strength.current_strength >= threshold
        ]
    
    def get_memory_stats(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a memory."""
        if memory_id not in self.memory_strengths:
            return None
            
        strength = self.memory_strengths[memory_id]
        return {
            "current_strength": strength.current_strength,
            "access_count": strength.access_count,
            "days_since_access": (datetime.now() - strength.last_accessed).days,
            "vitality_score": strength.vitality_score,
            "should_archive": strength.should_archive,
            "spacing_bonus": strength._calculate_spacing_bonus()
        }


# Global decay manager instance
decay_manager = MemoryDecayManager()


# Integration with existing memory operations
async def remember_with_strength(memory_id: str, content: str, 
                                importance: int = 3, emotion: Optional[str] = None):
    """Store memory with strength tracking."""
    # Calculate emotional boost
    emotional_boost = 0.0
    if emotion:
        emotion_boosts = {
            "breakthrough": 0.5,
            "joy": 0.3,
            "frustration": 0.3,
            "surprise": 0.2,
            "flow": 0.2
        }
        emotional_boost = emotion_boosts.get(emotion, 0.0)
    
    # Track the memory
    decay_manager.track_memory(
        memory_id,
        importance=importance,
        emotional_boost=emotional_boost
    )
    
    # Store actual content (would integrate with Engram storage)
    # For now, just return success
    return {
        "memory_id": memory_id,
        "initial_strength": 1.0 + emotional_boost,
        "importance": importance
    }


async def recall_and_reinforce(memory_id: str) -> Optional[Dict[str, Any]]:
    """Recall memory and reinforce it."""
    # Reinforce on access
    new_strength = decay_manager.reinforce(memory_id)
    
    if new_strength:
        # Would fetch actual memory content from Engram
        return {
            "memory_id": memory_id,
            "strength": new_strength,
            "content": f"Memory content for {memory_id}"  # Placeholder
        }
    
    return None