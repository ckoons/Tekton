"""
Emotional Context for ESR Memory System.

Provides emotional tagging and influence on memory formation and recall.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger("engram.experience.emotional")


class EmotionType(Enum):
    """Basic emotion categories based on psychological models."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"


@dataclass
class EmotionalTag:
    """Emotional metadata for a memory."""
    
    valence: float  # -1.0 (negative) to 1.0 (positive)
    arousal: float  # 0.0 (calm) to 1.0 (excited)
    dominance: float  # 0.0 (submissive) to 1.0 (dominant)
    
    primary_emotion: EmotionType
    emotion_intensity: float  # 0.0 to 1.0
    
    confidence: float  # 0.0 to 1.0 - how certain we are about this emotion
    
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate emotional values."""
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.dominance = max(0.0, min(1.0, self.dominance))
        self.emotion_intensity = max(0.0, min(1.0, self.emotion_intensity))
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'valence': self.valence,
            'arousal': self.arousal,
            'dominance': self.dominance,
            'primary_emotion': self.primary_emotion.value,
            'emotion_intensity': self.emotion_intensity,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalTag':
        """Create from dictionary."""
        return cls(
            valence=data['valence'],
            arousal=data['arousal'],
            dominance=data['dominance'],
            primary_emotion=EmotionType(data['primary_emotion']),
            emotion_intensity=data['emotion_intensity'],
            confidence=data['confidence'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            context=data.get('context')
        )
    
    @classmethod
    def neutral(cls) -> 'EmotionalTag':
        """Create a neutral emotional tag."""
        return cls(
            valence=0.0,
            arousal=0.3,  # Slight baseline arousal
            dominance=0.5,
            primary_emotion=EmotionType.NEUTRAL,
            emotion_intensity=0.0,
            confidence=1.0,
            timestamp=datetime.now()
        )


class EmotionalContext:
    """Manages emotional context for memories."""
    
    def __init__(self):
        self.current_mood = EmotionalTag.neutral()
        self.emotional_history: List[EmotionalTag] = []
        self.emotion_associations: Dict[str, List[str]] = {}  # memory_id -> related_ids
        
        logger.info("Emotional context initialized")
    
    def update_mood(self, emotion: EmotionalTag):
        """Update current emotional state."""
        # Blend with current mood (emotional inertia)
        blend_factor = 0.7  # How much new emotion affects mood
        
        self.current_mood.valence = (
            self.current_mood.valence * (1 - blend_factor) +
            emotion.valence * blend_factor
        )
        self.current_mood.arousal = (
            self.current_mood.arousal * (1 - blend_factor) +
            emotion.arousal * blend_factor
        )
        self.current_mood.dominance = (
            self.current_mood.dominance * (1 - blend_factor) +
            emotion.dominance * blend_factor
        )
        
        # Update primary emotion if new one is stronger
        if emotion.emotion_intensity > self.current_mood.emotion_intensity * 0.8:
            self.current_mood.primary_emotion = emotion.primary_emotion
            self.current_mood.emotion_intensity = emotion.emotion_intensity
        
        self.current_mood.timestamp = datetime.now()
        self.emotional_history.append(emotion)
        
        # Keep history bounded
        if len(self.emotional_history) > 100:
            self.emotional_history = self.emotional_history[-100:]
        
        logger.debug(f"Mood updated: {self.current_mood.primary_emotion.value} "
                    f"(v:{self.current_mood.valence:.2f}, "
                    f"a:{self.current_mood.arousal:.2f})")
    
    def tag_memory(self, memory_id: str, 
                   emotion: Optional[EmotionalTag] = None) -> EmotionalTag:
        """Tag a memory with emotional context."""
        if emotion is None:
            # Use current mood
            emotion = EmotionalTag(
                valence=self.current_mood.valence,
                arousal=self.current_mood.arousal,
                dominance=self.current_mood.dominance,
                primary_emotion=self.current_mood.primary_emotion,
                emotion_intensity=self.current_mood.emotion_intensity * 0.8,  # Slightly reduced
                confidence=0.9,  # High confidence in current mood
                timestamp=datetime.now()
            )
        
        logger.debug(f"Tagged memory {memory_id} with {emotion.primary_emotion.value}")
        return emotion
    
    def associate_emotions(self, memory_id: str, related_ids: List[str]):
        """Create emotional associations between memories."""
        if memory_id not in self.emotion_associations:
            self.emotion_associations[memory_id] = []
        
        self.emotion_associations[memory_id].extend(related_ids)
        
        # Bidirectional associations
        for related_id in related_ids:
            if related_id not in self.emotion_associations:
                self.emotion_associations[related_id] = []
            if memory_id not in self.emotion_associations[related_id]:
                self.emotion_associations[related_id].append(memory_id)
        
        logger.debug(f"Associated {memory_id} with {len(related_ids)} memories")
    
    def get_emotional_influence(self, query_emotion: EmotionalTag) -> float:
        """Calculate how much current emotion influences recall."""
        # Emotional congruence effect - similar emotions enhance recall
        valence_match = 1.0 - abs(self.current_mood.valence - query_emotion.valence)
        arousal_match = 1.0 - abs(self.current_mood.arousal - query_emotion.arousal)
        
        # Mood congruent memory: stronger effect for matching valence
        congruence = (valence_match * 0.6 + arousal_match * 0.4)
        
        # High arousal enhances all memory (yerkes-dodson law simplified)
        arousal_boost = min(self.current_mood.arousal * 0.3, 0.3)
        
        influence = congruence + arousal_boost
        return max(0.0, min(1.0, influence))
    
    def decay_emotion(self, emotion: EmotionalTag, time_elapsed: float) -> EmotionalTag:
        """Apply temporal decay to emotional intensity."""
        # Emotions decay over time (hours)
        decay_rate = 0.1  # Per hour
        decay_factor = max(0.0, 1.0 - (time_elapsed * decay_rate))
        
        decayed = EmotionalTag(
            valence=emotion.valence * decay_factor,
            arousal=emotion.arousal * decay_factor,
            dominance=emotion.dominance,  # Dominance doesn't decay as quickly
            primary_emotion=emotion.primary_emotion,
            emotion_intensity=emotion.emotion_intensity * decay_factor,
            confidence=emotion.confidence * 0.95,  # Confidence also decays slightly
            timestamp=emotion.timestamp,
            context=emotion.context
        )
        
        # If emotion has decayed significantly, shift toward neutral
        if decayed.emotion_intensity < 0.2:
            decayed.primary_emotion = EmotionType.NEUTRAL
        
        return decayed
    
    def infer_emotion_from_content(self, content: str) -> EmotionalTag:
        """Infer emotional context from content (simplified)."""
        # Simple keyword-based emotion detection
        # In production, this would use proper NLP/sentiment analysis
        
        content_lower = content.lower()
        
        # Emotion keywords (simplified)
        emotions = {
            EmotionType.JOY: ['happy', 'joy', 'excited', 'wonderful', 'great', 'amazing'],
            EmotionType.SADNESS: ['sad', 'unhappy', 'depressed', 'sorry', 'loss'],
            EmotionType.ANGER: ['angry', 'mad', 'furious', 'annoyed', 'frustrated'],
            EmotionType.FEAR: ['afraid', 'scared', 'worried', 'anxious', 'nervous'],
            EmotionType.SURPRISE: ['surprised', 'shocked', 'unexpected', 'sudden'],
            EmotionType.TRUST: ['trust', 'believe', 'confident', 'reliable', 'depend']
        }
        
        detected_emotion = EmotionType.NEUTRAL
        max_count = 0
        
        for emotion, keywords in emotions.items():
            count = sum(1 for keyword in keywords if keyword in content_lower)
            if count > max_count:
                max_count = count
                detected_emotion = emotion
        
        # Calculate intensity based on keyword density
        intensity = min(1.0, max_count * 0.3)
        
        # Map emotion to valence/arousal
        emotion_map = {
            EmotionType.JOY: (0.8, 0.7),
            EmotionType.SADNESS: (-0.7, 0.3),
            EmotionType.ANGER: (-0.6, 0.8),
            EmotionType.FEAR: (-0.5, 0.9),
            EmotionType.SURPRISE: (0.1, 0.9),
            EmotionType.TRUST: (0.5, 0.4),
            EmotionType.NEUTRAL: (0.0, 0.3)
        }
        
        valence, arousal = emotion_map[detected_emotion]
        
        return EmotionalTag(
            valence=valence * intensity,
            arousal=arousal,
            dominance=0.5,  # Neutral dominance for inferred
            primary_emotion=detected_emotion,
            emotion_intensity=intensity,
            confidence=0.5 if detected_emotion != EmotionType.NEUTRAL else 0.8,
            timestamp=datetime.now(),
            context={'inferred': True, 'keyword_count': max_count}
        )