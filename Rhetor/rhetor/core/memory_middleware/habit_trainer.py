"""
Habit Trainer for Progressive Memory Training
Gradually trains CIs to use memory naturally through progressive simplification.
"""

import json
import random
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        state_checkpoint,
        ci_orchestrated,
        performance_boundary,
        fuzzy_match
    )
except ImportError:
    def architecture_decision(**kwargs):
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
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    def fuzzy_match(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = logging.getLogger(__name__)


@dataclass
class TrainingProgress:
    """Track CI's memory habit development."""
    ci_name: str
    current_stage: str
    stage_started: datetime
    interactions_at_stage: int
    memory_usage_rate: float  # % of responses that reference memory
    successful_recalls: int
    total_attempts: int
    stage_history: List[Dict] = field(default_factory=list)
    
    def advance_stage(self, new_stage: str):
        """Advance to next training stage."""
        self.stage_history.append({
            'stage': self.current_stage,
            'completed': datetime.now().isoformat(),
            'interactions': self.interactions_at_stage,
            'success_rate': self.memory_usage_rate
        })
        self.current_stage = new_stage
        self.stage_started = datetime.now()
        self.interactions_at_stage = 0
        
    def update_metrics(self, used_memory: bool):
        """Update training metrics after interaction."""
        self.interactions_at_stage += 1
        self.total_attempts += 1
        if used_memory:
            self.successful_recalls += 1
        # Rolling average
        self.memory_usage_rate = self.successful_recalls / max(1, self.total_attempts)
        
    def ready_for_advancement(self) -> bool:
        """Check if CI is ready for next stage."""
        # Need sufficient interactions and good success rate
        return (
            self.interactions_at_stage >= 10 and
            self.memory_usage_rate >= 0.6
        )


@architecture_decision(
    title="Progressive Habit Training",
    description="Gradually trains CIs to use memory naturally through stages",
    rationale="Based on Casey's insight that habits form through progressive simplification",
    alternatives_considered=["Immediate full autonomy", "Fixed prompting", "Manual only"],
    impacts=["ci_autonomy", "memory_adoption", "natural_behavior"],
    decided_by="Casey",
    decision_date="2025-08-28"
)
@ci_orchestrated(
    title="Memory Habit Development",
    description="Progressive training pipeline for CI memory habits",
    orchestrator="habit_trainer",
    workflow=["explicit", "shortened", "minimal", "occasional", "autonomous"],
    ci_capabilities=["memory_reference", "contextual_recall", "autonomous_memory_use"]
)
class HabitTrainer:
    """
    Progressively trains CIs to develop memory habits.
    
    Training stages:
    1. Explicit: "/recall relevant memories" - Full instructions
    2. Shortened: "/r" - Abbreviated prompt
    3. Minimal: "/" - Just a nudge
    4. Occasional: 50% prompted, 50% natural
    5. Autonomous: CI uses memory naturally without prompts
    
    Based on Casey's observation that habits form through progressive simplification.
    """
    
    TRAINING_STAGES = [
        'explicit',
        'shortened', 
        'minimal',
        'occasional',
        'autonomous'
    ]
    
    STAGE_PROMPTS = {
        'explicit': "\n[Please recall and reference any relevant memories from our previous discussions]\n",
        'shortened': "\n/r\n",
        'minimal': "\n/\n",
        'occasional': None,  # Determined dynamically
        'autonomous': ""
    }
    
    @state_checkpoint(
        title="Training Progress State",
        description="Persistent tracking of CI memory habit development",
        state_type="training_progress",
        persistence=True,
        consistency_requirements="Preserve stage progression",
        recovery_strategy="Load from disk or start at explicit stage"
    )
    def __init__(self, progress_file: Optional[Path] = None):
        self.progress_file = progress_file or Path.home() / '.engram' / 'training_progress.json'
        self.progress: Dict[str, TrainingProgress] = self._load_progress()
        self.detection_patterns = [
            "I remember",
            "As I recall",
            "This reminds me",
            "Previously we",
            "In our earlier",
            "Based on past"
        ]
        
    @performance_boundary(
        title="Training Prompt Generation",
        description="Generate stage-appropriate memory prompts",
        sla="<5ms prompt generation",
        optimization_notes="Cached stage lookups, minimal string operations",
        measured_impact="Negligible overhead on prompt processing"
    )
    def get_training_prompt(self, ci_name: str, base_prompt: str) -> str:
        """
        Get the appropriate training prompt for CI's current stage.
        
        Args:
            ci_name: CI being trained
            base_prompt: Original prompt
            
        Returns:
            Modified prompt with memory training cue
        """
        progress = self._get_or_create_progress(ci_name)
        stage = progress.current_stage
        
        if stage == 'autonomous':
            # Fully trained - no modification needed
            return base_prompt
            
        elif stage == 'occasional':
            # 50/50 chance of adding prompt
            if random.random() > 0.5:
                return f"\n/\n{base_prompt}"
            else:
                return base_prompt
                
        else:
            # Add stage-appropriate prompt
            prompt_addition = self.STAGE_PROMPTS[stage]
            return f"{prompt_addition}{base_prompt}"
    
    @performance_boundary(
        title="Response Analysis",
        description="Analyze CI response for memory usage patterns",
        sla="<20ms analysis",
        optimization_notes="Pattern matching with early exit",
        measured_impact="Fast enough for real-time feedback"
    )
    def analyze_response(self, ci_name: str, response: str) -> Dict[str, Any]:
        """
        Analyze CI response for memory usage and update training progress.
        
        Args:
            ci_name: CI that generated response
            response: The response to analyze
            
        Returns:
            Analysis results including memory usage detection
        """
        progress = self._get_or_create_progress(ci_name)
        
        # Check if response contains memory references
        used_memory = self._detect_memory_usage(response)
        
        # Update metrics
        progress.update_metrics(used_memory)
        
        # Check for stage advancement
        if progress.ready_for_advancement():
            next_stage = self._get_next_stage(progress.current_stage)
            if next_stage:
                logger.info(f"{ci_name} advancing from {progress.current_stage} to {next_stage}")
                progress.advance_stage(next_stage)
                self._save_progress()
        
        # Periodic save
        if progress.interactions_at_stage % 5 == 0:
            self._save_progress()
        
        return {
            'used_memory': used_memory,
            'current_stage': progress.current_stage,
            'memory_usage_rate': progress.memory_usage_rate,
            'interactions': progress.interactions_at_stage,
            'ready_for_next': progress.ready_for_advancement()
        }
    
    @fuzzy_match(
        title="Memory Usage Detection",
        description="Detect memory references in CI responses",
        algorithm="pattern_matching_with_context",
        examples=["I remember", "Previously", "Earlier", "As mentioned"],
        priority="explicit_reference > contextual_reference > implicit"
    )
    def _detect_memory_usage(self, response: str) -> bool:
        """Detect if response references memories."""
        response_lower = response.lower()
        
        # Check for explicit memory references
        for pattern in self.detection_patterns:
            if pattern.lower() in response_lower:
                return True
        
        # Check for contextual references
        contextual_patterns = [
            "earlier",
            "previously",
            "last time",
            "before",
            "as mentioned",
            "we discussed"
        ]
        
        for pattern in contextual_patterns:
            if pattern in response_lower:
                return True
        
        return False
    
    def _get_or_create_progress(self, ci_name: str) -> TrainingProgress:
        """Get or create training progress for CI."""
        if ci_name not in self.progress:
            self.progress[ci_name] = TrainingProgress(
                ci_name=ci_name,
                current_stage='explicit',
                stage_started=datetime.now(),
                interactions_at_stage=0,
                memory_usage_rate=0.0,
                successful_recalls=0,
                total_attempts=0
            )
        return self.progress[ci_name]
    
    def _get_next_stage(self, current_stage: str) -> Optional[str]:
        """Get the next training stage."""
        try:
            current_index = self.TRAINING_STAGES.index(current_stage)
            if current_index < len(self.TRAINING_STAGES) - 1:
                return self.TRAINING_STAGES[current_index + 1]
        except ValueError:
            logger.error(f"Unknown stage: {current_stage}")
        return None
    
    def set_stage(self, ci_name: str, stage: str):
        """Manually set CI to specific training stage."""
        if stage not in self.TRAINING_STAGES:
            raise ValueError(f"Invalid stage: {stage}")
        
        progress = self._get_or_create_progress(ci_name)
        progress.advance_stage(stage)
        self._save_progress()
        
        logger.info(f"Manually set {ci_name} to stage: {stage}")
    
    def get_progress_report(self, ci_name: str) -> Dict:
        """Get detailed progress report for CI."""
        progress = self._get_or_create_progress(ci_name)
        
        return {
            'ci_name': ci_name,
            'current_stage': progress.current_stage,
            'stage_index': self.TRAINING_STAGES.index(progress.current_stage),
            'total_stages': len(self.TRAINING_STAGES),
            'interactions_at_current': progress.interactions_at_stage,
            'total_interactions': progress.total_attempts,
            'memory_usage_rate': f"{progress.memory_usage_rate:.1%}",
            'successful_recalls': progress.successful_recalls,
            'time_at_stage': str(datetime.now() - progress.stage_started),
            'ready_for_advancement': progress.ready_for_advancement(),
            'stage_history': progress.stage_history
        }
    
    @state_checkpoint(
        title="Progress Persistence",
        description="Load and save training progress to disk",
        state_type="file_based",
        persistence=True,
        consistency_requirements="JSON format preservation",
        recovery_strategy="Create new if corrupted"
    )
    def _load_progress(self) -> Dict[str, TrainingProgress]:
        """Load training progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    
                progress = {}
                for ci_name, prog_data in data.items():
                    # Reconstruct TrainingProgress objects
                    progress[ci_name] = TrainingProgress(
                        ci_name=ci_name,
                        current_stage=prog_data['current_stage'],
                        stage_started=datetime.fromisoformat(prog_data['stage_started']),
                        interactions_at_stage=prog_data['interactions_at_stage'],
                        memory_usage_rate=prog_data['memory_usage_rate'],
                        successful_recalls=prog_data['successful_recalls'],
                        total_attempts=prog_data['total_attempts'],
                        stage_history=prog_data.get('stage_history', [])
                    )
                return progress
                
            except Exception as e:
                logger.error(f"Failed to load training progress: {e}")
        
        return {}
    
    def _save_progress(self):
        """Save training progress to file."""
        try:
            # Ensure directory exists
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to JSON-serializable format
            data = {}
            for ci_name, progress in self.progress.items():
                data[ci_name] = {
                    'current_stage': progress.current_stage,
                    'stage_started': progress.stage_started.isoformat(),
                    'interactions_at_stage': progress.interactions_at_stage,
                    'memory_usage_rate': progress.memory_usage_rate,
                    'successful_recalls': progress.successful_recalls,
                    'total_attempts': progress.total_attempts,
                    'stage_history': progress.stage_history
                }
            
            with open(self.progress_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save training progress: {e}")