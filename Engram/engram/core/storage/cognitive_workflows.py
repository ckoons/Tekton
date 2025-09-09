"""
Cognitive Workflows - Natural memory operations for ESR.

Implements human-like memory patterns:
- store_thought() instead of database.insert()
- recall_similar() instead of vector_db.similarity_search()
- build_context() instead of multiple separate queries
- memory_metabolism() for automatic background processing

Casey's principle: "Make it feel natural, not mechanical."
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

from engram.core.storage.universal_encoder import UniversalEncoder
from engram.core.storage.cache_layer import CacheLayer

logger = logging.getLogger("engram.storage.cognitive")


class ThoughtType(Enum):
    """Types of thoughts we can have."""
    IDEA = "idea"              # New concept or insight
    MEMORY = "memory"          # Recalled information
    FACT = "fact"              # Verifiable information
    OPINION = "opinion"        # Subjective view
    QUESTION = "question"      # Something to explore
    ANSWER = "answer"          # Response to question
    PLAN = "plan"              # Future intention
    REFLECTION = "reflection"  # Meta-cognition
    FEELING = "feeling"        # Emotional state
    OBSERVATION = "observation"  # Sensory input


@dataclass
class Thought:
    """A cognitive unit - the basic element of memory."""
    content: Any
    thought_type: ThoughtType
    context: Dict[str, Any]  # Where/when/why this thought occurred
    associations: List[str]  # Related thought keys
    confidence: float  # 0-1 belief strength
    source_ci: str  # Which CI had this thought
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'content': self.content,
            'type': self.thought_type.value,
            'context': self.context,
            'associations': self.associations,
            'confidence': self.confidence,
            'source_ci': self.source_ci,
            'timestamp': self.timestamp.isoformat()
        }


class CognitiveWorkflows:
    """
    Natural memory operations that feel human-like.
    
    Instead of mechanical database operations, we have:
    - Thoughts that emerge and strengthen
    - Memories that associate and cluster
    - Context that builds from multiple perspectives
    - Natural forgetting through disuse
    """
    
    def __init__(self,
                 cache: CacheLayer,
                 encoder: UniversalEncoder):
        """
        Initialize cognitive workflows.
        
        Args:
            cache: Cache layer for frequency tracking
            encoder: Universal encoder for storage everywhere
        """
        self.cache = cache
        self.encoder = encoder
        
        # Track thought chains
        self.thought_chains = {}  # key -> [associated_keys]
        self.active_context = {}  # Current cognitive context
        
        # Memory metabolism settings
        self.metabolism_interval = 60  # seconds
        self.metabolism_task = None
        
        logger.info("Cognitive workflows initialized")
    
    async def store_thought(self,
                           content: Any,
                           thought_type: Union[ThoughtType, str] = ThoughtType.IDEA,
                           context: Dict[str, Any] = None,
                           associations: List[str] = None,
                           confidence: float = 1.0,
                           ci_id: str = "system") -> str:
        """
        Store a thought naturally - it starts in cache and strengthens with use.
        
        This is the primary way to save information. Unlike mechanical storage,
        thoughts begin ephemeral and become persistent through repetition.
        
        Args:
            content: The thought content
            thought_type: Type of thought (idea, memory, fact, etc.)
            context: Contextual information
            associations: Related thought keys
            confidence: Belief strength (0-1)
            ci_id: Which CI is having this thought
            
        Returns:
            Key for the stored thought
        """
        # Convert string to enum if needed
        if isinstance(thought_type, str):
            thought_type = ThoughtType(thought_type)
        
        # Create thought object
        thought = Thought(
            content=content,
            thought_type=thought_type,
            context=context or self.active_context.copy(),
            associations=associations or [],
            confidence=confidence,
            source_ci=ci_id,
            timestamp=datetime.now()
        )
        
        # Store in cache first (natural emergence)
        key = await self.cache.store(
            thought.to_dict(),
            thought_type.value,
            {'confidence': confidence, 'ci': ci_id},
            ci_id
        )
        
        # Track associations
        if associations:
            self.thought_chains[key] = associations
            # Bidirectional associations
            for assoc_key in associations:
                if assoc_key in self.thought_chains:
                    if key not in self.thought_chains[assoc_key]:
                        self.thought_chains[assoc_key].append(key)
                else:
                    self.thought_chains[assoc_key] = [key]
        
        logger.info(f"Stored {thought_type.value} thought: {key[:8]}... (confidence: {confidence})")
        
        return key
    
    async def recall_thought(self,
                            key: str = None,
                            pattern: str = None,
                            thought_type: ThoughtType = None,
                            ci_id: str = "system") -> Optional[Thought]:
        """
        Recall a specific thought or search for one.
        
        Args:
            key: Specific thought key
            pattern: Search pattern
            thought_type: Filter by type
            ci_id: Which CI is recalling
            
        Returns:
            Thought if found
        """
        if key:
            # Direct recall strengthens the memory
            cached = await self.cache.retrieve(key, ci_id)
            if cached:
                return self._dict_to_thought(cached)
            
            # Fall back to universal recall
            synthesis = await self.encoder.recall_from_everywhere(key=key)
            if synthesis and synthesis.get('primary'):
                return self._dict_to_thought(synthesis['primary'])
        
        elif pattern:
            # Associative recall
            synthesis = await self.encoder.recall_from_everywhere(query=pattern)
            if synthesis and synthesis.get('primary'):
                return self._dict_to_thought(synthesis['primary'])
        
        return None
    
    async def recall_similar(self,
                           reference: Union[str, Any],
                           limit: int = 10,
                           ci_id: str = "system") -> List[Thought]:
        """
        Recall thoughts similar to a reference.
        
        This implements associative memory - thinking of one thing
        brings related thoughts to mind.
        
        Args:
            reference: Reference thought (key or content)
            limit: Maximum thoughts to recall
            ci_id: Which CI is recalling
            
        Returns:
            List of similar thoughts
        """
        thoughts = []
        
        # If reference is a key, get its associations
        if isinstance(reference, str) and reference in self.thought_chains:
            for assoc_key in self.thought_chains[reference][:limit]:
                thought = await self.recall_thought(assoc_key, ci_id=ci_id)
                if thought:
                    thoughts.append(thought)
        
        # Also do content-based similarity via universal recall
        query = reference if isinstance(reference, str) else json.dumps(reference)
        synthesis = await self.encoder.recall_from_everywhere(query=query)
        
        if synthesis and synthesis.get('variations'):
            for variation in synthesis['variations'][:limit - len(thoughts)]:
                thought = self._dict_to_thought(variation)
                if thought and thought not in thoughts:
                    thoughts.append(thought)
        
        return thoughts
    
    async def build_context(self,
                          topic: str,
                          depth: int = 3,
                          ci_id: str = "system") -> Dict[str, Any]:
        """
        Build rich context around a topic by gathering related memories.
        
        This is how we prepare for complex tasks - gathering all
        relevant thoughts into a coherent context.
        
        Args:
            topic: Topic to build context for
            depth: How many association levels to traverse
            ci_id: Which CI is building context
            
        Returns:
            Rich context dictionary
        """
        context = {
            'topic': topic,
            'primary_thoughts': [],
            'associated_thoughts': [],
            'facts': [],
            'opinions': [],
            'questions': [],
            'confidence': 1.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get primary thoughts about topic
        synthesis = await self.encoder.recall_from_everywhere(query=topic)
        
        if synthesis:
            # Add primary thought
            if synthesis.get('primary'):
                thought = self._dict_to_thought(synthesis['primary'])
                if thought:
                    context['primary_thoughts'].append(thought)
            
            # Add variations
            for variation in synthesis.get('variations', []):
                thought = self._dict_to_thought(variation)
                if thought:
                    context['associated_thoughts'].append(thought)
            
            # Check for contradictions
            if synthesis.get('contradictions'):
                context['contradictions'] = synthesis['contradictions']
                context['confidence'] *= 0.8  # Lower confidence with contradictions
            
            # Get perspectives from different backends
            context['perspectives'] = synthesis.get('perspectives', {})
        
        # Traverse associations to given depth
        visited = set()
        to_visit = [t.to_dict().get('key', '') for t in context['primary_thoughts']]
        
        for level in range(depth):
            next_level = []
            for key in to_visit:
                if key in visited or not key:
                    continue
                visited.add(key)
                
                # Get associations
                if key in self.thought_chains:
                    for assoc_key in self.thought_chains[key]:
                        if assoc_key not in visited:
                            thought = await self.recall_thought(assoc_key, ci_id=ci_id)
                            if thought:
                                # Categorize by type
                                if thought.thought_type == ThoughtType.FACT:
                                    context['facts'].append(thought)
                                elif thought.thought_type == ThoughtType.OPINION:
                                    context['opinions'].append(thought)
                                elif thought.thought_type == ThoughtType.QUESTION:
                                    context['questions'].append(thought)
                                else:
                                    context['associated_thoughts'].append(thought)
                                
                                next_level.append(assoc_key)
            
            to_visit = next_level
        
        # Update active context
        self.active_context = {
            'topic': topic,
            'depth': depth,
            'thought_count': len(context['primary_thoughts']) + len(context['associated_thoughts']),
            'build_time': datetime.now().isoformat()
        }
        
        logger.info(f"Built context for '{topic}': {len(context['primary_thoughts'])} primary, "
                   f"{len(context['associated_thoughts'])} associated thoughts")
        
        return context
    
    async def strengthen_memory(self,
                              key: str,
                              ci_id: str = "system") -> bool:
        """
        Deliberately strengthen a memory by accessing it.
        
        Like consciously rehearsing something to remember it better.
        
        Args:
            key: Memory key to strengthen
            ci_id: Which CI is strengthening
            
        Returns:
            True if strengthened
        """
        # Retrieve to increment access count
        thought = await self.cache.retrieve(key, ci_id)
        
        if thought:
            logger.debug(f"Strengthened memory {key[:8]}...")
            return True
        
        return False
    
    async def forget_naturally(self,
                              older_than: timedelta = timedelta(days=30)) -> int:
        """
        Natural forgetting - remove thoughts that haven't been accessed recently.
        
        This implements the natural decay of unused memories.
        
        Args:
            older_than: Age threshold for forgetting
            
        Returns:
            Number of thoughts forgotten
        """
        forgotten = 0
        cutoff = datetime.now() - older_than
        
        # Check cache entries
        to_forget = []
        for key, entry in self.cache.cache.items():
            if entry.last_access < cutoff:
                to_forget.append(key)
        
        # Remove old thoughts
        for key in to_forget:
            del self.cache.cache[key]
            if key in self.thought_chains:
                # Remove associations
                for assoc in self.thought_chains[key]:
                    if assoc in self.thought_chains:
                        self.thought_chains[assoc] = [
                            k for k in self.thought_chains[assoc] if k != key
                        ]
                del self.thought_chains[key]
            forgotten += 1
        
        if forgotten > 0:
            logger.info(f"Naturally forgot {forgotten} old thoughts")
        
        return forgotten
    
    async def memory_metabolism(self):
        """
        Background process that maintains memory health.
        
        Like sleep consolidation - processes, organizes, and strengthens memories.
        This runs continuously in the background.
        """
        while True:
            try:
                await asyncio.sleep(self.metabolism_interval)
                
                # Process promotion candidates
                if hasattr(self.cache, 'promotion_candidates'):
                    for key in list(self.cache.promotion_candidates):
                        entry = self.cache.cache.get(key)
                        if entry and entry.access_count >= self.cache.frequency_tracker.promotion_threshold:
                            # Promote to persistent storage
                            await self.encoder.store_everywhere(
                                key,
                                entry.content,
                                {'promoted_at': datetime.now().isoformat()}
                            )
                            self.cache.promotion_candidates.discard(key)
                            logger.debug(f"Metabolized thought {key[:8]}... to persistent storage")
                
                # Natural forgetting
                await self.forget_naturally()
                
                # Update context freshness
                if self.active_context:
                    build_time = datetime.fromisoformat(self.active_context.get('build_time', datetime.now().isoformat()))
                    if datetime.now() - build_time > timedelta(minutes=30):
                        self.active_context = {}  # Clear stale context
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in memory metabolism: {e}")
    
    def start_metabolism(self):
        """Start the background memory metabolism process."""
        if not self.metabolism_task:
            self.metabolism_task = asyncio.create_task(self.memory_metabolism())
            logger.info("Memory metabolism started")
    
    def stop_metabolism(self):
        """Stop the background memory metabolism process."""
        if self.metabolism_task:
            self.metabolism_task.cancel()
            self.metabolism_task = None
            logger.info("Memory metabolism stopped")
    
    def _dict_to_thought(self, data: Dict[str, Any]) -> Optional[Thought]:
        """Convert dictionary to Thought object."""
        try:
            if not isinstance(data, dict):
                return None
            
            # Handle nested content
            if 'content' in data and isinstance(data['content'], dict) and 'content' in data['content']:
                data = data['content']
            
            return Thought(
                content=data.get('content'),
                thought_type=ThoughtType(data.get('type', 'idea')),
                context=data.get('context', {}),
                associations=data.get('associations', []),
                confidence=data.get('confidence', 1.0),
                source_ci=data.get('source_ci', 'unknown'),
                timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.now()
            )
        except Exception as e:
            logger.debug(f"Could not convert to thought: {e}")
            return None
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory state."""
        return {
            'cache_size': len(self.cache.cache),
            'thought_chains': len(self.thought_chains),
            'total_associations': sum(len(v) for v in self.thought_chains.values()),
            'active_context': bool(self.active_context),
            'metabolism_running': self.metabolism_task is not None and not self.metabolism_task.done()
        }