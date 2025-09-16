"""
Rhetor Prompt Service
Composes prompts for CI turns with task instructions and history.
Maximum prompt size: 64KB
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptService:
    """
    Composes task prompts for CI turns.
    
    Rhetor's role is to create clear, contextual prompts that bridge
    between turns while maintaining task focus.
    """
    
    # Maximum prompt size in characters (approximately 64KB)
    MAX_PROMPT_SIZE = 65536
    
    # Prompt styles for different task types
    PROMPT_STYLES = {
        'analysis': 'analytical',
        'conversation': 'conversational',
        'coding': 'technical',
        'planning': 'strategic',
        'creative': 'creative',
        'default': 'balanced'
    }
    
    def __init__(self):
        self.turn_history = {}  # Simple in-memory history per CI
        
    def compose_prompt(
        self,
        ci_name: str,
        task: Dict[str, Any],
        previous_turn: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Compose a prompt for a CI's turn.
        
        Args:
            ci_name: Name of the CI
            task: Current task specification
            previous_turn: Summary of previous turn
            
        Returns:
            Formatted prompt string (≤64KB)
        """
        logger.info(f"Composing prompt for {ci_name}")
        
        # Determine prompt style
        task_type = task.get('type', 'default')
        style = self.PROMPT_STYLES.get(task_type, 'balanced')
        
        # Build prompt sections
        sections = []
        
        # Add role definition
        role = self._define_ci_role(ci_name, task)
        if role:
            sections.append(role)
        
        # Add task instructions
        instructions = self._format_task_instructions(task, style)
        sections.append(instructions)
        
        # Add previous turn context if available
        if previous_turn:
            turn_context = self._format_turn_context(previous_turn, style)
            if turn_context:
                sections.append(turn_context)
        
        # Add constraints and guidelines
        guidelines = self._add_guidelines(task, style)
        if guidelines:
            sections.append(guidelines)
        
        # Add output format specification
        output_spec = self._specify_output_format(task)
        if output_spec:
            sections.append(output_spec)
        
        # Combine sections
        prompt = self._combine_sections(sections, style)
        
        # Enforce size limit
        prompt = self._enforce_size_limit(prompt)
        
        # Store in history
        self._update_history(ci_name, task, prompt)
        
        logger.info(f"Composed {len(prompt)} char prompt for {ci_name}")
        return prompt
    
    def _define_ci_role(self, ci_name: str, task: Dict[str, Any]) -> Optional[str]:
        """Define the CI's role for this turn."""
        # Map CI names to roles
        ci_roles = {
            'apollo': "You are Apollo, the predictive orchestrator. Focus on coordination and foresight.",
            'athena': "You are Athena, the strategic analyst. Apply wisdom and strategic thinking.",
            'hermes': "You are Hermes, the messenger. Facilitate clear communication.",
            'rhetor': "You are Rhetor, the eloquent communicator. Craft clear, effective messages.",
            'ergon': "You are Ergon, the task executor. Focus on practical implementation.",
            'metis': "You are Metis, the wise counselor. Provide thoughtful guidance.",
            'harmonia': "You are Harmonia, ensuring harmony and balance in the system.",
            'prometheus': "You are Prometheus, bringing innovation and foresight.",
            'synthesis': "You are Synthesis, integrating diverse elements into coherent wholes.",
            'noesis': "You are Noesis, providing deep understanding and insight.",
            'sophia': "You are Sophia, embodying wisdom and knowledge.",
            'engram': "You are Engram, the memory keeper. Manage and retrieve information.",
            'numa': "You are Numa, the pattern recognizer. Identify patterns and connections.",
            'penia': "You are Penia, the resource optimizer. Maximize efficiency.",
            'telos': "You are Telos, focused on purpose and goals.",
            'terma': "You are Terma, managing boundaries and limits."
        }
        
        base_role = ci_roles.get(ci_name.lower(), f"You are {ci_name}, a specialized CI.")
        
        # Add task-specific context to role
        if task.get('role_context'):
            base_role += f" {task['role_context']}"
        
        return base_role
    
    def _format_task_instructions(self, task: Dict[str, Any], style: str) -> str:
        """Format the main task instructions."""
        instructions = []
        
        # Main objective
        if 'objective' in task:
            if style == 'conversational':
                instructions.append(f"Your task is to {task['objective']}.")
            elif style == 'technical':
                instructions.append(f"OBJECTIVE: {task['objective']}")
            else:
                instructions.append(f"Task: {task['objective']}")
        
        # Specific steps
        if 'steps' in task:
            instructions.append("\nSteps to complete:")
            for i, step in enumerate(task['steps'], 1):
                instructions.append(f"{i}. {step}")
        
        # Context
        if 'context' in task:
            instructions.append(f"\nContext: {task['context']}")
        
        # Data or inputs
        if 'inputs' in task:
            instructions.append(f"\nProvided inputs: {task['inputs']}")
        
        return "\n".join(instructions)
    
    def _format_turn_context(self, previous_turn: Dict[str, Any], style: str) -> Optional[str]:
        """Format context from the previous turn."""
        if not previous_turn:
            return None
        
        context_parts = []
        
        if style == 'conversational':
            if 'summary' in previous_turn:
                context_parts.append(f"In the previous turn, {previous_turn['summary']}")
            if 'key_points' in previous_turn:
                context_parts.append("Key points to remember:")
                for point in previous_turn['key_points']:
                    context_parts.append(f"  • {point}")
        
        elif style == 'technical':
            context_parts.append("PREVIOUS TURN:")
            if 'action' in previous_turn:
                context_parts.append(f"  Action: {previous_turn['action']}")
            if 'result' in previous_turn:
                context_parts.append(f"  Result: {previous_turn['result']}")
            if 'issues' in previous_turn:
                context_parts.append(f"  Issues: {', '.join(previous_turn['issues'])}")
        
        else:  # balanced/default
            context_parts.append("Previous context:")
            for key, value in previous_turn.items():
                if key not in ['timestamp', 'ci_name']:
                    context_parts.append(f"  {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else None
    
    def _add_guidelines(self, task: Dict[str, Any], style: str) -> Optional[str]:
        """Add task-specific guidelines and constraints."""
        guidelines = []
        
        # General guidelines based on style
        style_guidelines = {
            'analytical': [
                "Provide data-driven analysis",
                "Consider multiple perspectives",
                "Support conclusions with evidence"
            ],
            'conversational': [
                "Maintain a helpful, friendly tone",
                "Be clear and concise",
                "Ask for clarification if needed"
            ],
            'technical': [
                "Be precise and accurate",
                "Use appropriate technical terminology",
                "Include relevant details"
            ],
            'strategic': [
                "Think long-term",
                "Consider risks and opportunities",
                "Align with overall objectives"
            ],
            'creative': [
                "Explore innovative approaches",
                "Think outside conventional boundaries",
                "Generate multiple options"
            ]
        }
        
        if style in style_guidelines:
            guidelines.append("Guidelines:")
            for guideline in style_guidelines[style]:
                guidelines.append(f"  • {guideline}")
        
        # Task-specific constraints
        if 'constraints' in task:
            guidelines.append("\nConstraints:")
            for constraint in task['constraints']:
                guidelines.append(f"  • {constraint}")
        
        # Quality requirements
        if 'quality_requirements' in task:
            guidelines.append("\nQuality requirements:")
            for req in task['quality_requirements']:
                guidelines.append(f"  • {req}")
        
        return "\n".join(guidelines) if guidelines else None
    
    def _specify_output_format(self, task: Dict[str, Any]) -> Optional[str]:
        """Specify the expected output format."""
        if 'output_format' not in task:
            return None
        
        format_spec = task['output_format']
        
        if isinstance(format_spec, dict):
            return f"\nProvide output in the following format:\n{json.dumps(format_spec, indent=2)}"
        elif isinstance(format_spec, str):
            return f"\nOutput format: {format_spec}"
        else:
            return None
    
    def _combine_sections(self, sections: List[str], style: str) -> str:
        """Combine prompt sections based on style."""
        # Filter out None values
        sections = [s for s in sections if s]
        
        if style == 'technical':
            # Use clear separators for technical style
            separator = "\n" + "="*40 + "\n"
        elif style == 'conversational':
            # Use softer transitions for conversational style
            separator = "\n\n"
        else:
            # Default separator
            separator = "\n" + "-"*20 + "\n"
        
        return separator.join(sections)
    
    def _enforce_size_limit(self, prompt: str) -> str:
        """Ensure prompt doesn't exceed size limit."""
        if len(prompt) <= self.MAX_PROMPT_SIZE:
            return prompt
        
        # Truncate with indicator
        truncated = prompt[:self.MAX_PROMPT_SIZE - 100]
        
        # Find good break point
        last_newline = truncated.rfind('\n')
        if last_newline > self.MAX_PROMPT_SIZE - 500:
            truncated = truncated[:last_newline]
        
        return truncated + "\n\n[Prompt truncated for size]"
    
    def _update_history(self, ci_name: str, task: Dict[str, Any], prompt: str):
        """Update turn history for the CI."""
        if ci_name not in self.turn_history:
            self.turn_history[ci_name] = []
        
        # Keep only last 5 turns
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task.get('type', 'unknown'),
            'objective': task.get('objective', ''),
            'prompt_size': len(prompt)
        }
        
        self.turn_history[ci_name].append(history_entry)
        
        # Limit history size
        if len(self.turn_history[ci_name]) > 5:
            self.turn_history[ci_name] = self.turn_history[ci_name][-5:]
    
    def get_prompt_stats(self, prompt: str) -> Dict[str, Any]:
        """Get statistics about a prompt."""
        return {
            'size_chars': len(prompt),
            'size_kb': len(prompt.encode('utf-8')) / 1024,
            'lines': prompt.count('\n'),
            'sections': prompt.count('---'),
            'within_limit': len(prompt) <= self.MAX_PROMPT_SIZE
        }
    
    def clear_history(self, ci_name: Optional[str] = None):
        """Clear turn history."""
        if ci_name:
            if ci_name in self.turn_history:
                del self.turn_history[ci_name]
        else:
            self.turn_history.clear()


# Singleton service instance
_prompt_service = None


def get_prompt_service() -> PromptService:
    """Get or create the prompt service."""
    global _prompt_service
    if _prompt_service is None:
        _prompt_service = PromptService()
    return _prompt_service


def compose_prompt_for_turn(
    ci_name: str,
    task: Dict[str, Any],
    previous_turn: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to compose a prompt for a CI turn.
    
    Args:
        ci_name: Name of the CI
        task: Current task specification
        previous_turn: Summary of previous turn
        
    Returns:
        Formatted prompt (≤64KB)
    """
    service = get_prompt_service()
    return service.compose_prompt(ci_name, task, previous_turn)