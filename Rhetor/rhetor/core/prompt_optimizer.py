#!/usr/bin/env python3
"""
Rhetor Prompt Optimizer

Optimizes and packages prompts with hard 64KB limit.
Includes summary pass and truncation fallback.
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """
    Optimizes prompts for CI consumption.

    Features:
    - Combines sundown notes, task, and Apollo digest
    - Summary pass if over 64KB
    - Truncation with [TRUNCATED] marker
    - Preserves critical information
    """

    # Maximum output size (64KB)
    MAX_SIZE_BYTES = 64 * 1024

    # Priority sections (preserve these first)
    PRIORITY_SECTIONS = [
        'todo_list',      # CI's todos are critical
        'current_task',   # What to do now
        'context_notes',  # CI's own context
        'memory_requests' # What CI needs
    ]

    def __init__(self):
        self.summary_cache = {}

    def optimize_prompt(
        self,
        sundown_notes: Optional[str],
        current_task: str,
        apollo_digest: Optional[str],
        feedback: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Optimize and package prompt within 64KB limit.

        Args:
            sundown_notes: CI's sundown from previous turn
            current_task: New task/message from user
            apollo_digest: Memory digest from Apollo
            feedback: CI feedback on information volume

        Returns:
            Optimized prompt (<64KB)
        """
        # Build initial prompt
        prompt = self._build_prompt(sundown_notes, current_task, apollo_digest)

        # Check size
        prompt_bytes = prompt.encode('utf-8')
        if len(prompt_bytes) <= self.MAX_SIZE_BYTES:
            return prompt

        # Too large - try summary pass
        logger.info(f"Prompt too large ({len(prompt_bytes)} bytes), applying summary")
        summarized = self._summary_pass(sundown_notes, current_task, apollo_digest)

        # Check summarized size
        summary_bytes = summarized.encode('utf-8')
        if len(summary_bytes) <= self.MAX_SIZE_BYTES:
            return summarized

        # Still too large - truncate
        logger.warning(f"Summary still too large ({len(summary_bytes)} bytes), truncating")
        return self._truncate_prompt(summarized)

    def _build_prompt(
        self,
        sundown_notes: Optional[str],
        current_task: str,
        apollo_digest: Optional[str]
    ) -> str:
        """
        Build initial prompt structure.
        """
        sections = []

        # Header
        sections.append("# SUNRISE PROMPT")
        sections.append(f"<!-- Generated: {datetime.now().isoformat()} -->")
        sections.append("")

        # Section 1: Previous state (sundown notes)
        if sundown_notes:
            sections.append("## Your Previous State")
            sections.append(sundown_notes)
            sections.append("")

        # Section 2: Current task
        sections.append("## Current Task")
        sections.append(current_task)
        sections.append("")

        # Section 3: Memory context (Apollo digest)
        if apollo_digest:
            sections.append("## Memory Context")
            sections.append(apollo_digest)
            sections.append("")

        # Footer with guidance
        sections.append("## Guidance")
        sections.append("- Ask questions early and often")
        sections.append("- Include Memory Requests in your sundown")
        sections.append("- Provide feedback on information volume")
        sections.append("")

        return '\n'.join(sections)

    def _summary_pass(
        self,
        sundown_notes: Optional[str],
        current_task: str,
        apollo_digest: Optional[str]
    ) -> str:
        """
        Apply summary pass to reduce size.

        Strategy:
        1. Parse and extract critical elements
        2. Summarize verbose sections
        3. Preserve structure
        """
        sections = []

        # Header
        sections.append("# SUNRISE PROMPT (SUMMARIZED)")
        sections.append("")

        # Summarize sundown if present
        if sundown_notes:
            summary = self._summarize_sundown(sundown_notes)
            sections.append("## Previous State (Summary)")
            sections.append(summary)
            sections.append("")

        # Keep task as-is (usually brief)
        sections.append("## Current Task")
        sections.append(current_task[:2000] if len(current_task) > 2000 else current_task)
        sections.append("")

        # Summarize Apollo digest if present
        if apollo_digest:
            # Extract just the most relevant parts
            digest_summary = self._summarize_digest(apollo_digest)
            sections.append("## Memory Context (Key Points)")
            sections.append(digest_summary)
            sections.append("")

        # Minimal guidance
        sections.append("*Ask questions | Request memories | Provide feedback*")

        return '\n'.join(sections)

    def _summarize_sundown(self, sundown: str) -> str:
        """
        Summarize sundown notes while preserving critical info.
        """
        lines = sundown.split('\n')
        summary_parts = []

        # Extract todos (critical)
        todo_count = {'completed': 0, 'in_progress': 0, 'pending': 0}
        in_todo_section = False

        for line in lines:
            if '#### Todo List' in line:
                in_todo_section = True
            elif '####' in line and in_todo_section:
                in_todo_section = False
            elif in_todo_section:
                if '[x]' in line:
                    todo_count['completed'] += 1
                elif '[~]' in line:
                    todo_count['in_progress'] += 1
                elif '[ ]' in line:
                    todo_count['pending'] += 1

        summary_parts.append(
            f"Todos: {todo_count['completed']} done, "
            f"{todo_count['in_progress']} in progress, "
            f"{todo_count['pending']} pending"
        )

        # Extract context (first line only)
        for i, line in enumerate(lines):
            if '#### Context for Next Turn' in line and i + 1 < len(lines):
                context_line = lines[i + 1].strip()
                if context_line.startswith('-'):
                    context_line = context_line[1:].strip()
                if len(context_line) > 100:
                    context_line = context_line[:97] + "..."
                summary_parts.append(f"Context: {context_line}")
                break

        # Extract memory requests count
        memory_request_count = sum(1 for line in lines if line.strip().startswith('- Need'))
        if memory_request_count > 0:
            summary_parts.append(f"Memory requests: {memory_request_count} items")

        # Extract open questions count
        question_count = sum(1 for line in lines if '?' in line and line.strip().startswith('-'))
        if question_count > 0:
            summary_parts.append(f"Open questions: {question_count}")

        return '\n'.join(summary_parts)

    def _summarize_digest(self, digest: str) -> str:
        """
        Extract key points from Apollo digest.
        """
        lines = digest.split('\n')
        key_points = []

        # Look for section headers and take first item
        current_section = None
        for line in lines:
            if line.startswith('##'):
                current_section = line
                key_points.append(line)
            elif line.startswith('- ') and len(key_points) < 10:
                # Take first bullet from each section
                if current_section and current_section not in key_points[-1:]:
                    content = line[2:].strip()
                    if len(content) > 80:
                        content = content[:77] + "..."
                    key_points.append(f"  - {content}")

        return '\n'.join(key_points[:15])  # Max 15 lines

    def _truncate_prompt(self, prompt: str) -> str:
        """
        Truncate prompt to fit within 64KB with marker.
        """
        truncation_marker = "\n\n[TRUNCATED - Exceeded 64KB limit]"
        marker_bytes = truncation_marker.encode('utf-8')

        # Calculate available space
        available_bytes = self.MAX_SIZE_BYTES - len(marker_bytes)

        # Truncate
        prompt_bytes = prompt.encode('utf-8')
        if len(prompt_bytes) <= available_bytes:
            return prompt + truncation_marker

        # Truncate at character boundary
        truncated = prompt_bytes[:available_bytes].decode('utf-8', errors='ignore')

        # Try to truncate at section boundary
        section_markers = ['\n##', '\n###', '\n\n']
        for marker in section_markers:
            last_marker = truncated.rfind(marker)
            if last_marker > available_bytes * 0.8:  # Don't lose too much
                truncated = truncated[:last_marker]
                break

        return truncated + truncation_marker

    def estimate_size_adjustment(self, feedback: Dict[str, str]) -> float:
        """
        Estimate size adjustment based on feedback.

        Returns:
            Multiplier for target size (0.5 to 2.0)
        """
        rhetor_feedback = feedback.get('rhetor_prompt', 'just right')

        if rhetor_feedback == 'too much':
            return 0.8  # Reduce by 20%
        elif rhetor_feedback == 'too little':
            return 1.2  # Increase by 20%
        else:
            return 1.0  # No change


# Singleton instance
_optimizer = PromptOptimizer()


def optimize_prompt(
    sundown_notes: Optional[str],
    current_task: str,
    apollo_digest: Optional[str] = None,
    feedback: Optional[Dict[str, str]] = None
) -> str:
    """
    Optimize prompt for CI consumption.

    Convenience function using singleton optimizer.
    """
    return _optimizer.optimize_prompt(sundown_notes, current_task, apollo_digest, feedback)


def truncate_at_limit(text: str, limit_kb: int = 64) -> str:
    """
    Simple truncation utility.

    For any text that needs hard limit enforcement.
    """
    limit_bytes = limit_kb * 1024
    text_bytes = text.encode('utf-8')

    if len(text_bytes) <= limit_bytes:
        return text

    # Truncate with marker
    marker = "\n[TRUNCATED]"
    available = limit_bytes - len(marker.encode('utf-8'))
    truncated = text_bytes[:available].decode('utf-8', errors='ignore')

    # Clean truncation point
    last_newline = truncated.rfind('\n')
    if last_newline > available * 0.9:
        truncated = truncated[:last_newline]

    return truncated + marker


if __name__ == "__main__":
    # Test optimizer
    print("Rhetor Prompt Optimizer Test\n")

    # Sample sundown (verbose)
    sundown = """### SUNDOWN NOTES ###
#### Todo List
- [x] Implemented memory prioritizer
- [x] Created prompt optimizer
- [~] Testing with Greek Chorus
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Gather feedback

#### Context for Next Turn
- Working on: Memory overflow fix
- Key finding: 64KB limit prevents crashes
- Next step: Wire into Claude handler
- Warning: Must intercept all memory requests

#### Memory Requests for Next Turn
- Need examples of: async hook patterns
- Need context about: Claude handler integration points
- Need to understand: Greek Chorus initialization

#### Open Questions
- How to handle legacy code?
- Should we add circuit breakers?
- What about error recovery?

### END SUNDOWN ###"""

    # Sample task
    task = "Continue implementing the memory fix and test with Greek Chorus CIs"

    # Sample Apollo digest
    digest = """# APOLLO MEMORY DIGEST

## Requested Information
### Previous Implementation
The old system used JSON.parse without size checks...

## Task Context
- Memory management patterns observed
- Circuit breaker implementations available
- Hook system ready for integration

## Memory Index
- 47 additional memories available
"""

    # Test optimization
    optimized = optimize_prompt(sundown, task, digest)

    print(optimized)
    print(f"\nSize: {len(optimized.encode('utf-8'))} bytes")
    print(f"Within limit: {len(optimized.encode('utf-8')) <= 64 * 1024}")

    # Test with oversized input
    print("\n" + "="*60)
    print("Testing with oversized input...")

    huge_digest = digest * 50  # Make it huge
    optimized_huge = optimize_prompt(sundown, task, huge_digest)

    print(f"Original size: {len((sundown + task + huge_digest).encode('utf-8'))} bytes")
    print(f"Optimized size: {len(optimized_huge.encode('utf-8'))} bytes")
    print("Ends with truncation marker:", "[TRUNCATED" in optimized_huge)