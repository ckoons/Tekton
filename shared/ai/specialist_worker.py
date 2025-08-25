# @tekton-module: Base CI Specialist Worker framework
# @tekton-depends: asyncio, httpx, json, socket
# @tekton-provides: ai-specialist-base, socket-server, llm-integration
# @tekton-version: 1.0.0
# @tekton-critical: true

"""
Base CI Specialist Worker class for Tekton CI specialists.

Provides common functionality for all CI specialists including:
- Socket communication
- Health monitoring
- Message handling
- Ollama/Anthropic integration
"""
import os
from shared.env import TektonEnviron
import sys
import json
import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from abc import ABC, abstractmethod
import socket

# Add Tekton root to path for model imports
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

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

# Import model management
from tekton.core.models.manager import ModelManager
from tekton.core.models.adapters import (
    AnthropicAdapter, OpenAIAdapter, LocalModelAdapter,
    GrokAdapter, GeminiAdapter
)

# Import CI registry for storing exchanges
# NOTE: This integration enables Apollo-Rhetor coordination through exchange storage
try:
    from shared.aish.src.registry.ci_registry import CIRegistry
    ci_registry = CIRegistry()
except ImportError:
    ci_registry = None
    logging.warning("CI Registry not available for storing CI exchanges")

# Architecture decision marker for CI Registry integration
@architecture_decision(
    title="AI Specialist CI Registry Integration",
    description="All CI specialists automatically store exchanges in CI Registry",
    rationale="Enables Apollo to monitor performance/stress and Rhetor to inject context",
    alternatives_considered=["Per-specialist opt-in", "Separate storage mechanism", "Direct Apollo API calls"],
    impacts=["apollo_monitoring", "rhetor_context", "performance_tracking"],
    decided_by="Casey",
    decision_date="2025-07-30"
)
class _CIRegistryIntegration:
    """Marker class for CI Registry integration architecture"""
    pass

# Import debug utilities
try:
    from shared.utils.debug_utils import create_component_logger
    logger = create_component_logger('ai_specialist')
except ImportError:
    logger = logging.getLogger(__name__)


# @tekton-class: Abstract base for CI specialists
# @tekton-singleton: false
# @tekton-lifecycle: worker
# @tekton-abstract: true
@architecture_decision(
    title="AI Specialist Worker Pattern",
    rationale="Provide common framework for all CI specialists with socket communication and LLM integration",
    alternatives_considered=["Direct HTTP APIs", "gRPC services", "Message queues"],
    impacts=["consistency", "code_reuse", "socket_overhead"]
)
@integration_point(
    title="LLM Provider Integration",
    target_component="Ollama/Anthropic",
    protocol="HTTP REST",
    data_flow="Prompt/response cycles"
)
class CISpecialistWorker(ABC):
    """Base class for CI specialist workers."""
    
    def __init__(self, 
                 ai_id: str,
                 component: str,
                 port: int,
                 description: str = "AI Specialist"):
        """
        Initialize CI Specialist Worker.
        
        Args:
            ai_id: Unique identifier for the AI
            component: Component name this CI belongs to
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
        
        # CI configuration
        self.model_provider = TektonEnviron.get('TEKTON_AI_PROVIDER', 'ollama')
        self.model_name = TektonEnviron.get(f'{component.upper()}_AI_MODEL', 
                                        self.get_default_model())
        
        # Initialize model manager
        self.model_manager = ModelManager()
        self.model_adapter = None
        self.model_ready = False
        
        # Setup logging
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{ai_id}")
        
    def get_default_model(self) -> str:
        """Get default model for this CI specialist."""
        return 'gpt-oss:20b'
    
    def detect_thinking_level(self, text: str) -> tuple[str, float, int]:
        """
        Detect required thinking level based on keywords in the text.
        
        Returns:
            Tuple of (model_name, temperature, max_tokens)
        """
        import re
        
        text_lower = text.lower()
        
        # Level 4: Extended Context & Deep Reasoning
        if any(phrase in text_lower for phrase in [
            "deeply think", "carefully consider", "contemplate", "reason through",
            "comprehensive analysis", "thorough examination", "full review", 
            "explore all", "extensive analysis"
        ]):
            return 'gpt-oss:120b', 0.9, 4096
        
        # Level 3: Analytical Thinking
        if any(phrase in text_lower for phrase in [
            "think about", "consider this", "analyze", "explain why", 
            "understand", "debug", "investigate", "examine", "evaluate"
        ]):
            return 'gpt-oss:120b', 0.7, 3072
        
        # Level 2: Code Generation & Problem Solving
        if any(phrase in text_lower for phrase in [
            "write code", "implement", "create function", "generate", 
            "solve", "fix", "optimize", "refactor"
        ]):
            return 'gpt-oss:120b', 0.6, 2048
        
        # Level 1: Quick/Simple Tasks (Default)
        # Keywords: quick, simple, list, show, status, check, what, where, when
        return 'gpt-oss:20b', 0.5, 1536
    
    def _get_thinking_level_name(self, model: str, temperature: float) -> str:
        """Get human-readable thinking level name."""
        if model == 'gpt-oss:120b':
            if temperature >= 0.9:
                return "Deep Reasoning"
            elif temperature >= 0.7:
                return "Analytical"
            else:
                return "Problem Solving"
        return "Quick Response"
    
    @state_checkpoint(
        title="Model Adapter Initialization",
        description="Initialize connection to LLM provider (Ollama, Anthropic, etc)",
        state_type="connection",
        persistence=False,
        consistency_requirements="Model must be ready before processing messages",
        recovery_strategy="Retry on failure, continue without LLM if unavailable"
    )
    async def initialize_model(self):
        """Initialize the model adapter based on provider configuration."""
        try:
            self.logger.info(f"Starting model initialization for {self.ai_id}")
            self.logger.info(f"Provider: {self.model_provider}, Model: {self.model_name}")
            
            # Map provider names to adapter classes
            adapter_map = {
                'ollama': LocalModelAdapter,
                'local': LocalModelAdapter,
                'anthropic': AnthropicAdapter,
                'openai': OpenAIAdapter,
                'grok': GrokAdapter,
                'gemini': GeminiAdapter
            }
            
            # Get adapter class
            adapter_class = adapter_map.get(self.model_provider.lower())
            if not adapter_class:
                self.logger.error(f"Unknown model provider: {self.model_provider}")
                return False
            
            self.logger.info(f"Using adapter class: {adapter_class.__name__}")
            
            # Prepare configuration
            config = {
                'model': self.model_name
            }
            
            # Add provider-specific configuration
            if self.model_provider.lower() in ['ollama', 'local']:
                config['endpoint'] = TektonEnviron.get('OLLAMA_ENDPOINT', 'http://localhost:11434')
                self.logger.info(f"Ollama endpoint: {config['endpoint']}")
            else:
                # Get API key from environment
                api_key_var = f"{self.model_provider.upper()}_API_KEY"
                api_key = TektonEnviron.get(api_key_var)
                if not api_key:
                    self.logger.error(f"API key not found: {api_key_var}")
                    return False
                config['api_key'] = api_key
            
            self.logger.info(f"Registering adapter with config: {config}")
            
            # Register adapter with model manager
            success = await self.model_manager.register_adapter(
                self.model_provider,
                adapter_class,
                config
            )
            
            self.logger.info(f"Registration result: {success}")
            
            if success:
                self.model_adapter = self.model_manager.adapters.get(self.model_provider)
                self.model_ready = True
                self.logger.info(f"Model initialized successfully: {self.model_provider}:{self.model_name}")
                self.logger.info(f"Model adapter type: {type(self.model_adapter)}")
                return True
            else:
                self.logger.error(f"Failed to initialize model adapter - registration returned False")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing model: {e}", exc_info=True)
            return False
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get system prompt for this CI specialist."""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message specific to this CI specialist.
        
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
    
    @performance_boundary(
        title="Chat Message Processing",
        description="Core chat handler with LLM integration",
        sla="<5s for typical prompts, <30s for complex analysis",
        optimization_notes="Streams responses when possible, caches model connection",
        measured_impact="Primary performance bottleneck for CI specialists"
    )
    async def _handle_chat(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat message using the configured model."""
        # Check if this CI is forwarded to Claude
        from shared.ai.claude_handler import process_with_claude
        ci_name = f"{self.component}-ci"
        
        # Try Claude first if forwarded
        user_content = message.get('content', message.get('message', ''))
        claude_response = await process_with_claude(ci_name, user_content)
        
        if claude_response:
            # Claude handled it - also update registry for monitoring
            from shared.aish.src.registry.ci_registry import get_registry
            registry = get_registry()
            registry.update_ci_last_output(ci_name, {
                'user_message': user_content,
                'content': claude_response,
                'timestamp': message.get('timestamp'),
                'model': 'claude'
            })
            
            return {
                'type': 'response',
                'ai_id': self.ai_id,
                'content': claude_response,
                'model': 'claude',
                'forwarded': True
            }
        
        # Not forwarded or Claude unavailable, use normal model
        if not self.model_ready:
            self.logger.warning(f"Model not ready for {self.ai_id}, attempting to reinitialize...")
            # Try to reinitialize once
            reinit_success = await self.initialize_model()
            if not reinit_success:
                self.logger.error(f"Reinitialization failed for {self.ai_id}")
                return {
                    'type': 'error',
                    'ai_id': self.ai_id,
                    'error': 'Model not initialized - Ollama may not be accessible'
                }
            self.logger.info(f"Reinitialization successful for {self.ai_id}")
        
        try:
            # Prepare messages for the model
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            
            # Add conversation history if provided
            if 'history' in message:
                messages.extend(message['history'])
            
            # Add the current user message
            user_content = message.get('content', message.get('message', ''))
            messages.append({"role": "user", "content": user_content})
            
            # Detect thinking level and select appropriate model
            detected_model, detected_temp, detected_tokens = self.detect_thinking_level(user_content)
            
            # Check if we need to switch models temporarily
            original_model = None
            if detected_model != self.model_name:
                original_model = self.model_name
                self.logger.info(f"Switching from {self.model_name} to {detected_model} based on keywords")
                
                # Temporarily update model configuration
                self.model_name = detected_model
                if hasattr(self.model_adapter, 'model'):
                    self.model_adapter.model = detected_model
            
            # Use detected parameters unless explicitly overridden
            temperature = message.get('temperature', detected_temp)
            max_tokens = message.get('max_tokens', detected_tokens)
            
            # Generate response
            response = await self.model_adapter.generate(
                messages,
                options={
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            )
            
            # Restore original model if we switched
            if original_model:
                self.model_name = original_model
                if hasattr(self.model_adapter, 'model'):
                    self.model_adapter.model = original_model
            
            # Update registry for monitoring
            from shared.aish.src.registry.ci_registry import get_registry
            registry = get_registry()
            registry.update_ci_last_output(ci_name, {
                'user_message': user_content,
                'content': response['content'],
                'timestamp': message.get('timestamp'),
                'model': response.get('model', detected_model)
            })
            
            return {
                'type': 'response',
                'ai_id': self.ai_id,
                'content': response['content'],
                'model': response.get('model', detected_model),
                'thinking_level': self._get_thinking_level_name(detected_model, detected_temp),
                'usage': response.get('usage', {}),
                'latency': response.get('latency', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                'type': 'error',
                'ai_id': self.ai_id,
                'error': str(e)
            }
    
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
                    
                    # Store exchange in CI registry for Apollo-Rhetor coordination
                    # NOTE: This is a critical integration point for Apollo performance monitoring
                    # and Rhetor context injection. Exchanges are stored atomically with timestamps.
                    if ci_registry and response.get('type') == 'response':
                        try:
                            # Build exchange record
                            exchange = {
                                'user_message': message.get('content', message.get('message', '')),
                                'ai_response': response,
                                'timestamp': time.time()
                            }
                            # Store with title-cased component name for CI registry
                            ci_registry.update_ci_last_output(self.component.title(), exchange)
                        except Exception as e:
                            # Storage failure shouldn't break the flow
                            self.logger.debug(f"Failed to store exchange in CI registry: {e}")
                    
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
        """Start the CI specialist server."""
        # Initialize model adapter
        model_initialized = await self.initialize_model()
        if not model_initialized:
            self.logger.warning(f"Model initialization failed for {self.ai_id}, continuing without LLM support")
        
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
        """Run the CI specialist."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            self.logger.info(f"Shutting down {self.ai_id}")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            sys.exit(1)