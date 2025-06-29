"""
Unified AI Client for Rhetor

This replaces the old multi-provider LLM client with a unified approach
that uses the AI Registry to discover and communicate with AI specialists.
"""
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass

# Add Tekton root to path
import os
import sys
script_path = os.path.realpath(__file__)
# Go up from rhetor/core to Tekton root
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.ai.registry_client import AIRegistryClient

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Response from an AI specialist."""
    content: str
    ai_id: str
    model: str
    metadata: Dict[str, Any] = None


class UnifiedAIClient:
    """
    Unified AI client that uses the AI Registry to find and communicate
    with AI specialists instead of direct LLM provider connections.
    """
    
    def __init__(self):
        """Initialize the unified AI client."""
        self.registry = AIRegistryClient()
        self._socket_connections = {}  # Cache open connections
        logger.info("Initialized UnifiedAIClient with AI Registry")
    
    async def complete(self, 
                      prompt: str,
                      role: str = 'general',
                      temperature: float = 0.7,
                      max_tokens: int = 4000,
                      stream: bool = False,
                      metadata: Dict[str, Any] = None) -> AIResponse:
        """
        Complete a prompt using the best available AI for the role.
        
        Args:
            prompt: The prompt to complete
            role: The role/capability needed (e.g., 'code-analysis', 'planning')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            metadata: Additional metadata for the request
            
        Returns:
            AIResponse with the completion
        """
        # Find the best AI for this role
        ai_id = self.registry.select_best_ai(role)
        
        if not ai_id:
            # Fallback to any available AI
            all_ais = self.registry.list_platform_ais()
            if all_ais:
                ai_id = list(all_ais.keys())[0]
                logger.warning(f"No AI found for role '{role}', using {ai_id}")
            else:
                raise RuntimeError("No AI specialists available")
        
        # Get socket info
        socket_info = self.registry.get_ai_socket(ai_id)
        if not socket_info:
            raise RuntimeError(f"AI {ai_id} not found in registry")
        
        # Send request to AI
        try:
            if stream:
                # Streaming not implemented yet, fall back to regular
                response = await self._send_to_ai(ai_id, socket_info, prompt, temperature, max_tokens)
            else:
                response = await self._send_to_ai(ai_id, socket_info, prompt, temperature, max_tokens)
            
            # Log successful completion
            self.registry.log_transition(ai_id, 'request_completed', {
                'role': role,
                'tokens': len(response.content.split()),
                'success': True
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error communicating with AI {ai_id}: {e}")
            
            # Log failure
            self.registry.log_transition(ai_id, 'request_failed', {
                'role': role,
                'error': str(e)
            })
            
            # Try fallback
            alternatives = self.registry.discover_by_role(role)
            for alt in alternatives:
                if alt['ai_id'] != ai_id:
                    try:
                        alt_socket = self.registry.get_ai_socket(alt['ai_id'])
                        if alt_socket:
                            return await self._send_to_ai(alt['ai_id'], alt_socket, prompt, temperature, max_tokens)
                    except:
                        continue
            
            raise RuntimeError(f"Failed to get response from any AI for role '{role}'")
    
    async def _send_to_ai(self, ai_id: str, socket_info: tuple, 
                         prompt: str, temperature: float, max_tokens: int) -> AIResponse:
        """Send a request to an AI specialist via socket."""
        host, port = socket_info
        
        try:
            # Connect to AI socket
            reader, writer = await asyncio.open_connection(host, port)
            
            # Send chat message
            message = {
                'type': 'chat',
                'content': prompt,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            writer.write(json.dumps(message).encode() + b'\n')
            await writer.drain()
            
            # Read response
            data = await reader.readline()
            response = json.loads(data.decode())
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            # Extract response content
            content = response.get('content', '')
            if not content and 'response' in response:
                content = response['response']
            
            return AIResponse(
                content=content,
                ai_id=ai_id,
                model=response.get('model', 'unknown'),
                metadata=response
            )
            
        except Exception as e:
            logger.error(f"Socket communication error with {ai_id}: {e}")
            raise
    
    async def list_available_models(self) -> Dict[str, List[str]]:
        """List available AI models by role."""
        roles = ['code-analysis', 'planning', 'orchestration', 'knowledge-synthesis', 
                 'memory', 'messaging', 'learning', 'agent-coordination']
        
        available = {}
        for role in roles:
            ais = self.registry.discover_by_role(role)
            available[role] = [f"{ai['ai_id']} ({ai['component']})" for ai in ais]
        
        return available
    
    async def get_model_info(self, ai_id: str) -> Dict[str, Any]:
        """Get information about a specific AI."""
        socket_info = self.registry.get_ai_socket(ai_id)
        if not socket_info:
            return {'error': f'AI {ai_id} not found'}
        
        try:
            # Send info request
            reader, writer = await asyncio.open_connection(socket_info[0], socket_info[1])
            
            message = {'type': 'info'}
            writer.write(json.dumps(message).encode() + b'\n')
            await writer.drain()
            
            data = await reader.readline()
            response = json.loads(data.decode())
            
            writer.close()
            await writer.wait_closed()
            
            return response
            
        except Exception as e:
            return {'error': f'Failed to get info from {ai_id}: {str(e)}'}
    
    def get_default_model(self) -> str:
        """Get the default AI model (first available)."""
        ais = self.registry.list_platform_ais()
        if ais:
            return list(ais.keys())[0]
        return "none-available"
    
    async def set_default_model(self, model: str) -> bool:
        """Set default model (no-op for compatibility)."""
        # In the unified system, we use role-based selection
        # This is kept for API compatibility
        logger.info(f"Default model request for {model} - using role-based selection")
        return True
    
    async def shutdown(self):
        """Shutdown the client and close connections."""
        # Close any cached connections
        for writer in self._socket_connections.values():
            if hasattr(writer, 'close'):
                writer.close()
                await writer.wait_closed()
        self._socket_connections.clear()
        logger.info("UnifiedAIClient shutdown complete")