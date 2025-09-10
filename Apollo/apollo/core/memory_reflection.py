"""
Memory Reflection Trigger for Apollo.

This module provides automatic memory reflection and consolidation
for CI systems to maintain coherent, evolving memories.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from enum import Enum

logger = logging.getLogger("apollo.memory_reflection")


class ReflectionTriggerType(Enum):
    """Types of reflection triggers."""
    TIME_BASED = "time_based"      # Every N minutes
    EVENT_BASED = "event_based"     # After significant events
    THRESHOLD_BASED = "threshold"   # When memory reaches size
    EXPLICIT = "explicit"           # CI requests reflection
    CONTEXT_CHANGE = "context"      # Major context shift


class MemoryReflectionTrigger:
    """
    Manages memory reflection triggers for CIs.
    
    This class monitors memory patterns and triggers reflection
    when appropriate to maintain memory coherence and relevance.
    """
    
    def __init__(self,
                 cognitive_workflows,
                 ci_id: str = "apollo",
                 reflection_interval: int = 300,  # 5 minutes
                 memory_threshold: int = 100,
                 enable_auto_reflection: bool = True):
        """
        Initialize memory reflection trigger.
        
        Args:
            cognitive_workflows: CognitiveWorkflows instance
            ci_id: CI identifier
            reflection_interval: Time between reflections (seconds)
            memory_threshold: Number of memories before reflection
            enable_auto_reflection: Enable automatic reflection
        """
        self.cognitive_workflows = cognitive_workflows
        self.ci_id = ci_id
        self.reflection_interval = reflection_interval
        self.memory_threshold = memory_threshold
        self.enable_auto_reflection = enable_auto_reflection
        
        # State tracking
        self.last_reflection = datetime.now()
        self.memory_count_since_reflection = 0
        self.recent_memories: List[str] = []
        self.context_shifts: List[Dict[str, Any]] = []
        self.reflection_task = None
        self.running = False
        
        # Reflection statistics
        self.reflection_stats = {
            "total_reflections": 0,
            "memories_promoted": 0,
            "memories_forgotten": 0,
            "associations_created": 0,
            "patterns_identified": 0
        }
    
    async def start(self):
        """Start the reflection trigger monitoring."""
        if self.running:
            return
        
        self.running = True
        if self.enable_auto_reflection:
            self.reflection_task = asyncio.create_task(self._reflection_loop())
            logger.info(f"Memory reflection trigger started for {self.ci_id}")
    
    async def stop(self):
        """Stop the reflection trigger monitoring."""
        self.running = False
        if self.reflection_task:
            self.reflection_task.cancel()
            try:
                await self.reflection_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Memory reflection trigger stopped for {self.ci_id}")
    
    async def _reflection_loop(self):
        """Main reflection monitoring loop."""
        while self.running:
            try:
                # Check if reflection is needed
                trigger_type = await self.should_reflect()
                if trigger_type:
                    await self.trigger_reflection(trigger_type)
                
                # Sleep before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in reflection loop: {e}")
                await asyncio.sleep(30)  # Back off on error
    
    async def should_reflect(self) -> Optional[ReflectionTriggerType]:
        """
        Check if reflection should be triggered.
        
        Returns:
            Trigger type if reflection needed, None otherwise
        """
        # Time-based trigger
        time_since_reflection = datetime.now() - self.last_reflection
        if time_since_reflection.total_seconds() >= self.reflection_interval:
            return ReflectionTriggerType.TIME_BASED
        
        # Threshold-based trigger
        if self.memory_count_since_reflection >= self.memory_threshold:
            return ReflectionTriggerType.THRESHOLD_BASED
        
        # Context change trigger
        if len(self.context_shifts) >= 3:  # Multiple context shifts
            return ReflectionTriggerType.CONTEXT_CHANGE
        
        return None
    
    async def trigger_reflection(self, 
                                trigger_type: ReflectionTriggerType = ReflectionTriggerType.EXPLICIT):
        """
        Trigger memory reflection process.
        
        Args:
            trigger_type: Type of trigger causing reflection
        """
        logger.info(f"Triggering memory reflection for {self.ci_id} ({trigger_type.value})")
        
        try:
            # 1. Gather recent memories
            recent_memories = await self._gather_recent_memories()
            
            # 2. Synthesize patterns
            patterns = await self._synthesize_patterns(recent_memories)
            
            # 3. Update associations
            associations = await self._update_associations(recent_memories, patterns)
            
            # 4. Promote important memories
            promoted = await self._promote_memories(recent_memories, patterns)
            
            # 5. Forget irrelevant memories
            forgotten = await self._forget_memories(recent_memories)
            
            # Update statistics
            self.reflection_stats["total_reflections"] += 1
            self.reflection_stats["memories_promoted"] += len(promoted)
            self.reflection_stats["memories_forgotten"] += len(forgotten)
            self.reflection_stats["associations_created"] += len(associations)
            self.reflection_stats["patterns_identified"] += len(patterns)
            
            # Reset state
            self.last_reflection = datetime.now()
            self.memory_count_since_reflection = 0
            self.recent_memories.clear()
            self.context_shifts.clear()
            
            logger.info(f"Reflection complete: {len(promoted)} promoted, "
                       f"{len(forgotten)} forgotten, {len(associations)} associations")
            
        except Exception as e:
            logger.error(f"Error during reflection: {e}")
    
    async def _gather_recent_memories(self) -> List[Dict[str, Any]]:
        """Gather memories since last reflection."""
        if not self.cognitive_workflows:
            return []
        
        # Get recent memory IDs
        memory_ids = self.recent_memories[-100:]  # Last 100 memories
        
        memories = []
        for memory_id in memory_ids:
            try:
                memory = await self.cognitive_workflows.recall_thought(memory_id)
                if memory:
                    memories.append(memory)
            except Exception as e:
                logger.debug(f"Could not recall memory {memory_id}: {e}")
        
        return memories
    
    async def _synthesize_patterns(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns in recent memories."""
        patterns = []
        
        if len(memories) < 3:
            return patterns
        
        # Group by thought type
        type_groups = {}
        for memory in memories:
            thought_type = memory.get("thought_type", "unknown")
            if thought_type not in type_groups:
                type_groups[thought_type] = []
            type_groups[thought_type].append(memory)
        
        # Find recurring themes
        for thought_type, group_memories in type_groups.items():
            if len(group_memories) >= 3:
                patterns.append({
                    "type": "recurring_theme",
                    "thought_type": thought_type,
                    "count": len(group_memories),
                    "confidence": min(1.0, len(group_memories) / 10.0)
                })
        
        return patterns
    
    async def _update_associations(self, 
                                  memories: List[Dict[str, Any]], 
                                  patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create new associations between memories."""
        associations = []
        
        # Associate memories within patterns
        for pattern in patterns:
            if pattern["type"] == "recurring_theme":
                thought_type = pattern["thought_type"]
                related_memories = [m for m in memories 
                                   if m.get("thought_type") == thought_type]
                
                # Create bidirectional associations
                for i in range(len(related_memories) - 1):
                    associations.append({
                        "from": related_memories[i].get("id"),
                        "to": related_memories[i + 1].get("id"),
                        "type": "temporal_sequence",
                        "strength": pattern["confidence"]
                    })
        
        return associations
    
    async def _promote_memories(self, 
                               memories: List[Dict[str, Any]], 
                               patterns: List[Dict[str, Any]]) -> List[str]:
        """Promote important memories for long-term retention."""
        promoted = []
        
        for memory in memories:
            # Promote if part of a pattern
            in_pattern = any(p["thought_type"] == memory.get("thought_type") 
                           for p in patterns)
            
            # Promote if high confidence
            high_confidence = memory.get("confidence", 0) > 0.8
            
            if in_pattern or high_confidence:
                memory_id = memory.get("id")
                if memory_id:
                    promoted.append(memory_id)
                    # Update memory metadata
                    memory["promoted"] = True
                    memory["promotion_time"] = datetime.now().isoformat()
        
        return promoted
    
    async def _forget_memories(self, memories: List[Dict[str, Any]]) -> List[str]:
        """Mark irrelevant memories for forgetting."""
        forgotten = []
        
        for memory in memories:
            # Forget if low confidence and old
            low_confidence = memory.get("confidence", 1.0) < 0.3
            
            # Check age (if timestamp available)
            old_memory = False
            if "timestamp" in memory:
                try:
                    timestamp = datetime.fromisoformat(memory["timestamp"])
                    age = datetime.now() - timestamp
                    old_memory = age.total_seconds() > 3600  # Older than 1 hour
                except:
                    pass
            
            if low_confidence and old_memory:
                memory_id = memory.get("id")
                if memory_id:
                    forgotten.append(memory_id)
                    memory["forgotten"] = True
        
        return forgotten
    
    def record_memory(self, memory_id: str):
        """Record a new memory for tracking."""
        self.recent_memories.append(memory_id)
        self.memory_count_since_reflection += 1
    
    def record_context_shift(self, old_context: Dict[str, Any], new_context: Dict[str, Any]):
        """Record a context shift."""
        self.context_shifts.append({
            "timestamp": datetime.now().isoformat(),
            "old": old_context,
            "new": new_context
        })
    
    async def request_reflection(self):
        """Explicitly request a reflection."""
        await self.trigger_reflection(ReflectionTriggerType.EXPLICIT)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reflection statistics."""
        return {
            **self.reflection_stats,
            "last_reflection": self.last_reflection.isoformat(),
            "memories_since_reflection": self.memory_count_since_reflection,
            "context_shifts": len(self.context_shifts),
            "auto_reflection_enabled": self.enable_auto_reflection
        }