"""
Component Discovery Module

This module provides functions for discovering components in the Tekton ecosystem.
"""

import os
import logging
from typing import Dict, List, Any, Optional

from .exceptions import ComponentNotFoundError, ComponentUnavailableError

# Configure logger
logger = logging.getLogger(__name__)


async def discover_component(
    component_id: str,
    hermes_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Discover a component in the Tekton ecosystem.
    
    Args:
        component_id: ID of the component to discover
        hermes_url: URL of the Hermes API
        
    Returns:
        Component information
        
    Raises:
        ComponentNotFoundError: If the component is not found
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    from shared.urls import hermes_url as get_hermes_url
    hermes_url = hermes_url or get_hermes_url("/api")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{hermes_url}/registry/component/{component_id}"
            ) as response:
                if response.status == 404:
                    raise ComponentNotFoundError(f"Component {component_id} not found")
                elif response.status != 200:
                    error_text = await response.text()
                    raise ComponentUnavailableError(
                        f"Failed to discover component: {response.status} {error_text}"
                    )
                
                return await response.json()
    except (ConnectionError, TimeoutError) as e:
        raise ComponentUnavailableError(f"Failed to connect to Hermes API: {e}")
    except ImportError:
        raise ImportError("aiohttp is required for discovering components")


async def discover_components_by_type(
    component_type: str,
    hermes_url: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Discover components of a specific type in the Tekton ecosystem.
    
    Args:
        component_type: Type of components to discover
        hermes_url: URL of the Hermes API
        
    Returns:
        List of component information
        
    Raises:
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    from shared.urls import hermes_url as get_hermes_url
    hermes_url = hermes_url or get_hermes_url("/api")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{hermes_url}/registry/components",
                params={"type": component_type}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ComponentUnavailableError(
                        f"Failed to discover components: {response.status} {error_text}"
                    )
                
                return await response.json()
    except (ConnectionError, TimeoutError) as e:
        raise ComponentUnavailableError(f"Failed to connect to Hermes API: {e}")
    except ImportError:
        raise ImportError("aiohttp is required for discovering components")


async def discover_components_by_capability(
    capability: str,
    hermes_url: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Discover components that have a specific capability in the Tekton ecosystem.
    
    Args:
        capability: Capability that components must have
        hermes_url: URL of the Hermes API
        
    Returns:
        List of component information
        
    Raises:
        ComponentUnavailableError: If the Hermes API is unavailable
    """
    from shared.urls import hermes_url as get_hermes_url
    hermes_url = hermes_url or get_hermes_url("/api")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{hermes_url}/registry/components",
                params={"capability": capability}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ComponentUnavailableError(
                        f"Failed to discover components: {response.status} {error_text}"
                    )
                
                return await response.json()
    except (ConnectionError, TimeoutError) as e:
        raise ComponentUnavailableError(f"Failed to connect to Hermes API: {e}")
    except ImportError:
        raise ImportError("aiohttp is required for discovering components")