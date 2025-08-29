"""
Memory Hooks Specification
Defines the hook interface for catalog-based memory system.
"""

from typing import Dict, List, Any, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
import asyncio


class MemoryTier(Enum):
    """Memory tier classification."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    LATENT = "latent"


@dataclass
class MemoryCatalogEntry:
    """Single entry in the memory catalog."""
    memory_id: str
    timestamp: float
    ci_name: str
    memory_type: str  # solution, decision, pattern, interaction
    summary: str  # 50 char max
    abstract: str  # 200 char max
    keywords: List[str]
    relevance_score: float  # 0.0 to 1.0
    token_size: int
    tier: MemoryTier
    metadata: Dict[str, Any]  # Additional metadata
    
    def to_catalog_entry(self) -> Dict:
        """Convert to catalog dictionary for CI consumption."""
        return {
            "id": self.memory_id,
            "summary": self.summary,
            "keywords": self.keywords,
            "relevance": self.relevance_score,
            "size": self.token_size,
            "tier": self.tier.value
        }


@dataclass
class MemoryCatalog:
    """Memory catalog presented to CIs."""
    ci_name: str
    prompt_context: Dict[str, Any]
    token_budget: int
    entries: List[MemoryCatalogEntry]
    recommendations: List[str]  # Recommended memory IDs
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CI consumption."""
        return {
            "token_budget": self.token_budget,
            "catalog": [entry.to_catalog_entry() for entry in self.entries],
            "recommendations": self.recommendations,
            "total_entries": len(self.entries)
        }


@dataclass
class MemoryRequest:
    """Request for specific memories from catalog."""
    ci_name: str
    memory_ids: List[str]
    max_tokens: Optional[int] = None
    format_style: str = "natural"  # natural, structured, minimal
    

@dataclass
class MemoryResponse:
    """Response containing requested memories."""
    memories: List[Dict[str, Any]]
    total_tokens: int
    format_style: str
    truncated: bool = False


class MemoryHookProtocol(Protocol):
    """Protocol defining memory hook interface."""
    
    async def pre_prompt_hook(
        self, 
        ci_name: str, 
        prompt: str, 
        context: Dict[str, Any]
    ) -> MemoryCatalog:
        """
        Called before CI processes prompt.
        
        Args:
            ci_name: Name of the CI
            prompt: The prompt to be processed
            context: Additional context (project, session, etc.)
            
        Returns:
            MemoryCatalog with available memories
        """
        ...
    
    async def memory_request_hook(
        self,
        request: MemoryRequest
    ) -> MemoryResponse:
        """
        CI requests specific memories from catalog.
        
        Args:
            request: Memory request with IDs and preferences
            
        Returns:
            MemoryResponse with formatted memories
        """
        ...
    
    async def post_response_hook(
        self,
        ci_name: str,
        response: str,
        memories_used: List[str],
        feedback: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Called after CI generates response.
        
        Args:
            ci_name: Name of the CI
            response: Generated response
            memories_used: IDs of memories that were used
            feedback: Optional feedback on memory usefulness
        """
        ...
    
    async def memory_creation_hook(
        self,
        ci_name: str,
        content: str,
        memory_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        CI creates a new memory.
        
        Args:
            ci_name: Name of the CI creating the memory
            content: Memory content
            memory_type: Type of memory (solution, pattern, etc.)
            metadata: Additional metadata
            
        Returns:
            Created memory ID
        """
        ...


class MemoryHookAdapter:
    """
    Adapter implementing the memory hook protocol.
    This is what gets integrated into CI handlers.
    """
    
    def __init__(self, apollo_curator=None, rhetor_optimizer=None):
        """
        Initialize hook adapter.
        
        Args:
            apollo_curator: Apollo memory curator instance
            rhetor_optimizer: Rhetor token optimizer instance
        """
        self.apollo = apollo_curator
        self.rhetor = rhetor_optimizer
        self._catalog_cache = {}
        
    async def pre_prompt_hook(
        self, 
        ci_name: str, 
        prompt: str, 
        context: Dict[str, Any]
    ) -> MemoryCatalog:
        """Generate memory catalog for CI."""
        # Apollo analyzes prompt and creates catalog
        if self.apollo:
            catalog_entries = await self.apollo.create_catalog(ci_name, prompt, context)
            recommendations = await self.apollo.recommend_memories(catalog_entries, prompt)
        else:
            catalog_entries = []
            recommendations = []
        
        # Rhetor determines token budget
        if self.rhetor:
            token_budget = self.rhetor.calculate_budget(ci_name, len(prompt))
        else:
            token_budget = 2000  # Default budget
        
        catalog = MemoryCatalog(
            ci_name=ci_name,
            prompt_context=context,
            token_budget=token_budget,
            entries=catalog_entries,
            recommendations=recommendations
        )
        
        # Cache for potential request
        self._catalog_cache[ci_name] = catalog
        
        return catalog
    
    async def memory_request_hook(
        self,
        request: MemoryRequest
    ) -> MemoryResponse:
        """Handle memory request from CI."""
        # Check token budget with Rhetor
        if self.rhetor:
            memory_ids = await self.rhetor.prioritize_memories(
                request.ci_name,
                request.memory_ids,
                request.max_tokens
            )
        else:
            memory_ids = request.memory_ids
        
        # Retrieve memories from Apollo
        if self.apollo:
            memories = await self.apollo.retrieve_memories(memory_ids)
        else:
            memories = []
        
        # Format with Rhetor
        if self.rhetor:
            formatted = await self.rhetor.format_memories(
                memories,
                request.format_style,
                request.max_tokens
            )
            total_tokens = self.rhetor.count_tokens(formatted)
            truncated = len(memories) > len(formatted)
        else:
            formatted = memories
            total_tokens = sum(len(str(m)) for m in memories) // 4  # Rough estimate
            truncated = False
        
        return MemoryResponse(
            memories=formatted,
            total_tokens=total_tokens,
            format_style=request.format_style,
            truncated=truncated
        )
    
    async def post_response_hook(
        self,
        ci_name: str,
        response: str,
        memories_used: List[str],
        feedback: Optional[Dict[str, Any]] = None
    ) -> None:
        """Process post-response feedback."""
        # Apollo learns from usage
        if self.apollo:
            await self.apollo.update_relevance(
                ci_name,
                memories_used,
                response,
                feedback
            )
        
        # Rhetor tracks token usage
        if self.rhetor:
            await self.rhetor.track_usage(
                ci_name,
                memories_used,
                len(response)
            )
        
        # Clear catalog cache
        self._catalog_cache.pop(ci_name, None)
    
    async def memory_creation_hook(
        self,
        ci_name: str,
        content: str,
        memory_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Handle memory creation."""
        if self.apollo:
            return await self.apollo.create_memory(
                ci_name,
                content,
                memory_type,
                metadata
            )
        return ""


# Example CI integration
class MemoryEnabledCIHandler:
    """
    Example of how a CI handler integrates with memory hooks.
    This treats the CI as a black box with hooks at the edges.
    """
    
    def __init__(self, name: str, memory_hooks: MemoryHookAdapter):
        self.name = name
        self.memory_hooks = memory_hooks
        
    async def process_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Process prompt with memory catalog support.
        
        This demonstrates the black box approach:
        1. Get catalog (lightweight)
        2. CI decides what it needs
        3. Request specific memories
        4. Process with memories
        5. Report usage
        """
        # 1. Get memory catalog
        catalog = await self.memory_hooks.pre_prompt_hook(
            self.name,
            prompt,
            context
        )
        
        # 2. CI autonomously decides what memories it needs
        needed_memory_ids = self._select_memories_from_catalog(
            catalog,
            prompt,
            context
        )
        
        # 3. Request specific memories if needed
        enriched_prompt = prompt
        memories_used = []
        
        if needed_memory_ids:
            request = MemoryRequest(
                ci_name=self.name,
                memory_ids=needed_memory_ids,
                max_tokens=catalog.token_budget,
                format_style="natural"
            )
            
            response = await self.memory_hooks.memory_request_hook(request)
            
            # Enrich prompt with memories
            if response.memories:
                enriched_prompt = self._enrich_prompt(prompt, response.memories)
                memories_used = needed_memory_ids
        
        # 4. Process normally (CI as black box)
        result = await self._generate_response(enriched_prompt)
        
        # 5. Report usage for learning
        await self.memory_hooks.post_response_hook(
            self.name,
            result,
            memories_used
        )
        
        return result
    
    def _select_memories_from_catalog(
        self,
        catalog: MemoryCatalog,
        prompt: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        CI-specific logic for selecting memories.
        This is where each CI's personality shines through.
        """
        # Start with recommendations
        selected = catalog.recommendations[:3]
        
        # Add high-relevance entries within budget
        remaining_budget = catalog.token_budget
        for entry in catalog.entries:
            if entry.memory_id not in selected:
                if entry.relevance_score > 0.7 and entry.token_size < remaining_budget:
                    selected.append(entry.memory_id)
                    remaining_budget -= entry.token_size
        
        return selected
    
    def _enrich_prompt(self, prompt: str, memories: List[Dict]) -> str:
        """Add memories to prompt."""
        if not memories:
            return prompt
        
        memory_context = "\n".join([
            f"[Memory {i+1}]: {m.get('content', '')}"
            for i, m in enumerate(memories)
        ])
        
        return f"{memory_context}\n\nCurrent request: {prompt}"
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response (placeholder for actual CI logic)."""
        # This is where the actual CI model generates a response
        return f"Response to: {prompt}"