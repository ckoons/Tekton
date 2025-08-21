"""
Component Client Factory Module

This module provides factory functions for creating component clients.
"""

from typing import Dict, List, Any, Optional, Type, Union, TypeVar

from .exceptions import ComponentNotFoundError
from .models import SecurityContext, RetryPolicy
from .client import ComponentClient
from .discovery import discover_component

# Type variables
T_Client = TypeVar("T_Client", bound=ComponentClient)


async def create_client(
    component_id: str,
    client_type: Optional[Type[T_Client]] = None,
    hermes_url: Optional[str] = None,
    security_context: Optional[SecurityContext] = None,
    retry_policy: Optional[RetryPolicy] = None
) -> Union[ComponentClient, T_Client]:
    """
    Create a client for a component.
    
    Args:
        component_id: ID of the component to create a client for
        client_type: Type of client to create (defaults to ComponentClient)
        hermes_url: URL of the Hermes API
        security_context: Security context for authentication/authorization
        retry_policy: Policy for retrying capability invocations
        
    Returns:
        Client for the component
        
    Raises:
        ComponentNotFoundError: If the component is not found
        TypeError: If client_type is not a subclass of ComponentClient
    """
    # Check if the component exists
    await discover_component(component_id, hermes_url)
    
    # Create the client
    if client_type is None:
        return ComponentClient(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    elif issubclass(client_type, ComponentClient):
        return client_type(
            component_id=component_id,
            hermes_url=hermes_url,
            security_context=security_context,
            retry_policy=retry_policy
        )
    else:
        raise TypeError(f"client_type must be a subclass of ComponentClient, got {client_type}")


def create_security_context(
    token: Optional[str] = None,
    client_id: Optional[str] = None,
    roles: Optional[List[str]] = None
) -> SecurityContext:
    """
    Create a security context for capability invocation.
    
    Args:
        token: Authentication token
        client_id: Client ID
        roles: Roles
        
    Returns:
        Security context
    """
    return SecurityContext(token=token, client_id=client_id, roles=roles)


def create_retry_policy(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_multiplier: float = 2.0,
    retry_max_delay: float = 30.0,
    retry_on: Optional[List[Type[Exception]]] = None
) -> RetryPolicy:
    """
    Create a retry policy for capability invocations.
    
    Args:
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        retry_multiplier: Multiplier for delay after each retry
        retry_max_delay: Maximum delay between retries in seconds
        retry_on: Types of exceptions to retry on
        
    Returns:
        Retry policy
    """
    return RetryPolicy(
        max_retries=max_retries,
        retry_delay=retry_delay,
        retry_multiplier=retry_multiplier,
        retry_max_delay=retry_max_delay,
        retry_on=retry_on
    )