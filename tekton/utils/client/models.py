"""
Component Client Models

This module provides data models for the component client.
"""

from typing import List, Type, Optional


class SecurityContext:
    """Security context for capability invocation."""
    
    def __init__(
        self,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        roles: Optional[List[str]] = None
    ):
        """
        Initialize the security context.
        
        Args:
            token: Authentication token
            client_id: Client ID
            roles: Roles
        """
        self.token = token
        self.client_id = client_id
        self.roles = roles or []


class RetryPolicy:
    """Policy for retrying capability invocations."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_multiplier: float = 2.0,
        retry_max_delay: float = 30.0,
        retry_on: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize the retry policy.
        
        Args:
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries in seconds
            retry_multiplier: Multiplier for delay after each retry
            retry_max_delay: Maximum delay between retries in seconds
            retry_on: Types of exceptions to retry on
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_max_delay = retry_max_delay
        
        # Import here to avoid circular imports
        from .exceptions import ComponentUnavailableError
        self.retry_on = retry_on or [ComponentUnavailableError]