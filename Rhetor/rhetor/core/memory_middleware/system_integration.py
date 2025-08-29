"""
System-Level Memory Integration for Tekton
Automatically adds memory to all CIs at startup.
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import logging

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        state_checkpoint,
        ci_orchestrated,
        ci_collaboration,
        danger_zone
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
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def ci_orchestrated(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def ci_collaboration(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

from .universal_adapter import get_universal_adapter
from shared.aish.src.registry.ci_registry import get_registry

logger = logging.getLogger(__name__)


@architecture_decision(
    title="System-Level Memory Integration",
    description="Automatic memory initialization for all Tekton CIs at startup",
    rationale="Zero-configuration memory for all CIs, configurable per CI type",
    alternatives_considered=["Manual per-CI setup", "Opt-in only", "External service"],
    impacts=["system_startup", "all_cis", "memory_persistence"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
@ci_orchestrated(
    title="Tekton Memory System",
    description="Orchestrates memory for entire CI ecosystem",
    orchestrator="memory_system",
    workflow=["load_config", "initialize_cis", "patch_handlers", "monitor"],
    ci_capabilities=["automatic_memory", "coordinated_memories", "system_wide_patterns"]
)
class TektonMemorySystem:
    """
    System-level memory integration for all Tekton CIs.
    Reads configuration and automatically initializes memory for each CI.
    """
    
    @state_checkpoint(
        title="Memory Configuration State",
        description="Persistent configuration for all CI memory settings",
        state_type="configuration",
        persistence=True,
        consistency_requirements="YAML format preservation",
        recovery_strategy="Load defaults if corrupted"
    )
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path.home() / '.tekton' / 'memory_config.yaml'
        self.adapter = get_universal_adapter()
        self.registry = get_registry()
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load memory configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # Default configuration
        return {
            'global': {
                'enabled': True,
                'auto_initialize': True,
                'default_training_stage': 'explicit'
            },
            'ci_configs': {
                'apollo': {
                    'injection_style': 'natural',
                    'training_stage': 'minimal',
                    'memory_tiers': ['short', 'medium', 'long', 'latent'],
                    'focus': 'decisions and priorities'
                },
                'prometheus': {
                    'injection_style': 'structured',
                    'training_stage': 'minimal',
                    'memory_tiers': ['short', 'medium', 'long', 'latent'],
                    'focus': 'patterns and predictions'
                },
                'ergon': {
                    'injection_style': 'natural',
                    'training_stage': 'occasional',
                    'memory_tiers': ['short', 'medium', 'long', 'latent'],
                    'focus': 'solutions and patterns'
                },
                'sophia': {
                    'injection_style': 'structured',
                    'training_stage': 'autonomous',
                    'memory_tiers': ['short', 'medium', 'long', 'latent'],
                    'focus': 'all memories'  # Sophia remembers everything
                },
                'hermes': {
                    'injection_style': 'minimal',
                    'training_stage': 'explicit',
                    'memory_tiers': ['short', 'medium'],
                    'focus': 'federation and connections'
                },
                'rhetor': {
                    'injection_style': 'minimal',
                    'training_stage': 'explicit',
                    'memory_tiers': ['short'],
                    'focus': 'model management'
                },
                'terma': {
                    'injection_style': 'natural',
                    'training_stage': 'minimal',
                    'memory_tiers': ['short', 'medium'],
                    'focus': 'user interactions'
                }
            }
        }
    
    @integration_point(
        title="CI Memory Initialization",
        description="Initialize memory for all registered CIs at startup",
        target_component="All CIs",
        protocol="batch_initialization",
        data_flow="registry → config → memory_init → all_cis",
        integration_date="2025-08-28"
    )
    @ci_collaboration(
        title="System-Wide Memory Setup",
        description="Coordinate memory initialization across all CIs",
        participants=["all_registered_cis"],
        coordination_method="sequential_init",
        synchronization="startup_time"
    )
    async def initialize_all_ci_memory(self):
        """Initialize memory for all registered CIs."""
        if not self.config['global']['enabled']:
            logger.info("Memory system disabled in config")
            return
        
        # Get all registered CIs
        all_cis = list(self.registry.get_all().keys())
        
        initialized = []
        for ci_name in all_cis:
            try:
                # Get CI-specific config or use defaults
                ci_config = self.config['ci_configs'].get(
                    ci_name.lower(),
                    self._get_default_config_for_ci(ci_name)
                )
                
                # Initialize memory for this CI
                self.adapter.initialize_ci_memory(ci_name, ci_config)
                initialized.append(ci_name)
                
                logger.info(f"Memory initialized for {ci_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize memory for {ci_name}: {e}")
        
        logger.info(f"Memory system initialized for {len(initialized)} CIs: {initialized}")
        return initialized
    
    def _get_default_config_for_ci(self, ci_name: str) -> Dict:
        """Get default config based on CI type."""
        # Check if it's a specialized CI
        ci_lower = ci_name.lower()
        
        if 'apollo' in ci_lower:
            base = 'apollo'
        elif 'prometheus' in ci_lower:
            base = 'prometheus'
        elif 'ergon' in ci_lower:
            base = 'ergon'
        elif 'sophia' in ci_lower:
            base = 'sophia'
        else:
            # Generic config
            return {
                'injection_style': 'natural',
                'training_stage': 'explicit',
                'memory_tiers': ['short', 'medium'],
                'focus': 'general'
            }
        
        # Return base config
        return self.config['ci_configs'].get(base, {})
    
    def save_config(self):
        """Save current configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        logger.info(f"Saved memory config to {self.config_file}")
    
    def update_ci_config(self, ci_name: str, config: Dict):
        """Update configuration for specific CI."""
        self.config['ci_configs'][ci_name.lower()] = config
        self.save_config()
        
        # Reinitialize with new config
        self.adapter.initialize_ci_memory(ci_name, config)
    
    def get_system_status(self) -> Dict:
        """Get status of entire memory system."""
        return {
            'enabled': self.config['global']['enabled'],
            'initialized_cis': list(self.adapter.enabled_cis),
            'total_memory_managers': len(self.adapter.memory_managers),
            'ci_statuses': self.adapter.get_memory_status()
        }


@danger_zone(
    title="Handler Monkey Patching",
    description="Runtime modification of CI handler classes",
    risk_level="medium",
    risks=["handler compatibility", "runtime errors", "version conflicts"],
    mitigation="Try-catch per handler, fallback to unpached",
    review_required=True
)
@integration_point(
    title="Handler Patching",
    description="Add memory capabilities to existing CI handlers",
    target_component="CI Handlers",
    protocol="monkey_patching",
    data_flow="handler_class → memory_wrapper → enhanced_handler",
    integration_date="2025-08-28"
)
async def patch_all_handlers():
    """
    Monkey-patch all CI handlers to add memory.
    This should be called at Tekton startup.
    """
    memory_system = TektonMemorySystem()
    
    # Initialize memory for all CIs
    await memory_system.initialize_all_ci_memory()
    
    # Patch Claude handler
    try:
        from shared.ai.claude_handler import ClaudeHandler
        from ..memory_middleware.integration import MemoryIntegratedClaudeHandler
        
        # Replace with memory-integrated version
        ClaudeHandler.__bases__ = (MemoryIntegratedClaudeHandler,)
        logger.info("Patched Claude handler with memory")
    except Exception as e:
        logger.error(f"Failed to patch Claude handler: {e}")
    
    # Patch other handlers as needed
    # ... add more handler patches here
    
    return memory_system


# Initialization script for Tekton startup
@integration_point(
    title="Tekton Memory Entry Point",
    description="Main entry point for memory system initialization",
    target_component="Tekton Main",
    protocol="startup_hook",
    data_flow="tekton_init → memory_init → all_systems",
    integration_date="2025-08-28"
)
@ci_orchestrated(
    title="Memory System Bootstrap",
    description="Bootstrap entire memory system at Tekton startup",
    orchestrator="main_system",
    workflow=["patch_handlers", "init_cis", "start_consolidation"],
    ci_capabilities=["system_wide_memory"]
)
async def initialize_tekton_memory():
    """
    Main initialization function to be called at Tekton startup.
    Add this to Tekton's main initialization.
    """
    logger.info("Initializing Tekton memory system...")
    
    try:
        # Patch all handlers
        memory_system = await patch_all_handlers()
        
        # Start background consolidation
        consolidation_task = asyncio.create_task(
            _consolidation_loop(memory_system)
        )
        
        logger.info("Tekton memory system initialized successfully")
        return memory_system
        
    except Exception as e:
        logger.error(f"Failed to initialize memory system: {e}")
        return None


async def _consolidation_loop(memory_system: TektonMemorySystem):
    """Background loop for memory consolidation."""
    while True:
        try:
            await asyncio.sleep(300)  # Every 5 minutes
            
            # Consolidate memory for all active CIs
            for ci_name in memory_system.adapter.enabled_cis:
                manager = memory_system.adapter.memory_managers.get(ci_name)
                if manager:
                    await manager._consolidate_phase(ci_name)
                    
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Consolidation error: {e}")