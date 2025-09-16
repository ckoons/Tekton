"""
Standardized Memory Middleware for Tekton CIs
Provides automatic memory injection and storage capabilities for all CIs.
Based on Rhetor's proven memory injection patterns.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sys

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        performance_boundary,
        state_checkpoint,
        with_memory,
        memory_aware
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
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator
    def with_memory(**kwargs):
        def decorator(func):
            return func
        return decorator
    def memory_aware(**kwargs):
        def decorator(func):
            return func
        return decorator

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class InjectionStyle(Enum):
    """Memory injection formatting styles."""
    NATURAL = "natural"        # Conversational, flowing narrative
    STRUCTURED = "structured"  # Clear sections and headers
    MINIMAL = "minimal"       # Just key facts
    TECHNICAL = "technical"   # Detailed technical context
    CREATIVE = "creative"     # Associative and inspirational


class MemoryTier(Enum):
    """Memory retrieval tiers."""
    RECENT = "recent"          # Last 5-10 interactions
    SESSION = "session"        # Current session context
    DOMAIN = "domain"         # Domain-specific knowledge
    ASSOCIATIONS = "associations"  # Vector similarity matches
    COLLECTIVE = "collective"  # Shared CI family memories


@dataclass
class MemoryConfig:
    """Configuration for memory middleware."""
    namespace: str
    enabled: bool = False  # DISABLED by default - must opt-in
    injection_style: InjectionStyle = InjectionStyle.MINIMAL  # Minimal by default
    memory_tiers: List[MemoryTier] = field(default_factory=lambda: [
        MemoryTier.RECENT,  # Only recent by default
    ])
    store_inputs: bool = False  # Don't store by default
    store_outputs: bool = False  # Don't store by default
    inject_context: bool = False  # Don't inject by default
    context_depth: int = 3  # Very limited context
    relevance_threshold: float = 0.9  # High threshold
    max_context_size: int = 500  # Small context
    enable_collective: bool = False
    performance_sla_ms: int = 50  # Tight SLA


@dataclass
class MemoryContext:
    """Container for memory context across tiers."""
    recent: List[Dict] = field(default_factory=list)
    session: List[Dict] = field(default_factory=list)
    domain: List[Dict] = field(default_factory=list)
    associations: List[Dict] = field(default_factory=list)
    collective: List[Dict] = field(default_factory=list)
    
    def is_empty(self) -> bool:
        """Check if all memory tiers are empty."""
        return not any([
            self.recent,
            self.session,
            self.domain,
            self.associations,
            self.collective
        ])
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'recent': self.recent,
            'session': self.session,
            'domain': self.domain,
            'associations': self.associations,
            'collective': self.collective
        }
    
    def total_items(self) -> int:
        """Count total memory items across all tiers."""
        return (
            len(self.recent) +
            len(self.session) +
            len(self.domain) +
            len(self.associations) +
            len(self.collective)
        )


@architecture_decision(
    title="Standardized Memory Middleware",
    description="Universal memory injection and storage for all Tekton CIs",
    rationale="Standardizes Rhetor's proven memory patterns for universal use",
    alternatives_considered=["CI-specific implementations", "Manual memory handling"],
    impacts=["ci_memory_consistency", "development_velocity", "memory_effectiveness"],
    decided_by="Casey",
    decision_date="2025-01-20"
)
class MemoryMiddleware:
    """
    Standardized memory middleware for automatic memory handling.
    
    Features:
    - Automatic memory context injection
    - Configurable memory tiers
    - Multiple injection styles
    - Performance optimized
    - Graceful degradation
    """
    
    def __init__(self, config: MemoryConfig):
        """Initialize memory middleware with configuration."""
        self.config = config
        self.memory_manager = None
        self._init_memory_manager()
        
        # Add memory limiter to prevent excessive memory usage
        from .memory_limiter import get_memory_limiter
        self.limiter = get_memory_limiter(config.namespace)
        
    def _init_memory_manager(self):
        """Initialize the memory manager."""
        try:
            from Engram.engram.core.memory_manager import MemoryManager
            self.memory_manager = MemoryManager(namespace=self.config.namespace)
            logger.info(f"Memory manager initialized for {self.config.namespace}")
        except ImportError:
            logger.warning(f"Engram not available, memory features disabled for {self.config.namespace}")
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
    
    @performance_boundary(
        title="Memory Context Retrieval",
        description="Gather memory context within performance SLA",
        sla="<200ms for all tiers",
        optimization_notes="Parallel retrieval with early termination on timeout"
    )
    async def get_memory_context(self, query: Optional[str] = None) -> MemoryContext:
        """
        Retrieve memory context across configured tiers.
        
        Args:
            query: Optional query for relevance filtering
            
        Returns:
            MemoryContext with populated tiers
        """
        if not self.config.enabled or not self.memory_manager:
            return MemoryContext()
        
        context = MemoryContext()
        
        # Parallel retrieval with timeout
        tasks = []
        
        if MemoryTier.RECENT in self.config.memory_tiers:
            tasks.append(self._get_recent_memories())
        
        if MemoryTier.SESSION in self.config.memory_tiers:
            tasks.append(self._get_session_memories())
        
        if MemoryTier.DOMAIN in self.config.memory_tiers and query:
            tasks.append(self._get_domain_memories(query))
        
        if MemoryTier.ASSOCIATIONS in self.config.memory_tiers and query:
            tasks.append(self._get_associations(query))
        
        if MemoryTier.COLLECTIVE in self.config.memory_tiers and self.config.enable_collective:
            tasks.append(self._get_collective_memories(query))
        
        try:
            # Execute with timeout
            timeout = self.config.performance_sla_ms / 1000.0
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
            
            # Map results to context
            for i, tier in enumerate(self.config.memory_tiers):
                if i < len(results) and not isinstance(results[i], Exception):
                    if tier == MemoryTier.RECENT:
                        context.recent = results[i]
                    elif tier == MemoryTier.SESSION:
                        context.session = results[i]
                    elif tier == MemoryTier.DOMAIN:
                        context.domain = results[i]
                    elif tier == MemoryTier.ASSOCIATIONS:
                        context.associations = results[i]
                    elif tier == MemoryTier.COLLECTIVE:
                        context.collective = results[i]
                        
        except asyncio.TimeoutError:
            logger.warning(f"Memory retrieval timeout after {self.config.performance_sla_ms}ms")
        except Exception as e:
            logger.error(f"Memory retrieval error: {e}")
        
        return context
    
    async def _get_recent_memories(self) -> List[Dict]:
        """Retrieve recent interaction memories."""
        try:
            recent = await self.memory_manager.get_recent(
                limit=self.config.context_depth
            )
            return [{'type': 'recent', 'content': m} for m in recent]
        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return []
    
    async def _get_session_memories(self) -> List[Dict]:
        """Retrieve current session memories."""
        try:
            session = await self.memory_manager.get_session_context()
            return [{'type': 'session', 'content': m} for m in session]
        except Exception as e:
            logger.error(f"Failed to get session memories: {e}")
            return []
    
    async def _get_domain_memories(self, query: str) -> List[Dict]:
        """Retrieve domain-specific memories."""
        try:
            domain = await self.memory_manager.search_domain(
                query=query,
                limit=5,
                threshold=self.config.relevance_threshold
            )
            return [{'type': 'domain', 'content': m} for m in domain]
        except Exception as e:
            logger.error(f"Failed to get domain memories: {e}")
            return []
    
    async def _get_associations(self, query: str) -> List[Dict]:
        """Retrieve associative memories via vector similarity."""
        try:
            associations = await self.memory_manager.find_similar(
                query=query,
                limit=5,
                threshold=self.config.relevance_threshold
            )
            return [{'type': 'association', 'content': m} for m in associations]
        except Exception as e:
            logger.error(f"Failed to get associations: {e}")
            return []
    
    async def _get_collective_memories(self, query: Optional[str]) -> List[Dict]:
        """Retrieve collective CI family memories."""
        try:
            from shared.ai.family_memory import FamilyMemory
            family = FamilyMemory()
            collective = await family.get_relevant_wisdom(
                context=query or "",
                limit=3
            )
            return [{'type': 'collective', 'content': m} for m in collective]
        except Exception as e:
            logger.error(f"Failed to get collective memories: {e}")
            return []
    
    @integration_point(
        title="Memory Injection into Prompts",
        description="Inject memory context into CI prompts",
        target_component="CI",
        protocol="prompt_enrichment",
        data_flow="prompt -> inject_memories -> enriched_prompt"
    )
    async def inject_memories(self, prompt: str, context: Optional[MemoryContext] = None) -> str:
        """
        Inject memory context into a prompt.
        
        Args:
            prompt: Original prompt
            context: Pre-retrieved context or None to retrieve
            
        Returns:
            Enriched prompt with memory context
        """
        if not self.config.inject_context:
            return prompt
        
        # Get context if not provided
        if context is None:
            context = await self.get_memory_context(query=prompt)
        
        if context.is_empty():
            return prompt
        
        # Format based on injection style
        if self.config.injection_style == InjectionStyle.NATURAL:
            return self._inject_natural(prompt, context)
        elif self.config.injection_style == InjectionStyle.STRUCTURED:
            return self._inject_structured(prompt, context)
        elif self.config.injection_style == InjectionStyle.MINIMAL:
            return self._inject_minimal(prompt, context)
        elif self.config.injection_style == InjectionStyle.TECHNICAL:
            return self._inject_technical(prompt, context)
        elif self.config.injection_style == InjectionStyle.CREATIVE:
            return self._inject_creative(prompt, context)
        else:
            return prompt
    
    def _inject_natural(self, prompt: str, context: MemoryContext) -> str:
        """Natural conversational memory injection."""
        prefix = []
        
        if context.recent:
            prefix.append(f"Recently, we discussed: {self._summarize_memories(context.recent, 3)}")
        
        if context.session:
            prefix.append(f"In this session: {self._summarize_memories(context.session, 2)}")
        
        if context.domain:
            prefix.append(f"Relevant context: {self._summarize_memories(context.domain, 2)}")
        
        if context.associations:
            prefix.append(f"Related topics: {self._summarize_memories(context.associations, 2)}")
        
        if context.collective:
            prefix.append(f"Team insights: {self._summarize_memories(context.collective, 1)}")
        
        if prefix:
            return f"{' '.join(prefix)}\n\nCurrent request: {prompt}"
        return prompt
    
    def _inject_structured(self, prompt: str, context: MemoryContext) -> str:
        """Structured memory injection with clear sections."""
        sections = []
        
        if context.recent:
            sections.append(f"## Recent Context\n{self._format_memories(context.recent)}")
        
        if context.session:
            sections.append(f"## Session History\n{self._format_memories(context.session)}")
        
        if context.domain:
            sections.append(f"## Domain Knowledge\n{self._format_memories(context.domain)}")
        
        if context.associations:
            sections.append(f"## Related Information\n{self._format_memories(context.associations)}")
        
        if context.collective:
            sections.append(f"## Collective Wisdom\n{self._format_memories(context.collective)}")
        
        if sections:
            return f"{chr(10).join(sections)}\n\n## Current Request\n{prompt}"
        return prompt
    
    def _inject_minimal(self, prompt: str, context: MemoryContext) -> str:
        """Minimal memory injection with just key facts."""
        facts = []
        
        # Extract most relevant from each tier
        for memories in [context.recent[:2], context.domain[:1], context.associations[:1]]:
            for mem in memories:
                if 'content' in mem:
                    facts.append(self._extract_key_fact(mem['content']))
        
        if facts:
            return f"Context: {'; '.join(facts)}\n\n{prompt}"
        return prompt
    
    def _inject_technical(self, prompt: str, context: MemoryContext) -> str:
        """Technical memory injection with detailed metadata."""
        sections = []
        
        for tier_name, memories in [
            ('RECENT', context.recent),
            ('SESSION', context.session),
            ('DOMAIN', context.domain),
            ('ASSOCIATIONS', context.associations),
            ('COLLECTIVE', context.collective)
        ]:
            if memories:
                sections.append(f"[{tier_name}]")
                for mem in memories:
                    sections.append(f"  - {self._format_technical(mem)}")
        
        if sections:
            return f"MEMORY_CONTEXT:\n{chr(10).join(sections)}\n\nREQUEST:\n{prompt}"
        return prompt
    
    def _inject_creative(self, prompt: str, context: MemoryContext) -> str:
        """Creative memory injection with associative connections."""
        narrative = []
        
        if context.associations:
            narrative.append(f"This reminds me of: {self._create_associations(context.associations)}")
        
        if context.collective:
            narrative.append(f"The team has learned: {self._summarize_memories(context.collective, 2)}")
        
        if context.domain:
            narrative.append(f"Drawing from experience: {self._summarize_memories(context.domain, 2)}")
        
        if narrative:
            return f"{' '.join(narrative)}\n\nConsidering your request: {prompt}"
        return prompt
    
    def _summarize_memories(self, memories: List[Dict], limit: int) -> str:
        """Summarize memories into a brief statement."""
        summaries = []
        for mem in memories[:limit]:
            if 'content' in mem:
                content = mem['content']
                if isinstance(content, dict):
                    summaries.append(content.get('summary', str(content)))
                else:
                    summaries.append(str(content)[:100])
        return ', '.join(summaries)
    
    def _format_memories(self, memories: List[Dict]) -> str:
        """Format memories for structured output."""
        formatted = []
        for mem in memories:
            if 'content' in mem:
                formatted.append(f"- {mem['content']}")
        return '\n'.join(formatted)
    
    def _extract_key_fact(self, memory: Any) -> str:
        """Extract a key fact from a memory."""
        if isinstance(memory, dict):
            return memory.get('fact', memory.get('summary', str(memory)))[:50]
        return str(memory)[:50]
    
    def _format_technical(self, memory: Dict) -> str:
        """Format memory with technical details."""
        mem_type = memory.get('type', 'unknown')
        content = memory.get('content', {})
        if isinstance(content, dict):
            return f"[{mem_type}] {content.get('id', 'N/A')}: {content.get('data', content)}"
        return f"[{mem_type}] {content}"
    
    def _create_associations(self, memories: List[Dict]) -> str:
        """Create associative narrative from memories."""
        associations = []
        for mem in memories[:3]:
            if 'content' in mem:
                associations.append(str(mem['content'])[:75])
        return ' ... '.join(associations)
    
    @with_memory(
        namespace="middleware",
        store_outputs=True
    )
    async def store_interaction(self, interaction: Dict[str, Any]) -> bool:
        """
        Store an interaction in memory.
        
        Args:
            interaction: Interaction data to store
            
        Returns:
            Success status
        """
        if not self.config.store_inputs or not self.memory_manager:
            return False
        
        try:
            await self.memory_manager.store(interaction)
            return True
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return False
    
    async def process_with_memory(self, func, *args, **kwargs):
        """
        Process a function with automatic memory handling.
        
        Args:
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            
        Returns:
            Function result with memory handling
        """
        # Get memory context
        context = None
        if self.config.inject_context:
            # Extract query from args if available
            query = args[0] if args and isinstance(args[0], str) else None
            context = await self.get_memory_context(query)
        
        # Store input if configured
        if self.config.store_inputs:
            await self.store_interaction({
                'type': 'input',
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs
            })
        
        # Add context to kwargs if function expects it
        if context and 'memory_context' in func.__code__.co_varnames:
            kwargs['memory_context'] = context
        
        # Execute function
        result = await func(*args, **kwargs)
        
        # Store output if configured
        if self.config.store_outputs:
            await self.store_interaction({
                'type': 'output',
                'function': func.__name__,
                'result': result
            })
        
        return result


# Convenience functions for quick setup

def create_memory_middleware(ci_name: str, **config_overrides) -> MemoryMiddleware:
    """
    Create a memory middleware instance with defaults.
    
    Args:
        ci_name: Name of the CI
        config_overrides: Optional config overrides
        
    Returns:
        Configured MemoryMiddleware instance
    """
    config = MemoryConfig(namespace=ci_name, **config_overrides)
    return MemoryMiddleware(config)


async def inject_memory_context(prompt: str, ci_name: str, style: InjectionStyle = InjectionStyle.NATURAL) -> str:
    """
    Quick function to inject memory into a prompt.
    
    Args:
        prompt: Original prompt
        ci_name: CI name for namespace
        style: Injection style
        
    Returns:
        Enriched prompt
    """
    middleware = create_memory_middleware(ci_name, injection_style=style)
    return await middleware.inject_memories(prompt)