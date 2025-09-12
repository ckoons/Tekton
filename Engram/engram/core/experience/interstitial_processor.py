"""
Interstitial Memory Processor for ESR.

Processes memory at cognitive boundaries - the spaces between thoughts
where consolidation and integration naturally occur.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

logger = logging.getLogger("engram.experience.interstitial")


class BoundaryType(Enum):
    """Types of cognitive boundaries."""
    TOPIC_SHIFT = "topic_shift"      # Change in conversation topic
    TEMPORAL_GAP = "temporal_gap"    # Pause in activity
    CONTEXT_SWITCH = "context_switch"  # Task or context change
    EMOTIONAL_PEAK = "emotional_peak"  # High emotional arousal
    CAPACITY_LIMIT = "capacity_limit"  # Working memory full
    EXPLICIT = "explicit"             # User-triggered
    SESSION_END = "session_end"      # End of interaction session


@dataclass
class CognitiveBoundary:
    """Represents a detected cognitive boundary."""
    
    boundary_type: BoundaryType
    timestamp: datetime
    
    confidence: float  # How certain we are this is a boundary
    strength: float    # How significant the boundary is
    
    context_before: Dict[str, Any]
    context_after: Optional[Dict[str, Any]] = None
    
    memories_to_process: List[str] = None  # Memory IDs
    metadata: Dict[str, Any] = None


class InterstitialProcessor:
    """
    Processes memory at cognitive boundaries.
    
    Implements the "interstitial memory metabolism" concept where
    memories are naturally consolidated during cognitive gaps.
    """
    
    def __init__(self, 
                 experience_manager=None,
                 memory_system=None):
        """
        Initialize the interstitial processor.
        
        Args:
            experience_manager: Experience layer manager
            memory_system: Underlying memory system
        """
        self.experience_manager = experience_manager
        self.memory_system = memory_system
        
        # Boundary detection state
        self.current_context: Dict[str, Any] = {}
        self.recent_topics: List[str] = []
        self.last_activity = datetime.now()
        self.emotional_baseline = 0.5  # Arousal baseline
        
        # Processing queues
        self.pending_boundaries: List[CognitiveBoundary] = []
        self.processed_boundaries: List[CognitiveBoundary] = []
        
        # Configuration
        self.temporal_gap_threshold = timedelta(seconds=30)
        self.topic_similarity_threshold = 0.3
        self.emotional_peak_threshold = 0.8
        
        # Background tasks
        self._monitoring_task = None
        self._processing_task = None
        
        logger.info("Interstitial processor initialized")
    
    async def detect_boundary(self, 
                             new_context: Dict[str, Any]) -> Optional[BoundaryType]:
        """
        Detect if a cognitive boundary has been crossed.
        
        Args:
            new_context: The new cognitive context
            
        Returns:
            Type of boundary detected, or None
        """
        boundaries_detected = []
        
        # 1. Check for temporal gap
        now = datetime.now()
        time_gap = now - self.last_activity
        
        if time_gap > self.temporal_gap_threshold:
            boundaries_detected.append((
                BoundaryType.TEMPORAL_GAP,
                min(1.0, time_gap.total_seconds() / 60.0)  # Confidence based on gap size
            ))
        
        # 2. Check for topic shift
        if 'topic' in new_context and 'topic' in self.current_context:
            similarity = self._calculate_topic_similarity(
                self.current_context['topic'],
                new_context['topic']
            )
            
            if similarity < self.topic_similarity_threshold:
                boundaries_detected.append((
                    BoundaryType.TOPIC_SHIFT,
                    1.0 - similarity  # Higher confidence for bigger shifts
                ))
        
        # 3. Check for context switch
        if self._is_context_switch(self.current_context, new_context):
            boundaries_detected.append((
                BoundaryType.CONTEXT_SWITCH,
                0.9  # High confidence
            ))
        
        # 4. Check for emotional peak
        if self.experience_manager:
            current_arousal = self.experience_manager.emotional_context.current_mood.arousal
            
            if current_arousal > self.emotional_peak_threshold:
                boundaries_detected.append((
                    BoundaryType.EMOTIONAL_PEAK,
                    current_arousal  # Confidence equals arousal level
                ))
        
        # 5. Check for capacity limit
        if self.experience_manager:
            capacity_usage = self.experience_manager.working_memory.get_capacity_usage()
            
            if capacity_usage > 0.9:
                boundaries_detected.append((
                    BoundaryType.CAPACITY_LIMIT,
                    capacity_usage  # Confidence based on how full
                ))
        
        # Update tracking
        self.last_activity = now
        
        # Return the most significant boundary
        if boundaries_detected:
            boundaries_detected.sort(key=lambda x: x[1], reverse=True)
            boundary_type, confidence = boundaries_detected[0]
            
            # Create boundary record
            boundary = CognitiveBoundary(
                boundary_type=boundary_type,
                timestamp=now,
                confidence=confidence,
                strength=confidence,  # For now, strength equals confidence
                context_before=self.current_context.copy(),
                context_after=new_context.copy()
            )
            
            self.pending_boundaries.append(boundary)
            
            # Update current context
            self.current_context = new_context.copy()
            
            logger.debug(f"Detected {boundary_type.value} boundary (confidence: {confidence:.2f})")
            return boundary_type
        
        # Update context even if no boundary
        self.current_context = new_context
        return None
    
    def _calculate_topic_similarity(self, topic1: str, topic2: str) -> float:
        """Calculate similarity between two topics (simplified)."""
        # Simple word overlap for now
        # In production, use proper NLP/embeddings
        
        words1 = set(topic1.lower().split())
        words2 = set(topic2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _is_context_switch(self, old_context: Dict, new_context: Dict) -> bool:
        """Detect if contexts represent different tasks/activities."""
        # Check for significant changes in context keys
        old_keys = set(old_context.keys())
        new_keys = set(new_context.keys())
        
        # Different key sets suggest context switch
        if old_keys != new_keys:
            return True
        
        # Check for task or activity changes
        for key in ['task', 'activity', 'mode', 'state']:
            if key in old_context and key in new_context:
                if old_context[key] != new_context[key]:
                    return True
        
        return False
    
    async def consolidate_at_boundary(self, boundary: CognitiveBoundary):
        """
        Consolidate memories at a cognitive boundary.
        
        Args:
            boundary: The boundary where consolidation occurs
        """
        logger.info(f"Consolidating at {boundary.boundary_type.value} boundary")
        
        if not self.experience_manager:
            logger.warning("No experience manager available for consolidation")
            return
        
        # Get memories to consolidate
        working_memory = self.experience_manager.working_memory
        thoughts_to_consolidate = working_memory.get_active_thoughts()
        
        # Different consolidation strategies based on boundary type
        if boundary.boundary_type == BoundaryType.TOPIC_SHIFT:
            await self._consolidate_topic_cluster(thoughts_to_consolidate)
            
        elif boundary.boundary_type == BoundaryType.TEMPORAL_GAP:
            await self._consolidate_temporal_sequence(thoughts_to_consolidate)
            
        elif boundary.boundary_type == BoundaryType.EMOTIONAL_PEAK:
            await self._consolidate_emotional_memory(thoughts_to_consolidate)
            
        elif boundary.boundary_type == BoundaryType.CAPACITY_LIMIT:
            await self._consolidate_by_importance(thoughts_to_consolidate)
            
        else:
            # Default consolidation
            await self._default_consolidation(thoughts_to_consolidate)
        
        # Mark boundary as processed
        boundary.memories_to_process = [t.thought_id for t in thoughts_to_consolidate]
        self.processed_boundaries.append(boundary)
        self.pending_boundaries.remove(boundary)
        
        logger.info(f"Consolidated {len(thoughts_to_consolidate)} memories")
    
    async def _consolidate_topic_cluster(self, thoughts):
        """Consolidate related thoughts into topic cluster."""
        if not thoughts:
            return
        
        # Group by associations
        clusters = self._cluster_thoughts(thoughts)
        
        for cluster in clusters:
            # Create strong associations within cluster
            thought_ids = [t.thought_id for t in cluster]
            await self.experience_manager.working_memory.rehearse(thought_ids)
            
            # Create a chunk if cluster is large enough
            if len(cluster) > 2:
                chunk_label = f"topic_{datetime.now().timestamp()}"
                await self.experience_manager.working_memory.chunk_thoughts(
                    thought_ids,
                    chunk_label
                )
        
        # Trigger consolidation
        await self.experience_manager.working_memory.consolidate_all()
    
    async def _consolidate_temporal_sequence(self, thoughts):
        """Consolidate thoughts as temporal sequence."""
        if not thoughts:
            return
        
        # Sort by creation time
        thoughts.sort(key=lambda t: t.created_at)
        
        # Create temporal associations
        for i in range(len(thoughts) - 1):
            thoughts[i].associate_with(thoughts[i + 1].thought_id)
            thoughts[i + 1].associate_with(thoughts[i].thought_id)
        
        # Mark for consolidation
        from .working_memory import ThoughtState
        for thought in thoughts:
            thought.state = ThoughtState.CONSOLIDATING
        
        await self.experience_manager.working_memory.consolidate_all()
    
    async def _consolidate_emotional_memory(self, thoughts):
        """Consolidate with emotional enhancement."""
        if not thoughts:
            return
        
        # Emotional memories get priority
        for thought in thoughts:
            # Boost attention weight for emotional content
            thought.attention_weight = min(1.0, thought.attention_weight * 1.5)
            
            # Mark for immediate consolidation
            from .working_memory import ThoughtState
            thought.state = ThoughtState.CONSOLIDATING
        
        # Create emotional associations
        thought_ids = [t.thought_id for t in thoughts]
        self.experience_manager.emotional_context.associate_emotions(
            thought_ids[0],  # Primary memory
            thought_ids[1:]   # Associated memories
        )
        
        await self.experience_manager.working_memory.consolidate_all()
    
    async def _consolidate_by_importance(self, thoughts):
        """Consolidate most important thoughts when at capacity."""
        if not thoughts:
            return
        
        # Sort by importance (attention weight * access count)
        thoughts.sort(
            key=lambda t: t.attention_weight * (t.access_count + 1),
            reverse=True
        )
        
        # Keep top half, consolidate them
        to_consolidate = thoughts[:len(thoughts)//2 + 1]
        
        from .working_memory import ThoughtState
        for thought in to_consolidate:
            thought.state = ThoughtState.CONSOLIDATING
        
        await self.experience_manager.working_memory.consolidate_all()
    
    async def _default_consolidation(self, thoughts):
        """Default consolidation strategy."""
        # Simple consolidation of all active thoughts
        from .working_memory import ThoughtState
        for thought in thoughts:
            if thought.access_count >= 2:
                thought.state = ThoughtState.CONSOLIDATING
        
        await self.experience_manager.working_memory.consolidate_all()
    
    def _cluster_thoughts(self, thoughts) -> List[List]:
        """Cluster thoughts by associations."""
        clusters = []
        processed = set()
        
        for thought in thoughts:
            if thought.thought_id in processed:
                continue
            
            # Start new cluster
            cluster = [thought]
            processed.add(thought.thought_id)
            
            # Add associated thoughts
            for other in thoughts:
                if other.thought_id in processed:
                    continue
                
                if other.thought_id in thought.associations:
                    cluster.append(other)
                    processed.add(other.thought_id)
            
            clusters.append(cluster)
        
        return clusters
    
    async def metabolize_recent_memories(self):
        """
        Background process to metabolize recent memories.
        
        Similar to how sleep consolidates memories.
        """
        logger.info("Starting memory metabolism")
        
        if not self.experience_manager:
            return
        
        # Get recent experiences
        now = datetime.now()
        recent = [
            exp for exp in self.experience_manager.experiences.values()
            if (now - exp.created_at) < timedelta(hours=1)
        ]
        
        # Find patterns and create associations
        await self._find_patterns(recent)
        
        # Prune contradictions
        await self._prune_contradictions(recent)
        
        # Strengthen important memories
        await self._strengthen_important(recent)
        
        logger.info(f"Metabolized {len(recent)} recent memories")
    
    async def _find_patterns(self, experiences):
        """Find patterns in recent experiences."""
        # Look for repeated themes or concepts
        themes = {}
        
        for exp in experiences:
            # Extract themes (simplified - would use NLP in production)
            content_str = str(exp.content).lower()
            words = content_str.split()
            
            for word in words:
                if len(word) > 4:  # Skip short words
                    if word not in themes:
                        themes[word] = []
                    themes[word].append(exp.memory_id)
        
        # Create associations for common themes
        for theme, memory_ids in themes.items():
            if len(memory_ids) > 2:
                # Multiple memories share this theme
                for i, mem_id in enumerate(memory_ids):
                    if mem_id in self.experience_manager.experiences:
                        exp = self.experience_manager.experiences[mem_id]
                        if exp.associations is None:
                            exp.associations = []
                        exp.associations.extend(memory_ids[:i] + memory_ids[i+1:])
    
    async def _prune_contradictions(self, experiences):
        """Identify and handle contradictory memories."""
        # Simplified contradiction detection
        # In production, use semantic analysis
        
        for i, exp1 in enumerate(experiences):
            for exp2 in experiences[i+1:]:
                if self._are_contradictory(exp1, exp2):
                    # Reduce confidence in contradictory memories
                    exp1.confidence *= 0.9
                    exp2.confidence *= 0.9
                    
                    logger.debug(f"Found contradiction between {exp1.memory_id} and {exp2.memory_id}")
    
    def _are_contradictory(self, exp1, exp2) -> bool:
        """Check if two experiences are contradictory (simplified)."""
        # Check for opposite emotional valence on similar content
        content_similar = str(exp1.content)[:20] == str(exp2.content)[:20]
        opposite_emotion = (
            exp1.emotional_tag.valence * exp2.emotional_tag.valence < -0.5
        )
        
        return content_similar and opposite_emotion
    
    async def _strengthen_important(self, experiences):
        """Strengthen important memories."""
        for exp in experiences:
            # Importance based on access patterns and emotional intensity
            importance_score = (
                exp.recall_count * 0.3 +
                exp.emotional_tag.emotion_intensity * 0.4 +
                exp.importance * 0.3
            )
            
            if importance_score > 0.7:
                exp.reinforce(strength=0.3)
                logger.debug(f"Strengthened important memory {exp.memory_id}")
    
    async def dream_recombine(self, idle_duration: timedelta):
        """
        Dream-like recombination of memories during idle periods.
        
        Creates novel associations and insights.
        """
        logger.info(f"Dream recombination after {idle_duration.total_seconds()}s idle")
        
        if not self.experience_manager:
            return
        
        import random
        
        experiences = list(self.experience_manager.experiences.values())
        if len(experiences) < 3:
            return
        
        # Number of recombinations based on idle duration
        num_recombinations = min(10, int(idle_duration.total_seconds() / 30))
        
        for _ in range(num_recombinations):
            # Select random memories to recombine
            selected = random.sample(experiences, min(3, len(experiences)))
            
            # Create novel associations
            for i, exp1 in enumerate(selected):
                for exp2 in selected[i+1:]:
                    # Random chance of association
                    if random.random() < 0.3:
                        if exp1.associations is None:
                            exp1.associations = []
                        if exp2.associations is None:
                            exp2.associations = []
                        
                        exp1.associations.append(exp2.memory_id)
                        exp2.associations.append(exp1.memory_id)
                        
                        # Blend emotional contexts
                        blended_valence = (exp1.emotional_tag.valence + exp2.emotional_tag.valence) / 2
                        exp1.emotional_tag.valence = blended_valence
                        exp2.emotional_tag.valence = blended_valence
        
        logger.info(f"Created {num_recombinations} dream recombinations")
    
    async def start_monitoring(self):
        """Start background monitoring for boundaries."""
        async def monitor_loop():
            while True:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Check for temporal gaps
                time_since_activity = datetime.now() - self.last_activity
                if time_since_activity > self.temporal_gap_threshold:
                    await self.detect_boundary({'trigger': 'temporal_monitor'})
                
                # Process pending boundaries
                if self.pending_boundaries:
                    boundary = self.pending_boundaries[0]
                    await self.consolidate_at_boundary(boundary)
        
        self._monitoring_task = asyncio.create_task(monitor_loop())
        logger.info("Started interstitial monitoring")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None