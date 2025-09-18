"""
Integration Module for Memory Middleware with Claude Handler
Connects the memory system to the Claude processing pipeline.
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import sys
import logging

# Imports should work without path manipulation

from .memory_phases import MemoryPhaseManager
from shared.ai.claude_handler import ClaudeHandler

logger = logging.getLogger(__name__)


class MemoryIntegratedClaudeHandler(ClaudeHandler):
    """
    Extended Claude handler with memory middleware integration.
    
    Adds transparent memory injection and extraction to Claude processing.
    """
    
    def __init__(self, engram_client=None, enable_memory: bool = True):
        super().__init__()
        self.memory_manager: Optional[MemoryPhaseManager] = None
        self.memory_enabled = False  # FORCE DISABLE MEMORY FOR DEBUGGING
        
        # Don't even initialize memory manager for now
        logger.info("Memory middleware DISABLED for debugging Node.js issues")
    
    async def handle_forwarded_message(self, ci_name: str, message: str) -> str:
        """
        Override to add memory processing.
        
        Args:
            ci_name: Name of the CI
            message: Message to process
            
        Returns:
            Response from Claude with memory processing
        """
        # COMPLETE NO-OP FOR CLAUDE CIs - Direct passthrough, no memory at all
        # This bypasses ALL memory processing to debug Node.js heap issues
        
        # Pure prompt/response - no memory injection, no extraction, nothing
        response = await super().handle_forwarded_message(ci_name, message)
        
        return response
    
    def toggle_memory(self, enabled: Optional[bool] = None) -> bool:
        """Toggle memory system on/off."""
        if enabled is not None:
            self.memory_enabled = enabled
        else:
            self.memory_enabled = not self.memory_enabled
            
        if self.memory_manager:
            self.memory_manager.hook_manager.toggle(self.memory_enabled)
            
        logger.info(f"Memory system {'enabled' if self.memory_enabled else 'disabled'}")
        return self.memory_enabled
    
    def get_memory_metrics(self, ci_name: Optional[str] = None) -> Dict:
        """Get memory system metrics."""
        if not self.memory_manager:
            return {'error': 'Memory system not initialized'}
            
        return self.memory_manager.get_metrics_report(ci_name)
    
    def get_training_progress(self, ci_name: str) -> Dict:
        """Get habit training progress for CI."""
        if not self.memory_manager:
            return {'error': 'Memory system not initialized'}
            
        return self.memory_manager.habit_trainer.get_progress_report(ci_name)
    
    def set_training_stage(self, ci_name: str, stage: str):
        """Manually set training stage for CI."""
        if not self.memory_manager:
            raise RuntimeError("Memory system not initialized")
            
        self.memory_manager.habit_trainer.set_stage(ci_name, stage)
    
    def set_injection_style(self, style: str):
        """Set memory injection style (natural, structured, minimal)."""
        if not self.memory_manager:
            raise RuntimeError("Memory system not initialized")
            
        self.memory_manager.injector.set_style(style)


def patch_claude_handler():
    """
    Monkey-patch the existing Claude handler to add memory.
    
    This allows adding memory to existing systems without changing imports.
    """
    import shared.ai.claude_handler as handler_module
    
    # Store original
    original_handler = handler_module.ClaudeHandler
    
    # Replace with memory-integrated version
    handler_module.ClaudeHandler = MemoryIntegratedClaudeHandler
    
    # Store reference to original for restoration
    handler_module._original_handler = original_handler
    
    logger.info("Claude handler patched with memory integration")


def unpatch_claude_handler():
    """Restore original Claude handler."""
    import shared.ai.claude_handler as handler_module
    
    if hasattr(handler_module, '_original_handler'):
        handler_module.ClaudeHandler = handler_module._original_handler
        del handler_module._original_handler
        logger.info("Claude handler restored to original")


# Singleton instance for direct use
_integrated_handler: Optional[MemoryIntegratedClaudeHandler] = None


def get_memory_integrated_handler(engram_client=None) -> MemoryIntegratedClaudeHandler:
    """Get singleton memory-integrated Claude handler."""
    global _integrated_handler
    if _integrated_handler is None:
        _integrated_handler = MemoryIntegratedClaudeHandler(engram_client)
    return _integrated_handler