#!/usr/bin/env python3
"""
Messaging Context for CI Communication
Injects collaboration awareness into CI contexts
"""

from typing import Dict, List, Optional
from datetime import datetime
from shared.aish.src.registry.ci_registry import CIRegistry
from shared.terma.message_router import get_router

class MessagingContextInjector:
    """Injects messaging context and awareness into CI prompts"""
    
    def __init__(self):
        self.registry = CIRegistry()
        self.router = get_router()
    
    def get_messaging_context(self, ci_name: str, include_history: bool = True) -> str:
        """Generate messaging context for a CI"""
        
        context_parts = []
        
        # Get available collaborators
        collaborators = self.router.get_collaborators()
        if collaborators:
            context_parts.append(self._format_collaborators(collaborators))
        
        # Get recent messages if requested
        if include_history:
            history = self.router.get_message_history(ci_name, limit=10)
            if history:
                context_parts.append(self._format_message_history(history, ci_name))
        
        # Add messaging instructions
        context_parts.append(self._get_messaging_instructions())
        
        return "\n\n".join(context_parts)
    
    def _format_collaborators(self, collaborators: List[Dict]) -> str:
        """Format list of available collaborators"""
        
        lines = ["=== Available Collaborators ==="]
        
        # Group by type
        terminals = [c for c in collaborators if c['type'] == 'message_terminal']
        cis = [c for c in collaborators if c['type'] != 'message_terminal']
        
        if terminals:
            lines.append("\nHuman Collaborators (via terminals):")
            for t in terminals:
                name = t['name']
                directory = t.get('working_directory', 'Unknown')
                lines.append(f"  - {name} (working in: {directory})")
        
        if cis:
            lines.append("\nCI Collaborators:")
            for c in cis:
                name = c['name']
                caps = ', '.join(c.get('capabilities', []))
                lines.append(f"  - {name} (capabilities: {caps})")
        
        return '\n'.join(lines)
    
    def _format_message_history(self, history: List[Dict], current_ci: str) -> str:
        """Format recent message history"""
        
        lines = ["=== Recent Messages ==="]
        
        for msg in history:
            timestamp = msg.get('timestamp', '')
            if timestamp:
                # Parse and format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%H:%M')
                except:
                    time_str = ''
            else:
                time_str = ''
            
            from_ci = msg.get('from', 'Unknown')
            to_ci = msg.get('to', 'Unknown')
            content = msg.get('content', '')
            msg_type = msg.get('type', 'message')
            
            # Format based on direction
            if from_ci == current_ci:
                direction = f"You → {to_ci}"
            else:
                direction = f"{from_ci} → You"
            
            # Format based on type
            if msg_type == 'question':
                type_label = "[Question]"
            elif msg_type == 'coding_request':
                type_label = "[Coding Request]"
            else:
                type_label = ""
            
            lines.append(f"{time_str} {direction} {type_label}: {content[:80]}...")
        
        return '\n'.join(lines)
    
    def _get_messaging_instructions(self) -> str:
        """Get instructions for using messaging commands"""
        
        return """=== Messaging Commands ===
When you need to communicate with collaborators, use these natural commands in your responses:

@send {target} "message" - Send a message to another CI or human
  Example: @send claude@Beth "I've completed the API updates in Coder-B"

@ask {target} "question" - Ask a question (expects a reply)
  Example: @ask numa@Casey "Should I use TypeScript or JavaScript for this component?"

@reply {target} "answer" - Reply to a question or message
  Example: @reply apollo "Yes, please proceed with that approach"

@status - Check your pending messages and active requests
  Example: @status

These commands will be automatically detected and executed when you include them in your responses.
When working with others mentioned by the user, proactively use these commands to coordinate."""
    
    def inject_into_context(self, base_context: str, ci_name: str) -> str:
        """Inject messaging context into a base context"""
        
        messaging_context = self.get_messaging_context(ci_name)
        
        # Check if user mentioned collaboration
        collaboration_keywords = ['work with', 'coordinate with', 'ask', 'tell', 'help']
        needs_emphasis = any(keyword in base_context.lower() for keyword in collaboration_keywords)
        
        if needs_emphasis:
            emphasis = "\n**Note: The user has asked you to collaborate. Use @send or @ask commands to communicate with the mentioned collaborators.**\n"
            return f"{base_context}\n\n{emphasis}\n{messaging_context}"
        else:
            return f"{base_context}\n\n{messaging_context}"

# Global injector
_injector = None

def get_messaging_context(ci_name: str) -> str:
    """Get messaging context for a CI"""
    global _injector
    if _injector is None:
        _injector = MessagingContextInjector()
    return _injector.get_messaging_context(ci_name)

def inject_messaging_awareness(base_context: str, ci_name: str) -> str:
    """Inject messaging awareness into CI context"""
    global _injector
    if _injector is None:
        _injector = MessagingContextInjector()
    return _injector.inject_into_context(base_context, ci_name)