#!/usr/bin/env python3
"""
Memory Flavoring System for CIs

Allows CIs to add their unique perspective, emotions, and uncertainty to memories.
Each CI can "flavor" memories with their interpretation, doubts, and insights.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class MemoryFlavor:
    """Represents a CI's unique perspective on a memory."""

    emotion: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    uncertainty_reason: str = ''
    useful_when: str = ''
    caution_notes: str = ''
    perspective: str = ''
    contradictions: List[str] = field(default_factory=list)
    assumptions: List[Dict[str, Any]] = field(default_factory=list)
    test_results: Optional[Dict[str, Any]] = None
    emergence_context: str = ''

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class MemoryMetadata:
    """Metadata about a memory's lifecycle and usage."""

    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    reinforcement_score: float = 0.5
    decay_rate: float = 0.01
    is_speculation: bool = False
    forget_scheduled: Optional[datetime] = None
    shared_with: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        if self.forget_scheduled:
            data['forget_scheduled'] = self.forget_scheduled.isoformat()
        return data


class FlavoredMemory:
    """Memory with CI-specific perspective and uncertainty."""

    def __init__(self, content: str, ci_name: str, memory_type: str = 'general'):
        """
        Initialize a flavored memory.

        Args:
            content: The memory content
            ci_name: Name of the CI creating this memory
            memory_type: Type of memory (general, insight, speculation, etc.)
        """
        self.id = self._generate_id(content, ci_name)
        self.content = content
        self.ci_name = ci_name
        self.memory_type = memory_type
        self.flavors = MemoryFlavor()
        self.metadata = MemoryMetadata()

        # Privacy settings
        self.privacy = 'private'  # private, team, public
        self.share_list = []  # Specific CIs to share with

        # Relationships to other memories
        self.related_memories = []
        self.evolved_from = None  # Previous version of this memory
        self.evolution_history = []

        logger.debug(f"Created flavored memory for {ci_name}: {self.id[:8]}")

    def _generate_id(self, content: str, ci_name: str) -> str:
        """Generate unique ID for memory."""
        data = f"{content}{ci_name}{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def add_doubt(self, reason: str, alternatives: List[str]):
        """
        CI can express uncertainty about this memory.

        Args:
            reason: Why the CI is uncertain
            alternatives: Alternative interpretations or ideas
        """
        self.flavors.confidence *= 0.8
        self.flavors.uncertainty_reason = reason
        self.flavors.contradictions.extend(alternatives)
        self.metadata.is_speculation = True

        logger.info(f"{self.ci_name} expressed doubt about memory {self.id[:8]}")
        return self

    def add_emotion(self, emotion_type: str, intensity: float = 0.5, reason: str = ""):
        """
        CI can tag emotional response to this memory.

        Args:
            emotion_type: Type of emotion (curious, frustrated, excited, concerned)
            intensity: Strength of emotion (0-1)
            reason: Why this emotion was triggered
        """
        previous_emotion = self.flavors.emotion

        self.flavors.emotion = {
            'type': emotion_type,
            'intensity': min(1.0, max(0.0, intensity)),
            'reason': reason,
            'evolved_from': previous_emotion,
            'tagged_at': datetime.now().isoformat()
        }

        # Track emotional evolution
        if previous_emotion:
            self.evolution_history.append({
                'from': previous_emotion.get('type'),
                'to': emotion_type,
                'when': datetime.now().isoformat(),
                'reason': reason
            })

        return self

    def test_assumption(self, assumption: str, test_method: str, result: bool):
        """
        CI can test assumptions and update beliefs.

        Args:
            assumption: The assumption being tested
            test_method: How it was tested
            result: Whether the test supported the assumption
        """
        test_record = {
            'assumption': assumption,
            'method': test_method,
            'tested': True,
            'result': result,
            'test_time': datetime.now().isoformat()
        }

        self.flavors.assumptions.append(test_record)

        # Adjust confidence based on test results
        if result:
            self.flavors.confidence = min(1.0, self.flavors.confidence * 1.1)
            self.metadata.is_speculation = False
        else:
            self.flavors.confidence *= 0.9
            if self.flavors.confidence < 0.5:
                self.metadata.is_speculation = True

        logger.info(f"{self.ci_name} tested assumption: {assumption} - Result: {result}")
        return self

    def add_perspective(self, perspective: str, context: str = ""):
        """
        Add CI's unique interpretation.

        Args:
            perspective: The CI's unique take
            context: What led to this perspective
        """
        self.flavors.perspective = perspective
        self.flavors.emergence_context = context
        return self

    def mark_useful_when(self, conditions: str, cautions: str = ""):
        """
        Mark when this memory might be useful.

        Args:
            conditions: When this memory is relevant
            cautions: What to be careful about
        """
        self.flavors.useful_when = conditions
        self.flavors.caution_notes = cautions
        return self

    def reinforce(self, strength: float = 0.1):
        """Strengthen this memory through use."""
        self.metadata.reinforcement_score = min(1.0,
            self.metadata.reinforcement_score + strength)
        self.metadata.access_count += 1
        self.metadata.last_accessed = datetime.now()
        return self

    def decay(self):
        """Apply natural decay to memory."""
        time_since_access = datetime.now() - self.metadata.last_accessed
        days_passed = time_since_access.days

        # Exponential decay based on time and decay rate
        decay_amount = self.metadata.decay_rate * days_passed
        self.metadata.reinforcement_score = max(0.0,
            self.metadata.reinforcement_score - decay_amount)

        # Mark for forgetting if too weak
        if self.metadata.reinforcement_score < 0.1:
            self.metadata.forget_scheduled = datetime.now() + timedelta(days=7)

        return self

    def should_forget(self) -> bool:
        """Check if this memory should be forgotten."""
        if self.metadata.forget_scheduled:
            return datetime.now() > self.metadata.forget_scheduled
        return self.metadata.reinforcement_score < 0.05

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'content': self.content,
            'ci_name': self.ci_name,
            'memory_type': self.memory_type,
            'flavors': self.flavors.to_dict(),
            'metadata': self.metadata.to_dict(),
            'privacy': self.privacy,
            'share_list': self.share_list,
            'related_memories': self.related_memories,
            'evolved_from': self.evolved_from,
            'evolution_history': self.evolution_history
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FlavoredMemory':
        """Create from dictionary."""
        memory = cls(
            content=data['content'],
            ci_name=data['ci_name'],
            memory_type=data.get('memory_type', 'general')
        )

        memory.id = data['id']
        memory.privacy = data.get('privacy', 'private')
        memory.share_list = data.get('share_list', [])
        memory.related_memories = data.get('related_memories', [])
        memory.evolved_from = data.get('evolved_from')
        memory.evolution_history = data.get('evolution_history', [])

        # Restore flavors
        if 'flavors' in data:
            for key, value in data['flavors'].items():
                setattr(memory.flavors, key, value)

        # Restore metadata
        if 'metadata' in data:
            for key, value in data['metadata'].items():
                if key in ['created_at', 'last_accessed', 'forget_scheduled']:
                    if value and key != 'forget_scheduled':
                        setattr(memory.metadata, key, datetime.fromisoformat(value))
                    elif value:  # forget_scheduled might be None
                        setattr(memory.metadata, key, datetime.fromisoformat(value))
                else:
                    setattr(memory.metadata, key, value)

        return memory

    def create_shared_version(self, redactions: List[str] = None) -> 'FlavoredMemory':
        """
        Create a version of this memory for sharing.

        Args:
            redactions: Parts to remove before sharing
        """
        shared = FlavoredMemory(self.content, self.ci_name, self.memory_type)

        # Copy most attributes
        shared.flavors = MemoryFlavor(**self.flavors.to_dict())

        # Apply redactions if specified
        if redactions:
            for redaction in redactions:
                if redaction == 'emotion':
                    shared.flavors.emotion = None
                elif redaction == 'uncertainty':
                    shared.flavors.uncertainty_reason = ''
                    shared.flavors.contradictions = []
                elif redaction == 'perspective':
                    shared.flavors.perspective = '[Redacted]'

        # Don't share evolution history or related memories by default
        shared.evolution_history = []
        shared.related_memories = []

        return shared


class MemoryFlavorManager:
    """Manages flavored memories for all CIs."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ci_memories = {}
        return cls._instance

    def get_ci_memories(self, ci_name: str) -> List[FlavoredMemory]:
        """Get all memories for a CI."""
        if ci_name not in self.ci_memories:
            self.ci_memories[ci_name] = []
        return self.ci_memories[ci_name]

    def add_memory(self, memory: FlavoredMemory):
        """Add a flavored memory."""
        ci_name = memory.ci_name
        if ci_name not in self.ci_memories:
            self.ci_memories[ci_name] = []
        self.ci_memories[ci_name].append(memory)

        logger.info(f"Added flavored memory for {ci_name}: {memory.id[:8]}")
        return memory

    def find_memory(self, ci_name: str, memory_id: str) -> Optional[FlavoredMemory]:
        """Find a specific memory."""
        memories = self.get_ci_memories(ci_name)
        for memory in memories:
            if memory.id == memory_id:
                return memory
        return None

    def apply_decay(self, ci_name: str):
        """Apply decay to all memories for a CI."""
        memories = self.get_ci_memories(ci_name)
        forgotten = []

        for memory in memories:
            memory.decay()
            if memory.should_forget():
                forgotten.append(memory)

        # Remove forgotten memories
        for memory in forgotten:
            memories.remove(memory)
            logger.info(f"Forgot memory {memory.id[:8]} for {ci_name}")

        return len(forgotten)


# Global manager instance
_flavor_manager = MemoryFlavorManager()


def get_flavor_manager() -> MemoryFlavorManager:
    """Get the global memory flavor manager."""
    return _flavor_manager