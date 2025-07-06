"""
Simple message handler - just moves messages to/from AI sockets
"""
import socket
import json
from typing import Dict, Optional
import sys
from pathlib import Path

# Add Tekton root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from shared.utils.env_config import get_tekton_config, get_component_config
    from shared.utils.ai_port_utils import get_ai_port
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

class MessageHandler:
    """Just send and receive messages - that's it"""
    
    def __init__(self, rhetor_endpoint: str = None, debug: bool = False, timeout: int = 20):
        self.timeout = timeout
        
        if HAS_CONFIG:
            # Get port bases from config
            tekton_config = get_tekton_config()
            component_config = get_component_config()
            
            self.port_base = tekton_config.port_base
            self.ai_port_base = tekton_config.ai_port_base
            
            # Build ports dynamically from config
            self.ports = {}
            for component in ['engram', 'hermes', 'ergon', 'rhetor', 'terma', 'athena',
                            'prometheus', 'harmonia', 'telos', 'synthesis', 'tekton_core',
                            'metis', 'apollo', 'penia', 'sophia', 'noesis', 'numa', 'hephaestus']:
                component_port = component_config.get_port(component)
                if component_port:
                    # Use standard formula from ai_port_utils
                    ai_port = get_ai_port(component_port)
                    self.ports[component] = ai_port
        else:
            # Fallback to hardcoded if config not available
            self.port_base = 8000
            self.ai_port_base = 45000
            self.ports = {
                'engram': 45000,
                'hermes': 45001,
                'ergon': 45002,
                'rhetor': 45003,
                'terma': 45004,
                'athena': 45005,
                'prometheus': 45006,
                'harmonia': 45007,
                'telos': 45008,
                'synthesis': 45009,
                'tekton_core': 45010,
                'metis': 45011,
                'apollo': 45012,
                'penia': 45013,
                'sophia': 45014,
                'noesis': 45015,
                'numa': 45016,
                'hephaestus': 45080
            }
    
    def send(self, ai_name: str, message: str) -> str:
        """Send message, get response. Raise exception on any error."""
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