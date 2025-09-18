#!/usr/bin/env python3
"""
Apollo Memory Prioritizer

Implements relevance-based memory prioritization with hard 64KB limit.
Uses 85% relevance, 15% recency as per Casey's specification.
Truncates or suppresses responses >64KB.
"""

import json
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MemoryPrioritizer:
    """
    Prioritizes memories by relevance and recency.

    Design:
    - 85% weight on relevance (task, keywords, explicit requests)
    - 15% weight on recency (exponential decay over 1 week)
    - Hard 64KB limit with truncation
    - Async memory fulfillment within hooks
    """

    # Maximum output size (64KB)
    MAX_SIZE_BYTES = 64 * 1024

    # Relevance weights
    WEIGHT_EXPLICIT_REQUEST = 0.40  # CI explicitly asked for this
    WEIGHT_TASK_RELEVANCE = 0.25    # Matches current task
    WEIGHT_KEYWORD_MATCH = 0.20     # Contains recent keywords
    WEIGHT_RECENCY = 0.15          # How recent (exponential decay)

    def __init__(self):
        self.keyword_cache = {}
        self.relevance_cache = {}
        self.cache_duration = timedelta(minutes=5)

    def prioritize_memories(
        self,
        memories: List[Dict[str, Any]],
        context: Dict[str, Any],
        memory_requests: Optional[List[str]] = None
    ) -> str:
        """
        Prioritize memories and create digest within 64KB limit.

        Args:
            memories: List of memory items to prioritize
            context: Current task context including keywords, task type
            memory_requests: Explicit memory requests from CI sundown

        Returns:
            Prioritized memory digest as string (<64KB)
        """
        if not memories:
            return "# Memory Digest\nNo relevant memories found.\n"

        # Score all memories
        scored_memories = []
        for memory in memories:
            score = self._calculate_relevance_score(memory, context, memory_requests)
            scored_memories.append((score, memory))

        # Sort by score (highest first)
        scored_memories.sort(key=lambda x: x[0], reverse=True)

        # Build digest within size limit
        digest = self._build_digest(scored_memories, context, memory_requests)

        # Ensure size limit (truncate if needed)
        digest = self._enforce_size_limit(digest)

        return digest

    def _calculate_relevance_score(
        self,
        memory: Dict[str, Any],
        context: Dict[str, Any],
        memory_requests: Optional[List[str]]
    ) -> float:
        """
        Calculate relevance score for a memory item.

        Scoring:
        - 40%: Explicit request match
        - 25%: Task relevance
        - 20%: Keyword match
        - 15%: Recency
        """
        score = 0.0
        memory_content = str(memory.get('content', '')).lower()
        memory_tags = memory.get('tags', [])

        # 1. Explicit request match (40%)
        if memory_requests:
            for request in memory_requests:
                request_keywords = self._extract_keywords(request.lower())
                matches = sum(1 for kw in request_keywords if kw in memory_content)
                if matches > 0:
                    match_ratio = matches / len(request_keywords)
                    score += self.WEIGHT_EXPLICIT_REQUEST * match_ratio
                    break  # Only count highest match

        # 2. Task relevance (25%)
        task_type = context.get('task_type', '')
        task_objective = context.get('objective', '')

        if task_type and task_type.lower() in memory_content:
            score += self.WEIGHT_TASK_RELEVANCE * 0.5

        if task_objective:
            objective_keywords = self._extract_keywords(task_objective.lower())
            matches = sum(1 for kw in objective_keywords if kw in memory_content)
            if matches > 0:
                match_ratio = min(1.0, matches / max(1, len(objective_keywords)))
                score += self.WEIGHT_TASK_RELEVANCE * 0.5 * match_ratio

        # 3. Keyword match from recent context (20%)
        recent_keywords = context.get('recent_keywords', [])
        if recent_keywords:
            matches = sum(1 for kw in recent_keywords if kw.lower() in memory_content)
            if matches > 0:
                match_ratio = min(1.0, matches / len(recent_keywords))
                score += self.WEIGHT_KEYWORD_MATCH * match_ratio

        # 4. Recency score (15%)
        timestamp = memory.get('timestamp')
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    mem_time = datetime.fromisoformat(timestamp)
                else:
                    mem_time = timestamp

                age = datetime.now() - mem_time
                # Exponential decay over 1 week (168 hours)
                decay_factor = max(0, 1 - (age.total_seconds() / (168 * 3600)))
                score += self.WEIGHT_RECENCY * decay_factor
            except:
                # If timestamp parsing fails, give neutral recency
                score += self.WEIGHT_RECENCY * 0.5

        return score

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text.

        Simple approach: words > 3 chars, not stopwords
        """
        stopwords = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'been'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return keywords

    def _build_digest(
        self,
        scored_memories: List[Tuple[float, Dict]],
        context: Dict[str, Any],
        memory_requests: Optional[List[str]]
    ) -> str:
        """
        Build memory digest from scored memories.

        Format:
        - Requested memories first
        - High relevance memories
        - Context memories
        - Index of additional memories
        """
        sections = []
        current_size = 0
        max_section_size = self.MAX_SIZE_BYTES // 4  # Reserve space for each section

        # Header
        header = "# APOLLO MEMORY DIGEST\n"
        header += f"<!-- Generated: {datetime.now().isoformat()} -->\n\n"
        sections.append(header)
        current_size += len(header.encode('utf-8'))

        # Section 1: Explicitly requested memories (if any)
        if memory_requests and scored_memories:
            requested_section = "## Requested Information\n"
            added_count = 0

            for score, memory in scored_memories:
                if score >= self.WEIGHT_EXPLICIT_REQUEST * 0.5:  # Likely requested
                    memory_text = self._format_memory(memory)
                    memory_size = len(memory_text.encode('utf-8'))

                    if current_size + memory_size < max_section_size:
                        requested_section += memory_text + "\n"
                        current_size += memory_size
                        added_count += 1

                    if added_count >= 5:  # Limit requested memories
                        break

            if added_count > 0:
                sections.append(requested_section)

        # Section 2: Task-relevant memories
        task_section = "## Task Context\n"
        task_count = 0

        for score, memory in scored_memories:
            if score >= 0.3 and task_count < 10:  # Relevance threshold
                memory_text = self._format_memory(memory, brief=True)
                memory_size = len(memory_text.encode('utf-8'))

                if current_size + memory_size < self.MAX_SIZE_BYTES * 0.7:
                    task_section += memory_text + "\n"
                    current_size += memory_size
                    task_count += 1

        if task_count > 0:
            sections.append(task_section)

        # Section 3: Memory index (just pointers, not content)
        if len(scored_memories) > task_count + 5:
            index_section = "## Memory Index\n"
            index_section += f"*{len(scored_memories) - task_count} additional memories available*\n\n"

            for score, memory in scored_memories[task_count + 5:task_count + 15]:
                # Just show type and reference
                mem_type = memory.get('type', 'memory')
                mem_id = memory.get('id', 'unknown')
                index_section += f"- [{mem_type}] {mem_id} (score: {score:.2f})\n"

            if len(index_section.encode('utf-8')) + current_size < self.MAX_SIZE_BYTES:
                sections.append(index_section)

        # Footer with size info
        footer = f"\n<!-- Digest size: {current_size} bytes of {self.MAX_SIZE_BYTES} -->"
        sections.append(footer)

        return '\n'.join(sections)

    def _format_memory(self, memory: Dict[str, Any], brief: bool = False) -> str:
        """
        Format a memory item for inclusion in digest.

        Args:
            memory: Memory item to format
            brief: If True, use condensed format

        Returns:
            Formatted memory string
        """
        if brief:
            # Brief format - one line
            content = memory.get('content', '')
            if len(content) > 100:
                content = content[:97] + "..."
            return f"- {content}"
        else:
            # Full format
            mem_type = memory.get('type', 'memory')
            content = memory.get('content', '')
            source = memory.get('source', '')

            # Limit content size
            if len(content) > 500:
                content = content[:497] + "..."

            formatted = f"### {mem_type}\n{content}\n"
            if source:
                formatted += f"*Source: {source}*\n"

            return formatted

    def _enforce_size_limit(self, digest: str) -> str:
        """
        Enforce 64KB size limit on digest.

        If over limit, truncate with marker.
        """
        digest_bytes = digest.encode('utf-8')

        if len(digest_bytes) <= self.MAX_SIZE_BYTES:
            return digest

        # Need to truncate
        truncation_marker = "\n\n[TRUNCATED - Exceeded 64KB limit]"
        marker_bytes = truncation_marker.encode('utf-8')

        # Calculate how much we can keep
        available_bytes = self.MAX_SIZE_BYTES - len(marker_bytes)

        # Truncate at a character boundary
        truncated = digest_bytes[:available_bytes].decode('utf-8', errors='ignore')

        # Try to truncate at a line boundary
        last_newline = truncated.rfind('\n')
        if last_newline > available_bytes * 0.9:  # If we're not losing too much
            truncated = truncated[:last_newline]

        return truncated + truncation_marker

    async def fulfill_memory_request_async(
        self,
        request: str,
        context: Dict[str, Any],
        callback = None
    ) -> None:
        """
        Asynchronously fulfill a memory request.

        This runs in background and calls callback when ready.
        Designed to work within hooks without blocking.

        Args:
            request: Memory request string
            context: Current context
            callback: Function to call with results
        """
        import asyncio

        try:
            # Simulate memory retrieval (would connect to Engram)
            await asyncio.sleep(0.1)  # Non-blocking

            # In real implementation, would query Engram
            memories = []  # Would be actual retrieval

            # Prioritize with request
            digest = self.prioritize_memories(
                memories,
                context,
                memory_requests=[request]
            )

            # Call callback if provided
            if callback:
                callback(digest)

        except Exception as e:
            logger.error(f"Async memory request failed: {e}")
            if callback:
                callback(f"Error retrieving memories: {e}")


# Singleton instance
_prioritizer = MemoryPrioritizer()


def get_memory_digest(
    memories: List[Dict[str, Any]],
    context: Dict[str, Any],
    memory_requests: Optional[List[str]] = None
) -> str:
    """
    Get prioritized memory digest.

    Convenience function using singleton prioritizer.
    """
    return _prioritizer.prioritize_memories(memories, context, memory_requests)


async def request_memory_async(request: str, context: Dict, callback = None):
    """
    Request memory asynchronously.

    Non-blocking memory request for use in hooks.
    """
    await _prioritizer.fulfill_memory_request_async(request, context, callback)


if __name__ == "__main__":
    # Test prioritization
    print("Apollo Memory Prioritizer Test\n")

    # Sample memories
    test_memories = [
        {
            'content': 'Previous implementation used JSON.parse without size checks',
            'type': 'insight',
            'timestamp': datetime.now() - timedelta(hours=2),
            'tags': ['bug', 'memory', 'json']
        },
        {
            'content': 'Casey specified 85% relevance, 15% recency weighting',
            'type': 'decision',
            'timestamp': datetime.now() - timedelta(days=1),
            'tags': ['design', 'memory']
        },
        {
            'content': 'Old irrelevant data from last month',
            'type': 'note',
            'timestamp': datetime.now() - timedelta(days=30),
            'tags': ['old']
        }
    ]

    # Test context
    context = {
        'task_type': 'bug_fix',
        'objective': 'Fix memory overflow in JSON parsing',
        'recent_keywords': ['memory', 'overflow', 'json', 'parse']
    }

    # Test memory requests
    requests = [
        "Need examples of JSON parsing fixes",
        "Show memory management patterns"
    ]

    # Get digest
    digest = get_memory_digest(test_memories, context, requests)

    print(digest)
    print(f"\nDigest size: {len(digest.encode('utf-8'))} bytes")
    print(f"Within limit: {len(digest.encode('utf-8')) <= 64 * 1024}")