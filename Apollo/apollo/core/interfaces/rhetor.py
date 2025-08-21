"""
Rhetor Interface for Apollo.

This module provides an interface for communicating with the Rhetor component
to monitor LLM context usage and metrics.
"""

import os
import logging
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import from shared utils
import sys
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Try to import landmarks
try:
    from landmarks import integration_point, api_contract
except ImportError:
    # Define no-op decorators if landmarks not available
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Use Tekton's centralized URL management
from shared.urls import rhetor_url, hermes_url, apollo_url

def get_component_url(component_name: str, protocol: str = "http") -> str:
    """Get component URL using Tekton's centralized URL management."""
    if protocol == "ws":
        # For WebSocket, we need to build it manually
        if component_name == "rhetor":
            base_url = rhetor_url("")
        elif component_name == "hermes":
            base_url = hermes_url("")
        elif component_name == "apollo":
            base_url = apollo_url("")
        else:
            # Fallback
            base_url = f"http://localhost:8000"
        
        # Convert http to ws
        return base_url.replace("http://", "ws://").replace("https://", "wss://")
    
    # For HTTP, use the URL builders directly
    if component_name == "rhetor":
        return rhetor_url("")
    elif component_name == "hermes":
        return hermes_url("")
    elif component_name == "apollo":
        return apollo_url("")
    else:
        # Fallback
        return f"http://localhost:8000"

# Configure logging
logger = logging.getLogger(__name__)


@integration_point(
    title="Apollo-Rhetor LLM Interface",
    target_component="Rhetor LLM Service",
    protocol="HTTP REST API and WebSocket",
    data_flow="Apollo ↔ Rhetor (context monitoring, metrics, directives)",
    critical_notes="Primary interface for Apollo to monitor and control LLM contexts"
)
class RhetorInterface:
    """
    Interface for communicating with the Rhetor component.
    
    This class handles API calls to Rhetor for retrieving metrics, context information,
    and sending directives for context management.
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 10.0
    ):
        """
        Initialize the Rhetor Interface.
        
        Args:
            base_url: Base URL for the Rhetor API (default: use port_config)
            retry_count: Number of retries for failed requests
            retry_delay: Delay between retries (seconds)
            timeout: Request timeout (seconds)
        """
        self.base_url = base_url or get_component_url("rhetor")
        self.ws_url = get_component_url("rhetor", protocol="ws")
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Session for HTTP requests
        self._session = None
        self._ws = None
        self._ws_connected = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create an HTTP session.
        
        Returns:
            aiohttp.ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Any:
        """
        Make an HTTP request to the Rhetor API with retries.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for the request
            
        Returns:
            Response data
            
        Raises:
            Exception: If the request fails after retries
        """
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.retry_count):
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        text = await response.text()
                        logger.error(f"Rhetor API error: {response.status} - {text}")
                        raise Exception(f"Rhetor API error: {response.status} - {text}")
                    
                    return await response.json()
                    
            except asyncio.TimeoutError:
                logger.warning(f"Request to Rhetor API timed out (attempt {attempt + 1}/{self.retry_count})")
                
            except Exception as e:
                logger.warning(f"Error in request to Rhetor API (attempt {attempt + 1}/{self.retry_count}): {e}")
                
            # Last attempt failed
            if attempt == self.retry_count - 1:
                logger.error(f"Request to Rhetor API failed after {self.retry_count} attempts")
                raise
                
            # Wait before retrying
            await asyncio.sleep(self.retry_delay)
    
    @api_contract(
        title="Get Active LLM Sessions",
        endpoint="/api/v1/ai/specialists",
        method="GET",
        response_schema={"specialists": "array"},
        auth_required=False
    )
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get information about all active AI specialists as sessions from Rhetor.
        
        Returns:
            List of session information dictionaries
        """
        try:
            response = await self._request("GET", "/api/v1/ai/specialists")
            
            # Transform specialists to session format
            sessions = []
            # Handle both array response (new) and object with specialists key (old)
            specialists = response if isinstance(response, list) else response.get("specialists", [])
            for specialist in specialists:
                # Handle different ID field names
                specialist_id = specialist.get("ai_id") or specialist.get("id") or specialist.get("specialist_id")
                if not specialist_id:
                    logger.warning(f"Specialist missing ID field: {specialist}")
                    continue
                    
                sessions.append({
                    "context_id": specialist_id,
                    "name": specialist.get("name", specialist_id),
                    "type": specialist.get("category") or specialist.get("type") or specialist.get("specialist_type", "unknown"),
                    "active": specialist.get("healthy", specialist.get("active", specialist.get("status") == "active")),
                    "message_count": specialist.get("messages", 0),
                    "session_count": specialist.get("sessions", 0),
                    "model": specialist.get("model", "unknown")
                })
            return sessions
        except Exception as e:
            logger.error(f"Error getting active sessions from Rhetor: {e}")
            return []
    
    @api_contract(
        title="Get Session Metrics",
        endpoint="/api/v1/specialists/{context_id}",
        method="GET",
        response_schema={"metrics": "object"},
        auth_required=False
    )
    async def get_session_metrics(self, context_id: str) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific AI specialist session.
        
        Args:
            context_id: Context/Specialist identifier
            
        Returns:
            Dictionary of session metrics
        """
        try:
            response = await self._request("GET", f"/api/v1/specialists/{context_id}")
            
            # Transform to metrics format, handling both "id" and "specialist_id"
            specialist_id = response.get("id") or response.get("specialist_id", context_id)
            
            return {
                "context_id": specialist_id,
                "metrics": {
                    "message_count": response.get("messages", 0),
                    "session_count": response.get("sessions", 0),
                    "status": response.get("status", "unknown"),
                    "model": response.get("model", "unknown"),
                    "capabilities": response.get("capabilities", [])
                }
            }
        except Exception as e:
            logger.error(f"Error getting session metrics for {context_id}: {e}")
            return {}
    
    async def compress_context(
        self, 
        context_id: str,
        level: str = "moderate",
        max_tokens: Optional[int] = None
    ) -> bool:
        """
        Request context compression for an AI specialist session.
        Note: Compression not yet implemented in Rhetor.
        
        Args:
            context_id: Context/Specialist identifier
            level: Compression level (light, moderate, aggressive)
            max_tokens: Maximum tokens to retain after compression
            
        Returns:
            True if the request was successful
        """
        logger.warning(f"Context compression not yet implemented in Rhetor for {context_id}")
        # TODO: Implement when Rhetor adds compression support
        return False
    
    async def reset_context(self, context_id: str) -> bool:
        """
        Request a context reset for an AI specialist session.
        This is done by deactivating and reactivating the specialist.
        
        Args:
            context_id: Context/Specialist identifier
            
        Returns:
            True if the request was successful
        """
        try:
            # First try to deactivate
            try:
                await self._request("DELETE", f"/api/v1/ai/specialists/{context_id}/fire")
            except Exception:
                # Deactivation might not be implemented yet
                pass
            
            # Then reactivate
            response = await self._request("POST", f"/api/v1/ai/specialists/{context_id}/hire")
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Error requesting context reset for {context_id}: {e}")
            return False
    
    @api_contract(
        title="Inject System Message",
        endpoint="/api/v1/chat",
        method="POST",
        request_schema={"message": "string", "context_id": "string", "options": "object"},
        response_schema={"success": "boolean"},
        auth_required=False,
        critical_notes="Used by Apollo to inject attention management directives"
    )
    async def inject_system_message(
        self, 
        context_id: str,
        message: str,
        priority: int = 5
    ) -> bool:
        """
        Inject a system message into an AI specialist context.
        
        Args:
            context_id: Context/Specialist identifier
            message: System message to inject
            priority: Message priority (0-10)
            
        Returns:
            True if the request was successful
        """
        try:
            data = {
                "message": f"SYSTEM[{priority}]: {message}",
                "context_id": context_id,
                "streaming": False,
                "options": {
                    "type": "system",
                    "priority": priority
                }
            }
            
            response = await self._request("POST", f"/api/v1/chat", json=data)
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Error injecting system message for {context_id}: {e}")
            return False
    
    async def connect_websocket(self) -> bool:
        """
        Connect to the Rhetor WebSocket for real-time updates.
        
        Returns:
            True if connection was successful
        """
        if self._ws_connected:
            return True
            
        try:
            session = await self._get_session()
            self._ws = await session.ws_connect(self.ws_url)
            self._ws_connected = True
            
            # Send registration message
            await self._ws.send_json({
                "type": "REGISTER",
                "source": "APOLLO"
            })
            
            logger.info("Connected to Rhetor WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Rhetor WebSocket: {e}")
            self._ws_connected = False
            return False
    
    async def disconnect_websocket(self):
        """Disconnect from the Rhetor WebSocket."""
        if not self._ws_connected or self._ws is None:
            return
            
        try:
            await self._ws.close()
        except Exception as e:
            logger.error(f"Error disconnecting from Rhetor WebSocket: {e}")
        finally:
            self._ws_connected = False
            self._ws = None
    
    async def subscribe_to_context_updates(
        self, 
        context_id: Optional[str] = None,
        callback = None
    ):
        """
        Subscribe to real-time context updates via WebSocket.
        
        Args:
            context_id: Optional context ID to filter updates
            callback: Callback function for updates
            
        Note: This is a placeholder for future implementation.
        """
        # This would be implemented in a future version
        pass
        
    async def close(self):
        """Close all connections."""
        await self.disconnect_websocket()
        
        if self._session and not self._session.closed:
            await self._session.close()