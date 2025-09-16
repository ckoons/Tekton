"""
Memory Template for Orchestrator CIs
Optimized for coordination, task management, and multi-CI collaboration.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from ..middleware import (
    MemoryConfig,
    InjectionStyle,
    MemoryTier
)
from ..decorators import (
    with_memory,
    collective_memory,
    memory_trigger
)


@dataclass
class OrchestratorMemoryTemplate:
    """
    Memory template for orchestrator CIs like Apollo, Harmonia, Tekton-Core.
    
    Features:
    - Multi-CI coordination tracking
    - Task history and outcomes
    - Collective memory sharing
    - Structured workflow memory
    """
    
    # Default configuration
    config = MemoryConfig(
        namespace="orchestrator",
        injection_style=InjectionStyle.STRUCTURED,
        memory_tiers=[
            MemoryTier.SESSION,     # Current coordination session
            MemoryTier.COLLECTIVE,  # Shared team knowledge
            MemoryTier.RECENT,      # Recent task outcomes
            MemoryTier.DOMAIN       # Orchestration patterns
        ],
        store_inputs=True,
        store_outputs=True,
        inject_context=True,
        context_depth=20,
        relevance_threshold=0.7,
        max_context_size=2000,
        enable_collective=True,  # Always share with team
        performance_sla_ms=200
    )
    
    # Decorator presets
    decorators = {
        'task_orchestration': 'orchestrate_task',
        'team_coordination': 'coordinate_team',
        'workflow_management': 'manage_workflow',
        'outcome_tracking': 'track_outcome'
    }
    
    # Memory patterns
    patterns = {
        'task_delegation': {
            'tiers': [MemoryTier.SESSION, MemoryTier.RECENT],
            'depth': 15,
            'style': InjectionStyle.STRUCTURED
        },
        'team_coordination': {
            'tiers': [MemoryTier.COLLECTIVE, MemoryTier.SESSION],
            'depth': 20,
            'style': InjectionStyle.STRUCTURED
        },
        'workflow_execution': {
            'tiers': [MemoryTier.DOMAIN, MemoryTier.RECENT],
            'depth': 25,
            'style': InjectionStyle.TECHNICAL
        },
        'conflict_resolution': {
            'tiers': [MemoryTier.COLLECTIVE, MemoryTier.DOMAIN],
            'depth': 15,
            'style': InjectionStyle.NATURAL
        }
    }


# Decorator implementations for orchestrator CIs

def orchestrate_task(func):
    """Decorator for task orchestration with full memory."""
    return with_memory(
        namespace="orchestration",
        memory_tiers=[MemoryTier.SESSION, MemoryTier.COLLECTIVE, MemoryTier.RECENT],
        injection_style=InjectionStyle.STRUCTURED,
        context_depth=20,
        store_inputs=True,
        store_outputs=True,
        enable_collective=True
    )(func)


def coordinate_team(func):
    """Decorator for team coordination with collective memory."""
    return collective_memory(
        share_with=["all_team_members"],
        memory_type="coordination",
        visibility="team"
    )(func)


def manage_workflow(func):
    """Decorator for workflow management."""
    return with_memory(
        namespace="workflow",
        memory_tiers=[MemoryTier.DOMAIN, MemoryTier.SESSION],
        injection_style=InjectionStyle.TECHNICAL,
        context_depth=25,
        store_inputs=True,
        store_outputs=True
    )(func)


def track_outcome(func):
    """Decorator for outcome tracking with consolidation."""
    return memory_trigger(
        on_event="task_completion",
        consolidation_type="delayed",
        reflection_depth="medium",
        auto_consolidate=True
    )(func)


# Example usage class

class OrchestratorCI:
    """Example implementation of an orchestrator CI with memory."""
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.template = OrchestratorMemoryTemplate()
        self.memory_context = None
        self.team_members = []
    
    @orchestrate_task
    async def orchestrate(self, task: Dict, team: List[str]) -> Dict:
        """
        Orchestrate a task across multiple CIs.
        
        Uses memory to inform delegation and track outcomes.
        """
        context = self.memory_context
        
        # Get past orchestration patterns
        patterns = self._get_orchestration_patterns(context)
        
        # Determine optimal delegation
        delegation = self._determine_delegation(task, team, patterns)
        
        # Execute orchestration
        results = await self._execute_orchestration(delegation)
        
        return {
            'task': task,
            'delegation': delegation,
            'results': results,
            'success': self._evaluate_success(results)
        }
    
    @coordinate_team
    async def coordinate(self, objective: str, participants: List[str]) -> Dict:
        """
        Coordinate team members with shared memory.
        
        Automatically shares coordination state with all participants.
        """
        # Create coordination plan
        plan = self._create_coordination_plan(objective, participants)
        
        # This will be shared with all participants
        coordination_state = {
            'objective': objective,
            'participants': participants,
            'plan': plan,
            'status': 'active',
            'coordinator': self.ci_name
        }
        
        return coordination_state
    
    @manage_workflow
    async def execute_workflow(self, workflow: Dict) -> Dict:
        """
        Execute a workflow with memory-informed decisions.
        
        Uses domain knowledge and session context.
        """
        context = self.memory_context
        
        # Get workflow patterns from memory
        workflow_patterns = self._get_workflow_patterns(context)
        
        # Optimize workflow based on patterns
        optimized = self._optimize_workflow(workflow, workflow_patterns)
        
        # Execute workflow steps
        results = await self._execute_workflow_steps(optimized)
        
        return results
    
    @track_outcome
    async def record_outcome(self, task_id: str, outcome: Dict) -> Dict:
        """
        Record task outcome with automatic consolidation.
        
        Triggers memory consolidation for learning.
        """
        # Analyze outcome
        analysis = self._analyze_outcome(outcome)
        
        # Extract lessons learned
        lessons = self._extract_lessons(outcome, analysis)
        
        # This will trigger consolidation
        return {
            'task_id': task_id,
            'outcome': outcome,
            'analysis': analysis,
            'lessons': lessons,
            'recorded_at': 'now'
        }
    
    def _get_orchestration_patterns(self, context) -> List[Dict]:
        """Get orchestration patterns from memory."""
        if not context or not context.domain:
            return []
        
        patterns = []
        for item in context.domain:
            if 'pattern' in item.get('content', {}):
                patterns.append(item['content']['pattern'])
        
        return patterns
    
    def _determine_delegation(self, task, team, patterns) -> Dict:
        """Determine optimal task delegation."""
        # Placeholder implementation
        return {
            'assignments': {member: 'subtask' for member in team},
            'strategy': 'parallel'
        }
    
    async def _execute_orchestration(self, delegation) -> Dict:
        """Execute the orchestration plan."""
        # Placeholder implementation
        return {'status': 'completed', 'results': []}
    
    def _evaluate_success(self, results) -> bool:
        """Evaluate orchestration success."""
        # Placeholder implementation
        return True
    
    def _create_coordination_plan(self, objective, participants) -> Dict:
        """Create coordination plan."""
        # Placeholder implementation
        return {
            'phases': ['planning', 'execution', 'review'],
            'assignments': {p: 'role' for p in participants}
        }
    
    def _get_workflow_patterns(self, context) -> List[Dict]:
        """Get workflow patterns from memory."""
        # Placeholder implementation
        return []
    
    def _optimize_workflow(self, workflow, patterns) -> Dict:
        """Optimize workflow based on patterns."""
        # Placeholder implementation
        return workflow
    
    async def _execute_workflow_steps(self, workflow) -> Dict:
        """Execute workflow steps."""
        # Placeholder implementation
        return {'status': 'completed', 'steps_completed': 0}
    
    def _analyze_outcome(self, outcome) -> Dict:
        """Analyze task outcome."""
        # Placeholder implementation
        return {'success_rate': 0.9, 'efficiency': 0.85}
    
    def _extract_lessons(self, outcome, analysis) -> List[str]:
        """Extract lessons learned."""
        # Placeholder implementation
        return ['lesson1', 'lesson2']


# Configuration builder

def create_orchestrator_config(
    ci_name: str,
    team_size: int = 5,
    **overrides
) -> MemoryConfig:
    """
    Create memory configuration for an orchestrator CI.
    
    Args:
        ci_name: Name of the CI
        team_size: Expected team size
        **overrides: Configuration overrides
        
    Returns:
        Configured MemoryConfig
    """
    base_config = OrchestratorMemoryTemplate.config
    
    # Adjust for team size
    context_depth = min(20 + team_size * 2, 50)
    
    # Apply overrides
    config_dict = {
        'namespace': ci_name,
        'injection_style': base_config.injection_style,
        'memory_tiers': base_config.memory_tiers,
        'store_inputs': base_config.store_inputs,
        'store_outputs': base_config.store_outputs,
        'inject_context': base_config.inject_context,
        'context_depth': context_depth,
        'relevance_threshold': base_config.relevance_threshold,
        'max_context_size': base_config.max_context_size,
        'enable_collective': True,  # Always enable for orchestrators
        'performance_sla_ms': base_config.performance_sla_ms
    }
    
    config_dict.update(overrides)
    
    return MemoryConfig(**config_dict)