"""
Memory Injection Patterns for Tekton CIs
Standardized patterns for injecting memory context into CI interactions.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

try:
    # Try relative import first (when used as package)
    from .middleware import (
        MemoryMiddleware,
        MemoryConfig,
        MemoryContext,
        InjectionStyle,
        MemoryTier,
        create_memory_middleware
    )
except ImportError:
    # Fall back to absolute import (when used directly)
    from middleware import (
        MemoryMiddleware,
        MemoryConfig,
        MemoryContext,
        InjectionStyle,
        MemoryTier,
        create_memory_middleware
    )

logger = logging.getLogger(__name__)


class InjectionPattern(Enum):
    """Standard memory injection patterns."""
    CONVERSATION = "conversation"    # Chat-based interactions
    ANALYSIS = "analysis"            # Analytical tasks
    CREATIVE = "creative"            # Creative generation
    TECHNICAL = "technical"          # Technical problem solving
    COORDINATION = "coordination"    # Multi-CI coordination
    LEARNING = "learning"           # Learning and adaptation


@dataclass
class PatternConfig:
    """Configuration for specific injection patterns."""
    pattern: InjectionPattern
    style: InjectionStyle
    tiers: List[MemoryTier]
    context_depth: int
    relevance_threshold: float
    enable_collective: bool = False


# Standard pattern configurations
PATTERN_CONFIGS = {
    InjectionPattern.CONVERSATION: PatternConfig(
        pattern=InjectionPattern.CONVERSATION,
        style=InjectionStyle.NATURAL,
        tiers=[MemoryTier.RECENT, MemoryTier.SESSION],
        context_depth=10,
        relevance_threshold=0.6,
        enable_collective=False
    ),
    InjectionPattern.ANALYSIS: PatternConfig(
        pattern=InjectionPattern.ANALYSIS,
        style=InjectionStyle.STRUCTURED,
        tiers=[MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS],
        context_depth=15,
        relevance_threshold=0.8,
        enable_collective=False
    ),
    InjectionPattern.CREATIVE: PatternConfig(
        pattern=InjectionPattern.CREATIVE,
        style=InjectionStyle.CREATIVE,
        tiers=[MemoryTier.ASSOCIATIONS, MemoryTier.COLLECTIVE],
        context_depth=20,
        relevance_threshold=0.5,
        enable_collective=True
    ),
    InjectionPattern.TECHNICAL: PatternConfig(
        pattern=InjectionPattern.TECHNICAL,
        style=InjectionStyle.TECHNICAL,
        tiers=[MemoryTier.DOMAIN, MemoryTier.RECENT],
        context_depth=10,
        relevance_threshold=0.9,
        enable_collective=False
    ),
    InjectionPattern.COORDINATION: PatternConfig(
        pattern=InjectionPattern.COORDINATION,
        style=InjectionStyle.STRUCTURED,
        tiers=[MemoryTier.SESSION, MemoryTier.COLLECTIVE],
        context_depth=15,
        relevance_threshold=0.7,
        enable_collective=True
    ),
    InjectionPattern.LEARNING: PatternConfig(
        pattern=InjectionPattern.LEARNING,
        style=InjectionStyle.NATURAL,
        tiers=[MemoryTier.RECENT, MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS],
        context_depth=25,
        relevance_threshold=0.6,
        enable_collective=True
    )
}


class MemoryInjector:
    """
    High-level memory injection interface with pattern support.
    """
    
    def __init__(self, ci_name: str, default_pattern: InjectionPattern = InjectionPattern.CONVERSATION):
        """
        Initialize memory injector.
        
        Args:
            ci_name: Name of the CI
            default_pattern: Default injection pattern
        """
        self.ci_name = ci_name
        self.default_pattern = default_pattern
        self.middlewares = {}
        self._init_middlewares()
    
    def _init_middlewares(self):
        """Initialize middleware instances for each pattern."""
        for pattern, config in PATTERN_CONFIGS.items():
            middleware_config = MemoryConfig(
                namespace=self.ci_name,
                injection_style=config.style,
                memory_tiers=config.tiers,
                context_depth=config.context_depth,
                relevance_threshold=config.relevance_threshold,
                enable_collective=config.enable_collective
            )
            self.middlewares[pattern] = MemoryMiddleware(middleware_config)
    
    async def inject(
        self,
        prompt: str,
        pattern: Optional[InjectionPattern] = None,
        context: Optional[MemoryContext] = None
    ) -> str:
        """
        Inject memory into a prompt using specified pattern.
        
        Args:
            prompt: Original prompt
            pattern: Injection pattern to use
            context: Pre-retrieved context or None
            
        Returns:
            Enriched prompt
        """
        pattern = pattern or self.default_pattern
        middleware = self.middlewares.get(pattern)
        
        if not middleware:
            logger.warning(f"Unknown pattern {pattern}, using default")
            middleware = self.middlewares[self.default_pattern]
        
        return await middleware.inject_memories(prompt, context)
    
    async def get_context(
        self,
        query: Optional[str] = None,
        pattern: Optional[InjectionPattern] = None
    ) -> MemoryContext:
        """
        Get memory context for a pattern.
        
        Args:
            query: Optional query for relevance
            pattern: Pattern to use for context retrieval
            
        Returns:
            Memory context
        """
        pattern = pattern or self.default_pattern
        middleware = self.middlewares.get(pattern)
        
        if not middleware:
            middleware = self.middlewares[self.default_pattern]
        
        return await middleware.get_memory_context(query)
    
    async def store(self, data: Dict[str, Any]) -> bool:
        """
        Store data in memory.
        
        Args:
            data: Data to store
            
        Returns:
            Success status
        """
        # Use default pattern middleware for storage
        middleware = self.middlewares[self.default_pattern]
        return await middleware.store_interaction(data)


class ConversationalInjector(MemoryInjector):
    """Specialized injector for conversational CIs."""
    
    def __init__(self, ci_name: str):
        super().__init__(ci_name, InjectionPattern.CONVERSATION)
    
    async def inject_for_response(self, message: str, user: str) -> str:
        """
        Inject memory for generating a response.
        
        Args:
            message: User message
            user: User identifier
            
        Returns:
            Enriched prompt
        """
        # Add user context
        enriched = f"User {user} says: {message}"
        return await self.inject(enriched)


class AnalyticalInjector(MemoryInjector):
    """Specialized injector for analytical CIs."""
    
    def __init__(self, ci_name: str):
        super().__init__(ci_name, InjectionPattern.ANALYSIS)
    
    async def inject_for_analysis(self, data: Dict, analysis_type: str) -> str:
        """
        Inject memory for analysis tasks.
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis
            
        Returns:
            Enriched analysis prompt
        """
        prompt = f"Analyze {analysis_type}: {data}"
        return await self.inject(prompt)


class CoordinationInjector(MemoryInjector):
    """Specialized injector for coordination tasks."""
    
    def __init__(self, ci_name: str):
        super().__init__(ci_name, InjectionPattern.COORDINATION)
    
    async def inject_for_coordination(self, task: str, participants: List[str]) -> str:
        """
        Inject memory for multi-CI coordination.
        
        Args:
            task: Coordination task
            participants: List of participating CIs
            
        Returns:
            Enriched coordination prompt
        """
        prompt = f"Coordinate task '{task}' with {', '.join(participants)}"
        return await self.inject(prompt)


# Injection utilities

async def inject_conversational_memory(prompt: str, ci_name: str) -> str:
    """Quick injection for conversational context."""
    injector = ConversationalInjector(ci_name)
    return await injector.inject(prompt)


async def inject_analytical_memory(prompt: str, ci_name: str) -> str:
    """Quick injection for analytical context."""
    injector = AnalyticalInjector(ci_name)
    return await injector.inject(prompt)


async def inject_coordination_memory(prompt: str, ci_name: str, participants: List[str]) -> str:
    """Quick injection for coordination context."""
    injector = CoordinationInjector(ci_name)
    return await injector.inject_for_coordination(prompt, participants)


# Pattern selection helpers

def select_pattern_for_task(task_type: str) -> InjectionPattern:
    """
    Select appropriate injection pattern based on task type.
    
    Args:
        task_type: Type of task being performed
        
    Returns:
        Recommended injection pattern
    """
    task_patterns = {
        'chat': InjectionPattern.CONVERSATION,
        'message': InjectionPattern.CONVERSATION,
        'analyze': InjectionPattern.ANALYSIS,
        'research': InjectionPattern.ANALYSIS,
        'create': InjectionPattern.CREATIVE,
        'generate': InjectionPattern.CREATIVE,
        'debug': InjectionPattern.TECHNICAL,
        'fix': InjectionPattern.TECHNICAL,
        'coordinate': InjectionPattern.COORDINATION,
        'team': InjectionPattern.COORDINATION,
        'learn': InjectionPattern.LEARNING,
        'adapt': InjectionPattern.LEARNING
    }
    
    task_lower = task_type.lower()
    for keyword, pattern in task_patterns.items():
        if keyword in task_lower:
            return pattern
    
    return InjectionPattern.CONVERSATION


def create_custom_injector(
    ci_name: str,
    style: InjectionStyle,
    tiers: List[MemoryTier],
    **kwargs
) -> MemoryInjector:
    """
    Create a custom memory injector with specific configuration.
    
    Args:
        ci_name: CI name
        style: Injection style
        tiers: Memory tiers to use
        kwargs: Additional configuration
        
    Returns:
        Configured MemoryInjector
    """
    # Create custom pattern config
    custom_config = PatternConfig(
        pattern=InjectionPattern.CONVERSATION,  # Base pattern
        style=style,
        tiers=tiers,
        context_depth=kwargs.get('context_depth', 10),
        relevance_threshold=kwargs.get('relevance_threshold', 0.7),
        enable_collective=kwargs.get('enable_collective', False)
    )
    
    # Create injector with custom config
    injector = MemoryInjector(ci_name)
    
    # Override default pattern config
    middleware_config = MemoryConfig(
        namespace=ci_name,
        injection_style=custom_config.style,
        memory_tiers=custom_config.tiers,
        context_depth=custom_config.context_depth,
        relevance_threshold=custom_config.relevance_threshold,
        enable_collective=custom_config.enable_collective
    )
    injector.middlewares[injector.default_pattern] = MemoryMiddleware(middleware_config)
    
    return injector


# Batch injection for multiple prompts

async def inject_batch(
    prompts: List[str],
    ci_name: str,
    pattern: InjectionPattern = InjectionPattern.CONVERSATION
) -> List[str]:
    """
    Inject memory into multiple prompts.
    
    Args:
        prompts: List of prompts
        ci_name: CI name
        pattern: Injection pattern
        
    Returns:
        List of enriched prompts
    """
    injector = MemoryInjector(ci_name, pattern)
    
    # Get context once for efficiency
    context = await injector.get_context()
    
    # Inject into all prompts
    enriched = []
    for prompt in prompts:
        enriched.append(await injector.inject(prompt, pattern, context))
    
    return enriched