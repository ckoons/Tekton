"""
Memory Template for Analytical CIs
Optimized for data analysis, pattern recognition, and insight generation.
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
    memory_trigger
)


@dataclass
class AnalyticalMemoryTemplate:
    """
    Memory template for analytical CIs like Athena, Metis, Noesis.
    
    Features:
    - Domain knowledge retrieval
    - Pattern history tracking
    - Analysis result caching
    - Structured data injection
    """
    
    # Default configuration
    config = MemoryConfig(
        namespace="analytical",
        injection_style=InjectionStyle.STRUCTURED,
        memory_tiers=[
            MemoryTier.DOMAIN,       # Domain-specific knowledge
            MemoryTier.ASSOCIATIONS, # Related analyses
            MemoryTier.RECENT       # Recent analysis context
        ],
        store_inputs=True,
        store_outputs=True,
        inject_context=True,
        context_depth=15,
        relevance_threshold=0.8,  # Higher threshold for precision
        max_context_size=2500,    # More space for data
        enable_collective=True,   # Share insights
        performance_sla_ms=250    # Allow more time for complex retrieval
    )
    
    # Decorator presets
    decorators = {
        'analysis_handler': 'analytical_process',
        'pattern_detection': 'pattern_memory',
        'insight_generation': 'insight_trigger',
        'data_preprocessing': 'data_context'
    }
    
    # Memory patterns
    patterns = {
        'data_analysis': {
            'tiers': [MemoryTier.DOMAIN, MemoryTier.RECENT],
            'depth': 20,
            'style': InjectionStyle.TECHNICAL
        },
        'pattern_recognition': {
            'tiers': [MemoryTier.ASSOCIATIONS, MemoryTier.DOMAIN],
            'depth': 30,
            'style': InjectionStyle.STRUCTURED
        },
        'hypothesis_testing': {
            'tiers': [MemoryTier.DOMAIN],
            'depth': 15,
            'style': InjectionStyle.TECHNICAL
        },
        'trend_analysis': {
            'tiers': [MemoryTier.RECENT, MemoryTier.ASSOCIATIONS],
            'depth': 25,
            'style': InjectionStyle.STRUCTURED
        }
    }


# Decorator implementations for analytical CIs

def analytical_process(func):
    """Decorator for analytical processing with full memory."""
    return with_memory(
        namespace="analysis",
        memory_tiers=[MemoryTier.DOMAIN, MemoryTier.ASSOCIATIONS, MemoryTier.RECENT],
        injection_style=InjectionStyle.STRUCTURED,
        context_depth=20,
        relevance_threshold=0.8,
        store_inputs=True,
        store_outputs=True
    )(func)


def pattern_memory(func):
    """Decorator for pattern detection with associative memory."""
    return with_memory(
        namespace="patterns",
        memory_tiers=[MemoryTier.ASSOCIATIONS, MemoryTier.DOMAIN],
        injection_style=InjectionStyle.TECHNICAL,
        context_depth=30,
        relevance_threshold=0.7,
        store_outputs=True
    )(func)


def insight_trigger(func):
    """Decorator for insight generation with consolidation."""
    return memory_trigger(
        on_event="insight_generated",
        consolidation_type="immediate",
        reflection_depth="deep",
        auto_consolidate=True
    )(func)


def data_context(func):
    """Decorator for data preprocessing with context."""
    return memory_aware(
        namespace="data",
        context_depth=10,
        relevance_threshold=0.9
    )(func)


# Example usage class

class AnalyticalCI:
    """Example implementation of an analytical CI with memory."""
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.template = AnalyticalMemoryTemplate()
        self.memory_context = None
    
    @analytical_process
    async def analyze_data(self, data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """
        Perform data analysis with automatic memory.
        
        Retrieves relevant domain knowledge and past analyses.
        """
        context = self.memory_context
        
        # Use domain knowledge for analysis
        domain_knowledge = self._extract_domain_knowledge(context)
        
        # Check for similar past analyses
        similar_analyses = self._find_similar_analyses(context, data)
        
        # Perform analysis
        results = await self._perform_analysis(
            data,
            analysis_type,
            domain_knowledge,
            similar_analyses
        )
        
        return results
    
    @pattern_memory
    async def detect_patterns(self, dataset: List[Dict]) -> List[Dict]:
        """
        Detect patterns in dataset with associative memory.
        
        Automatically stores detected patterns for future reference.
        """
        context = self.memory_context
        
        # Get related patterns from memory
        known_patterns = self._get_known_patterns(context)
        
        # Detect new patterns
        patterns = []
        for data_point in dataset:
            pattern = self._analyze_pattern(data_point, known_patterns)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    @insight_trigger
    async def generate_insight(self, analysis_results: Dict) -> Dict:
        """
        Generate insights with automatic consolidation.
        
        Triggers memory consolidation for important insights.
        """
        # Extract key findings
        findings = self._extract_findings(analysis_results)
        
        # Generate insight
        insight = {
            'type': 'analytical_insight',
            'findings': findings,
            'confidence': self._calculate_confidence(findings),
            'implications': self._derive_implications(findings)
        }
        
        # This will trigger consolidation automatically
        return insight
    
    @data_context
    async def preprocess_data(self, raw_data: Any) -> Dict:
        """
        Preprocess data with relevant context.
        
        Uses memory context without storing preprocessing steps.
        """
        context = self.memory_context
        
        # Get preprocessing hints from memory
        preprocessing_hints = self._get_preprocessing_hints(context)
        
        # Apply preprocessing
        processed = self._apply_preprocessing(raw_data, preprocessing_hints)
        
        return processed
    
    def _extract_domain_knowledge(self, context) -> Dict:
        """Extract relevant domain knowledge from context."""
        if not context:
            return {}
        
        knowledge = {}
        for item in context.domain:
            if 'content' in item:
                knowledge.update(item['content'])
        
        return knowledge
    
    def _find_similar_analyses(self, context, data) -> List:
        """Find similar past analyses."""
        if not context:
            return []
        
        similar = []
        for item in context.associations:
            if self._is_similar(item, data):
                similar.append(item)
        
        return similar
    
    async def _perform_analysis(self, data, analysis_type, knowledge, similar) -> Dict:
        """Perform the actual analysis."""
        # Placeholder for actual analysis
        return {
            'type': analysis_type,
            'results': {'placeholder': 'analysis'},
            'used_knowledge': len(knowledge),
            'similar_analyses': len(similar)
        }
    
    def _get_known_patterns(self, context) -> List:
        """Get known patterns from memory."""
        # Placeholder implementation
        return []
    
    def _analyze_pattern(self, data_point, known_patterns) -> Optional[Dict]:
        """Analyze a single data point for patterns."""
        # Placeholder implementation
        return None
    
    def _extract_findings(self, results) -> List:
        """Extract key findings from results."""
        # Placeholder implementation
        return ['finding1', 'finding2']
    
    def _calculate_confidence(self, findings) -> float:
        """Calculate confidence in findings."""
        # Placeholder implementation
        return 0.85
    
    def _derive_implications(self, findings) -> List:
        """Derive implications from findings."""
        # Placeholder implementation
        return ['implication1', 'implication2']
    
    def _get_preprocessing_hints(self, context) -> Dict:
        """Get preprocessing hints from context."""
        # Placeholder implementation
        return {}
    
    def _apply_preprocessing(self, raw_data, hints) -> Dict:
        """Apply preprocessing to raw data."""
        # Placeholder implementation
        return {'processed': raw_data}
    
    def _is_similar(self, item, data) -> bool:
        """Check if an analysis is similar."""
        # Placeholder implementation
        return False


# Configuration builder

def create_analytical_config(
    ci_name: str,
    **overrides
) -> MemoryConfig:
    """
    Create memory configuration for an analytical CI.
    
    Args:
        ci_name: Name of the CI
        **overrides: Configuration overrides
        
    Returns:
        Configured MemoryConfig
    """
    base_config = AnalyticalMemoryTemplate.config
    
    # Apply overrides
    config_dict = {
        'namespace': ci_name,
        'injection_style': base_config.injection_style,
        'memory_tiers': base_config.memory_tiers,
        'store_inputs': base_config.store_inputs,
        'store_outputs': base_config.store_outputs,
        'inject_context': base_config.inject_context,
        'context_depth': base_config.context_depth,
        'relevance_threshold': base_config.relevance_threshold,
        'max_context_size': base_config.max_context_size,
        'enable_collective': base_config.enable_collective,
        'performance_sla_ms': base_config.performance_sla_ms
    }
    
    config_dict.update(overrides)
    
    return MemoryConfig(**config_dict)