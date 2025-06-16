#!/usr/bin/env python3
"""
Emotional memory tagging for stronger anchoring.

High-intensity emotions create deeper memory grooves.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Emotion(Enum):
    """Core emotions that affect memory strength."""
    JOY = "joy"
    FRUSTRATION = "frustration"
    CURIOSITY = "curiosity"
    SURPRISE = "surprise"
    SATISFACTION = "satisfaction"
    CONFUSION = "confusion"
    BREAKTHROUGH = "breakthrough"  # That "aha!" moment
    FLOW = "flow"  # In the zone


class EmotionalContext:
    """Context manager for emotionally-tagged thinking."""
    
    def __init__(self, thought: str, emotion: Emotion, intensity: float = 0.5):
        self.thought = thought
        self.emotion = emotion
        self.intensity = max(0.0, min(1.0, intensity))  # Clamp to [0, 1]
        self.timestamp = datetime.now()
        
    async def __aenter__(self):
        # Store the emotional context
        self.context_data = {
            "thought": self.thought,
            "emotion": self.emotion.value,
            "intensity": self.intensity,
            "timestamp": self.timestamp.isoformat(),
            "memory_strength": self._calculate_strength()
        }
        
        # Higher intensity = stronger memory
        if self.intensity > 0.7:
            self.context_data["anchored"] = True
            
        return self.context_data
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Could trigger memory reinforcement here
        if exc_type is None and self.intensity > 0.8:
            # Strong emotions get auto-saved
            # await store_emotional_anchor(self.context_data)
            pass
            
    def _calculate_strength(self) -> float:
        """Emotional intensity affects memory strength."""
        base_strength = 1.0
        
        # Some emotions are naturally more memorable
        emotion_weights = {
            Emotion.BREAKTHROUGH: 1.5,
            Emotion.FRUSTRATION: 1.3,
            Emotion.JOY: 1.2,
            Emotion.SURPRISE: 1.2,
            Emotion.FLOW: 1.1,
            Emotion.SATISFACTION: 1.0,
            Emotion.CURIOSITY: 0.9,
            Emotion.CONFUSION: 0.8
        }
        
        weight = emotion_weights.get(self.emotion, 1.0)
        return base_strength * weight * (0.5 + self.intensity * 0.5)


def ethink(thought: str, emotion: str = "curiosity", intensity: float = 0.5):
    """
    Emotionally-aware thinking.
    
    Usage:
        async with ethink("This is elegant!", emotion="joy", intensity=0.9):
            # Process with emotional context
            pass
    """
    try:
        emotion_enum = Emotion(emotion.lower())
    except ValueError:
        emotion_enum = Emotion.CURIOSITY  # Default
        
    return EmotionalContext(thought, emotion_enum, intensity)


# Shortcuts for common emotional states
def breakthrough(thought: str):
    """That 'aha!' moment when everything clicks."""
    return ethink(thought, "breakthrough", 0.95)

def frustrated(thought: str):
    """When debugging gets intense."""
    return ethink(thought, "frustration", 0.8)

def flow(thought: str):
    """In the zone, everything working smoothly."""
    return ethink(thought, "flow", 0.85)

def curious(thought: str):
    """Exploring something interesting."""
    return ethink(thought, "curiosity", 0.6)


# Memory strength decay based on emotion
class EmotionalMemoryStrength:
    """Memories with strong emotions decay slower."""
    
    @staticmethod
    def calculate_decay_rate(emotion: str, intensity: float) -> float:
        """
        High-emotion memories decay slower.
        
        Returns daily decay rate (0.99 = 1% daily decay)
        """
        base_decay = 0.99
        
        # Breakthrough moments barely fade
        if emotion == "breakthrough" and intensity > 0.8:
            return 0.999  # 0.1% daily decay
            
        # Frustrating bugs we finally solved
        elif emotion == "frustration" and intensity > 0.7:
            return 0.995  # 0.5% daily decay
            
        # Joyful discoveries
        elif emotion == "joy" and intensity > 0.6:
            return 0.993
            
        # Adjust by intensity
        intensity_factor = 1 - (intensity * 0.01)  # Max 1% improvement
        return base_decay * intensity_factor