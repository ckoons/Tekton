#!/usr/bin/env python3
"""
Unified AI Registry for Tekton Platform

Provides both sync and async interfaces for AI discovery and management.
Single source of truth for all AI registrations.

Features:
- Event-driven architecture with real-time updates
- Health monitoring and status tracking
- Smart routing with load balancing
- Both sync and async interfaces
- Multiple backend support (file, memory, Engram)
- Performance metrics and analytics
"""

import asyncio
import json
import logging
import time
import os
from typing import Dict, Optional, Any, List, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from datetime import datetime
import fcntl
import tempfile
from collections import defaultdict

from landmarks import (
    architecture_decision,
    performance_boundary,
    integration_point,
    state_checkpoint,
    danger_zone,
    api_contract
)

from .socket_client import AISocketClient

logger = logging.getLogger(__name__)


class AIStatus(Enum):
    """AI specialist status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNRESPONSIVE = "unresponsive"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class AISpecialist:
    """Represents an AI specialist in the registry"""
    id: str
    name: str
    port: int
    host: str = "localhost"
    model: str = "unknown"
    component: str = ""
    capabilities: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    status: AIStatus = AIStatus.UNKNOWN
    last_seen: float = 0
    registered_at: float = field(default_factory=time.time)
    response_times: List[float] = field(default_factory=list)
    success_rate: float = 1.0
    total_requests: int = 0
    failed_requests: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AISpecialist':
        """Create from dictionary"""
        data = data.copy()
        if 'status' in data:
            data['status'] = AIStatus(data['status'])
        return cls(**data)
    
    def update_metrics(self, response_time: float, success: bool):
        """Update performance metrics"""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
        
        # Update rolling response times (keep last 20)
        if success:
            self.response_times.append(response_time)
            if len(self.response_times) > 20:
                self.response_times.pop(0)
        
        # Calculate success rate
        self.success_rate = (self.total_requests - self.failed_requests) / self.total_requests
        
    @property
    def avg_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def is_available(self) -> bool:
        """Check if AI is available for requests"""
        return self.status in [AIStatus.HEALTHY, AIStatus.DEGRADED]


class AIRegistryBackend(ABC):
    """Abstract backend for registry storage"""
    
    @abstractmethod
    async def load(self) -> Dict[str, AISpecialist]:
        """Load all specialists from storage"""
        pass
    
    @abstractmethod
    async def save(self, specialists: Dict[str, AISpecialist]) -> bool:
        """Save all specialists to storage"""
        pass
    
    @abstractmethod
    async def get(self, ai_id: str) -> Optional[AISpecialist]:
        """Get a specific specialist"""
        pass
    
    @abstractmethod
    async def set(self, ai_id: str, specialist: AISpecialist) -> bool:
        """Save a specific specialist"""
        pass
    
    @abstractmethod
    async def delete(self, ai_id: str) -> bool:
        """Delete a specific specialist"""
        pass
    
    @abstractmethod
    async def list_ids(self) -> List[str]:
        """List all specialist IDs"""
        pass


class FileBackend(AIRegistryBackend):
    """File-based backend for registry storage"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path:
            self.registry_path = registry_path
        else:
            self.registry_path = Path.home() / '.tekton' / 'ai_registry' / 'unified_registry.json'
        
        # Ensure directory exists
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def load(self) -> Dict[str, AISpecialist]:
        """Load registry from file"""
        if not self.registry_path.exists():
            return {}
            
        try:
            with open(self.registry_path, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return {
                        ai_id: AISpecialist.from_dict(spec_data)
                        for ai_id, spec_data in data.items()
                    }
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return {}
    
    async def save(self, specialists: Dict[str, AISpecialist]) -> bool:
        """Save registry to file atomically"""
        try:
            # Convert to serializable format
            data = {
                ai_id: spec.to_dict()
                for ai_id, spec in specialists.items()
            }
            
            # Write to temp file first
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=self.registry_path.parent,
                delete=False
            ) as tmp:
                json.dump(data, tmp, indent=2)
                tmp_path = Path(tmp.name)
            
            # Atomic rename
            tmp_path.replace(self.registry_path)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
            return False
    
    async def get(self, ai_id: str) -> Optional[AISpecialist]:
        """Get specific specialist"""
        specialists = await self.load()
        return specialists.get(ai_id)
    
    async def set(self, ai_id: str, specialist: AISpecialist) -> bool:
        """Save specific specialist"""
        specialists = await self.load()
        specialists[ai_id] = specialist
        return await self.save(specialists)
    
    async def delete(self, ai_id: str) -> bool:
        """Delete specific specialist"""
        specialists = await self.load()
        if ai_id in specialists:
            del specialists[ai_id]
            return await self.save(specialists)
        return False
    
    async def list_ids(self) -> List[str]:
        """List all specialist IDs"""
        specialists = await self.load()
        return list(specialists.keys())


class MemoryBackend(AIRegistryBackend):
    """In-memory backend for testing and caching"""
    
    def __init__(self):
        self._specialists: Dict[str, AISpecialist] = {}
        
    async def load(self) -> Dict[str, AISpecialist]:
        return self._specialists.copy()
    
    async def save(self, specialists: Dict[str, AISpecialist]) -> bool:
        self._specialists = specialists.copy()
        return True
    
    async def get(self, ai_id: str) -> Optional[AISpecialist]:
        return self._specialists.get(ai_id)
    
    async def set(self, ai_id: str, specialist: AISpecialist) -> bool:
        self._specialists[ai_id] = specialist
        return True
    
    async def delete(self, ai_id: str) -> bool:
        if ai_id in self._specialists:
            del self._specialists[ai_id]
            return True
        return False
    
    async def list_ids(self) -> List[str]:
        return list(self._specialists.keys())


@architecture_decision(
    title="Unified AI Registry Architecture",
    rationale="Create a single source of truth for all AI specialists with event-driven updates and health monitoring",
    alternatives_considered=["Distributed registries", "Static configuration", "Service mesh"],
    impacts=["scalability", "consistency", "observability"],
    decided_by="Casey"
)
@state_checkpoint(
    title="Central AI Registry State",
    state_type="singleton",
    persistence=True,
    consistency_requirements="Eventually consistent with file locking",
    recovery_strategy="Reload from persistent storage on restart"
)
class UnifiedAIRegistry:
    """
    Unified AI Registry with event-driven updates and health monitoring.
    
    Features:
    - Event bus for real-time updates
    - Health monitoring with automatic status updates
    - Smart discovery with caching
    - Performance metrics tracking
    - Both sync and async interfaces
    """
    
    def __init__(self, backend: Optional[AIRegistryBackend] = None):
        self.backend = backend or FileBackend()
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._health_task: Optional[asyncio.Task] = None
        self._discovery_cache: Dict[str, Tuple[float, List[AISpecialist]]] = {}
        self._cache_ttl = 60  # seconds
        self._socket_client = AISocketClient(default_timeout=5.0)
        self._running = False
        
    async def start(self):
        """Start background services"""
        if self._running:
            return
            
        self._running = True
        self._health_task = asyncio.create_task(self._health_monitor())
        logger.info("Unified AI Registry started")
        
    async def stop(self):
        """Stop background services"""
        self._running = False
        
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Unified AI Registry stopped")
    
    # Event System
    def on(self, event: str, handler: Callable):
        """
        Register event handler.
        
        Events:
        - registered: New AI registered
        - deregistered: AI removed
        - status_changed: AI status changed
        - discovered: AI discovery completed
        - metrics_updated: Performance metrics updated
        """
        self._event_handlers[event].append(handler)
        
    def off(self, event: str, handler: Callable):
        """Unregister event handler"""
        if handler in self._event_handlers[event]:
            self._event_handlers[event].remove(handler)
            
    async def _emit(self, event: str, data: Any):
        """Emit event to all handlers"""
        for handler in self._event_handlers[event]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    # Run sync handlers in executor
                    await asyncio.get_event_loop().run_in_executor(
                        None, handler, data
                    )
            except Exception as e:
                logger.error(f"Event handler error for {event}: {e}")
    
    # Core Registry Operations
    async def register(self, 
                      ai_id: str,
                      name: str,
                      port: int,
                      host: str = "localhost",
                      model: str = "unknown",
                      component: str = "",
                      capabilities: Optional[List[str]] = None,
                      roles: Optional[List[str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new AI specialist"""
        specialist = AISpecialist(
            id=ai_id,
            name=name,
            port=port,
            host=host,
            model=model,
            component=component,
            capabilities=capabilities or [],
            roles=roles or [],
            status=AIStatus.STARTING,
            metadata=metadata or {}
        )
        
        # Save to backend
        success = await self.backend.set(ai_id, specialist)
        
        if success:
            # Clear discovery cache
            self._discovery_cache.clear()
            
            # Emit event
            await self._emit("registered", specialist)
            
            # Initial health check
            asyncio.create_task(self._check_health(specialist))
            
        return success
    
    async def deregister(self, ai_id: str) -> bool:
        """Deregister an AI specialist"""
        specialist = await self.backend.get(ai_id)
        if not specialist:
            return False
            
        success = await self.backend.delete(ai_id)
        
        if success:
            # Clear discovery cache
            self._discovery_cache.clear()
            
            # Emit event
            await self._emit("deregistered", specialist)
            
        return success
    
    async def get(self, ai_id: str) -> Optional[AISpecialist]:
        """Get a specific AI specialist"""
        return await self.backend.get(ai_id)
    
    @performance_boundary(
        title="AI Discovery with Caching",
        sla="<10ms for cached queries, <100ms for fresh queries",
        optimization_notes="Uses in-memory cache with 60s TTL, filters are applied in-memory",
        metrics={"cache_ttl": "60s", "typical_results": "1-5 AIs"}
    )
    async def discover(self,
                      role: Optional[str] = None,
                      capabilities: Optional[List[str]] = None,
                      status: Optional[AIStatus] = None,
                      component: Optional[str] = None,
                      min_success_rate: float = 0.0) -> List[AISpecialist]:
        """
        Discover AI specialists with smart filtering.
        
        Args:
            role: Filter by role
            capabilities: Required capabilities
            status: Filter by status
            component: Filter by component
            min_success_rate: Minimum success rate (0-1)
            
        Returns:
            List of matching specialists sorted by performance
        """
        # Check cache
        cache_key = f"{role}:{capabilities}:{status}:{component}:{min_success_rate}"
        if cache_key in self._discovery_cache:
            cached_time, cached_result = self._discovery_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_result
        
        # Load all specialists
        all_specialists = await self.backend.load()
        
        # Filter
        results = []
        for specialist in all_specialists.values():
            # Role filter
            if role and role not in specialist.roles:
                continue
                
            # Capabilities filter
            if capabilities:
                if not all(cap in specialist.capabilities for cap in capabilities):
                    continue
                    
            # Status filter
            if status and specialist.status != status:
                continue
                
            # Component filter
            if component and specialist.component != component:
                continue
                
            # Success rate filter
            if specialist.success_rate < min_success_rate:
                continue
                
            results.append(specialist)
        
        # Sort by performance (success rate * avg response time)
        results.sort(
            key=lambda s: (s.success_rate, -s.avg_response_time),
            reverse=True
        )
        
        # Cache results
        self._discovery_cache[cache_key] = (time.time(), results)
        
        # Emit event
        await self._emit("discovered", results)
        
        return results
    
    async def update_status(self, ai_id: str, status: AIStatus) -> bool:
        """Update AI status"""
        specialist = await self.backend.get(ai_id)
        if not specialist:
            return False
            
        old_status = specialist.status
        specialist.status = status
        specialist.last_seen = time.time()
        
        success = await self.backend.set(ai_id, specialist)
        
        if success and old_status != status:
            await self._emit("status_changed", {
                "specialist": specialist,
                "old_status": old_status,
                "new_status": status
            })
            
        return success
    
    async def update_metrics(self, 
                           ai_id: str,
                           response_time: float,
                           success: bool) -> bool:
        """Update performance metrics for an AI"""
        specialist = await self.backend.get(ai_id)
        if not specialist:
            return False
            
        specialist.update_metrics(response_time, success)
        
        success = await self.backend.set(ai_id, specialist)
        
        if success:
            await self._emit("metrics_updated", {
                "specialist": specialist,
                "response_time": response_time,
                "success": success
            })
            
        return success
    
    # Health Monitoring
    async def _health_monitor(self):
        """Background health monitoring task"""
        while self._running:
            try:
                # Wait before first check
                await asyncio.sleep(30)
                
                # Check all specialists
                specialists = await self.backend.load()
                
                for specialist in specialists.values():
                    if self._running:
                        await self._check_health(specialist)
                        await asyncio.sleep(0.1)  # Small delay between checks
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_health(self, specialist: AISpecialist) -> AIStatus:
        """Check health of a specialist"""
        try:
            start_time = time.time()
            
            # Send ping
            response = await self._socket_client.ping(
                specialist.host,
                specialist.port,
                timeout=5.0
            )
            
            elapsed = time.time() - start_time
            
            if response["success"]:
                # Update metrics
                await self.update_metrics(specialist.id, elapsed, True)
                
                # Determine health based on response time
                if elapsed < 1.0:
                    new_status = AIStatus.HEALTHY
                elif elapsed < 5.0:
                    new_status = AIStatus.DEGRADED
                else:
                    new_status = AIStatus.UNRESPONSIVE
            else:
                # Update metrics
                await self.update_metrics(specialist.id, elapsed, False)
                new_status = AIStatus.UNRESPONSIVE
                
            # Update status
            if specialist.status != new_status:
                await self.update_status(specialist.id, new_status)
                
            return new_status
            
        except Exception as e:
            logger.error(f"Health check failed for {specialist.id}: {e}")
            await self.update_status(specialist.id, AIStatus.UNKNOWN)
            return AIStatus.UNKNOWN
    
    # Utility Methods
    async def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        specialists = await self.backend.load()
        
        status_counts = defaultdict(int)
        total_requests = 0
        total_failures = 0
        
        for spec in specialists.values():
            status_counts[spec.status.value] += 1
            total_requests += spec.total_requests
            total_failures += spec.failed_requests
            
        return {
            "total_specialists": len(specialists),
            "status_breakdown": dict(status_counts),
            "total_requests": total_requests,
            "total_failures": total_failures,
            "overall_success_rate": (total_requests - total_failures) / total_requests if total_requests > 0 else 1.0,
            "last_update": datetime.now().isoformat()
        }
    
    # Synchronous Wrappers
    def register_sync(self, **kwargs) -> bool:
        """Sync wrapper for register"""
        return self._run_async(self.register(**kwargs))
    
    def deregister_sync(self, ai_id: str) -> bool:
        """Sync wrapper for deregister"""
        return self._run_async(self.deregister(ai_id))
    
    def get_sync(self, ai_id: str) -> Optional[AISpecialist]:
        """Sync wrapper for get"""
        return self._run_async(self.get(ai_id))
    
    def discover_sync(self, **kwargs) -> List[AISpecialist]:
        """Sync wrapper for discover"""
        return self._run_async(self.discover(**kwargs))
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop running, create one
            return asyncio.run(coro)
        else:
            # Loop already running
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()


# Global registry instance
_global_registry: Optional[UnifiedAIRegistry] = None


def get_registry() -> UnifiedAIRegistry:
    """Get the global registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = UnifiedAIRegistry()
    return _global_registry


async def init_registry():
    """Initialize and start the global registry"""
    registry = get_registry()
    await registry.start()
    return registry