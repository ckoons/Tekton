"""
AI Port Utilities for Tekton Platform

Simple utilities for calculating CI specialist ports based on component ports.
Uses configurable port bases from environment variables.
"""
import os
from shared.env import TektonEnviron

# Get port bases from environment - NO DEFAULTS! Each Tekton has its own .env.local
# Main Tekton might be 8000/45000, Coder-A might be 8100/44000, Coder-B 8200/43000, etc.
_port_base = TektonEnviron.get('TEKTON_PORT_BASE')
_ai_port_base = TektonEnviron.get('TEKTON_AI_PORT_BASE')

if not _port_base or not _ai_port_base:
    raise ValueError(
        f"TEKTON_PORT_BASE and TEKTON_AI_PORT_BASE must be set in {os.environ.get('TEKTON_ROOT', '.')}/.env.local\n"
        "Each Tekton instance has unique port ranges. No defaults are allowed."
    )

TEKTON_PORT_BASE = int(_port_base)
TEKTON_AI_PORT_BASE = int(_ai_port_base)


def get_ai_port(component_port: int) -> int:
    """
    Calculate CI specialist port from component port.
    
    Formula: CI port = TEKTON_AI_PORT_BASE + (component_port - TEKTON_PORT_BASE)
    
    Examples with defaults (TEKTON_PORT_BASE=8100, TEKTON_AI_PORT_BASE=44000):
        Engram (8100) -> 44000
        Hermes (8101) -> 44001
        Rhetor (8103) -> 44003
        Apollo (8112) -> 44012
        
    Args:
        component_port: The main component port
        
    Returns:
        The calculated CI port
    """
    return TEKTON_AI_PORT_BASE + (component_port - TEKTON_PORT_BASE)


def get_component_port_from_ai(ai_port: int) -> int:
    """
    Calculate component port from CI specialist port (reverse formula).
    
    Formula: component_port = TEKTON_PORT_BASE + (ai_port - TEKTON_AI_PORT_BASE)
    
    Args:
        ai_port: The CI specialist port
        
    Returns:
        The calculated component port
    """
    return TEKTON_PORT_BASE + (ai_port - TEKTON_AI_PORT_BASE)


# Component ports (will be read from env, but defaults here for reference)
COMPONENT_PORTS = {
    'engram': int(TektonEnviron.get('ENGRAM_PORT', str(TEKTON_PORT_BASE + 0))),
    'hermes': int(TektonEnviron.get('HERMES_PORT', str(TEKTON_PORT_BASE + 1))),
    'ergon': int(TektonEnviron.get('ERGON_PORT', str(TEKTON_PORT_BASE + 2))),
    'rhetor': int(TektonEnviron.get('RHETOR_PORT', str(TEKTON_PORT_BASE + 3))),
    'terma': int(TektonEnviron.get('TERMA_PORT', str(TEKTON_PORT_BASE + 4))),
    'athena': int(TektonEnviron.get('ATHENA_PORT', str(TEKTON_PORT_BASE + 5))),
    'prometheus': int(TektonEnviron.get('PROMETHEUS_PORT', str(TEKTON_PORT_BASE + 6))),
    'harmonia': int(TektonEnviron.get('HARMONIA_PORT', str(TEKTON_PORT_BASE + 7))),
    'telos': int(TektonEnviron.get('TELOS_PORT', str(TEKTON_PORT_BASE + 8))),
    'synthesis': int(TektonEnviron.get('SYNTHESIS_PORT', str(TEKTON_PORT_BASE + 9))),
    'tekton_core': int(TektonEnviron.get('TEKTON_CORE_PORT', str(TEKTON_PORT_BASE + 10))),
    'metis': int(TektonEnviron.get('METIS_PORT', str(TEKTON_PORT_BASE + 11))),
    'apollo': int(TektonEnviron.get('APOLLO_PORT', str(TEKTON_PORT_BASE + 12))),
    'penia': int(TektonEnviron.get('PENIA_PORT', str(TEKTON_PORT_BASE + 13))),
    'sophia': int(TektonEnviron.get('SOPHIA_PORT', str(TEKTON_PORT_BASE + 14))),
    'noesis': int(TektonEnviron.get('NOESIS_PORT', str(TEKTON_PORT_BASE + 15))),
    'numa': int(TektonEnviron.get('NUMA_PORT', str(TEKTON_PORT_BASE + 16))),
    'hephaestus': int(TektonEnviron.get('HEPHAESTUS_PORT', str(TEKTON_PORT_BASE + 80))),
}

# Dynamic port mappings calculated from component ports
AI_PORT_MAP = {
    f'{name}-ci': get_ai_port(port) 
    for name, port in COMPONENT_PORTS.items()
}


def get_ai_port_by_name(ai_name: str) -> int:
    """
    Get CI port by CI name (e.g., 'apollo-ci').
    
    Args:
        ai_name: CI specialist name with -ci suffix
        
    Returns:
        CI port number
        
    Raises:
        ValueError: If CI name not found
    """
    if ai_name not in AI_PORT_MAP:
        raise ValueError(f"Unknown CI specialist: {ai_name}")
    return AI_PORT_MAP[ai_name]
