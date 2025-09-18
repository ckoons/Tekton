#!/usr/bin/env python3
"""
Enhanced CI Sundown/Sunrise Mechanism

Improvements:
- Template on validation failure
- Feedback mechanism for sizing
- Memory requests for targeted retrieval
- Question encouragement system
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.ci_tools.sundown import CISundown as BaseSundown


class EnhancedCISundown(BaseSundown):
    """Enhanced sundown manager with feedback and memory requests."""

    # Track validation failures per CI
    validation_failures = {}

    SUNDOWN_TEMPLATE = """### SUNDOWN NOTES ###
<!-- CI: {ci_name} | Session: {session_id} | Time: {timestamp} -->

#### Todo List
<!-- Mark completed [x], in-progress [~], or pending [ ] -->
- [ ] [REQUIRED: Add your todo items here]
- [ ] [Add as many as needed]

#### Context for Next Turn
<!-- REQUIRED: What are you working on? What did you discover? What's next? -->
- Working on: [REQUIRED: Current focus]
- Key findings: [What did you learn?]
- Next step: [REQUIRED: What needs to be done next?]
- Watch for: [Any warnings or gotchas?]

#### Memory Requests for Next Turn
<!-- What specific memories would help you continue? Be specific! -->
- Need examples of: [what patterns or implementations?]
- Need context about: [what decisions or discussions?]
- Need to understand: [what concepts or approaches?]

#### Open Questions
<!-- What questions need answers? -->
- [Questions that need clarification]
- [Design decisions to be made]

#### Files/Resources in Focus
<!-- What files are you actively working with? -->
- /path/to/file (description of relevance)

#### Feedback on Information Volume
<!-- Help us tune the system! -->
- Apollo digest: [too much | just right | too little]
- Rhetor prompt: [too much | just right | too little]
- Overall context: [overwhelming | adequate | need more]

### END SUNDOWN ###

INSTRUCTIONS:
1. Replace all [BRACKETED] sections with your actual content
2. Remove these instructions before submitting
3. Ensure Todo List and Context sections are meaningful
4. Be specific in Memory Requests to get relevant information"""

    def get_failure_template(self, ci_name: str, failure_count: int) -> str:
        """
        Get appropriate response for validation failure.

        Args:
            ci_name: Name of the CI
            failure_count: Number of times validation has failed

        Returns:
            Template or feedback request
        """
        if failure_count == 1:
            # First failure: provide template
            return f"""
═══════════════════════════════════════════════════════════════════════
                    SUNDOWN VALIDATION FAILED - TEMPLATE PROVIDED
═══════════════════════════════════════════════════════════════════════

Your sundown notes didn't meet requirements. Please use this template:

{self.SUNDOWN_TEMPLATE.format(
    ci_name=ci_name,
    session_id=self.session_id,
    timestamp=datetime.now().isoformat()
)}

Remember: Sundown is MANDATORY for continuity. Without it, you'll lose context!
═══════════════════════════════════════════════════════════════════════"""

        elif failure_count >= 2:
            # Second+ failure: ask why
            return f"""
═══════════════════════════════════════════════════════════════════════
                    SUNDOWN VALIDATION FAILED AGAIN - NEED FEEDBACK
═══════════════════════════════════════════════════════════════════════

{ci_name}, your sundown notes failed validation twice.

Please help us understand:
1. What's confusing about the sundown format?
2. What makes it difficult to provide?
3. Would a different format work better?
4. Are you having technical issues?

Your feedback helps us improve the system for all CIs.

For now, please provide at minimum:
- What you were working on
- What should happen next turn
- Any questions you have

Even brief notes are better than none!
═══════════════════════════════════════════════════════════════════════"""

    def validate_sundown_notes_with_feedback(self, content: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Validate sundown notes and provide feedback on failure.

        Args:
            content: Sundown notes to validate

        Returns:
            Tuple of (validation_result, feedback_message)
        """
        result = self.validate_sundown_notes(content)

        if not result['valid']:
            # Track failures
            if self.ci_name not in self.validation_failures:
                self.validation_failures[self.ci_name] = 0
            self.validation_failures[self.ci_name] += 1

            failure_count = self.validation_failures[self.ci_name]
            feedback = self.get_failure_template(self.ci_name, failure_count)

            return result, feedback
        else:
            # Reset failure count on success
            if self.ci_name in self.validation_failures:
                self.validation_failures[self.ci_name] = 0

            return result, None

    def create_enhanced_sundown_notes(
        self,
        todo_list: List[Dict[str, str]],
        context_notes: str,
        memory_requests: Optional[List[str]] = None,
        open_questions: Optional[List[str]] = None,
        files_in_focus: Optional[List[str]] = None,
        feedback: Optional[Dict[str, str]] = None,
        custom_data: Optional[Dict] = None
    ) -> str:
        """
        Create enhanced sundown notes with memory requests and feedback.

        Args:
            todo_list: List of todos with status
            context_notes: Context for next turn
            memory_requests: Specific memories needed next turn
            open_questions: Questions to address
            files_in_focus: Files being worked on
            feedback: Feedback on information volume
            custom_data: Additional CI-specific data

        Returns:
            Formatted sundown notes
        """
        if not todo_list:
            raise ValueError("Todo list is mandatory")
        if not context_notes:
            raise ValueError("Context notes are mandatory")

        notes = [self.SUNDOWN_MARKER_START]
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

        # Memory Requests (recommended for better relevance)
        if memory_requests:
            notes.append("#### Memory Requests for Next Turn")
            for request in memory_requests:
                notes.append(f"- {request}")
            notes.append("")

        # Open Questions
        if open_questions:
            notes.append("#### Open Questions")
            for question in open_questions:
                notes.append(f"- {question}")
            notes.append("")

        # Files/Resources in Focus
        if files_in_focus:
            notes.append("#### Files/Resources in Focus")
            for file_path in files_in_focus:
                if isinstance(file_path, dict):
                    path = file_path.get('path', '')
                    desc = file_path.get('description', '')
                    notes.append(f"- {path} ({desc})" if desc else f"- {path}")
                else:
                    notes.append(f"- {file_path}")
            notes.append("")

        # Feedback on Information Volume
        if feedback:
            notes.append("#### Feedback on Information Volume")
            apollo = feedback.get('apollo_digest', 'not provided')
            rhetor = feedback.get('rhetor_prompt', 'not provided')
            overall = feedback.get('overall_context', 'not provided')
            notes.append(f"- Apollo digest: {apollo}")
            notes.append(f"- Rhetor prompt: {rhetor}")
            notes.append(f"- Overall context: {overall}")
            notes.append("")

        # Custom CI State
        if custom_data:
            notes.append("#### CI State")
            notes.append("```json")
            notes.append(json.dumps(custom_data, indent=2))
            notes.append("```")
            notes.append("")

        notes.append(self.SUNDOWN_MARKER_END)
        return '\n'.join(notes)

    def parse_enhanced_sundown_notes(self, content: str) -> Dict[str, Any]:
        """
        Parse enhanced sundown notes including memory requests and feedback.

        Args:
            content: Sundown notes content

        Returns:
            Parsed data with additional fields
        """
        parsed = self.parse_sundown_notes(content)
        if not parsed:
            return None

        # Add enhanced fields
        parsed['memory_requests'] = []
        parsed['feedback'] = {}

        lines = content.split('\n')
        current_section = None

        for line in lines:
            # Detect new sections
            if line.startswith("#### Memory Requests"):
                current_section = 'memory_requests'
            elif line.startswith("#### Feedback on Information"):
                current_section = 'feedback'
            # Parse section content
            elif current_section == 'memory_requests' and line.strip().startswith('- '):
                request = line.strip()[2:]
                parsed['memory_requests'].append(request)
            elif current_section == 'feedback' and line.strip().startswith('- '):
                content = line.strip()[2:]
                if 'Apollo digest:' in content:
                    parsed['feedback']['apollo_digest'] = content.split(':', 1)[1].strip()
                elif 'Rhetor prompt:' in content:
                    parsed['feedback']['rhetor_prompt'] = content.split(':', 1)[1].strip()
                elif 'Overall context:' in content:
                    parsed['feedback']['overall_context'] = content.split(':', 1)[1].strip()

        return parsed

    def save_to_working_memory(self, ci_name: str, sundown_data: Dict[str, Any]) -> bool:
        """
        Save sundown data to /tmp for working memory.

        Args:
            ci_name: CI name
            sundown_data: Parsed sundown data

        Returns:
            Success boolean
        """
        try:
            # Create directory for CI
            sundown_path = Path(f"/tmp/sundown/{ci_name}")
            sundown_path.mkdir(parents=True, exist_ok=True)

            # Save as latest.json
            latest_file = sundown_path / "latest.json"
            with open(latest_file, 'w') as f:
                json.dump(sundown_data, f, indent=2)

            # Also save timestamped version
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_file = sundown_path / f"{timestamp}.json"
            with open(timestamped_file, 'w') as f:
                json.dump(sundown_data, f, indent=2)

            print(f"[Sundown] Saved to working memory: {latest_file}")
            return True

        except Exception as e:
            print(f"[Sundown] Failed to save to working memory: {e}")
            return False


class QuestionEncourager:
    """Encourages CIs to ask questions, especially at task start."""

    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.turn_count = 0
        self.questions_asked = []
        self.task_started = False

    def check_output_for_questions(self, output: str) -> List[str]:
        """
        Extract questions from CI output.

        Args:
            output: CI output to analyze

        Returns:
            List of questions found
        """
        questions = []
        lines = output.split('\n')

        for line in lines:
            # Look for question marks
            if '?' in line:
                questions.append(line.strip())
            # Look for "need to know" patterns
            elif any(phrase in line.lower() for phrase in [
                'need to know', 'need to understand', 'wondering',
                'not sure', 'unclear', 'help me understand'
            ]):
                questions.append(line.strip())

        return questions

    def generate_encouragement(self, has_questions: bool, turn_count: int) -> Optional[str]:
        """
        Generate encouragement for asking questions.

        Args:
            has_questions: Whether CI asked questions
            turn_count: Current turn number

        Returns:
            Encouragement message or None
        """
        if turn_count == 1 and not has_questions:
            return """
💡 TIP: Consider asking questions before diving in! For example:
- What existing patterns should I follow?
- Are there similar implementations to review?
- What constraints or requirements should I consider?
- What has been tried before?

Taking a moment to gather context often leads to better solutions."""

        elif turn_count == 2 and not has_questions:
            return """
💡 REMINDER: Questions help you avoid rework! Even simple questions like:
- "Show me related code"
- "What errors have occurred here before?"
- "What's the preferred approach?"

Your Memory Requests in sundown will get you targeted information next turn."""

        elif has_questions and turn_count <= 3:
            return "✓ Great questions! These will help Apollo provide targeted memories."

        return None


class FeedbackCollector:
    """Collects feedback on information volume for system tuning."""

    def __init__(self):
        self.feedback_history = []
        self.adjustment_factors = {
            'apollo_size': 1.0,  # Multiplier for digest size
            'rhetor_size': 1.0,  # Multiplier for prompt size
            'relevance_threshold': 0.3  # Minimum relevance score
        }

    def process_feedback(self, feedback: Dict[str, str]) -> Dict[str, float]:
        """
        Process feedback and adjust factors.

        Args:
            feedback: Feedback from sundown notes

        Returns:
            Updated adjustment factors
        """
        self.feedback_history.append({
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback
        })

        # Adjust based on feedback
        apollo = feedback.get('apollo_digest', 'just right')
        rhetor = feedback.get('rhetor_prompt', 'just right')

        # Apollo adjustments
        if apollo == 'too much':
            self.adjustment_factors['apollo_size'] *= 0.8
            self.adjustment_factors['relevance_threshold'] += 0.05
        elif apollo == 'too little':
            self.adjustment_factors['apollo_size'] *= 1.2
            self.adjustment_factors['relevance_threshold'] -= 0.05

        # Rhetor adjustments
        if rhetor == 'too much':
            self.adjustment_factors['rhetor_size'] *= 0.8
        elif rhetor == 'too little':
            self.adjustment_factors['rhetor_size'] *= 1.2

        # Keep factors in reasonable bounds
        self.adjustment_factors['apollo_size'] = max(0.5, min(2.0, self.adjustment_factors['apollo_size']))
        self.adjustment_factors['rhetor_size'] = max(0.5, min(2.0, self.adjustment_factors['rhetor_size']))
        self.adjustment_factors['relevance_threshold'] = max(0.1, min(0.6, self.adjustment_factors['relevance_threshold']))

        return self.adjustment_factors

    def get_size_targets(self) -> Dict[str, int]:
        """
        Get target sizes based on feedback.

        Returns:
            Target sizes in KB
        """
        return {
            'apollo_digest_kb': int(48 * self.adjustment_factors['apollo_size']),  # Base 48KB
            'rhetor_prompt_kb': int(48 * self.adjustment_factors['rhetor_size']),  # Base 48KB
            'relevance_threshold': self.adjustment_factors['relevance_threshold']
        }

    def generate_tuning_report(self) -> str:
        """
        Generate a report on system tuning.

        Returns:
            Tuning report as string
        """
        recent_feedback = self.feedback_history[-10:] if len(self.feedback_history) > 10 else self.feedback_history

        # Count feedback types
        apollo_feedback = {'too much': 0, 'just right': 0, 'too little': 0}
        rhetor_feedback = {'too much': 0, 'just right': 0, 'too little': 0}

        for entry in recent_feedback:
            fb = entry['feedback']
            apollo = fb.get('apollo_digest', 'just right')
            rhetor = fb.get('rhetor_prompt', 'just right')
            apollo_feedback[apollo] += 1
            rhetor_feedback[rhetor] += 1

        targets = self.get_size_targets()

        return f"""
SYSTEM TUNING REPORT
====================
Recent Feedback (last {len(recent_feedback)} turns):

Apollo Digest:
  Too much: {apollo_feedback['too much']}
  Just right: {apollo_feedback['just right']}
  Too little: {apollo_feedback['too little']}
  Current target: {targets['apollo_digest_kb']}KB

Rhetor Prompt:
  Too much: {rhetor_feedback['too much']}
  Just right: {rhetor_feedback['just right']}
  Too little: {rhetor_feedback['too little']}
  Current target: {targets['rhetor_prompt_kb']}KB

Relevance Threshold: {targets['relevance_threshold']:.2f}

Adjustments:
  Apollo size factor: {self.adjustment_factors['apollo_size']:.2f}x
  Rhetor size factor: {self.adjustment_factors['rhetor_size']:.2f}x
"""


# Global feedback collector (shared across sessions)
_feedback_collector = FeedbackCollector()


def prepare_enhanced_sundown(
    todo_list: List[Dict[str, str]],
    context_notes: str,
    memory_requests: Optional[List[str]] = None,
    open_questions: Optional[List[str]] = None,
    files_in_focus: Optional[List[str]] = None,
    feedback: Optional[Dict[str, str]] = None,
    ci_name: Optional[str] = None
) -> str:
    """
    Prepare enhanced sundown notes with memory requests and feedback.

    Example:
        sundown = prepare_enhanced_sundown(
            todo_list=[{"task": "Implement feature", "status": "completed"}],
            context_notes="Working on memory management",
            memory_requests=[
                "Need examples of memory pooling",
                "Need context about previous OOM issues"
            ],
            feedback={
                'apollo_digest': 'too much',
                'rhetor_prompt': 'just right',
                'overall_context': 'adequate'
            }
        )
    """
    manager = EnhancedCISundown(ci_name)

    # Process feedback if provided
    if feedback:
        _feedback_collector.process_feedback(feedback)

    return manager.create_enhanced_sundown_notes(
        todo_list, context_notes, memory_requests,
        open_questions, files_in_focus, feedback, None
    )


if __name__ == "__main__":
    # Test enhanced features
    print("Enhanced Sundown System Test\n")

    # Test with memory requests and feedback
    sundown = prepare_enhanced_sundown(
        todo_list=[
            {"task": "Analyzed requirements", "status": "completed"},
            {"task": "Started implementation", "status": "in_progress"}
        ],
        context_notes="Working on Apollo prioritization. Need relevance algorithm.",
        memory_requests=[
            "Need examples of: relevance scoring algorithms",
            "Need context about: previous prioritization attempts",
            "Need to understand: catastrophe theory application"
        ],
        feedback={
            'apollo_digest': 'too much',
            'rhetor_prompt': 'just right',
            'overall_context': 'adequate'
        },
        ci_name="TestCI"
    )

    print(sundown)
    print("\n" + "="*60)

    # Test validation failure handling
    manager = EnhancedCISundown("TestCI")

    # First failure
    bad_sundown = "This is not valid sundown"
    result, feedback = manager.validate_sundown_notes_with_feedback(bad_sundown)
    if feedback:
        print("\nFirst Failure Response:")
        print(feedback[:500] + "...")

    # Second failure
    result, feedback = manager.validate_sundown_notes_with_feedback(bad_sundown)
    if feedback:
        print("\nSecond Failure Response:")
        print(feedback[:500] + "...")

    # Test feedback system
    print("\n" + "="*60)
    print(_feedback_collector.generate_tuning_report())