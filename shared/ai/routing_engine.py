#!/usr/bin/env python3
"""
Intelligent Routing Engine for AI Requests

Provides smart routing with load balancing, fallback chains,
and capability-based selection.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import defaultdict
import random

from landmarks import (
    architecture_decision,
    performance_boundary,
    danger_zone,
    state_checkpoint
)

from .unified_registry import UnifiedAIRegistry, AISpecialist, AIStatus
from .socket_client import AISocketClient, StreamChunk

logger = logging.getLogger(__name__)


@dataclass
class RoutingRule:
    """Defines a routing rule for AI selection"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    preferred_ais: List[str]
    required_capabilities: List[str]
    fallback_chain: List[str]
    load_balance: bool = True
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if rule matches the context"""
        return self.condition(context)


@dataclass
class RouteResult:
    """Result of routing decision"""
    specialist: AISpecialist
    rule_used: Optional[str] = None
    fallback_level: int = 0
    reason: str = ""


@architecture_decision(
    title="Rule-Based AI Routing Engine",
    rationale="Enable intelligent routing of AI requests based on context, capabilities, and performance",
    alternatives_considered=["Random selection", "Round-robin", "Static mapping"],
    impacts=["performance", "flexibility", "complexity"],
    decided_by="Casey"
)
@state_checkpoint(
    title="Routing State and Metrics",
    state_type="cache",
    persistence=False,
    consistency_requirements="In-memory only, resets on restart",
    recovery_strategy="Rebuild from registry on startup"
)
class RoutingEngine:
    """
    Intelligent routing engine for AI requests.
    
    Features:
    - Rule-based routing
    - Load balancing
    - Fallback chains
    - Capability matching
    - Performance-based selection
    """
    
    def __init__(self, registry: UnifiedAIRegistry):
        self.registry = registry
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.default_fallback_chain = []
        self._request_counts: Dict[str, int] = defaultdict(int)
        
    def add_rule(self, rule: RoutingRule):
        """Add a routing rule"""
        self.routing_rules[rule.name] = rule
        
    def remove_rule(self, name: str):
        """Remove a routing rule"""
        if name in self.routing_rules:
            del self.routing_rules[name]
            
    def set_default_fallback_chain(self, ai_ids: List[str]):
        """Set default fallback chain for when no rules match"""
        self.default_fallback_chain = ai_ids
        
    @performance_boundary(
        title="Message Routing Decision",
        sla="<50ms routing decision time",
        optimization_notes="Uses cached registry data, applies rules in priority order"
    )
    @danger_zone(
        title="Complex Routing Logic",
        risk_level="medium",
        risks=["Routing loops", "Availability cascades", "Load imbalance"],
        mitigation="Fallback limits, exclude lists, load balancing"
    )
    async def route_message(self,
                           message: str,
                           context: Optional[Dict[str, Any]] = None,
                           preferred_ai: Optional[str] = None,
                           required_capabilities: Optional[List[str]] = None,
                           exclude_ais: Optional[List[str]] = None) -> RouteResult:
        """
        Route a message to the best available AI.
        
        Args:
            message: The message to route
            context: Context for routing decisions
            preferred_ai: Preferred AI if available
            required_capabilities: Required capabilities
            exclude_ais: AIs to exclude from selection
            
        Returns:
            RouteResult with selected specialist
        """
        context = context or {}
        exclude_ais = exclude_ais or []
        
        # Try preferred AI first if specified
        if preferred_ai and preferred_ai not in exclude_ais:
            specialist = await self.registry.get(preferred_ai)
            if specialist and specialist.is_available:
                return RouteResult(
                    specialist=specialist,
                    rule_used=None,
                    fallback_level=0,
                    reason=f"Preferred AI {preferred_ai} is available"
                )
        
        # Check routing rules
        for rule_name, rule in self.routing_rules.items():
            if rule.matches(context):
                result = await self._apply_rule(
                    rule, 
                    exclude_ais,
                    required_capabilities
                )
                if result:
                    result.rule_used = rule_name
                    return result
        
        # No rules matched, use capability-based selection
        if required_capabilities:
            candidates = await self.registry.discover(
                capabilities=required_capabilities,
                status=AIStatus.HEALTHY,
                min_success_rate=0.8
            )
            
            # Filter out excluded AIs
            candidates = [c for c in candidates if c.id not in exclude_ais]
            
            if candidates:
                selected = await self._select_best_candidate(candidates)
                return RouteResult(
                    specialist=selected,
                    rule_used=None,
                    fallback_level=0,
                    reason=f"Selected based on capabilities: {required_capabilities}"
                )
        
        # Try default fallback chain
        for i, ai_id in enumerate(self.default_fallback_chain):
            if ai_id not in exclude_ais:
                specialist = await self.registry.get(ai_id)
                if specialist and specialist.is_available:
                    return RouteResult(
                        specialist=specialist,
                        rule_used=None,
                        fallback_level=i + 1,
                        reason=f"Default fallback chain (level {i + 1})"
                    )
        
        # Last resort: any available AI
        all_available = await self.registry.discover(
            status=AIStatus.HEALTHY,
            min_success_rate=0.5
        )
        
        all_available = [a for a in all_available if a.id not in exclude_ais]
        
        if all_available:
            selected = await self._select_best_candidate(all_available)
            return RouteResult(
                specialist=selected,
                rule_used=None,
                fallback_level=99,
                reason="Last resort: any available AI"
            )
        
        raise ValueError("No suitable AI specialists available for routing")
    
    async def _apply_rule(self,
                         rule: RoutingRule,
                         exclude_ais: List[str],
                         additional_capabilities: Optional[List[str]] = None) -> Optional[RouteResult]:
        """Apply a routing rule"""
        # Combine required capabilities
        required_caps = rule.required_capabilities.copy()
        if additional_capabilities:
            required_caps.extend(additional_capabilities)
        
        # Try preferred AIs from the rule
        for ai_id in rule.preferred_ais:
            if ai_id not in exclude_ais:
                specialist = await self.registry.get(ai_id)
                if specialist and specialist.is_available:
                    # Check capabilities
                    if all(cap in specialist.capabilities for cap in required_caps):
                        return RouteResult(
                            specialist=specialist,
                            fallback_level=0,
                            reason=f"Rule preferred AI: {ai_id}"
                        )
        
        # Try capability-based selection
        if required_caps:
            candidates = await self.registry.discover(
                capabilities=required_caps,
                status=AIStatus.HEALTHY,
                min_success_rate=0.7
            )
            
            candidates = [c for c in candidates if c.id not in exclude_ais]
            
            if candidates:
                if rule.load_balance:
                    selected = await self._select_with_load_balancing(candidates)
                else:
                    selected = await self._select_best_candidate(candidates)
                    
                return RouteResult(
                    specialist=selected,
                    fallback_level=0,
                    reason=f"Rule capability match"
                )
        
        # Try fallback chain
        for i, ai_id in enumerate(rule.fallback_chain):
            if ai_id not in exclude_ais:
                specialist = await self.registry.get(ai_id)
                if specialist and specialist.is_available:
                    return RouteResult(
                        specialist=specialist,
                        fallback_level=i + 1,
                        reason=f"Rule fallback (level {i + 1})"
                    )
        
        return None
    
    async def _select_best_candidate(self, candidates: List[AISpecialist]) -> AISpecialist:
        """Select best candidate based on performance metrics"""
        if not candidates:
            raise ValueError("No candidates to select from")
        
        # Score candidates based on:
        # - Success rate (40%)
        # - Response time (40%)
        # - Recent availability (20%)
        
        scored_candidates = []
        current_time = asyncio.get_event_loop().time()
        
        for candidate in candidates:
            # Success rate score (0-1)
            success_score = candidate.success_rate
            
            # Response time score (inverse, normalized)
            if candidate.avg_response_time > 0:
                # Assume 5s is poor, 0.1s is excellent
                rt_score = max(0, 1 - (candidate.avg_response_time / 5.0))
            else:
                rt_score = 0.5  # No data, neutral score
            
            # Recency score (how recently was it seen)
            time_since_seen = current_time - candidate.last_seen
            if time_since_seen < 60:  # Seen in last minute
                recency_score = 1.0
            elif time_since_seen < 300:  # Seen in last 5 minutes
                recency_score = 0.8
            else:
                recency_score = 0.5
            
            # Combined score
            total_score = (
                success_score * 0.4 +
                rt_score * 0.4 +
                recency_score * 0.2
            )
            
            scored_candidates.append((total_score, candidate))
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        return scored_candidates[0][1]
    
    async def _select_with_load_balancing(self, candidates: List[AISpecialist]) -> AISpecialist:
        """Select candidate with load balancing"""
        if not candidates:
            raise ValueError("No candidates for load balancing")
        
        # Get request counts for candidates
        candidate_loads = [
            (self._request_counts[c.id], c) for c in candidates
        ]
        
        # Sort by load (lowest first)
        candidate_loads.sort(key=lambda x: x[0])
        
        # Select from least loaded candidates (with some randomness)
        # Take the 3 least loaded or all if less than 3
        pool_size = min(3, len(candidate_loads))
        pool = candidate_loads[:pool_size]
        
        # Weighted random selection based on inverse load
        if pool[0][0] == pool[-1][0]:
            # All have same load, pick randomly
            selected = random.choice(pool)[1]
        else:
            # Weight by inverse load
            weights = [1.0 / (load + 1) for load, _ in pool]
            selected = random.choices(
                [c for _, c in pool],
                weights=weights,
                k=1
            )[0]
        
        # Update request count
        self._request_counts[selected.id] += 1
        
        return selected
    
    async def route_to_team(self,
                           message: str,
                           team_size: int = 3,
                           diverse: bool = True,
                           context: Optional[Dict[str, Any]] = None) -> List[RouteResult]:
        """
        Route to a team of AIs for collaborative work.
        
        Args:
            message: The message to route
            team_size: Number of AIs to select
            diverse: Whether to select diverse capabilities
            context: Context for routing
            
        Returns:
            List of RouteResults for the team
        """
        # Get all healthy AIs
        candidates = await self.registry.discover(
            status=AIStatus.HEALTHY,
            min_success_rate=0.7
        )
        
        if len(candidates) < team_size:
            # Not enough healthy AIs, include degraded ones
            degraded = await self.registry.discover(
                status=AIStatus.DEGRADED,
                min_success_rate=0.5
            )
            candidates.extend(degraded)
        
        if not candidates:
            raise ValueError("No AI specialists available for team routing")
        
        selected_team = []
        selected_ids = set()
        
        if diverse:
            # Select AIs with diverse capabilities
            capability_coverage = defaultdict(int)
            
            while len(selected_team) < team_size and candidates:
                # Find AI that adds most new capabilities
                best_score = -1
                best_candidate = None
                
                for candidate in candidates:
                    if candidate.id in selected_ids:
                        continue
                        
                    # Score based on new capabilities added
                    new_caps = sum(
                        1 for cap in candidate.capabilities
                        if capability_coverage[cap] == 0
                    )
                    
                    # Also consider performance
                    perf_score = candidate.success_rate * (1 - candidate.avg_response_time / 5.0)
                    
                    score = new_caps * 0.7 + perf_score * 0.3
                    
                    if score > best_score:
                        best_score = score
                        best_candidate = candidate
                
                if best_candidate:
                    selected_team.append(RouteResult(
                        specialist=best_candidate,
                        reason=f"Team member {len(selected_team) + 1} (diverse selection)"
                    ))
                    selected_ids.add(best_candidate.id)
                    
                    # Update capability coverage
                    for cap in best_candidate.capabilities:
                        capability_coverage[cap] += 1
                else:
                    break
        else:
            # Select best performing AIs
            sorted_candidates = sorted(
                candidates,
                key=lambda c: (c.success_rate, -c.avg_response_time),
                reverse=True
            )
            
            for i, candidate in enumerate(sorted_candidates[:team_size]):
                selected_team.append(RouteResult(
                    specialist=candidate,
                    reason=f"Team member {i + 1} (performance-based selection)"
                ))
        
        return selected_team


# Example routing rules
def create_default_rules() -> List[RoutingRule]:
    """Create default routing rules"""
    
    # Rule for code analysis requests
    code_analysis_rule = RoutingRule(
        name="code_analysis",
        condition=lambda ctx: any(
            keyword in ctx.get("message", "").lower()
            for keyword in ["analyze", "review", "code quality", "static analysis"]
        ),
        preferred_ais=["apollo-ai", "minerva-ai"],
        required_capabilities=["code_analysis", "static_analysis"],
        fallback_chain=["athena-ai", "sophia-ai"],
        load_balance=True
    )
    
    # Rule for documentation requests
    docs_rule = RoutingRule(
        name="documentation",
        condition=lambda ctx: any(
            keyword in ctx.get("message", "").lower()
            for keyword in ["document", "docs", "readme", "explain"]
        ),
        preferred_ais=["hermes-ai", "thoth-ai"],
        required_capabilities=["documentation", "technical_writing"],
        fallback_chain=["athena-ai"],
        load_balance=False
    )
    
    # Rule for memory/context requests
    memory_rule = RoutingRule(
        name="memory_context",
        condition=lambda ctx: any(
            keyword in ctx.get("message", "").lower()
            for keyword in ["remember", "context", "history", "previous"]
        ),
        preferred_ais=["mnemosyne-ai", "engram-ai"],
        required_capabilities=["memory", "context_management"],
        fallback_chain=["athena-ai"],
        load_balance=False
    )
    
    return [code_analysis_rule, docs_rule, memory_rule]