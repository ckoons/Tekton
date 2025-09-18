#!/usr/bin/env python3
"""
Working Memory System for CI Continuity

Replaces --continue with intelligent context management.
Working memory is the full context (up to 533KB) composed of:
- Recent exchanges (ephemeral)
- Sundown/sunrise notes (semi-persistent in /tmp)
- Apollo memory digest (from Engram)
- Current task context

The CI has ~267KB free for their response.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import hashlib

logger = logging.getLogger(__name__)

# Size limits based on 200K token context (~800KB text)
# Reserve 1/3 for CI work = 267KB
# Working memory gets 533KB
MEMORY_LIMITS = {
    'total_working_memory': 533 * 1024,     # 533KB total context
    'recent_exchanges': 200 * 1024,         # 200KB for conversation
    'sundown_context': 50 * 1024,           # 50KB for continuity
    'apollo_digest': 64 * 1024,             # 64KB from Apollo
    'rhetor_output': 64 * 1024,             # 64KB from Rhetor
    'buffer_overhead': 155 * 1024,          # Buffer and overhead
    'ci_workspace': 267 * 1024,             # Reserved for CI
}


class WorkingMemory:
    """
    Manages the full working memory context for a CI.

    This is ephemeral - only exists during active conversation.
    What needs to persist is determined by the CI through sundown.
    """

    def __init__(self, ci_name: str):
        """Initialize working memory for a CI."""
        self.ci_name = ci_name
        self.recent_exchanges: List[Tuple[str, str]] = []  # (user, assistant) pairs
        self.sundown_context: Optional[Dict] = None
        self.apollo_digest: Optional[str] = None
        self.current_task: Optional[str] = None
        self.active_memory: Dict[str, Any] = {}  # Key facts and context

        # Sundown storage location
        self.sundown_path = Path(f"/tmp/sundown/{ci_name}")
        self.sundown_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Working memory initialized for {ci_name}")

    def add_exchange(self, user_message: str, assistant_response: str) -> None:
        """
        Add a conversation exchange to working memory.

        Automatically manages size by removing oldest exchanges.
        """
        self.recent_exchanges.append((user_message, assistant_response))

        # Trim if too large
        while self._calculate_exchanges_size() > MEMORY_LIMITS['recent_exchanges']:
            if len(self.recent_exchanges) > 1:
                self.recent_exchanges.pop(0)  # Remove oldest
                logger.debug(f"Trimmed oldest exchange for {self.ci_name}")
            else:
                # If even one exchange is too large, truncate it
                user, assistant = self.recent_exchanges[0]
                max_each = MEMORY_LIMITS['recent_exchanges'] // 2
                if len(user.encode('utf-8')) > max_each:
                    user = user[:max_each // 3] + "\n[TRUNCATED]"
                if len(assistant.encode('utf-8')) > max_each:
                    assistant = assistant[:max_each // 3] + "\n[TRUNCATED]"
                self.recent_exchanges[0] = (user, assistant)
                break

    def load_sundown_notes(self) -> Optional[Dict]:
        """Load the most recent sundown notes from /tmp."""
        try:
            latest_file = self.sundown_path / "latest.json"
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    self.sundown_context = json.load(f)
                    logger.info(f"Loaded sundown for {self.ci_name}")
                    return self.sundown_context

            # Fallback to most recent timestamped file
            sundown_files = sorted(self.sundown_path.glob("*.json"), reverse=True)
            if sundown_files and sundown_files[0].name != "latest.json":
                with open(sundown_files[0], 'r') as f:
                    self.sundown_context = json.load(f)
                    logger.info(f"Loaded sundown from {sundown_files[0].name}")
                    return self.sundown_context

        except Exception as e:
            logger.error(f"Failed to load sundown: {e}")

        return None

    def set_apollo_digest(self, digest: str) -> None:
        """Set the Apollo memory digest."""
        # Enforce size limit
        max_size = MEMORY_LIMITS['apollo_digest']
        if len(digest.encode('utf-8')) > max_size:
            digest = digest[:max_size - 50] + "\n[TRUNCATED]"
        self.apollo_digest = digest

    def set_current_task(self, task: str) -> None:
        """Set the current task description."""
        self.current_task = task

    def get_context_prompt(self) -> str:
        """
        Compose the full working memory context.

        Returns structured context ready for the CI.
        Total size will be under 533KB.
        """
        sections = []

        # 1. Sundown context (if exists)
        if self.sundown_context:
            sections.append(self._format_sundown_section())

        # 2. Current task
        if self.current_task:
            sections.append(f"## Current Task\n{self.current_task}\n")

        # 3. Recent conversation context
        if self.recent_exchanges:
            sections.append(self._format_exchanges_section())

        # 4. Apollo memory digest
        if self.apollo_digest:
            sections.append(f"## Memory Context\n{self.apollo_digest}\n")

        # 5. Active memory/key facts
        if self.active_memory:
            sections.append(self._format_active_memory())

        # Combine all sections
        full_context = "\n".join(sections)

        # Final size check and truncation if needed
        context_bytes = full_context.encode('utf-8')
        if len(context_bytes) > MEMORY_LIMITS['total_working_memory']:
            # Truncate with warning
            max_size = MEMORY_LIMITS['total_working_memory'] - 100
            full_context = full_context[:max_size // 3]  # Rough char estimate
            full_context += "\n\n[CONTEXT TRUNCATED TO FIT LIMITS]"
            logger.warning(f"Context truncated for {self.ci_name}")

        return full_context

    def _calculate_exchanges_size(self) -> int:
        """Calculate total size of recent exchanges."""
        total = 0
        for user, assistant in self.recent_exchanges:
            total += len(user.encode('utf-8')) + len(assistant.encode('utf-8'))
        return total

    def _format_sundown_section(self) -> str:
        """Format sundown notes into context section."""
        if not self.sundown_context:
            return ""

        lines = ["## Previous Session Context"]

        if 'todo_list' in self.sundown_context:
            lines.append("\n### Todo List")
            for item in self.sundown_context['todo_list']:
                status = "✓" if item.get('completed') else "○"
                lines.append(f"- {status} {item.get('task', 'Unknown task')}")

        if 'context_notes' in self.sundown_context:
            lines.append("\n### Context for This Turn")
            lines.append(self.sundown_context['context_notes'])

        if 'memory_requests' in self.sundown_context:
            lines.append("\n### Requested Memories")
            for req in self.sundown_context['memory_requests']:
                lines.append(f"- {req}")

        return "\n".join(lines)

    def _format_exchanges_section(self) -> str:
        """Format recent exchanges into context section."""
        if not self.recent_exchanges:
            return ""

        lines = ["## Recent Conversation"]

        # Show last 3-5 exchanges (or all if fewer)
        exchanges_to_show = self.recent_exchanges[-5:]

        for i, (user, assistant) in enumerate(exchanges_to_show, 1):
            lines.append(f"\n### Exchange {i}")
            lines.append(f"**User:** {user[:500]}...")  # Truncate long messages
            lines.append(f"**Assistant:** {assistant[:500]}...")

        return "\n".join(lines)

    def _format_active_memory(self) -> str:
        """Format active memory/key facts."""
        if not self.active_memory:
            return ""

        lines = ["## Active Context"]

        for key, value in self.active_memory.items():
            if isinstance(value, dict):
                lines.append(f"\n### {key}")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"\n### {key}")
                for item in value[:10]:  # Limit list items
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def prepare_for_sunrise(self, memory_requests: Optional[List[str]] = None) -> Dict:
        """
        Prepare context for sunrise (new session).

        Returns context dict for Apollo and Rhetor.
        """
        context = {
            'ci_name': self.ci_name,
            'has_sundown': self.sundown_context is not None,
            'current_task': self.current_task,
            'recent_exchanges_count': len(self.recent_exchanges),
            'memory_requests': memory_requests or []
        }

        # Add sundown memory requests if any
        if self.sundown_context and 'memory_requests' in self.sundown_context:
            context['memory_requests'].extend(self.sundown_context['memory_requests'])

        # Add keywords from recent conversation
        if self.recent_exchanges:
            # Extract keywords from last exchange
            last_user, _ = self.recent_exchanges[-1] if self.recent_exchanges else ("", "")
            context['recent_keywords'] = self._extract_keywords(last_user)

        return context

    def _extract_keywords(self, text: str, limit: int = 20) -> List[str]:
        """Extract keywords from text for context."""
        import re
        stopwords = {
            'the', 'and', 'for', 'with', 'from', 'this', 'that',
            'have', 'been', 'will', 'can', 'should', 'would'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]

        # Return unique keywords, preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
                if len(unique_keywords) >= limit:
                    break

        return unique_keywords


class WorkingMemoryManager:
    """
    Manages working memory for all CIs.
    Singleton pattern for consistent memory across the system.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.memories = {}
        return cls._instance

    def get_memory(self, ci_name: str) -> WorkingMemory:
        """Get or create working memory for a CI."""
        if ci_name not in self.memories:
            self.memories[ci_name] = WorkingMemory(ci_name)
        return self.memories[ci_name]

    def clear_memory(self, ci_name: str) -> None:
        """Clear working memory for a CI (on sundown)."""
        if ci_name in self.memories:
            del self.memories[ci_name]
            logger.info(f"Cleared working memory for {ci_name}")


# Global manager instance
_manager = WorkingMemoryManager()


def get_working_memory(ci_name: str) -> WorkingMemory:
    """Get working memory for a CI."""
    return _manager.get_memory(ci_name)


def clear_working_memory(ci_name: str) -> None:
    """Clear working memory for a CI."""
    _manager.clear_memory(ci_name)