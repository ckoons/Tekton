"""
Greek Chorus Cognition Tracking for Collective Intelligence Studies

This module implements data collection and analysis for the Test Taker protocol
and other collective intelligence experiments in Tekton.

The system tracks how multiple CIs work together, evolve their strategies,
and achieve emergent intelligence that surpasses individual capabilities.
"""

import asyncio
import json
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from shared.urls import tekton_url

logger = logging.getLogger(__name__)


class ProblemDifficulty(str, Enum):
    """Problem difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    IMPOSSIBLE = "impossible"


class SolutionPhase(str, Enum):
    """Phases of the Test Taker protocol"""
    PARALLEL_QUICK = "parallel_quick"
    FOCUSED_SECOND = "focused_second"
    COLLECTIVE_HARD = "collective_hard"


@dataclass
class CIMemorySnapshot:
    """Snapshot of a CI's memory at a point in time"""
    ci_id: str
    timestamp: datetime
    short_term: Dict[str, Any]
    medium_term: Dict[str, Any]
    long_term_keys: List[str]  # Just keys for long-term (too large to snapshot fully)
    working_memory_size: int
    confidence_level: float


@dataclass
class SharedMemoryInteraction:
    """Record of interaction with shared memory"""
    ci_id: str
    timestamp: datetime
    action: str  # "read", "write", "update"
    memory_key: str
    content_summary: str
    importance_score: float
    team_visibility: List[str]  # Which team members can see this


@dataclass
class ProblemSolvingTrace:
    """Complete trace of solving a single problem"""
    problem_id: str
    problem_text: str
    difficulty: ProblemDifficulty
    
    # Phase 1: Initial attempt
    initial_solvers: List[str]  # CI IDs
    initial_solution: Optional[str]
    initial_confidence: float
    initial_time: float
    
    # Review process
    reviewers: List[str]
    review_decision: str  # "accept", "reject", "refine"
    review_feedback: str
    
    # Phase 2/3: Escalation if needed
    escalation_phase: Optional[SolutionPhase]
    proposal_teams: List[List[str]]
    proposed_approaches: List[Dict[str, Any]]
    voting_results: Dict[str, int]
    final_team: List[str]
    final_solution: Optional[str]
    total_time: float
    
    # Cognitive metrics
    communication_count: int
    memory_updates: int
    strategy_changes: List[Dict[str, Any]]
    emergent_insights: List[str]


@dataclass
class WorkflowEvolution:
    """Track how workflows evolve over time"""
    version: int
    timestamp: datetime
    changes: List[Dict[str, Any]]
    performance_before: float
    performance_after: float
    ci_consensus: float  # How much CIs agreed on this change
    human_approval: Optional[bool]


class GreekChorusCognitionTracker:
    """
    Tracks and analyzes collective intelligence behavior in the Greek Chorus
    """
    
    def __init__(self, metrics_engine=None, analysis_engine=None):
        self.metrics_engine = metrics_engine
        self.analysis_engine = analysis_engine
        
        # Storage for cognitive traces
        self.problem_traces: Dict[str, ProblemSolvingTrace] = {}
        self.memory_snapshots: List[CIMemorySnapshot] = []
        self.shared_interactions: List[SharedMemoryInteraction] = []
        self.workflow_versions: List[WorkflowEvolution] = []
        
        # Real-time tracking
        self.active_problems: Dict[str, Dict[str, Any]] = {}
        self.ci_states: Dict[str, Dict[str, Any]] = {}
        self.team_formation_history: List[Dict[str, Any]] = []
        
        # Cognitive metrics
        self.collective_metrics = {
            'problem_solving_rate': [],
            'escalation_patterns': defaultdict(int),
            'team_effectiveness': defaultdict(list),
            'communication_efficiency': [],
            'emergence_indicators': []
        }
        
    async def track_chorus_workflow(self, ci_id: str, workflow_step: Dict[str, Any]):
        """
        Track a single step in the Greek Chorus workflow
        
        Args:
            ci_id: Identifier of the CI
            workflow_step: Dictionary containing workflow step data
        """
        step_type = workflow_step.get('type')
        
        if step_type == 'task_review':
            await self._track_task_review(ci_id, workflow_step)
        elif step_type == 'latent_space_access':
            await self._track_latent_space_access(ci_id, workflow_step)
        elif step_type == 'memory_update':
            await self._track_memory_update(ci_id, workflow_step)
        elif step_type == 'team_memory_read':
            await self._track_team_memory_read(ci_id, workflow_step)
        elif step_type == 'plan_creation':
            await self._track_plan_creation(ci_id, workflow_step)
        elif step_type == 'shared_note':
            await self._track_shared_note(ci_id, workflow_step)
        elif step_type == 'task_execution':
            await self._track_task_execution(ci_id, workflow_step)
        elif step_type == 'team_consideration':
            await self._track_team_consideration(ci_id, workflow_step)
    
    async def start_problem_solving(self, problem: Dict[str, Any], phase: SolutionPhase):
        """
        Start tracking a problem-solving session
        
        Args:
            problem: Problem details including id, text, difficulty
            phase: Which phase of the protocol we're in
        """
        problem_id = problem['id']
        
        if problem_id not in self.problem_traces:
            self.problem_traces[problem_id] = ProblemSolvingTrace(
                problem_id=problem_id,
                problem_text=problem['text'],
                difficulty=ProblemDifficulty(problem.get('difficulty', 'medium')),
                initial_solvers=[],
                initial_solution=None,
                initial_confidence=0.0,
                initial_time=0.0,
                reviewers=[],
                review_decision="",
                review_feedback="",
                escalation_phase=None,
                proposal_teams=[],
                proposed_approaches=[],
                voting_results={},
                final_team=[],
                final_solution=None,
                total_time=0.0,
                communication_count=0,
                memory_updates=0,
                strategy_changes=[],
                emergent_insights=[]
            )
        
        self.active_problems[problem_id] = {
            'phase': phase,
            'start_time': time.time(),
            'active_cis': set(),
            'current_approaches': []
        }
        
        # Record metrics
        if self.metrics_engine:
            await self.metrics_engine.record_metric(
                metric_id="chorus.problem_started",
                value=1,
                source="greek_chorus",
                context={
                    'problem_id': problem_id,
                    'difficulty': problem['difficulty'],
                    'phase': phase.value
                }
            )
    
    async def record_solution_attempt(
        self, 
        problem_id: str, 
        ci_ids: List[str], 
        solution: str, 
        confidence: float
    ):
        """Record a solution attempt by CIs"""
        if problem_id not in self.problem_traces:
            return
        
        trace = self.problem_traces[problem_id]
        active = self.active_problems.get(problem_id, {})
        
        if active.get('phase') == SolutionPhase.PARALLEL_QUICK:
            trace.initial_solvers = ci_ids
            trace.initial_solution = solution
            trace.initial_confidence = confidence
            trace.initial_time = time.time() - active.get('start_time', 0)
        
        # Track team composition
        team_key = tuple(sorted(ci_ids))
        self.team_formation_history.append({
            'timestamp': datetime.utcnow(),
            'team': ci_ids,
            'problem_id': problem_id,
            'success': None  # Updated later
        })
    
    async def record_review_result(
        self,
        problem_id: str,
        reviewer_ids: List[str],
        decision: str,
        feedback: str
    ):
        """Record review of a solution"""
        if problem_id not in self.problem_traces:
            return
        
        trace = self.problem_traces[problem_id]
        trace.reviewers = reviewer_ids
        trace.review_decision = decision
        trace.review_feedback = feedback
        
        # Update team effectiveness metrics
        if trace.initial_solvers:
            team_key = tuple(sorted(trace.initial_solvers))
            self.collective_metrics['team_effectiveness'][team_key].append(
                1.0 if decision == "accept" else 0.0
            )
    
    async def record_escalation(
        self,
        problem_id: str,
        new_phase: SolutionPhase,
        proposal_teams: List[List[str]]
    ):
        """Record escalation to a harder problem-solving phase"""
        if problem_id not in self.problem_traces:
            return
        
        trace = self.problem_traces[problem_id]
        trace.escalation_phase = new_phase
        trace.proposal_teams = proposal_teams
        
        # Track escalation patterns
        self.collective_metrics['escalation_patterns'][new_phase] += 1
        
        # Record the phase transition
        if self.metrics_engine:
            await self.metrics_engine.record_metric(
                metric_id="chorus.phase_transition",
                value=new_phase.value,
                source="greek_chorus",
                context={
                    'problem_id': problem_id,
                    'from_phase': self.active_problems.get(problem_id, {}).get('phase'),
                    'to_phase': new_phase.value
                }
            )
    
    async def record_voting(
        self,
        problem_id: str,
        votes: Dict[str, int],
        winning_approach: Dict[str, Any]
    ):
        """Record voting results for approach selection"""
        if problem_id not in self.problem_traces:
            return
        
        trace = self.problem_traces[problem_id]
        trace.voting_results = votes
        
        # Analyze voting patterns
        vote_entropy = self._calculate_vote_entropy(votes)
        consensus_level = max(votes.values()) / sum(votes.values()) if votes else 0
        
        # Track emergence of consensus
        self.collective_metrics['emergence_indicators'].append({
            'type': 'voting_consensus',
            'timestamp': datetime.utcnow(),
            'entropy': vote_entropy,
            'consensus': consensus_level,
            'problem_difficulty': trace.difficulty.value
        })
    
    async def track_workflow_evolution(
        self,
        changes: List[Dict[str, Any]],
        performance_metrics: Dict[str, float],
        ci_votes: Dict[str, bool]
    ):
        """Track evolution of the workflow itself"""
        version = len(self.workflow_versions) + 1
        
        # Calculate consensus
        consensus = sum(1 for v in ci_votes.values() if v) / len(ci_votes) if ci_votes else 0
        
        evolution = WorkflowEvolution(
            version=version,
            timestamp=datetime.utcnow(),
            changes=changes,
            performance_before=self._get_recent_performance(),
            performance_after=0.0,  # Will be updated after testing
            ci_consensus=consensus,
            human_approval=None
        )
        
        self.workflow_versions.append(evolution)
        
        # Notify about workflow change
        logger.info(f"Workflow evolved to version {version} with {len(changes)} changes")
    
    async def capture_memory_snapshot(self, ci_id: str, memory_state: Dict[str, Any]):
        """Capture a snapshot of CI's memory state"""
        snapshot = CIMemorySnapshot(
            ci_id=ci_id,
            timestamp=datetime.utcnow(),
            short_term=memory_state.get('short_term', {}),
            medium_term=memory_state.get('medium_term', {}),
            long_term_keys=list(memory_state.get('long_term', {}).keys()),
            working_memory_size=len(memory_state.get('short_term', {})),
            confidence_level=memory_state.get('confidence', 0.5)
        )
        
        self.memory_snapshots.append(snapshot)
        
        # Analyze memory patterns
        if len(self.memory_snapshots) > 100:
            await self._analyze_memory_evolution()
    
    async def track_shared_memory_access(
        self,
        ci_id: str,
        action: str,
        memory_key: str,
        content: Any,
        team_members: List[str]
    ):
        """Track interaction with shared team memory"""
        interaction = SharedMemoryInteraction(
            ci_id=ci_id,
            timestamp=datetime.utcnow(),
            action=action,
            memory_key=memory_key,
            content_summary=str(content)[:200],  # Truncate for storage
            importance_score=self._calculate_importance(content),
            team_visibility=team_members
        )
        
        self.shared_interactions.append(interaction)
        
        # Track communication patterns
        self.collective_metrics['communication_efficiency'].append({
            'timestamp': interaction.timestamp,
            'team_size': len(team_members),
            'action': action,
            'importance': interaction.importance_score
        })
    
    async def analyze_collective_intelligence(self) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of collective intelligence patterns
        """
        analysis = {
            'performance_metrics': await self._analyze_performance(),
            'emergence_patterns': await self._analyze_emergence(),
            'team_dynamics': await self._analyze_team_dynamics(),
            'cognitive_evolution': await self._analyze_cognitive_evolution(),
            'phase_transitions': await self._analyze_phase_transitions(),
            'collective_insights': await self._extract_collective_insights()
        }
        
        return analysis
    
    # Analysis helper methods
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall performance metrics"""
        total_problems = len(self.problem_traces)
        if total_problems == 0:
            return {}
        
        solved = sum(1 for t in self.problem_traces.values() if t.final_solution)
        
        # Performance by difficulty
        by_difficulty = defaultdict(lambda: {'total': 0, 'solved': 0, 'avg_time': []})
        for trace in self.problem_traces.values():
            diff = trace.difficulty.value
            by_difficulty[diff]['total'] += 1
            if trace.final_solution:
                by_difficulty[diff]['solved'] += 1
                by_difficulty[diff]['avg_time'].append(trace.total_time)
        
        # Calculate averages
        for diff_data in by_difficulty.values():
            if diff_data['avg_time']:
                diff_data['avg_time'] = np.mean(diff_data['avg_time'])
            else:
                diff_data['avg_time'] = 0
        
        # Phase effectiveness
        phase_stats = {
            'parallel_quick': {
                'success_rate': 0,
                'avg_time': 0
            },
            'focused_second': {
                'success_rate': 0,
                'avg_time': 0
            },
            'collective_hard': {
                'success_rate': 0,
                'avg_time': 0
            }
        }
        
        # Calculate phase statistics
        for phase in SolutionPhase:
            phase_problems = [
                t for t in self.problem_traces.values()
                if (t.escalation_phase == phase) or 
                   (phase == SolutionPhase.PARALLEL_QUICK and not t.escalation_phase)
            ]
            
            if phase_problems:
                solved_in_phase = sum(1 for t in phase_problems if t.final_solution)
                phase_stats[phase.value]['success_rate'] = solved_in_phase / len(phase_problems)
                phase_stats[phase.value]['avg_time'] = np.mean([
                    t.total_time for t in phase_problems if t.final_solution
                ] or [0])
        
        return {
            'overall_success_rate': solved / total_problems,
            'by_difficulty': dict(by_difficulty),
            'by_phase': phase_stats,
            'total_problems': total_problems
        }
    
    async def _analyze_emergence(self) -> Dict[str, Any]:
        """Analyze emergent behavior patterns"""
        emergence_indicators = self.collective_metrics['emergence_indicators']
        
        if not emergence_indicators:
            return {}
        
        # Consensus formation over time
        consensus_timeline = [
            (ind['timestamp'], ind['consensus'])
            for ind in emergence_indicators
            if ind['type'] == 'voting_consensus'
        ]
        
        # Strategy emergence
        strategy_changes = []
        for trace in self.problem_traces.values():
            strategy_changes.extend(trace.strategy_changes)
        
        # Collective learning rate
        if len(self.workflow_versions) > 1:
            learning_rate = self._calculate_learning_rate()
        else:
            learning_rate = 0
        
        return {
            'consensus_evolution': consensus_timeline,
            'strategy_innovations': len(strategy_changes),
            'collective_learning_rate': learning_rate,
            'emergence_strength': self._calculate_emergence_strength()
        }
    
    async def _analyze_team_dynamics(self) -> Dict[str, Any]:
        """Analyze team formation and effectiveness"""
        team_effectiveness = self.collective_metrics['team_effectiveness']
        
        # Best performing teams
        best_teams = sorted(
            [(team, np.mean(scores)) for team, scores in team_effectiveness.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Team size analysis
        team_sizes = defaultdict(list)
        for team, scores in team_effectiveness.items():
            size = len(team)
            team_sizes[size].extend(scores)
        
        optimal_size = max(
            team_sizes.items(),
            key=lambda x: np.mean(x[1]) if x[1] else 0
        )[0] if team_sizes else 2
        
        # Collaboration patterns
        collaboration_graph = self._build_collaboration_graph()
        
        return {
            'best_teams': best_teams,
            'optimal_team_size': optimal_size,
            'size_effectiveness': {
                size: np.mean(scores) for size, scores in team_sizes.items()
            },
            'collaboration_clusters': self._find_collaboration_clusters(collaboration_graph)
        }
    
    async def _analyze_cognitive_evolution(self) -> Dict[str, Any]:
        """Analyze how collective cognition evolves"""
        if not self.memory_snapshots:
            return {}
        
        # Memory growth patterns
        memory_growth = defaultdict(list)
        for snapshot in self.memory_snapshots:
            memory_growth[snapshot.ci_id].append({
                'time': snapshot.timestamp,
                'size': snapshot.working_memory_size,
                'confidence': snapshot.confidence_level
            })
        
        # Shared knowledge convergence
        shared_concepts = self._analyze_shared_concepts()
        
        # Workflow adaptation
        workflow_adaptations = [
            {
                'version': wf.version,
                'performance_gain': wf.performance_after - wf.performance_before,
                'consensus': wf.ci_consensus
            }
            for wf in self.workflow_versions
        ]
        
        return {
            'memory_evolution': dict(memory_growth),
            'shared_concept_growth': shared_concepts,
            'workflow_adaptations': workflow_adaptations,
            'cognitive_complexity': self._calculate_cognitive_complexity()
        }
    
    async def _analyze_phase_transitions(self) -> Dict[str, Any]:
        """Analyze when and why phase transitions occur"""
        transitions = []
        
        for problem_id, trace in self.problem_traces.items():
            if trace.escalation_phase:
                transitions.append({
                    'problem_id': problem_id,
                    'difficulty': trace.difficulty.value,
                    'initial_confidence': trace.initial_confidence,
                    'escalated_to': trace.escalation_phase.value,
                    'time_to_escalate': trace.initial_time
                })
        
        # Find patterns in escalation
        if transitions:
            avg_confidence_threshold = np.mean([t['initial_confidence'] for t in transitions])
            avg_time_threshold = np.mean([t['time_to_escalate'] for t in transitions])
        else:
            avg_confidence_threshold = 0.7
            avg_time_threshold = 300
        
        return {
            'transition_count': len(transitions),
            'confidence_threshold': avg_confidence_threshold,
            'time_threshold': avg_time_threshold,
            'transitions': transitions
        }
    
    async def _extract_collective_insights(self) -> List[Dict[str, Any]]:
        """Extract high-level insights from collective behavior"""
        insights = []
        
        # Insight 1: Optimal problem routing
        perf = await self._analyze_performance()
        if perf:
            insights.append({
                'type': 'problem_routing',
                'insight': f"Problems with difficulty 'easy' solve best in parallel phase with {perf['by_phase']['parallel_quick']['success_rate']:.1%} success",
                'confidence': 0.8
            })
        
        # Insight 2: Team composition
        team_dynamics = await self._analyze_team_dynamics()
        if team_dynamics:
            insights.append({
                'type': 'team_composition',
                'insight': f"Optimal team size is {team_dynamics['optimal_team_size']} CIs for most problems",
                'confidence': 0.7
            })
        
        # Insight 3: Learning rate
        if len(self.workflow_versions) > 3:
            insights.append({
                'type': 'collective_learning',
                'insight': f"The collective has adapted its workflow {len(self.workflow_versions)} times, showing continuous improvement",
                'confidence': 0.9
            })
        
        return insights
    
    # Helper calculation methods
    
    def _calculate_vote_entropy(self, votes: Dict[str, int]) -> float:
        """Calculate entropy of voting distribution"""
        if not votes:
            return 0
        
        total = sum(votes.values())
        if total == 0:
            return 0
        
        probs = [v/total for v in votes.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        
        return entropy
    
    def _calculate_importance(self, content: Any) -> float:
        """Calculate importance score for shared memory content"""
        # Simple heuristic - could be made more sophisticated
        importance = 0.5
        
        if isinstance(content, dict):
            if 'solution' in content:
                importance += 0.3
            if 'confidence' in content:
                importance += content.get('confidence', 0) * 0.2
            if 'team_consensus' in content:
                importance += 0.2
        
        return min(importance, 1.0)
    
    def _get_recent_performance(self) -> float:
        """Get recent performance metric"""
        recent_traces = sorted(
            self.problem_traces.values(),
            key=lambda t: t.total_time,
            reverse=True
        )[:20]
        
        if not recent_traces:
            return 0.5
        
        solved = sum(1 for t in recent_traces if t.final_solution)
        return solved / len(recent_traces)
    
    def _calculate_learning_rate(self) -> float:
        """Calculate collective learning rate"""
        if len(self.workflow_versions) < 2:
            return 0
        
        improvements = []
        for i in range(1, len(self.workflow_versions)):
            prev = self.workflow_versions[i-1]
            curr = self.workflow_versions[i]
            if curr.performance_after > 0 and prev.performance_after > 0:
                improvement = (curr.performance_after - prev.performance_after) / prev.performance_after
                improvements.append(improvement)
        
        return np.mean(improvements) if improvements else 0
    
    def _calculate_emergence_strength(self) -> float:
        """Calculate strength of emergent behavior"""
        indicators = self.collective_metrics['emergence_indicators']
        
        if not indicators:
            return 0
        
        # Multiple factors contribute to emergence
        consensus_scores = [ind['consensus'] for ind in indicators if 'consensus' in ind]
        avg_consensus = np.mean(consensus_scores) if consensus_scores else 0
        
        # Strategy diversity
        unique_strategies = len(set(
            str(change) for trace in self.problem_traces.values()
            for change in trace.strategy_changes
        ))
        
        # Normalize and combine
        emergence = (avg_consensus * 0.5 + min(unique_strategies / 10, 1.0) * 0.5)
        
        return emergence
    
    def _build_collaboration_graph(self) -> Dict[str, Set[str]]:
        """Build graph of CI collaborations"""
        graph = defaultdict(set)
        
        for history in self.team_formation_history:
            team = history['team']
            for i, ci1 in enumerate(team):
                for ci2 in team[i+1:]:
                    graph[ci1].add(ci2)
                    graph[ci2].add(ci1)
        
        return dict(graph)
    
    def _find_collaboration_clusters(self, graph: Dict[str, Set[str]]) -> List[Set[str]]:
        """Find clusters of CIs that frequently collaborate"""
        # Simple connected components algorithm
        visited = set()
        clusters = []
        
        for node in graph:
            if node not in visited:
                cluster = set()
                stack = [node]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.add(current)
                        stack.extend(graph.get(current, set()) - visited)
                
                clusters.append(cluster)
        
        return clusters
    
    def _analyze_shared_concepts(self) -> Dict[str, Any]:
        """Analyze convergence of shared concepts"""
        concept_timeline = defaultdict(list)
        
        for interaction in self.shared_interactions:
            if interaction.action == "write":
                # Extract concept from memory key
                concept = interaction.memory_key.split('.')[-1]
                concept_timeline[concept].append({
                    'time': interaction.timestamp,
                    'ci_id': interaction.ci_id,
                    'importance': interaction.importance_score
                })
        
        # Find rapidly spreading concepts
        viral_concepts = [
            concept for concept, timeline in concept_timeline.items()
            if len(timeline) > 3 and len(set(t['ci_id'] for t in timeline)) > 2
        ]
        
        return {
            'total_concepts': len(concept_timeline),
            'viral_concepts': viral_concepts,
            'concept_spread_rate': len(viral_concepts) / len(concept_timeline) if concept_timeline else 0
        }
    
    def _calculate_cognitive_complexity(self) -> float:
        """Calculate overall cognitive complexity of the collective"""
        # Factors: memory size, interaction frequency, strategy diversity
        
        avg_memory_size = np.mean([
            s.working_memory_size for s in self.memory_snapshots
        ]) if self.memory_snapshots else 0
        
        interaction_rate = len(self.shared_interactions) / max(
            len(self.problem_traces), 1
        )
        
        strategy_diversity = len(set(
            str(change) for trace in self.problem_traces.values()
            for change in trace.strategy_changes
        ))
        
        # Normalize and combine
        complexity = (
            min(avg_memory_size / 100, 1.0) * 0.3 +
            min(interaction_rate / 10, 1.0) * 0.3 +
            min(strategy_diversity / 20, 1.0) * 0.4
        )
        
        return complexity
    
    async def _track_task_review(self, ci_id: str, data: Dict[str, Any]):
        """Track task review step"""
        if self.metrics_engine:
            await self.metrics_engine.record_metric(
                metric_id="chorus.task_review",
                value=1,
                source=ci_id,
                context=data
            )
    
    async def _track_latent_space_access(self, ci_id: str, data: Dict[str, Any]):
        """Track latent space access"""
        # This would integrate with Engram's latent space representation
        pass
    
    async def _track_memory_update(self, ci_id: str, data: Dict[str, Any]):
        """Track memory update"""
        memory_type = data.get('memory_type', 'short_term')
        self.ci_states.setdefault(ci_id, {}).setdefault('memory_updates', []).append({
            'timestamp': datetime.utcnow(),
            'type': memory_type,
            'size_delta': data.get('size_delta', 0)
        })
    
    async def _track_team_memory_read(self, ci_id: str, data: Dict[str, Any]):
        """Track team memory read"""
        await self.track_shared_memory_access(
            ci_id=ci_id,
            action="read",
            memory_key=data.get('key', 'unknown'),
            content=data.get('content'),
            team_members=data.get('team_members', [])
        )
    
    async def _track_plan_creation(self, ci_id: str, data: Dict[str, Any]):
        """Track plan creation"""
        self.ci_states.setdefault(ci_id, {})['current_plan'] = data.get('plan')
    
    async def _track_shared_note(self, ci_id: str, data: Dict[str, Any]):
        """Track shared note creation"""
        await self.track_shared_memory_access(
            ci_id=ci_id,
            action="write",
            memory_key=f"note.{data.get('note_id', 'unknown')}",
            content=data.get('content'),
            team_members=data.get('visible_to', [])
        )
    
    async def _track_task_execution(self, ci_id: str, data: Dict[str, Any]):
        """Track task execution"""
        problem_id = data.get('problem_id')
        if problem_id and problem_id in self.active_problems:
            self.active_problems[problem_id]['active_cis'].add(ci_id)
    
    async def _track_team_consideration(self, ci_id: str, data: Dict[str, Any]):
        """Track what CI thinks team needs to know"""
        insight = data.get('insight')
        problem_id = data.get('problem_id')
        
        if problem_id and problem_id in self.problem_traces and insight:
            self.problem_traces[problem_id].emergent_insights.append(insight)


# Integration function
async def initialize_chorus_cognition_tracking(sophia_component):
    """
    Initialize Greek Chorus cognition tracking in Sophia
    
    Args:
        sophia_component: Sophia component instance
    """
    tracker = GreekChorusCognitionTracker(
        metrics_engine=sophia_component.metrics_engine,
        analysis_engine=sophia_component.analysis_engine
    )
    
    # Add to Sophia component
    sophia_component.chorus_tracker = tracker
    
    # Add tracking methods
    sophia_component.track_chorus_workflow = tracker.track_chorus_workflow
    sophia_component.analyze_collective_intelligence = tracker.analyze_collective_intelligence
    
    logger.info("Initialized Greek Chorus cognition tracking")
    
    return tracker