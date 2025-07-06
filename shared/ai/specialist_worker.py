# @tekton-module: Base AI Specialist Worker framework
# @tekton-depends: asyncio, httpx, json, socket
# @tekton-provides: ai-specialist-base, socket-server, llm-integration
# @tekton-version: 1.0.0
# @tekton-critical: true

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

# Import landmarks for architectural documentation
try:
    from landmarks import (
        architecture_decision,
        performance_boundary,
        api_contract,
        integration_point,
        state_checkpoint
    )
except ImportError:
    # If landmarks not available, create no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func):
            return func
        return decorator

# Import debug utilities
try:
    from shared.utils.debug_utils import create_component_logger
    logger = create_component_logger('ai_specialist')
except ImportError:
    logger = logging.getLogger(__name__)


# @tekton-class: Abstract base for AI specialists
# @tekton-singleton: false
# @tekton-lifecycle: worker
# @tekton-abstract: true
@architecture_decision(
    title="AI Specialist Worker Pattern",
    rationale="Provide common framework for all AI specialists with socket communication and LLM integration",
    alternatives_considered=["Direct HTTP APIs", "gRPC services", "Message queues"],
    impacts=["consistency", "code_reuse", "socket_overhead"]
)
@integration_point(
    title="LLM Provider Integration",
    target_component="Ollama/Anthropic",
    protocol="HTTP REST",
    data_flow="Prompt/response cycles"
)
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
    
    # LLM chat handler removed - AIs use simple personality responses instead
    
    # @tekton-method: Handle socket client connections
    # @tekton-async: true
    # @tekton-socket-handler: true
    # @tekton-concurrent: true
    @api_contract(
        title="Socket Message Protocol",
        endpoint="socket://{port}",
        method="SOCKET",
        request_schema={"type": "string", "content": "any"},
        response_schema={"type": "string", "ai_id": "string", "content": "any"}
    )
    async def handle_client(self, reader: asyncio.StreamReader, 
                          writer: asyncio.StreamWriter):
        """Handle client connection."""
        client_addr = writer.get_extra_info('peername')
        self.logger.info(f"Client connected: {client_addr}")
        self.logger.debug(f"Active clients: {len(self.clients) + 1}")
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
                    self.logger.debug(f"Processing message type: {msg_type}")
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
    
    # @tekton-method: Start socket server
    # @tekton-async: true
    # @tekton-lifecycle: startup
    @state_checkpoint(
        title="AI Specialist Server State",
        state_type="runtime",
        persistence=False,
        consistency_requirements="Socket bound to port"
    )
    async def start(self):
        """Start the AI specialist server."""
        # Pre-initialize connection pool if available
        try:
            from .connection_pool import get_connection_pool
            pool = await get_connection_pool()
            pool.start_health_monitoring()
            self.logger.info("Connection pool initialized and health monitoring started")
        except ImportError:
            pass  # Connection pool not available
        except Exception as e:
            self.logger.warning(f"Could not initialize connection pool: {e}")
        
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