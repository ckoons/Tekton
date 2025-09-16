"""
Memory Decorators for Tekton CIs
Automatic memory handling through function decoration.
"""

import asyncio
import functools
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Import middleware components
try:
    from .middleware import (
        MemoryMiddleware,
        MemoryConfig,
        MemoryContext,
        InjectionStyle,
        MemoryTier,
        create_memory_middleware
    )
    from .injection import (
        MemoryInjector,
        InjectionPattern,
        select_pattern_for_task
    )
except ImportError:
    from middleware import (
        MemoryMiddleware,
        MemoryConfig,
        MemoryContext,
        InjectionStyle,
        MemoryTier,
        create_memory_middleware
    )
    from injection import (
        MemoryInjector,
        InjectionPattern,
        select_pattern_for_task
    )

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


class ConsolidationType(Enum):
    """Types of memory consolidation."""
    IMMEDIATE = "immediate"      # Consolidate right away
    DELAYED = "delayed"          # Consolidate after delay
    BATCH = "batch"             # Batch with other memories
    PERIODIC = "periodic"       # Consolidate periodically


class MemoryVisibility(Enum):
    """Visibility levels for shared memories."""
    PRIVATE = "private"         # Only this CI
    FAMILY = "family"          # All CIs in family
    TEAM = "team"             # Specific team of CIs
    PUBLIC = "public"         # All CIs


@dataclass
class MemoryDecoratorConfig:
    """Configuration for memory decorators."""
    namespace: Optional[str] = None
    store_inputs: bool = True
    store_outputs: bool = True
    inject_context: bool = True
    memory_tiers: List[MemoryTier] = None
    injection_style: InjectionStyle = InjectionStyle.NATURAL
    context_depth: int = 10
    relevance_threshold: float = 0.7
    auto_consolidate: bool = False
    consolidation_type: ConsolidationType = ConsolidationType.IMMEDIATE
    visibility: MemoryVisibility = MemoryVisibility.PRIVATE
    share_with: List[str] = None
    memory_type: str = "general"
    reflection_depth: str = "shallow"


# Global registry for memory-decorated functions
_memory_functions = {}


def with_memory(**decorator_kwargs):
    """
    Decorator that automatically handles memory storage and retrieval.
    
    Usage:
        @with_memory(
            namespace="apollo",
            store_inputs=True,
            store_outputs=True,
            inject_context=True,
            memory_tiers=["recent", "session", "domain"]
        )
        async def process_request(message: str) -> str:
            # Memory context available via self.memory_context
            # or as memory_context parameter
            return response
    
    Args:
        namespace: Memory namespace (defaults to function module)
        store_inputs: Store function inputs
        store_outputs: Store function outputs
        inject_context: Inject memory context
        memory_tiers: List of memory tiers to retrieve
        injection_style: How to format injected memories
        context_depth: Number of memories to retrieve
        relevance_threshold: Minimum relevance score
    """
    def decorator(func: F) -> F:
        # Parse configuration
        config = MemoryDecoratorConfig(**decorator_kwargs)
        
        # Default namespace to module name
        if config.namespace is None:
            config.namespace = func.__module__.split('.')[-1]
        
        # Default memory tiers
        if config.memory_tiers is None:
            config.memory_tiers = [
                MemoryTier.RECENT,
                MemoryTier.SESSION,
                MemoryTier.DOMAIN
            ]
        
        # Create middleware
        middleware_config = MemoryConfig(
            namespace=config.namespace,
            injection_style=config.injection_style,
            memory_tiers=config.memory_tiers,
            store_inputs=config.store_inputs,
            store_outputs=config.store_outputs,
            inject_context=config.inject_context,
            context_depth=config.context_depth,
            relevance_threshold=config.relevance_threshold
        )
        middleware = MemoryMiddleware(middleware_config)
        
        # Register function
        _memory_functions[f"{config.namespace}.{func.__name__}"] = {
            'function': func,
            'config': config,
            'middleware': middleware
        }
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get memory context if needed
            memory_context = None
            if config.inject_context:
                # Extract query from arguments
                query = _extract_query(args, kwargs)
                memory_context = await middleware.get_memory_context(query)
                
                # Inject context into function
                if 'memory_context' in inspect.signature(func).parameters:
                    kwargs['memory_context'] = memory_context
                elif args and hasattr(args[0], '__dict__'):
                    # Set on self if method
                    args[0].memory_context = memory_context
            
            # Store inputs if configured
            if config.store_inputs:
                await middleware.store_interaction({
                    'type': 'input',
                    'function': func.__name__,
                    'namespace': config.namespace,
                    'args': _serialize_args(args),
                    'kwargs': _serialize_kwargs(kwargs),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Execute function
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                # Store error
                await middleware.store_interaction({
                    'type': 'error',
                    'function': func.__name__,
                    'namespace': config.namespace,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                raise
            
            # Store outputs if configured
            if config.store_outputs:
                await middleware.store_interaction({
                    'type': 'output',
                    'function': func.__name__,
                    'namespace': config.namespace,
                    'result': _serialize_result(result),
                    'timestamp': datetime.now().isoformat()
                })
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Run async function in event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def memory_aware(**decorator_kwargs):
    """
    Decorator that provides memory context without storing.
    
    Usage:
        @memory_aware(
            namespace="athena",
            context_depth=10,
            relevance_threshold=0.7
        )
        async def analyze_pattern(data: dict) -> dict:
            # Receives memory context but doesn't store
            relevant = self.memory_context.get("relevant")
            return analysis
    
    Args:
        namespace: Memory namespace
        context_depth: Number of memories to retrieve
        relevance_threshold: Minimum relevance score
    """
    def decorator(func: F) -> F:
        # Use with_memory but disable storage
        return with_memory(
            store_inputs=False,
            store_outputs=False,
            inject_context=True,
            **decorator_kwargs
        )(func)
    
    return decorator


def memory_trigger(**decorator_kwargs):
    """
    Decorator that triggers memory operations on events.
    
    Usage:
        @memory_trigger(
            on_event="task_completion",
            consolidation_type="immediate",
            reflection_depth="full"
        )
        async def on_task_complete(task_result: dict):
            # Triggers memory consolidation
            pass
    
    Args:
        on_event: Event that triggers this function
        consolidation_type: How to consolidate memories
        reflection_depth: Depth of reflection process
    """
    def decorator(func: F) -> F:
        config = MemoryDecoratorConfig(**decorator_kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Trigger consolidation
            if config.auto_consolidate:
                await _trigger_consolidation(
                    config.namespace or func.__module__,
                    config.consolidation_type,
                    config.reflection_depth
                )
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def collective_memory(**decorator_kwargs):
    """
    Decorator for functions that contribute to shared CI memory.
    
    Usage:
        @collective_memory(
            share_with=["apollo", "athena", "rhetor"],
            memory_type="breakthrough",
            visibility="family"
        )
        async def share_insight(insight: dict):
            # Automatically shares with specified CIs
            pass
    
    Args:
        share_with: List of CIs to share with
        memory_type: Type of shared memory
        visibility: Visibility level
    """
    def decorator(func: F) -> F:
        config = MemoryDecoratorConfig(**decorator_kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Share result with collective
            if config.share_with or config.visibility != MemoryVisibility.PRIVATE:
                await _share_memory(
                    data=result,
                    share_with=config.share_with,
                    visibility=config.visibility,
                    memory_type=config.memory_type,
                    namespace=config.namespace or func.__module__
                )
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def memory_context(**decorator_kwargs):
    """
    Decorator that defines memory retrieval patterns.
    
    Usage:
        @memory_context(
            context_type="conversation",
            lookback_window="30_minutes",
            include_associations=True,
            semantic_clustering=True
        )
        async def get_conversation_context(topic: str) -> dict:
            # Retrieves contextually relevant memories
            return context
    
    Args:
        context_type: Type of context to retrieve
        lookback_window: Time window for memories
        include_associations: Include associated memories
        semantic_clustering: Group by semantic similarity
    """
    def decorator(func: F) -> F:
        config = MemoryDecoratorConfig(**decorator_kwargs)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get specialized context
            context = await _get_specialized_context(
                context_type=decorator_kwargs.get('context_type', 'general'),
                lookback_window=decorator_kwargs.get('lookback_window', '1_hour'),
                include_associations=decorator_kwargs.get('include_associations', True),
                semantic_clustering=decorator_kwargs.get('semantic_clustering', False),
                namespace=config.namespace or func.__module__
            )
            
            # Inject context
            if 'memory_context' in inspect.signature(func).parameters:
                kwargs['memory_context'] = context
            
            # Execute function
            result = await func(*args, **kwargs)
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Helper functions

def _extract_query(args: tuple, kwargs: dict) -> Optional[str]:
    """Extract query string from function arguments."""
    # Check kwargs first
    if 'query' in kwargs:
        return str(kwargs['query'])
    if 'message' in kwargs:
        return str(kwargs['message'])
    if 'prompt' in kwargs:
        return str(kwargs['prompt'])
    
    # Check args
    if args:
        # Skip self/cls if present
        start_idx = 1 if args and hasattr(args[0], '__dict__') else 0
        if len(args) > start_idx and isinstance(args[start_idx], str):
            return args[start_idx]
    
    return None


def _serialize_args(args: tuple) -> list:
    """Serialize function arguments for storage."""
    serialized = []
    for arg in args:
        if hasattr(arg, '__dict__'):
            # Skip self/cls
            continue
        elif isinstance(arg, (str, int, float, bool, list, dict)):
            serialized.append(arg)
        else:
            serialized.append(str(arg))
    return serialized


def _serialize_kwargs(kwargs: dict) -> dict:
    """Serialize function keyword arguments for storage."""
    serialized = {}
    for key, value in kwargs.items():
        if isinstance(value, (str, int, float, bool, list, dict)):
            serialized[key] = value
        else:
            serialized[key] = str(value)
    return serialized


def _serialize_result(result: Any) -> Any:
    """Serialize function result for storage."""
    if isinstance(result, (str, int, float, bool, list, dict)):
        return result
    elif hasattr(result, 'to_dict'):
        return result.to_dict()
    elif hasattr(result, '__dict__'):
        return {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
    else:
        return str(result)


async def _trigger_consolidation(
    namespace: str,
    consolidation_type: ConsolidationType,
    reflection_depth: str
):
    """Trigger memory consolidation."""
    try:
        # This would integrate with Engram's consolidation system
        logger.info(f"Triggering {consolidation_type.value} consolidation for {namespace}")
        logger.info(f"Reflection depth: {reflection_depth}")
        
        # TODO: Implement actual consolidation
        # from Engram.engram.core.consolidation import consolidate_memories
        # await consolidate_memories(namespace, consolidation_type, reflection_depth)
        
    except Exception as e:
        logger.error(f"Consolidation failed: {e}")


async def _share_memory(
    data: Any,
    share_with: Optional[List[str]],
    visibility: MemoryVisibility,
    memory_type: str,
    namespace: str
):
    """Share memory with other CIs."""
    try:
        logger.info(f"Sharing {memory_type} memory from {namespace}")
        logger.info(f"Visibility: {visibility.value}, Recipients: {share_with}")
        
        # TODO: Implement actual sharing
        # from shared.memory.collective import CollectiveMemory
        # collective = CollectiveMemory()
        # await collective.share(data, share_with, visibility, memory_type)
        
    except Exception as e:
        logger.error(f"Memory sharing failed: {e}")


async def _get_specialized_context(
    context_type: str,
    lookback_window: str,
    include_associations: bool,
    semantic_clustering: bool,
    namespace: str
) -> MemoryContext:
    """Get specialized memory context."""
    try:
        # Parse lookback window
        window_parts = lookback_window.split('_')
        if len(window_parts) == 2:
            amount = int(window_parts[0])
            unit = window_parts[1]
            
            if unit == 'minutes':
                delta = timedelta(minutes=amount)
            elif unit == 'hours':
                delta = timedelta(hours=amount)
            elif unit == 'days':
                delta = timedelta(days=amount)
            else:
                delta = timedelta(hours=1)
        else:
            delta = timedelta(hours=1)
        
        logger.info(f"Getting {context_type} context for {namespace}")
        logger.info(f"Lookback: {delta}, Associations: {include_associations}")
        
        # Create specialized context
        # TODO: Implement actual context retrieval with time windows
        context = MemoryContext()
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to get specialized context: {e}")
        return MemoryContext()


# Convenience functions for common patterns

def memory_function(namespace: str):
    """Simple decorator for memory-enabled functions."""
    return with_memory(namespace=namespace)


def conversational_memory(namespace: str):
    """Decorator for conversational functions."""
    return with_memory(
        namespace=namespace,
        memory_tiers=[MemoryTier.RECENT, MemoryTier.SESSION],
        injection_style=InjectionStyle.NATURAL
    )


def analytical_memory(namespace: str):
    """Decorator for analytical functions."""
    return with_memory(
        namespace=namespace,
        memory_tiers=[MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS],
        injection_style=InjectionStyle.STRUCTURED
    )


def creative_memory(namespace: str):
    """Decorator for creative functions."""
    return with_memory(
        namespace=namespace,
        memory_tiers=[MemoryTier.ASSOCIATIONS, MemoryTier.COLLECTIVE],
        injection_style=InjectionStyle.CREATIVE
    )


# Registry access functions

def get_memory_functions() -> Dict[str, Dict]:
    """Get all registered memory-decorated functions."""
    return _memory_functions


def get_function_memory_config(func_path: str) -> Optional[MemoryDecoratorConfig]:
    """Get memory configuration for a function."""
    if func_path in _memory_functions:
        return _memory_functions[func_path]['config']
    return None


def clear_memory_registry():
    """Clear the memory function registry."""
    _memory_functions.clear()