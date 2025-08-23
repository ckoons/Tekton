"""
MCP interface for Construct questions.

Allows CIs to access and interact with the guided dialog questions programmatically.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConstructQuestionsMCP:
    """MCP tool for Construct questions."""
    
    def __init__(self):
        """Initialize with questions data."""
        self.questions_path = Path(__file__).parent / 'questions.json'
        self.load_questions()
        self.current_index = 0
        self.responses = {}
    
    def load_questions(self):
        """Load questions from JSON file."""
        with open(self.questions_path, 'r') as f:
            self.data = json.load(f)
            self.questions = self.data['questions']
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Get all questions for review."""
        return self.questions
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question to answer."""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    
    def submit_answer(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Submit an answer for a question."""
        # Store the response
        self.responses[question_id] = answer
        
        # Parse the answer for smart filling
        parsed = self._parse_answer(question_id, answer)
        
        # Move to next question
        self.current_index += 1
        
        return {
            'status': 'accepted',
            'question_id': question_id,
            'answer': answer,
            'parsed': parsed,
            'next_question': self.get_current_question()
        }
    
    def get_suggestions(self, question_id: str) -> Dict[str, Any]:
        """Get AI suggestions for a question based on context."""
        question = next((q for q in self.questions if q['id'] == question_id), None)
        if not question:
            return {'error': 'Question not found'}
        
        suggestions = []
        
        # Apply smart defaults based on previous answers
        if question_id == 'container' and self.responses.get('deployment') == 'containerized':
            suggestions.append({
                'value': 'yes',
                'reason': 'Containerized deployment selected'
            })
        
        if question_id == 'ci_association':
            if self.responses.get('container') == 'yes':
                suggestions.append({
                    'value': 'container',
                    'reason': 'Container management CI recommended for containerized solutions'
                })
            elif 'interactive' in str(self.responses.get('purpose', '')).lower():
                suggestions.append({
                    'value': 'ci-terminal',
                    'reason': 'Interactive solution detected'
                })
        
        return {
            'question_id': question_id,
            'suggestions': suggestions
        }
    
    def build_workspace(self) -> Dict[str, Any]:
        """Build the final workspace configuration from responses."""
        workspace = {
            'components': [],
            'connections': [],
            'constraints': {},
            'metadata': {
                'purpose': self.responses.get('purpose', ''),
                'deployment': self.responses.get('deployment', 'standalone'),
                'container': self.responses.get('container', 'no'),
                'ci_type': self.responses.get('ci_association', 'none')
            }
        }
        
        # Parse components
        if 'components' in self.responses:
            components_text = self.responses['components']
            # Simple parsing - in production, use NLP
            component_names = [c.strip() for c in components_text.split(',')]
            workspace['components'] = [
                {'alias': name, 'registry_id': f'{name.lower()}-pending'}
                for name in component_names if name
            ]
        
        # Parse constraints
        if 'constraints' in self.responses:
            constraints_text = self.responses['constraints']
            if 'gb' in constraints_text.lower() or 'mb' in constraints_text.lower():
                # Extract memory constraint
                import re
                mem_match = re.search(r'(\d+)\s*(gb|mb)', constraints_text, re.IGNORECASE)
                if mem_match:
                    workspace['constraints']['memory'] = f"{mem_match.group(1)}{mem_match.group(2).upper()}"
        
        return workspace
    
    def _parse_answer(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Parse an answer to extract structured data."""
        parsed = {'raw': answer}
        
        question = next((q for q in self.questions if q['id'] == question_id), None)
        if not question:
            return parsed
        
        # Parse based on question type
        if question.get('type') == 'choice':
            # Match against options
            answer_lower = answer.lower()
            for option in question.get('options', []):
                if option.lower() in answer_lower:
                    parsed['selected'] = option
                    break
        
        elif question.get('type') == 'component_selection':
            # Extract component names
            components = []
            for word in answer.split():
                if '-' in word or word.startswith('comp'):
                    components.append(word)
            parsed['components'] = components
        
        return parsed
    
    # MCP Tool Interface
    async def handle_tool_call(self, action: str, **params) -> Dict[str, Any]:
        """Handle MCP tool calls from CIs."""
        if action == 'get_all':
            return {'questions': self.get_all_questions()}
        
        elif action == 'get_next':
            question = self.get_current_question()
            if question:
                return {'question': question}
            return {'status': 'complete', 'workspace': self.build_workspace()}
        
        elif action == 'submit_answer':
            question_id = params.get('question_id')
            answer = params.get('answer')
            if not question_id or not answer:
                return {'error': 'Missing question_id or answer'}
            return self.submit_answer(question_id, answer)
        
        elif action == 'get_suggestions':
            question_id = params.get('question_id')
            if not question_id:
                return {'error': 'Missing question_id'}
            return self.get_suggestions(question_id)
        
        elif action == 'build_workspace':
            return {'workspace': self.build_workspace()}
        
        else:
            return {'error': f'Unknown action: {action}'}


# Export for MCP registration
def get_mcp_tool():
    """Get MCP tool definition for registration."""
    return {
        'name': 'ergon_construct_questions',
        'description': 'Access and interact with Construct guided dialog questions',
        'handler': ConstructQuestionsMCP(),
        'schema': {
            'type': 'object',
            'properties': {
                'action': {
                    'type': 'string',
                    'enum': ['get_all', 'get_next', 'submit_answer', 'get_suggestions', 'build_workspace'],
                    'description': 'Action to perform'
                },
                'question_id': {
                    'type': 'string',
                    'description': 'ID of the question'
                },
                'answer': {
                    'type': 'string',
                    'description': 'Answer to submit'
                }
            },
            'required': ['action']
        }
    }