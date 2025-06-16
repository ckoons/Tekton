"""
Standardized log formats for Tekton components.

This module provides consistent logging formats that can be used across
all Tekton components to ensure uniform log output.
"""

# Standard formats available to all components
FORMATS = {
    # Compact format for simple messages (like startup scripts)
    "compact": "%(asctime)s %(message)s",
    
    # Standard format for most components
    "standard": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
    # Detailed format with component tag (like Apollo)
    "detailed": "%(asctime)s [%(name)s] [%(levelname)s] %(module)s: %(message)s",
    
    # Debug format with file location
    "debug": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    
    # Minimal format for clean output
    "minimal": "%(levelname)s: %(message)s",
    
    # JSON-structured format for log aggregation
    "json": '{"timestamp":"%(asctime)s","component":"%(name)s","level":"%(levelname)s","module":"%(module)s","message":"%(message)s"}',
}

# Default format for all Tekton components
DEFAULT_FORMAT = FORMATS["standard"]

# Component-specific format overrides (if needed)
COMPONENT_FORMATS = {
    # Components that need special formatting can be listed here
    # "apollo": FORMATS["detailed"],
    # "hermes": FORMATS["standard"],
}

def get_format_for_component(component_name: str) -> str:
    """
    Get the appropriate log format for a component.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Format string to use for logging
    """
    # Check for component-specific override
    if component_name.lower() in COMPONENT_FORMATS:
        return COMPONENT_FORMATS[component_name.lower()]
    
    # Otherwise use default
    return DEFAULT_FORMAT