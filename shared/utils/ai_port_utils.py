"""
AI Port Utilities for Tekton Platform

Simple utilities for calculating AI specialist ports based on component ports.
Uses the formula: AI port = (component_port - 8000) + 45000
"""

def get_ai_port(component_port: int) -> int:
    """
    Calculate AI specialist port from component port.
    
    Formula: AI port = (component_port - 8000) + 45000
    
    Examples:
        Engram (8000) -> 45000
        Hermes (8001) -> 45001
        Rhetor (8003) -> 45003
        Apollo (8012) -> 45012
        
    Args:
        component_port: The main component port (8000-8080 range)
        
    Returns:
        The calculated AI port (45000+ range)
    """
    return (component_port - 8000) + 45000


def get_component_port_from_ai(ai_port: int) -> int:
    """
    Calculate component port from AI specialist port (reverse formula).
    
    Formula: component_port = (ai_port - 45000) + 8000
    
    Args:
        ai_port: The AI specialist port (45000+ range)
        
    Returns:
        The calculated component port (8000-8080 range)
    """
    return (ai_port - 45000) + 8000


# Fixed port mappings for reference (derived from tekton_components.yaml)
AI_PORT_MAP = {
    'engram-ai': 45000,      # 8000 -> 45000
    'hermes-ai': 45001,      # 8001 -> 45001
    'ergon-ai': 45002,       # 8002 -> 45002
    'rhetor-ai': 45003,      # 8003 -> 45003
    'terma-ai': 45004,       # 8004 -> 45004
    'athena-ai': 45005,      # 8005 -> 45005
    'prometheus-ai': 45006,  # 8006 -> 45006
    'harmonia-ai': 45007,    # 8007 -> 45007
    'telos-ai': 45008,       # 8008 -> 45008
    'synthesis-ai': 45009,   # 8009 -> 45009
    'tekton_core-ai': 45010, # 8010 -> 45010
    'metis-ai': 45011,       # 8011 -> 45011
    'apollo-ai': 45012,      # 8012 -> 45012
    'penia-ai': 45013,       # 8013 -> 45013
    'sophia-ai': 45014,      # 8014 -> 45014
    'noesis-ai': 45015,      # 8015 -> 45015
    'numa-ai': 45016,        # 8016 -> 45016
    'hephaestus-ai': 45080,  # 8080 -> 45080
}


def get_ai_port_by_name(ai_name: str) -> int:
    """
    Get AI port by AI name (e.g., 'apollo-ai').
    
    Args:
        ai_name: AI specialist name with -ai suffix
        
    Returns:
        AI port number
        
    Raises:
        ValueError: If AI name not found
    """
    if ai_name not in AI_PORT_MAP:
        raise ValueError(f"Unknown AI specialist: {ai_name}")
    return AI_PORT_MAP[ai_name]