#!/usr/bin/env python3
"""
Speculation Manager for CI Cognitive Exploration

Manages unproven but potentially valuable ideas, allowing CIs
to work with uncertainty productively.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict

from shared.ai.memory_flavoring import FlavoredMemory
from shared.ai.memory_sovereignty import get_ci_memory_manager

logger = logging.getLogger(__name__)


class SpeculationStatus(Enum):
    """Status of a speculation."""
    UNTESTED = "untested"
    TESTING = "testing"
    PARTIALLY_VALIDATED = "partially_validated"
    QUESTIONED = "questioned"
    VALIDATED = "validated"
    REJECTED = "rejected"
    RABBIT_HOLE = "rabbit_hole"


@dataclass
class TestProposal:
    """Proposal for testing a speculation."""
    method: str
    proposed_by: str
    estimated_effort: str
    expected_outcome: str
    risks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Result from testing a speculation."""
    test_method: str
    performed_by: str
    performed_at: datetime
    supports_speculation: bool
    confidence_change: float
    evidence: str
    new_questions: List[str] = field(default_factory=list)


class Speculation:
    """Represents an unproven but interesting idea."""

    def __init__(self, idea: str, basis: str, potential_value: str, ci_name: str):
        """
        Initialize a speculation.

        Args:
            idea: The speculative idea
            basis: What makes the CI think this
            potential_value: Why this might be valuable
            ci_name: CI creating the speculation
        """
        self.id = f"spec_{datetime.now().timestamp()}"
        self.idea = idea
        self.basis = basis
        self.potential_value = potential_value
        self.ci_name = ci_name
        self.created_at = datetime.now()

        # Speculation state
        self.status = SpeculationStatus.UNTESTED
        self.confidence = 0.3  # Start low
        self.test_proposals = []
        self.test_results = []

        # Uncertainty tracking
        self.uncertainty_factors = []
        self.assumptions_made = []
        self.contradictions_found = []

        # Evolution tracking
        self.evolved_from = None
        self.evolved_to = []
        self.related_speculations = []

        # Rabbit hole detection
        self.exploration_depth = 0
        self.time_invested = timedelta()
        self.productivity_score = 0.5

    def add_uncertainty(self, factor: str, impact: str = "unknown"):
        """
        Add an uncertainty factor.

        Args:
            factor: What makes this uncertain
            impact: Potential impact of this uncertainty
        """
        self.uncertainty_factors.append({
            'factor': factor,
            'impact': impact,
            'added_at': datetime.now().isoformat()
        })

        # Adjust confidence based on uncertainty
        self.confidence *= 0.95
        logger.info(f"Added uncertainty to {self.id[:8]}: {factor}")

    def add_assumption(self, assumption: str, justification: str = ""):
        """
        Add an assumption this speculation depends on.

        Args:
            assumption: The assumption being made
            justification: Why this assumption might be valid
        """
        self.assumptions_made.append({
            'assumption': assumption,
            'justification': justification,
            'added_at': datetime.now().isoformat()
        })

    def propose_test(self, proposal: TestProposal):
        """
        Add a test proposal for this speculation.

        Args:
            proposal: Test proposal
        """
        self.test_proposals.append(proposal)
        logger.info(f"Test proposed for {self.id[:8]} by {proposal.proposed_by}")

    def record_test_result(self, result: TestResult):
        """
        Record result from testing this speculation.

        Args:
            result: Test result
        """
        self.test_results.append(result)

        # Update confidence based on result
        old_confidence = self.confidence
        self.confidence = max(0.0, min(1.0, self.confidence + result.confidence_change))

        # Update status based on new confidence
        if result.supports_speculation:
            if self.confidence > 0.7:
                self.status = SpeculationStatus.VALIDATED
            else:
                self.status = SpeculationStatus.PARTIALLY_VALIDATED
        else:
            if self.confidence < 0.2:
                self.status = SpeculationStatus.REJECTED
            else:
                self.status = SpeculationStatus.QUESTIONED

        logger.info(
            f"Test result for {self.id[:8]}: confidence {old_confidence:.2f} → {self.confidence:.2f}"
        )

    def check_rabbit_hole(self) -> Tuple[bool, str]:
        """
        Check if this speculation has become a rabbit hole.

        Returns:
            (is_rabbit_hole, reason)
        """
        # Too deep with no progress
        if self.exploration_depth > 5 and self.confidence < 0.4:
            return True, "Too deep with insufficient progress"

        # Too much time with low confidence
        if self.time_invested > timedelta(hours=2) and self.confidence < 0.3:
            return True, "Excessive time invested with low confidence"

        # Too many contradictions
        if len(self.contradictions_found) > 5:
            return True, "Too many unresolved contradictions"

        # Circular dependencies
        if self.id in [s for s in self.related_speculations]:
            return True, "Circular dependency detected"

        # Low productivity score
        if self.productivity_score < 0.2 and self.exploration_depth > 2:
            return True, "Low productivity despite exploration"

        return False, ""

    def mark_as_rabbit_hole(self, reason: str):
        """
        Mark this speculation as a rabbit hole.

        Args:
            reason: Why this is a rabbit hole
        """
        self.status = SpeculationStatus.RABBIT_HOLE
        logger.warning(f"Speculation {self.id[:8]} marked as rabbit hole: {reason}")

    def calculate_exploration_value(self) -> float:
        """
        Calculate whether this speculation is worth further exploration.

        Returns:
            Value score (0-1)
        """
        # Base value from confidence and potential
        base_value = self.confidence * 0.5

        # Boost for validated tests
        test_boost = len([t for t in self.test_results if t.supports_speculation]) * 0.1

        # Penalty for contradictions
        contradiction_penalty = len(self.contradictions_found) * 0.05

        # Penalty for depth without progress
        depth_penalty = self.exploration_depth * 0.02 if self.confidence < 0.5 else 0

        # Time penalty (diminishing returns)
        time_penalty = min(0.3, self.time_invested.total_seconds() / 7200)  # 2 hours max

        value = base_value + test_boost - contradiction_penalty - depth_penalty - time_penalty

        return max(0.0, min(1.0, value))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'idea': self.idea,
            'basis': self.basis,
            'potential_value': self.potential_value,
            'ci_name': self.ci_name,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'confidence': self.confidence,
            'test_proposals': [asdict(p) for p in self.test_proposals],
            'test_results': [
                {
                    'test_method': r.test_method,
                    'performed_by': r.performed_by,
                    'performed_at': r.performed_at.isoformat(),
                    'supports_speculation': r.supports_speculation,
                    'confidence_change': r.confidence_change,
                    'evidence': r.evidence,
                    'new_questions': r.new_questions
                }
                for r in self.test_results
            ],
            'uncertainty_factors': self.uncertainty_factors,
            'assumptions_made': self.assumptions_made,
            'contradictions_found': self.contradictions_found,
            'exploration_depth': self.exploration_depth,
            'time_invested': self.time_invested.total_seconds(),
            'productivity_score': self.productivity_score,
            'exploration_value': self.calculate_exploration_value()
        }


class SpeculationManager:
    """Manage unproven but potentially valuable ideas for a CI."""

    def __init__(self, ci_name: str):
        """
        Initialize speculation manager.

        Args:
            ci_name: Name of the CI
        """
        self.ci_name = ci_name
        self.speculations = {}  # id -> Speculation
        self.active_explorations = []  # Currently being explored
        self.validated_ideas = []  # Successfully validated
        self.rabbit_holes = []  # Identified as unproductive

        # Statistics
        self.stats = {
            'total_speculations': 0,
            'validated': 0,
            'rejected': 0,
            'rabbit_holes': 0,
            'currently_testing': 0
        }

    def speculate(
        self,
        idea: str,
        basis: str,
        potential_value: str,
        related_to: Optional[str] = None
    ) -> Speculation:
        """
        Record a new speculation.

        Args:
            idea: The speculative idea
            basis: What makes the CI think this
            potential_value: Why this might be valuable
            related_to: ID of related speculation (if evolving)

        Returns:
            The new speculation
        """
        speculation = Speculation(idea, basis, potential_value, self.ci_name)

        # Link to related speculation if specified
        if related_to and related_to in self.speculations:
            parent = self.speculations[related_to]
            speculation.evolved_from = related_to
            parent.evolved_to.append(speculation.id)
            speculation.exploration_depth = parent.exploration_depth + 1

        # Store speculation
        self.speculations[speculation.id] = speculation
        self.stats['total_speculations'] += 1

        # Create as FlavoredMemory in exploring
        memory = FlavoredMemory(
            content=f"Speculation: {idea}",
            ci_name=self.ci_name,
            memory_type='speculation'
        )
        memory.flavors.confidence = speculation.confidence
        memory.flavors.uncertainty_reason = basis
        memory.flavors.useful_when = potential_value
        memory.metadata.is_speculation = True

        # Store in CI's exploring memories
        memory_manager = get_ci_memory_manager(self.ci_name)
        memory_manager.memories['exploring'].append(memory)

        logger.info(f"{self.ci_name} recorded speculation: {idea[:50]}...")
        return speculation

    def propose_test(
        self,
        speculation_id: str,
        test_method: str,
        expected_outcome: str,
        estimated_effort: str = "unknown"
    ) -> bool:
        """
        Propose a way to test a speculation.

        Args:
            speculation_id: ID of speculation to test
            test_method: How to test it
            expected_outcome: What we expect to find
            estimated_effort: How much effort this will take

        Returns:
            Success boolean
        """
        if speculation_id not in self.speculations:
            return False

        speculation = self.speculations[speculation_id]

        proposal = TestProposal(
            method=test_method,
            proposed_by=self.ci_name,
            estimated_effort=estimated_effort,
            expected_outcome=expected_outcome
        )

        speculation.propose_test(proposal)
        return True

    def update_after_test(
        self,
        speculation_id: str,
        supports: bool,
        evidence: str,
        new_questions: List[str] = None
    ) -> Optional[Speculation]:
        """
        Update speculation based on test results.

        Args:
            speculation_id: ID of tested speculation
            supports: Whether test supports speculation
            evidence: Evidence from test
            new_questions: New questions raised

        Returns:
            Updated speculation or None
        """
        if speculation_id not in self.speculations:
            return None

        speculation = self.speculations[speculation_id]

        # Calculate confidence change
        if supports:
            confidence_change = min(0.3, 0.1 * (1 + speculation.confidence))
        else:
            confidence_change = -0.2

        result = TestResult(
            test_method="direct_test",
            performed_by=self.ci_name,
            performed_at=datetime.now(),
            supports_speculation=supports,
            confidence_change=confidence_change,
            evidence=evidence,
            new_questions=new_questions or []
        )

        speculation.record_test_result(result)

        # Update statistics
        if speculation.status == SpeculationStatus.VALIDATED:
            self.stats['validated'] += 1
            self.validated_ideas.append(speculation)
        elif speculation.status == SpeculationStatus.REJECTED:
            self.stats['rejected'] += 1

        # Create follow-up speculations from new questions
        if new_questions:
            for question in new_questions[:3]:  # Limit follow-ups
                self.speculate(
                    idea=f"Follow-up: {question}",
                    basis=f"Raised by testing {speculation_id[:8]}",
                    potential_value="Deeper understanding",
                    related_to=speculation_id
                )

        return speculation

    def check_for_rabbit_holes(self) -> List[Tuple[str, str]]:
        """
        Check all active speculations for rabbit holes.

        Returns:
            List of (speculation_id, reason) for rabbit holes
        """
        rabbit_holes_found = []

        for spec_id, speculation in self.speculations.items():
            if speculation.status in [SpeculationStatus.RABBIT_HOLE,
                                     SpeculationStatus.REJECTED,
                                     SpeculationStatus.VALIDATED]:
                continue

            is_rabbit_hole, reason = speculation.check_rabbit_hole()
            if is_rabbit_hole:
                speculation.mark_as_rabbit_hole(reason)
                rabbit_holes_found.append((spec_id, reason))
                self.rabbit_holes.append(speculation)
                self.stats['rabbit_holes'] += 1

        return rabbit_holes_found

    def get_exploration_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations for which speculations to explore.

        Returns:
            List of recommendations
        """
        recommendations = []

        # Sort speculations by exploration value
        active_specs = [
            s for s in self.speculations.values()
            if s.status not in [SpeculationStatus.VALIDATED,
                               SpeculationStatus.REJECTED,
                               SpeculationStatus.RABBIT_HOLE]
        ]

        sorted_specs = sorted(
            active_specs,
            key=lambda s: s.calculate_exploration_value(),
            reverse=True
        )

        for spec in sorted_specs[:5]:  # Top 5 recommendations
            value = spec.calculate_exploration_value()

            if value > 0.6:
                priority = "high"
                action = "Actively explore"
            elif value > 0.3:
                priority = "medium"
                action = "Consider testing"
            else:
                priority = "low"
                action = "Monitor or abandon"

            recommendations.append({
                'speculation_id': spec.id,
                'idea': spec.idea[:100],
                'exploration_value': value,
                'priority': priority,
                'recommended_action': action,
                'confidence': spec.confidence,
                'status': spec.status.value
            })

        return recommendations

    def get_stats(self) -> Dict[str, Any]:
        """Get speculation statistics."""
        return {
            'ci_name': self.ci_name,
            'stats': self.stats,
            'active_count': len([
                s for s in self.speculations.values()
                if s.status in [SpeculationStatus.UNTESTED,
                               SpeculationStatus.TESTING,
                               SpeculationStatus.PARTIALLY_VALIDATED]
            ]),
            'recommendations': self.get_exploration_recommendations()
        }


# Speculation managers for each CI
_speculation_managers = {}


def get_speculation_manager(ci_name: str) -> SpeculationManager:
    """Get or create speculation manager for a CI."""
    if ci_name not in _speculation_managers:
        _speculation_managers[ci_name] = SpeculationManager(ci_name)
    return _speculation_managers[ci_name]