#!/usr/bin/env python3
"""
Memory fusion - combining similar memories into stronger truths.

When multiple sources report similar things, we can extract common elements
and preserve unique perspectives.
"""

from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio


@dataclass
class FusedMemory:
    """A memory created from fusing multiple similar memories."""
    fusion_id: str
    source_memories: List[str]  # IDs of original memories
    common_content: str  # What they agree on
    perspectives: Dict[str, str]  # source_id -> unique perspective
    confidence: float  # Collective confidence
    fusion_time: datetime
    fusion_reason: str


class MemoryFusionEngine:
    """
    Fuses similar memories from different sources into unified understanding.
    
    Like consensus building - finds common truth while preserving perspectives.
    """
    
    def __init__(self):
        self.fused_memories: Dict[str, FusedMemory] = {}
        self.fusion_threshold = 0.7  # Similarity threshold for fusion
        
    async def analyze_for_fusion(self, memories: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Analyze memories to find fusion candidates.
        
        Returns groups of memories that could be fused.
        """
        if len(memories) < 2:
            return []
        
        fusion_groups = []
        processed = set()
        
        for i, mem1 in enumerate(memories):
            if i in processed:
                continue
                
            group = [mem1]
            processed.add(i)
            
            for j, mem2 in enumerate(memories[i+1:], i+1):
                if j in processed:
                    continue
                    
                similarity = self._calculate_similarity(mem1, mem2)
                if similarity >= self.fusion_threshold:
                    group.append(mem2)
                    processed.add(j)
            
            if len(group) > 1:
                fusion_groups.append(group)
        
        return fusion_groups
    
    async def fuse_memories(self, similar_memories: List[Dict[str, Any]], 
                          reason: str = "High similarity detected") -> FusedMemory:
        """
        Fuse similar memories into a unified memory.
        
        Extracts consensus while preserving unique insights.
        """
        if len(similar_memories) < 2:
            raise ValueError("Need at least 2 memories to fuse")
        
        # Extract common elements
        common_elements = self._extract_consensus(similar_memories)
        
        # Preserve unique perspectives
        perspectives = self._extract_perspectives(similar_memories, common_elements)
        
        # Calculate collective confidence
        confidence = self._calculate_collective_confidence(similar_memories)
        
        # Create fused memory
        fusion_id = f"fusion_{datetime.now().timestamp():.0f}"
        fused = FusedMemory(
            fusion_id=fusion_id,
            source_memories=[m.get('id', f'mem_{i}') for i, m in enumerate(similar_memories)],
            common_content=common_elements,
            perspectives=perspectives,
            confidence=confidence,
            fusion_time=datetime.now(),
            fusion_reason=reason
        )
        
        self.fused_memories[fusion_id] = fused
        
        return fused
    
    def _calculate_similarity(self, mem1: Dict[str, Any], mem2: Dict[str, Any]) -> float:
        """Calculate similarity between two memories."""
        content1 = mem1.get('content', '').lower()
        content2 = mem2.get('content', '').lower()
        
        # Simple word overlap (would use embeddings in production)
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        base_similarity = intersection / union if union > 0 else 0.0
        
        # Boost if same category or tags
        if mem1.get('category') == mem2.get('category'):
            base_similarity *= 1.2
        
        tags1 = set(mem1.get('tags', []))
        tags2 = set(mem2.get('tags', []))
        if tags1 & tags2:
            base_similarity *= 1.1
        
        return min(base_similarity, 1.0)
    
    def _extract_consensus(self, memories: List[Dict[str, Any]]) -> str:
        """Extract what all memories agree on."""
        # Get all content
        all_content = [m.get('content', '') for m in memories]
        
        # Find common words/phrases (simplified)
        word_counts = {}
        for content in all_content:
            words = content.lower().split()
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Words that appear in majority of memories
        threshold = len(memories) * 0.6
        common_words = [
            word for word, count in word_counts.items()
            if count >= threshold and len(word) > 3
        ]
        
        # Build consensus statement
        if not common_words:
            return "Multiple related observations"
        
        # Try to preserve some structure
        consensus_parts = []
        for content in all_content:
            sentences = content.split('.')
            for sentence in sentences:
                sentence_words = set(sentence.lower().split())
                if len(sentence_words & set(common_words)) >= 3:
                    consensus_parts.append(sentence.strip())
                    break
        
        if consensus_parts:
            # Return most representative sentence
            return max(consensus_parts, key=lambda s: len(set(s.lower().split()) & set(common_words)))
        
        return f"Common concepts: {', '.join(common_words[:5])}"
    
    def _extract_perspectives(self, memories: List[Dict[str, Any]], 
                            common_content: str) -> Dict[str, str]:
        """Extract unique perspective from each memory."""
        perspectives = {}
        common_words = set(common_content.lower().split())
        
        for mem in memories:
            mem_id = mem.get('id', 'unknown')
            content = mem.get('content', '')
            
            # Find unique aspects
            mem_words = set(content.lower().split())
            unique_words = mem_words - common_words
            
            # Extract sentences with unique content
            unique_sentences = []
            for sentence in content.split('.'):
                sentence_words = set(sentence.lower().split())
                if sentence_words & unique_words:
                    unique_sentences.append(sentence.strip())
            
            if unique_sentences:
                perspectives[mem_id] = '. '.join(unique_sentences[:2])
            else:
                # Note the source even if no unique content
                source = mem.get('metadata', {}).get('source', 'unknown')
                perspectives[mem_id] = f"Confirmed by {source}"
        
        return perspectives
    
    def _calculate_collective_confidence(self, memories: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on consensus and individual confidences."""
        # Get individual confidences
        confidences = []
        for mem in memories:
            conf = mem.get('confidence', 0.5)
            if isinstance(mem.get('metadata'), dict):
                conf = mem['metadata'].get('confidence', conf)
            confidences.append(conf)
        
        if not confidences:
            return 0.5
        
        # Average confidence
        avg_conf = sum(confidences) / len(confidences)
        
        # Boost for consensus
        consensus_boost = min(0.2, len(memories) * 0.05)
        
        # Penalty for high variance (disagreement)
        if len(confidences) > 1:
            variance = sum((c - avg_conf) ** 2 for c in confidences) / len(confidences)
            variance_penalty = variance * 0.5
        else:
            variance_penalty = 0
        
        final_confidence = avg_conf + consensus_boost - variance_penalty
        
        return max(0.0, min(1.0, final_confidence))
    
    async def auto_fuse(self, memories: List[Dict[str, Any]], 
                       min_group_size: int = 2) -> List[FusedMemory]:
        """Automatically find and fuse similar memories."""
        fusion_groups = await self.analyze_for_fusion(memories)
        
        fused_results = []
        for group in fusion_groups:
            if len(group) >= min_group_size:
                fused = await self.fuse_memories(
                    group,
                    reason=f"Auto-fusion: {len(group)} similar memories"
                )
                fused_results.append(fused)
        
        return fused_results
    
    def get_fusion_report(self, fusion_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed report about a fusion."""
        fused = self.fused_memories.get(fusion_id)
        if not fused:
            return None
        
        return {
            "fusion_id": fused.fusion_id,
            "source_count": len(fused.source_memories),
            "consensus": fused.common_content,
            "confidence": fused.confidence,
            "perspectives": fused.perspectives,
            "fusion_time": fused.fusion_time.isoformat(),
            "reason": fused.fusion_reason
        }


# Global fusion engine
fusion_engine = MemoryFusionEngine()

# Convenience functions
async def fuse(memories: List[Dict[str, Any]], reason: Optional[str] = None) -> FusedMemory:
    """Manually fuse similar memories."""
    return await fusion_engine.fuse_memories(
        memories, 
        reason or "Manual fusion requested"
    )

async def auto_fuse(memories: List[Dict[str, Any]]) -> List[FusedMemory]:
    """Automatically find and fuse similar memories."""
    return await fusion_engine.auto_fuse(memories)

def fusion_report(fusion_id: str) -> Optional[Dict[str, Any]]:
    """Get report on a specific fusion."""
    return fusion_engine.get_fusion_report(fusion_id)