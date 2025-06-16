"""
Tekton HTTP Client Utility

This module provides a standardized HTTP client for making requests to Tekton components
and external services, with consistent error handling, retries, and timeout management.

Usage:
    from tekton.utils.tekton_http import http_request, HTTPClient
    
    # Function-based interface
    response = await http_request(
        method="GET",
        url="http://localhost:8001/api/components",
        headers={"Authorization": "Bearer token"}
    )
    
    # Class-based interface
    client = HTTPClient(base_url="http://localhost:8001")
    response = await client.get("/api/components")
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Union, List, Tuple
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientResponseError, ClientConnectorError, ClientTimeout

# Import the custom error types
from .tekton_errors import (
    TektonHTTPError,
    TektonConnectionError,
    TektonTimeoutError,
    TektonAuthenticationError,
    TektonServerError,
    TektonNotFoundError
)

# Set up logger
logger = logging.getLogger(__name__)


async def http_request(
    method: str,
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    retries: int = 3,
    retry_delay: float = 1.0,
    json_response: bool = True,
    auth_token: Optional[str] = None,
    ssl: Optional[bool] = None,
    raise_for_status: bool = True,
    session: Optional[aiohttp.ClientSession] = None
) -> Union[Dict[str, Any], str, bytes]:
    """
    Make an HTTP request with standardized error handling and retries.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Request URL
        data: Request form data (for POST/PUT)
        json_data: Request JSON data (for POST/PUT)
        params: Query parameters
        headers: Request headers
        timeout: Request timeout in seconds
        retries: Maximum number of retries
        retry_delay: Base delay between retries in seconds (uses exponential backoff)
        json_response: Whether to parse the response as JSON
        auth_token: Optional auth token for Bearer authentication
        ssl: SSL verification (None=default, True=verify, False=skip verification)
        raise_for_status: Whether to raise exceptions for non-2xx responses
        session: Optional existing aiohttp session to use
    
    Returns:
        Response data (parsed JSON if json_response=True, otherwise text or bytes)
    
    Raises:
        TektonHTTPError: Base class for all HTTP-related errors
        TektonConnectionError: If connection to the server fails
        TektonTimeoutError: If the request times out
        TektonAuthenticationError: If authentication fails (401)
        TektonNotFoundError: If resource is not found (404)
        TektonServerError: If server returns 5xx error
    """
    # Prepare headers
    request_headers = headers.copy() if headers else {}
    
    # Add auth token if provided
    if auth_token:
        request_headers["Authorization"] = f"Bearer {auth_token}"
    
    # Set up timeout
    client_timeout = ClientTimeout(total=timeout)
    
    # Prepare for retries with exponential backoff
    max_retries = max(0, retries)
    should_close_session = session is None
    
    try:
        # Create session if not provided
        if session is None:
            session = aiohttp.ClientSession(timeout=client_timeout)
        
        # Track retry attempts
        attempt = 0
        last_exception = None
        
        while attempt <= max_retries:
            try:
                async with session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    headers=request_headers,
                    data=data,
                    json=json_data,
                    ssl=ssl,
                    raise_for_status=raise_for_status
                ) as response:
                    # Handle successful response
                    if json_response:
                        try:
                            return await response.json()
                        except json.JSONDecodeError as e:
                            content = await response.text()
                            raise TektonHTTPError(
                                f"Failed to parse JSON response: {e}. Content: {content[:500]}"
                            ) from e
                    else:
                        # Return text or bytes based on content type
                        content_type = response.headers.get("Content-Type", "")
                        if "text" in content_type or "json" in content_type:
                            return await response.text()
                        else:
                            return await response.read()
            
            except ClientResponseError as e:
                # Map HTTP status codes to specific exceptions
                if e.status == 401:
                    raise TektonAuthenticationError(f"Authentication failed: {e.message}")
                elif e.status == 404:
                    raise TektonNotFoundError(f"Resource not found: {url}")
                elif 500 <= e.status < 600:
                    raise TektonServerError(f"Server error {e.status}: {e.message}")
                
                # Only retry for 5xx errors
                if 500 <= e.status < 600 and attempt < max_retries:
                    last_exception = e
                    logger.warning(f"Request failed with status {e.status} (attempt {attempt+1}/{max_retries+1}), retrying...")
                    attempt += 1
                    # Exponential backoff
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise TektonHTTPError(f"HTTP error {e.status}: {e.message}") from e
            
            except (ClientConnectorError, ConnectionError) as e:
                # Only retry connection errors
                if attempt < max_retries:
                    last_exception = e
                    logger.warning(f"Connection error (attempt {attempt+1}/{max_retries+1}), retrying...")
                    attempt += 1
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise TektonConnectionError(f"Failed to connect to {url}: {str(e)}") from e
            
            except asyncio.TimeoutError as e:
                # Only retry timeouts
                if attempt < max_retries:
                    last_exception = e
                    logger.warning(f"Request timed out (attempt {attempt+1}/{max_retries+1}), retrying...")
                    attempt += 1
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise TektonTimeoutError(f"Request to {url} timed out after {timeout} seconds") from e
            
            except Exception as e:
                # Any other error is immediately raised
                raise TektonHTTPError(f"Request failed: {str(e)}") from e
            
            # If we got here, the request was successful
            break
        
        # If we exhausted retries, raise the last exception
        if attempt > max_retries and last_exception is not None:
            if isinstance(last_exception, ClientConnectorError):
                raise TektonConnectionError(f"Failed to connect to {url} after {max_retries} retries: {str(last_exception)}")
            elif isinstance(last_exception, asyncio.TimeoutError):
                raise TektonTimeoutError(f"Request to {url} timed out after {max_retries} retries")
            else:
                raise TektonHTTPError(f"Request failed after {max_retries} retries: {str(last_exception)}")
        
        # Should never reach here
        raise TektonHTTPError("Unexpected error in http_request")
    
    finally:
        # Close session if we created it
        if should_close_session and session is not None:
            await session.close()


class HTTPClient:
    """
    HTTP client for making requests to Tekton components with standardized error handling.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: int = 30,
        retries: int = 3,
        retry_delay: float = 1.0,
        headers: Optional[Dict[str, str]] = None,
        component_id: Optional[str] = None,
        ssl: Optional[bool] = None
    ):
        """
        Initialize the HTTP client.
        
        Args:
            base_url: Base URL for requests
            auth_token: Authentication token for Bearer auth
            timeout: Default request timeout in seconds
            retries: Default maximum number of retries
            retry_delay: Default base delay between retries
            headers: Default headers to include in all requests
            component_id: ID of the component for logging
            ssl: SSL verification (None=default, True=verify, False=skip verification)
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.headers = headers or {}
        self.component_id = component_id
        self.ssl = ssl
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> None:
        """Initialize the client session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=ClientTimeout(total=self.timeout))
    
    async def close(self) -> None:
        """Close the client session."""
        if self.session is not None:
            await self.session.close()
            self.session = None
    
    def _get_url(self, path: str) -> str:
        """
        Get the full URL for a path.
        
        Args:
            path: URL path
        
        Returns:
            Full URL
        """
        if self.base_url:
            # Ensure path starts with / if needed
            if not path.startswith("/") and not self.base_url.endswith("/"):
                path = f"/{path}"
            return urljoin(self.base_url, path)
        return path
    
    async def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        json_response: bool = True,
        auth_token: Optional[str] = None,
        ssl: Optional[bool] = None,
        raise_for_status: bool = True
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make an HTTP request.
        
        Args:
            method: HTTP method
            path: URL path (will be joined with base_url if provided)
            data: Request form data
            json_data: Request JSON data
            params: Query parameters
            headers: Request headers (merged with default headers)
            timeout: Request timeout in seconds (overrides default)
            retries: Maximum number of retries (overrides default)
            retry_delay: Base delay between retries (overrides default)
            json_response: Whether to parse the response as JSON
            auth_token: Auth token for Bearer auth (overrides default)
            ssl: SSL verification (overrides default)
            raise_for_status: Whether to raise exceptions for non-2xx responses
        
        Returns:
            Response data
        """
        # Ensure session is initialized
        await self.initialize()
        
        # Prepare URL
        url = self._get_url(path)
        
        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Use provided parameters or fall back to defaults
        final_timeout = timeout if timeout is not None else self.timeout
        final_retries = retries if retries is not None else self.retries
        final_retry_delay = retry_delay if retry_delay is not None else self.retry_delay
        final_auth_token = auth_token if auth_token is not None else self.auth_token
        final_ssl = ssl if ssl is not None else self.ssl
        
        # Make the request
        return await http_request(
            method=method,
            url=url,
            data=data,
            json_data=json_data,
            params=params,
            headers=request_headers,
            timeout=final_timeout,
            retries=final_retries,
            retry_delay=final_retry_delay,
            json_response=json_response,
            auth_token=final_auth_token,
            ssl=final_ssl,
            raise_for_status=raise_for_status,
            session=self.session
        )
    
    # Convenience methods for common HTTP methods
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make a GET request.
        
        Args:
            path: URL path
            params: Query parameters
            **kwargs: Additional arguments for request()
        
        Returns:
            Response data
        """
        return await self.request("GET", path, params=params, **kwargs)
    
    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make a POST request.
        
        Args:
            path: URL path
            data: Form data
            json_data: JSON data
            **kwargs: Additional arguments for request()
        
        Returns:
            Response data
        """
        return await self.request("POST", path, data=data, json_data=json_data, **kwargs)
    
    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make a PUT request.
        
        Args:
            path: URL path
            data: Form data
            json_data: JSON data
            **kwargs: Additional arguments for request()
        
        Returns:
            Response data
        """
        return await self.request("PUT", path, data=data, json_data=json_data, **kwargs)
    
    async def delete(
        self,
        path: str,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make a DELETE request.
        
        Args:
            path: URL path
            **kwargs: Additional arguments for request()
        
        Returns:
            Response data
        """
        return await self.request("DELETE", path, **kwargs)
    
    async def head(
        self,
        path: str,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make a HEAD request.
        
        Args:
            path: URL path
            **kwargs: Additional arguments for request()
        
        Returns:
            Response data
        """
        return await self.request("HEAD", path, **kwargs)
    
    async def patch(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        Make a PATCH request.
        
        Args:
            path: URL path
            data: Form data
            json_data: JSON data
            **kwargs: Additional arguments for request()
        
        Returns:
            Response data
        """
        return await self.request("PATCH", path, data=data, json_data=json_data, **kwargs)
    
    # Context manager support
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Helper function to create a client from environment variables
def create_client_from_env(
    component_id: str,
    env_var_prefix: Optional[str] = None,
    default_port: Optional[int] = None
) -> HTTPClient:
    """
    Create an HTTP client for a component using environment variables.
    
    Args:
        component_id: Component ID (e.g., "hermes", "engram")
        env_var_prefix: Prefix for environment variables (default: component_id.upper())
        default_port: Default port if environment variable is not set
    
    Returns:
        Configured HTTPClient instance
    """
    prefix = env_var_prefix or component_id.upper()
    
    # Get port from environment variable
    port_var = f"{prefix}_PORT"
    host = os.environ.get(f"{prefix}_HOST", "localhost")
    port = os.environ.get(port_var, default_port)
    
    if port is None:
        # Use standard port assignments if known
        known_ports = {
            "engram": 8000,
            "hermes": 8001,
            "ergon": 8002,
            "rhetor": 8003,
            "terma": 8004,
            "athena": 8005,
            "prometheus": 8006,
            "harmonia": 8007,
            "telos": 8008,
            "synthesis": 8009,
            "tekton_core": 8010,
            "hephaestus": 8080
        }
        port = known_ports.get(component_id.lower())
    
    if port is None:
        raise ValueError(f"No port specified for {component_id} and no default available")
    
    # Get auth token if available
    auth_token = os.environ.get(f"{prefix}_AUTH_TOKEN")
    
    # Build base URL
    base_url = f"http://{host}:{port}"
    
    # Create client
    return HTTPClient(
        base_url=base_url,
        auth_token=auth_token,
        component_id=component_id
    )


# Create clients for all Tekton components
def create_hermes_client() -> HTTPClient:
    """Create a client for the Hermes component."""
    return create_client_from_env("hermes", default_port=8001)

def create_engram_client() -> HTTPClient:
    """Create a client for the Engram component."""
    return create_client_from_env("engram", default_port=8000)

def create_rhetor_client() -> HTTPClient:
    """Create a client for the Rhetor component."""
    return create_client_from_env("rhetor", default_port=8003)

def create_ergon_client() -> HTTPClient:
    """Create a client for the Ergon component."""
    return create_client_from_env("ergon", default_port=8002)