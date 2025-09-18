#!/usr/bin/env python3
"""
CI Sundown/Sunrise Mechanism

This module provides utilities for CIs to prepare sundown notes for continuity
between turns. The sundown notes are mandatory and structured to ensure
smooth handoffs via Apollo/Rhetor.

Design Philosophy:
- CI owns its own continuity (sundown notes are for the CI, by the CI)
- Structured format ensures predictability
- Mandatory elements guarantee minimum continuity
- Fits within memory budget constraints (<32KB typical)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class CISundown:
    """Manages CI sundown notes for session continuity."""

    SUNDOWN_MARKER_START = "### SUNDOWN NOTES ###"
    SUNDOWN_MARKER_END = "### END SUNDOWN ###"

    def __init__(self, ci_name: str = None):
        """
        Initialize sundown manager for a CI.

        Args:
            ci_name: Name of the CI (e.g., 'Amy', 'Betty-ci')
        """
        self.ci_name = ci_name or os.environ.get('CI_NAME', 'unknown-ci')
        self.session_id = os.environ.get('CI_SESSION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))

    def create_sundown_notes(
        self,
        todo_list: List[Dict[str, str]],
        context_notes: str,
        open_questions: Optional[List[str]] = None,
        files_in_focus: Optional[List[str]] = None,
        custom_data: Optional[Dict] = None
    ) -> str:
        """
        Create structured sundown notes.

        Args:
            todo_list: List of todos with status (required)
                      Format: [{"task": "...", "status": "completed|pending|in_progress"}]
            context_notes: Context for next turn (required)
            open_questions: Questions to address next turn
            files_in_focus: Files/resources being worked on
            custom_data: Additional CI-specific data

        Returns:
            Formatted sundown notes as markdown string
        """
        if not todo_list:
            raise ValueError("Todo list is mandatory for sundown notes")
        if not context_notes:
            raise ValueError("Context notes are mandatory for sundown notes")

        # Build sundown notes
        notes = [self.SUNDOWN_MARKER_START]

        # Add metadata
        notes.append(f"<!-- CI: {self.ci_name} | Session: {self.session_id} | Time: {datetime.now().isoformat()} -->")
        notes.append("")

        # Todo List (mandatory)
        notes.append("#### Todo List")
        for todo in todo_list:
            status_char = {
                'completed': 'x',
                'in_progress': '~',
                'pending': ' '
            }.get(todo.get('status', 'pending'), ' ')
            task = todo.get('task', '')
            notes.append(f"- [{status_char}] {task}")
        notes.append("")

        # Context for Next Turn (mandatory)
        notes.append("#### Context for Next Turn")
        for line in context_notes.split('\n'):
            notes.append(f"- {line}" if line and not line.startswith('-') else line)
        notes.append("")

        # Open Questions (optional but recommended)
        if open_questions:
            notes.append("#### Open Questions")
            for question in open_questions:
                notes.append(f"- {question}")
            notes.append("")

        # Files/Resources in Focus (recommended)
        if files_in_focus:
            notes.append("#### Files/Resources in Focus")
            for file_path in files_in_focus:
                # Add brief description if available
                if isinstance(file_path, dict):
                    path = file_path.get('path', '')
                    desc = file_path.get('description', '')
                    notes.append(f"- {path} ({desc})" if desc else f"- {path}")
                else:
                    notes.append(f"- {file_path}")
            notes.append("")

        # Custom CI Data (optional)
        if custom_data:
            notes.append("#### CI State")
            notes.append("```json")
            notes.append(json.dumps(custom_data, indent=2))
            notes.append("```")
            notes.append("")

        notes.append(self.SUNDOWN_MARKER_END)

        return '\n'.join(notes)

    def validate_sundown_notes(self, content: str) -> Dict[str, Any]:
        """
        Validate that sundown notes meet requirements.

        Args:
            content: Content to validate

        Returns:
            Validation result with status and details
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'size_kb': len(content.encode('utf-8')) / 1024
        }

        # Check for markers
        if self.SUNDOWN_MARKER_START not in content:
            result['errors'].append("Missing sundown start marker")
            result['valid'] = False

        if self.SUNDOWN_MARKER_END not in content:
            result['errors'].append("Missing sundown end marker")
            result['valid'] = False

        # Check for mandatory sections
        if "#### Todo List" not in content:
            result['errors'].append("Missing mandatory Todo List section")
            result['valid'] = False
        elif content.count("- [ ]") + content.count("- [x]") + content.count("- [~]") == 0:
            result['errors'].append("Todo List appears to be empty")
            result['valid'] = False

        if "#### Context for Next Turn" not in content:
            result['errors'].append("Missing mandatory Context section")
            result['valid'] = False

        # Size checks
        if result['size_kb'] > 32:
            result['errors'].append(f"Sundown notes too large ({result['size_kb']:.1f}KB > 32KB)")
            result['valid'] = False
        elif result['size_kb'] > 24:
            result['warnings'].append(f"Sundown notes approaching size limit ({result['size_kb']:.1f}KB)")
        elif result['size_kb'] < 1:
            result['warnings'].append(f"Sundown notes seem too brief ({result['size_kb']:.1f}KB)")

        # Recommended sections
        if "#### Open Questions" not in content:
            result['warnings'].append("Missing recommended Open Questions section")

        if "#### Files/Resources in Focus" not in content:
            result['warnings'].append("Missing recommended Files/Resources section")

        return result

    def extract_sundown_notes(self, content: str) -> Optional[str]:
        """
        Extract sundown notes from larger content.

        Args:
            content: Content potentially containing sundown notes

        Returns:
            Extracted sundown notes or None if not found
        """
        start_idx = content.find(self.SUNDOWN_MARKER_START)
        if start_idx == -1:
            return None

        end_idx = content.find(self.SUNDOWN_MARKER_END, start_idx)
        if end_idx == -1:
            return None

        # Include the end marker in extraction
        end_idx += len(self.SUNDOWN_MARKER_END)

        return content[start_idx:end_idx]

    def parse_sundown_notes(self, content: str) -> Dict[str, Any]:
        """
        Parse sundown notes into structured data.

        Args:
            content: Sundown notes content

        Returns:
            Parsed data structure
        """
        notes = self.extract_sundown_notes(content)
        if not notes:
            return None

        lines = notes.split('\n')
        parsed = {
            'ci_name': self.ci_name,
            'todo_list': [],
            'context_notes': [],
            'open_questions': [],
            'files_in_focus': [],
            'custom_data': None
        }

        current_section = None
        in_json = False
        json_lines = []

        for line in lines:
            # Handle JSON blocks
            if line.strip() == '```json':
                in_json = True
                json_lines = []
                continue
            elif line.strip() == '```' and in_json:
                in_json = False
                if json_lines:
                    try:
                        parsed['custom_data'] = json.loads('\n'.join(json_lines))
                    except json.JSONDecodeError:
                        pass
                continue
            elif in_json:
                json_lines.append(line)
                continue

            # Detect sections
            if line.startswith("#### Todo List"):
                current_section = 'todo'
            elif line.startswith("#### Context for Next Turn"):
                current_section = 'context'
            elif line.startswith("#### Open Questions"):
                current_section = 'questions'
            elif line.startswith("#### Files/Resources"):
                current_section = 'files'
            elif line.startswith("#### CI State"):
                current_section = 'state'
            # Parse section content
            elif current_section and line.strip().startswith('- '):
                content = line.strip()[2:]  # Remove '- '

                if current_section == 'todo':
                    # Parse todo format: [x] or [ ] or [~]
                    if content.startswith('['):
                        status_char = content[1]
                        task = content[3:].strip()
                        status = {
                            'x': 'completed',
                            ' ': 'pending',
                            '~': 'in_progress'
                        }.get(status_char, 'pending')
                        parsed['todo_list'].append({'task': task, 'status': status})
                elif current_section == 'context':
                    parsed['context_notes'].append(content)
                elif current_section == 'questions':
                    parsed['open_questions'].append(content)
                elif current_section == 'files':
                    # Parse file format (might include description)
                    if ' (' in content and content.endswith(')'):
                        path = content[:content.rindex(' (')]
                        desc = content[content.rindex(' (') + 2:-1]
                        parsed['files_in_focus'].append({'path': path, 'description': desc})
                    else:
                        parsed['files_in_focus'].append({'path': content, 'description': ''})

        # Convert context notes list to string
        if parsed['context_notes']:
            parsed['context_notes'] = '\n'.join(parsed['context_notes'])

        return parsed


# Convenience function for CIs to use
def prepare_sundown(
    todo_list: List[Dict[str, str]],
    context_notes: str,
    open_questions: Optional[List[str]] = None,
    files_in_focus: Optional[List[str]] = None,
    custom_data: Optional[Dict] = None,
    ci_name: Optional[str] = None
) -> str:
    """
    Convenience function to prepare sundown notes.

    This is the primary function CIs should call at the end of their turn.

    Example:
        sundown = prepare_sundown(
            todo_list=[
                {"task": "Implement memory digest", "status": "in_progress"},
                {"task": "Test with Apollo", "status": "pending"}
            ],
            context_notes="Working on memory overflow fix. Next: Apollo integration.",
            open_questions=["Should digest include code snippets?"],
            files_in_focus=["/Engram/memory_manager.py"]
        )
    """
    manager = CISundown(ci_name)
    return manager.create_sundown_notes(
        todo_list, context_notes, open_questions, files_in_focus, custom_data
    )


if __name__ == "__main__":
    # Example usage and testing
    print("CI Sundown Module - Example Usage\n")

    # Create example sundown notes
    example_todos = [
        {"task": "Analyzed memory overflow issue", "status": "completed"},
        {"task": "Designed new memory architecture", "status": "completed"},
        {"task": "Implement Apollo digest system", "status": "in_progress"},
        {"task": "Create Rhetor prompt optimizer", "status": "pending"},
        {"task": "Test new memory pipeline", "status": "pending"}
    ]

    example_context = """Working on: Fixing Engram memory overflow
Key insight: Must limit data to 128KB total
Next step: Implement Apollo's digest function
Watch out for: Cache accumulation in EngramService"""

    example_questions = [
        "Should digest include code snippets?",
        "How to handle multi-CI coordination?",
        "What's the best format for memory indices?"
    ]

    example_files = [
        {"path": "/Engram/engram/core/memory_manager.py", "description": "main logic"},
        {"path": "/Hephaestus/ui/scripts/engram/engram-service.js", "description": "overflow location"},
        {"path": "/Apollo/apollo/core/attention.py", "description": "digest implementation"}
    ]

    # Generate sundown notes
    sundown = prepare_sundown(
        todo_list=example_todos,
        context_notes=example_context,
        open_questions=example_questions,
        files_in_focus=example_files,
        ci_name="Amy"
    )

    print(sundown)
    print("\n" + "="*60 + "\n")

    # Validate the notes
    manager = CISundown("Amy")
    validation = manager.validate_sundown_notes(sundown)

    print("Validation Results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Size: {validation['size_kb']:.1f}KB")
    if validation['errors']:
        print("  Errors:")
        for error in validation['errors']:
            print(f"    - {error}")
    if validation['warnings']:
        print("  Warnings:")
        for warning in validation['warnings']:
            print(f"    - {warning}")