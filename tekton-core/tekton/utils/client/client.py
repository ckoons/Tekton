"""
Component Client

This module provides the base client for Tekton components.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional

from .models import SecurityContext, RetryPolicy
from .exceptions import (
    ComponentNotFoundError,
    CapabilityNotFoundError,
    CapabilityInvocationError,
    ComponentUnavailableError,
    AuthenticationError,
    AuthorizationError
)

# Configure logger
logger = logging.getLogger(__name__)


class ComponentClient:
    """Base client for Tekton components."""
    
    def __init__(
        self,
        component_id: str,
        hermes_url: Optional[str] = None,
        security_context: Optional[SecurityContext] = None,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """
        Initialize the component client.
        
        Args:
            component_id: ID of the component to connect to
            hermes_url: URL of the Hermes API (defaults to HERMES_URL env var)
            security_context: Security context for authentication/authorization
            retry_policy: Policy for retrying capability invocations
        """
        self.component_id = component_id
        self.hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:8000/api")
        self.security_context = security_context or SecurityContext()
        self.retry_policy = retry_policy or RetryPolicy()
        
        # Component info will be loaded lazily
        self._component_info = None
        self._http_client = None
        self._closed = False
    
    async def _get_http_client(self):
        """Get the HTTP client for making requests."""
        if self._http_client is None:
            try:
                import aiohttp
                self._http_client = aiohttp.ClientSession(
                    headers=self._get_auth_headers()
                )
            except ImportError:
                logger.error("aiohttp not installed, cannot make HTTP requests")
                raise ImportError("aiohttp is required for making HTTP requests")
        return self._http_client
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {}
        if self.security_context.token:
            headers["Authorization"] = f"Bearer {self.security_context.token}"
        if self.security_context.client_id:
            headers["X-Client-ID"] = self.security_context.client_id
        return headers
    
    async def _get_component_info(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get information about the component from the service registry.
        
        Args:
            force_refresh: Whether to force a refresh of the component info
            
        Returns:
            Component information
            
        Raises:
            ComponentNotFoundError: If the component is not found
            ComponentUnavailableError: If the Hermes API is unavailable
        """
        if self._component_info is None or force_refresh:
            try:
                http_client = await self._get_http_client()
                async with http_client.get(
                    f"{self.hermes_url}/registry/component/{self.component_id}"
                ) as response:
                    if response.status == 404:
                        raise ComponentNotFoundError(f"Component {self.component_id} not found")
                    elif response.status != 200:
                        error_text = await response.text()
                        raise ComponentUnavailableError(
                            f"Failed to get component info: {response.status} {error_text}"
                        )
                    
                    self._component_info = await response.json()
            except (ConnectionError, TimeoutError) as e:
                raise ComponentUnavailableError(f"Failed to connect to Hermes API: {e}")
        
        return self._component_info
    
    async def _get_capability_info(self, capability: str) -> Dict[str, Any]:
        """
        Get information about a capability from the component.
        
        Args:
            capability: Name of the capability
            
        Returns:
            Capability information
            
        Raises:
            CapabilityNotFoundError: If the capability is not found
        """
        component_info = await self._get_component_info()
        capabilities = component_info.get("capabilities", [])
        
        for cap in capabilities:
            if isinstance(cap, dict) and cap.get("name") == capability:
                return cap
            elif isinstance(cap, str) and cap == capability:
                return {"name": capability}
        
        raise CapabilityNotFoundError(
            f"Component {self.component_id} does not have capability {capability}"
        )
    
    async def invoke_capability(
        self,
        capability: str,
        parameters: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Any:
        """
        Invoke a capability on the component.
        
        Args:
            capability: Name of the capability to invoke
            parameters: Parameters for the capability
            timeout: Timeout for the capability invocation in seconds
            
        Returns:
            Result of the capability invocation
            
        Raises:
            ComponentNotFoundError: If the component is not found
            CapabilityNotFoundError: If the capability is not found
            CapabilityInvocationError: If the capability invocation fails
            ComponentUnavailableError: If the component is unavailable
            AuthenticationError: If authentication fails
            AuthorizationError: If authorization fails
        """
        if self._closed:
            raise RuntimeError("Client is closed")
        
        # Get component info to ensure it exists and get the endpoint
        component_info = await self._get_component_info()
        endpoint = component_info.get("endpoint")
        if not endpoint:
            raise ComponentUnavailableError(
                f"Component {self.component_id} does not have an endpoint"
            )
        
        # Get capability info to ensure it exists
        try:
            await self._get_capability_info(capability)
        except CapabilityNotFoundError:
            # If the component was loaded from cache, try refreshing
            if self._component_info is not None:
                component_info = await self._get_component_info(force_refresh=True)
                try:
                    await self._get_capability_info(capability)
                except CapabilityNotFoundError:
                    raise
        
        # Apply retry policy
        retry_count = 0
        current_delay = self.retry_policy.retry_delay
        
        while True:
            try:
                return await self._do_invoke_capability(endpoint, capability, parameters, timeout)
            except tuple(self.retry_policy.retry_on) as e:
                retry_count += 1
                if retry_count > self.retry_policy.max_retries:
                    logger.warning(
                        f"Max retries ({self.retry_policy.max_retries}) exceeded "
                        f"for {capability} on {self.component_id}"
                    )
                    raise
                
                logger.info(
                    f"Retrying {capability} on {self.component_id} "
                    f"after error: {e} (retry {retry_count}/{self.retry_policy.max_retries})"
                )
                
                await asyncio.sleep(current_delay)
                current_delay = min(
                    current_delay * self.retry_policy.retry_multiplier,
                    self.retry_policy.retry_max_delay
                )
    
    async def _do_invoke_capability(
        self,
        endpoint: str,
        capability: str,
        parameters: Dict[str, Any],
        timeout: Optional[float]
    ) -> Any:
        """
        Perform the actual capability invocation.
        
        Args:
            endpoint: Component endpoint
            capability: Name of the capability to invoke
            parameters: Parameters for the capability
            timeout: Timeout for the capability invocation in seconds
            
        Returns:
            Result of the capability invocation
            
        Raises:
            CapabilityInvocationError: If the capability invocation fails
            ComponentUnavailableError: If the component is unavailable
            AuthenticationError: If authentication fails
            AuthorizationError: If authorization fails
        """
        try:
            http_client = await self._get_http_client()
            
            # Construct the request URL
            request_url = f"{endpoint}/capabilities/{capability}"
            
            # Make the request
            async with http_client.post(
                request_url,
                json=parameters,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise AuthenticationError("Authentication failed")
                elif response.status == 403:
                    raise AuthorizationError("Authorization failed")
                elif response.status == 404:
                    raise CapabilityNotFoundError(
                        f"Component {self.component_id} does not have capability {capability}"
                    )
                elif response.status >= 500:
                    error_text = await response.text()
                    raise ComponentUnavailableError(
                        f"Component {self.component_id} is unavailable: {error_text}"
                    )
                else:
                    error_text = await response.text()
                    try:
                        error_data = json.loads(error_text)
                        error_message = error_data.get("message", error_text)
                        error_detail = error_data.get("detail")
                    except (json.JSONDecodeError, ValueError):
                        error_message = error_text
                        error_detail = None
                    
                    raise CapabilityInvocationError(
                        f"Error invoking capability {capability} on {self.component_id}: {error_message}",
                        error_detail
                    )
        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as e:
            raise ComponentUnavailableError(
                f"Failed to connect to component {self.component_id}: {e}"
            )
    
    async def close(self):
        """Close the client and release resources."""
        if not self._closed and self._http_client is not None:
            await self._http_client.close()
            self._http_client = None
        
        self._closed = True