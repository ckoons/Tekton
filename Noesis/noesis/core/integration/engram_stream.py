"""
Engram Data Streaming Integration for Noesis
Provides real-time streaming of memory state data from Engram for theoretical analysis
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import numpy as np

from shared.urls import tekton_url

logger = logging.getLogger(__name__)


@dataclass 
class MemoryState:
    """Represents a snapshot of Engram memory state"""
    timestamp: datetime
    component_id: str
    latent_spaces: Dict[str, Any] = field(default_factory=dict)
    thought_states: Dict[str, str] = field(default_factory=dict)  # thought_id -> state
    memory_metrics: Dict[str, float] = field(default_factory=dict)
    attention_weights: List[float] = field(default_factory=list)
    activity_levels: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_vector(self) -> np.ndarray:
        """Convert memory state to numerical vector for analysis"""
        # Collect all numerical features
        features = []
        
        # Memory metrics
        for key in sorted(self.memory_metrics.keys()):
            features.append(self.memory_metrics[key])
        
        # Attention weights (pad/truncate to fixed size)
        attention_size = 64  # Fixed attention vector size
        if len(self.attention_weights) >= attention_size:
            features.extend(self.attention_weights[:attention_size])
        else:
            features.extend(self.attention_weights)
            features.extend([0.0] * (attention_size - len(self.attention_weights)))
        
        # Activity levels
        for key in sorted(self.activity_levels.keys()):
            features.append(self.activity_levels[key])
        
        # Thought state distribution (count of each state type)
        state_counts = {}
        for state in ["initial", "refining", "finalized", "paused", "abandoned", "rejected"]:
            state_counts[state] = sum(1 for s in self.thought_states.values() if s == state)
        
        total_thoughts = len(self.thought_states) or 1
        for state in sorted(state_counts.keys()):
            features.append(state_counts[state] / total_thoughts)
        
        # Latent space dimensions (simplified)
        features.append(len(self.latent_spaces))
        features.append(sum(len(space.get("thoughts", {})) for space in self.latent_spaces.values()))
        
        return np.array(features)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "component_id": self.component_id,
            "latent_spaces": self.latent_spaces,
            "thought_states": self.thought_states,
            "memory_metrics": self.memory_metrics,
            "attention_weights": self.attention_weights,
            "activity_levels": self.activity_levels,
            "metadata": self.metadata
        }


@dataclass
class MemoryEvent:
    """Represents a discrete memory event from Engram"""
    event_type: str  # "thought_created", "thought_refined", "state_transition", etc.
    timestamp: datetime
    component_id: str
    thought_id: Optional[str] = None
    space_id: Optional[str] = None
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    event_data: Dict[str, Any] = field(default_factory=dict)
    

class EngramStreamListener(ABC):
    """Abstract base class for Engram stream listeners"""
    
    @abstractmethod
    async def on_memory_state(self, state: MemoryState) -> None:
        """Called when a new memory state is received"""
        pass
    
    @abstractmethod
    async def on_memory_event(self, event: MemoryEvent) -> None:
        """Called when a memory event is received"""
        pass
    
    @abstractmethod
    async def on_stream_error(self, error: Exception) -> None:
        """Called when a stream error occurs"""
        pass


class EngramDataStreamer:
    """
    Streams memory data from Engram to Noesis for theoretical analysis
    Supports both polling and event-driven streaming modes
    """
    
    def __init__(self, engram_url: Optional[str] = None, poll_interval: float = 5.0):
        self.engram_url = engram_url or tekton_url("engram")
        self.poll_interval = poll_interval
        
        self.listeners: List[EngramStreamListener] = []
        self.is_streaming = False
        self.stream_task: Optional[asyncio.Task] = None
        
        # State tracking
        self.last_poll_time: Optional[datetime] = None
        self.known_thoughts: Dict[str, str] = {}  # thought_id -> last_known_state
        self.memory_history: List[MemoryState] = []
        self.max_history_size = 1000
        
        # HTTP client for polling
        self.http_client = None
        
        logger.info(f"Initialized Engram data streamer for {self.engram_url}")
    
    def add_listener(self, listener: EngramStreamListener) -> None:
        """Add a listener for memory events"""
        self.listeners.append(listener)
        logger.info(f"Added listener: {listener.__class__.__name__}")
    
    def remove_listener(self, listener: EngramStreamListener) -> None:
        """Remove a listener"""
        if listener in self.listeners:
            self.listeners.remove(listener)
            logger.info(f"Removed listener: {listener.__class__.__name__}")
    
    async def start_streaming(self) -> None:
        """Start streaming memory data from Engram"""
        if self.is_streaming:
            logger.warning("Streaming already active")
            return
        
        try:
            import httpx
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            self.is_streaming = True
            self.stream_task = asyncio.create_task(self._stream_loop())
            
            logger.info("Started Engram data streaming")
            
        except ImportError:
            logger.error("httpx library required for Engram streaming")
            raise
    
    async def stop_streaming(self) -> None:
        """Stop streaming memory data"""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
            self.stream_task = None
        
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
        
        logger.info("Stopped Engram data streaming")
    
    async def _stream_loop(self) -> None:
        """Main streaming loop - polls Engram for memory state changes"""
        logger.info("Starting Engram stream loop")
        
        while self.is_streaming:
            try:
                # Poll for current memory state
                await self._poll_memory_state()
                
                # Wait for next poll
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                logger.info("Stream loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in stream loop: {e}")
                await self._notify_error(e)
                
                # Brief pause before retrying
                await asyncio.sleep(1.0)
    
    async def _poll_memory_state(self) -> None:
        """Poll Engram for current memory state"""
        try:
            # Get memory state from Engram
            memory_state = await self._fetch_memory_state()
            if memory_state:
                # Detect events by comparing with previous state
                events = self._detect_events(memory_state)
                
                # Notify listeners
                await self._notify_memory_state(memory_state)
                for event in events:
                    await self._notify_memory_event(event)
                
                # Update history
                self._update_history(memory_state)
                
                self.last_poll_time = datetime.now()
        
        except Exception as e:
            logger.error(f"Error polling memory state: {e}")
            raise
    
    async def _fetch_memory_state(self) -> Optional[MemoryState]:
        """Fetch current memory state from Engram API"""
        try:
            # Try to get memory state from Engram health/status endpoint
            response = await self.http_client.get(f"{self.engram_url}/health")
            if response.status_code != 200:
                logger.warning(f"Engram health check failed: {response.status_code}")
                return None
            
            health_data = response.json()
            
            # Get detailed memory state if available
            try:
                state_response = await self.http_client.get(f"{self.engram_url}/api/memory/state")
                if state_response.status_code == 200:
                    state_data = state_response.json()
                else:
                    # Fallback to simulated state based on health
                    state_data = self._simulate_memory_state(health_data)
            except:
                # Engram might not have this endpoint yet, simulate
                state_data = self._simulate_memory_state(health_data)
            
            # Convert to MemoryState object
            memory_state = MemoryState(
                timestamp=datetime.now(),
                component_id="engram",
                latent_spaces=state_data.get("latent_spaces", {}),
                thought_states=state_data.get("thought_states", {}),
                memory_metrics=state_data.get("memory_metrics", {}),
                attention_weights=state_data.get("attention_weights", []),
                activity_levels=state_data.get("activity_levels", {}),
                metadata=state_data.get("metadata", {})
            )
            
            return memory_state
            
        except Exception as e:
            logger.error(f"Failed to fetch memory state: {e}")
            return None
    
    def _simulate_memory_state(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate memory state when full API is not available"""
        # Create a realistic simulated memory state for analysis
        import random
        
        # Simulate latent spaces
        num_spaces = random.randint(1, 5)
        latent_spaces = {}
        
        for i in range(num_spaces):
            space_id = f"space_{i}"
            num_thoughts = random.randint(0, 20)
            
            thoughts = {}
            for j in range(num_thoughts):
                thought_id = f"thought_{i}_{j}"
                thoughts[thought_id] = {
                    "state": random.choice(["initial", "refining", "finalized", "paused"]),
                    "iterations": random.randint(1, 5),
                    "last_updated": datetime.now().isoformat()
                }
            
            latent_spaces[space_id] = {
                "thoughts": thoughts,
                "owner": "collective_intelligence",
                "shared": random.choice([True, False])
            }
        
        # Simulate thought states
        all_thoughts = {}
        for space in latent_spaces.values():
            for thought_id, thought_data in space["thoughts"].items():
                all_thoughts[thought_id] = thought_data["state"]
        
        # Simulate memory metrics
        memory_metrics = {
            "total_memories": random.randint(100, 1000),
            "active_thoughts": len([t for t in all_thoughts.values() if t in ["initial", "refining"]]),
            "memory_utilization": random.uniform(0.3, 0.8),
            "compression_ratio": random.uniform(0.1, 0.5),
            "retrieval_latency": random.uniform(0.01, 0.1),
            "storage_efficiency": random.uniform(0.7, 0.95)
        }
        
        # Simulate attention weights (dimensionality reduction of focus)
        attention_size = random.randint(10, 64)
        attention_weights = [random.uniform(0, 1) for _ in range(attention_size)]
        # Normalize to sum to 1
        total = sum(attention_weights)
        if total > 0:
            attention_weights = [w / total for w in attention_weights]
        
        # Simulate activity levels
        activity_levels = {
            "thought_creation_rate": random.uniform(0, 5),  # thoughts per minute
            "refinement_rate": random.uniform(0, 10),  # refinements per minute
            "finalization_rate": random.uniform(0, 2),  # finalizations per minute
            "query_rate": random.uniform(0, 20),  # queries per minute
            "memory_churn": random.uniform(0, 0.1)  # fraction of memory changing
        }
        
        return {
            "latent_spaces": latent_spaces,
            "thought_states": all_thoughts,
            "memory_metrics": memory_metrics,
            "attention_weights": attention_weights,
            "activity_levels": activity_levels,
            "metadata": {
                "engram_healthy": health_data.get("status") == "healthy",
                "simulation": True,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _detect_events(self, current_state: MemoryState) -> List[MemoryEvent]:
        """Detect memory events by comparing current state with previous state"""
        events = []
        current_time = datetime.now()
        
        # Compare thought states with known states
        for thought_id, current_thought_state in current_state.thought_states.items():
            previous_state = self.known_thoughts.get(thought_id)
            
            if previous_state is None:
                # New thought discovered
                events.append(MemoryEvent(
                    event_type="thought_created",
                    timestamp=current_time,
                    component_id=current_state.component_id,
                    thought_id=thought_id,
                    new_state=current_thought_state,
                    event_data={"initial_state": current_thought_state}
                ))
            
            elif previous_state != current_thought_state:
                # State transition
                events.append(MemoryEvent(
                    event_type="state_transition", 
                    timestamp=current_time,
                    component_id=current_state.component_id,
                    thought_id=thought_id,
                    old_state=previous_state,
                    new_state=current_thought_state,
                    event_data={"transition": f"{previous_state} -> {current_thought_state}"}
                ))
        
        # Check for disappeared thoughts
        for thought_id, previous_state in self.known_thoughts.items():
            if thought_id not in current_state.thought_states:
                events.append(MemoryEvent(
                    event_type="thought_removed",
                    timestamp=current_time,
                    component_id=current_state.component_id,
                    thought_id=thought_id,
                    old_state=previous_state,
                    event_data={"last_state": previous_state}
                ))
        
        # Update known states
        self.known_thoughts = dict(current_state.thought_states)
        
        return events
    
    def _update_history(self, memory_state: MemoryState) -> None:
        """Update memory state history"""
        self.memory_history.append(memory_state)
        
        # Limit history size
        if len(self.memory_history) > self.max_history_size:
            self.memory_history = self.memory_history[-self.max_history_size:]
    
    async def _notify_memory_state(self, state: MemoryState) -> None:
        """Notify all listeners of memory state update"""
        for listener in self.listeners:
            try:
                await listener.on_memory_state(state)
            except Exception as e:
                logger.error(f"Error notifying listener {listener.__class__.__name__}: {e}")
    
    async def _notify_memory_event(self, event: MemoryEvent) -> None:
        """Notify all listeners of memory event"""
        for listener in self.listeners:
            try:
                await listener.on_memory_event(event)
            except Exception as e:
                logger.error(f"Error notifying listener {listener.__class__.__name__}: {e}")
    
    async def _notify_error(self, error: Exception) -> None:
        """Notify all listeners of stream error"""
        for listener in self.listeners:
            try:
                await listener.on_stream_error(error)
            except Exception as e:
                logger.error(f"Error notifying listener {listener.__class__.__name__} of error: {e}")
    
    def get_memory_history(self, 
                          duration: Optional[timedelta] = None,
                          limit: Optional[int] = None) -> List[MemoryState]:
        """Get historical memory states"""
        if not self.memory_history:
            return []
        
        states = self.memory_history.copy()
        
        # Filter by time if specified
        if duration:
            cutoff_time = datetime.now() - duration
            states = [s for s in states if s.timestamp >= cutoff_time]
        
        # Limit results if specified
        if limit:
            states = states[-limit:]
        
        return states
    
    def get_current_state(self) -> Optional[MemoryState]:
        """Get most recent memory state"""
        if self.memory_history:
            return self.memory_history[-1]
        return None
    
    async def force_poll(self) -> Optional[MemoryState]:
        """Force an immediate poll of memory state"""
        return await self._fetch_memory_state()


class NoesisMemoryAnalyzer(EngramStreamListener):
    """
    Noesis-specific analyzer for Engram memory streams
    Performs theoretical analysis on memory state evolution
    """
    
    def __init__(self, theoretical_framework=None):
        self.theoretical_framework = theoretical_framework
        self.state_vectors: List[np.ndarray] = []
        self.event_log: List[MemoryEvent] = []
        self.analysis_cache: Dict[str, Any] = {}
        
        logger.info("Initialized Noesis memory analyzer")
    
    async def on_memory_state(self, state: MemoryState) -> None:
        """Analyze new memory state"""
        try:
            # Convert state to vector for analysis
            state_vector = state.to_vector()
            self.state_vectors.append(state_vector)
            
            # Limit vector history
            if len(self.state_vectors) > 1000:
                self.state_vectors = self.state_vectors[-1000:]
            
            # Perform theoretical analysis if we have enough data
            if len(self.state_vectors) >= 10:
                await self._analyze_memory_dynamics(state)
            
            logger.debug(f"Analyzed memory state from {state.component_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing memory state: {e}")
    
    async def on_memory_event(self, event: MemoryEvent) -> None:
        """Analyze memory event"""
        try:
            self.event_log.append(event)
            
            # Limit event history
            if len(self.event_log) > 10000:
                self.event_log = self.event_log[-10000:]
            
            # Analyze event patterns
            await self._analyze_event_patterns(event)
            
            logger.debug(f"Analyzed memory event: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Error analyzing memory event: {e}")
    
    async def on_stream_error(self, error: Exception) -> None:
        """Handle stream errors"""
        logger.error(f"Memory stream error: {error}")
        # Could implement error recovery or notification here
    
    async def _analyze_memory_dynamics(self, current_state: MemoryState) -> None:
        """Perform theoretical analysis of memory dynamics"""
        if not self.theoretical_framework:
            return
        
        try:
            # Get recent state vectors for dynamics analysis
            recent_vectors = np.array(self.state_vectors[-50:])  # Last 50 states
            
            if self.theoretical_framework.manifold_analyzer:
                # Analyze memory state manifold
                manifold_analysis = await self.theoretical_framework.manifold_analyzer.analyze(
                    recent_vectors,
                    analysis_type="memory_manifold"
                )
                self.analysis_cache["manifold"] = manifold_analysis
            
            if self.theoretical_framework.dynamics_analyzer:
                # Analyze memory dynamics 
                dynamics_analysis = await self.theoretical_framework.dynamics_analyzer.analyze(
                    recent_vectors,
                    analysis_type="memory_dynamics"
                )
                self.analysis_cache["dynamics"] = dynamics_analysis
                
            if self.theoretical_framework.catastrophe_analyzer:
                # Look for phase transitions in memory
                catastrophe_analysis = await self.theoretical_framework.catastrophe_analyzer.analyze(
                    recent_vectors,
                    analysis_type="memory_transitions"
                )
                self.analysis_cache["catastrophe"] = catastrophe_analysis
                
            logger.debug("Completed theoretical analysis of memory dynamics")
            
        except Exception as e:
            logger.error(f"Error in memory dynamics analysis: {e}")
    
    async def _analyze_event_patterns(self, event: MemoryEvent) -> None:
        """Analyze patterns in memory events"""
        try:
            # Get recent events for pattern analysis
            recent_events = self.event_log[-100:]  # Last 100 events
            
            # Analyze event frequency patterns
            event_types = [e.event_type for e in recent_events]
            type_counts = {}
            for event_type in event_types:
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
            
            # Analyze temporal patterns
            event_times = [e.timestamp for e in recent_events]
            if len(event_times) >= 2:
                time_intervals = [
                    (event_times[i] - event_times[i-1]).total_seconds()
                    for i in range(1, len(event_times))
                ]
                
                # Store pattern analysis
                self.analysis_cache["event_patterns"] = {
                    "type_distribution": type_counts,
                    "average_interval": np.mean(time_intervals) if time_intervals else 0,
                    "event_rate": len(recent_events) / (
                        (event_times[-1] - event_times[0]).total_seconds() / 60
                    ) if len(event_times) > 1 else 0  # events per minute
                }
            
        except Exception as e:
            logger.error(f"Error analyzing event patterns: {e}")
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """Get latest theoretical analysis results"""
        return self.analysis_cache.copy()
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about observed memory states"""
        if not self.state_vectors:
            return {}
        
        vectors = np.array(self.state_vectors)
        
        return {
            "total_observations": len(self.state_vectors),
            "vector_dimensionality": vectors.shape[1] if vectors.ndim > 1 else 0,
            "observation_span_minutes": (
                (datetime.now() - self.event_log[0].timestamp).total_seconds() / 60
                if self.event_log else 0
            ),
            "mean_vector": np.mean(vectors, axis=0).tolist() if vectors.ndim > 1 else [],
            "std_vector": np.std(vectors, axis=0).tolist() if vectors.ndim > 1 else [],
            "total_events": len(self.event_log),
            "event_types": list(set(e.event_type for e in self.event_log))
        }