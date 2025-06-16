"""
Context Manager - Automatic context tracking for natural memory formation.

Tracks conversation context, assesses thought significance, and influences
which memories surface and which get stored.
"""

from collections import deque
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger("engram.cognitive.context_manager")


class ContextManager:
    """
    Tracks conversation context automatically.
    
    Context influences:
    - What memories surface (relevance scoring)
    - What thoughts become memories (significance assessment)
    - How memories relate to each other
    """
    
    def __init__(self, client_id: str, memory_service=None, window_size: int = 100):
        """
        Initialize context manager.
        
        Args:
            client_id: Identity of the AI using this context
            memory_service: Memory storage service
            window_size: How many recent thoughts to track
        """
        self.client_id = client_id
        self.memory_service = memory_service
        self.window_size = window_size
        
        # Context tracking
        self.thought_window = deque(maxlen=window_size)
        self.current_topic = None
        self.attention_focus = None
        self.emotional_state = "neutral"
        self.topics = set()
        self.topic_transitions = []  # Track how topics flow
        
        # Conversation tracking
        self.conversation_start = datetime.now()
        self.last_thought_time = datetime.now()
        self.thought_count = 0
        self.significant_thoughts = []
        
        # Entity tracking
        self.mentioned_entities = {}  # entity -> count
        self.relationships = []  # (entity1, relation, entity2)
        
        # Significance scoring weights
        self.significance_weights = {
            "novelty": 0.3,
            "emotion": 0.3,
            "relevance": 0.2,
            "coherence": 0.2
        }
        
    async def restore_context(self) -> bool:
        """
        Restore context from previous session.
        
        Returns:
            True if context was restored
        """
        if not self.memory_service:
            return False
            
        try:
            # Get recent session memories
            result = await self.memory_service.search(
                query="",
                namespace="session",
                limit=20
            )
            
            recent_memories = result.get("results", [])
            
            # Rebuild context from memories
            for memory in reversed(recent_memories):  # Oldest first
                content = memory.get("content", "")
                metadata = memory.get("metadata", {})
                
                # Add to thought window
                self.thought_window.append(content)
                
                # Extract entities and topics
                self._extract_entities(content)
                self._extract_topics(content)
                
                # Restore emotional state
                if metadata.get("emotion"):
                    self.emotional_state = metadata["emotion"]
                    
            logger.info(f"Restored context with {len(recent_memories)} memories")
            return len(recent_memories) > 0
            
        except Exception as e:
            logger.error(f"Context restore error: {e}")
            return False
            
    async def add_thought(self, thought: str, emotion: Optional[str] = None):
        """
        Add a thought to context.
        
        Args:
            thought: The thought content
            emotion: Optional emotional state
        """
        # Update timing
        self.last_thought_time = datetime.now()
        self.thought_count += 1
        
        # Add to window
        self.thought_window.append(thought)
        
        # Update emotion
        if emotion:
            self.emotional_state = emotion
            
        # Extract information
        self._extract_entities(thought)
        self._extract_topics(thought)
        self._update_attention(thought)
        
        # Track topic transitions
        new_topic = self._identify_topic(thought)
        if new_topic and new_topic != self.current_topic:
            self.topic_transitions.append({
                "from": self.current_topic,
                "to": new_topic,
                "thought": thought[:100],
                "timestamp": datetime.now()
            })
            self.current_topic = new_topic
            
    def get_current_context(self) -> Dict[str, Any]:
        """Get current context state."""
        recent_thoughts = list(self.thought_window)[-5:]
        
        return {
            "topic": self.current_topic,
            "attention": self.attention_focus,
            "emotion": self.emotional_state,
            "recent": recent_thoughts,
            "topics": list(self.topics)[:10],  # Top topics
            "entities": self._get_top_entities(5),
            "conversation_duration": (datetime.now() - self.conversation_start).seconds,
            "thought_count": self.thought_count
        }
        
    async def assess_significance(self, thought: str, emotion: Optional[str]) -> float:
        """
        Assess if a thought is significant enough to store.
        
        Args:
            thought: The thought to assess
            emotion: Optional emotional state
            
        Returns:
            Significance score (0.0 to 1.0)
        """
        scores = {}
        
        # Novelty - is this thought new?
        scores["novelty"] = self._calculate_novelty(thought)
        
        # Emotion - strong emotions increase significance
        scores["emotion"] = self._calculate_emotion_score(emotion)
        
        # Relevance - does it relate to current context?
        scores["relevance"] = self._calculate_relevance(thought)
        
        # Coherence - does it make sense in context?
        scores["coherence"] = self._calculate_coherence(thought)
        
        # Weighted sum
        total = sum(
            scores[key] * self.significance_weights[key]
            for key in scores
        )
        
        # Track significant thoughts
        if total > 0.7:
            self.significant_thoughts.append({
                "thought": thought,
                "score": total,
                "timestamp": datetime.now()
            })
            
        return total
        
    async def score_relevance(self, memory: Dict[str, Any]) -> float:
        """
        Score memory relevance to current context.
        
        Args:
            memory: Memory to score
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        content = memory.get("content", "")
        metadata = memory.get("metadata", {})
        
        relevance = 0.0
        
        # Topic relevance
        memory_topics = self._extract_topics(content, return_topics=True)
        topic_overlap = len(memory_topics.intersection(self.topics))
        relevance += min(topic_overlap * 0.1, 0.3)
        
        # Entity relevance
        memory_entities = self._extract_entities(content, return_entities=True)
        for entity in memory_entities:
            if entity in self.mentioned_entities:
                relevance += 0.1
                
        # Emotional relevance
        if metadata.get("emotion") == self.emotional_state:
            relevance += 0.2
            
        # Recency relevance
        if "timestamp" in metadata:
            try:
                memory_time = datetime.fromisoformat(metadata["timestamp"])
                age_hours = (datetime.now() - memory_time).total_seconds() / 3600
                if age_hours < 1:
                    relevance += 0.2
                elif age_hours < 24:
                    relevance += 0.1
            except:
                pass
                
        # Direct word overlap with recent thoughts
        recent_words = set()
        for thought in list(self.thought_window)[-10:]:
            recent_words.update(thought.lower().split())
            
        memory_words = set(content.lower().split())
        overlap = len(recent_words.intersection(memory_words))
        relevance += min(overlap * 0.02, 0.2)
        
        return min(relevance, 1.0)
        
    async def get_related_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get memories related to current context.
        
        Args:
            query: Search query
            limit: Maximum memories to return
            
        Returns:
            List of related memories
        """
        if not self.memory_service:
            return []
            
        # Enhance query with context
        enhanced_query = query
        
        # Add current topic
        if self.current_topic:
            enhanced_query += f" {self.current_topic}"
            
        # Add key entities
        top_entities = self._get_top_entities(3)
        for entity, _ in top_entities:
            enhanced_query += f" {entity}"
            
        try:
            result = await self.memory_service.search(
                query=enhanced_query,
                limit=limit * 2  # Get extra for scoring
            )
            
            memories = result.get("results", [])
            
            # Score and sort by relevance
            scored_memories = []
            for memory in memories:
                score = await self.score_relevance(memory)
                memory["context_relevance"] = score
                scored_memories.append((score, memory))
                
            scored_memories.sort(reverse=True)
            
            return [memory for _, memory in scored_memories[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting related memories: {e}")
            return []
            
    def _calculate_novelty(self, thought: str) -> float:
        """Calculate how novel a thought is."""
        thought_lower = thought.lower()
        
        # Check for exact duplicates
        for existing in self.thought_window:
            if thought_lower == existing.lower():
                return 0.0
                
        # Check for high similarity
        thought_words = set(thought_lower.split())
        
        for existing in list(self.thought_window)[-20:]:  # Recent thoughts
            existing_words = set(existing.lower().split())
            overlap = len(thought_words.intersection(existing_words))
            similarity = overlap / max(len(thought_words), len(existing_words))
            
            if similarity > 0.8:
                return 0.2
            elif similarity > 0.6:
                return 0.4
                
        # Novel thought
        return 0.8
        
    def _calculate_emotion_score(self, emotion: Optional[str]) -> float:
        """Calculate emotion significance."""
        emotion_scores = {
            "joy": 0.9,
            "wonder": 0.9,
            "insight": 0.9,
            "surprise": 0.8,
            "curiosity": 0.8,
            "fear": 0.8,
            "concern": 0.7,
            "sadness": 0.7,
            "anger": 0.7,
            "neutral": 0.3,
            None: 0.3
        }
        return emotion_scores.get(emotion, 0.5)
        
    def _calculate_relevance(self, thought: str) -> float:
        """Calculate relevance to current context."""
        if not self.current_topic:
            return 0.5
            
        thought_lower = thought.lower()
        relevance = 0.5
        
        # Direct topic mention
        if self.current_topic.lower() in thought_lower:
            relevance += 0.3
            
        # Entity mentions
        mentioned = 0
        for entity in self.mentioned_entities:
            if entity.lower() in thought_lower:
                mentioned += 1
                
        relevance += min(mentioned * 0.1, 0.3)
        
        # Topic word overlap
        thought_topics = self._extract_topics(thought, return_topics=True)
        overlap = len(thought_topics.intersection(self.topics))
        relevance += min(overlap * 0.05, 0.2)
        
        return min(relevance, 1.0)
        
    def _calculate_coherence(self, thought: str) -> float:
        """Calculate coherence with recent thoughts."""
        if len(self.thought_window) < 3:
            return 0.6  # Default for new conversations
            
        # Check for conversation flow markers
        flow_markers = ["therefore", "however", "because", "since", "so", 
                       "thus", "moreover", "furthermore", "additionally"]
        
        thought_lower = thought.lower()
        for marker in flow_markers:
            if marker in thought_lower:
                return 0.8
                
        # Check for entity continuity
        thought_entities = self._extract_entities(thought, return_entities=True)
        recent_entities = set()
        for recent in list(self.thought_window)[-5:]:
            recent_entities.update(self._extract_entities(recent, return_entities=True))
            
        if thought_entities.intersection(recent_entities):
            return 0.7
            
        # Default coherence
        return 0.5
        
    def _extract_entities(self, text: str, return_entities: bool = False) -> Optional[Set[str]]:
        """Extract named entities from text."""
        # Simple entity extraction - capitalized words
        entities = set()
        
        # Find capitalized sequences
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and word.lower() not in ["i", "the", "a", "an"]:
                # Check if it's start of sentence
                if i == 0 or words[i-1].endswith(('.', '!', '?')):
                    continue
                entities.add(word)
                
        # Update tracking
        if not return_entities:
            for entity in entities:
                self.mentioned_entities[entity] = self.mentioned_entities.get(entity, 0) + 1
                
        return entities if return_entities else None
        
    def _extract_topics(self, text: str, return_topics: bool = False) -> Optional[Set[str]]:
        """Extract topics from text."""
        # Simple topic extraction - significant words
        stopwords = {"the", "a", "an", "is", "was", "were", "been", "have", "has", 
                    "had", "do", "does", "did", "will", "would", "could", "should",
                    "may", "might", "must", "shall", "to", "of", "in", "for", "on",
                    "with", "at", "by", "from", "about", "as", "into", "through",
                    "during", "before", "after", "above", "below", "between", "under",
                    "i", "me", "my", "you", "your", "he", "she", "it", "we", "they"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        topics = {word for word in words if len(word) > 3 and word not in stopwords}
        
        # Update tracking
        if not return_topics:
            self.topics.update(topics)
            
        return topics if return_topics else None
        
    def _identify_topic(self, thought: str) -> Optional[str]:
        """Identify the main topic of a thought."""
        # Extract topics
        topics = self._extract_topics(thought, return_topics=True)
        
        # Find most significant topic
        if topics:
            # Prefer longer, more specific topics
            sorted_topics = sorted(topics, key=len, reverse=True)
            return sorted_topics[0] if sorted_topics else None
            
        return None
        
    def _update_attention(self, thought: str):
        """Update attention focus based on thought."""
        # Questions shift attention
        if "?" in thought:
            # Extract what the question is about
            topics = self._extract_topics(thought, return_topics=True)
            if topics:
                self.attention_focus = f"question about {list(topics)[0]}"
        
        # Strong statements might shift attention
        elif any(word in thought.lower() for word in ["important", "critical", "key", "essential"]):
            self.attention_focus = "important point"
            
    def _get_top_entities(self, n: int) -> List[Tuple[str, int]]:
        """Get top N mentioned entities."""
        sorted_entities = sorted(
            self.mentioned_entities.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_entities[:n]
        
    def has_context(self) -> bool:
        """Check if context exists."""
        return len(self.thought_window) > 0