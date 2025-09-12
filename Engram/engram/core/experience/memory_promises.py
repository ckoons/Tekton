"""
Memory Promises for optimistic recall patterns.

Enables non-blocking memory operations with progressive resolution.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger("engram.experience.promises")


class PromiseState(Enum):
    """States of a memory promise."""
    PENDING = "pending"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class MemoryPromise:
    """A promise for future memory resolution."""
    
    promise_id: str
    query: str
    state: PromiseState = PromiseState.PENDING
    
    created_at: datetime = field(default_factory=datetime.now)
    timeout: timedelta = field(default_factory=lambda: timedelta(seconds=5))
    
    partial_results: List[Any] = field(default_factory=list)
    final_result: Optional[Any] = None
    error: Optional[str] = None
    
    confidence: float = 0.0  # Confidence in current results
    resolution_progress: float = 0.0  # 0.0 to 1.0
    
    callbacks: List[Callable] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize promise tracking."""
        self._future = asyncio.Future()
        self._resolution_task = None
    
    def is_pending(self) -> bool:
        """Check if promise is still pending."""
        return self.state in [PromiseState.PENDING, PromiseState.RESOLVING]
    
    def is_complete(self) -> bool:
        """Check if promise is complete (resolved or failed)."""
        return self.state in [PromiseState.RESOLVED, PromiseState.FAILED, PromiseState.TIMEOUT]
    
    async def wait(self, timeout: Optional[float] = None) -> Any:
        """Wait for promise resolution."""
        try:
            return await asyncio.wait_for(
                self._future,
                timeout=timeout or self.timeout.total_seconds()
            )
        except asyncio.TimeoutError:
            self.state = PromiseState.TIMEOUT
            self.error = f"Promise timed out after {self.timeout}"
            raise
    
    def add_partial(self, result: Any, confidence: float = 0.5):
        """Add a partial result."""
        self.partial_results.append(result)
        self.confidence = max(self.confidence, confidence)
        self.resolution_progress = min(1.0, self.resolution_progress + 0.2)
        
        # Notify callbacks of partial result
        for callback in self.callbacks:
            try:
                callback(self, result, is_partial=True)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def resolve(self, result: Any):
        """Resolve the promise with final result."""
        if self.is_complete():
            logger.warning(f"Attempt to resolve completed promise {self.promise_id}")
            return
        
        self.final_result = result
        self.state = PromiseState.RESOLVED
        self.resolution_progress = 1.0
        self.confidence = 1.0
        
        # Set the future result
        if not self._future.done():
            self._future.set_result(result)
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(self, result, is_partial=False)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        logger.debug(f"Promise {self.promise_id} resolved")
    
    def fail(self, error: str):
        """Mark promise as failed."""
        if self.is_complete():
            return
        
        self.state = PromiseState.FAILED
        self.error = error
        
        # Set the future exception
        if not self._future.done():
            self._future.set_exception(Exception(error))
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(self, None, is_partial=False, error=error)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        logger.warning(f"Promise {self.promise_id} failed: {error}")
    
    def on_progress(self, callback: Callable):
        """Register a callback for progress updates."""
        self.callbacks.append(callback)
    
    def get_best_result(self) -> Any:
        """Get the best available result (final or best partial)."""
        if self.final_result is not None:
            return self.final_result
        elif self.partial_results:
            # Return the most recent partial result
            return self.partial_results[-1]
        return None


class PromiseResolver:
    """Resolves memory promises with progressive refinement."""
    
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.active_promises: Dict[str, MemoryPromise] = {}
        self.resolution_strategies = {
            'fast': self._resolve_fast,
            'deep': self._resolve_deep,
            'progressive': self._resolve_progressive
        }
        
        logger.info("Promise resolver initialized")
    
    async def create_promise(self, 
                            query: str,
                            strategy: str = 'progressive',
                            timeout: timedelta = timedelta(seconds=5)) -> MemoryPromise:
        """Create a new memory promise."""
        import uuid
        promise_id = str(uuid.uuid4())[:8]
        
        promise = MemoryPromise(
            promise_id=promise_id,
            query=query,
            timeout=timeout
        )
        
        self.active_promises[promise_id] = promise
        
        # Start resolution in background
        promise._resolution_task = asyncio.create_task(
            self._resolve_promise(promise, strategy)
        )
        
        logger.debug(f"Created promise {promise_id} for query: {query}")
        return promise
    
    async def _resolve_promise(self, promise: MemoryPromise, strategy: str):
        """Resolve a promise using the specified strategy."""
        try:
            promise.state = PromiseState.RESOLVING
            
            if strategy in self.resolution_strategies:
                await self.resolution_strategies[strategy](promise)
            else:
                await self._resolve_progressive(promise)
                
        except asyncio.CancelledError:
            promise.fail("Resolution cancelled")
        except Exception as e:
            promise.fail(str(e))
    
    async def _resolve_fast(self, promise: MemoryPromise):
        """Fast resolution - return first available result."""
        if not self.memory_system:
            promise.fail("No memory system available")
            return
        
        try:
            # Quick cache check
            from ..storage.cache_layer import CacheLayer
            cache = CacheLayer()
            
            cached = await cache.get(promise.query)
            if cached:
                promise.resolve(cached)
                return
            
            # If not in cache, do a quick search
            result = await self._quick_search(promise.query)
            promise.resolve(result)
            
        except Exception as e:
            promise.fail(f"Fast resolution failed: {e}")
    
    async def _resolve_deep(self, promise: MemoryPromise):
        """Deep resolution - thorough search across all backends."""
        if not self.memory_system:
            promise.fail("No memory system available")
            return
        
        try:
            # Search all backends
            results = await self._deep_search(promise.query)
            
            # Add partial results as they come in
            for i, result in enumerate(results):
                confidence = 0.3 + (i * 0.1)  # Increasing confidence
                promise.add_partial(result, confidence)
                await asyncio.sleep(0.1)  # Small delay for progressive feel
            
            # Synthesize final result
            if results:
                final = await self._synthesize_results(results)
                promise.resolve(final)
            else:
                promise.resolve(None)
                
        except Exception as e:
            promise.fail(f"Deep resolution failed: {e}")
    
    async def _resolve_progressive(self, promise: MemoryPromise):
        """Progressive resolution - start fast, refine over time."""
        if not self.memory_system:
            promise.fail("No memory system available")
            return
        
        try:
            # Phase 1: Quick cache check (0-100ms)
            cached = await self._quick_cache_check(promise.query)
            if cached:
                promise.add_partial(cached, confidence=0.6)
            
            # Phase 2: Fast search (100-500ms)
            quick_result = await self._quick_search(promise.query)
            if quick_result:
                promise.add_partial(quick_result, confidence=0.7)
            
            # Phase 3: Broader search (500ms-2s)
            if promise.state == PromiseState.RESOLVING:
                broader_results = await self._broader_search(promise.query)
                for result in broader_results[:3]:  # Top 3
                    promise.add_partial(result, confidence=0.8)
            
            # Phase 4: Deep synthesis (2s+)
            if promise.state == PromiseState.RESOLVING:
                all_results = promise.partial_results + broader_results
                final = await self._synthesize_results(all_results)
                promise.resolve(final)
            
        except asyncio.TimeoutError:
            # Resolve with best partial if we timeout
            if promise.partial_results:
                promise.resolve(promise.get_best_result())
            else:
                promise.fail("No results found before timeout")
        except Exception as e:
            promise.fail(f"Progressive resolution failed: {e}")
    
    async def _quick_cache_check(self, query: str) -> Optional[Any]:
        """Quick cache check."""
        # Simulate cache check
        await asyncio.sleep(0.05)  # 50ms
        return None  # Placeholder
    
    async def _quick_search(self, query: str) -> Optional[Any]:
        """Quick search in primary storage."""
        # Simulate quick search
        await asyncio.sleep(0.2)  # 200ms
        return {"type": "quick", "query": query, "results": []}
    
    async def _broader_search(self, query: str) -> List[Any]:
        """Broader search across multiple backends."""
        # Simulate broader search
        await asyncio.sleep(0.5)  # 500ms
        return [
            {"type": "broad", "source": "sql", "data": {}},
            {"type": "broad", "source": "document", "data": {}},
            {"type": "broad", "source": "vector", "data": {}}
        ]
    
    async def _deep_search(self, query: str) -> List[Any]:
        """Deep search across all backends."""
        # Simulate deep search
        await asyncio.sleep(1.0)  # 1 second
        return await self._broader_search(query) + [
            {"type": "deep", "source": "graph", "data": {}},
            {"type": "deep", "source": "cache", "data": {}}
        ]
    
    async def _synthesize_results(self, results: List[Any]) -> Any:
        """Synthesize multiple results into final answer."""
        # Simulate synthesis
        await asyncio.sleep(0.2)
        return {
            "synthesized": True,
            "source_count": len(results),
            "confidence": 0.9,
            "data": results[0] if results else None
        }
    
    def cancel_promise(self, promise_id: str):
        """Cancel an active promise."""
        if promise_id in self.active_promises:
            promise = self.active_promises[promise_id]
            if promise._resolution_task:
                promise._resolution_task.cancel()
            promise.fail("Cancelled by user")
            del self.active_promises[promise_id]
    
    async def cleanup_expired(self):
        """Clean up expired promises."""
        now = datetime.now()
        expired = []
        
        for promise_id, promise in self.active_promises.items():
            if promise.is_complete():
                expired.append(promise_id)
            elif now - promise.created_at > promise.timeout:
                promise.state = PromiseState.TIMEOUT
                promise.fail("Promise expired")
                expired.append(promise_id)
        
        for promise_id in expired:
            del self.active_promises[promise_id]
        
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired promises")