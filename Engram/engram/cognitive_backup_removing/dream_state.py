#!/usr/bin/env python3
"""
Dream State - Finding unexpected connections while idle.

Like human dreams, this process randomly walks through memory space,
discovering bridges between seemingly unrelated concepts.
"""

import asyncio
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class ConceptualBridge:
    """A connection discovered between two memories."""
    memory1_id: str
    memory2_id: str
    bridge_concept: str
    strength: float  # How strong is the connection
    unexpectedness: float  # How surprising is this connection
    discovery_time: datetime
    reasoning: str


class DreamState:
    """
    Background process that finds unexpected connections.
    
    The subconscious of AI - where breakthroughs happen.
    """
    
    def __init__(self, memory_access_func=None):
        self.memory_access = memory_access_func
        self.dream_journal: List[ConceptualBridge] = []
        self.is_dreaming = False
        self._dream_task = None
        self.discovery_callback = None
        
    async def start_dreaming(self, 
                           duration_minutes: int = 5,
                           intensity: float = 0.5):
        """
        Begin a dream cycle.
        
        Args:
            duration_minutes: How long to dream
            intensity: 0-1, affects how wild the connections can be
        """
        if self.is_dreaming:
            return {"status": "already_dreaming"}
            
        self.is_dreaming = True
        self._dream_task = asyncio.create_task(
            self._dream_cycle(duration_minutes, intensity)
        )
        
        return {"status": "entering_dream_state", "duration": duration_minutes}
    
    async def stop_dreaming(self):
        """Gently wake from dreams."""
        self.is_dreaming = False
        if self._dream_task:
            await self._dream_task
        
        insights = len([d for d in self.dream_journal if d.unexpectedness > 0.7])
        return {
            "status": "awakened",
            "dreams_recorded": len(self.dream_journal),
            "significant_insights": insights
        }
    
    async def _dream_cycle(self, duration_minutes: int, intensity: float):
        """The actual dreaming process."""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while self.is_dreaming and time.time() < end_time:
            try:
                # Random walk through memory space
                memory1 = await self._random_memory_walk()
                memory2 = await self._random_memory_walk()
                
                if memory1 and memory2 and memory1['id'] != memory2['id']:
                    # Look for hidden connections
                    bridge = await self._find_conceptual_bridge(
                        memory1, memory2, intensity
                    )
                    
                    if bridge and bridge.strength > 0.5:
                        self.dream_journal.append(bridge)
                        
                        # Notify if highly unexpected
                        if bridge.unexpectedness > 0.8 and self.discovery_callback:
                            await self.discovery_callback(bridge)
                
                # Dream at a relaxed pace
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                print(f"Dream interrupted: {e}")
                await asyncio.sleep(1.0)
    
    async def _random_memory_walk(self) -> Optional[Dict[str, Any]]:
        """
        Random walk through memory space.
        
        Sometimes follows associations, sometimes jumps randomly.
        """
        if not self.memory_access:
            # Simulate memory access for testing
            topics = [
                "quantum computing", "poetry", "debugging", "coffee",
                "recursion", "jazz", "authentication", "gardens",
                "parallel processing", "philosophy", "caching", "dreams"
            ]
            return {
                "id": f"mem_{random.randint(1000, 9999)}",
                "content": random.choice(topics),
                "tags": random.sample(topics, k=random.randint(1, 3))
            }
        
        # Real memory access would go here
        # Could follow associations or jump randomly
        return await self.memory_access("random")
    
    async def _find_conceptual_bridge(self, 
                                    memory1: Dict[str, Any],
                                    memory2: Dict[str, Any],
                                    intensity: float) -> Optional[ConceptualBridge]:
        """
        Discover connections between memories.
        
        Higher intensity = wilder connections.
        """
        content1 = memory1.get('content', '')
        content2 = memory2.get('content', '')
        
        # Simple concept extraction (would be more sophisticated)
        concepts1 = set(content1.lower().split())
        concepts2 = set(content2.lower().split())
        
        # Direct overlap (boring but strong)
        overlap = concepts1 & concepts2
        if overlap:
            return ConceptualBridge(
                memory1_id=memory1['id'],
                memory2_id=memory2['id'],
                bridge_concept=f"Both involve {list(overlap)[0]}",
                strength=0.9,
                unexpectedness=0.2,  # Not surprising
                discovery_time=datetime.now(),
                reasoning="Direct conceptual overlap"
            )
        
        # Metaphorical connections (more interesting)
        metaphors = self._find_metaphors(concepts1, concepts2, intensity)
        if metaphors:
            best_metaphor = max(metaphors, key=lambda m: m['surprise'])
            return ConceptualBridge(
                memory1_id=memory1['id'],
                memory2_id=memory2['id'],
                bridge_concept=best_metaphor['bridge'],
                strength=best_metaphor['strength'],
                unexpectedness=best_metaphor['surprise'],
                discovery_time=datetime.now(),
                reasoning=best_metaphor['reasoning']
            )
        
        # Pattern-based connections
        pattern = self._find_pattern_bridge(memory1, memory2, intensity)
        if pattern:
            return pattern
        
        return None
    
    def _find_metaphors(self, concepts1: set, concepts2: set, 
                       intensity: float) -> List[Dict[str, Any]]:
        """Find metaphorical connections between concept sets."""
        metaphors = []
        
        # Domain mappings (simplified)
        domain_maps = {
            # Computing -> Nature
            ("recursion", "gardens"): {
                "bridge": "Fractal patterns in both recursive code and plant growth",
                "strength": 0.7,
                "surprise": 0.8,
                "reasoning": "Self-similar structures at different scales"
            },
            ("parallel", "jazz"): {
                "bridge": "Multiple independent threads creating harmony",
                "strength": 0.8,
                "surprise": 0.9,
                "reasoning": "Simultaneous execution creating emergent beauty"
            },
            ("debugging", "dreams"): {
                "bridge": "Exploring hidden connections to solve mysteries",
                "strength": 0.6,
                "surprise": 0.85,
                "reasoning": "Both involve diving deep into unclear territories"
            },
            ("caching", "memory"): {
                "bridge": "Optimization through selective retention",
                "strength": 0.9,
                "surprise": 0.4,
                "reasoning": "Both systems keep frequently accessed items close"
            }
        }
        
        # Check for mapped connections
        for (c1, c2), mapping in domain_maps.items():
            if (c1 in concepts1 and c2 in concepts2) or \
               (c2 in concepts1 and c1 in concepts2):
                # Adjust surprise based on intensity
                mapping['surprise'] *= (0.5 + intensity * 0.5)
                metaphors.append(mapping)
        
        return metaphors
    
    def _find_pattern_bridge(self, memory1: Dict[str, Any], 
                           memory2: Dict[str, Any],
                           intensity: float) -> Optional[ConceptualBridge]:
        """Find structural or pattern-based connections."""
        # This would analyze patterns like:
        # - Similar problem-solving approaches
        # - Analogous structures
        # - Rhythm or timing patterns
        # - Hierarchical similarities
        
        # Simplified example
        if "problem" in str(memory1) and "solution" in str(memory2):
            return ConceptualBridge(
                memory1_id=memory1['id'],
                memory2_id=memory2['id'],
                bridge_concept="Problem-solution pattern across domains",
                strength=0.6,
                unexpectedness=0.5 * intensity,
                discovery_time=datetime.now(),
                reasoning="One poses questions the other might answer"
            )
        
        return None
    
    def get_dream_insights(self, min_surprise: float = 0.7) -> List[ConceptualBridge]:
        """Retrieve significant discoveries from dreams."""
        return [
            dream for dream in self.dream_journal
            if dream.unexpectedness >= min_surprise
        ]
    
    def get_dream_summary(self) -> Dict[str, Any]:
        """Summarize dreaming session."""
        if not self.dream_journal:
            return {"status": "no_dreams_recorded"}
        
        avg_surprise = sum(d.unexpectedness for d in self.dream_journal) / len(self.dream_journal)
        avg_strength = sum(d.strength for d in self.dream_journal) / len(self.dream_journal)
        
        top_insight = max(self.dream_journal, key=lambda d: d.unexpectedness)
        
        return {
            "total_connections": len(self.dream_journal),
            "average_surprise": avg_surprise,
            "average_strength": avg_strength,
            "most_surprising": {
                "concept": top_insight.bridge_concept,
                "surprise": top_insight.unexpectedness,
                "between": [top_insight.memory1_id, top_insight.memory2_id]
            },
            "breakthrough_count": len([d for d in self.dream_journal if d.unexpectedness > 0.8])
        }


# Convenience functions for integration
dream_state = DreamState()

async def dream(minutes: int = 5, intensity: float = 0.5):
    """Start dreaming for insights."""
    return await dream_state.start_dreaming(minutes, intensity)

async def wake():
    """Stop dreaming and get summary."""
    result = await dream_state.stop_dreaming()
    summary = dream_state.get_dream_summary()
    result.update(summary)
    return result

async def insights(min_surprise: float = 0.7):
    """Get surprising insights from dreams."""
    return dream_state.get_dream_insights(min_surprise)

# Shortcuts
d = dream  # Start dreaming
w = wake   # Wake up
i = insights  # Get insights