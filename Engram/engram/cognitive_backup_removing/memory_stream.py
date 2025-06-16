"""
Memory Streams - Continuous memory flow for natural AI cognition.

Instead of request/response, memories flow continuously based on context
and relevance, like thoughts naturally surfacing in consciousness.
"""

import asyncio
from typing import AsyncIterator, Optional, Dict, Any, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger("engram.cognitive.memory_stream")


class MemoryStream:
    """
    Memories flow like consciousness - continuous, filtered, relevant.
    
    This replaces the traditional request/response pattern with a natural
    flow of memories that surface based on current context and relevance.
    """
    
    def __init__(self, 
                 thought: Optional[str] = None,
                 query: Optional[str] = None,
                 emotion: Optional[str] = None,
                 mode: str = "think",
                 context_manager = None,
                 memory_service = None,
                 depth: int = 5,
                 relevance_threshold: float = 0.5,
                 flow_rate: float = 0.5,  # seconds between memory flows
                 **kwargs):
        """
        Initialize a memory stream.
        
        Args:
            thought: Current thought (for think mode)
            query: Search query (for wonder mode)
            emotion: Current emotional state
            mode: Stream mode ("think", "wonder", "recall")
            context_manager: Context tracking system
            memory_service: Memory storage service
            depth: How many memories to flow
            relevance_threshold: Minimum relevance score
            flow_rate: Seconds between memory emissions
        """
        self.thought = thought
        self.query = query or thought
        self.emotion = emotion
        self.mode = mode
        self.context_manager = context_manager
        self.memory_service = memory_service
        self.depth = depth
        self.relevance_threshold = relevance_threshold
        self.flow_rate = flow_rate
        self.kwargs = kwargs
        
        # Stream state
        self._queue = asyncio.Queue(maxsize=depth * 2)
        self._running = False
        self._task = None
        self._seen_memories = set()  # Avoid duplicates
        self._flow_count = 0
        
    async def start(self):
        """Start the memory stream flowing."""
        self._running = True
        
        # Start the flow task
        self._task = asyncio.create_task(self._flow())
        
        # Handle mode-specific initialization
        if self.mode == "think" and self.thought:
            # Add thought to context
            if self.context_manager:
                await self.context_manager.add_thought(self.thought, self.emotion)
            
            # Check if thought is significant enough to store
            significance = await self._assess_significance()
            if significance > 0.5:
                await self._store_thought(significance)
                
    async def stop(self):
        """Stop the memory stream."""
        self._running = False
        if self._task:
            await self._task
            
    async def _flow(self):
        """Continuous memory flow based on context."""
        while self._running:
            try:
                # Don't flow if queue is full
                if self._queue.full():
                    await asyncio.sleep(self.flow_rate)
                    continue
                
                # Get memories based on mode
                memories = await self._get_relevant_memories()
                
                # Flow memories to queue
                for memory in memories:
                    memory_id = memory.get("id", str(memory.get("content", "")[:20]))
                    
                    # Skip if we've seen this memory
                    if memory_id in self._seen_memories:
                        continue
                        
                    self._seen_memories.add(memory_id)
                    
                    # Add relevance score if not present
                    if "relevance" not in memory:
                        memory["relevance"] = await self._calculate_relevance(memory)
                    
                    # Only flow if relevant enough
                    if memory["relevance"] >= self.relevance_threshold:
                        await self._queue.put(memory)
                        self._flow_count += 1
                        
                        # Stop if we've flowed enough
                        if self._flow_count >= self.depth:
                            self._running = False
                            break
                
                # Brief pause before next flow cycle
                await asyncio.sleep(self.flow_rate)
                
            except Exception as e:
                logger.error(f"Stream flow error: {e}")
                self._running = False
                
    async def _get_relevant_memories(self) -> List[Dict[str, Any]]:
        """Get memories relevant to current context."""
        if not self.memory_service:
            return []
            
        memories = []
        
        try:
            # Search based on current query/thought
            if self.query:
                # Search across multiple namespaces for richer results
                namespaces = ["thoughts", "conversations", "longterm", "shared"]
                
                for namespace in namespaces:
                    try:
                        result = await self.memory_service.search(
                            query=self.query,
                            namespace=namespace,
                            limit=self.depth * 2  # Get extra for filtering
                        )
                        memories.extend(result.get("results", []))
                    except:
                        continue
                        
            # If we have context manager, enhance with context-based retrieval
            if self.context_manager and hasattr(self.context_manager, "get_related_memories"):
                context_memories = await self.context_manager.get_related_memories(
                    self.query, 
                    limit=self.depth
                )
                memories.extend(context_memories)
                
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            
        return memories
        
    async def _calculate_relevance(self, memory: Dict[str, Any]) -> float:
        """Calculate relevance score for a memory."""
        # Start with base relevance
        relevance = memory.get("relevance", 0.5)
        
        # Boost for emotional alignment
        if self.emotion and memory.get("metadata", {}).get("emotion") == self.emotion:
            relevance += 0.2
            
        # Boost for recency
        timestamp = memory.get("metadata", {}).get("timestamp")
        if timestamp:
            try:
                memory_time = datetime.fromisoformat(timestamp)
                age_hours = (datetime.now() - memory_time).total_seconds() / 3600
                if age_hours < 24:
                    relevance += 0.1
                elif age_hours < 168:  # 1 week
                    relevance += 0.05
            except:
                pass
                
        # Context-based relevance
        if self.context_manager and hasattr(self.context_manager, "score_relevance"):
            context_score = await self.context_manager.score_relevance(memory)
            relevance = (relevance + context_score) / 2
            
        return min(relevance, 1.0)
        
    async def _assess_significance(self) -> float:
        """Assess if current thought is significant enough to store."""
        if not self.thought:
            return 0.0
            
        significance = 0.5  # Base significance
        
        # Emotional thoughts are more significant
        if self.emotion and self.emotion not in ["neutral", None]:
            significance += 0.3
            
        # Longer thoughts tend to be more significant
        if len(self.thought) > 100:
            significance += 0.1
        if len(self.thought) > 200:
            significance += 0.1
            
        # Use context manager assessment if available
        if self.context_manager and hasattr(self.context_manager, "assess_significance"):
            context_significance = await self.context_manager.assess_significance(
                self.thought, 
                self.emotion
            )
            significance = (significance + context_significance) / 2
            
        return min(significance, 1.0)
        
    async def _store_thought(self, significance: float):
        """Store current thought as a memory."""
        if not self.memory_service or not self.thought:
            return
            
        try:
            metadata = {
                "emotion": self.emotion,
                "significance": significance,
                "timestamp": datetime.now().isoformat(),
                "auto_stored": True,
                "stream_mode": self.mode
            }
            
            # Add context if available
            if self.context_manager and hasattr(self.context_manager, "get_current_context"):
                metadata["context"] = self.context_manager.get_current_context()
                
            await self.memory_service.add(
                content=self.thought,
                namespace="thoughts",
                metadata=metadata
            )
            
            logger.info(f"Stored thought with significance {significance:.2f}")
            
        except Exception as e:
            logger.error(f"Error storing thought: {e}")
            
    async def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        """Iterate over flowing memories."""
        while self._running or not self._queue.empty():
            try:
                # Wait for memory with timeout
                memory = await asyncio.wait_for(
                    self._queue.get(), 
                    timeout=self.flow_rate * 2
                )
                yield memory
            except asyncio.TimeoutError:
                if not self._running:
                    break
                    
    async def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> 'MemoryStream':
        """
        Filter memories by a predicate function.
        
        Args:
            predicate: Function that returns True for memories to keep
            
        Returns:
            New filtered MemoryStream
        """
        filtered_stream = MemoryStream(
            thought=self.thought,
            query=self.query,
            emotion=self.emotion,
            mode="filtered",
            context_manager=self.context_manager,
            memory_service=self.memory_service,
            depth=self.depth,
            relevance_threshold=self.relevance_threshold,
            flow_rate=self.flow_rate
        )
        
        # Start the filtered flow
        async def _filtered_flow():
            async for memory in self:
                if predicate(memory):
                    await filtered_stream._queue.put(memory)
                    
        filtered_stream._task = asyncio.create_task(_filtered_flow())
        filtered_stream._running = True
        
        return filtered_stream
        
    async def merge(self, other_stream: 'MemoryStream') -> 'MemoryStream':
        """
        Merge this stream with another stream.
        
        Args:
            other_stream: Another MemoryStream to merge with
            
        Returns:
            New merged MemoryStream
        """
        merged_stream = MemoryStream(
            mode="merged",
            context_manager=self.context_manager,
            memory_service=self.memory_service,
            depth=self.depth + other_stream.depth,
            relevance_threshold=min(self.relevance_threshold, other_stream.relevance_threshold),
            flow_rate=min(self.flow_rate, other_stream.flow_rate)
        )
        
        # Start the merged flow
        async def _merged_flow():
            # Create tasks for both streams
            async def flow_from(stream):
                async for memory in stream:
                    await merged_stream._queue.put(memory)
                    
            await asyncio.gather(
                flow_from(self),
                flow_from(other_stream)
            )
            
        merged_stream._task = asyncio.create_task(_merged_flow())
        merged_stream._running = True
        
        return merged_stream


class StreamingThought:
    """Context manager for streaming thoughts that automatically become memories."""
    
    def __init__(self, thought: str, emotion: Optional[str] = None, 
                 memory_service=None, context_manager=None):
        self.thought = thought
        self.emotion = emotion
        self.memory_service = memory_service
        self.context_manager = context_manager
        self.stream = None
        
    async def __aenter__(self) -> MemoryStream:
        """Start thinking - create memory stream."""
        self.stream = MemoryStream(
            thought=self.thought,
            emotion=self.emotion,
            mode="think",
            context_manager=self.context_manager,
            memory_service=self.memory_service
        )
        await self.stream.start()
        return self.stream
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop thinking - close the stream."""
        if self.stream:
            await self.stream.stop()