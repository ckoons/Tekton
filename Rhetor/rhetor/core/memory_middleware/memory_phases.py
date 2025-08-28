"""
Memory Phase Manager
Orchestrates the complete memory processing pipeline for CIs.
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import sys

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        performance_boundary,
        state_checkpoint,
        ci_orchestrated,
        ci_collaboration
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
    def performance_boundary(**kwargs):
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

# Imports should work without path manipulation

from .hook_manager import get_hook_manager, HookManager
from .memory_injector import MemoryInjector
from .memory_extractor import MemoryExtractor
from .habit_trainer import HabitTrainer

logger = logging.getLogger(__name__)


@dataclass
class MemoryMetrics:
    """Track memory system performance."""
    total_injections: int = 0
    total_extractions: int = 0
    avg_injection_time_ms: float = 0
    avg_extraction_time_ms: float = 0
    memories_referenced: int = 0
    memories_stored: int = 0
    habit_stage: str = 'explicit'
    memory_usage_rate: float = 0.0


@architecture_decision(
    title="Memory Phase Architecture",
    description="Complete memory pipeline orchestration for CI cognition",
    rationale="Provides structured phases for memory processing to enable consistent CI memory capabilities",
    alternatives_considered=["Ad-hoc memory access", "Direct database queries", "Manual memory management"],
    impacts=["ci_cognition", "memory_consistency", "performance"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
@ci_orchestrated(
    title="Memory Pipeline Orchestration",
    description="Coordinates all memory phases for CI processing",
    orchestrator="memory_phase_manager",
    workflow=["review", "inject", "process", "extract", "consolidate"],
    ci_capabilities=["contextual_awareness", "memory_formation", "pattern_recognition"]
)
class MemoryPhaseManager:
    """
    Orchestrates the complete memory pipeline.
    
    Phases:
    1. Review: Query all memory tiers
    2. Inject: Enrich prompt with memories
    3. Process: CI processes enriched prompt
    4. Extract: Analyze response for new memories
    5. Consolidate: Background memory organization
    """
    
    def __init__(self, engram_client=None):
        self.hook_manager: HookManager = get_hook_manager()
        self.injector = MemoryInjector(engram_client)
        self.extractor = MemoryExtractor(engram_client)
        self.habit_trainer = HabitTrainer()
        self.engram = engram_client
        
        self.metrics: Dict[str, MemoryMetrics] = {}
        self.consolidation_task = None
        
        # Register hooks
        self._register_hooks()
        
        # Start background consolidation
        self.start_consolidation()
        
    def _register_hooks(self):
        """Register all memory hooks with the hook manager."""
        # Pre-message: Memory injection
        self.hook_manager.register(
            'pre_message',
            self._inject_phase,
            priority=10  # Run early
        )
        
        # Post-response: Memory extraction  
        self.hook_manager.register(
            'post_response',
            self._extract_phase,
            priority=20  # Run after response
        )
        
        # Idle: Memory consolidation
        self.hook_manager.register(
            'idle_consolidation',
            self._consolidate_phase,
            priority=50
        )
        
        # Context change: Memory context switch
        self.hook_manager.register(
            'context_change',
            self._context_switch_phase,
            priority=30
        )
        
        logger.info("Memory hooks registered")
    
    @integration_point(
        title="Memory Pipeline Entry",
        description="Main entry point for memory-enhanced CI processing",
        target_component="CI System",
        protocol="memory_enrichment",
        data_flow="message → review → inject → training → enriched_message",
        integration_date="2025-08-28"
    )
    async def process_with_memory(
        self, 
        ci_name: str, 
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main entry point - process message with full memory pipeline.
        
        Args:
            ci_name: CI receiving the message
            message: Original message
            context: Optional context
            
        Returns:
            Memory-enriched message ready for CI processing
        """
        context = context or {}
        
        # Phase 1: Review memories (gather relevant context)
        enriched_message = await self._review_phase(ci_name, message, context)
        
        # Phase 2: Apply habit training
        trained_message = self._apply_training(ci_name, enriched_message)
        
        return trained_message
    
    async def _review_phase(self, ci_name: str, message: str, context: Dict) -> str:
        """Phase 1: Review and gather relevant memories."""
        import time
        start_time = time.time()
        
        try:
            # Use injector to gather and inject memories
            enriched = await self.injector.inject_memories(ci_name, message, context)
            
            # Update metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self._update_injection_metrics(ci_name, elapsed_ms)
            
            return enriched
            
        except Exception as e:
            logger.error(f"Review phase error: {e}")
            return message
    
    def _apply_training(self, ci_name: str, message: str) -> str:
        """Phase 2: Apply habit training modifications."""
        return self.habit_trainer.get_training_prompt(ci_name, message)
    
    async def _inject_phase(self, ci_name: str, message: str, context: Dict) -> str:
        """Hook: Pre-message memory injection."""
        return await self.process_with_memory(ci_name, message, context)
    
    async def _extract_phase(self, ci_name: str, message: str, response: str, context: Dict):
        """Hook: Post-response memory extraction."""
        import time
        start_time = time.time()
        
        try:
            # Extract memories from response
            memories = await self.extractor.extract_memories(
                ci_name, message, response, context
            )
            
            # Analyze for habit formation
            analysis = self.habit_trainer.analyze_response(ci_name, response)
            
            # Update metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self._update_extraction_metrics(ci_name, elapsed_ms, len(memories))
            
            # Update habit metrics
            metrics = self._get_metrics(ci_name)
            metrics.habit_stage = analysis['current_stage']
            metrics.memory_usage_rate = analysis['memory_usage_rate']
            
            if analysis['used_memory']:
                metrics.memories_referenced += 1
                
            logger.debug(f"Extracted {len(memories)} memories from {ci_name} response")
            
        except Exception as e:
            logger.error(f"Extract phase error: {e}")
    
    @ci_collaboration(
        title="Memory Consolidation",
        description="Background consolidation of CI memories",
        participants=["memory_system", "engram"],
        coordination_method="periodic_background",
        synchronization="async_periodic"
    )
    @performance_boundary(
        title="Consolidation Task",
        description="Memory tier migration and pattern extraction",
        sla="<5s per CI",
        optimization_notes="Runs during idle, batches operations",
        measured_impact="No impact on active processing"
    )
    async def _consolidate_phase(self, ci_name: str):
        """Hook: Idle-time memory consolidation."""
        if not self.engram:
            return
            
        try:
            # Move memories between tiers based on age and significance
            await self._consolidate_memory_tiers(ci_name)
            
            # Extract patterns from repeated memories
            await self._extract_memory_patterns(ci_name)
            
            # Clean up old/redundant memories
            await self._cleanup_memories(ci_name)
            
            logger.debug(f"Consolidated memories for {ci_name}")
            
        except Exception as e:
            logger.error(f"Consolidation error: {e}")
    
    @state_checkpoint(
        title="Context Switch Handler",
        description="Manages CI memory state during context changes",
        state_type="context_transition",
        persistence=True,
        consistency_requirements="Preserve context continuity",
        recovery_strategy="Snapshot and restore"
    )
    async def _context_switch_phase(self, ci_name: str, old_context: Dict, new_context: Dict):
        """Hook: Handle context switches."""
        try:
            # Save current context memories
            if old_context.get('project'):
                await self._save_context_memories(ci_name, old_context)
            
            # Pre-load new context memories
            if new_context.get('project'):
                await self._preload_context_memories(ci_name, new_context)
            
            # Clear injector cache for fresh context
            self.injector.clear_cache()
            
            logger.debug(f"Context switch for {ci_name}: {old_context.get('project')} -> {new_context.get('project')}")
            
        except Exception as e:
            logger.error(f"Context switch error: {e}")
    
    async def _consolidate_memory_tiers(self, ci_name: str):
        """Move memories between short/medium/long-term tiers."""
        if not self.engram:
            return
            
        # Get aged short-term memories (>1 hour old)
        aged_memories = await self.engram.get_aged_memories(
            ci_name, 
            compartment='session',
            older_than_minutes=60
        )
        
        for memory in aged_memories:
            significance = memory.get('metadata', {}).get('significance', 0)
            
            if significance > 0.7:
                # Move to long-term
                await self.engram.move_memory(
                    memory['id'],
                    from_compartment='session',
                    to_compartment='longterm'
                )
            elif significance > 0.4:
                # Move to medium-term
                await self.engram.move_memory(
                    memory['id'],
                    from_compartment='session',
                    to_compartment='projects'
                )
            # else: Let it fade from short-term
    
    @ci_collaboration(
        title="Pattern Extraction",
        description="Extract patterns from CI memory repetition",
        participants=["memory_extractor", "engram"],
        coordination_method="pattern_analysis",
        synchronization="batch_processing"
    )
    async def _extract_memory_patterns(self, ci_name: str):
        """Extract patterns from repeated memories."""
        if not self.engram:
            return
            
        # Find repeated concepts across memories
        patterns = await self.engram.find_patterns(ci_name)
        
        for pattern in patterns:
            if pattern['frequency'] >= 3:
                # Create a pattern memory
                await self.engram.add_memory(
                    client_id=ci_name,
                    content=f"Pattern: {pattern['concept']} (observed {pattern['frequency']} times)",
                    metadata={
                        'type': 'pattern',
                        'frequency': pattern['frequency'],
                        'examples': pattern['examples'][:3]
                    },
                    compartment='longterm'
                )
    
    async def _cleanup_memories(self, ci_name: str):
        """Remove old, redundant, or low-significance memories."""
        if not self.engram:
            return
            
        # Remove old low-significance memories
        await self.engram.cleanup_memories(
            ci_name,
            older_than_days=7,
            significance_below=0.3
        )
        
        # Deduplicate similar memories
        await self.engram.deduplicate_memories(ci_name)
    
    async def _save_context_memories(self, ci_name: str, context: Dict):
        """Save memories related to current context."""
        if not self.engram:
            return
            
        # Create context snapshot
        await self.engram.add_memory(
            client_id=ci_name,
            content=f"Context snapshot for {context.get('project', 'unknown')}",
            metadata={
                'type': 'context_snapshot',
                'context': context,
                'timestamp': datetime.now().isoformat()
            },
            compartment='projects'
        )
    
    async def _preload_context_memories(self, ci_name: str, context: Dict):
        """Pre-load memories for new context."""
        if not self.engram:
            return
            
        # Warm up cache with relevant memories
        project = context.get('project')
        if project:
            memories = await self.engram.search_memories(
                ci_name,
                query=f"project:{project}",
                limit=10
            )
            
            # Pre-populate injector cache
            cache_key = f"{ci_name}_context_{project}"
            self.injector.cache[cache_key] = memories
    
    def start_consolidation(self):
        """Start background memory consolidation task."""
        if not self.consolidation_task:
            self.consolidation_task = asyncio.create_task(
                self._consolidation_loop()
            )
            logger.info("Started memory consolidation task")
    
    @performance_boundary(
        title="Consolidation Loop",
        description="Periodic background memory consolidation",
        sla="Every 5 minutes",
        optimization_notes="Low priority background task",
        measured_impact="<1% CPU usage"
    )
    async def _consolidation_loop(self):
        """Background loop for periodic consolidation."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Consolidate for all active CIs
                for ci_name in self.metrics.keys():
                    await self._consolidate_phase(ci_name)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Consolidation loop error: {e}")
    
    def stop_consolidation(self):
        """Stop background consolidation task."""
        if self.consolidation_task:
            self.consolidation_task.cancel()
            self.consolidation_task = None
    
    def _get_metrics(self, ci_name: str) -> MemoryMetrics:
        """Get or create metrics for CI."""
        if ci_name not in self.metrics:
            self.metrics[ci_name] = MemoryMetrics()
        return self.metrics[ci_name]
    
    def _update_injection_metrics(self, ci_name: str, elapsed_ms: float):
        """Update injection metrics."""
        metrics = self._get_metrics(ci_name)
        metrics.total_injections += 1
        
        # Running average
        metrics.avg_injection_time_ms = (
            (metrics.avg_injection_time_ms * (metrics.total_injections - 1) + elapsed_ms) /
            metrics.total_injections
        )
    
    def _update_extraction_metrics(self, ci_name: str, elapsed_ms: float, memories_count: int):
        """Update extraction metrics."""
        metrics = self._get_metrics(ci_name)
        metrics.total_extractions += 1
        metrics.memories_stored += memories_count
        
        # Running average
        metrics.avg_extraction_time_ms = (
            (metrics.avg_extraction_time_ms * (metrics.total_extractions - 1) + elapsed_ms) /
            metrics.total_extractions
        )
    
    def get_metrics_report(self, ci_name: Optional[str] = None) -> Dict:
        """Get metrics report for CI or all CIs."""
        if ci_name:
            metrics = self._get_metrics(ci_name)
            return {
                'ci_name': ci_name,
                'total_injections': metrics.total_injections,
                'total_extractions': metrics.total_extractions,
                'avg_injection_time_ms': round(metrics.avg_injection_time_ms, 2),
                'avg_extraction_time_ms': round(metrics.avg_extraction_time_ms, 2),
                'memories_referenced': metrics.memories_referenced,
                'memories_stored': metrics.memories_stored,
                'habit_stage': metrics.habit_stage,
                'memory_usage_rate': f"{metrics.memory_usage_rate:.1%}"
            }
        else:
            # Return all CI metrics
            return {
                ci: self.get_metrics_report(ci)
                for ci in self.metrics.keys()
            }