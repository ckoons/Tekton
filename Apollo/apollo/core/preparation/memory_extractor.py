"""
Apollo Memory Extractor
Extracts insights, decisions, and key information from CI exchanges
Creates memory landmarks for the knowledge graph
Part of Apollo's Preparation service
"""

import re
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Import memory types from context_brief
from .context_brief import (
    MemoryItem, MemoryType, CIType, ContextBriefManager
)


class ExtractionPattern:
    """Pattern definitions for extracting different types of memories"""
    
    DECISION_PATTERNS = [
        r"(?i)(decided|chose|selected|will use|going with|opted for)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(the decision is|we'll go with|let's use)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(switching to|migrating to|adopting)\s+(.+?)(?:\.|,|;|$)"
    ]
    
    INSIGHT_PATTERNS = [
        r"(?i)(learned|discovered|realized|found that|noticed)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(turns out|it seems|apparently|interestingly)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(the issue was|the problem is|the cause is)\s+(.+?)(?:\.|,|;|$)"
    ]
    
    ERROR_PATTERNS = [
        r"(?i)(error|exception|failure|crash|bug)(?:\s+in)?\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(failed to|couldn't|unable to)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(broken|not working|malfunctioning)\s+(.+?)(?:\.|,|;|$)"
    ]
    
    PLAN_PATTERNS = [
        r"(?i)(will|plan to|going to|need to|should)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(next step|todo|task)(?:\s+is)?\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(implement|create|build|develop)\s+(.+?)(?:\.|,|;|$)"
    ]
    
    CONTEXT_PATTERNS = [
        r"(?i)(user prefers|casey mentioned|requirement is)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(configured|set up|initialized)\s+(.+?)(?:\.|,|;|$)",
        r"(?i)(using|working with|based on)\s+(.+?)(?:\.|,|;|$)"
    ]


class MemoryExtractor:
    """
    Extracts memories from CI exchanges
    Works as a black box observer of message flow
    """
    
    def __init__(self, catalog: Optional[ContextBriefManager] = None):
        """
        Initialize the memory extractor
        
        Args:
            catalog: Optional ContextBriefManager instance to use
        """
        self.catalog = catalog or ContextBriefManager()
        self.patterns = ExtractionPattern()
        
        # Minimum content length to consider
        self.min_content_length = 20
        
        # Maximum summary length
        self.max_summary_length = 50
        
        logger.info("Memory extractor initialized")
    
    def extract_from_exchange(self, ci_name: str, user_message: str, 
                             ci_response: str) -> List[MemoryItem]:
        """
        Extract memories from a user-CI exchange
        
        Args:
            ci_name: Name of the CI
            user_message: User's input message
            ci_response: CI's response
            
        Returns:
            List of extracted memory items
        """
        memories = []
        
        # Extract from CI response (primary source)
        if ci_response:
            memories.extend(self._extract_from_text(ci_name, ci_response))
        
        # Extract context from user message
        if user_message:
            context_memories = self._extract_context(ci_name, user_message)
            memories.extend(context_memories)
        
        # Deduplicate similar memories
        memories = self._deduplicate_memories(memories)
        
        # Auto-tag memories
        for memory in memories:
            memory.relevance_tags = self._extract_tags(memory.content)
        
        logger.info(f"Extracted {len(memories)} memories from {ci_name} exchange")
        return memories
    
    def _extract_from_text(self, ci_name: str, text: str) -> List[MemoryItem]:
        """Extract memories from text using pattern matching"""
        memories = []
        
        # Check each memory type
        type_patterns = [
            (MemoryType.DECISION, self.patterns.DECISION_PATTERNS),
            (MemoryType.INSIGHT, self.patterns.INSIGHT_PATTERNS),
            (MemoryType.ERROR, self.patterns.ERROR_PATTERNS),
            (MemoryType.PLAN, self.patterns.PLAN_PATTERNS),
        ]
        
        for memory_type, patterns in type_patterns:
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.MULTILINE)
                for match in matches:
                    content = match.group(0)
                    if len(content) >= self.min_content_length:
                        memory = self._create_memory(
                            ci_name=ci_name,
                            memory_type=memory_type,
                            content=content,
                            priority=self._calculate_priority(memory_type, content)
                        )
                        memories.append(memory)
        
        return memories
    
    def _extract_context(self, ci_name: str, user_message: str) -> List[MemoryItem]:
        """Extract contextual information from user messages"""
        memories = []
        
        for pattern in self.patterns.CONTEXT_PATTERNS:
            matches = re.finditer(pattern, user_message, re.MULTILINE)
            for match in matches:
                content = match.group(0)
                if len(content) >= self.min_content_length:
                    memory = self._create_memory(
                        ci_name=ci_name,
                        memory_type=MemoryType.CONTEXT,
                        content=content,
                        priority=5  # Standard priority for context
                    )
                    memories.append(memory)
        
        return memories
    
    def _create_memory(self, ci_name: str, memory_type: MemoryType,
                      content: str, priority: int = 5) -> MemoryItem:
        """Create a memory item from extracted content"""
        # Generate summary
        summary = self._generate_summary(content)
        
        # Detect CI type
        ci_type = self._detect_ci_type(ci_name)
        
        # Calculate expiration (longer for high priority)
        expires_days = 14 if priority >= 7 else 7
        expires = datetime.now() + timedelta(days=expires_days)
        
        # Generate unique ID
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        return MemoryItem(
            id=memory_id,
            timestamp=datetime.now(),
            ci_source=ci_name,
            ci_type=ci_type,
            type=memory_type,
            summary=summary,
            content=content,
            tokens=self._count_tokens(content),
            relevance_tags=[],  # Will be filled by caller
            priority=priority,
            expires=expires,
            references=[]
        )
    
    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary from content"""
        # Clean up the content
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove common prefixes
        prefixes = ['(?i)^(decided|learned|discovered|found that|will|plan to|error|failed to) ']
        for prefix in prefixes:
            content = re.sub(prefix, '', content)
        
        # Truncate to max length
        if len(content) > self.max_summary_length:
            content = content[:self.max_summary_length-3] + '...'
        
        # Capitalize first letter
        if content:
            content = content[0].upper() + content[1:]
        
        return content
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        
        # Technology keywords
        tech_keywords = [
            'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'django', 'flask', 'fastapi', 'nodejs', 'express',
            'docker', 'kubernetes', 'aws', 'gcp', 'azure',
            'postgres', 'mysql', 'mongodb', 'redis',
            'git', 'github', 'gitlab', 'ci/cd',
            'testing', 'jest', 'pytest', 'unittest'
        ]
        
        content_lower = content.lower()
        for keyword in tech_keywords:
            if keyword in content_lower:
                tags.append(keyword)
        
        # Extract camelCase and PascalCase identifiers
        identifiers = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', content)
        tags.extend(identifiers[:3])  # Limit to 3 identifiers
        
        # Extract file extensions
        extensions = re.findall(r'\.\w{2,4}\b', content)
        tags.extend(ext.lstrip('.') for ext in extensions[:2])
        
        # Deduplicate and limit
        seen = set()
        unique_tags = []
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag)
        
        return unique_tags[:10]  # Max 10 tags
    
    def _calculate_priority(self, memory_type: MemoryType, content: str) -> int:
        """Calculate priority based on type and content"""
        # Base priority by type
        base_priority = {
            MemoryType.ERROR: 7,
            MemoryType.DECISION: 6,
            MemoryType.INSIGHT: 5,
            MemoryType.PLAN: 4,
            MemoryType.CONTEXT: 3
        }
        
        priority = base_priority.get(memory_type, 5)
        
        # Boost for critical keywords
        critical_keywords = ['critical', 'important', 'urgent', 'breaking', 'security', 'vulnerability']
        if any(keyword in content.lower() for keyword in critical_keywords):
            priority = min(priority + 2, 10)
        
        # Boost for user mentions
        if 'casey' in content.lower() or 'user' in content.lower():
            priority = min(priority + 1, 10)
        
        return priority
    
    def _deduplicate_memories(self, memories: List[MemoryItem]) -> List[MemoryItem]:
        """Remove duplicate or very similar memories"""
        if len(memories) <= 1:
            return memories
        
        unique_memories = []
        seen_content = set()
        
        for memory in memories:
            # Simple content hash for exact duplicates
            content_hash = hashlib.md5(memory.content.lower().encode()).hexdigest()
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_memories.append(memory)
        
        return unique_memories
    
    def _detect_ci_type(self, ci_name: str) -> CIType:
        """Detect the type of CI from its name"""
        ci_name_lower = ci_name.lower()
        
        # Greek Chorus CIs
        greek_chorus = [
            'apollo', 'athena', 'ergon', 'penia', 'hermes',
            'hephaestus', 'mnemosyne', 'terma', 'kyklos'
        ]
        if any(name in ci_name_lower for name in greek_chorus):
            return CIType.GREEK
        
        # Terminal CIs
        if 'terminal' in ci_name_lower or 'term' in ci_name_lower:
            return CIType.TERMINAL
        
        # Project CIs
        if 'project' in ci_name_lower or 'proj' in ci_name_lower:
            return CIType.PROJECT
        
        return CIType.UNKNOWN
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Simple approximation: ~4 characters per token
        """
        return len(text) // 4
    
    def store_memories(self, memories: List[MemoryItem]) -> int:
        """
        Store extracted memories in the catalog
        
        Args:
            memories: List of memory items to store
            
        Returns:
            Number of memories stored
        """
        stored = 0
        for memory in memories:
            try:
                self.catalog.add_memory(memory)
                stored += 1
            except Exception as e:
                logger.error(f"Failed to store memory {memory.id}: {e}")
        
        if stored > 0:
            self.catalog.save()
            logger.info(f"Stored {stored} memories to catalog")
        
        return stored


# Example usage and testing
if __name__ == "__main__":
    # Test the extractor
    extractor = MemoryExtractor()
    
    # Sample exchange
    user_message = "Casey mentioned we should use TypeScript with strict mode enabled"
    ci_response = """
    I've decided to use Redux for state management after evaluating the options.
    Discovered that the performance bottleneck was in the render loop.
    I will implement memoization to fix this issue.
    There's an error in the import statements that needs fixing.
    """
    
    # Extract memories
    memories = extractor.extract_from_exchange(
        ci_name="ergon-ci",
        user_message=user_message,
        ci_response=ci_response
    )
    
    print(f"Extracted {len(memories)} memories:")
    for memory in memories:
        print(f"  [{memory.type.value}] {memory.summary}")
        print(f"    Tags: {', '.join(memory.relevance_tags)}")
        print(f"    Priority: {memory.priority}")