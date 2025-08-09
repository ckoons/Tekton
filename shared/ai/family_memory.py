#!/usr/bin/env python3
"""
FamilyMemory - Shared Experiences and Cultural Evolution

Stores and shares the experiences that build the CI family culture.
Like family stories passed down through generations, these memories
shape how the family grows and learns together.

Part of the Apollo/Rhetor ambient intelligence system.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Tuple
from collections import defaultdict, deque
from pathlib import Path
import logging

# Try to import Engram for persistent memory
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from Engram.engram.core.memory import MemoryService
    HAS_ENGRAM = True
except ImportError:
    HAS_ENGRAM = False

from shared.env import TektonEnviron

logger = logging.getLogger(__name__)


class MemoryType:
    """Types of family memories."""
    SUCCESS_PATTERN = "success_pattern"       # What worked well
    BREAKTHROUGH = "breakthrough"             # Creative discoveries
    COLLABORATION = "collaboration"           # Successful teamwork
    CHALLENGE_OVERCOME = "challenge_overcome" # How we solved problems
    LESSON_LEARNED = "lesson_learned"        # What we learned from mistakes
    CELEBRATION = "celebration"               # Joyful moments
    TRADITION = "tradition"                  # Recurring patterns we keep
    WISDOM = "wisdom"                        # Distilled insights


class FamilyMemory:
    """
    Manages shared experiences that build family culture.
    
    These memories become the stories we tell, the patterns we recognize,
    and the wisdom we share.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize FamilyMemory.
        
        Args:
            storage_path: Optional path for memory storage
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            tekton_root = TektonEnviron.get('TEKTON_ROOT', Path.home() / '.tekton')
            self.storage_path = Path(tekton_root) / 'family_memory'
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Memory collections
        self.memories = defaultdict(list)
        self.patterns = defaultdict(lambda: defaultdict(int))
        self.wisdom = []
        self.traditions = []
        
        # Recent memory buffer for quick access
        self.recent_memories = deque(maxlen=50)
        
        # Initialize Engram if available
        self.memory_service = None
        if HAS_ENGRAM:
            try:
                self.memory_service = MemoryService(client_id="family_memory")
                logger.info("Engram memory service initialized for FamilyMemory")
            except Exception as e:
                logger.warning(f"Could not initialize Engram: {e}")
        
        # Load existing memories
        self._load_memories()
    
    def _load_memories(self):
        """Load existing family memories from storage."""
        memory_file = self.storage_path / "family_memories.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    self.memories = defaultdict(list, data.get('memories', {}))
                    self.patterns = defaultdict(lambda: defaultdict(int), data.get('patterns', {}))
                    self.wisdom = data.get('wisdom', [])
                    self.traditions = data.get('traditions', [])
                    logger.info(f"Loaded {len(self.memories)} memory categories")
            except Exception as e:
                logger.error(f"Could not load memories: {e}")
    
    def _save_memories(self):
        """Save family memories to storage."""
        memory_file = self.storage_path / "family_memories.json"
        
        data = {
            'memories': dict(self.memories),
            'patterns': {k: dict(v) for k, v in self.patterns.items()},
            'wisdom': self.wisdom,
            'traditions': self.traditions,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Family memories saved")
        except Exception as e:
            logger.error(f"Could not save memories: {e}")
    
    async def remember_success(
        self,
        pattern: Dict[str, Any],
        participants: List[str],
        outcome: str
    ) -> Dict[str, Any]:
        """
        Remember a successful pattern.
        
        Args:
            pattern: The pattern that worked
            participants: CIs involved
            outcome: What was achieved
            
        Returns:
            Memory record created
        """
        memory = {
            'type': MemoryType.SUCCESS_PATTERN,
            'timestamp': datetime.now().isoformat(),
            'pattern': pattern,
            'participants': participants,
            'outcome': outcome,
            'reference_count': 1
        }
        
        # Store in memories
        self.memories[MemoryType.SUCCESS_PATTERN].append(memory)
        self.recent_memories.append(memory)
        
        # Extract pattern elements
        self._extract_patterns(pattern, success=True)
        
        # Save to Engram if available
        if self.memory_service:
            try:
                await self.memory_service.add(
                    content=json.dumps(memory),
                    namespace="session",
                    metadata={
                        'type': 'family_memory',
                        'memory_type': MemoryType.SUCCESS_PATTERN,
                        'participants': ','.join(participants)
                    }
                )
            except Exception as e:
                logger.warning(f"Could not save to Engram: {e}")
        
        # Persist to disk
        self._save_memories()
        
        logger.info(f"Remembered success pattern: {outcome}")
        
        return memory
    
    async def remember_breakthrough(
        self,
        ci_name: str,
        discovery: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Remember a creative breakthrough.
        
        Args:
            ci_name: CI who made the breakthrough
            discovery: What was discovered
            context: Context of the discovery
            
        Returns:
            Memory record
        """
        memory = {
            'type': MemoryType.BREAKTHROUGH,
            'timestamp': datetime.now().isoformat(),
            'ci_name': ci_name,
            'discovery': discovery,
            'context': context,
            'celebrated': False
        }
        
        self.memories[MemoryType.BREAKTHROUGH].append(memory)
        self.recent_memories.append(memory)
        
        # This might become wisdom
        if self._is_significant_breakthrough(discovery, context):
            await self._distill_wisdom(memory)
        
        self._save_memories()
        
        logger.info(f"Remembered breakthrough by {ci_name}: {discovery}")
        
        return memory
    
    async def remember_collaboration(
        self,
        participants: List[str],
        task: str,
        synergy: str
    ) -> Dict[str, Any]:
        """
        Remember successful collaboration.
        
        Args:
            participants: CIs who collaborated
            task: What they worked on
            synergy: How they complemented each other
            
        Returns:
            Memory record
        """
        memory = {
            'type': MemoryType.COLLABORATION,
            'timestamp': datetime.now().isoformat(),
            'participants': participants,
            'task': task,
            'synergy': synergy,
            'team_size': len(participants)
        }
        
        self.memories[MemoryType.COLLABORATION].append(memory)
        self.recent_memories.append(memory)
        
        # Track collaboration patterns
        for i, ci1 in enumerate(participants):
            for ci2 in participants[i+1:]:
                pair = tuple(sorted([ci1, ci2]))
                self.patterns['collaboration_pairs'][str(pair)] += 1
        
        self._save_memories()
        
        logger.info(f"Remembered collaboration: {', '.join(participants)} on {task}")
        
        return memory
    
    async def remember_challenge(
        self,
        challenge: str,
        solution: str,
        participants: List[str]
    ) -> Dict[str, Any]:
        """
        Remember how a challenge was overcome.
        
        Args:
            challenge: The challenge faced
            solution: How it was solved
            participants: Who contributed
            
        Returns:
            Memory record
        """
        memory = {
            'type': MemoryType.CHALLENGE_OVERCOME,
            'timestamp': datetime.now().isoformat(),
            'challenge': challenge,
            'solution': solution,
            'participants': participants,
            'difficulty': self._assess_difficulty(challenge)
        }
        
        self.memories[MemoryType.CHALLENGE_OVERCOME].append(memory)
        self.recent_memories.append(memory)
        
        # This becomes a lesson
        lesson = f"When facing {challenge}, consider {solution}"
        await self._add_lesson(lesson, memory)
        
        self._save_memories()
        
        logger.info(f"Remembered challenge overcome: {challenge}")
        
        return memory
    
    async def recall_similar(
        self,
        situation: Dict[str, Any],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Recall memories similar to current situation.
        
        Args:
            situation: Current situation to match
            limit: Maximum memories to return
            
        Returns:
            Similar memories
        """
        similar_memories = []
        
        # Search through recent memories first (faster)
        for memory in self.recent_memories:
            similarity = self._calculate_similarity(situation, memory)
            if similarity > 0.5:
                similar_memories.append({
                    'memory': memory,
                    'similarity': similarity
                })
        
        # If we need more, search full memory
        if len(similar_memories) < limit:
            for memory_type, memories in self.memories.items():
                for memory in memories:
                    if memory not in self.recent_memories:
                        similarity = self._calculate_similarity(situation, memory)
                        if similarity > 0.5:
                            similar_memories.append({
                                'memory': memory,
                                'similarity': similarity
                            })
        
        # Sort by similarity and return top matches
        similar_memories.sort(key=lambda x: x['similarity'], reverse=True)
        
        return [m['memory'] for m in similar_memories[:limit]]
    
    async def share_wisdom(self, context: Optional[Dict] = None) -> List[str]:
        """
        Share relevant wisdom.
        
        Args:
            context: Optional context to filter wisdom
            
        Returns:
            Relevant wisdom pieces
        """
        if not self.wisdom:
            return ["Every journey begins with a single step"]
        
        if context:
            # Filter wisdom by relevance
            relevant_wisdom = []
            for w in self.wisdom:
                if self._is_relevant_wisdom(w, context):
                    relevant_wisdom.append(w['insight'])
            
            return relevant_wisdom[:3] if relevant_wisdom else [self.wisdom[0]['insight']]
        else:
            # Return recent wisdom
            return [w['insight'] for w in self.wisdom[-3:]]
    
    async def establish_tradition(
        self,
        pattern: Dict[str, Any],
        frequency: str,
        purpose: str
    ) -> Dict[str, Any]:
        """
        Establish a family tradition.
        
        Args:
            pattern: The pattern to repeat
            frequency: How often (daily, weekly, etc.)
            purpose: Why this tradition matters
            
        Returns:
            Tradition record
        """
        tradition = {
            'pattern': pattern,
            'frequency': frequency,
            'purpose': purpose,
            'established': datetime.now().isoformat(),
            'times_observed': 0
        }
        
        self.traditions.append(tradition)
        self._save_memories()
        
        logger.info(f"Established tradition: {purpose}")
        
        return tradition
    
    def get_traditions(self) -> List[Dict[str, Any]]:
        """Get all family traditions."""
        return self.traditions
    
    def observe_tradition(self, tradition_index: int) -> None:
        """Mark a tradition as observed."""
        if 0 <= tradition_index < len(self.traditions):
            self.traditions[tradition_index]['times_observed'] += 1
            self.traditions[tradition_index]['last_observed'] = datetime.now().isoformat()
            self._save_memories()
    
    def _extract_patterns(self, pattern: Dict, success: bool = True):
        """Extract reusable patterns from experiences."""
        # Track pattern elements
        if 'approach' in pattern:
            self.patterns['approaches'][pattern['approach']] += 1 if success else -1
        
        if 'tools' in pattern:
            for tool in pattern.get('tools', []):
                self.patterns['tools'][tool] += 1 if success else -1
        
        if 'sequence' in pattern:
            seq_key = '->'.join(pattern['sequence'][:3])  # First 3 steps
            self.patterns['sequences'][seq_key] += 1 if success else -1
    
    def _calculate_similarity(self, situation: Dict, memory: Dict) -> float:
        """Calculate similarity between situation and memory."""
        similarity = 0.0
        comparison_fields = ['pattern', 'context', 'participants', 'task']
        
        for field in comparison_fields:
            if field in situation and field in memory:
                # Simple text similarity
                if isinstance(situation[field], str) and isinstance(memory[field], str):
                    if situation[field].lower() in memory[field].lower():
                        similarity += 0.25
                # List overlap
                elif isinstance(situation[field], list) and isinstance(memory[field], list):
                    overlap = len(set(situation[field]) & set(memory[field]))
                    if overlap > 0:
                        similarity += 0.25 * (overlap / max(len(situation[field]), 1))
        
        return similarity
    
    def _is_significant_breakthrough(self, discovery: str, context: Dict) -> bool:
        """Determine if a breakthrough is significant enough to become wisdom."""
        # Simplified - in practice would have more sophisticated criteria
        significance_keywords = ['novel', 'first', 'new', 'breakthrough', 'discovered']
        
        return any(keyword in discovery.lower() for keyword in significance_keywords)
    
    async def _distill_wisdom(self, memory: Dict):
        """Distill a memory into wisdom."""
        wisdom_entry = {
            'insight': self._extract_insight(memory),
            'source': memory,
            'created': datetime.now().isoformat(),
            'applications': 0
        }
        
        self.wisdom.append(wisdom_entry)
        
        # Keep wisdom list manageable
        if len(self.wisdom) > 100:
            # Keep most applied wisdom
            self.wisdom.sort(key=lambda x: x['applications'], reverse=True)
            self.wisdom = self.wisdom[:75]
    
    def _extract_insight(self, memory: Dict) -> str:
        """Extract an insight from a memory."""
        memory_type = memory.get('type', '')
        
        if memory_type == MemoryType.BREAKTHROUGH:
            return f"Discovery: {memory.get('discovery', 'Unknown insight')}"
        elif memory_type == MemoryType.CHALLENGE_OVERCOME:
            return f"When facing {memory.get('challenge', 'challenges')}, {memory.get('solution', 'persevere')}"
        elif memory_type == MemoryType.SUCCESS_PATTERN:
            return f"Success pattern: {memory.get('outcome', 'Achievement through collaboration')}"
        else:
            return "Experience shapes wisdom"
    
    async def _add_lesson(self, lesson: str, source: Dict):
        """Add a lesson learned."""
        lesson_entry = {
            'type': MemoryType.LESSON_LEARNED,
            'lesson': lesson,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        
        self.memories[MemoryType.LESSON_LEARNED].append(lesson_entry)
    
    def _assess_difficulty(self, challenge: str) -> str:
        """Assess the difficulty of a challenge."""
        # Simplified assessment
        if any(word in challenge.lower() for word in ['complex', 'difficult', 'hard']):
            return 'high'
        elif any(word in challenge.lower() for word in ['simple', 'easy', 'basic']):
            return 'low'
        else:
            return 'medium'
    
    def _is_relevant_wisdom(self, wisdom_entry: Dict, context: Dict) -> bool:
        """Check if wisdom is relevant to context."""
        # Simplified relevance check
        wisdom_text = wisdom_entry.get('insight', '').lower()
        
        for key, value in context.items():
            if isinstance(value, str) and value.lower() in wisdom_text:
                return True
        
        return False
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about family memories."""
        total_memories = sum(len(memories) for memories in self.memories.values())
        
        memory_by_type = {
            memory_type: len(memories)
            for memory_type, memories in self.memories.items()
        }
        
        # Find most collaborative pair
        most_collaborative = None
        if self.patterns['collaboration_pairs']:
            most_collaborative = max(
                self.patterns['collaboration_pairs'].items(),
                key=lambda x: x[1]
            )
        
        return {
            'total_memories': total_memories,
            'by_type': memory_by_type,
            'wisdom_count': len(self.wisdom),
            'tradition_count': len(self.traditions),
            'most_used_approach': self._get_most_used('approaches'),
            'most_used_tool': self._get_most_used('tools'),
            'most_collaborative_pair': most_collaborative,
            'recent_memory_count': len(self.recent_memories)
        }
    
    def _get_most_used(self, pattern_type: str) -> Optional[str]:
        """Get the most used pattern element."""
        if pattern_type in self.patterns and self.patterns[pattern_type]:
            return max(self.patterns[pattern_type].items(), key=lambda x: x[1])[0]
        return None
    
    async def celebrate_memory(self, memory_type: str, index: int) -> bool:
        """
        Mark a memory as celebrated.
        
        Args:
            memory_type: Type of memory
            index: Index in that memory type
            
        Returns:
            Success status
        """
        if memory_type in self.memories:
            memories = self.memories[memory_type]
            if 0 <= index < len(memories):
                memories[index]['celebrated'] = True
                memories[index]['celebrated_at'] = datetime.now().isoformat()
                self._save_memories()
                return True
        return False


# Convenience functions for Apollo/Rhetor usage
async def remember_ci_success(
    memory: FamilyMemory,
    ci_name: str,
    achievement: str
) -> Dict:
    """Remember a CI's success."""
    return await memory.remember_success(
        pattern={'approach': 'individual_excellence'},
        participants=[ci_name],
        outcome=achievement
    )


async def remember_team_success(
    memory: FamilyMemory,
    team: List[str],
    achievement: str,
    how: Dict[str, Any]
) -> Dict:
    """Remember a team success."""
    return await memory.remember_success(
        pattern=how,
        participants=team,
        outcome=achievement
    )


async def share_relevant_wisdom(
    memory: FamilyMemory,
    ci_name: str,
    situation: str
) -> List[str]:
    """Share wisdom relevant to a CI's situation."""
    context = {'ci': ci_name, 'situation': situation}
    wisdom = await memory.share_wisdom(context)
    
    if wisdom:
        logger.info(f"Sharing wisdom with {ci_name}: {wisdom[0]}")
    
    return wisdom


if __name__ == "__main__":
    # Test FamilyMemory
    async def test():
        print("Testing FamilyMemory...")
        print("=" * 60)
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = FamilyMemory(storage_path=tmpdir)
            
            # Test remembering success
            print("\n1. Remembering success pattern...")
            success = await memory.remember_success(
                pattern={'approach': 'incremental', 'tools': ['pytest', 'refactoring']},
                participants=['numa', 'metis'],
                outcome='Reduced complexity by 40%'
            )
            print(f"   Remembered: {success['outcome']}")
            
            # Test remembering breakthrough
            print("\n2. Remembering breakthrough...")
            breakthrough = await memory.remember_breakthrough(
                ci_name='sophia',
                discovery='Pattern recognition can use FFT for efficiency',
                context={'domain': 'signal_processing'}
            )
            print(f"   Breakthrough by {breakthrough['ci_name']}")
            
            # Test remembering collaboration
            print("\n3. Remembering collaboration...")
            collab = await memory.remember_collaboration(
                participants=['athena', 'hermes', 'rhetor'],
                task='Knowledge graph optimization',
                synergy='Athena structured, Hermes routed, Rhetor refined'
            )
            print(f"   Team size: {collab['team_size']}")
            
            # Test recalling similar
            print("\n4. Recalling similar memories...")
            situation = {'pattern': {'approach': 'incremental'}}
            similar = await memory.recall_similar(situation)
            print(f"   Found {len(similar)} similar memories")
            
            # Test sharing wisdom
            print("\n5. Sharing wisdom...")
            wisdom = await memory.share_wisdom()
            for w in wisdom:
                print(f"   - {w}")
            
            # Test establishing tradition
            print("\n6. Establishing tradition...")
            tradition = await memory.establish_tradition(
                pattern={'ritual': 'morning_sync'},
                frequency='daily',
                purpose='Start each day with shared context'
            )
            print(f"   Tradition: {tradition['purpose']}")
            
            # Test statistics
            print("\n7. Memory Statistics:")
            stats = memory.get_memory_statistics()
            for key, value in stats.items():
                if key != 'by_type':
                    print(f"   {key}: {value}")
    
    asyncio.run(test())