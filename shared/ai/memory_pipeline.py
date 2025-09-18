#!/usr/bin/env python3
"""
Memory Pipeline for Claude Handler

Integrates Apollo and Rhetor to process all memory before Claude.
Enforces 64KB limits and prevents direct Engram access.
"""

import sys
import asyncio
import json
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
            Optimized prompt ready for Claude (<533KB working memory)
        """
        logger.info(f"Processing message for {ci_name} through memory pipeline")

        # Initialize working memory
        from shared.ai.working_memory import get_working_memory
        working_mem = get_working_memory(ci_name)

        # Load sundown notes into working memory
        working_mem.load_sundown_notes()
        working_mem.set_current_task(message)

        # Step 1: Get sundown notes if available
        sundown_notes = None
        memory_requests = None

        if working_mem.sundown_context:
            # Use sundown from working memory
            sundown_notes = json.dumps(working_mem.sundown_context, indent=2)
            memory_requests = working_mem.sundown_context.get('memory_requests', [])

        # Step 2: Get relevant memories through Apollo
        apollo_digest = await self._get_apollo_digest(
            ci_name,
            message,
            context,
            memory_requests
        )

        # Set Apollo digest in working memory
        working_mem.set_apollo_digest(apollo_digest)

        # Step 3: Optimize through Rhetor
        optimized_prompt = self._optimize_with_rhetor(
            sundown_notes,
            message,
            apollo_digest
        )

        # Step 4: Build full working memory context
        # Use working memory's get_context_prompt which handles all size limits
        full_context = working_mem.get_context_prompt()

        # Step 5: Final size check (should be under 533KB)
        context_bytes = full_context.encode('utf-8')
        if len(context_bytes) > 533 * 1024:
            logger.warning(f"Context still too large ({len(context_bytes)} bytes), forcing truncation")
            full_context = self._force_truncate(full_context, 533)

        logger.info(f"Pipeline complete: {len(context_bytes)} bytes")
        return full_context

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
        Fetch LIMITED memories from ESR system.

        Connects to real Engram storage with strict limits.
        """
        memories = []

        try:
            # Import ESR system
            from Engram.engram.core.storage.unified_interface import ESRMemorySystem
            from Engram.engram.core.storage.cognitive_workflows import CognitiveWorkflows

            # Initialize with strict limits
            esr = ESRMemorySystem()
            workflows = CognitiveWorkflows()

            # Set hard limits for safety
            MAX_ITEMS = 20
            MAX_SIZE_KB = 100  # 100KB max from Engram (before Apollo)

            # Try cognitive workflow first for intelligent retrieval
            try:
                # Get task-relevant thoughts
                thoughts = await workflows.retrieve_thoughts(
                    context=context.get('objective', ''),
                    max_results=10
                )

                # Convert thoughts to memory format
                for thought in thoughts[:MAX_ITEMS]:
                    memories.append({
                        'content': thought.get('content', ''),
                        'type': 'thought',
                        'timestamp': thought.get('timestamp', ''),
                        'relevance': thought.get('relevance', 0.5)
                    })

            except Exception as e:
                logger.debug(f"Cognitive workflow not available: {e}")

            # Fallback to ESR query
            if not memories:
                try:
                    result = await esr.query_memories(
                        query=context.get('objective', ''),
                        filters={
                            'ci_name': ci_name,
                            'limit': MAX_ITEMS,
                            'recency': '7d'  # Last 7 days
                        }
                    )

                    if isinstance(result, dict) and 'memories' in result:
                        memories = result['memories'][:MAX_ITEMS]
                    elif isinstance(result, list):
                        memories = result[:MAX_ITEMS]

                except Exception as e:
                    logger.debug(f"ESR query failed: {e}")

            # If still no memories, try storage service
            if not memories:
                try:
                    from Engram.engram.core.storage_service import StorageService
                    storage = StorageService()

                    # Get recent memories for CI
                    stored = storage.get_memories(ci_name, limit=MAX_ITEMS)
                    if stored:
                        memories = stored

                except Exception as e:
                    logger.debug(f"Storage service failed: {e}")

            # Size check - ensure we don't return too much
            total_size = sum(len(str(m)) for m in memories)
            if total_size > MAX_SIZE_KB * 1024:
                # Truncate to size limit
                truncated = []
                current_size = 0
                for memory in memories:
                    mem_size = len(str(memory))
                    if current_size + mem_size > MAX_SIZE_KB * 1024:
                        break
                    truncated.append(memory)
                    current_size += mem_size

                logger.warning(f"Truncated memories from {len(memories)} to {len(truncated)}")
                memories = truncated

        except Exception as e:
            logger.error(f"Memory fetch failed completely: {e}")
            # Return empty rather than crash
            memories = []

        logger.info(f"Fetched {len(memories)} memories for {ci_name}")
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