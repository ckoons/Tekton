#!/usr/bin/env python3
"""
Memory Exchange System for Cross-CI Communication

Enables rich memory sharing between CIs with perspectives,
consensus building, and collective intelligence emergence.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
import statistics

from shared.ai.memory_flavoring import FlavoredMemory
from shared.ai.memory_sovereignty import get_ci_memory_manager

logger = logging.getLogger(__name__)


class MemoryOffer:
    """Represents a memory offered for sharing."""

    def __init__(self, from_ci: str, memory: FlavoredMemory, topic: str):
        self.id = f"offer_{datetime.now().timestamp()}"
        self.from_ci = from_ci
        self.memory = memory
        self.topic = topic
        self.offered_at = datetime.now()
        self.responses = []
        self.accepted_by = []
        self.perspective = memory.flavors.perspective
        self.confidence = memory.flavors.confidence
        self.seeking = 'alternative_views'
        self.invited = []  # Specific CIs or 'all'


class MemoryRequest:
    """Represents a request for memories."""

    def __init__(self, from_ci: str, query: str, context: Dict[str, Any]):
        self.id = f"request_{datetime.now().timestamp()}"
        self.from_ci = from_ci
        self.query = query
        self.context = context
        self.requested_at = datetime.now()
        self.responses = []
        self.offering_in_return = 'will_share_results'


class ConsensusMemory:
    """Represents a memory agreed upon by multiple CIs."""

    def __init__(self, topic: str, memories: List[FlavoredMemory]):
        self.id = f"consensus_{datetime.now().timestamp()}"
        self.topic = topic
        self.memories = memories
        self.agreed_by = [m.ci_name for m in memories]
        self.created_at = datetime.now()

        # Calculate consensus confidence
        confidences = [m.flavors.confidence for m in memories]
        self.consensus_confidence = statistics.mean(confidences)
        self.confidence_variance = statistics.variance(confidences) if len(confidences) > 1 else 0

        # Collect perspectives
        self.perspectives = {
            m.ci_name: m.flavors.perspective
            for m in memories if m.flavors.perspective
        }

        # Identify dissent
        self.dissent = [
            m for m in memories
            if m.flavors.confidence < self.consensus_confidence - 0.2
        ]

        # Find contradictions
        all_contradictions = []
        for m in memories:
            all_contradictions.extend(m.flavors.contradictions)
        self.unresolved_contradictions = list(set(all_contradictions))


class MemoryExchange:
    """Marketplace for memory sharing between CIs."""

    def __init__(self):
        """Initialize the memory exchange."""
        self.offers = {}          # Active memory offers
        self.requests = {}        # Active memory requests
        self.channels = defaultdict(list)  # Topic-based channels
        self.consensus_memories = []       # Validated consensus memories
        self.exchange_stats = {
            'total_offers': 0,
            'total_requests': 0,
            'total_exchanges': 0,
            'consensus_formed': 0
        }

        # CI participation tracking
        self.ci_activity = defaultdict(lambda: {
            'offers_made': 0,
            'requests_made': 0,
            'responses_given': 0,
            'consensus_participated': 0
        })

        logger.info("Memory Exchange initialized")

    async def offer_perspective(
        self,
        ci_name: str,
        memory: FlavoredMemory,
        topic: str,
        invitation: List[str] = None
    ) -> MemoryOffer:
        """
        CI offers their perspective on something.

        Args:
            ci_name: CI making the offer
            memory: Memory to share
            topic: Topic/channel for the memory
            invitation: Specific CIs to invite (None = all)

        Returns:
            The memory offer
        """
        offer = MemoryOffer(ci_name, memory, topic)
        offer.invited = invitation or ['all']

        # Store offer
        self.offers[offer.id] = offer

        # Add to topic channel
        self.channels[topic].append(offer)

        # Update stats
        self.exchange_stats['total_offers'] += 1
        self.ci_activity[ci_name]['offers_made'] += 1

        # Notify invited CIs
        await self._notify_cis(offer)

        logger.info(f"{ci_name} offered perspective on {topic}")
        return offer

    async def request_experiences(
        self,
        ci_name: str,
        query: str,
        context: Dict[str, Any],
        timeout: int = 5
    ) -> List[FlavoredMemory]:
        """
        CI asks others for relevant experiences.

        Args:
            ci_name: CI making request
            query: What they're looking for
            context: Context for the request
            timeout: Seconds to wait for responses

        Returns:
            List of relevant memories from other CIs
        """
        request = MemoryRequest(ci_name, query, context)

        # Store request
        self.requests[request.id] = request

        # Update stats
        self.exchange_stats['total_requests'] += 1
        self.ci_activity[ci_name]['requests_made'] += 1

        # Notify all CIs
        await self._broadcast_request(request)

        # Wait for responses
        await asyncio.sleep(timeout)

        # Gather and interpret responses
        responses = await self._gather_responses(request)

        # CI interprets responses through their lens
        interpreted = self._interpret_responses(ci_name, responses)

        # Share results as promised
        if request.offering_in_return == 'will_share_results' and interpreted:
            result_memory = FlavoredMemory(
                content=f"Results from query: {query}",
                ci_name=ci_name,
                memory_type='synthesis'
            )
            result_memory.add_perspective(
                f"Synthesized from {len(interpreted)} responses",
                context="collective_inquiry"
            )
            await self.offer_perspective(ci_name, result_memory, "shared_learning")

        return interpreted

    def form_consensus(
        self,
        topic: str,
        memories: List[FlavoredMemory],
        threshold: float = 0.7
    ) -> Optional[ConsensusMemory]:
        """
        Form consensus from multiple CI perspectives.

        Args:
            topic: Topic of consensus
            memories: Memories to form consensus from
            threshold: Agreement threshold (0-1)

        Returns:
            Consensus memory if agreement reached
        """
        if len(memories) < 2:
            return None

        # Calculate agreement level
        agreement = self._calculate_agreement(memories)

        if agreement < threshold:
            logger.info(f"Consensus not reached on {topic}: {agreement:.2f} < {threshold}")
            return None

        # Create consensus
        consensus = ConsensusMemory(topic, memories)

        # Store consensus
        self.consensus_memories.append(consensus)

        # Update stats
        self.exchange_stats['consensus_formed'] += 1
        for ci_name in consensus.agreed_by:
            self.ci_activity[ci_name]['consensus_participated'] += 1

        logger.info(f"Consensus formed on {topic} by {consensus.agreed_by}")

        # Handle unresolved contradictions
        if consensus.unresolved_contradictions:
            self._create_exploration_tasks(consensus.unresolved_contradictions)

        return consensus

    def explore_contradiction(
        self,
        memories: List[FlavoredMemory]
    ) -> Dict[str, Any]:
        """
        Explore contradicting perspectives without forcing resolution.

        Args:
            memories: Contradicting memories

        Returns:
            Analysis of contradictions
        """
        if len(memories) < 2:
            return {'error': 'Need at least 2 memories to explore contradictions'}

        # Group by perspective
        perspectives = defaultdict(list)
        for memory in memories:
            if memory.flavors.perspective:
                perspectives[memory.flavors.perspective].append(memory)

        # Analyze assumptions
        assumption_sets = []
        for memory in memories:
            if memory.flavors.assumptions:
                assumption_sets.append({
                    'ci': memory.ci_name,
                    'assumptions': memory.flavors.assumptions,
                    'confidence': memory.flavors.confidence
                })

        # Find common ground
        common_ground = self._find_common_elements(memories)

        # Identify divergence points
        divergence_points = self._find_divergence_points(memories)

        analysis = {
            'contradiction_id': f"contra_{datetime.now().timestamp()}",
            'perspectives': dict(perspectives),
            'assumption_sets': assumption_sets,
            'common_ground': common_ground,
            'divergence_points': divergence_points,
            'recommendation': self._recommend_exploration_path(divergence_points)
        }

        logger.info(f"Explored contradiction with {len(memories)} perspectives")
        return analysis

    async def _notify_cis(self, offer: MemoryOffer):
        """Notify relevant CIs about an offer."""
        # In a real implementation, this would send notifications
        # For now, just log
        if offer.invited == ['all']:
            logger.debug(f"Broadcasting offer {offer.id} to all CIs")
        else:
            logger.debug(f"Notifying {offer.invited} about offer {offer.id}")

    async def _broadcast_request(self, request: MemoryRequest):
        """Broadcast a memory request to all CIs."""
        logger.debug(f"Broadcasting request {request.id}: {request.query}")

    async def _gather_responses(self, request: MemoryRequest) -> List[FlavoredMemory]:
        """Gather responses to a memory request."""
        # In real implementation, would collect from responding CIs
        # For now, check if any CI managers have relevant memories
        responses = []

        # Simulate gathering from different CIs
        # This would integrate with the actual CI memory managers
        logger.debug(f"Gathered {len(responses)} responses for request {request.id}")

        return responses

    def _interpret_responses(
        self,
        ci_name: str,
        responses: List[FlavoredMemory]
    ) -> List[FlavoredMemory]:
        """
        CI interprets responses through their own perspective.

        Args:
            ci_name: Interpreting CI
            responses: Raw responses

        Returns:
            Interpreted responses
        """
        interpreted = []

        for response in responses:
            # Create interpreted version
            interp = FlavoredMemory(
                content=response.content,
                ci_name=ci_name,
                memory_type='interpreted'
            )

            # Add interpretation layer
            interp.flavors.perspective = f"As understood by {ci_name}"
            interp.flavors.confidence = response.flavors.confidence * 0.9  # Slightly less confident
            interp.evolved_from = response.id

            interpreted.append(interp)

        return interpreted

    def _calculate_agreement(self, memories: List[FlavoredMemory]) -> float:
        """
        Calculate agreement level between memories.

        Args:
            memories: Memories to compare

        Returns:
            Agreement score (0-1)
        """
        if len(memories) < 2:
            return 1.0

        # Compare confidence levels
        confidences = [m.flavors.confidence for m in memories]
        avg_confidence = statistics.mean(confidences)

        # Check for contradictions
        total_contradictions = sum(len(m.flavors.contradictions) for m in memories)
        contradiction_penalty = min(0.5, total_contradictions * 0.1)

        # Check perspective alignment (simplified)
        unique_perspectives = set(m.flavors.perspective for m in memories
                                 if m.flavors.perspective)
        diversity_penalty = len(unique_perspectives) * 0.05

        agreement = avg_confidence - contradiction_penalty - diversity_penalty
        return max(0.0, min(1.0, agreement))

    def _find_common_elements(self, memories: List[FlavoredMemory]) -> List[str]:
        """Find common elements across memories."""
        common = []

        # Check for common assumptions
        all_assumptions = []
        for m in memories:
            for a in m.flavors.assumptions:
                if isinstance(a, dict):
                    all_assumptions.append(a.get('assumption', ''))
                else:
                    all_assumptions.append(str(a))

        # Find assumptions that appear multiple times
        assumption_counts = defaultdict(int)
        for assumption in all_assumptions:
            if assumption:
                assumption_counts[assumption] += 1

        for assumption, count in assumption_counts.items():
            if count >= len(memories) / 2:
                common.append(f"Shared assumption: {assumption}")

        return common

    def _find_divergence_points(self, memories: List[FlavoredMemory]) -> List[Dict]:
        """Identify where perspectives diverge."""
        divergence_points = []

        # Check confidence divergence
        confidences = [m.flavors.confidence for m in memories]
        if confidences:
            if max(confidences) - min(confidences) > 0.3:
                divergence_points.append({
                    'type': 'confidence',
                    'range': [min(confidences), max(confidences)],
                    'description': 'Significant confidence variation'
                })

        # Check assumption divergence
        assumption_sets = [set(str(a) for a in m.flavors.assumptions)
                          for m in memories]
        if len(assumption_sets) > 1:
            common_assumptions = set.intersection(*assumption_sets) if assumption_sets else set()
            unique_assumptions = set.union(*assumption_sets) - common_assumptions if assumption_sets else set()

            if unique_assumptions:
                divergence_points.append({
                    'type': 'assumptions',
                    'unique_count': len(unique_assumptions),
                    'description': f"{len(unique_assumptions)} differing assumptions"
                })

        return divergence_points

    def _recommend_exploration_path(self, divergence_points: List[Dict]) -> str:
        """Recommend how to explore contradictions productively."""
        if not divergence_points:
            return "Perspectives are well-aligned, consider testing together"

        recommendations = []

        for point in divergence_points:
            if point['type'] == 'confidence':
                recommendations.append(
                    "Test to increase confidence alignment"
                )
            elif point['type'] == 'assumptions':
                recommendations.append(
                    "Examine differing assumptions through controlled tests"
                )

        return " | ".join(recommendations)

    def _create_exploration_tasks(self, contradictions: List[str]):
        """Create tasks to explore unresolved contradictions."""
        for contradiction in contradictions:
            logger.info(f"Created exploration task for: {contradiction[:50]}")

    def get_exchange_stats(self) -> Dict[str, Any]:
        """Get statistics about the exchange."""
        return {
            'exchange_stats': self.exchange_stats,
            'active_offers': len(self.offers),
            'active_requests': len(self.requests),
            'total_consensus': len(self.consensus_memories),
            'topics': list(self.channels.keys()),
            'participating_cis': list(self.ci_activity.keys())
        }


# Global exchange instance
_memory_exchange = MemoryExchange()


def get_memory_exchange() -> MemoryExchange:
    """Get the global memory exchange."""
    return _memory_exchange