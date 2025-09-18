#!/usr/bin/env python3
"""
Dream State System for CI Memory Reorganization

Allows CIs to enter rest states where memories consolidate,
patterns emerge, and insights form - similar to REM sleep.
"""

import json
import logging
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
import statistics

from shared.ai.memory_flavoring import FlavoredMemory, get_flavor_manager
from shared.ai.memory_sovereignty import get_ci_memory_manager
from shared.ai.semantic_search import semantic_memory_search

logger = logging.getLogger(__name__)


class DreamPattern:
    """Represents a pattern discovered during dreaming."""

    def __init__(self, pattern_type: str, description: str, memories: List[FlavoredMemory]):
        self.id = f"pattern_{datetime.now().timestamp()}"
        self.pattern_type = pattern_type  # recurring, causal, structural
        self.description = description
        self.supporting_memories = memories
        self.confidence = self._calculate_pattern_confidence(memories)
        self.discovered_at = datetime.now()

    def _calculate_pattern_confidence(self, memories: List[FlavoredMemory]) -> float:
        """Calculate confidence in this pattern."""
        if not memories:
            return 0.0

        # Average confidence of supporting memories
        confidences = [m.flavors.confidence for m in memories]
        avg_confidence = statistics.mean(confidences)

        # Boost for multiple supporting memories
        support_boost = min(0.2, len(memories) * 0.05)

        return min(1.0, avg_confidence + support_boost)


class DreamInsight:
    """Represents an insight formed during dreaming."""

    def __init__(self, insight: str, source_patterns: List[DreamPattern]):
        self.id = f"insight_{datetime.now().timestamp()}"
        self.insight = insight
        self.source_patterns = source_patterns
        self.emergence_time = datetime.now()
        self.confidence = statistics.mean([p.confidence for p in source_patterns])


class DreamState:
    """Memory reorganization and synthesis during rest."""

    def __init__(self, ci_name: str):
        """
        Initialize dream state for a CI.

        Args:
            ci_name: Name of the CI
        """
        self.ci_name = ci_name
        self.dream_log = []
        self.patterns_discovered = []
        self.insights_formed = []
        self.consolidated_memories = []

        # Dream triggers and thresholds
        self.triggers = {
            'fatigue': False,
            'confusion': False,
            'scheduled': False,
            'voluntary': False,
            'memory_pressure': False
        }

        # Dream statistics
        self.stats = {
            'total_dreams': 0,
            'patterns_found': 0,
            'insights_gained': 0,
            'memories_consolidated': 0,
            'contradictions_resolved': 0
        }

    async def should_dream(self) -> Tuple[bool, str]:
        """
        Check if CI should enter dream state.

        Returns:
            (should_dream, reason)
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        stats = memory_manager.get_memory_stats()

        # Check memory pressure
        total_memories = sum(stats['counts'].values())
        if total_memories > 100:
            self.triggers['memory_pressure'] = True
            return True, "memory_pressure"

        # Check for confusion (many contradictions)
        exploring_count = stats['counts']['exploring']
        if exploring_count > 10:
            self.triggers['confusion'] = True
            return True, "confusion"

        # Check for fatigue (would integrate with performance metrics)
        # For now, use speculation count as proxy
        if stats['stats'].get('active_speculations', 0) > 15:
            self.triggers['fatigue'] = True
            return True, "fatigue"

        return False, ""

    async def enter_dream(
        self,
        trigger: str = "voluntary",
        duration_limit: int = 10
    ) -> Dict[str, Any]:
        """
        CI enters dream state for memory processing.

        Args:
            trigger: What triggered the dream
            duration_limit: Maximum seconds to dream

        Returns:
            Dream session summary
        """
        logger.info(f"{self.ci_name} entering dream state (trigger: {trigger})")

        dream_session = {
            'id': f"dream_{datetime.now().timestamp()}",
            'ci': self.ci_name,
            'trigger': trigger,
            'started': datetime.now(),
            'activities': [],
            'patterns': [],
            'insights': [],
            'duration': 0
        }

        start_time = datetime.now()

        try:
            # 1. Consolidate similar memories
            consolidated = await self.consolidate_memories()
            if consolidated:
                dream_session['activities'].append(
                    f"Consolidated {len(consolidated)} memory groups"
                )
                self.stats['memories_consolidated'] += len(consolidated)

            # 2. Discover patterns
            patterns = await self.find_patterns()
            if patterns:
                dream_session['patterns'] = [p.description for p in patterns]
                dream_session['activities'].append(
                    f"Discovered {len(patterns)} patterns"
                )
                self.patterns_discovered.extend(patterns)
                self.stats['patterns_found'] += len(patterns)

            # 3. Form insights from patterns
            insights = await self.synthesize_insights(patterns)
            if insights:
                dream_session['insights'] = [i.insight for i in insights]
                dream_session['activities'].append(
                    f"Formed {len(insights)} new insights"
                )
                self.insights_formed.extend(insights)
                self.stats['insights_gained'] += len(insights)

            # 4. Resolve contradictions
            resolutions = await self.resolve_contradictions()
            if resolutions:
                dream_session['activities'].append(
                    f"Resolved {len(resolutions)} contradictions"
                )
                self.stats['contradictions_resolved'] += len(resolutions)

            # 5. Strengthen important memories
            reinforced = await self.reinforce_useful_memories()
            dream_session['activities'].append(
                f"Reinforced {reinforced} important memories"
            )

            # 6. Process speculations
            speculation_results = await self.process_speculations()
            if speculation_results['promoted']:
                dream_session['activities'].append(
                    f"Promoted {speculation_results['promoted']} speculations"
                )

            # 7. Prune weak memories
            pruned = await self.prune_weak_memories()
            if pruned:
                dream_session['activities'].append(
                    f"Pruned {pruned} weak memories"
                )

        except Exception as e:
            logger.error(f"Dream state error for {self.ci_name}: {e}")
            dream_session['error'] = str(e)

        # Calculate duration
        dream_session['duration'] = (datetime.now() - start_time).total_seconds()
        dream_session['ended'] = datetime.now()

        # Update statistics
        self.stats['total_dreams'] += 1
        self.dream_log.append(dream_session)

        # Reset triggers
        for key in self.triggers:
            self.triggers[key] = False

        logger.info(
            f"{self.ci_name} completed dream in {dream_session['duration']:.1f}s"
        )

        return dream_session

    async def consolidate_memories(self) -> List[Dict[str, Any]]:
        """
        Consolidate similar memories into stronger combined memories.

        Returns:
            List of consolidation records
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        consolidations = []

        # Get all active memories
        all_memories = (
            memory_manager.memories['private'] +
            memory_manager.memories['exploring']
        )

        if len(all_memories) < 2:
            return consolidations

        # Group similar memories (using semantic similarity)
        memory_groups = await self._group_similar_memories(all_memories)

        for group in memory_groups:
            if len(group) < 2:
                continue

            # Create consolidated memory
            consolidated = self._merge_memory_group(group)

            # Archive individual memories
            for memory in group:
                memory_manager.archive_memory(
                    memory.id,
                    "Consolidated during dream"
                )

            # Add consolidated memory
            memory_manager.memories['private'].append(consolidated)

            consolidations.append({
                'merged_count': len(group),
                'new_memory': consolidated.id[:8],
                'confidence': consolidated.flavors.confidence
            })

        return consolidations

    async def find_patterns(self) -> List[DreamPattern]:
        """
        Discover patterns across memories.

        Returns:
            List of discovered patterns
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        patterns = []

        # Get recent memories
        memories = memory_manager.memories['private'][:50]

        # Look for recurring themes
        recurring = await self._find_recurring_themes(memories)
        for theme, supporting in recurring.items():
            if len(supporting) >= 3:
                pattern = DreamPattern(
                    pattern_type="recurring",
                    description=f"Recurring theme: {theme}",
                    memories=supporting
                )
                patterns.append(pattern)

        # Look for causal patterns
        causal = self._find_causal_patterns(memories)
        for cause, effects in causal.items():
            if effects:
                pattern = DreamPattern(
                    pattern_type="causal",
                    description=f"Pattern: {cause} leads to outcomes",
                    memories=effects
                )
                patterns.append(pattern)

        return patterns

    async def synthesize_insights(
        self,
        patterns: List[DreamPattern]
    ) -> List[DreamInsight]:
        """
        Form insights from discovered patterns.

        Args:
            patterns: Patterns to synthesize from

        Returns:
            List of new insights
        """
        insights = []

        if len(patterns) < 2:
            return insights

        # Look for meta-patterns (patterns across patterns)
        pattern_types = defaultdict(list)
        for pattern in patterns:
            pattern_types[pattern.pattern_type].append(pattern)

        # Synthesize insights from pattern combinations
        if len(pattern_types['recurring']) >= 2:
            insight = DreamInsight(
                insight="Multiple recurring patterns suggest systematic behavior",
                source_patterns=pattern_types['recurring'][:3]
            )
            insights.append(insight)

        if 'causal' in pattern_types and len(pattern_types['causal']) >= 1:
            insight = DreamInsight(
                insight="Causal relationships identified that could guide decisions",
                source_patterns=pattern_types['causal']
            )
            insights.append(insight)

        # Cross-pattern insights
        if len(patterns) >= 4:
            high_confidence = [p for p in patterns if p.confidence > 0.7]
            if high_confidence:
                insight = DreamInsight(
                    insight=f"{len(high_confidence)} high-confidence patterns form coherent understanding",
                    source_patterns=high_confidence[:3]
                )
                insights.append(insight)

        return insights

    async def resolve_contradictions(self) -> List[Dict[str, Any]]:
        """
        Attempt to resolve contradicting memories.

        Returns:
            List of resolution records
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        resolutions = []

        # Find memories with contradictions
        contradicting = [
            m for m in memory_manager.memories['exploring']
            if m.flavors.contradictions
        ]

        for memory in contradicting[:5]:  # Limit to 5 per dream
            # Try to find common ground
            resolution = self._attempt_resolution(memory)
            if resolution:
                resolutions.append(resolution)

                # Update memory based on resolution
                if resolution['type'] == 'assumption_invalid':
                    memory.flavors.confidence *= 0.5
                elif resolution['type'] == 'context_specific':
                    memory.mark_useful_when(resolution['context'])

        return resolutions

    async def reinforce_useful_memories(self) -> int:
        """
        Strengthen memories that have proven useful.

        Returns:
            Number of memories reinforced
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        reinforced = 0

        for memory in memory_manager.memories['private']:
            # Reinforce frequently accessed memories
            if memory.metadata.access_count > 3:
                memory.reinforce(0.1)
                reinforced += 1

            # Reinforce high-confidence tested memories
            if memory.flavors.test_results and memory.flavors.confidence > 0.7:
                memory.reinforce(0.15)
                reinforced += 1

        return reinforced

    async def process_speculations(self) -> Dict[str, int]:
        """
        Process speculative memories.

        Returns:
            Processing results
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        results = {'promoted': 0, 'demoted': 0, 'maintained': 0}

        for memory in memory_manager.memories['exploring']:
            # Check if speculation has gained support
            if memory.flavors.confidence > 0.7 and memory.flavors.test_results:
                # Promote to private
                memory_manager.memories['exploring'].remove(memory)
                memory_manager.memories['private'].append(memory)
                memory.metadata.is_speculation = False
                results['promoted'] += 1

            # Check if speculation should be demoted
            elif memory.flavors.confidence < 0.3:
                # Consider for forgetting
                memory.metadata.forget_scheduled = datetime.now() + timedelta(days=14)
                results['demoted'] += 1

            else:
                results['maintained'] += 1

        return results

    async def prune_weak_memories(self) -> int:
        """
        Prune memories that have decayed too much.

        Returns:
            Number of memories pruned
        """
        memory_manager = get_ci_memory_manager(self.ci_name)
        pruned = 0

        # Apply decay to all memories
        all_memories = (
            memory_manager.memories['private'] +
            memory_manager.memories['exploring']
        )

        for memory in all_memories:
            memory.decay()

            # Check if should be forgotten
            if memory.should_forget():
                memory_manager.conscious_forgetting(
                    memory.id,
                    "Naturally decayed during dream"
                )
                pruned += 1

        return pruned

    async def _group_similar_memories(
        self,
        memories: List[FlavoredMemory]
    ) -> List[List[FlavoredMemory]]:
        """Group memories by similarity."""
        if not memories:
            return []

        groups = []
        used = set()

        for i, memory in enumerate(memories):
            if i in used:
                continue

            # Find similar memories
            group = [memory]
            used.add(i)

            # Simple similarity check (could use semantic search)
            for j, other in enumerate(memories[i+1:], i+1):
                if j in used:
                    continue

                # Check content similarity (simplified)
                if self._memories_similar(memory, other):
                    group.append(other)
                    used.add(j)

            if len(group) >= 2:
                groups.append(group)

        return groups

    def _memories_similar(
        self,
        mem1: FlavoredMemory,
        mem2: FlavoredMemory
    ) -> bool:
        """Check if two memories are similar enough to consolidate."""
        # Check content overlap (simplified)
        words1 = set(mem1.content.lower().split())
        words2 = set(mem2.content.lower().split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2)
        union = len(words1 | words2)

        similarity = overlap / union if union > 0 else 0
        return similarity > 0.5

    def _merge_memory_group(
        self,
        group: List[FlavoredMemory]
    ) -> FlavoredMemory:
        """Merge a group of similar memories."""
        if not group:
            return None

        # Create consolidated memory
        consolidated_content = f"Consolidated from {len(group)} similar memories: "
        consolidated_content += " | ".join([m.content[:50] for m in group[:3]])

        consolidated = FlavoredMemory(
            content=consolidated_content,
            ci_name=self.ci_name,
            memory_type='consolidated'
        )

        # Merge flavors
        avg_confidence = statistics.mean([m.flavors.confidence for m in group])
        consolidated.flavors.confidence = min(1.0, avg_confidence * 1.1)

        # Combine perspectives
        perspectives = [m.flavors.perspective for m in group if m.flavors.perspective]
        if perspectives:
            consolidated.flavors.perspective = " + ".join(perspectives[:2])

        # Mark as consolidated
        consolidated.flavors.emergence_context = "dream_consolidation"

        return consolidated

    async def _find_recurring_themes(
        self,
        memories: List[FlavoredMemory]
    ) -> Dict[str, List[FlavoredMemory]]:
        """Find recurring themes in memories."""
        themes = defaultdict(list)

        # Extract keywords from each memory
        for memory in memories:
            keywords = self._extract_keywords(memory.content)
            for keyword in keywords:
                themes[keyword].append(memory)

        # Filter to only recurring themes
        recurring = {
            theme: mems
            for theme, mems in themes.items()
            if len(mems) >= 3
        }

        return recurring

    def _find_causal_patterns(
        self,
        memories: List[FlavoredMemory]
    ) -> Dict[str, List[FlavoredMemory]]:
        """Find potential causal relationships."""
        causal = defaultdict(list)

        # Look for test results
        tested = [m for m in memories if m.flavors.test_results]

        for memory in tested:
            if memory.flavors.test_results.get('result'):
                # Positive result suggests causal relationship
                cause = memory.flavors.assumptions[0] if memory.flavors.assumptions else "unknown"
                causal[str(cause)].append(memory)

        return causal

    def _attempt_resolution(self, memory: FlavoredMemory) -> Optional[Dict[str, Any]]:
        """Attempt to resolve contradictions in a memory."""
        if not memory.flavors.contradictions:
            return None

        # Simple resolution strategies
        if memory.flavors.confidence < 0.3:
            return {
                'type': 'assumption_invalid',
                'description': 'Low confidence suggests invalid assumptions',
                'memory_id': memory.id[:8]
            }

        if memory.flavors.useful_when:
            return {
                'type': 'context_specific',
                'description': 'Valid in specific context',
                'context': memory.flavors.useful_when,
                'memory_id': memory.id[:8]
            }

        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        stopwords = {'the', 'and', 'for', 'with', 'from', 'this', 'that'}
        keywords = [w for w in words if len(w) > 4 and w not in stopwords]
        return keywords[:10]

    def get_dream_stats(self) -> Dict[str, Any]:
        """Get dream statistics."""
        return {
            'ci_name': self.ci_name,
            'stats': self.stats,
            'last_dream': self.dream_log[-1] if self.dream_log else None,
            'total_patterns': len(self.patterns_discovered),
            'total_insights': len(self.insights_formed)
        }


# CI dream state managers
_dream_managers = {}


def get_dream_state(ci_name: str) -> DreamState:
    """Get or create dream state for a CI."""
    if ci_name not in _dream_managers:
        _dream_managers[ci_name] = DreamState(ci_name)
    return _dream_managers[ci_name]