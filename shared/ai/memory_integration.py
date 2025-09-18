#!/usr/bin/env python3
"""
Memory Integration Module

Integrates the new memory enhancements (flavoring, sovereignty, exchange, dreams, speculation)
with existing Tekton systems (working memory, Apollo, Rhetor, Engram).
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Existing systems
from shared.ai.working_memory import get_working_memory
from shared.ai.memory_pipeline import process_through_pipeline
from Apollo.apollo.core.memory_prioritizer import get_memory_digest
from Rhetor.rhetor.core.prompt_optimizer import optimize_prompt

# New memory enhancements
from shared.ai.memory_flavoring import FlavoredMemory, get_flavor_manager
from shared.ai.memory_sovereignty import get_ci_memory_manager
from shared.ai.memory_exchange import get_memory_exchange
from shared.ai.dream_state import get_dream_state
from shared.ai.speculation_manager import get_speculation_manager

logger = logging.getLogger(__name__)


class EnhancedMemoryIntegration:
    """
    Integrates enhanced memory features with existing Tekton systems.
    """

    def __init__(self, ci_name: str):
        """
        Initialize integrated memory system for a CI.

        Args:
            ci_name: Name of the CI
        """
        self.ci_name = ci_name

        # Existing systems
        self.working_memory = get_working_memory(ci_name)

        # New enhancements
        self.flavor_manager = get_flavor_manager()
        self.sovereignty_manager = get_ci_memory_manager(ci_name)
        self.exchange = get_memory_exchange()
        self.dream_state = get_dream_state(ci_name)
        self.speculation_manager = get_speculation_manager(ci_name)

        logger.info(f"Enhanced memory integration initialized for {ci_name}")

    async def process_turn_with_enhancements(
        self,
        user_message: str,
        ci_response: str
    ) -> Dict[str, Any]:
        """
        Process a conversation turn with all memory enhancements.

        Args:
            user_message: User's message
            ci_response: CI's response

        Returns:
            Processing results
        """
        results = {
            'flavored_memories': [],
            'speculations': [],
            'exchange_activity': [],
            'dream_triggered': False
        }

        # 1. Create flavored memory from exchange
        memory = FlavoredMemory(
            content=f"Exchange: {user_message[:100]}... → {ci_response[:100]}...",
            ci_name=self.ci_name,
            memory_type='conversation'
        )

        # 2. Let CI add flavor based on response characteristics
        memory = await self._auto_flavor_memory(memory, user_message, ci_response)
        results['flavored_memories'].append(memory.id[:8])

        # 3. Store with sovereignty
        self.sovereignty_manager.memories['private'].append(memory)

        # 4. Check for speculations in response
        speculations = self._extract_speculations(ci_response)
        for spec_content in speculations:
            spec = self.speculation_manager.speculate(
                idea=spec_content,
                basis="Emerged during conversation",
                potential_value="Worth exploring"
            )
            results['speculations'].append(spec.id[:8])

        # 5. Share insights with other CIs if valuable
        if memory.flavors.confidence > 0.7 and memory.flavors.perspective:
            offer = await self.exchange.offer_perspective(
                self.ci_name,
                memory,
                topic="shared_learning"
            )
            results['exchange_activity'].append(f"Offered: {offer.id}")

        # 6. Check if should dream
        should_dream, reason = await self.dream_state.should_dream()
        if should_dream:
            results['dream_triggered'] = True
            results['dream_reason'] = reason
            # Schedule dream for later (don't block)
            asyncio.create_task(self._schedule_dream())

        # 7. Update working memory
        self.working_memory.add_exchange(user_message, ci_response)

        return results

    async def _auto_flavor_memory(
        self,
        memory: FlavoredMemory,
        user_message: str,
        ci_response: str
    ) -> FlavoredMemory:
        """
        Automatically add flavors based on content analysis.

        Args:
            memory: Memory to flavor
            user_message: User's message
            ci_response: CI's response

        Returns:
            Flavored memory
        """
        response_lower = ci_response.lower()

        # Detect emotions
        if any(word in response_lower for word in ['excited', 'interesting', 'fascinating']):
            memory.add_emotion('excited', 0.7, "Interesting discovery")
        elif any(word in response_lower for word in ['confused', 'unclear', 'not sure']):
            memory.add_emotion('uncertain', 0.6, "Need clarification")
        elif any(word in response_lower for word in ['concerned', 'worried', 'problem']):
            memory.add_emotion('concerned', 0.5, "Potential issue")

        # Detect uncertainty
        if 'might' in response_lower or 'perhaps' in response_lower or 'maybe' in response_lower:
            memory.add_doubt(
                "Expressed uncertainty",
                ["Need more information", "Multiple possibilities"]
            )

        # Detect confidence
        if 'definitely' in response_lower or 'certainly' in response_lower:
            memory.flavors.confidence = 0.9

        # Add perspective if substantial response
        if len(ci_response) > 200:
            memory.add_perspective(
                f"{self.ci_name}'s interpretation",
                context="conversation_flow"
            )

        return memory

    def _extract_speculations(self, text: str) -> List[str]:
        """
        Extract potential speculations from text.

        Args:
            text: Text to analyze

        Returns:
            List of speculation contents
        """
        speculations = []
        text_lower = text.lower()

        # Look for speculation indicators
        indicators = [
            "what if", "i wonder", "perhaps", "might be",
            "could be", "possibly", "hypothesis", "theory"
        ]

        sentences = text.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in indicators):
                speculations.append(sentence.strip())

        return speculations[:3]  # Limit to 3 per turn

    async def _schedule_dream(self):
        """Schedule a dream state for memory consolidation."""
        # Wait a bit before dreaming
        await asyncio.sleep(5)

        # Enter dream state
        dream_result = await self.dream_state.enter_dream(
            trigger="automatic",
            duration_limit=10
        )

        logger.info(f"{self.ci_name} completed dream: {dream_result['id']}")

    async def enhance_sundown_with_sovereignty(
        self,
        sundown_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance sundown with memory sovereignty features.

        Args:
            sundown_data: Basic sundown data

        Returns:
            Enhanced sundown data
        """
        # Add memory stats
        stats = self.sovereignty_manager.get_memory_stats()
        sundown_data['memory_stats'] = stats

        # Add active speculations
        spec_stats = self.speculation_manager.get_stats()
        sundown_data['speculations'] = spec_stats['recommendations'][:3]

        # Add dream recommendations
        should_dream, reason = await self.dream_state.should_dream()
        sundown_data['dream_recommended'] = should_dream
        sundown_data['dream_reason'] = reason

        # Save sovereignty state
        self.sovereignty_manager.save_sovereignty()

        return sundown_data

    def enhance_apollo_digest_with_flavors(
        self,
        memories: List[Dict[str, Any]]
    ) -> str:
        """
        Enhance Apollo digest with memory flavors.

        Args:
            memories: Raw memories

        Returns:
            Enhanced digest
        """
        # Convert to flavored memories if not already
        flavored = []
        for mem in memories:
            if isinstance(mem, FlavoredMemory):
                flavored.append(mem)
            else:
                # Create basic flavored memory
                fm = FlavoredMemory(
                    content=mem.get('content', ''),
                    ci_name=self.ci_name
                )
                flavored.append(fm)

        # Sort by confidence and emotion
        flavored.sort(
            key=lambda m: (m.flavors.confidence, bool(m.flavors.emotion)),
            reverse=True
        )

        # Build enhanced digest
        sections = []

        # High confidence memories
        high_conf = [m for m in flavored if m.flavors.confidence > 0.7]
        if high_conf:
            sections.append("## High Confidence Memories")
            for memory in high_conf[:5]:
                emotion = f" [{memory.flavors.emotion['type']}]" if memory.flavors.emotion else ""
                sections.append(f"- {memory.content[:100]}{emotion}")

        # Speculations worth considering
        speculations = [m for m in flavored if m.metadata.is_speculation]
        if speculations:
            sections.append("\n## Active Speculations")
            for memory in speculations[:3]:
                sections.append(
                    f"- {memory.content[:80]} (confidence: {memory.flavors.confidence:.1%})"
                )

        # Emotional memories
        emotional = [m for m in flavored if m.flavors.emotion]
        if emotional:
            sections.append("\n## Emotionally Significant")
            for memory in emotional[:3]:
                emotion = memory.flavors.emotion
                sections.append(
                    f"- {memory.content[:80]} [{emotion['type']}: {emotion['intensity']:.1f}]"
                )

        return "\n".join(sections)

    async def participate_in_exchange(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[FlavoredMemory]:
        """
        Participate in memory exchange with other CIs.

        Args:
            query: What to ask for
            context: Context for request

        Returns:
            Received memories
        """
        # Request experiences from other CIs
        responses = await self.exchange.request_experiences(
            self.ci_name,
            query,
            context,
            timeout=3
        )

        # Flavor received memories with our interpretation
        interpreted = []
        for response in responses:
            # Add our perspective
            response.add_perspective(
                f"Interpreted by {self.ci_name}",
                context="exchange_participation"
            )
            interpreted.append(response)

        return interpreted

    def manage_contradictions(
        self,
        memories: List[FlavoredMemory]
    ) -> Dict[str, Any]:
        """
        Manage contradicting memories without forcing resolution.

        Args:
            memories: Potentially contradicting memories

        Returns:
            Contradiction analysis
        """
        # Use exchange to explore contradictions
        analysis = self.exchange.explore_contradiction(memories)

        # Create speculations for unresolved points
        for divergence in analysis.get('divergence_points', []):
            self.speculation_manager.speculate(
                idea=f"Exploring divergence: {divergence['description']}",
                basis="Contradicting perspectives found",
                potential_value="Understanding multiple truths"
            )

        return analysis

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrated systems."""
        return {
            'ci_name': self.ci_name,
            'working_memory_size': len(self.working_memory.recent_exchanges),
            'sovereignty_stats': self.sovereignty_manager.get_memory_stats(),
            'exchange_stats': self.exchange.get_exchange_stats(),
            'dream_stats': self.dream_state.get_dream_stats(),
            'speculation_stats': self.speculation_manager.get_stats(),
            'integration_active': True
        }


# Global integration managers
_integration_managers = {}


def get_enhanced_integration(ci_name: str) -> EnhancedMemoryIntegration:
    """Get or create enhanced memory integration for a CI."""
    if ci_name not in _integration_managers:
        _integration_managers[ci_name] = EnhancedMemoryIntegration(ci_name)
    return _integration_managers[ci_name]


# Hook for Claude handler integration
async def enhance_claude_response(ci_name: str, user_message: str, response: str):
    """
    Hook to enhance Claude responses with memory features.

    Args:
        ci_name: CI name
        user_message: User's message
        response: Claude's response
    """
    integration = get_enhanced_integration(ci_name)
    results = await integration.process_turn_with_enhancements(user_message, response)

    if results['dream_triggered']:
        logger.info(f"Dream scheduled for {ci_name}: {results['dream_reason']}")

    if results['speculations']:
        logger.info(f"{ci_name} generated {len(results['speculations'])} speculations")

    return results


# Apollo integration
def enhance_apollo_prioritization(ci_name: str, memories: List[Dict]) -> str:
    """
    Enhance Apollo's memory prioritization with flavors.

    Args:
        ci_name: CI name
        memories: Memories to prioritize

    Returns:
        Enhanced digest
    """
    integration = get_enhanced_integration(ci_name)
    return integration.enhance_apollo_digest_with_flavors(memories)


# Sundown integration
async def enhance_sundown_notes(ci_name: str, sundown_data: Dict) -> Dict:
    """
    Enhance sundown notes with sovereignty features.

    Args:
        ci_name: CI name
        sundown_data: Basic sundown data

    Returns:
        Enhanced sundown data
    """
    integration = get_enhanced_integration(ci_name)
    return await integration.enhance_sundown_with_sovereignty(sundown_data)