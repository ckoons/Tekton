"""
Tekton URL Builder - Centralized URL construction for distributed Tekton stacks.

This module provides a unified way to build URLs for Tekton components that works
across different environments (local, Coder-A/B/C, remote deployments).

Host resolution order:
1. Explicit host argument (highest priority)
2. Component-specific {COMPONENT}_HOST env var
3. Global TEKTON_HOST env var
4. Default to 'localhost'

Examples:
    from shared.urls import tekton_url
    
    # Basic usage
    url = tekton_url("hermes", "/api/mcp/v2")
    
    # With explicit host
    url = tekton_url("athena", "/api/v1/query", host="remote.tekton.io")
    
    # With TEKTON_HOST=coder-b.local set:
    url = tekton_url("hermes", "/api")  # -> http://coder-b.local:6001/api
"""

from typing import Optional
from shared.env import TektonEnviron

# Cache for efficiency
_url_cache = {}


def tekton_url(component: str, path: str = "", host: Optional[str] = None, scheme: str = "http") -> str:
    """
    Build URL for any Tekton component with smart host resolution.
    
    Args:
        component: Component name (e.g., "hermes", "athena", "ui-devtools")
        path: URL path to append (e.g., "/api/mcp/v2")
        host: Explicit host override (optional)
        scheme: URL scheme (default: "http")
    
    Returns:
        Complete URL string
    
    Component names are normalized: hyphens to underscores, then uppercase.
    Examples:
        "hermes" → HERMES_PORT
        "ui-devtools" → UI_DEVTOOLS_PORT
        "ui_devtools" → UI_DEVTOOLS_PORT
    """
    # Normalize component name for environment lookup
    env_component = component.replace("-", "_").upper()
    
    # Host resolution with proper precedence
    if host is None:
        # Check component-specific host first
        component_host = TektonEnviron.get(f"{env_component}_HOST")
        if component_host:
            host = component_host
        else:
            # Fall back to global TEKTON_HOST or localhost
            host = TektonEnviron.get("TEKTON_HOST", "localhost")
    
    # Use component name in cache key to handle different normalizations
    cache_key = f"{component}:{host}:{scheme}"
    
    if cache_key not in _url_cache:
        # Get port from environment
        port = TektonEnviron.get(f"{env_component}_PORT")
        
        if not port:
            # Fallback to component config if available
            try:
                from shared.component_config import SERVICES
                # Handle both normalized and original component names
                port = SERVICES.get(component, {}).get('port') or \
                       SERVICES.get(component.replace("-", "_"), {}).get('port', '8000')
            except ImportError:
                # If component_config doesn't exist, use a sensible default
                port = '8000'
        
        _url_cache[cache_key] = f"{scheme}://{host}:{port}"
    
    return f"{_url_cache[cache_key]}{path}"


def clear_url_cache():
    """
    Clear the URL cache.
    
    Useful when environment variables change or for testing.
    """
    global _url_cache
    _url_cache = {}


# Convenience functions for common patterns
def engram_url(path: str = "", **kwargs) -> str:
    """Shortcut for Engram URLs."""
    return tekton_url("engram", path, **kwargs)


def hermes_url(path: str = "", **kwargs) -> str:
    """Shortcut for Hermes URLs."""
    return tekton_url("hermes", path, **kwargs)


def ergon_url(path: str = "", **kwargs) -> str:
    """Shortcut for Ergon URLs."""
    return tekton_url("ergon", path, **kwargs)


def rhetor_url(path: str = "", **kwargs) -> str:
    """Shortcut for Rhetor URLs."""
    return tekton_url("rhetor", path, **kwargs)


def terma_url(path: str = "", **kwargs) -> str:
    """Shortcut for Terma URLs."""
    return tekton_url("terma", path, **kwargs)


def athena_url(path: str = "", **kwargs) -> str:
    """Shortcut for Athena URLs."""
    return tekton_url("athena", path, **kwargs)


def prometheus_url(path: str = "", **kwargs) -> str:
    """Shortcut for Prometheus URLs."""
    return tekton_url("prometheus", path, **kwargs)


def harmonia_url(path: str = "", **kwargs) -> str:
    """Shortcut for Harmonia URLs."""
    return tekton_url("harmonia", path, **kwargs)


def telos_url(path: str = "", **kwargs) -> str:
    """Shortcut for Telos URLs."""
    return tekton_url("telos", path, **kwargs)


def synthesis_url(path: str = "", **kwargs) -> str:
    """Shortcut for Synthesis URLs."""
    return tekton_url("synthesis", path, **kwargs)


def tekton_core_url(path: str = "", **kwargs) -> str:
    """Shortcut for Tekton Core URLs."""
    return tekton_url("tekton-core", path, **kwargs)


def metis_url(path: str = "", **kwargs) -> str:
    """Shortcut for Metis URLs."""
    return tekton_url("metis", path, **kwargs)


def apollo_url(path: str = "", **kwargs) -> str:
    """Shortcut for Apollo URLs."""
    return tekton_url("apollo", path, **kwargs)


def budget_url(path: str = "", **kwargs) -> str:
    """Shortcut for Budget URLs."""
    return tekton_url("budget", path, **kwargs)


def penia_url(path: str = "", **kwargs) -> str:
    """Shortcut for Penia URLs."""
    return tekton_url("penia", path, **kwargs)


def sophia_url(path: str = "", **kwargs) -> str:
    """Shortcut for Sophia URLs."""
    return tekton_url("sophia", path, **kwargs)


def noesis_url(path: str = "", **kwargs) -> str:
    """Shortcut for Noesis URLs."""
    return tekton_url("noesis", path, **kwargs)


def numa_url(path: str = "", **kwargs) -> str:
    """Shortcut for Numa URLs."""
    return tekton_url("numa", path, **kwargs)


def aish_url(path: str = "", **kwargs) -> str:
    """Shortcut for Aish URLs."""
    return tekton_url("aish", path, **kwargs)


def aish_mcp_url(path: str = "", **kwargs) -> str:
    """Shortcut for Aish MCP URLs."""
    return tekton_url("aish-mcp", path, **kwargs)


def hephaestus_url(path: str = "", **kwargs) -> str:
    """Shortcut for Hephaestus URLs."""
    return tekton_url("hephaestus", path, **kwargs)


def hephaestus_mcp_url(path: str = "", **kwargs) -> str:
    """Shortcut for Hephaestus MCP URLs."""
    return tekton_url("hephaestus-mcp", path, **kwargs)


def db_mcp_url(path: str = "", **kwargs) -> str:
    """Shortcut for Database MCP URLs."""
    return tekton_url("db-mcp", path, **kwargs)