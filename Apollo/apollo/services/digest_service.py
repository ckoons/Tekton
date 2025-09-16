"""
Apollo Digest Service
Prepares memory digests for CIs at the start of each turn.
Maximum digest size: 64KB
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class DigestService:
    """
    Prepares concise memory digests for CI turns.
    
    Apollo's role is to curate relevant memories into digestible summaries
    that provide context without overwhelming the CI.
    """
    
    # Maximum digest size in characters (approximately 64KB)
    MAX_DIGEST_SIZE = 65536
    
    # Digest formats for different CI types
    DIGEST_FORMATS = {
        'conversational': 'narrative',
        'analytical': 'structured',
        'orchestrator': 'structured',
        'specialist': 'minimal'
    }
    
    def __init__(self):
        self.engram_client = None
        self._init_engram_connection()
        
    def _init_engram_connection(self):
        """Initialize connection to Engram storage."""
        try:
            # This will be the simple Engram storage API
            from Engram.engram.services.storage_service import StorageService
            self.engram_client = StorageService()
            logger.info("Connected to Engram storage service")
        except ImportError:
            logger.warning("Engram not available, using mock storage")
            self.engram_client = MockStorage()
    
    def prepare_digest(
        self,
        ci_name: str,
        task_context: Dict[str, Any],
        ci_type: str = 'specialist'
    ) -> str:
        """
        Prepare a memory digest for a CI's turn.
        
        Args:
            ci_name: Name of the CI
            task_context: Context about the current task
            ci_type: Type of CI (affects formatting)
            
        Returns:
            Formatted digest string (≤64KB)
        """
        logger.info(f"Preparing digest for {ci_name} (type: {ci_type})")
        
        # Determine digest format
        format_style = self.DIGEST_FORMATS.get(ci_type, 'minimal')
        
        # Gather relevant memories
        memories = self._gather_relevant_memories(ci_name, task_context)
        
        # Format based on CI type
        if format_style == 'narrative':
            digest = self._format_narrative_digest(memories, task_context)
        elif format_style == 'structured':
            digest = self._format_structured_digest(memories, task_context)
        else:
            digest = self._format_minimal_digest(memories, task_context)
        
        # Ensure size limit
        digest = self._enforce_size_limit(digest)
        
        logger.info(f"Prepared {len(digest)} char digest for {ci_name}")
        return digest
    
    def _gather_relevant_memories(
        self,
        ci_name: str,
        task_context: Dict[str, Any]
    ) -> Dict[str, List[Dict]]:
        """Gather memories relevant to the task."""
        memories = {
            'previous_turn': [],
            'task_related': [],
            'domain_knowledge': [],
            'insights': []
        }
        
        if not self.engram_client:
            return memories
        
        try:
            # Get previous turn summary
            previous = self.engram_client.get_previous_turn(ci_name)
            if previous:
                memories['previous_turn'] = [previous]
            
            # Get task-related memories
            if 'task_type' in task_context:
                task_memories = self.engram_client.retrieve(
                    ci_name=ci_name,
                    query=task_context['task_type'],
                    limit=5
                )
                memories['task_related'] = task_memories
            
            # Get domain knowledge if specified
            if 'domain' in task_context:
                domain_memories = self.engram_client.retrieve_domain(
                    domain=task_context['domain'],
                    limit=3
                )
                memories['domain_knowledge'] = domain_memories
            
            # Get recent insights
            insights = self.engram_client.retrieve_insights(
                ci_name=ci_name,
                limit=2
            )
            memories['insights'] = insights
            
        except Exception as e:
            logger.error(f"Error gathering memories: {e}")
        
        return memories
    
    def _format_narrative_digest(
        self,
        memories: Dict[str, List[Dict]],
        task_context: Dict[str, Any]
    ) -> str:
        """Format memories as a narrative digest."""
        sections = []
        
        # Previous turn context
        if memories['previous_turn']:
            prev = memories['previous_turn'][0]
            sections.append(
                f"Previously, you {prev.get('action', 'worked on')} "
                f"{prev.get('target', 'a task')}. "
                f"{prev.get('outcome', '')}"
            )
        
        # Task-related context
        if memories['task_related']:
            relevant_points = []
            for mem in memories['task_related'][:3]:
                if 'content' in mem:
                    relevant_points.append(mem['content'])
            
            if relevant_points:
                sections.append(
                    f"Relevant context: {'; '.join(relevant_points)}"
                )
        
        # Domain knowledge
        if memories['domain_knowledge']:
            knowledge = memories['domain_knowledge'][0]
            sections.append(
                f"Remember: {knowledge.get('content', '')}"
            )
        
        # Insights
        if memories['insights']:
            insight = memories['insights'][0]
            sections.append(
                f"Key insight: {insight.get('content', '')}"
            )
        
        # Combine sections
        digest = "\n\n".join(sections)
        
        # Add task focus
        if 'objective' in task_context:
            digest = f"Current objective: {task_context['objective']}\n\n{digest}"
        
        return digest
    
    def _format_structured_digest(
        self,
        memories: Dict[str, List[Dict]],
        task_context: Dict[str, Any]
    ) -> str:
        """Format memories as a structured digest."""
        digest_structure = {
            'task_context': task_context,
            'previous_turn': None,
            'relevant_memories': [],
            'domain_knowledge': [],
            'insights': []
        }
        
        # Add previous turn
        if memories['previous_turn']:
            prev = memories['previous_turn'][0]
            digest_structure['previous_turn'] = {
                'action': prev.get('action'),
                'result': prev.get('result'),
                'timestamp': prev.get('timestamp')
            }
        
        # Add relevant memories (limited)
        for mem in memories['task_related'][:5]:
            digest_structure['relevant_memories'].append({
                'content': mem.get('content', ''),
                'relevance': mem.get('relevance', 0)
            })
        
        # Add domain knowledge
        for knowledge in memories['domain_knowledge'][:3]:
            digest_structure['domain_knowledge'].append(
                knowledge.get('content', '')
            )
        
        # Add insights
        for insight in memories['insights'][:2]:
            digest_structure['insights'].append({
                'content': insight.get('content', ''),
                'confidence': insight.get('confidence', 0)
            })
        
        # Convert to formatted string
        digest = "=== MEMORY DIGEST ===\n\n"
        
        if digest_structure['previous_turn']:
            digest += "Previous Turn:\n"
            prev = digest_structure['previous_turn']
            digest += f"  Action: {prev['action']}\n"
            digest += f"  Result: {prev['result']}\n\n"
        
        if digest_structure['relevant_memories']:
            digest += "Relevant Context:\n"
            for mem in digest_structure['relevant_memories']:
                digest += f"  • {mem['content']}\n"
            digest += "\n"
        
        if digest_structure['domain_knowledge']:
            digest += "Domain Knowledge:\n"
            for knowledge in digest_structure['domain_knowledge']:
                digest += f"  • {knowledge}\n"
            digest += "\n"
        
        if digest_structure['insights']:
            digest += "Key Insights:\n"
            for insight in digest_structure['insights']:
                digest += f"  • {insight['content']}\n"
        
        return digest
    
    def _format_minimal_digest(
        self,
        memories: Dict[str, List[Dict]],
        task_context: Dict[str, Any]
    ) -> str:
        """Format a minimal digest with just essentials."""
        points = []
        
        # Previous turn (one line)
        if memories['previous_turn']:
            prev = memories['previous_turn'][0]
            points.append(f"Previous: {prev.get('summary', 'N/A')}")
        
        # Most relevant memory
        if memories['task_related']:
            points.append(f"Context: {memories['task_related'][0].get('content', '')}")
        
        # Key insight if any
        if memories['insights']:
            points.append(f"Note: {memories['insights'][0].get('content', '')}")
        
        return "\n".join(points)
    
    def _enforce_size_limit(self, digest: str) -> str:
        """Ensure digest doesn't exceed size limit."""
        if len(digest) <= self.MAX_DIGEST_SIZE:
            return digest
        
        # Truncate with indicator
        truncated = digest[:self.MAX_DIGEST_SIZE - 100]
        
        # Find good break point
        last_newline = truncated.rfind('\n')
        if last_newline > self.MAX_DIGEST_SIZE - 500:
            truncated = truncated[:last_newline]
        
        return truncated + "\n\n[Digest truncated for size]"
    
    def get_digest_stats(self, digest: str) -> Dict[str, Any]:
        """Get statistics about a digest."""
        return {
            'size_chars': len(digest),
            'size_kb': len(digest.encode('utf-8')) / 1024,
            'lines': digest.count('\n'),
            'sections': digest.count('==='),
            'within_limit': len(digest) <= self.MAX_DIGEST_SIZE
        }


class MockStorage:
    """Mock storage for testing without Engram."""
    
    def get_previous_turn(self, ci_name: str) -> Optional[Dict]:
        return {
            'action': 'analyzed data',
            'target': 'user metrics',
            'outcome': 'Found 3 patterns',
            'timestamp': datetime.now().isoformat()
        }
    
    def retrieve(self, ci_name: str, query: str, limit: int) -> List[Dict]:
        return [
            {'content': f'Mock memory about {query}', 'relevance': 0.8}
        ]
    
    def retrieve_domain(self, domain: str, limit: int) -> List[Dict]:
        return [
            {'content': f'Domain knowledge for {domain}'}
        ]
    
    def retrieve_insights(self, ci_name: str, limit: int) -> List[Dict]:
        return [
            {'content': 'Mock insight', 'confidence': 0.7}
        ]


# Singleton service instance
_digest_service = None


def get_digest_service() -> DigestService:
    """Get or create the digest service."""
    global _digest_service
    if _digest_service is None:
        _digest_service = DigestService()
    return _digest_service


def prepare_digest_for_turn(
    ci_name: str,
    task_context: Dict[str, Any],
    ci_type: str = 'specialist'
) -> str:
    """
    Convenience function to prepare a digest for a CI turn.
    
    Args:
        ci_name: Name of the CI
        task_context: Context about the current task
        ci_type: Type of CI
        
    Returns:
        Formatted digest (≤64KB)
    """
    service = get_digest_service()
    return service.prepare_digest(ci_name, task_context, ci_type)