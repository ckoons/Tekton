"""
Knowledge Graph Markers
Lightweight decorators that mark functions and classes for knowledge graph construction.
These are metadata-only markers with zero runtime overhead.
"""

import functools
from typing import Any, Callable, Dict, Optional, List


def knowledge_node(
    node_type: str = "general",
    tags: Optional[List[str]] = None,
    importance: float = 0.5
) -> Callable:
    """
    Mark a function/class as a knowledge node.
    
    This is a metadata marker only - no runtime behavior.
    Used to build knowledge graphs and understand code structure.
    
    Args:
        node_type: Type of knowledge node (e.g., "process", "decision", "data")
        tags: Tags for categorization
        importance: Importance score (0-1)
    """
    def decorator(func_or_class):
        # Just add metadata attributes
        func_or_class.__knowledge_node__ = True
        func_or_class.__node_type__ = node_type
        func_or_class.__tags__ = tags or []
        func_or_class.__importance__ = importance
        return func_or_class
    
    return decorator


def context_aware(
    context_type: str = "general",
    requires: Optional[List[str]] = None
) -> Callable:
    """
    Mark a function as requiring context.
    
    This is a metadata marker only - no runtime behavior.
    Indicates what context a function needs to operate effectively.
    
    Args:
        context_type: Type of context needed
        requires: List of required context elements
    """
    def decorator(func):
        func.__context_aware__ = True
        func.__context_type__ = context_type
        func.__requires__ = requires or []
        return func
    
    return decorator


def insight_trigger(
    trigger_type: str = "discovery",
    confidence_threshold: float = 0.7
) -> Callable:
    """
    Mark a function that generates insights.
    
    This is a metadata marker only - no runtime behavior.
    Indicates functions that produce valuable insights.
    
    Args:
        trigger_type: Type of insight trigger
        confidence_threshold: Minimum confidence for insight
    """
    def decorator(func):
        func.__insight_trigger__ = True
        func.__trigger_type__ = trigger_type
        func.__confidence_threshold__ = confidence_threshold
        return func
    
    return decorator


def knowledge_share(
    share_with: Optional[List[str]] = None,
    share_type: str = "general"
) -> Callable:
    """
    Mark a function that shares knowledge.
    
    This is a metadata marker only - no runtime behavior.
    Indicates functions that produce shareable knowledge.
    
    Args:
        share_with: List of CIs to share with
        share_type: Type of knowledge being shared
    """
    def decorator(func):
        func.__knowledge_share__ = True
        func.__share_with__ = share_with or []
        func.__share_type__ = share_type
        return func
    
    return decorator


def memory_point(
    memory_type: str = "event",
    retention: str = "normal"
) -> Callable:
    """
    Mark a point where memory should be created.
    
    This is a metadata marker only - no runtime behavior.
    CIs can use this to identify what to remember.
    
    Args:
        memory_type: Type of memory to create
        retention: How long to retain ("short", "normal", "long")
    """
    def decorator(func):
        func.__memory_point__ = True
        func.__memory_type__ = memory_type
        func.__retention__ = retention
        return func
    
    return decorator


def pattern_detector(
    pattern_type: str = "general",
    min_occurrences: int = 2
) -> Callable:
    """
    Mark a function that detects patterns.
    
    This is a metadata marker only - no runtime behavior.
    Indicates pattern detection capabilities.
    
    Args:
        pattern_type: Type of pattern to detect
        min_occurrences: Minimum occurrences to consider a pattern
    """
    def decorator(func):
        func.__pattern_detector__ = True
        func.__pattern_type__ = pattern_type
        func.__min_occurrences__ = min_occurrences
        return func
    
    return decorator


def decision_point(
    decision_type: str = "tactical",
    factors: Optional[List[str]] = None
) -> Callable:
    """
    Mark a decision point in the code.
    
    This is a metadata marker only - no runtime behavior.
    Helps understand decision flow.
    
    Args:
        decision_type: Type of decision ("tactical", "strategic", "operational")
        factors: Factors considered in decision
    """
    def decorator(func):
        func.__decision_point__ = True
        func.__decision_type__ = decision_type
        func.__factors__ = factors or []
        return func
    
    return decorator


def learning_opportunity(
    learning_type: str = "experience",
    domain: Optional[str] = None
) -> Callable:
    """
    Mark a learning opportunity.
    
    This is a metadata marker only - no runtime behavior.
    Indicates where learning can occur.
    
    Args:
        learning_type: Type of learning
        domain: Domain of learning
    """
    def decorator(func):
        func.__learning_opportunity__ = True
        func.__learning_type__ = learning_type
        func.__domain__ = domain
        return func
    
    return decorator


class KnowledgeGraphBuilder:
    """
    Utility to scan code and build knowledge graph from markers.
    
    This is for analysis only - not used at runtime.
    """
    
    @staticmethod
    def scan_module(module) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan a module for knowledge markers.
        
        Args:
            module: Python module to scan
            
        Returns:
            Dictionary of marked elements by type
        """
        marked_elements = {
            'knowledge_nodes': [],
            'context_aware': [],
            'insight_triggers': [],
            'knowledge_shares': [],
            'memory_points': [],
            'pattern_detectors': [],
            'decision_points': [],
            'learning_opportunities': []
        }
        
        # Scan all attributes in module
        for name in dir(module):
            if name.startswith('_'):
                continue
                
            obj = getattr(module, name)
            
            # Check for markers
            if hasattr(obj, '__knowledge_node__'):
                marked_elements['knowledge_nodes'].append({
                    'name': name,
                    'type': obj.__node_type__,
                    'tags': obj.__tags__,
                    'importance': obj.__importance__
                })
            
            if hasattr(obj, '__context_aware__'):
                marked_elements['context_aware'].append({
                    'name': name,
                    'context_type': obj.__context_type__,
                    'requires': obj.__requires__
                })
            
            if hasattr(obj, '__insight_trigger__'):
                marked_elements['insight_triggers'].append({
                    'name': name,
                    'trigger_type': obj.__trigger_type__,
                    'confidence_threshold': obj.__confidence_threshold__
                })
            
            if hasattr(obj, '__knowledge_share__'):
                marked_elements['knowledge_shares'].append({
                    'name': name,
                    'share_with': obj.__share_with__,
                    'share_type': obj.__share_type__
                })
            
            if hasattr(obj, '__memory_point__'):
                marked_elements['memory_points'].append({
                    'name': name,
                    'memory_type': obj.__memory_type__,
                    'retention': obj.__retention__
                })
            
            if hasattr(obj, '__pattern_detector__'):
                marked_elements['pattern_detectors'].append({
                    'name': name,
                    'pattern_type': obj.__pattern_type__,
                    'min_occurrences': obj.__min_occurrences__
                })
            
            if hasattr(obj, '__decision_point__'):
                marked_elements['decision_points'].append({
                    'name': name,
                    'decision_type': obj.__decision_type__,
                    'factors': obj.__factors__
                })
            
            if hasattr(obj, '__learning_opportunity__'):
                marked_elements['learning_opportunities'].append({
                    'name': name,
                    'learning_type': obj.__learning_type__,
                    'domain': obj.__domain__
                })
        
        return marked_elements


# Example usage (for documentation, not runtime):
"""
@knowledge_node(node_type="analyzer", tags=["data", "metrics"], importance=0.8)
class DataAnalyzer:
    
    @context_aware(context_type="data", requires=["dataset", "parameters"])
    def analyze(self, data):
        # Function needs data context
        pass
    
    @insight_trigger(trigger_type="anomaly", confidence_threshold=0.9)
    def detect_anomaly(self, data):
        # This function generates insights
        pass
    
    @memory_point(memory_type="analysis_result", retention="long")
    def store_results(self, results):
        # This is where we should remember something
        pass
    
    @pattern_detector(pattern_type="trend", min_occurrences=3)
    def find_trends(self, timeseries):
        # Detects patterns
        pass
    
    @decision_point(decision_type="strategic", factors=["risk", "reward"])
    def make_recommendation(self, analysis):
        # Decision point
        pass
    
    @learning_opportunity(learning_type="pattern", domain="analytics")
    def learn_from_feedback(self, feedback):
        # Learning opportunity
        pass
    
    @knowledge_share(share_with=["apollo", "athena"], share_type="insights")
    def share_findings(self, findings):
        # Shares knowledge with other CIs
        pass
"""