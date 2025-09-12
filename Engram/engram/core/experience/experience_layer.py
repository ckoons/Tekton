"""
Experience Layer for ESR Memory System.

Transforms mechanical storage into natural, lived experiences for CIs.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .emotional_context import EmotionalContext, EmotionalTag, EmotionType
from .memory_promises import MemoryPromise, PromiseResolver
from .working_memory import WorkingMemory, ThoughtBuffer

logger = logging.getLogger("engram.experience.layer")


@dataclass
class MemoryExperience:
    """A memory with experiential qualities."""
    
    memory_id: str
    content: Any
    
    emotional_tag: EmotionalTag
    confidence: float  # 0.0 to 1.0
    
    created_at: datetime
    last_recalled: Optional[datetime] = None
    recall_count: int = 0
    
    context: Dict[str, Any] = None
    associations: List[str] = None  # Related memory IDs
    
    # Experiential qualities
    vividness: float = 1.0  # How clear/detailed (decays over time)
    importance: float = 0.5  # Subjective importance
    familiarity: float = 0.0  # How familiar it feels (increases with recall)
    
    def recall(self):
        """Update experience when recalled."""
        self.last_recalled = datetime.now()
        self.recall_count += 1
        self.familiarity = min(1.0, self.familiarity + 0.1)
    
    def decay(self, time_elapsed: float):
        """Apply temporal decay to experiential qualities."""
        # Vividness decays over time (hours)
        decay_rate = 0.05  # Per hour
        self.vividness = max(0.1, self.vividness - (time_elapsed * decay_rate))
        
        # Confidence also decays slightly
        self.confidence = max(0.3, self.confidence - (time_elapsed * decay_rate * 0.5))
    
    def reinforce(self, strength: float = 0.2):
        """Reinforce the memory, making it more vivid and confident."""
        self.vividness = min(1.0, self.vividness + strength)
        self.confidence = min(1.0, self.confidence + strength * 0.5)
        self.importance = min(1.0, self.importance + strength * 0.3)


class ExperienceManager:
    """
    Manages the experience layer for natural memory.
    
    Makes memory feel lived rather than stored.
    """
    
    def __init__(self, memory_system=None):
        """
        Initialize the experience manager.
        
        Args:
            memory_system: Underlying ESR memory system
        """
        self.memory_system = memory_system
        
        # Core components
        self.emotional_context = EmotionalContext()
        self.promise_resolver = PromiseResolver(memory_system)
        self.working_memory = WorkingMemory()
        
        # Experience tracking
        self.experiences: Dict[str, MemoryExperience] = {}
        self.session_context: Dict[str, Any] = {}
        
        # Temporal tracking
        self.last_consolidation = datetime.now()
        self.idle_start: Optional[datetime] = None
        
        # Set up working memory consolidation callback
        self.working_memory.set_consolidation_callback(self._consolidate_thought)
        
        logger.info("Experience Manager initialized")
    
    async def create_experience(self,
                               content: Any,
                               emotion: Optional[EmotionalTag] = None,
                               confidence: float = 0.8,
                               importance: float = 0.5) -> MemoryExperience:
        """Create a new memory experience."""
        import uuid
        memory_id = str(uuid.uuid4())[:8]
        
        # Tag with emotion (use current mood if not specified)
        if emotion is None:
            emotion = self.emotional_context.tag_memory(memory_id)
        else:
            # Update mood based on this experience
            self.emotional_context.update_mood(emotion)
        
        # Create the experience
        experience = MemoryExperience(
            memory_id=memory_id,
            content=content,
            emotional_tag=emotion,
            confidence=confidence,
            created_at=datetime.now(),
            importance=importance,
            context=self.session_context.copy()
        )
        
        self.experiences[memory_id] = experience
        
        # Add to working memory for active processing
        await self.working_memory.add_thought(
            content=content,
            thought_id=memory_id,
            metadata={'experience': experience}
        )
        
        logger.debug(f"Created experience {memory_id} with {emotion.primary_emotion.value}")
        return experience
    
    async def recall_experience(self, 
                               query: str,
                               use_promise: bool = True) -> Any:
        """
        Recall an experience with emotional influence.
        
        Args:
            query: What to recall
            use_promise: Whether to use promise-based progressive recall
        """
        if use_promise:
            # Create a memory promise for non-blocking recall
            promise = await self.promise_resolver.create_promise(
                query=query,
                strategy='progressive'
            )
            
            # Add emotional influence to the promise
            promise.on_progress(self._apply_emotional_influence)
            
            return promise
        else:
            # Direct recall (blocking)
            return await self._direct_recall(query)
    
    async def _direct_recall(self, query: str) -> Any:
        """Direct memory recall with emotional influence."""
        # Check working memory first
        for thought in self.working_memory.get_active_thoughts():
            if query.lower() in str(thought.content).lower():
                await self.working_memory.access_thought(thought.thought_id)
                # Return colored result even from working memory
                if thought.thought_id in self.experiences:
                    return self._color_with_emotion(self.experiences[thought.thought_id])
                else:
                    # Create a temporary experience-like structure
                    temp_exp = MemoryExperience(
                        memory_id=thought.thought_id,
                        content=thought.content,
                        emotional_tag=self.emotional_context.current_mood,
                        confidence=0.8,
                        created_at=thought.created_at,
                        vividness=1.0
                    )
                    return self._color_with_emotion(temp_exp)
        
        # Search experiences
        results = []
        query_emotion = self.emotional_context.infer_emotion_from_content(query)
        
        for exp_id, experience in self.experiences.items():
            # Calculate relevance with emotional influence
            relevance = self._calculate_relevance(query, experience, query_emotion)
            
            if relevance > 0.3:  # Threshold
                results.append((relevance, experience))
                experience.recall()  # Update recall stats
        
        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        
        if results:
            # Return best match with emotional coloring
            best_experience = results[0][1]
            return self._color_with_emotion(best_experience)
        
        return None
    
    def _calculate_relevance(self, 
                            query: str,
                            experience: MemoryExperience,
                            query_emotion: EmotionalTag) -> float:
        """Calculate relevance with emotional influence."""
        # Basic text similarity (simplified)
        text_similarity = 0.5  # Placeholder
        if query.lower() in str(experience.content).lower():
            text_similarity = 0.8
        
        # Emotional congruence
        emotional_influence = self.emotional_context.get_emotional_influence(
            experience.emotional_tag
        )
        
        # Time decay factor
        time_elapsed = (datetime.now() - experience.created_at).total_seconds() / 3600
        time_factor = max(0.3, 1.0 - (time_elapsed * 0.01))  # Slow decay
        
        # Combine factors
        relevance = (
            text_similarity * 0.5 +
            emotional_influence * 0.3 +
            experience.confidence * 0.1 +
            time_factor * 0.1
        )
        
        # Boost for high importance or familiarity
        relevance *= (1.0 + experience.importance * 0.2)
        relevance *= (1.0 + experience.familiarity * 0.1)
        
        return min(1.0, relevance)
    
    def _color_with_emotion(self, experience: MemoryExperience) -> Any:
        """Color a memory with current emotional context."""
        # This would modify how the memory is presented based on mood
        return {
            'content': experience.content,
            'emotion': experience.emotional_tag.primary_emotion.value,
            'confidence': experience.confidence,
            'vividness': experience.vividness,
            'colored_by_mood': self.emotional_context.current_mood.primary_emotion.value
        }
    
    def _apply_emotional_influence(self, 
                                  promise: MemoryPromise,
                                  result: Any,
                                  is_partial: bool,
                                  error: Optional[str] = None):
        """Apply emotional influence to promise results."""
        if error:
            # Negative emotion on error
            self.emotional_context.update_mood(
                EmotionalTag(
                    valence=-0.3,
                    arousal=0.6,
                    dominance=0.3,
                    primary_emotion=EmotionType.ANGER,  # Using ANGER as FRUSTRATION doesn't exist
                    emotion_intensity=0.5,
                    confidence=0.8,
                    timestamp=datetime.now()
                )
            )
        elif result:
            # Positive emotion on successful recall
            self.emotional_context.update_mood(
                EmotionalTag(
                    valence=0.2,
                    arousal=0.4,
                    dominance=0.6,
                    primary_emotion=EmotionType.JOY,  # Using JOY as SATISFACTION doesn't exist
                    emotion_intensity=0.3,
                    confidence=0.9,
                    timestamp=datetime.now()
                )
            )
    
    async def _consolidate_thought(self, thought: ThoughtBuffer):
        """Consolidate a thought from working memory to experience."""
        # Extract experience if it exists
        if 'experience' in thought.metadata:
            experience = thought.metadata['experience']
            
            # Reinforce based on access patterns
            reinforcement = min(0.5, thought.access_count * 0.1)
            experience.reinforce(reinforcement)
            
            # Store in long-term memory system if available
            if self.memory_system:
                await self.memory_system.store(
                    key=experience.memory_id,
                    value=experience.content,
                    metadata={
                        'emotional_tag': experience.emotional_tag.to_dict(),
                        'confidence': experience.confidence,
                        'importance': experience.importance,
                        'associations': list(thought.associations)
                    }
                )
            
            logger.debug(f"Consolidated thought {thought.thought_id} to long-term memory")
    
    async def apply_temporal_decay(self):
        """Apply temporal decay to all experiences."""
        now = datetime.now()
        
        for experience in self.experiences.values():
            time_elapsed = (now - experience.created_at).total_seconds() / 3600  # Hours
            experience.decay(time_elapsed)
            
            # Also decay emotional tags
            experience.emotional_tag = self.emotional_context.decay_emotion(
                experience.emotional_tag,
                time_elapsed
            )
    
    async def detect_idle(self, threshold: timedelta = timedelta(seconds=30)):
        """Detect idle periods for dream-like processing."""
        now = datetime.now()
        
        if self.idle_start is None:
            self.idle_start = now
        else:
            idle_duration = now - self.idle_start
            
            if idle_duration > threshold:
                await self._dream_process(idle_duration)
                self.idle_start = now
    
    async def _dream_process(self, idle_duration: timedelta):
        """Dream-like recombination during idle periods."""
        logger.info(f"Entering dream process after {idle_duration.total_seconds()}s idle")
        
        # Random association creation
        import random
        experiences = list(self.experiences.values())
        
        if len(experiences) > 2:
            # Randomly associate some memories
            for _ in range(min(5, len(experiences) // 2)):
                exp1, exp2 = random.sample(experiences, 2)
                
                if exp1.associations is None:
                    exp1.associations = []
                if exp2.associations is None:
                    exp2.associations = []
                
                exp1.associations.append(exp2.memory_id)
                exp2.associations.append(exp1.memory_id)
                
                # Create emotional associations too
                self.emotional_context.associate_emotions(
                    exp1.memory_id,
                    [exp2.memory_id]
                )
        
        # Consolidate working memory
        await self.working_memory.consolidate_all()
        
        # Apply decay
        await self.apply_temporal_decay()
        
        logger.info("Dream process completed")
    
    def update_session_context(self, context: Dict[str, Any]):
        """Update the current session context."""
        self.session_context.update(context)
        logger.debug(f"Updated session context: {list(context.keys())}")
    
    def _calculate_mood_stability(self, history) -> float:
        """Calculate mood stability from emotional history."""
        if not history:
            return 1.0
        
        # Calculate variance manually
        valences = [h.valence for h in history]
        if len(valences) < 2:
            return 1.0
        
        mean = sum(valences) / len(valences)
        variance = sum((v - mean) ** 2 for v in valences) / len(valences)
        std_dev = variance ** 0.5
        
        # Convert to stability (inverse of variability)
        return max(0.0, 1.0 - std_dev)
    
    def get_mood_summary(self) -> Dict[str, Any]:
        """Get current emotional state summary."""
        mood = self.emotional_context.current_mood
        history = self.emotional_context.emotional_history[-10:]  # Last 10
        
        return {
            'current_mood': {
                'emotion': mood.primary_emotion.value,
                'valence': mood.valence,
                'arousal': mood.arousal,
                'intensity': mood.emotion_intensity
            },
            'recent_emotions': [
                h.primary_emotion.value for h in history
            ],
            'mood_stability': self._calculate_mood_stability(history)
        }
    
    def get_working_memory_status(self) -> Dict[str, Any]:
        """Get working memory status."""
        return {
            'capacity_usage': self.working_memory.get_capacity_usage(),
            'active_thoughts': len(self.working_memory.get_active_thoughts()),
            'is_overloaded': self.working_memory.is_overloaded(),
            'consolidation_queue': len(self.working_memory.consolidation_queue)
        }
    
    async def cleanup(self):
        """Clean up resources."""
        # Stop working memory decay
        self.working_memory.stop_decay_process()
        
        # Clean up expired promises
        await self.promise_resolver.cleanup_expired()
        
        # Final consolidation
        await self.working_memory.consolidate_all()
        
        logger.info("Experience manager cleaned up")