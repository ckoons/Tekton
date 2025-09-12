"""
Landmark decorators for the Engram ESR system.

Provides fallback no-op decorators when landmarks module is not available.
"""

try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        ci_orchestrated,
        message_buffer,
        fuzzy_match,
        ci_collaboration,
        danger_zone,
        state_checkpoint,
        memory_landmark,
        decision_landmark,
        insight_landmark,
        error_landmark
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def ci_orchestrated(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def message_buffer(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def fuzzy_match(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def ci_collaboration(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def memory_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def decision_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def insight_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def error_landmark(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

__all__ = [
    'architecture_decision',
    'api_contract',
    'integration_point',
    'performance_boundary',
    'ci_orchestrated',
    'message_buffer',
    'fuzzy_match',
    'ci_collaboration',
    'danger_zone',
    'state_checkpoint',
    'memory_landmark',
    'decision_landmark',
    'insight_landmark',
    'error_landmark'
]