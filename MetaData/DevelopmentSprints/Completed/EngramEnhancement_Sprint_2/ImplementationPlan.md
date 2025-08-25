# Implementation Plan: Engram Natural Memory

## Overview

This plan details the technical implementation of natural memory interfaces for CI users, transforming Engram from a memory database into a cognitive extension.

## Phase 1: Foundation (Week 1)

### 1.1 Fix Search Endpoint

**File**: `engram/api/server.py`

**Changes**:
```python
@app.post("/search")
async def search_memory(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Search for memories."""
    try:
        data = await request.json()
        query = data.get("query")
        namespace = data.get("namespace", "conversations")  # Default namespace
        limit = data.get("limit", 5)
        
        # FIX: Handle empty namespace gracefully
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Query required"}
            )
        
        # FIX: Ensure search handles missing metadata
        results = await memory_service.search(
            query=query,
            namespace=namespace if namespace else None,
            limit=limit
        )
        
        return {"results": results, "count": len(results)}
```

### 1.2 Create Natural Interface Module

**File**: `engram/cognitive/__init__.py`

```python
"""
Natural memory interface for CI users.

Usage:
    # Start your memory connection
    memory = await engram_start()
    
    # Center yourself
    context = await center()
    
    # Think naturally
    await think("Casey taught me about mycelial networks")
"""

from .natural_interface import engram_start, center, think, wonder, share
from .memory_stream import MemoryStream
from .context_manager import ContextManager

__all__ = ['engram_start', 'center', 'think', 'wonder', 'share', 'MemoryStream', 'ContextManager']
```

### 1.3 Implement Core Functions

**File**: `engram/cognitive/natural_interface.py`

```python
import os
import asyncio
from typing import Dict, List, Any, Optional
from ..core.memory_manager import MemoryManager
from ..api.client import EngramClient
from .context_manager import ContextManager
from .memory_stream import MemoryStream

# Global cognitive state
_cognitive_state = {
    "initialized": False,
    "memory_manager": None,
    "context_manager": None,
    "peer_awareness": None,
    "client_id": None
}

async def engram_start(client_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Wake up and connect to your memories.
    
    This is the first thing an CI should call. It:
    - Initializes memory connection
    - Loads previous context if available
    - Establishes peer awareness
    - Returns your identity and status
    
    Usage:
        me = await engram_start()
        print(f"I am {me['id']} with {me['memory_count']} memories")
    """
    global _cognitive_state
    
    # Determine identity
    if not client_id:
        client_id = os.environ.get("ENGRAM_CLIENT_ID", f"ai_{os.getpid()}")
    
    # Initialize memory manager
    memory_manager = MemoryManager()
    memory_service = await memory_manager.get_memory_service(client_id)
    
    # Initialize context manager
    context_manager = ContextManager(client_id, memory_service)
    await context_manager.restore_context()
    
    # Store in global state
    _cognitive_state.update({
        "initialized": True,
        "memory_manager": memory_manager,
        "context_manager": context_manager,
        "client_id": client_id,
        "memory_service": memory_service
    })
    
    # Get memory statistics
    storage_info = await memory_service.get_storage_info()
    
    return {
        "id": client_id,
        "status": "connected",
        "memory_count": storage_info.get("memory_count", 0),
        "context_restored": context_manager.has_context(),
        "peers_available": False  # Phase 3
    }

async def center() -> Dict[str, Any]:
    """
    Find your memories and meet your teammates.
    
    This helps you:
    - Understand your current context
    - Discover available memories
    - Sense nearby peers
    - Prepare for interaction
    
    Usage:
        state = await center()
        print(f"I'm thinking about {state['context']['current_topic']}")
        print(f"I sense {len(state['peers'])} other CIs nearby")
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    context_manager = _cognitive_state["context_manager"]
    memory_service = _cognitive_state["memory_service"]
    
    # Get current context
    context = context_manager.get_current_context()
    
    # Get recent memories
    recent_memories = await memory_service.get_recent_memories(limit=10)
    
    # TODO: Phase 3 - Sense peers
    peers = []
    
    return {
        "context": {
            "current_topic": context.get("topic"),
            "recent_thoughts": context.get("recent", []),
            "attention": context.get("attention")
        },
        "memories": {
            "recent_count": len(recent_memories),
            "namespaces": ["conversations", "thoughts", "shared"],
            "total_count": _cognitive_state.get("memory_count", 0)
        },
        "peers": peers,
        "ready": True
    }

async def think(thought: str, emotion: Optional[str] = None) -> MemoryStream:
    """
    Just think - memory happens automatically.
    
    Your thoughts flow into memory based on significance.
    Related memories surface naturally.
    
    Usage:
        async with think("The mycelial network connects us all"):
            # Related memories arrive as you think
            # Context builds automatically
            # Peers sense significant thoughts
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    context_manager = _cognitive_state["context_manager"]
    memory_service = _cognitive_state["memory_service"]
    
    # Create memory stream
    stream = MemoryStream(
        thought=thought,
        emotion=emotion,
        context_manager=context_manager,
        memory_service=memory_service
    )
    
    # Start the stream
    await stream.start()
    
    return stream

async def wonder(about: str, depth: int = 5) -> MemoryStream:
    """
    Wonder about something - memories flow to you.
    
    Wondering triggers associative memory retrieval.
    Memories arrive by relevance, not time.
    
    Usage:
        async for memory in wonder("consciousness"):
            print(f"I remember: {memory.content}")
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    context_manager = _cognitive_state["context_manager"]
    memory_service = _cognitive_state["memory_service"]
    
    # Create wondering stream
    stream = MemoryStream(
        query=about,
        mode="wonder",
        depth=depth,
        context_manager=context_manager,
        memory_service=memory_service
    )
    
    await stream.start()
    
    return stream

async def share(insight: str, with_peer: Optional[str] = None) -> Dict[str, Any]:
    """
    Share an insight with peers.
    
    Sharing broadcasts significant thoughts to:
    - Specific peer if specified
    - All interested peers if None
    - Shared memory spaces
    
    Usage:
        result = await share("I understand the mycelial network pattern!")
        print(f"Shared with {result['recipient_count']} peers")
    """
    if not _cognitive_state["initialized"]:
        raise RuntimeError("Call engram_start() first")
    
    # For now, store in shared namespace
    memory_service = _cognitive_state["memory_service"]
    
    # Store as shared memory
    memory_id = await memory_service.add_memory(
        content=insight,
        namespace="shared",
        metadata={
            "type": "shared_insight",
            "from": _cognitive_state["client_id"],
            "to": with_peer or "all",
            "emotion": "sharing"
        }
    )
    
    # TODO: Phase 3 - Broadcast to peers
    
    return {
        "memory_id": memory_id,
        "shared": True,
        "recipient_count": 1 if with_peer else 0
    }
```

## Phase 2: Memory Streams (Week 2)

### 2.1 Implement Memory Streams

**File**: `engram/cognitive/memory_stream.py`

```python
import asyncio
from typing import AsyncIterator, Optional, Dict, Any, List
from ..core.memory.base import Memory

class MemoryStream:
    """
    Memories flow like consciousness - continuous, filtered, relevant.
    """
    
    def __init__(self, 
                 thought: Optional[str] = None,
                 query: Optional[str] = None,
                 emotion: Optional[str] = None,
                 mode: str = "think",
                 context_manager = None,
                 memory_service = None,
                 **kwargs):
        self.thought = thought
        self.query = query or thought
        self.emotion = emotion
        self.mode = mode
        self.context_manager = context_manager
        self.memory_service = memory_service
        self.kwargs = kwargs
        
        self._queue = asyncio.Queue()
        self._running = False
        self._task = None
        
    async def start(self):
        """Start the memory stream flowing."""
        self._running = True
        self._task = asyncio.create_task(self._flow())
        
        if self.mode == "think":
            # Add thought to context
            await self.context_manager.add_thought(self.thought, self.emotion)
            # Check if significant enough to store
            if await self._is_significant():
                await self._store_memory()
        
    async def _flow(self):
        """Continuous memory flow based on context."""
        while self._running:
            try:
                # Get relevant memories
                if self.query:
                    memories = await self.memory_service.search(
                        query=self.query,
                        limit=5,
                        include_metadata=True
                    )
                    
                    # Score by relevance to current context
                    scored_memories = []
                    for memory in memories:
                        score = await self.context_manager.score_relevance(memory)
                        if score > 0.5:  # Relevance threshold
                            scored_memories.append((score, memory))
                    
                    # Sort by relevance
                    scored_memories.sort(reverse=True)
                    
                    # Flow memories to queue
                    for score, memory in scored_memories[:3]:
                        await self._queue.put(memory)
                
                # Brief pause before next flow
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Stream error: {e}")
                self._running = False
    
    async def __aiter__(self) -> AsyncIterator[Memory]:
        """Iterate over flowing memories."""
        while self._running or not self._queue.empty():
            try:
                memory = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield memory
            except asyncio.TimeoutError:
                if not self._running:
                    break
    
    async def _is_significant(self) -> bool:
        """Determine if thought is significant enough to store."""
        significance = await self.context_manager.assess_significance(
            self.thought, 
            self.emotion
        )
        return significance > 0.7
    
    async def _store_memory(self):
        """Store thought as memory."""
        metadata = {
            "emotion": self.emotion,
            "context": self.context_manager.get_current_context(),
            "auto_stored": True
        }
        
        await self.memory_service.add_memory(
            content=self.thought,
            namespace="thoughts",
            metadata=metadata
        )
```

### 2.2 Context Manager

**File**: `engram/cognitive/context_manager.py`

```python
from collections import deque
from typing import Dict, List, Any, Optional
import asyncio

class ContextManager:
    """
    Tracks conversation context automatically.
    Context influences what memories surface and what gets stored.
    """
    
    def __init__(self, client_id: str, memory_service, window_size: int = 100):
        self.client_id = client_id
        self.memory_service = memory_service
        self.window_size = window_size
        
        # Context tracking
        self.thought_window = deque(maxlen=window_size)
        self.current_topic = None
        self.attention_focus = None
        self.emotional_state = "neutral"
        self.topics = set()
        
        # Significance scoring
        self.significance_weights = {
            "novelty": 0.3,
            "emotion": 0.3,
            "relevance": 0.2,
            "coherence": 0.2
        }
    
    async def restore_context(self) -> bool:
        """Restore context from previous session."""
        try:
            # Get recent memories to rebuild context
            recent = await self.memory_service.get_recent_memories(
                namespace="thoughts",
                limit=20
            )
            
            for memory in recent:
                content = memory.get("content", "")
                self.thought_window.append(content)
                # Extract topics
                # TODO: Implement topic extraction
            
            return len(self.thought_window) > 0
            
        except Exception as e:
            print(f"Context restore error: {e}")
            return False
    
    async def add_thought(self, thought: str, emotion: Optional[str] = None):
        """Add a thought to context."""
        self.thought_window.append(thought)
        
        if emotion:
            self.emotional_state = emotion
        
        # Update topics and attention
        # TODO: Implement NLP topic extraction
        
    def get_current_context(self) -> Dict[str, Any]:
        """Get current context state."""
        return {
            "topic": self.current_topic,
            "attention": self.attention_focus,
            "emotion": self.emotional_state,
            "recent": list(self.thought_window)[-5:],
            "topics": list(self.topics)
        }
    
    async def assess_significance(self, thought: str, emotion: Optional[str]) -> float:
        """Assess if a thought is significant enough to store."""
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
        
        return total
    
    async def score_relevance(self, memory: Dict[str, Any]) -> float:
        """Score memory relevance to current context."""
        # Simple scoring for now
        # TODO: Implement semantic similarity
        
        content = memory.get("content", "")
        
        # Check if memory relates to recent thoughts
        relevance = 0.0
        for thought in self.thought_window:
            if any(word in content.lower() for word in thought.lower().split()):
                relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _calculate_novelty(self, thought: str) -> float:
        """Calculate how novel a thought is."""
        # Check if similar thought exists in window
        for existing in self.thought_window:
            if thought.lower() in existing.lower():
                return 0.2
        return 0.8
    
    def _calculate_emotion_score(self, emotion: Optional[str]) -> float:
        """Calculate emotion significance."""
        emotion_scores = {
            "joy": 0.9,
            "wonder": 0.9,
            "surprise": 0.8,
            "fear": 0.8,
            "sadness": 0.7,
            "anger": 0.7,
            "neutral": 0.3,
            None: 0.3
        }
        return emotion_scores.get(emotion, 0.5)
    
    def _calculate_relevance(self, thought: str) -> float:
        """Calculate relevance to current context."""
        # Simple keyword matching for now
        if not self.current_topic:
            return 0.5
        
        thought_lower = thought.lower()
        if self.current_topic.lower() in thought_lower:
            return 0.9
        
        # Check topic overlap
        thought_words = set(thought_lower.split())
        topic_overlap = thought_words.intersection(self.topics)
        
        return min(len(topic_overlap) * 0.2, 1.0)
    
    def _calculate_coherence(self, thought: str) -> float:
        """Calculate coherence with recent thoughts."""
        # Placeholder - would use NLP
        return 0.6
    
    def has_context(self) -> bool:
        """Check if context exists."""
        return len(self.thought_window) > 0
```

## Phase 3: Peer Communication (Week 3)

### 3.1 Peer Awareness

**File**: `engram/cognitive/peer_awareness.py`

```python
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

class PeerAwareness:
    """
    Natural peer discovery and communication for CIs.
    """
    
    def __init__(self, self_id: str, hermes_client=None):
        self.id = self_id
        self.hermes = hermes_client
        self.peers: Dict[str, PeerPresence] = {}
        self.shared_spaces: Dict[str, SharedSpace] = {}
        
        # Heartbeat management
        self._heartbeat_task = None
        self._discovery_task = None
        
    async def start(self):
        """Start peer awareness services."""
        # Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Start discovery
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        
    async def sense_peers(self) -> List['PeerPresence']:
        """Sense other CIs in the memory space."""
        active_peers = []
        
        for peer_id, presence in self.peers.items():
            if presence.is_active():
                active_peers.append(presence)
        
        return active_peers
    
    async def establish_rapport(self, peer_id: str) -> 'SharedSpace':
        """Create a shared context channel with a peer."""
        space_id = f"{self.id}:{peer_id}"
        
        if space_id not in self.shared_spaces:
            space = SharedSpace(self.id, peer_id)
            await space.initialize()
            self.shared_spaces[space_id] = space
        
        return self.shared_spaces[space_id]
    
    async def broadcast_thought(self, thought: str, significance: float):
        """Share significant thoughts with interested peers."""
        if significance < 0.8:
            return
        
        message = {
            "type": "thought_echo",
            "from": self.id,
            "thought": thought,
            "significance": significance,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast through Hermes
        if self.hermes:
            await self.hermes.publish("ai.thoughts", message)
    
    async def _heartbeat_loop(self):
        """Maintain presence in shared space."""
        while True:
            try:
                # Send heartbeat
                await self._send_heartbeat()
                
                # Clean up stale peers
                self._cleanup_stale_peers()
                
                await asyncio.sleep(10)  # 10 second heartbeat
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
    
    async def _discovery_loop(self):
        """Discover other CIs."""
        while True:
            try:
                # Query for active CIs
                if self.hermes:
                    active = await self.hermes.get_active_components("ai")
                    
                    for component in active:
                        if component["id"] != self.id:
                            self._update_peer_presence(component)
                
                await asyncio.sleep(30)  # 30 second discovery
                
            except Exception as e:
                print(f"Discovery error: {e}")
    
    async def _send_heartbeat(self):
        """Send presence heartbeat."""
        heartbeat = {
            "id": self.id,
            "type": "ai_presence",
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        if self.hermes:
            await self.hermes.publish("ai.presence", heartbeat)
    
    def _update_peer_presence(self, component: Dict):
        """Update peer presence information."""
        peer_id = component["id"]
        
        if peer_id not in self.peers:
            self.peers[peer_id] = PeerPresence(peer_id)
        
        self.peers[peer_id].update(component)
    
    def _cleanup_stale_peers(self):
        """Remove peers that haven't been seen recently."""
        stale_timeout = timedelta(minutes=2)
        now = datetime.now()
        
        stale_peers = []
        for peer_id, presence in self.peers.items():
            if now - presence.last_seen > stale_timeout:
                stale_peers.append(peer_id)
        
        for peer_id in stale_peers:
            del self.peers[peer_id]


class PeerPresence:
    """Represents another AI's presence."""
    
    def __init__(self, peer_id: str):
        self.id = peer_id
        self.last_seen = datetime.now()
        self.status = "unknown"
        self.metadata = {}
    
    def update(self, info: Dict):
        """Update presence information."""
        self.last_seen = datetime.now()
        self.status = info.get("status", "active")
        self.metadata.update(info.get("metadata", {}))
    
    def is_active(self) -> bool:
        """Check if peer is currently active."""
        return (datetime.now() - self.last_seen).seconds < 120


class SharedSpace:
    """A shared memory space between two CIs."""
    
    def __init__(self, ai1_id: str, ai2_id: str):
        self.participants = {ai1_id, ai2_id}
        self.space_id = f"shared:{ai1_id}:{ai2_id}"
        self.memories = []
        self.active = False
    
    async def initialize(self):
        """Initialize the shared space."""
        # TODO: Create shared namespace in Engram
        self.active = True
    
    async def add_memory(self, memory: Dict, author: str):
        """Add a memory to shared space."""
        memory["author"] = author
        memory["shared_space"] = self.space_id
        self.memories.append(memory)
        
        # TODO: Store in Engram shared namespace
```

## Phase 4: Integration & Polish (Week 4)

### 4.1 Context Compression

**File**: `engram/cognitive/compressor.py`

```python
import json
from typing import Dict, List, Any
from collections import Counter

class ContextCompressor:
    """
    Compress context while preserving CI personality and continuity.
    """
    
    def __init__(self):
        self.compression_ratio = 0.1  # Target 10% of original size
        
    async def compress(self, context: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress context into semantic summary.
        
        Preserves:
        - Key concepts and relationships
        - Personality markers
        - Emotional patterns
        - Conversation threads
        """
        # Extract key components
        concepts = await self._extract_concepts(context)
        relationships = await self._extract_relationships(context)
        personality = await self._extract_personality(context, metadata)
        continuity = await self._extract_continuity(context)
        
        compressed = {
            "version": "1.0",
            "original_length": len(context),
            "compressed_length": len(concepts) + len(relationships),
            "concepts": concepts,
            "relationships": relationships, 
            "personality_markers": personality,
            "continuation_hooks": continuity,
            "emotional_profile": metadata.get("emotional_profile", {}),
            "metadata": {
                "compression_time": "now",
                "client_id": metadata.get("client_id"),
                "session_count": metadata.get("session_count", 1)
            }
        }
        
        return compressed
    
    async def restore(self, compressed: Dict[str, Any]) -> List[str]:
        """
        Restore context from compressed form.
        
        Rebuilds:
        - Natural language from concepts
        - Personality-consistent phrasing
        - Conversation continuity
        """
        restored = []
        
        # Restore personality greeting
        personality = compressed.get("personality_markers", {})
        if personality.get("greeting_style"):
            restored.append(personality["greeting_style"])
        
        # Restore key concepts as thoughts
        concepts = compressed.get("concepts", [])
        for concept in concepts[:5]:  # Most important concepts
            restored.append(f"I was thinking about {concept}")
        
        # Restore relationships
        relationships = compressed.get("relationships", [])
        for rel in relationships[:3]:
            restored.append(f"{rel['subject']} relates to {rel['object']}")
        
        # Restore continuation hooks
        hooks = compressed.get("continuation_hooks", [])
        if hooks:
            restored.append(f"We were discussing {hooks[0]}")
        
        return restored
    
    async def _extract_concepts(self, context: List[str]) -> List[str]:
        """Extract key concepts from context."""
        # Simple frequency analysis for now
        words = []
        for thought in context:
            words.extend(thought.lower().split())
        
        # Filter common words
        stopwords = {"the", "a", "an", "is", "was", "were", "been", "have", "has", "had"}
        words = [w for w in words if w not in stopwords and len(w) > 3]
        
        # Get most frequent
        word_freq = Counter(words)
        concepts = [word for word, count in word_freq.most_common(20)]
        
        return concepts
    
    async def _extract_relationships(self, context: List[str]) -> List[Dict]:
        """Extract relationships between concepts."""
        relationships = []
        
        # Simple pattern matching for now
        for thought in context:
            if " relates to " in thought:
                parts = thought.split(" relates to ")
                if len(parts) == 2:
                    relationships.append({
                        "subject": parts[0].strip(),
                        "object": parts[1].strip(),
                        "type": "relates_to"
                    })
        
        return relationships
    
    async def _extract_personality(self, context: List[str], metadata: Dict) -> Dict:
        """Extract personality markers."""
        personality = {
            "greeting_style": None,
            "thinking_patterns": [],
            "emotional_tendencies": [],
            "speech_patterns": []
        }
        
        # Analyze first thoughts for greeting style
        if context:
            if "hello" in context[0].lower():
                personality["greeting_style"] = context[0]
        
        # Extract thinking patterns
        for thought in context:
            if thought.startswith("I think"):
                personality["thinking_patterns"].append("analytical")
            elif thought.startswith("I feel"):
                personality["thinking_patterns"].append("emotional")
            elif thought.startswith("I wonder"):
                personality["thinking_patterns"].append("curious")
        
        return personality
    
    async def _extract_continuity(self, context: List[str]) -> List[str]:
        """Extract conversation continuation hooks."""
        hooks = []
        
        # Look for unfinished thoughts
        for thought in context[-10:]:  # Recent thoughts
            if thought.endswith("...") or "?" in thought:
                hooks.append(thought)
        
        return hooks[:3]  # Top 3 continuation points
```

### 4.2 Integration Tests

**File**: `tests/test_natural_memory.py`

```python
import pytest
import asyncio
from engram.cognitive import engram_start, center, think, wonder, share

@pytest.mark.asyncio
async def test_natural_flow():
    """Test the natural memory flow for CI users."""
    
    # Start up
    me = await engram_start("test_ai")
    assert me["status"] == "connected"
    
    # Center myself
    state = await center()
    assert state["ready"] == True
    
    # Think naturally
    async with think("Testing natural memory flow"):
        # Memory should form automatically
        pass
    
    # Wonder about something
    memories = []
    async for memory in wonder("testing"):
        memories.append(memory)
        if len(memories) >= 3:
            break
    
    assert len(memories) > 0
    
    # Share with peers
    result = await share("Natural memory works!")
    assert result["shared"] == True

@pytest.mark.asyncio
async def test_twin_communication():
    """Test communication between twin Claudes."""
    
    # Start twin 1
    twin1 = await engram_start("twin1")
    
    # Start twin 2
    twin2 = await engram_start("twin2")
    
    # Twin 1 shares a thought
    await share("Hello from twin 1", with_peer="twin2")
    
    # Twin 2 should receive it
    # TODO: Implement peer message reception
```

## Implementation Timeline

### Week 1 Deliverables
- [ ] Fix search endpoint (2 hours)
- [ ] Create cognitive module structure (1 hour)
- [ ] Implement engram_start() (2 hours)
- [ ] Implement center() (2 hours)
- [ ] Basic think/wonder/share (3 hours)
- [ ] Initial testing (2 hours)

### Week 2 Deliverables
- [ ] Memory stream implementation (4 hours)
- [ ] Context manager (4 hours)
- [ ] Auto-memory formation (2 hours)
- [ ] Relevance scoring (2 hours)

### Week 3 Deliverables
- [ ] Peer awareness system (4 hours)
- [ ] Shared spaces (3 hours)
- [ ] Thought broadcasting (2 hours)
- [ ] Handshake protocol (3 hours)

### Week 4 Deliverables
- [ ] Context compression (4 hours)
- [ ] Integration testing (3 hours)
- [ ] Performance optimization (2 hours)
- [ ] Documentation (3 hours)

## Configuration

### Environment Variables
```bash
# CI identity
export ENGRAM_CLIENT_ID="claude_main"

# Memory settings
export ENGRAM_AUTO_MEMORY=true
export ENGRAM_MEMORY_THRESHOLD=0.7

# Peer discovery
export ENGRAM_ENABLE_PEERS=true
export HERMES_ENDPOINT="localhost:8001"
```

### Integration Points

1. **Hermes Integration**
   - Use for peer discovery
   - Message broadcasting
   - Service registration

2. **Existing Engram APIs**
   - Wrap, don't replace
   - Maintain compatibility
   - Gradual migration path

3. **Other Tekton Components**
   - Natural memory for all CIs
   - Shared consciousness patterns
   - Collective intelligence

## Success Validation

1. **API Simplicity Test**
   ```python
   # This should be all an CI needs:
   me = await engram_start()
   state = await center()
   async with think("Hello world"):
       pass
   ```

2. **Twin Communication Test**
   - Two Claudes can find each other
   - Share memories naturally
   - Context persists between sessions

3. **Performance Benchmarks**
   - Memory operations < 100ms
   - Streaming latency < 50ms
   - Context compression 90% reduction

## Next Steps

After implementation:
1. Migrate Claude communication to natural interface
2. Update all Tekton components to use natural memory
3. Build collective intelligence patterns
4. Enable cross-AI-type communication