"""
Memory Extractor for Post-Response Analysis
Extracts significant memories from CI responses for storage.
"""

import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import sys

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        performance_boundary,
        state_checkpoint,
        ci_orchestrated,
        fuzzy_match
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
    def fuzzy_match(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Imports should work without path manipulation
from Engram.engram.core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


@dataclass
class ExtractedMemory:
    """Represents an extracted memory with metadata."""
    content: str
    significance: float
    memory_type: str  # 'insight', 'learning', 'decision', 'emotion', 'pattern'
    privacy_level: str  # 'private', 'team', 'tribal'
    tags: List[str]
    context: Dict[str, Any]
    
    def to_engram_format(self, ci_name: str) -> Dict:
        """Convert to Engram storage format."""
        return {
            'content': self.content,
            'metadata': {
                'ci_name': ci_name,
                'significance': self.significance,
                'type': self.memory_type,
                'privacy': self.privacy_level,
                'tags': self.tags,
                'context': self.context,
                'timestamp': datetime.now().isoformat()
            }
        }


@architecture_decision(
    title="Memory Extraction Architecture",
    description="Pattern-based extraction of significant memories from CI responses",
    rationale="Captures insights, learnings, and patterns for long-term CI cognition",
    alternatives_considered=["Manual tagging", "Full response storage", "LLM-based extraction"],
    impacts=["memory_quality", "storage_efficiency", "ci_learning"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
@ci_orchestrated(
    title="Memory Extraction Pipeline",
    description="Analyzes CI responses for significant memories",
    orchestrator="memory_extractor",
    workflow=["pattern_detection", "significance_scoring", "privacy_classification", "storage"],
    ci_capabilities=["insight_detection", "learning_capture", "pattern_recognition"]
)
class MemoryExtractor:
    """
    Extracts significant memories from CI responses.
    
    Detection patterns:
    - Explicit memory markers ("I remember", "Worth noting")
    - Implicit significance (breakthroughs, decisions, emotions)
    - Pattern recognition (repeated concepts, solutions)
    - Cultural learnings (team wisdom, shared experiences)
    """
    
    # Memory marker patterns
    EXPLICIT_PATTERNS = {
        'memory': r"(?i)(I remember|I recall|This reminds me|As I mentioned)",
        'insight': r"(?i)(I (realize|understand|see)|It('s| is) clear that|The key is)",
        'learning': r"(?i)(I('ve)? learned|discovered|found out|understand now)",
        'decision': r"(?i)(I('ll| will)|We should|Let's|Decided to|Choosing)",
        'note': r"(?i)(Worth noting|Important:|For future reference|Keep in mind)"
    }
    
    # Significance indicators
    SIGNIFICANCE_PATTERNS = {
        'breakthrough': (r"(?i)(breakthrough|aha|eureka|finally|solved)", 0.9),
        'problem': (r"(?i)(issue|problem|bug|error|stuck)", 0.6),
        'solution': (r"(?i)(fixed|resolved|works now|solution)", 0.8),
        'emotion': (r"(?i)(frustrated|excited|confused|happy|satisfied)", 0.5),
        'pattern': (r"(?i)(pattern|always|usually|tends to|frequently)", 0.7)
    }
    
    def __init__(self, engram_client: Optional[MemoryManager] = None):
        self.engram = engram_client
        self.min_significance = 0.3  # Minimum significance to store
        self.extraction_queue = asyncio.Queue()
        
    @integration_point(
        title="Memory Extraction Entry",
        description="Analyzes CI responses for memory extraction",
        target_component="Engram Storage",
        protocol="async_extraction",
        data_flow="response → pattern_match → extraction → engram_storage",
        integration_date="2025-08-28"
    )
    @performance_boundary(
        title="Memory Extraction",
        description="Extract and store significant memories",
        sla="<100ms extraction, async storage",
        optimization_notes="Fire-and-forget storage, parallel pattern matching",
        measured_impact="No impact on response latency due to async"
    )
    async def extract_memories(
        self, 
        ci_name: str, 
        message: str, 
        response: str, 
        context: Dict[str, Any]
    ) -> List[ExtractedMemory]:
        """
        Main extraction method - analyzes response for memories.
        
        Args:
            ci_name: CI that generated the response
            message: Original message sent
            response: CI's response
            context: Additional context
            
        Returns:
            List of extracted memories
        """
        memories = []
        
        # Check for explicit memory markers
        explicit = self._extract_explicit_memories(response)
        memories.extend(explicit)
        
        # Check for implicit significance
        implicit = self._extract_implicit_memories(response, message)
        memories.extend(implicit)
        
        # Check for patterns and repetitions
        patterns = self._extract_patterns(response, context)
        memories.extend(patterns)
        
        # Deduplicate and filter by significance
        memories = self._filter_memories(memories)
        
        # Determine privacy levels based on content
        for memory in memories:
            memory.privacy_level = self._determine_privacy(memory, ci_name)
        
        # Store significant memories asynchronously
        if memories and self.engram:
            asyncio.create_task(self._store_memories(ci_name, memories))
        
        return memories
    
    @fuzzy_match(
        title="Explicit Memory Detection",
        description="Pattern matching for explicit memory markers",
        algorithm="regex_pattern_matching",
        examples=["I remember", "Worth noting", "I learned", "I realize"],
        priority="exact_match > case_insensitive > partial"
    )
    def _extract_explicit_memories(self, response: str) -> List[ExtractedMemory]:
        """Extract memories with explicit markers."""
        memories = []
        
        for memory_type, pattern in self.EXPLICIT_PATTERNS.items():
            matches = re.finditer(pattern, response)
            
            for match in matches:
                # Extract the sentence containing the match
                start = max(0, match.start() - 100)
                end = min(len(response), match.end() + 100)
                context_text = response[start:end]
                
                # Find sentence boundaries
                sentence = self._extract_sentence(context_text, match.start() - start)
                
                if sentence and len(sentence) > 20:  # Min length filter
                    memory = ExtractedMemory(
                        content=sentence,
                        significance=0.7,  # Explicit memories are significant
                        memory_type=memory_type,
                        privacy_level='team',  # Default
                        tags=[memory_type],
                        context={'marker': match.group()}
                    )
                    memories.append(memory)
        
        return memories
    
    def _extract_implicit_memories(self, response: str, message: str) -> List[ExtractedMemory]:
        """Extract memories based on implicit significance."""
        memories = []
        
        for sig_type, (pattern, base_significance) in self.SIGNIFICANCE_PATTERNS.items():
            matches = re.finditer(pattern, response)
            
            for match in matches:
                sentence = self._extract_sentence(response, match.start())
                
                if sentence and len(sentence) > 20:
                    # Adjust significance based on context
                    significance = self._calculate_significance(
                        sentence, message, base_significance
                    )
                    
                    if significance >= self.min_significance:
                        memory = ExtractedMemory(
                            content=sentence,
                            significance=significance,
                            memory_type=sig_type,
                            privacy_level='team',
                            tags=[sig_type],
                            context={'trigger': match.group()}
                        )
                        memories.append(memory)
        
        return memories
    
    def _extract_patterns(self, response: str, context: Dict) -> List[ExtractedMemory]:
        """Extract pattern-based memories."""
        memories = []
        
        # Look for code patterns
        code_blocks = re.findall(r'```[\s\S]*?```', response)
        for code in code_blocks:
            if 'def ' in code or 'class ' in code or 'function ' in code:
                memory = ExtractedMemory(
                    content=f"Code solution: {code[:200]}...",
                    significance=0.6,
                    memory_type='pattern',
                    privacy_level='team',
                    tags=['code', 'solution'],
                    context={'type': 'code_pattern'}
                )
                memories.append(memory)
        
        # Look for repeated concepts (mentioned 3+ times)
        words = re.findall(r'\b[A-Z][a-z]+\b|\b\w{5,}\b', response)
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        
        for word, count in word_counts.items():
            if count >= 3 and word not in ['the', 'and', 'that', 'this', 'with']:
                memory = ExtractedMemory(
                    content=f"Focus concept: {word} (mentioned {count} times)",
                    significance=0.4,
                    memory_type='pattern',
                    privacy_level='team',
                    tags=['concept', word],
                    context={'frequency': count}
                )
                memories.append(memory)
                break  # Just one concept memory
        
        return memories
    
    def _extract_sentence(self, text: str, position: int) -> str:
        """Extract the complete sentence containing the position."""
        # Find sentence boundaries
        sentences = re.split(r'[.!?]\s+', text)
        
        current_pos = 0
        for sentence in sentences:
            if current_pos <= position < current_pos + len(sentence):
                return sentence.strip()
            current_pos += len(sentence) + 2  # Account for delimiter
        
        return ""
    
    @fuzzy_match(
        title="Significance Calculation",
        description="Contextual scoring of memory significance",
        algorithm="weighted_feature_scoring",
        examples=["breakthrough=0.9", "solution=0.8", "pattern=0.7"],
        priority="breakthrough > solution > insight > pattern"
    )
    def _calculate_significance(self, sentence: str, original_message: str, base_sig: float) -> float:
        """Calculate adjusted significance based on context."""
        significance = base_sig
        
        # Boost if response directly addresses the question
        if any(word in sentence.lower() for word in original_message.lower().split()[:5]):
            significance *= 1.2
        
        # Boost for longer, more detailed responses
        if len(sentence) > 100:
            significance *= 1.1
        
        # Boost for definitiveness
        if any(word in sentence.lower() for word in ['definitely', 'absolutely', 'critical', 'essential']):
            significance *= 1.15
        
        return min(1.0, significance)  # Cap at 1.0
    
    @state_checkpoint(
        title="Privacy Classification",
        description="Determines memory privacy levels for compartmentalization",
        state_type="classification",
        persistence=False,
        consistency_requirements="Consistent privacy rules",
        recovery_strategy="Default to team level"
    )
    def _determine_privacy(self, memory: ExtractedMemory, ci_name: str) -> str:
        """Determine appropriate privacy level for memory."""
        content_lower = memory.content.lower()
        
        # Private memories
        if any(term in content_lower for term in ['personal', 'private', 'casey', 'kai']):
            return 'private'
        
        # Tribal memories (shared wisdom)
        if any(term in content_lower for term in ['we should', 'team', 'always', 'best practice']):
            return 'tribal'
        
        # Default to team level
        return 'team'
    
    def _filter_memories(self, memories: List[ExtractedMemory]) -> List[ExtractedMemory]:
        """Filter and deduplicate memories."""
        if not memories:
            return []
        
        # Sort by significance
        memories.sort(key=lambda m: m.significance, reverse=True)
        
        # Deduplicate similar content
        filtered = []
        seen_content = set()
        
        for memory in memories:
            # Simple dedup - could be enhanced with similarity scoring
            content_key = memory.content[:50].lower()
            if content_key not in seen_content and memory.significance >= self.min_significance:
                filtered.append(memory)
                seen_content.add(content_key)
        
        return filtered[:5]  # Limit to top 5 memories per response
    
    @integration_point(
        title="Engram Storage Integration",
        description="Persists extracted memories to Engram system",
        target_component="Engram",
        protocol="async_storage",
        data_flow="extracted_memory → compartment_routing → engram_storage",
        integration_date="2025-08-28"
    )
    async def _store_memories(self, ci_name: str, memories: List[ExtractedMemory]):
        """Store extracted memories in Engram."""
        if not self.engram:
            return
        
        for memory in memories:
            try:
                # Determine compartment based on privacy
                compartment = {
                    'private': 'personal',
                    'team': 'projects',
                    'tribal': 'longterm'
                }.get(memory.privacy_level, 'session')
                
                # Store in Engram
                await self.engram.add_memory(
                    client_id=ci_name,
                    content=memory.content,
                    metadata=memory.to_engram_format(ci_name),
                    compartment=compartment
                )
                
                logger.info(f"Stored {memory.memory_type} memory for {ci_name}")
                
            except Exception as e:
                logger.error(f"Failed to store memory: {e}")
    
    def set_min_significance(self, threshold: float):
        """Set minimum significance threshold for storage."""
        self.min_significance = max(0.0, min(1.0, threshold))