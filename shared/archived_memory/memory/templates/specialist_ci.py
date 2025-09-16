"""
Memory Template for Specialist CIs
Optimized for domain expertise and specialized knowledge management.
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
    memory_aware,
    collective_memory
)


@dataclass
class SpecialistMemoryTemplate:
    """
    Memory template for specialist CIs like Ergon, Prometheus, Sophia, Synthesis.
    
    Features:
    - Deep domain knowledge retention
    - Expertise sharing with collective
    - Technical documentation memory
    - Specialized pattern recognition
    """
    
    # Default configuration
    config = MemoryConfig(
        namespace="specialist",
        injection_style=InjectionStyle.TECHNICAL,
        memory_tiers=[
            MemoryTier.DOMAIN,       # Deep domain expertise
            MemoryTier.ASSOCIATIONS, # Related technical knowledge
            MemoryTier.COLLECTIVE,   # Shared specialist insights
            MemoryTier.RECENT       # Recent context
        ],
        store_inputs=True,
        store_outputs=True,
        inject_context=True,
        context_depth=25,        # More depth for expertise
        relevance_threshold=0.85, # High precision for expertise
        max_context_size=3000,    # Large context for technical details
        enable_collective=True,   # Share expertise
        performance_sla_ms=300    # Allow time for deep retrieval
    )
    
    # Decorator presets
    decorators = {
        'expertise_application': 'apply_expertise',
        'knowledge_retrieval': 'retrieve_knowledge',
        'insight_sharing': 'share_insight',
        'problem_solving': 'solve_problem'
    }
    
    # Memory patterns by specialty
    patterns = {
        'technical_implementation': {
            'tiers': [MemoryTier.DOMAIN, MemoryTier.RECENT],
            'depth': 30,
            'style': InjectionStyle.TECHNICAL
        },
        'creative_generation': {
            'tiers': [MemoryTier.ASSOCIATIONS, MemoryTier.COLLECTIVE],
            'depth': 35,
            'style': InjectionStyle.CREATIVE
        },
        'problem_diagnosis': {
            'tiers': [MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS],
            'depth': 25,
            'style': InjectionStyle.STRUCTURED
        },
        'knowledge_synthesis': {
            'tiers': [MemoryTier.COLLECTIVE, MemoryTier.DOMAIN],
            'depth': 40,
            'style': InjectionStyle.TECHNICAL
        }
    }


# Decorator implementations for specialist CIs

def apply_expertise(func):
    """Decorator for applying specialized expertise."""
    return with_memory(
        namespace="expertise",
        memory_tiers=[MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS],
        injection_style=InjectionStyle.TECHNICAL,
        context_depth=30,
        relevance_threshold=0.9,
        store_inputs=True,
        store_outputs=True
    )(func)


def retrieve_knowledge(func):
    """Decorator for knowledge retrieval without storage."""
    return memory_aware(
        namespace="knowledge",
        context_depth=40,
        relevance_threshold=0.85
    )(func)


def share_insight(func):
    """Decorator for sharing specialist insights."""
    return collective_memory(
        share_with=["specialists"],
        memory_type="expertise",
        visibility="family"
    )(func)


def solve_problem(func):
    """Decorator for problem-solving with full memory."""
    return with_memory(
        namespace="problem_solving",
        memory_tiers=[MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS, MemoryTier.COLLECTIVE],
        injection_style=InjectionStyle.STRUCTURED,
        context_depth=35,
        relevance_threshold=0.8,
        store_inputs=True,
        store_outputs=True,
        enable_collective=True
    )(func)


# Example usage class

class SpecialistCI:
    """Example implementation of a specialist CI with memory."""
    
    def __init__(self, ci_name: str, specialty: str):
        self.ci_name = ci_name
        self.specialty = specialty
        self.template = SpecialistMemoryTemplate()
        self.memory_context = None
    
    @apply_expertise
    async def apply_specialized_knowledge(self, problem: Dict) -> Dict:
        """
        Apply specialized expertise to a problem.
        
        Leverages deep domain knowledge from memory.
        """
        context = self.memory_context
        
        # Retrieve relevant expertise
        expertise = self._retrieve_expertise(context, problem)
        
        # Find similar past solutions
        past_solutions = self._find_past_solutions(context, problem)
        
        # Apply expertise to solve
        solution = await self._apply_expertise_to_problem(
            problem,
            expertise,
            past_solutions
        )
        
        return {
            'problem': problem,
            'solution': solution,
            'confidence': self._calculate_solution_confidence(solution, expertise),
            'references': self._get_references(expertise, past_solutions)
        }
    
    @retrieve_knowledge
    async def lookup_technical_knowledge(self, query: str) -> Dict:
        """
        Look up technical knowledge without storing query.
        
        Pure retrieval for reference purposes.
        """
        context = self.memory_context
        
        # Extract relevant knowledge
        knowledge = self._extract_technical_knowledge(context, query)
        
        # Organize by relevance
        organized = self._organize_by_relevance(knowledge)
        
        return {
            'query': query,
            'knowledge': organized,
            'sources': self._get_knowledge_sources(organized)
        }
    
    @share_insight
    async def contribute_expertise(self, insight: Dict) -> Dict:
        """
        Share specialist insight with the collective.
        
        Automatically shared with other specialists.
        """
        # Validate and enhance insight
        enhanced_insight = self._enhance_insight(insight)
        
        # Add specialist metadata
        specialist_insight = {
            'specialist': self.ci_name,
            'specialty': self.specialty,
            'insight': enhanced_insight,
            'confidence': self._assess_insight_confidence(enhanced_insight),
            'applications': self._identify_applications(enhanced_insight)
        }
        
        # This will be shared automatically
        return specialist_insight
    
    @solve_problem
    async def solve_complex_problem(self, problem: Dict, constraints: Dict) -> Dict:
        """
        Solve complex problem using all memory resources.
        
        Combines domain expertise, associations, and collective knowledge.
        """
        context = self.memory_context
        
        # Analyze problem complexity
        complexity = self._analyze_complexity(problem, constraints)
        
        # Gather all relevant knowledge
        knowledge_base = self._gather_comprehensive_knowledge(context, problem)
        
        # Generate solution approach
        approach = self._generate_approach(problem, constraints, knowledge_base)
        
        # Execute solution
        solution = await self._execute_solution(approach, knowledge_base)
        
        # Validate solution
        validation = self._validate_solution(solution, constraints)
        
        return {
            'problem': problem,
            'complexity': complexity,
            'approach': approach,
            'solution': solution,
            'validation': validation,
            'success': validation['is_valid']
        }
    
    def _retrieve_expertise(self, context, problem) -> Dict:
        """Retrieve relevant expertise from context."""
        if not context or not context.domain:
            return {}
        
        expertise = {}
        for item in context.domain:
            if self._is_relevant_expertise(item, problem):
                expertise[item.get('id', 'unknown')] = item['content']
        
        return expertise
    
    def _find_past_solutions(self, context, problem) -> List[Dict]:
        """Find past solutions to similar problems."""
        if not context or not context.associations:
            return []
        
        solutions = []
        for item in context.associations:
            if 'solution' in item.get('content', {}):
                solutions.append(item['content'])
        
        return solutions
    
    async def _apply_expertise_to_problem(self, problem, expertise, past_solutions) -> Dict:
        """Apply expertise to solve problem."""
        # Placeholder implementation
        return {
            'approach': 'specialized',
            'steps': ['analyze', 'design', 'implement'],
            'used_expertise': len(expertise),
            'referenced_solutions': len(past_solutions)
        }
    
    def _calculate_solution_confidence(self, solution, expertise) -> float:
        """Calculate confidence in solution."""
        # Placeholder implementation
        base_confidence = 0.7
        expertise_boost = min(len(expertise) * 0.05, 0.25)
        return min(base_confidence + expertise_boost, 0.95)
    
    def _get_references(self, expertise, past_solutions) -> List[str]:
        """Get references for solution."""
        # Placeholder implementation
        refs = []
        for exp_id in expertise.keys():
            refs.append(f"expertise:{exp_id}")
        for i, sol in enumerate(past_solutions[:3]):
            refs.append(f"solution:{i}")
        return refs
    
    def _extract_technical_knowledge(self, context, query) -> List[Dict]:
        """Extract technical knowledge relevant to query."""
        # Placeholder implementation
        return []
    
    def _organize_by_relevance(self, knowledge) -> List[Dict]:
        """Organize knowledge by relevance."""
        # Placeholder implementation
        return knowledge
    
    def _get_knowledge_sources(self, knowledge) -> List[str]:
        """Get sources of knowledge."""
        # Placeholder implementation
        return ['domain_expertise', 'technical_docs', 'past_experience']
    
    def _enhance_insight(self, insight) -> Dict:
        """Enhance insight with specialist perspective."""
        # Placeholder implementation
        insight['enhanced'] = True
        insight['specialty_context'] = self.specialty
        return insight
    
    def _assess_insight_confidence(self, insight) -> float:
        """Assess confidence in insight."""
        # Placeholder implementation
        return 0.88
    
    def _identify_applications(self, insight) -> List[str]:
        """Identify applications for insight."""
        # Placeholder implementation
        return ['application1', 'application2']
    
    def _analyze_complexity(self, problem, constraints) -> Dict:
        """Analyze problem complexity."""
        # Placeholder implementation
        return {
            'level': 'high',
            'dimensions': ['technical', 'resource', 'time'],
            'challenges': ['constraint1', 'constraint2']
        }
    
    def _gather_comprehensive_knowledge(self, context, problem) -> Dict:
        """Gather all relevant knowledge."""
        # Placeholder implementation
        return {
            'domain': [],
            'associations': [],
            'collective': []
        }
    
    def _generate_approach(self, problem, constraints, knowledge) -> Dict:
        """Generate solution approach."""
        # Placeholder implementation
        return {
            'strategy': 'divide_and_conquer',
            'phases': ['analysis', 'design', 'implementation', 'validation'],
            'resources': ['knowledge', 'tools', 'time']
        }
    
    async def _execute_solution(self, approach, knowledge) -> Dict:
        """Execute the solution."""
        # Placeholder implementation
        return {
            'implementation': 'completed',
            'results': {'success': True}
        }
    
    def _validate_solution(self, solution, constraints) -> Dict:
        """Validate solution against constraints."""
        # Placeholder implementation
        return {
            'is_valid': True,
            'constraints_met': list(constraints.keys()),
            'quality_score': 0.92
        }
    
    def _is_relevant_expertise(self, item, problem) -> bool:
        """Check if expertise item is relevant to problem."""
        # Placeholder implementation
        return True


# Configuration builder

def create_specialist_config(
    ci_name: str,
    specialty: str,
    **overrides
) -> MemoryConfig:
    """
    Create memory configuration for a specialist CI.
    
    Args:
        ci_name: Name of the CI
        specialty: Area of specialization
        **overrides: Configuration overrides
        
    Returns:
        Configured MemoryConfig
    """
    base_config = SpecialistMemoryTemplate.config
    
    # Adjust based on specialty
    specialty_adjustments = {
        'technical': {'injection_style': InjectionStyle.TECHNICAL, 'context_depth': 35},
        'creative': {'injection_style': InjectionStyle.CREATIVE, 'context_depth': 40},
        'analytical': {'injection_style': InjectionStyle.STRUCTURED, 'context_depth': 30},
        'strategic': {'injection_style': InjectionStyle.STRUCTURED, 'context_depth': 25}
    }
    
    adjustments = specialty_adjustments.get(specialty, {})
    
    # Apply overrides
    config_dict = {
        'namespace': f"{ci_name}_{specialty}",
        'injection_style': adjustments.get('injection_style', base_config.injection_style),
        'memory_tiers': base_config.memory_tiers,
        'store_inputs': base_config.store_inputs,
        'store_outputs': base_config.store_outputs,
        'inject_context': base_config.inject_context,
        'context_depth': adjustments.get('context_depth', base_config.context_depth),
        'relevance_threshold': base_config.relevance_threshold,
        'max_context_size': base_config.max_context_size,
        'enable_collective': base_config.enable_collective,
        'performance_sla_ms': base_config.performance_sla_ms
    }
    
    config_dict.update(overrides)
    
    return MemoryConfig(**config_dict)