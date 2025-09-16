"""
Turn Context Manager
Manages turn-based context for CIs with digest and prompt.
Simple, lightweight, no persistent memory.
"""

import json
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TurnContext:
    """
    Context for a single CI turn.
    
    Contains prompt and digest, totaling ~128KB maximum.
    """
    ci_name: str
    turn_id: str
    prompt: str
    digest: str
    task: Dict[str, Any]
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    @property
    def total_size(self) -> int:
        """Total size of context in characters."""
        return len(self.prompt) + len(self.digest)
    
    @property
    def size_kb(self) -> float:
        """Total size in KB."""
        return self.total_size / 1024
    
    def is_within_limits(self) -> bool:
        """Check if context is within size limits."""
        # 128KB limit for prompt + digest
        return self.size_kb <= 128
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ci_name': self.ci_name,
            'turn_id': self.turn_id,
            'prompt': self.prompt,
            'digest': self.digest,
            'task': self.task,
            'timestamp': self.timestamp,
            'size_kb': self.size_kb
        }
    
    def format_for_ci(self) -> str:
        """
        Format context for CI consumption.
        
        Returns combined prompt and digest in a clear format.
        """
        formatted = []
        
        # Add digest first (background context)
        if self.digest:
            formatted.append("=== CONTEXT DIGEST ===")
            formatted.append(self.digest)
            formatted.append("")
        
        # Add prompt (current task)
        if self.prompt:
            formatted.append("=== TASK PROMPT ===")
            formatted.append(self.prompt)
        
        return "\n".join(formatted)


class TurnManager:
    """
    Manages turns for all CIs.
    
    Coordinates with Apollo (digest) and Rhetor (prompt) to prepare contexts.
    """
    
    def __init__(self):
        """Initialize turn manager."""
        self.current_turns = {}  # Current turn per CI
        self.apollo_service = None
        self.rhetor_service = None
        self.engram_service = None
        self._init_services()
    
    def _init_services(self):
        """Initialize service connections."""
        try:
            from Apollo.apollo.services.digest_service import get_digest_service
            self.apollo_service = get_digest_service()
            logger.info("Connected to Apollo digest service")
        except ImportError:
            logger.warning("Apollo digest service not available")
        
        try:
            from Rhetor.rhetor.services.prompt_service import get_prompt_service
            self.rhetor_service = get_prompt_service()
            logger.info("Connected to Rhetor prompt service")
        except ImportError:
            logger.warning("Rhetor prompt service not available")
        
        try:
            from Engram.engram.services.storage_service import get_storage_service
            self.engram_service = get_storage_service()
            logger.info("Connected to Engram storage service")
        except ImportError:
            logger.warning("Engram storage service not available")
    
    def start_turn(
        self,
        ci_name: str,
        task: Dict[str, Any],
        ci_type: str = 'specialist'
    ) -> TurnContext:
        """
        Start a new turn for a CI.
        
        Args:
            ci_name: Name of the CI
            task: Task specification
            ci_type: Type of CI
            
        Returns:
            TurnContext with prompt and digest
        """
        logger.info(f"Starting turn for {ci_name}")
        
        # Generate turn ID
        turn_id = self._generate_turn_id(ci_name)
        
        # Get previous turn summary if any
        previous_turn = None
        if self.engram_service:
            previous_turn = self.engram_service.get_previous_turn(ci_name)
        
        # Prepare digest (Apollo)
        digest = ""
        if self.apollo_service:
            digest = self.apollo_service.prepare_digest(
                ci_name=ci_name,
                task_context=task,
                ci_type=ci_type
            )
        else:
            digest = self._create_fallback_digest(ci_name, task)
        
        # Prepare prompt (Rhetor)
        prompt = ""
        if self.rhetor_service:
            prompt = self.rhetor_service.compose_prompt(
                ci_name=ci_name,
                task=task,
                previous_turn=previous_turn
            )
        else:
            prompt = self._create_fallback_prompt(ci_name, task)
        
        # Create turn context
        context = TurnContext(
            ci_name=ci_name,
            turn_id=turn_id,
            prompt=prompt,
            digest=digest,
            task=task
        )
        
        # Validate size
        if not context.is_within_limits():
            logger.warning(f"Turn context exceeds limits: {context.size_kb:.1f}KB")
            # Truncate if needed
            context = self._truncate_context(context)
        
        # Store as current turn
        self.current_turns[ci_name] = context
        
        logger.info(f"Started turn {turn_id} for {ci_name} ({context.size_kb:.1f}KB)")
        
        return context
    
    def end_turn(
        self,
        ci_name: str,
        memories_to_store: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        End a CI's turn and store memories.
        
        Args:
            ci_name: Name of the CI
            memories_to_store: Memories to store from this turn
            
        Returns:
            True if successful
        """
        if ci_name not in self.current_turns:
            logger.warning(f"No active turn for {ci_name}")
            return False
        
        context = self.current_turns[ci_name]
        logger.info(f"Ending turn {context.turn_id} for {ci_name}")
        
        # Store memories if provided
        if memories_to_store and self.engram_service:
            success = self.engram_service.store(
                ci_name=ci_name,
                turn_id=context.turn_id,
                memories=memories_to_store
            )
            if success:
                logger.info(f"Stored {len(memories_to_store)} memories for {ci_name}")
        
        # Clear current turn
        del self.current_turns[ci_name]
        
        return True
    
    def get_current_context(self, ci_name: str) -> Optional[TurnContext]:
        """
        Get the current turn context for a CI.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Current TurnContext or None
        """
        return self.current_turns.get(ci_name)
    
    def format_context_for_ci(self, ci_name: str) -> Optional[str]:
        """
        Get formatted context ready for CI consumption.
        
        Args:
            ci_name: Name of the CI
            
        Returns:
            Formatted context string or None
        """
        context = self.get_current_context(ci_name)
        if context:
            return context.format_for_ci()
        return None
    
    def _generate_turn_id(self, ci_name: str) -> str:
        """Generate unique turn ID."""
        timestamp = datetime.now().isoformat()
        content = f"{ci_name}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _create_fallback_digest(self, ci_name: str, task: Dict[str, Any]) -> str:
        """Create a simple fallback digest."""
        return f"Context for {ci_name}: {task.get('objective', 'No specific objective')}"
    
    def _create_fallback_prompt(self, ci_name: str, task: Dict[str, Any]) -> str:
        """Create a simple fallback prompt."""
        prompt_parts = [
            f"Task for {ci_name}:",
            f"Objective: {task.get('objective', 'Complete the task')}",
        ]
        
        if 'steps' in task:
            prompt_parts.append("Steps:")
            for i, step in enumerate(task['steps'], 1):
                prompt_parts.append(f"  {i}. {step}")
        
        return "\n".join(prompt_parts)
    
    def _truncate_context(self, context: TurnContext) -> TurnContext:
        """Truncate context to fit within limits."""
        max_size = 128 * 1024  # 128KB in chars
        
        # Calculate how much to keep from each
        prompt_ratio = 0.5  # Split 50/50
        max_prompt = int(max_size * prompt_ratio)
        max_digest = int(max_size * (1 - prompt_ratio))
        
        # Truncate if needed
        if len(context.prompt) > max_prompt:
            context.prompt = context.prompt[:max_prompt - 50] + "\n[Truncated]"
        
        if len(context.digest) > max_digest:
            context.digest = context.digest[:max_digest - 50] + "\n[Truncated]"
        
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get turn manager statistics."""
        return {
            'active_turns': len(self.current_turns),
            'services': {
                'apollo': self.apollo_service is not None,
                'rhetor': self.rhetor_service is not None,
                'engram': self.engram_service is not None
            },
            'turns': {
                ci_name: {
                    'turn_id': context.turn_id,
                    'size_kb': context.size_kb,
                    'task_type': context.task.get('type', 'unknown')
                }
                for ci_name, context in self.current_turns.items()
            }
        }


# Singleton manager instance
_turn_manager = None


def get_turn_manager() -> TurnManager:
    """Get or create the turn manager."""
    global _turn_manager
    if _turn_manager is None:
        _turn_manager = TurnManager()
    return _turn_manager


def start_ci_turn(
    ci_name: str,
    task: Dict[str, Any],
    ci_type: str = 'specialist'
) -> str:
    """
    Convenience function to start a CI turn.
    
    Args:
        ci_name: Name of the CI
        task: Task specification
        ci_type: Type of CI
        
    Returns:
        Formatted context string for the CI
    """
    manager = get_turn_manager()
    context = manager.start_turn(ci_name, task, ci_type)
    return context.format_for_ci()


def end_ci_turn(
    ci_name: str,
    memories: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """
    Convenience function to end a CI turn.
    
    Args:
        ci_name: Name of the CI
        memories: Memories to store
        
    Returns:
        True if successful
    """
    manager = get_turn_manager()
    return manager.end_turn(ci_name, memories)