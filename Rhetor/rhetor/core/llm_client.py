"""
Unified LLM Client that uses the CI Registry instead of direct provider connections.

This replaces the old multi-provider LLM client with a unified approach
that discovers and communicates with CI specialists via the registry.
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from datetime import datetime

# Import the new shared CI components
import sys
import os
# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.env import TektonEnviron

from landmarks import architecture_decision, integration_point

from shared.ai.simple_ai import ai_send, ai_send_sync
from dataclasses import dataclass
from typing import AsyncIterator

@dataclass
class CIResponse:
    """Response from a CI specialist."""
    content: str
    ai_id: str
    model: str
    metadata: Dict[str, Any] = None

# LLM client now uses simple_ai for direct CI communication
# All functionality previously from tekton_llm_client is now implemented locally

# Create placeholder classes/functions for compatibility
class PromptTemplateRegistry:
    def __init__(self):
        self.templates = {}
        
class PromptTemplate:
    pass
    
class JSONParser:
    pass
    
def parse_json(text):
    import json
    try:
        return json.loads(text)
    except:
        return None
        
def extract_json(text):
    import json
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return None
    
class StreamHandler:
    pass
    
async def collect_stream(stream):
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
    return ''.join(chunks)
    
def stream_to_string(stream):
    return ''.join(stream)
    
class StructuredOutputParser:
    pass
    
class OutputFormat:
    pass
    
class ClientSettings:
    pass
    
class LLMSettings:
    pass
    
def load_settings(component):
    return {}
    
def get_env(key, default=None):
    from shared.env import TektonEnviron
    return TektonEnviron.get(key, default)

from landmarks import architecture_decision, integration_point, state_checkpoint

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Rhetor LLM Client Using Simple CI System",
    rationale="Direct socket communication with fixed CI ports via simple_ai",
    alternatives_considered=["Registry-based discovery", "Complex routing", "Connection pooling"],
    impacts=["simplicity", "reliability", "fixed_port_mapping"],
    decided_by="Casey"
)
@integration_point(
    title="Direct CI Socket Communication",
    target_component="CI Specialists (ports 45000-50000)",
    protocol="Direct socket via simple_ai",
    data_flow="Request → simple_ai → Fixed Port Socket → CI Response"
)
@architecture_decision(
    title="One Queue One Socket One CI Architecture",
    rationale="Each CI has exactly one message queue and one socket connection",
    alternatives_considered=["Connection pooling", "Load balancing", "Multiple queues"],
    impacts=["simplicity", "predictability", "maintainability"],
    decided_by="Casey"
)
class LLMClient:
    """
    Drop-in replacement for the old LLMClient that uses the unified CI registry.
    
    This maintains the same API interface while routing all requests through
    the CI Registry for dynamic specialist selection.
    """
    
    def __init__(self, default_provider=None, default_model=None):
        """
        Initialize the unified LLM client.
        
        Args:
            default_provider: Ignored - kept for compatibility
            default_model: Ignored - kept for compatibility
        """
        # Using simple_ai - no registry or socket client needed
        self.providers = {}  # Compatibility mapping
        self.default_provider_id = "unified"
        self.default_model = "registry-selected"
        
        # Initialize prompt template registry for compatibility
        self.prompt_registry = PromptTemplateRegistry()
        
        # Load default templates if directory exists
        templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        if os.path.exists(templates_dir):
            try:
                # Try the new method name first
                if hasattr(self.prompt_registry, 'load_templates_from_directory'):
                    self.prompt_registry.load_templates_from_directory(templates_dir)
                elif hasattr(self.prompt_registry, 'load_from_directory'):
                    self.prompt_registry.load_from_directory(templates_dir)
                else:
                    logger.warning("No template loading method available")
            except Exception as e:
                logger.warning(f"Failed to load templates: {e}")
        
        logger.info("Initialized unified LLM client with CI Registry")
    
    async def initialize(self):
        """Initialize the client and discover CIs."""
        try:
            # Discover available CIs
            ais = await self.registry.discover()
            logger.info(f"Discovered {len(ais)} CI specialists")
            
            # Create compatibility provider mapping
            self._create_provider_mapping()
            
        except Exception as e:
            logger.warning(f"Failed to discover CIs: {e}")
    
    def _create_provider_mapping(self):
        """Create compatibility mapping for old provider names."""
        # Map old providers to roles
        self.providers = {
            # Providers removed - using simple_ai directly
        }
    
    @property
    def is_initialized(self):
        """Check if the client is initialized."""
        return True  # Always ready with registry
    
    def get_provider(self, provider_id=None):
        """Get a provider by ID - returns unified provider."""
        if provider_id and provider_id in self.providers:
            return self.providers[provider_id]
        return None  # No providers - using simple_ai directly
    
    def list_providers(self):
        """List available providers - returns compatibility list."""
        return list(self.providers.keys())
    
    def list_models(self, provider_id=None):
        """List available models - returns CI specialists."""
        # This is now async but kept sync for compatibility
        # Real implementation would need to handle this properly
        return ["registry-managed"]
    
    def get_model_info(self, model_id, provider_id=None):
        """Get model information - returns CI info."""
        return {
            "id": model_id,
            "name": "CI Registry Managed Model",
            "provider": "unified",
            "context_window": 100000,
            "capabilities": ["chat", "completion"]
        }
    
    async def complete(self, prompt, model=None, provider_id=None, **kwargs):
        """
        Complete a prompt using the unified CI client.
        
        Maps old provider/model selection to role-based routing.
        """
        # Map provider/model to role
        role = self._map_to_role(provider_id, model, kwargs.get('task_type'))
        
        # Extract relevant parameters
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 4000)
        
        # Map role to CI component name
        role_to_component = {
            'orchestration': 'rhetor',
            'code-analysis': 'apollo',
            'knowledge': 'athena',
            'general': 'numa'
        }
        
        component = role_to_component.get(role, 'numa')
        
        # Get AI port from TektonEnviron
        ai_port = TektonEnviron.get(f"{component.upper()}_AI_PORT")
        if not ai_port:
            # Fallback to default if not found
            ai_port = 44016  # NUMA default
            logger.warning(f"No AI port found for {component}, using default {ai_port}")
        else:
            ai_port = int(ai_port)
        
        # Build AI ID and connection info
        # Use -ai suffix for the AI specialists (not -ci)
        ai_id = f"{component}-ai"
        host = 'localhost'
        port = ai_port
        
        # Send message using simple_ai
        try:
            response_text = await ai_send(ai_id, prompt, host, port)
        except Exception as e:
            raise RuntimeError(f"Failed to get response from {ai_id}: {e}")
        
        # Convert to old format
        return {
            'content': response_text,
            'model': 'llama3.3:70b',
            'provider': ai_id,
            'usage': {
                'prompt_tokens': len(prompt.split()),
                'completion_tokens': len(response_text.split()),
                'total_tokens': len(prompt.split()) + len(response_text.split())
            }
        }
    
    async def complete_stream(self, prompt, model=None, provider_id=None, **kwargs):
        """
        Stream completion using unified client.
        
        Currently returns full response as single chunk for compatibility.
        """
        # Get full response
        response = await self.complete(prompt, model, provider_id, **kwargs)
        
        # Yield as single chunk
        yield response['content']
    
    def _map_to_role(self, provider_id: Optional[str], model: Optional[str], 
                     task_type: Optional[str]) -> str:
        """Map old provider/model/task to CI role."""
        # Task type takes precedence
        if task_type:
            role_map = {
                'code': 'code-analysis',
                'planning': 'planning',
                'reasoning': 'knowledge-synthesis',
                'chat': 'messaging',
                'orchestration': 'orchestration',
                'memory': 'memory',
                'agent': 'agent-coordination'
            }
            if task_type in role_map:
                return role_map[task_type]
        
        # Provider-based mapping
        if provider_id:
            provider_role_map = {
                'anthropic': 'orchestration',
                'openai': 'code-analysis',
                'ollama': 'general'
            }
            if provider_id in provider_role_map:
                return provider_role_map[provider_id]
        
        # Model-based mapping
        if model:
            if 'opus' in model.lower():
                return 'code-analysis'
            elif 'sonnet' in model.lower():
                return 'orchestration'
            elif 'haiku' in model.lower():
                return 'messaging'
        
        return 'general'
    
    async def get_default_model(self):
        """Get default model - returns first available AI."""
        ais = await self.registry.discover()
        if ais:
            return ais[0].id
        return "none-available"
    
    def set_default_model(self, model_id, provider_id=None):
        """Set default model - no-op for compatibility."""
        logger.info(f"Default model request: {model_id} - using role-based selection")
        return True
    
    async def cleanup(self):
        """Cleanup resources."""
        # No cleanup needed for shared socket client


# UnifiedProvider class removed - using simple_ai directly
