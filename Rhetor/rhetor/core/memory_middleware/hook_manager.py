"""
Hook Manager for Memory Middleware
Manages pre/post processing hooks for CI interactions.
"""

import asyncio
import time
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        performance_boundary,
        state_checkpoint,
        ci_orchestrated,
        ci_collaboration
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def ci_orchestrated(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def ci_collaboration(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = logging.getLogger(__name__)


@dataclass
class HookMetrics:
    """Track hook performance metrics."""
    total_calls: int = 0
    total_time_ms: float = 0
    memory_references: int = 0
    memory_stores: int = 0
    
    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.total_calls if self.total_calls > 0 else 0


@architecture_decision(
    title="Memory Hook Architecture",
    description="Central hook manager for transparent CI memory integration",
    rationale="Provides unified pre/post processing for all CI interactions without modifying CI code",
    alternatives_considered=["Direct CI modification", "External proxy", "Message queue"],
    impacts=["ci_performance", "memory_persistence", "cognition_tracking"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
@ci_orchestrated(
    title="Memory Hook Orchestration",
    description="Orchestrates memory injection and extraction for CI cognition",
    orchestrator="memory_middleware",
    workflow=["pre_message", "ci_processing", "post_response", "consolidation"],
    ci_capabilities=["memory_recall", "context_enrichment", "insight_extraction"]
)
class HookManager:
    """
    Manages memory hooks for CI processing pipeline.
    
    Hooks are executed at specific points:
    - pre_message: Before message goes to CI
    - post_response: After CI responds
    - idle_consolidation: During idle periods
    - context_change: When switching topics/projects
    """
    
    @state_checkpoint(
        title="Hook Registry",
        description="Maintains registry of active hooks and metrics per CI",
        state_type="registry",
        persistence=False,
        consistency_requirements="Thread-safe access",
        recovery_strategy="Re-register hooks on restart"
    )
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {
            'pre_message': [],
            'post_response': [],
            'idle_consolidation': [],
            'context_change': []
        }
        self.metrics: Dict[str, HookMetrics] = {
            hook_type: HookMetrics() for hook_type in self.hooks
        }
        self.enabled = True
        
    def register(self, hook_type: str, callback: Callable, priority: int = 50):
        """
        Register a hook callback.
        
        Args:
            hook_type: Type of hook (pre_message, post_response, etc.)
            callback: Async function to call
            priority: Lower numbers execute first (0-100)
        """
        if hook_type not in self.hooks:
            raise ValueError(f"Unknown hook type: {hook_type}")
            
        # Store with priority for ordering
        self.hooks[hook_type].append((priority, callback))
        # Sort by priority
        self.hooks[hook_type].sort(key=lambda x: x[0])
        
        logger.info(f"Registered {callback.__name__} for {hook_type} hook")
        
    @integration_point(
        title="Pre-Message Hook Execution",
        description="Executes memory injection before CI processes message",
        target_component="CI System",
        protocol="hook_chain",
        data_flow="message → pre_hooks → enriched_message → CI",
        integration_date="2025-08-28"
    )
    @performance_boundary(
        title="Pre-Hook Chain",
        description="Sequential execution of pre-processing hooks",
        sla="<100ms total",
        optimization_notes="Hooks executed in priority order",
        measured_impact="Adds 20-50ms latency for memory enrichment"
    )
    async def execute_pre_message(self, ci_name: str, message: str, context: Dict[str, Any]) -> str:
        """
        Execute pre-message hooks to enrich the message with memory.
        
        Args:
            ci_name: Name of the CI receiving the message
            message: Original message
            context: Additional context
            
        Returns:
            Enriched message with memory context
        """
        if not self.enabled or not self.hooks['pre_message']:
            return message
            
        start_time = time.time()
        enriched_message = message
        
        try:
            for priority, hook in self.hooks['pre_message']:
                enriched_message = await hook(ci_name, enriched_message, context)
                
        except Exception as e:
            logger.error(f"Error in pre_message hook: {e}")
            # Return original message on error
            return message
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = self.metrics['pre_message']
            metrics.total_calls += 1
            metrics.total_time_ms += elapsed_ms
            
            if elapsed_ms > 100:
                logger.warning(f"Slow pre_message hook: {elapsed_ms:.2f}ms")
                
        return enriched_message
    
    @integration_point(
        title="Post-Response Hook Execution",
        description="Extracts memories after CI generates response",
        target_component="Memory System",
        protocol="async_hook_chain",
        data_flow="CI_response → post_hooks → memory_extraction → storage",
        integration_date="2025-08-28"
    )
    @performance_boundary(
        title="Post-Hook Chain",
        description="Async execution of memory extraction hooks",
        sla="<200ms total",
        optimization_notes="Extraction happens async, doesn't block response",
        measured_impact="No impact on response latency"
    )
    async def execute_post_response(self, ci_name: str, message: str, response: str, context: Dict[str, Any]):
        """
        Execute post-response hooks to extract memories.
        
        Args:
            ci_name: Name of the CI that responded
            message: Original message sent
            response: CI's response
            context: Additional context
        """
        if not self.enabled or not self.hooks['post_response']:
            return
            
        start_time = time.time()
        
        # Fire and forget - don't block response
        asyncio.create_task(self._async_post_response(ci_name, message, response, context, start_time))
        
    async def _async_post_response(self, ci_name: str, message: str, response: str, context: Dict[str, Any], start_time: float):
        """Async execution of post-response hooks."""
        try:
            for priority, hook in self.hooks['post_response']:
                await hook(ci_name, message, response, context)
                
        except Exception as e:
            logger.error(f"Error in post_response hook: {e}")
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = self.metrics['post_response']
            metrics.total_calls += 1
            metrics.total_time_ms += elapsed_ms
            
    @ci_collaboration(
        title="Idle Memory Consolidation",
        description="CI memory consolidation during quiet periods",
        participants=["memory_system", "target_ci"],
        coordination_method="background_task",
        synchronization="async_periodic"
    )
    async def execute_idle_consolidation(self, ci_name: str):
        """
        Execute memory consolidation during idle time.
        
        Args:
            ci_name: CI to consolidate memory for
        """
        if not self.enabled or not self.hooks['idle_consolidation']:
            return
            
        try:
            for priority, hook in self.hooks['idle_consolidation']:
                await hook(ci_name)
        except Exception as e:
            logger.error(f"Error in idle_consolidation hook: {e}")
            
    @state_checkpoint(
        title="Context Transition",
        description="Manages CI context switches and memory transitions",
        state_type="transition",
        persistence=True,
        consistency_requirements="Preserve context continuity",
        recovery_strategy="Load last known context"
    )
    async def execute_context_change(self, ci_name: str, old_context: Dict, new_context: Dict):
        """
        Execute hooks when context changes (topic/project switch).
        
        Args:
            ci_name: CI experiencing context change
            old_context: Previous context
            new_context: New context
        """
        if not self.enabled or not self.hooks['context_change']:
            return
            
        try:
            for priority, hook in self.hooks['context_change']:
                await hook(ci_name, old_context, new_context)
        except Exception as e:
            logger.error(f"Error in context_change hook: {e}")
    
    def get_metrics(self) -> Dict[str, Dict]:
        """Get performance metrics for all hooks."""
        return {
            hook_type: {
                'total_calls': metrics.total_calls,
                'avg_time_ms': metrics.avg_time_ms,
                'memory_references': metrics.memory_references,
                'memory_stores': metrics.memory_stores
            }
            for hook_type, metrics in self.metrics.items()
        }
        
    def toggle(self, enabled: Optional[bool] = None) -> bool:
        """Toggle hook system on/off."""
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = not self.enabled
        return self.enabled


# Singleton instance
_hook_manager = None


def get_hook_manager() -> HookManager:
    """Get the singleton HookManager instance."""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
    return _hook_manager