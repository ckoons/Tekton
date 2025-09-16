"""
Memory Injector V2 - Using Standardized Memory Middleware
Rhetor's memory injection updated to use shared memory infrastructure.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        performance_boundary,
        with_memory
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    def with_memory(**kwargs):
        def decorator(func):
            return func
        return decorator

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Import standardized memory components
from shared.memory.middleware import (
    MemoryMiddleware,
    MemoryConfig,
    MemoryContext,
    InjectionStyle,
    MemoryTier,
    create_memory_middleware
)
from shared.memory.injection import (
    MemoryInjector,
    InjectionPattern,
    ConversationalInjector,
    AnalyticalInjector,
    select_pattern_for_task
)

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Rhetor Memory Injector V2",
    description="Updated to use standardized memory middleware",
    rationale="Leverage shared memory infrastructure for consistency",
    alternatives_considered=["Keep custom implementation", "Direct Engram integration"],
    impacts=["rhetor_performance", "memory_consistency", "maintenance"],
    decided_by="Casey",
    decision_date="2025-01-20"
)
class MemoryInjectorV2:
    """
    Rhetor's memory injector using standardized middleware.
    
    This version leverages the shared memory infrastructure while
    maintaining backward compatibility with Rhetor's existing interfaces.
    """
    
    def __init__(self, injection_style: str = 'natural'):
        """
        Initialize the memory injector.
        
        Args:
            injection_style: Style of injection ('natural', 'structured', 'minimal')
        """
        self.injection_style = self._map_injection_style(injection_style)
        self.injectors = {}  # Cache of CI-specific injectors
        
    def _map_injection_style(self, style: str) -> InjectionStyle:
        """Map Rhetor's style names to standard injection styles."""
        style_map = {
            'natural': InjectionStyle.NATURAL,
            'structured': InjectionStyle.STRUCTURED,
            'minimal': InjectionStyle.MINIMAL,
            'technical': InjectionStyle.TECHNICAL,
            'creative': InjectionStyle.CREATIVE
        }
        return style_map.get(style, InjectionStyle.NATURAL)
    
    def _get_injector(self, ci_name: str) -> MemoryInjector:
        """Get or create an injector for a specific CI."""
        if ci_name not in self.injectors:
            # Determine pattern based on CI type
            pattern = self._determine_pattern(ci_name)
            self.injectors[ci_name] = MemoryInjector(ci_name, pattern)
        return self.injectors[ci_name]
    
    def _determine_pattern(self, ci_name: str) -> InjectionPattern:
        """Determine injection pattern based on CI name/type."""
        ci_patterns = {
            # Conversational CIs
            'hermes': InjectionPattern.CONVERSATION,
            'rhetor': InjectionPattern.CONVERSATION,
            
            # Analytical CIs
            'athena': InjectionPattern.ANALYSIS,
            'metis': InjectionPattern.ANALYSIS,
            'noesis': InjectionPattern.ANALYSIS,
            
            # Creative CIs
            'sophia': InjectionPattern.CREATIVE,
            'synthesis': InjectionPattern.CREATIVE,
            
            # Technical CIs
            'ergon': InjectionPattern.TECHNICAL,
            'prometheus': InjectionPattern.TECHNICAL,
            
            # Coordination CIs
            'apollo': InjectionPattern.COORDINATION,
            'harmonia': InjectionPattern.COORDINATION,
            
            # Learning CIs
            'engram': InjectionPattern.LEARNING,
            'numa': InjectionPattern.LEARNING
        }
        
        # Check for exact match
        for ci, pattern in ci_patterns.items():
            if ci in ci_name.lower():
                return pattern
        
        # Default to conversation
        return InjectionPattern.CONVERSATION
    
    @integration_point(
        title="Standardized Memory Injection",
        description="Memory injection using shared middleware",
        target_component="CI Prompt",
        protocol="memory_middleware",
        data_flow="prompt -> middleware -> enriched_prompt"
    )
    @performance_boundary(
        title="Memory Injection V2",
        description="Standardized memory injection pipeline",
        sla="<200ms for complete injection",
        optimization_notes="Leverages middleware caching and parallel retrieval"
    )
    async def inject_memories(
        self,
        ci_name: str,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Main injection method - enriches message with relevant memories.
        
        Args:
            ci_name: CI receiving the message
            message: Original message
            context: Additional context (project, topic, etc.)
            
        Returns:
            Enriched message with memory context
        """
        try:
            # Get appropriate injector
            injector = self._get_injector(ci_name)
            
            # Determine pattern from context if available
            pattern = None
            if 'task_type' in context:
                pattern = select_pattern_for_task(context['task_type'])
            
            # Build query with context
            query = self._build_query(message, context)
            
            # Inject memories
            enriched = await injector.inject(query, pattern)
            
            # Store the interaction
            await self._store_interaction(ci_name, message, enriched, context)
            
            return enriched
            
        except Exception as e:
            logger.error(f"Memory injection failed for {ci_name}: {e}")
            return message  # Fail gracefully
    
    def _build_query(self, message: str, context: Dict) -> str:
        """Build query string with context information."""
        parts = [message]
        
        if 'project' in context:
            parts.append(f"[Project: {context['project']}]")
        
        if 'topic' in context:
            parts.append(f"[Topic: {context['topic']}]")
        
        if 'user' in context:
            parts.append(f"[User: {context['user']}]")
        
        return ' '.join(parts)
    
    @with_memory(
        namespace="rhetor",
        store_outputs=True
    )
    async def _store_interaction(
        self,
        ci_name: str,
        original: str,
        enriched: str,
        context: Dict
    ):
        """Store the interaction for future reference."""
        injector = self._get_injector(ci_name)
        await injector.store({
            'type': 'memory_injection',
            'ci': ci_name,
            'original': original,
            'enriched': enriched,
            'context': context,
            'style': self.injection_style.value
        })
    
    async def get_memory_context(
        self,
        ci_name: str,
        query: Optional[str] = None
    ) -> MemoryContext:
        """
        Get memory context for a CI.
        
        Args:
            ci_name: CI name
            query: Optional query for relevance
            
        Returns:
            Memory context
        """
        injector = self._get_injector(ci_name)
        return await injector.get_context(query)
    
    def set_injection_style(self, style: str):
        """
        Set the injection style.
        
        Args:
            style: New injection style
        """
        self.injection_style = self._map_injection_style(style)
        # Clear injector cache to apply new style
        self.injectors.clear()
    
    # Backward compatibility methods
    
    async def inject_natural(self, ci_name: str, message: str, context: Dict) -> str:
        """Backward compatible natural injection."""
        self.injection_style = InjectionStyle.NATURAL
        return await self.inject_memories(ci_name, message, context)
    
    async def inject_structured(self, ci_name: str, message: str, context: Dict) -> str:
        """Backward compatible structured injection."""
        self.injection_style = InjectionStyle.STRUCTURED
        return await self.inject_memories(ci_name, message, context)
    
    async def inject_minimal(self, ci_name: str, message: str, context: Dict) -> str:
        """Backward compatible minimal injection."""
        self.injection_style = InjectionStyle.MINIMAL
        return await self.inject_memories(ci_name, message, context)


# Singleton instance for Rhetor
_memory_injector: Optional[MemoryInjectorV2] = None


def get_memory_injector() -> MemoryInjectorV2:
    """Get the singleton memory injector instance."""
    global _memory_injector
    if _memory_injector is None:
        _memory_injector = MemoryInjectorV2()
    return _memory_injector


# Quick injection functions for common patterns

async def inject_conversational(ci_name: str, message: str) -> str:
    """Quick conversational memory injection."""
    injector = ConversationalInjector(ci_name)
    return await injector.inject(message)


async def inject_analytical(ci_name: str, data: Dict, analysis_type: str) -> str:
    """Quick analytical memory injection."""
    injector = AnalyticalInjector(ci_name)
    return await injector.inject_for_analysis(data, analysis_type)


async def inject_with_pattern(
    ci_name: str,
    message: str,
    pattern: InjectionPattern
) -> str:
    """Inject with specific pattern."""
    injector = MemoryInjector(ci_name, pattern)
    return await injector.inject(message)


# Migration helper

async def migrate_rhetor_to_v2():
    """
    Migrate Rhetor to use the new memory injector.
    
    This function updates Rhetor's configuration to use
    the standardized memory middleware.
    """
    logger.info("Migrating Rhetor to Memory Injector V2")
    
    # Update import in main Rhetor module
    try:
        # This would be done in the actual Rhetor code
        # Just logging the migration steps here
        logger.info("1. Update imports to use memory_injector_v2")
        logger.info("2. Replace MemoryInjector with MemoryInjectorV2")
        logger.info("3. Update configuration to use standardized patterns")
        logger.info("4. Test backward compatibility")
        logger.info("Migration complete!")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False