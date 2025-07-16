"""
Simple message handler - just moves messages to/from AI sockets
"""
import socket
import json
from typing import Dict, Optional
import sys
from pathlib import Path
import os

# Try to import landmarks if available
try:
    from landmarks import architecture_decision, integration_point, api_contract, state_checkpoint
except ImportError:
    # Landmarks not available, create no-op decorators
    def architecture_decision(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(name, description, rationale=""):
        def decorator(func):
            return func
        return decorator

# Add Tekton root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Always use TektonEnviron - it's required
from shared.env import TektonEnviron
from shared.utils.ai_port_utils import get_ai_port, COMPONENT_PORTS

# Import forwarding registry
try:
    from forwarding.forwarding_registry import ForwardingRegistry
except ImportError:
    # Try absolute import if relative fails
    from src.forwarding.forwarding_registry import ForwardingRegistry

class MessageHandler:
    """Just send and receive messages - that's it"""
    
    def __init__(self, rhetor_endpoint: str = None, debug: bool = False, timeout: int = 20):
        self.timeout = timeout
        self.forwarding = ForwardingRegistry()
        
        # Get port bases from environment
        self.port_base = int(TektonEnviron.get('TEKTON_PORT_BASE', '8000'))
        self.ai_port_base = int(TektonEnviron.get('TEKTON_AI_PORT_BASE', '45000'))
        
        # Build ports dynamically using ai_port_utils
        self.ports = {}
        for component_name, component_port in COMPONENT_PORTS.items():
            # Calculate AI port using the standard formula
            ai_port = get_ai_port(component_port)
            self.ports[component_name] = ai_port
    
    # Landmark: AI Message Routing Decision - Critical branch for forwarding
    def send(self, ai_name: str, message: str) -> str:
        """Send message, check forwarding first."""
        
        # Check if AI is forwarded
        forward_target = self.forwarding.get_forward(ai_name)
        if forward_target:
            return self._send_forwarded(ai_name, message, forward_target)
        
        # Normal AI routing
        return self._send_to_ai_direct(ai_name, message)
    
    def _send_forwarded(self, ai_name: str, message: str, terminal_name: str) -> str:
        """Send message to terminal inbox instead of AI."""
        try:
            # Format message for human inbox
            formatted_msg = f"[{ai_name}] {message}"
            
            # Send to terminal inbox
            success = self._send_to_terminal_inbox(terminal_name, formatted_msg)
            
            if success:
                return f"Message forwarded to {terminal_name}"
            else:
                # Fallback to AI if forwarding fails
                return self._send_to_ai_direct(ai_name, message)
                
        except Exception as e:
            print(f"Forwarding failed: {e}, falling back to AI")
            return self._send_to_ai_direct(ai_name, message)
    
    # Landmark: AI Socket Communication - Direct connection to AI specialist
    def _send_to_ai_direct(self, ai_name: str, message: str) -> str:
        """Direct AI communication (original logic)."""
        port = self.ports.get(ai_name)
        if not port:
            raise ValueError(f"Unknown AI: {ai_name}")
        
        s = socket.socket()
        s.settimeout(self.timeout)
        s.connect(('localhost', port))
        s.send((json.dumps({'content': message}) + '\n').encode())
        
        data = s.recv(4096)
        s.close()
        
        resp = json.loads(data.decode())
        return resp.get('content', '')
    
    def _send_to_terminal_inbox(self, terminal_name: str, message: str) -> bool:
        """Send message to terminal's inbox via terma."""
        try:
            # Import here to avoid circular dependencies
            try:
                from commands.terma import terma_send_message_to_terminal
            except ImportError:
                from src.commands.terma import terma_send_message_to_terminal
            return terma_send_message_to_terminal(terminal_name, message)
        except Exception:
            return False
    
    def broadcast(self, message: str) -> Dict[str, str]:
        """Send to all AIs. Return dict of responses or errors."""
        responses = {}
        for ai_name, port in self.ports.items():
            try:
                responses[ai_name] = self.send(ai_name, message)
            except Exception as e:
                responses[ai_name] = f"ERROR: {str(e)}"
        return responses
    
    # Compatibility methods for aish
    def write(self, socket_id: str, message: str) -> bool:
        """Compatibility wrapper for aish"""
        if socket_id == "team-chat-all":
            responses = self.broadcast(message)
            # Store responses for read() method
            self._last_responses = responses
            return len(responses) > 0
        else:
            # Extract AI name from socket_id (e.g. "apollo-socket" -> "apollo")
            ai_name = socket_id.replace('-socket', '')
            try:
                response = self.send(ai_name, message)
                self._last_responses = {ai_name: response}
                return True
            except:
                return False
    
    def read(self, socket_id: str) -> list:
        """Compatibility wrapper for aish"""
        if not hasattr(self, '_last_responses'):
            return []
            
        if socket_id == "team-chat-all":
            messages = []
            for ai_name, response in self._last_responses.items():
                if not response.startswith('ERROR:'):
                    messages.append(f"[team-chat-from-{ai_name}] {response}")
            return messages
        else:
            # For individual AI, check if we have a response
            ai_name = socket_id.replace('-socket', '')
            if ai_name in self._last_responses:
                response = self._last_responses[ai_name]
                if not response.startswith('ERROR:'):
                    # Clear after reading
                    del self._last_responses[ai_name]
                    return [f"[team-chat-from-{ai_name}] {response}"]
        return []
    
    def create(self, ai_name: str, model: str = None, prompt: str = None, context: Dict = None) -> str:
        """Compatibility - just return a socket ID"""
        return f"{ai_name}-socket"