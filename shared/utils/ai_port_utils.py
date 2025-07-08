"""
AI Port Utilities for Tekton Platform

Simple utilities for calculating AI specialist ports based on component ports.
Uses configurable port bases from environment variables.
"""
import os

# Get port bases from environment, with defaults for backwards compatibility
TEKTON_PORT_BASE = int(os.environ.get('TEKTON_PORT_BASE', '8000'))
TEKTON_AI_PORT_BASE = int(os.environ.get('TEKTON_AI_PORT_BASE', '45000'))


def get_ai_port(component_port: int) -> int:
    """
    Calculate AI specialist port from component port.
    
    Formula: AI port = TEKTON_AI_PORT_BASE + (component_port - TEKTON_PORT_BASE)
    
    Examples with defaults (TEKTON_PORT_BASE=8000, TEKTON_AI_PORT_BASE=45000):
        Engram (8000) -> 45000
        Hermes (8001) -> 45001
        Rhetor (8003) -> 45003
        Apollo (8012) -> 45012
        
    Args:
        component_port: The main component port
        
    Returns:
        The calculated AI port
    """
    return TEKTON_AI_PORT_BASE + (component_port - TEKTON_PORT_BASE)


def get_component_port_from_ai(ai_port: int) -> int:
    """
    Calculate component port from AI specialist port (reverse formula).
    
    Formula: component_port = TEKTON_PORT_BASE + (ai_port - TEKTON_AI_PORT_BASE)
    
    Args:
        ai_port: The AI specialist port
        
    Returns:
        The calculated component port
    """
    return TEKTON_PORT_BASE + (ai_port - TEKTON_AI_PORT_BASE)


# Component ports (will be read from env, but defaults here for reference)
COMPONENT_PORTS = {
    'engram': int(os.environ.get('ENGRAM_PORT', str(TEKTON_PORT_BASE + 0))),
    'hermes': int(os.environ.get('HERMES_PORT', str(TEKTON_PORT_BASE + 1))),
    'ergon': int(os.environ.get('ERGON_PORT', str(TEKTON_PORT_BASE + 2))),
    'rhetor': int(os.environ.get('RHETOR_PORT', str(TEKTON_PORT_BASE + 3))),
    'terma': int(os.environ.get('TERMA_PORT', str(TEKTON_PORT_BASE + 4))),
    'athena': int(os.environ.get('ATHENA_PORT', str(TEKTON_PORT_BASE + 5))),
    'prometheus': int(os.environ.get('PROMETHEUS_PORT', str(TEKTON_PORT_BASE + 6))),
    'harmonia': int(os.environ.get('HARMONIA_PORT', str(TEKTON_PORT_BASE + 7))),
    'telos': int(os.environ.get('TELOS_PORT', str(TEKTON_PORT_BASE + 8))),
    'synthesis': int(os.environ.get('SYNTHESIS_PORT', str(TEKTON_PORT_BASE + 9))),
    'tekton_core': int(os.environ.get('TEKTON_CORE_PORT', str(TEKTON_PORT_BASE + 10))),
    'metis': int(os.environ.get('METIS_PORT', str(TEKTON_PORT_BASE + 11))),
    'apollo': int(os.environ.get('APOLLO_PORT', str(TEKTON_PORT_BASE + 12))),
    'penia': int(os.environ.get('PENIA_PORT', str(TEKTON_PORT_BASE + 13))),
    'sophia': int(os.environ.get('SOPHIA_PORT', str(TEKTON_PORT_BASE + 14))),
    'noesis': int(os.environ.get('NOESIS_PORT', str(TEKTON_PORT_BASE + 15))),
    'numa': int(os.environ.get('NUMA_PORT', str(TEKTON_PORT_BASE + 16))),
    'hephaestus': int(os.environ.get('HEPHAESTUS_PORT', str(TEKTON_PORT_BASE + 80))),
}

# Dynamic port mappings calculated from component ports
AI_PORT_MAP = {
    f'{name}-ai': get_ai_port(port) 
    for name, port in COMPONENT_PORTS.items()
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