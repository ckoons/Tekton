#!/usr/bin/env python3
"""
Memory Pipeline for Claude Handler

Integrates Apollo and Rhetor to process all memory before Claude.
Enforces 64KB limits and prevents direct Engram access.
"""

import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import Apollo and Rhetor
from Apollo.apollo.core.memory_prioritizer import MemoryPrioritizer, get_memory_digest
from Rhetor.rhetor.core.prompt_optimizer import PromptOptimizer, optimize_prompt

# Import sundown handling
from shared.ci_tools.sundown_enhanced import EnhancedCISundown

logger = logging.getLogger(__name__)


class MemoryPipeline:
    """
    Processes all memory through Apollo/Rhetor before Claude.

    This pipeline:
    1. Intercepts memory requests
    2. Gets Apollo digest (<64KB)
    3. Optimizes with Rhetor (<64KB)
    4. Passes clean text to Claude (no JSON parsing!)
    """

    def __init__(self):
        self.apollo = MemoryPrioritizer()
        self.rhetor = PromptOptimizer()
        self.sundown_manager = None
        self.memory_cache = {}
        self.pending_requests = {}

    async def process_for_claude(
        self,
        ci_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process message through memory pipeline for Claude.

        Args:
            ci_name: Name of the CI
            message: User message/task
            context: Optional context (sundown, memory requests, etc.)

        Returns:
            Optimized prompt ready for Claude (<128KB total)
        """
        logger.info(f"Processing message for {ci_name} through memory pipeline")

        # Step 1: Get sundown notes if available
        sundown_notes = await self._get_sundown_notes(ci_name)
        memory_requests = None

        if sundown_notes:
            # Parse memory requests from sundown
            if not self.sundown_manager:
                self.sundown_manager = EnhancedCISundown(ci_name)
            parsed = self.sundown_manager.parse_enhanced_sundown_notes(sundown_notes)
            if parsed:
                memory_requests = parsed.get('memory_requests', [])

        # Step 2: Get relevant memories through Apollo
        apollo_digest = await self._get_apollo_digest(
            ci_name,
            message,
            context,
            memory_requests
        )

        # Step 3: Optimize through Rhetor
        optimized_prompt = self._optimize_with_rhetor(
            sundown_notes,
            message,
            apollo_digest
        )

        # Step 4: Final size check
        prompt_bytes = optimized_prompt.encode('utf-8')
        if len(prompt_bytes) > 128 * 1024:
            logger.warning(f"Prompt still too large ({len(prompt_bytes)} bytes), forcing truncation")
            optimized_prompt = self._force_truncate(optimized_prompt, 128)

        logger.info(f"Pipeline complete: {len(prompt_bytes)} bytes")
        return optimized_prompt

    async def _get_sundown_notes(self, ci_name: str) -> Optional[str]:
        """
        Retrieve sundown notes for CI.

        In production, this would query Engram.
        For now, checks local storage.
        """
        try:
            # Check for stored sundown
            storage_dir = Path('/Users/cskoons/projects/github/Coder-A/engram/sundown')
            if not storage_dir.exists():
                return None

            # Find most recent sundown for this CI
            pattern = f"{ci_name}_*.md"
            sundown_files = sorted(storage_dir.glob(pattern), reverse=True)

            if sundown_files:
                with open(sundown_files[0], 'r') as f:
                    return f.read()

        except Exception as e:
            logger.error(f"Error retrieving sundown: {e}")

        return None

    async def _get_apollo_digest(
        self,
        ci_name: str,
        message: str,
        context: Optional[Dict[str, Any]],
        memory_requests: Optional[List[str]]
    ) -> str:
        """
        Get memory digest from Apollo.

        This replaces direct Engram access!
        """
        try:
            # Build context for Apollo
            apollo_context = {
                'task_type': self._identify_task_type(message),
                'objective': message[:200],  # First 200 chars as objective
                'recent_keywords': self._extract_keywords(message)
            }

            if context:
                apollo_context.update(context)

            # In production, Apollo would query Engram
            # For now, simulate with limited data
            memories = await self._fetch_limited_memories(ci_name, apollo_context)

            # Get prioritized digest from Apollo
            digest = get_memory_digest(
                memories,
                apollo_context,
                memory_requests
            )

            return digest

        except Exception as e:
            logger.error(f"Apollo digest failed: {e}")
            return "# Memory Digest\n*Memory service temporarily unavailable*\n"

    async def _fetch_limited_memories(
        self,
        ci_name: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch LIMITED memories (not all!).

        This is the key fix - we never fetch everything.
        """
        memories = []

        try:
            # Would connect to Engram with LIMITS
            # For now, return empty to prevent overflow
            pass

        except Exception as e:
            logger.error(f"Memory fetch failed: {e}")

        return memories

    def _optimize_with_rhetor(
        self,
        sundown_notes: Optional[str],
        message: str,
        apollo_digest: str
    ) -> str:
        """
        Optimize prompt through Rhetor.
        """
        try:
            # Get optimized prompt
            optimized = optimize_prompt(
                sundown_notes,
                message,
                apollo_digest
            )

            return optimized

        except Exception as e:
            logger.error(f"Rhetor optimization failed: {e}")
            # Fallback to basic combination
            return f"# Task\n{message}\n\n# Context\n{apollo_digest}"

    def _identify_task_type(self, message: str) -> str:
        """Identify the type of task from message."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['fix', 'bug', 'error', 'crash']):
            return 'bug_fix'
        elif any(word in message_lower for word in ['implement', 'create', 'build', 'add']):
            return 'implementation'
        elif any(word in message_lower for word in ['analyze', 'review', 'check', 'inspect']):
            return 'analysis'
        elif any(word in message_lower for word in ['test', 'verify', 'validate']):
            return 'testing'
        else:
            return 'general'

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        import re
        stopwords = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'been'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return keywords[:20]  # Limit to 20 keywords

    def _force_truncate(self, text: str, limit_kb: int) -> str:
        """Force truncate to absolute limit."""
        limit_bytes = limit_kb * 1024
        text_bytes = text.encode('utf-8')

        if len(text_bytes) <= limit_bytes:
            return text

        marker = "\n\n[TRUNCATED - ABSOLUTE LIMIT]"
        marker_bytes = marker.encode('utf-8')
        available = limit_bytes - len(marker_bytes)

        truncated = text_bytes[:available].decode('utf-8', errors='ignore')
        return truncated + marker

    async def handle_memory_request_async(
        self,
        ci_name: str,
        request: str,
        callback = None
    ) -> None:
        """
        Handle async memory request from hooks.

        Non-blocking - fulfills in background.
        """
        request_id = f"{ci_name}_{datetime.now().timestamp()}"
        self.pending_requests[request_id] = {
            'status': 'pending',
            'request': request
        }

        try:
            # Process in background
            asyncio.create_task(
                self._fulfill_memory_request(request_id, ci_name, request, callback)
            )
        except Exception as e:
            logger.error(f"Failed to create async task: {e}")

    async def _fulfill_memory_request(
        self,
        request_id: str,
        ci_name: str,
        request: str,
        callback = None
    ):
        """Fulfill memory request in background."""
        try:
            await asyncio.sleep(0.1)  # Simulate processing

            # Get memories for request
            context = {'objective': request}
            memories = await self._fetch_limited_memories(ci_name, context)

            # Create digest
            digest = get_memory_digest(
                memories,
                context,
                memory_requests=[request]
            )

            # Update status
            self.pending_requests[request_id] = {
                'status': 'complete',
                'result': digest
            }

            # Call callback if provided
            if callback:
                callback(digest)

        except Exception as e:
            logger.error(f"Memory request failed: {e}")
            self.pending_requests[request_id] = {
                'status': 'error',
                'error': str(e)
            }


# Singleton pipeline
_pipeline = MemoryPipeline()


async def process_through_pipeline(
    ci_name: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Process message through memory pipeline.

    This is the main entry point for the Claude handler.
    """
    return await _pipeline.process_for_claude(ci_name, message, context)


async def request_memory_async(ci_name: str, request: str, callback = None):
    """
    Request memory asynchronously (for hooks).
    """
    await _pipeline.handle_memory_request_async(ci_name, request, callback)


if __name__ == "__main__":
    # Test pipeline
    import asyncio

    async def test():
        print("Memory Pipeline Test\n")

        # Test message
        message = "Help me fix the memory overflow in Engram integration"

        # Test context
        context = {
            'recent_keywords': ['memory', 'overflow', 'engram']
        }

        # Process through pipeline
        result = await process_through_pipeline(
            "TestCI",
            message,
            context
        )

        print(result)
        print(f"\nSize: {len(result.encode('utf-8'))} bytes")
        print(f"Under 128KB: {len(result.encode('utf-8')) <= 128 * 1024}")

    asyncio.run(test())