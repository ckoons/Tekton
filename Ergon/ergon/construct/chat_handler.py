"""
Bidirectional chat handler for Ergon Construct.

Detects whether input is JSON (from CI) or text (from human) and
responds appropriately. This makes Ergon natively bilingual.
"""

import json
import re
from typing import Dict, Any, Union, Optional
from datetime import datetime
import logging

from .engine import CompositionEngine

logger = logging.getLogger(__name__)


class ConstructChatHandler:
    """
    Handles both JSON and natural language for the Construct system.
    
    Core principle: JSON is the native language, text is translated.
    """
    
    def __init__(self, engine: Optional[CompositionEngine] = None):
        """
        Initialize with composition engine.
        
        Args:
            engine: The pure JSON composition engine
        """
        self.engine = engine or CompositionEngine()
        self.context = {}  # Conversation context per user/CI
        
        # Intent patterns for natural language
        self.intent_patterns = {
            'compose': [
                r'build.*?(?:solution|pipeline|system)',
                r'create.*?(?:from|using|with)',
                r'combine.*?components?',
                r'compose.*?(?:solution|pipeline)'
            ],
            'validate': [
                r'check.*?(?:valid|correct)',
                r'validate.*?(?:composition|solution)',
                r'verify.*?(?:connections|setup)'
            ],
            'test': [
                r'test.*?(?:solution|composition|pipeline)',
                r'run.*?(?:test|sandbox)',
                r'try.*?(?:out|it)'
            ],
            'publish': [
                r'publish.*?(?:registry|solution)',
                r'save.*?(?:registry|permanent)',
                r'release.*?(?:version|solution)'
            ],
            'help': [
                r'help',
                r'how.*?(?:do|can|should)',
                r'what.*?(?:can|should)',
                r'explain'
            ]
        }
    
    async def process_message(self, message: str, sender_id: str = 'unknown') -> str:
        """
        Process incoming message and return appropriate response.
        
        Args:
            message: Input message (JSON string or natural text)
            sender_id: ID of sender (CI or human)
            
        Returns:
            Response string (JSON for CIs, natural text for humans)
        """
        # Try to parse as JSON first
        json_data = self._try_parse_json(message)
        
        if json_data:
            # CI is speaking - respond in JSON
            return await self._handle_json_message(json_data, sender_id)
        else:
            # Human is speaking - parse intent and respond naturally
            return await self._handle_text_message(message, sender_id)
    
    def _try_parse_json(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Try to parse message as JSON.
        
        Returns None if not valid JSON.
        """
        try:
            # Handle JSON blocks in markdown
            if '```json' in message:
                json_match = re.search(r'```json\s*(.*?)\s*```', message, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            
            # Try direct JSON parse
            return json.loads(message)
        except (json.JSONDecodeError, AttributeError):
            return None
    
    async def _handle_json_message(self, data: Dict[str, Any], sender_id: str) -> str:
        """
        Handle JSON message from CI.
        
        Returns JSON response as string.
        """
        # Add sender context
        data['sender_id'] = sender_id
        data['timestamp'] = datetime.utcnow().isoformat()
        
        # Process through engine
        response = await self.engine.process(data)
        
        # Track in context
        self._update_context(sender_id, 'json', data, response)
        
        # Return JSON string
        return json.dumps(response, indent=2)
    
    async def _handle_text_message(self, message: str, sender_id: str) -> str:
        """
        Handle natural language message from human.
        
        Returns natural language response.
        """
        # Parse intent
        intent, entities = self._parse_intent(message)
        
        if not intent:
            return self._help_response()
        
        # Convert to JSON request
        json_request = self._text_to_json(intent, entities, sender_id)
        
        # Process through engine
        response = await self.engine.process(json_request)
        
        # Track in context
        self._update_context(sender_id, 'text', message, response)
        
        # Convert response to natural language
        return self._json_to_text(response, intent)
    
    def _parse_intent(self, message: str) -> tuple[Optional[str], Dict[str, Any]]:
        """
        Parse intent from natural language.
        
        Returns:
            (intent, entities) tuple
        """
        message_lower = message.lower()
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Extract entities (components, constraints, etc.)
                    entities = self._extract_entities(message)
                    return intent, entities
        
        return None, {}
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities from natural language.
        """
        entities = {}
        
        # Extract component names (assuming format: "using ComponentA and ComponentB")
        component_match = re.findall(r'using\s+([\w\s,]+?)(?:\s+(?:to|for|with)|\s*$)', message, re.IGNORECASE)
        if component_match:
            components = [c.strip() for c in component_match[0].split(',')]
            entities['components'] = components
        
        # Extract constraints (memory, timeout, etc.)
        memory_match = re.search(r'(\d+)\s*(gb|mb|g|m)', message, re.IGNORECASE)
        if memory_match:
            entities['memory'] = f"{memory_match.group(1)}{memory_match.group(2).upper()}"
        
        timeout_match = re.search(r'(\d+)\s*(?:seconds?|mins?|minutes?)', message, re.IGNORECASE)
        if timeout_match:
            entities['timeout'] = int(timeout_match.group(1))
        
        return entities
    
    def _text_to_json(self, intent: str, entities: Dict[str, Any], sender_id: str) -> Dict[str, Any]:
        """
        Convert parsed intent to JSON request.
        """
        # Get workspace from context if exists
        workspace_id = self.context.get(sender_id, {}).get('workspace_id')
        
        # Build JSON request based on intent
        if intent == 'compose':
            return {
                'action': 'compose',
                'workspace_id': workspace_id,
                'components': entities.get('components', []),
                'constraints': {
                    'max_memory': entities.get('memory', '4GB')
                }
            }
        
        elif intent == 'validate':
            return {
                'action': 'validate',
                'workspace_id': workspace_id,
                'checks': ['connections', 'dependencies', 'standards']
            }
        
        elif intent == 'test':
            return {
                'action': 'test',
                'workspace_id': workspace_id,
                'sandbox_config': {
                    'timeout': entities.get('timeout', 300)
                }
            }
        
        elif intent == 'publish':
            return {
                'action': 'publish',
                'workspace_id': workspace_id,
                'metadata': {
                    'name': entities.get('name', 'Composed Solution'),
                    'version': '1.0.0'
                }
            }
        
        else:
            return {'action': 'help'}
    
    def _json_to_text(self, response: Dict[str, Any], intent: str) -> str:
        """
        Convert JSON response to natural language.
        """
        status = response.get('status', 'unknown')
        
        if status == 'error':
            error = response.get('error', {})
            return f"Sorry, there was an error: {error.get('message', 'Unknown error')}"
        
        # Format response based on intent
        if intent == 'compose':
            workspace_id = response.get('workspace_id', 'unknown')
            validation = response.get('validation', {})
            
            if validation.get('valid'):
                return f"Great! I've created composition {workspace_id[:8]}. All connections are valid. Ready to test or add more components."
            else:
                errors = validation.get('errors', [])
                return f"Composition created but has issues: {', '.join(errors)}. Let me help you fix them."
        
        elif intent == 'validate':
            if response.get('valid'):
                return "✓ Your composition is valid! All checks passed. Ready to test or publish."
            else:
                errors = response.get('errors', [])
                warnings = response.get('warnings', [])
                msg = "Validation found some issues:\n"
                if errors:
                    msg += f"Errors: {', '.join(errors)}\n"
                if warnings:
                    msg += f"Warnings: {', '.join(warnings)}"
                return msg
        
        elif intent == 'test':
            sandbox_id = response.get('sandbox_id', 'unknown')
            return f"Testing your composition in sandbox {sandbox_id[:8]}. I'll stream the results as they come in..."
        
        elif intent == 'publish':
            registry_id = response.get('registry_id', 'unknown')
            return f"Successfully published to Registry! ID: {registry_id[:8]}. Your composition is now reusable by others."
        
        else:
            return json.dumps(response, indent=2)
    
    def _help_response(self) -> str:
        """
        Return help text for humans.
        """
        return """I can help you compose solutions! Try:
- "Build a data pipeline using Parser and Analyzer"
- "Validate my composition"
- "Test this solution"
- "Publish to Registry"

I understand both natural language and JSON. CIs can send me JSON directly for faster processing."""
    
    def _update_context(self, sender_id: str, msg_type: str, request: Any, response: Any):
        """
        Update conversation context.
        """
        if sender_id not in self.context:
            self.context[sender_id] = {
                'history': [],
                'workspace_id': None
            }
        
        # Track workspace from responses
        if isinstance(response, dict) and 'workspace_id' in response:
            self.context[sender_id]['workspace_id'] = response['workspace_id']
        
        # Add to history
        self.context[sender_id]['history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': msg_type,
            'request': request,
            'response': response
        })
        
        # Keep only last 10 messages
        self.context[sender_id]['history'] = self.context[sender_id]['history'][-10:]
    
    def get_context(self, sender_id: str) -> Dict[str, Any]:
        """
        Get conversation context for a sender.
        """
        return self.context.get(sender_id, {})