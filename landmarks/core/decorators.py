"""
Landmark decorators for marking code with persistent memory
"""

import functools
import inspect
import traceback
from typing import Callable, Any, Optional, List, Dict
from pathlib import Path

from .landmark import (
    Landmark, 
    ArchitectureDecision,
    PerformanceBoundary,
    APIContract,
    DangerZone,
    IntegrationPoint,
    StateCheckpoint
)
from .registry import LandmarkRegistry


def _get_caller_info():
    """Get file path and line number of the decorated function"""
    # Get the stack, excluding this function
    stack = traceback.extract_stack()
    
    # Find the first frame outside the landmarks module
    for frame in reversed(stack):
        if 'landmarks' not in frame.filename and 'decorators.py' not in frame.filename:
            return frame.filename, frame.lineno
    
    # Fallback
    return 'unknown', 0


def landmark(type: str, title: str, description: str = "", **metadata):
    """
    Generic landmark decorator for marking functions or classes.
    
    Args:
        type: Type of landmark (e.g., 'architecture_decision', 'performance_boundary')
        title: Short title for the landmark
        description: Longer description (if not provided, uses docstring)
        **metadata: Additional metadata to store with the landmark
    
    Example:
        @landmark(type="architecture_decision", title="Use AsyncIO", 
                 rationale="Need to handle 1000+ concurrent connections")
        async def handle_connection():
            pass
    """
    def decorator(obj: Callable) -> Callable:
        # Get source information
        try:
            source_file = inspect.getsourcefile(obj)
            source_lines = inspect.getsourcelines(obj)
            line_number = source_lines[1]
        except:
            # Fallback for cases where inspect fails
            source_file, line_number = _get_caller_info()
        
        # Use docstring as description if not provided
        if not description and hasattr(obj, '__doc__'):
            desc = obj.__doc__ or ""
        else:
            desc = description
        
        # Create the landmark
        lm = Landmark.create(
            type=type,
            title=title,
            description=desc.strip(),
            file_path=str(source_file),
            line_number=line_number,
            author=metadata.pop('author', 'system'),
            metadata=metadata
        )
        
        # Register it
        LandmarkRegistry.register(lm)
        
        # For classes, just attach and return
        if inspect.isclass(obj):
            obj._landmark = lm
            return obj
        
        # For functions, create wrapper
        @functools.wraps(obj)
        def wrapper(*args, **kwargs):
            return obj(*args, **kwargs)
        
        # Attach landmark to function for runtime access
        wrapper._landmark = lm
        
        # For async functions
        if inspect.iscoroutinefunction(obj):
            @functools.wraps(obj)
            async def async_wrapper(*args, **kwargs):
                return await obj(*args, **kwargs)
            async_wrapper._landmark = lm
            return async_wrapper
            
        return wrapper
    
    return decorator


def architecture_decision(title: str, 
                        rationale: str,
                        alternatives_considered: Optional[List[str]] = None,
                        impacts: Optional[List[str]] = None,
                        decided_by: str = "team",
                        **kwargs):
    """
    Mark an architectural decision in code.
    
    Args:
        title: Decision title
        rationale: Why this decision was made
        alternatives_considered: Other options that were evaluated
        impacts: Areas of the system affected by this decision
        decided_by: Who made the decision
        **kwargs: Additional metadata
    
    Example:
        @architecture_decision(
            title="Use WebSockets for real-time updates",
            rationale="Need <100ms latency for UI responsiveness",
            alternatives_considered=["REST polling", "Server-sent events"],
            impacts=["scalability", "complexity"],
            decided_by="Casey"
        )
        async def setup_websocket_handler():
            pass
    """
    metadata = {
        'rationale': rationale,
        'alternatives_considered': alternatives_considered or [],
        'impacts': impacts or [],
        'decided_by': decided_by,
        **kwargs
    }
    
    return landmark(
        type="architecture_decision",
        title=title,
        **metadata
    )


def performance_boundary(title: str,
                       sla: str,
                       optimization_notes: str = "",
                       metrics: Optional[Dict[str, Any]] = None,
                       **kwargs):
    """
    Mark performance-critical code sections.
    
    Args:
        title: Boundary title
        sla: Service Level Agreement (e.g., "<50ms response time")
        optimization_notes: Notes about optimizations applied
        metrics: Performance metrics and benchmarks
        **kwargs: Additional metadata
    
    Example:
        @performance_boundary(
            title="Message processing pipeline",
            sla="<50ms per message",
            optimization_notes="Uses batching and async I/O",
            metrics={"throughput": "10k msg/sec", "p99_latency": "45ms"}
        )
        async def process_messages(messages):
            pass
    """
    metadata = {
        'sla': sla,
        'optimization_notes': optimization_notes,
        'metrics': metrics or {},
        **kwargs
    }
    
    return landmark(
        type="performance_boundary",
        title=title,
        **metadata
    )


def api_contract(title: str,
                endpoint: str,
                method: str = "GET",
                request_schema: Optional[Dict] = None,
                response_schema: Optional[Dict] = None,
                auth_required: bool = False,
                **kwargs):
    """
    Mark API endpoints and their contracts.
    
    Args:
        title: Contract title
        endpoint: API endpoint path
        method: HTTP method
        request_schema: Expected request format
        response_schema: Response format
        auth_required: Whether authentication is required
        **kwargs: Additional metadata
    
    Example:
        @api_contract(
            title="Component Registration",
            endpoint="/api/register",
            method="POST",
            request_schema={"name": "string", "capabilities": ["string"]},
            response_schema={"id": "string", "status": "string"},
            auth_required=True
        )
        async def register_component(request):
            pass
    """
    metadata = {
        'endpoint': endpoint,
        'method': method,
        'request_schema': request_schema or {},
        'response_schema': response_schema or {},
        'auth_required': auth_required,
        **kwargs
    }
    
    return landmark(
        type="api_contract",
        title=title,
        **metadata
    )


def danger_zone(title: str,
               risk_level: str = "medium",
               risks: Optional[List[str]] = None,
               mitigation: str = "",
               review_required: bool = True,
               **kwargs):
    """
    Mark complex or risky code sections.
    
    Args:
        title: Description of the danger
        risk_level: "low", "medium", or "high"
        risks: List of specific risks
        mitigation: How risks are mitigated
        review_required: Whether code review is required for changes
        **kwargs: Additional metadata
    
    Example:
        @danger_zone(
            title="Concurrent state modification",
            risk_level="high",
            risks=["race conditions", "deadlock potential"],
            mitigation="Using locks and careful ordering",
            review_required=True
        )
        async def modify_shared_state():
            pass
    """
    metadata = {
        'risk_level': risk_level,
        'risks': risks or [],
        'mitigation': mitigation,
        'review_required': review_required,
        **kwargs
    }
    
    return landmark(
        type="danger_zone",
        title=title,
        **metadata
    )


def integration_point(title: str,
                     target_component: str,
                     protocol: str,
                     data_flow: str = "",
                     **kwargs):
    """
    Mark where components integrate.
    
    Args:
        title: Integration point title
        target_component: Component being integrated with
        protocol: Communication protocol (e.g., "WebSocket", "REST", "MCP")
        data_flow: Description of data flow
        **kwargs: Additional metadata
    
    Example:
        @integration_point(
            title="Hermes message subscription",
            target_component="Hermes",
            protocol="WebSocket",
            data_flow="Subscribe to component events"
        )
        async def subscribe_to_hermes():
            pass
    """
    metadata = {
        'target_component': target_component,
        'protocol': protocol,
        'data_flow': data_flow,
        **kwargs
    }
    
    return landmark(
        type="integration_point", 
        title=title,
        **metadata
    )


def state_checkpoint(title: str,
                    state_type: str,
                    persistence: bool = False,
                    consistency_requirements: str = "",
                    recovery_strategy: str = "",
                    **kwargs):
    """
    Mark important state management points.
    
    Args:
        title: Checkpoint title
        state_type: Type of state (e.g., "singleton", "cache", "session")
        persistence: Whether state is persisted
        consistency_requirements: Consistency guarantees
        recovery_strategy: How state is recovered after failure
        **kwargs: Additional metadata
    
    Example:
        @state_checkpoint(
            title="Component registry singleton",
            state_type="singleton",
            persistence=True,
            consistency_requirements="Eventually consistent",
            recovery_strategy="Reload from disk on restart"
        )
        def get_instance():
            pass
    """
    metadata = {
        'state_type': state_type,
        'persistence': persistence,
        'consistency_requirements': consistency_requirements,
        'recovery_strategy': recovery_strategy,
        **kwargs
    }
    
    return landmark(
        type="state_checkpoint",
        title=title,
        **metadata
    )