"""
Base AI Specialist Worker class for Tekton AI specialists.

Provides common functionality for all AI specialists including:
- Socket communication
- Health monitoring
- Message handling
- Ollama/Anthropic integration
"""
import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
import socket

logger = logging.getLogger(__name__)


class AISpecialistWorker(ABC):
    """Base class for AI specialist workers."""
    
    def __init__(self, 
                 ai_id: str,
                 component: str,
                 port: int,
                 description: str = "AI Specialist"):
        """
        Initialize AI Specialist Worker.
        
        Args:
            ai_id: Unique identifier for the AI
            component: Component name this AI belongs to
            port: Port to listen on
            description: Human-readable description
        """
        self.ai_id = ai_id
        self.component = component
        self.port = port
        self.description = description
        
        # Socket server
        self.server = None
        self.clients = []
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {
            'ping': self._handle_ping,
            'health': self._handle_health,
            'info': self._handle_info,
            'chat': self._handle_chat,
        }
        
        # AI configuration
        self.model_provider = os.environ.get('TEKTON_AI_PROVIDER', 'ollama')
        self.model_name = os.environ.get(f'{component.upper()}_AI_MODEL', 
                                        self.get_default_model())
        
        # Setup logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{ai_id}")
        
    def get_default_model(self) -> str:
        """Get default model for this AI specialist."""
        return 'llama3.3:70b'
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this AI specialist."""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message specific to this AI specialist.
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        pass
    
    async def _handle_ping(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping message."""
        return {
            'type': 'pong',
            'ai_id': self.ai_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _handle_health(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check."""
        return {
            'type': 'health_response',
            'ai_id': self.ai_id,
            'status': 'healthy',
            'component': self.component,
            'model': f"{self.model_provider}:{self.model_name}",
            'clients': len(self.clients)
        }
    
    async def _handle_info(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle info request."""
        return {
            'type': 'info_response',
            'ai_id': self.ai_id,
            'component': self.component,
            'description': self.description,
            'model_provider': self.model_provider,
            'model_name': self.model_name,
            'system_prompt': self.get_system_prompt()[:200] + '...',
            'port': self.port
        }
    
    async def _handle_chat(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat message - delegates to LLM."""
        try:
            # Get prompt from message
            prompt = message.get('content', '')
            if not prompt:
                return {
                    'type': 'error',
                    'error': 'No content provided'
                }
            
            # Call LLM based on provider
            if self.model_provider == 'ollama':
                response = await self._call_ollama(prompt)
            elif self.model_provider == 'anthropic':
                response = await self._call_anthropic(prompt)
            else:
                response = f"Unknown provider: {self.model_provider}"
            
            return {
                'type': 'chat_response',
                'ai_id': self.ai_id,
                'content': response
            }
            
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return {
                'type': 'error',
                'error': str(e)
            }
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': self.model_name,
                        'prompt': f"{self.get_system_prompt()}\n\nUser: {prompt}\n\nAssistant:",
                        'stream': False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()['response']
                else:
                    return f"Ollama error: {response.status_code}"
                    
        except Exception as e:
            return f"Ollama connection error: {e}"
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API via Rhetor."""
        try:
            import httpx
            
            # Use Rhetor's API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'http://localhost:8003/api/v1/chat',
                    json={
                        'messages': [
                            {'role': 'system', 'content': self.get_system_prompt()},
                            {'role': 'user', 'content': prompt}
                        ],
                        'model': self.model_name,
                        'temperature': 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()['content']
                else:
                    return f"Rhetor error: {response.status_code}"
                    
        except Exception as e:
            return f"Rhetor connection error: {e}"
    
    async def handle_client(self, reader: asyncio.StreamReader, 
                          writer: asyncio.StreamWriter):
        """Handle client connection."""
        client_addr = writer.get_extra_info('peername')
        self.logger.info(f"Client connected: {client_addr}")
        self.clients.append(writer)
        
        try:
            while True:
                # Read message
                data = await reader.readline()
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    msg_type = message.get('type', 'unknown')
                    
                    # Get handler
                    handler = self.handlers.get(msg_type, self.process_message)
                    
                    # Process message
                    response = await handler(message)
                    
                    # Send response
                    writer.write(json.dumps(response).encode() + b'\n')
                    await writer.drain()
                    
                except json.JSONDecodeError:
                    error_response = {'type': 'error', 'error': 'Invalid JSON'}
                    writer.write(json.dumps(error_response).encode() + b'\n')
                    await writer.drain()
                    
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.error(f"Client error: {e}")
        finally:
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            self.logger.info(f"Client disconnected: {client_addr}")
    
    async def start(self):
        """Start the AI specialist server."""
        self.server = await asyncio.start_server(
            self.handle_client,
            'localhost',
            self.port
        )
        
        self.logger.info(f"{self.ai_id} listening on port {self.port}")
        
        async with self.server:
            await self.server.serve_forever()
    
    def run(self):
        """Run the AI specialist."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            self.logger.info(f"Shutting down {self.ai_id}")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            sys.exit(1)