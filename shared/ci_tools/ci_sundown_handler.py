#!/usr/bin/env python3
"""
CI Sundown Handler

Automatic sundown note generation for CI sessions.
This handler integrates with CI wrappers to ensure mandatory sundown notes.

Design:
- Monitors CI output for task completion signals
- Automatically prompts for sundown when appropriate
- Validates and stores sundown notes for Apollo/Rhetor
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.ci_tools.sundown import CISundown, prepare_sundown

class CISundownHandler:
    """Handles automatic sundown note generation for CI sessions."""

    def __init__(self, ci_name: str):
        """
        Initialize the sundown handler.

        Args:
            ci_name: Name of the CI
        """
        self.ci_name = ci_name
        self.sundown_manager = CISundown(ci_name)
        self.session_active = True
        self.current_todos = []
        self.context_accumulator = []
        self.files_accessed = set()

    def detect_task_completion(self, output: str) -> bool:
        """
        Detect if CI output indicates task completion.

        Args:
            output: CI output to analyze

        Returns:
            True if task appears complete
        """
        completion_markers = [
            "task complete",
            "finished implementing",
            "done with",
            "completed the",
            "that's all",
            "anything else",
            "ready for",
            "let me know if"
        ]

        output_lower = output.lower()
        return any(marker in output_lower for marker in completion_markers)

    def extract_todos_from_output(self, output: str) -> List[Dict[str, str]]:
        """
        Extract todo items from CI output.

        Looks for various todo formats:
        - [x] completed task
        - [ ] pending task
        - TODO: task
        - - [ ] task (GitHub style)

        Args:
            output: CI output to parse

        Returns:
            List of todo items
        """
        todos = []

        # Pattern 1: Checkbox format [x] or [ ]
        checkbox_pattern = r'\[([ x~])\]\s+(.+?)(?:\n|$)'
        for match in re.finditer(checkbox_pattern, output):
            status_char = match.group(1)
            task = match.group(2).strip()
            status = {
                'x': 'completed',
                ' ': 'pending',
                '~': 'in_progress'
            }.get(status_char, 'pending')
            todos.append({'task': task, 'status': status})

        # Pattern 2: TODO format
        todo_pattern = r'TODO:\s*(.+?)(?:\n|$)'
        for match in re.finditer(todo_pattern, output, re.IGNORECASE):
            task = match.group(1).strip()
            todos.append({'task': task, 'status': 'pending'})

        # Pattern 3: Numbered lists that look like tasks
        numbered_pattern = r'^\d+\.\s+(\w+ing\s+.+?)(?:\n|$)'
        for match in re.finditer(numbered_pattern, output, re.MULTILINE):
            task = match.group(1).strip()
            # Only add if it looks like an action item (starts with verb+ing)
            if any(task.lower().startswith(v) for v in
                   ['implement', 'creat', 'fix', 'add', 'remov', 'updat', 'test', 'debug']):
                todos.append({'task': task, 'status': 'pending'})

        return todos

    def extract_context_from_output(self, output: str) -> str:
        """
        Extract context information from CI output.

        Looks for:
        - What was worked on
        - Key insights or findings
        - Next steps mentioned
        - Warnings or important notes

        Args:
            output: CI output to parse

        Returns:
            Context notes string
        """
        context_parts = []

        # Look for "Working on" patterns
        working_pattern = r'(?:working on|implementing|fixing|debugging):\s*(.+?)(?:\n|$)'
        for match in re.finditer(working_pattern, output, re.IGNORECASE):
            context_parts.append(f"Working on: {match.group(1).strip()}")

        # Look for "Next step" patterns
        next_pattern = r'(?:next step|next|then|should|will):\s*(.+?)(?:\n|$)'
        for match in re.finditer(next_pattern, output, re.IGNORECASE):
            context_parts.append(f"Next: {match.group(1).strip()}")

        # Look for key insights
        insight_pattern = r'(?:found|discovered|realized|issue is|problem is|root cause):\s*(.+?)(?:\n|$)'
        for match in re.finditer(insight_pattern, output, re.IGNORECASE):
            context_parts.append(f"Finding: {match.group(1).strip()}")

        # If no specific patterns found, take the last substantive paragraph
        if not context_parts:
            paragraphs = [p.strip() for p in output.split('\n\n') if len(p.strip()) > 50]
            if paragraphs:
                context_parts.append(paragraphs[-1][:200])  # Last paragraph, truncated

        return '\n'.join(context_parts) if context_parts else "Continued work on assigned tasks"

    def extract_files_from_output(self, output: str) -> List[str]:
        """
        Extract file paths mentioned in CI output.

        Args:
            output: CI output to parse

        Returns:
            List of file paths
        """
        files = set()

        # Pattern 1: Explicit file paths
        file_pattern = r'(?:/[\w\-\.]+)+/[\w\-\.]+\.\w+'
        for match in re.finditer(file_pattern, output):
            files.add(match.group(0))

        # Pattern 2: Relative paths with extensions
        relative_pattern = r'(?:[\w\-\.]+/)+[\w\-\.]+\.\w+'
        for match in re.finditer(relative_pattern, output):
            files.add(match.group(0))

        # Pattern 3: File references in backticks
        backtick_pattern = r'`([^`]+\.\w+)`'
        for match in re.finditer(backtick_pattern, output):
            files.add(match.group(1))

        return list(files)

    def generate_sundown_prompt(self) -> str:
        """
        Generate a prompt asking the CI to create sundown notes.

        Returns:
            Prompt string
        """
        return """
Please prepare your mandatory sundown notes for session continuity.

Include:
1. Todo list with status (completed/in_progress/pending)
2. Context notes for your next turn
3. Any open questions
4. Key files you're working with

Use the format:
### SUNDOWN NOTES ###
#### Todo List
- [x] Completed task
- [~] In progress task
- [ ] Pending task

#### Context for Next Turn
- What you're working on
- Key findings
- Next steps

#### Open Questions
- Questions to address

#### Files/Resources in Focus
- /path/to/file (description)
### END SUNDOWN ###
"""

    def prompt_for_sundown(self) -> Optional[str]:
        """
        Prompt the CI to generate sundown notes.

        Returns:
            Sundown notes or None if not provided
        """
        print("\n" + "="*60)
        print("SUNDOWN REQUIRED")
        print("="*60)
        print(self.generate_sundown_prompt())
        print("="*60 + "\n")

        # In a real implementation, this would wait for CI response
        # For now, return None to indicate manual sundown needed
        return None

    def auto_generate_sundown(self, session_output: str) -> str:
        """
        Automatically generate sundown notes from session output.

        Args:
            session_output: Complete session output

        Returns:
            Generated sundown notes
        """
        # Extract components from output
        todos = self.extract_todos_from_output(session_output)
        context = self.extract_context_from_output(session_output)
        files = self.extract_files_from_output(session_output)

        # If no todos found, create a default one
        if not todos:
            todos = [{"task": "Continue current work", "status": "in_progress"}]

        # Generate sundown notes
        return prepare_sundown(
            todo_list=todos,
            context_notes=context,
            open_questions=["Review and confirm next steps"],
            files_in_focus=files if files else None,
            ci_name=self.ci_name
        )

    def validate_and_store_sundown(self, sundown_notes: str) -> Dict[str, Any]:
        """
        Validate and store sundown notes.

        Args:
            sundown_notes: Sundown notes to validate and store

        Returns:
            Validation result
        """
        # Validate
        validation = self.sundown_manager.validate_sundown_notes(sundown_notes)

        if validation['valid']:
            # Store in Engram (via file for now)
            storage_dir = Path(os.environ.get('TEKTON_ROOT', '.')) / 'engram' / 'sundown'
            storage_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = storage_dir / f"{self.ci_name}_{timestamp}.md"

            with open(filename, 'w') as f:
                f.write(sundown_notes)

            validation['stored_at'] = str(filename)

            # Also store parsed version for Apollo/Rhetor
            parsed = self.sundown_manager.parse_sundown_notes(sundown_notes)
            json_filename = storage_dir / f"{self.ci_name}_{timestamp}.json"
            with open(json_filename, 'w') as f:
                json.dump(parsed, f, indent=2)

        return validation

    def process_ci_output(self, output: str) -> Optional[Dict[str, Any]]:
        """
        Process CI output and handle sundown if appropriate.

        Args:
            output: CI output to process

        Returns:
            Sundown result if generated, None otherwise
        """
        # Check if sundown notes already present
        existing_sundown = self.sundown_manager.extract_sundown_notes(output)
        if existing_sundown:
            result = self.validate_and_store_sundown(existing_sundown)
            return {
                'action': 'extracted',
                'validation': result,
                'notes': existing_sundown
            }

        # Check if task appears complete
        if self.detect_task_completion(output):
            # Try to auto-generate
            auto_sundown = self.auto_generate_sundown(output)
            result = self.validate_and_store_sundown(auto_sundown)

            if result['valid']:
                return {
                    'action': 'auto_generated',
                    'validation': result,
                    'notes': auto_sundown
                }
            else:
                # Prompt for manual sundown
                return {
                    'action': 'prompt_required',
                    'validation': result,
                    'prompt': self.generate_sundown_prompt()
                }

        return None


def integrate_with_ci_wrapper(ci_name: str, wrapper_output_handler):
    """
    Integration function for CI wrappers.

    This function should be called by CI wrappers to add sundown handling.

    Args:
        ci_name: Name of the CI
        wrapper_output_handler: The wrapper's output handler function

    Returns:
        Enhanced output handler with sundown support
    """
    handler = CISundownHandler(ci_name)

    def enhanced_handler(output: str) -> str:
        # Process for sundown
        sundown_result = handler.process_ci_output(output)

        if sundown_result:
            if sundown_result['action'] == 'prompt_required':
                # Append prompt to output
                output += "\n\n" + sundown_result['prompt']
            elif sundown_result['action'] in ['extracted', 'auto_generated']:
                # Add confirmation
                output += f"\n\n✓ Sundown notes {'extracted' if sundown_result['action'] == 'extracted' else 'generated'} and stored"
                if sundown_result['validation'].get('warnings'):
                    output += "\n  Warnings: " + ", ".join(sundown_result['validation']['warnings'])

        # Call original handler
        return wrapper_output_handler(output)

    return enhanced_handler


if __name__ == "__main__":
    # Test the handler
    print("CI Sundown Handler - Test\n")

    handler = CISundownHandler("TestCI")

    # Test with sample output
    sample_output = """
I've completed the analysis of the memory overflow issue. Here's what I found:

The root cause is that Engram is sending massive JSON payloads (>4GB) to the Claude handler,
causing the Node.js process to run out of heap memory during JSON.parse().

TODO: Implement pagination for memory queries
TODO: Add cache eviction policies
[x] Analyzed the stack trace
[x] Identified the bottleneck in engram-service.js
[ ] Create Apollo digest system
[~] Testing memory limits

Working on: Fixing the memory overflow in Engram integration
Next step: Implement the Apollo digest function to limit memory to 64KB

Key files involved:
- /Engram/engram/core/memory_manager.py
- /Hephaestus/ui/scripts/engram/engram-service.js
"""

    # Test extraction
    todos = handler.extract_todos_from_output(sample_output)
    print("Extracted Todos:")
    for todo in todos:
        print(f"  - [{todo['status']}] {todo['task']}")

    print("\nExtracted Context:")
    context = handler.extract_context_from_output(sample_output)
    print(f"  {context}")

    print("\nExtracted Files:")
    files = handler.extract_files_from_output(sample_output)
    for f in files:
        print(f"  - {f}")

    print("\n" + "="*60)
    print("Auto-generated Sundown:")
    print("="*60)
    sundown = handler.auto_generate_sundown(sample_output)
    print(sundown)