"""
Apollo Brief Presenter
Formats and presents Context Briefs to CIs within token budgets
Part of Apollo's Preparation service
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Import context brief components
try:
    from .context_brief import (
        ContextBriefManager, MemoryItem, MemoryType, CIType
    )
except ImportError:
    # For standalone testing
    from context_brief import (
        ContextBriefManager, MemoryItem, MemoryType, CIType
    )


class BriefPresenter:
    """
    Presents Context Briefs to CIs in a token-aware format
    Provides progressive disclosure and smart selection
    """
    
    def __init__(self, catalog: Optional[ContextBriefManager] = None):
        """
        Initialize the memory presenter
        
        Args:
            catalog: Optional MemoryCatalog instance to use
        """
        self.catalog = catalog or ContextBriefManager()
        
        # Configuration
        self.max_injection_tokens = 2000
        self.summary_mode_threshold = 1500  # Use summaries when near limit
        
        # Presentation templates
        self.templates = {
            'header': "## Relevant Context\n",
            'memory_full': "- **{type}** [{time_ago}]: {content}\n",
            'memory_summary': "- **{type}**: {summary}\n",
            'footer': "\n---\n"
        }
        
        logger.info("Memory presenter initialized")
    
    def get_memory_context(self, ci_name: str, message: str,
                           max_tokens: Optional[int] = None) -> str:
        """
        Get formatted memory context for injection into CI message
        
        Args:
            ci_name: Name of the CI requesting memories
            message: Current message content for relevance scoring
            max_tokens: Maximum token budget (default 2000)
            
        Returns:
            Formatted string of relevant memories
        """
        max_tokens = max_tokens or self.max_injection_tokens
        
        # Update relevance scores based on current context
        context = {
            'ci_name': ci_name,
            'message': message
        }
        self.catalog.update_relevance_scores(context)
        
        # Get packed memories within token budget
        memories = self.catalog.pack_memories(max_tokens - 100)  # Reserve space for formatting
        
        if not memories:
            return ""
        
        # Format memories
        formatted = self._format_memories(memories, max_tokens)
        
        logger.info(f"Prepared {len(memories)} memories for {ci_name}")
        return formatted
    
    def _format_memories(self, memories: List[MemoryItem], max_tokens: int) -> str:
        """Format memories for presentation"""
        output = []
        current_tokens = 0
        
        # Add header
        header = self.templates['header']
        output.append(header)
        current_tokens += self._count_tokens(header)
        
        # Group memories by type for better organization
        by_type = {}
        for memory in memories:
            type_key = memory.type.value if hasattr(memory.type, 'value') else str(memory.type)
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append(memory)
        
        # Priority order for types
        type_order = ['error', 'decision', 'insight', 'plan', 'context']
        
        # Add memories by type
        for memory_type in type_order:
            if memory_type in by_type:
                type_memories = by_type[memory_type]
                
                # Add type section
                section_header = f"\n### {memory_type.capitalize()}s\n"
                if current_tokens + self._count_tokens(section_header) < max_tokens:
                    output.append(section_header)
                    current_tokens += self._count_tokens(section_header)
                
                # Add individual memories
                for memory in type_memories:
                    formatted_memory = self._format_single_memory(memory, 
                                                                  current_tokens, 
                                                                  max_tokens)
                    if formatted_memory:
                        memory_tokens = self._count_tokens(formatted_memory)
                        if current_tokens + memory_tokens < max_tokens:
                            output.append(formatted_memory)
                            current_tokens += memory_tokens
                        else:
                            break  # Token limit reached
        
        # Add footer if space
        footer = self.templates['footer']
        if current_tokens + self._count_tokens(footer) < max_tokens:
            output.append(footer)
        
        return ''.join(output)
    
    def _format_single_memory(self, memory: MemoryItem, 
                             current_tokens: int, max_tokens: int) -> Optional[str]:
        """Format a single memory item"""
        # Calculate time ago
        time_ago = self._format_time_ago(memory.timestamp)
        
        # Determine if we should use full content or summary
        remaining_tokens = max_tokens - current_tokens
        use_summary = remaining_tokens < self.summary_mode_threshold
        
        if use_summary or len(memory.content) == len(memory.summary):
            # Use summary format
            return self.templates['memory_summary'].format(
                type=memory.type.value if hasattr(memory.type, 'value') else str(memory.type),
                summary=memory.summary
            )
        else:
            # Use full format
            return self.templates['memory_full'].format(
                type=memory.type.value if hasattr(memory.type, 'value') else str(memory.type),
                time_ago=time_ago,
                content=memory.content
            )
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as human-readable time ago"""
        now = datetime.now()
        delta = now - timestamp
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Simple approximation: ~4 characters per token
        """
        return len(text) // 4
    
    def get_memory_summary(self, ci_name: str) -> Dict[str, Any]:
        """
        Get a summary of memories for a CI
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Dictionary with memory statistics
        """
        # Filter memories by CI
        ci_memories = self.catalog.filter_by_ci(ci_name)
        
        # Calculate statistics
        stats = {
            'total_memories': len(ci_memories),
            'total_tokens': sum(m.tokens for m in ci_memories),
            'by_type': {},
            'recent_count': 0,
            'high_priority_count': 0
        }
        
        # Count by type
        for memory in ci_memories:
            type_key = memory.type.value if hasattr(memory.type, 'value') else str(memory.type)
            stats['by_type'][type_key] = stats['by_type'].get(type_key, 0) + 1
        
        # Count recent (last 24 hours)
        now = datetime.now()
        for memory in ci_memories:
            if (now - memory.timestamp).days < 1:
                stats['recent_count'] += 1
        
        # Count high priority
        stats['high_priority_count'] = sum(1 for m in ci_memories if m.priority >= 7)
        
        return stats
    
    def format_for_api(self, memories: List[MemoryItem]) -> List[Dict[str, Any]]:
        """
        Format memories for API response
        
        Args:
            memories: List of memory items
            
        Returns:
            List of dictionaries suitable for JSON serialization
        """
        formatted = []
        
        for memory in memories:
            formatted.append({
                'id': memory.id,
                'timestamp': memory.timestamp.isoformat() if isinstance(memory.timestamp, datetime) else memory.timestamp,
                'ci_source': memory.ci_source,
                'ci_type': memory.ci_type.value if hasattr(memory.ci_type, 'value') else memory.ci_type,
                'type': memory.type.value if hasattr(memory.type, 'value') else memory.type,
                'summary': memory.summary,
                'content': memory.content,
                'tokens': memory.tokens,
                'tags': memory.relevance_tags,
                'priority': memory.priority,
                'relevance_score': memory.relevance_score,
                'time_ago': self._format_time_ago(memory.timestamp)
            })
        
        return formatted


# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Create test catalog with sample memories
    test_dir = Path("/tmp/test_memory_presenter")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    catalog = MemoryCatalog(storage_dir=test_dir)
    presenter = MemoryPresenter(catalog)
    
    # Add sample memories
    from datetime import timedelta
    
    sample_memories = [
        MemoryItem(
            id="test1",
            timestamp=datetime.now() - timedelta(hours=1),
            ci_source="ergon-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.DECISION,
            summary="Use Redux for state management",
            content="After evaluating options, decided to use Redux for predictable state management",
            tokens=20,
            relevance_tags=["redux", "state"],
            priority=8,
            relevance_score=0.9
        ),
        MemoryItem(
            id="test2",
            timestamp=datetime.now() - timedelta(minutes=30),
            ci_source="apollo-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.INSIGHT,
            summary="Performance issue in render loop",
            content="Discovered that unnecessary re-renders were causing 200ms delays",
            tokens=15,
            relevance_tags=["performance", "react"],
            priority=7,
            relevance_score=0.8
        ),
        MemoryItem(
            id="test3",
            timestamp=datetime.now() - timedelta(days=2),
            ci_source="athena-ci",
            ci_type=CIType.GREEK,
            type=MemoryType.CONTEXT,
            summary="User prefers TypeScript",
            content="Casey mentioned preferring TypeScript with strict mode",
            tokens=12,
            relevance_tags=["typescript", "preferences"],
            priority=5,
            relevance_score=0.5
        )
    ]
    
    for memory in sample_memories:
        catalog.add_memory(memory)
    
    # Test memory context generation
    context = presenter.get_memory_context(
        ci_name="ergon-ci",
        message="I need to work on the Redux implementation",
        max_tokens=500
    )
    
    print("Generated Memory Context:")
    print(context)
    
    # Test memory summary
    summary = presenter.get_memory_summary("ergon-ci")
    print("\nMemory Summary for ergon-ci:")
    print(f"  Total memories: {summary['total_memories']}")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Recent memories: {summary['recent_count']}")
    
    # Test API formatting
    api_memories = presenter.format_for_api(sample_memories[:2])
    print("\nAPI Format (first memory):")
    import json
    print(json.dumps(api_memories[0], indent=2))
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)