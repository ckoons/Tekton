"""
Universal Memory Hook Adapter for All Tekton CIs
Makes memory integration work across different CI types and models.
"""

import asyncio
from typing import Dict, Any, Optional, Protocol
from abc import abstractmethod
import logging
from pathlib import Path
import sys

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        ci_orchestrated,
        fuzzy_match,
        state_checkpoint
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def ci_orchestrated(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def fuzzy_match(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Removed path manipulation - imports should work without it

from .memory_phases import MemoryPhaseManager
from shared.aish.src.registry.ci_registry import get_registry

logger = logging.getLogger(__name__)


class CIHandler(Protocol):
    """Protocol that all CI handlers must implement for memory hooks."""
    
    @abstractmethod
    async def process_message(self, ci_name: str, message: str) -> str:
        """Process a message and return response."""
        pass


@architecture_decision(
    title="Universal Memory Adapter",
    description="Model-agnostic memory integration for all CI types",
    rationale="Single adapter works with Claude, GPT, local models, and streaming without CI-specific code",
    alternatives_considered=["Per-model adapters", "CI-specific implementations", "Direct model modification"],
    impacts=["all_ci_memory", "unified_interface", "model_portability"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
@ci_orchestrated(
    title="Universal CI Memory",
    description="Adds memory to any CI regardless of underlying model",
    orchestrator="universal_adapter",
    workflow=["detect_model", "configure_memory", "wrap_handler", "inject_extract"],
    ci_capabilities=["model_agnostic_memory", "adaptive_configuration", "streaming_support"]
)
class UniversalMemoryAdapter:
    """
    Universal adapter that adds memory to ANY CI type.
    Works with Claude, local models, streaming models, etc.
    """
    
    def __init__(self):
        self.memory_managers: Dict[str, MemoryPhaseManager] = {}
        self.registry = get_registry()
        self.enabled_cis = set()
        
    def initialize_ci_memory(self, ci_name: str, config: Optional[Dict] = None):
        """
        Initialize memory for a specific CI.
        
        Args:
            ci_name: Name of the CI
            config: Optional memory configuration
        """
        config = config or self._get_default_config(ci_name)
        
        # Create memory manager for this CI
        if ci_name not in self.memory_managers:
            # Get Engram client if available
            engram_client = self._get_engram_client(ci_name)
            
            # Create memory manager
            self.memory_managers[ci_name] = MemoryPhaseManager(engram_client)
            
            # Apply configuration
            self._apply_config(ci_name, config)
            
            self.enabled_cis.add(ci_name)
            logger.info(f"Initialized memory for {ci_name}")
    
    @fuzzy_match(
        title="Model Type Detection",
        description="Auto-detect CI model type for optimal memory configuration",
        algorithm="string_pattern_matching",
        examples=["claude->natural", "gpt->structured", "llama->minimal"],
        priority="exact_model > model_family > default"
    )
    def _get_default_config(self, ci_name: str) -> Dict:
        """Get default memory configuration for CI type."""
        ci_info = self.registry.get_ci(ci_name)
        
        if not ci_info:
            # Default configuration
            return {
                'injection_style': 'natural',
                'training_stage': 'explicit',
                'memory_tiers': ['short', 'medium', 'long', 'latent'],
                'auto_extract': True
            }
        
        # Determine config based on CI type
        model = ci_info.get('model', '').lower()
        
        if 'claude' in model:
            return {
                'injection_style': 'natural',
                'training_stage': 'minimal',  # Claude adapts quickly
                'memory_tiers': ['short', 'medium', 'long', 'latent'],
                'auto_extract': True
            }
        elif 'gpt' in model:
            return {
                'injection_style': 'structured',
                'training_stage': 'explicit',
                'memory_tiers': ['short', 'medium', 'long'],
                'auto_extract': True
            }
        elif 'llama' in model or 'mixtral' in model:
            return {
                'injection_style': 'minimal',  # Local models have less context
                'training_stage': 'shortened',
                'memory_tiers': ['short', 'medium'],
                'auto_extract': False  # Manual extraction for efficiency
            }
        else:
            # Generic streaming model
            return {
                'injection_style': 'minimal',
                'training_stage': 'explicit',
                'memory_tiers': ['short'],
                'auto_extract': False
            }
    
    def _apply_config(self, ci_name: str, config: Dict):
        """Apply configuration to CI's memory manager."""
        manager = self.memory_managers[ci_name]
        
        # Set injection style
        if 'injection_style' in config:
            manager.injector.set_style(config['injection_style'])
        
        # Set training stage
        if 'training_stage' in config:
            manager.habit_trainer.set_stage(ci_name, config['training_stage'])
        
        # Configure extraction
        if 'auto_extract' in config:
            manager.auto_extract = config['auto_extract']
    
    @integration_point(
        title="Handler Wrapping",
        description="Transparently wraps any CI handler with memory",
        target_component="CI Handler",
        protocol="wrapper_pattern",
        data_flow="handler → memory_wrapper → enhanced_handler",
        integration_date="2025-08-28"
    )
    async def wrap_handler(self, handler: CIHandler, ci_name: str) -> CIHandler:
        """
        Wrap any CI handler with memory capabilities.
        
        Args:
            handler: Original CI handler
            ci_name: Name of the CI
            
        Returns:
            Memory-enhanced handler
        """
        if ci_name not in self.enabled_cis:
            self.initialize_ci_memory(ci_name)
        
        class MemoryWrappedHandler:
            def __init__(self, original_handler, memory_adapter):
                self.handler = original_handler
                self.adapter = memory_adapter
                
            async def process_message(self, ci_name: str, message: str) -> str:
                # Pre-process with memory injection
                enriched_message = await self.adapter.inject_memory(
                    ci_name, message
                )
                
                # Original processing
                response = await self.handler.process_message(
                    ci_name, enriched_message
                )
                
                # Post-process with memory extraction
                await self.adapter.extract_memory(
                    ci_name, message, response
                )
                
                return response
        
        return MemoryWrappedHandler(handler, self)
    
    async def inject_memory(self, ci_name: str, message: str) -> str:
        """Inject relevant memories into message."""
        if ci_name not in self.memory_managers:
            return message
            
        manager = self.memory_managers[ci_name]
        context = {'ci_name': ci_name}
        
        return await manager.process_with_memory(ci_name, message, context)
    
    async def extract_memory(self, ci_name: str, message: str, response: str):
        """Extract significant memories from response."""
        if ci_name not in self.memory_managers:
            return
            
        manager = self.memory_managers[ci_name]
        context = {'ci_name': ci_name}
        
        # Fire and forget
        asyncio.create_task(
            manager._extract_phase(ci_name, message, response, context)
        )
    
    def get_memory_status(self, ci_name: Optional[str] = None) -> Dict:
        """Get memory status for CI(s)."""
        if ci_name:
            if ci_name not in self.memory_managers:
                return {'error': f'No memory manager for {ci_name}'}
            
            return self.memory_managers[ci_name].get_metrics_report(ci_name)
        
        # Return all CI statuses
        return {
            ci: self.memory_managers[ci].get_metrics_report(ci)
            for ci in self.memory_managers
        }
    
    def _get_engram_client(self, ci_name: str):
        """Get or create Engram client for CI."""
        try:
            # Import Engram if available
            from Engram.engram.core.memory_manager import MemoryManager
            
            # Create client for this CI
            return MemoryManager(client_id=ci_name)
        except ImportError:
            logger.warning(f"Engram not available for {ci_name}")
            return None


@architecture_decision(
    title="Streaming Memory Support",
    description="Memory integration for token-by-token streaming models",
    rationale="Streaming models need special handling for memory accumulation",
    alternatives_considered=["Buffer all tokens", "No streaming support", "Periodic injection"],
    impacts=["streaming_models", "real_time_memory", "token_processing"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
class StreamingMemoryAdapter:
    """
    Special adapter for streaming models that process token-by-token.
    """
    
    @state_checkpoint(
        title="Streaming Session State",
        description="Tracks active streaming sessions for memory accumulation",
        state_type="session_tracking",
        persistence=False,
        consistency_requirements="Token order preservation",
        recovery_strategy="Discard incomplete streams"
    )
    def __init__(self, memory_adapter: UniversalMemoryAdapter):
        self.adapter = memory_adapter
        self.active_streams: Dict[str, Dict] = {}
        
    async def start_stream(self, ci_name: str, message: str) -> str:
        """Start a streaming session with memory injection."""
        # Inject memories into initial message
        enriched = await self.adapter.inject_memory(ci_name, message)
        
        # Track streaming session
        self.active_streams[ci_name] = {
            'original_message': message,
            'enriched_message': enriched,
            'accumulated_response': []
        }
        
        return enriched
    
    async def process_token(self, ci_name: str, token: str):
        """Process a streaming token."""
        if ci_name in self.active_streams:
            self.active_streams[ci_name]['accumulated_response'].append(token)
    
    async def end_stream(self, ci_name: str):
        """End streaming session and extract memories."""
        if ci_name not in self.active_streams:
            return
            
        session = self.active_streams[ci_name]
        full_response = ''.join(session['accumulated_response'])
        
        # Extract memories from complete response
        await self.adapter.extract_memory(
            ci_name,
            session['original_message'],
            full_response
        )
        
        # Clean up
        del self.active_streams[ci_name]


# Global singleton
_universal_adapter: Optional[UniversalMemoryAdapter] = None


@integration_point(
    title="Global Memory Adapter",
    description="Singleton access point for universal memory system",
    target_component="All CI Systems",
    protocol="singleton_pattern",
    data_flow="CI → get_adapter → memory_system",
    integration_date="2025-08-28"
)
def get_universal_adapter() -> UniversalMemoryAdapter:
    """Get the universal memory adapter singleton."""
    global _universal_adapter
    if _universal_adapter is None:
        _universal_adapter = UniversalMemoryAdapter()
    return _universal_adapter