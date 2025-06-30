"""
MCP Tools Integration Module for Rhetor - Unified with AI Registry.

This module provides the integration layer between MCP tools and the AI Registry,
replacing the old specialist manager with registry-based discovery.
"""

import logging
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.ai.registry_client import AIRegistryClient
from shared.ai.ai_discovery_service import AIDiscoveryService

logger = logging.getLogger(__name__)


class MCPToolsIntegrationUnified:
    """
    Integration layer connecting MCP tools to the AI Registry.
    
    This class provides real implementations for MCP tool functions,
    using the AI Registry for specialist discovery and management.
    """
    
    def __init__(self, hermes_url: str = "http://localhost:8001"):
        """Initialize the MCP tools integration with AI Registry.
        
        Args:
            hermes_url: URL of the Hermes message bus
        """
        self.hermes_url = hermes_url
        self.registry = AIRegistryClient()
        self.discovery = AIDiscoveryService()
        logger.info("Initialized MCP tools integration with AI Registry")
    
    async def list_specialists(self) -> List[Dict[str, Any]]:
        """List all AI specialists from the registry.
        
        Returns:
            List of specialist information
        """
        try:
            result = await self.discovery.list_ais()
            return result.get('ais', [])
        except Exception as e:
            logger.error(f"Failed to list specialists: {e}")
            return []
    
    async def activate_specialist(self, specialist_id: str) -> Dict[str, Any]:
        """Activate an AI specialist (placeholder - specialists auto-start).
        
        Args:
            specialist_id: ID of the specialist
            
        Returns:
            Activation result
        """
        try:
            # Check if specialist exists
            ai_info = await self.discovery.get_ai_info(specialist_id)
            if not ai_info:
                return {"success": False, "error": f"Specialist {specialist_id} not found"}
            
            # Specialists auto-start with the platform, so just check status
            if ai_info.get('status') == 'healthy':
                return {
                    "success": True,
                    "message": f"Specialist {specialist_id} is already active"
                }
            else:
                return {
                    "success": False,
                    "error": f"Specialist {specialist_id} is not healthy: {ai_info.get('status')}"
                }
        except Exception as e:
            logger.error(f"Failed to activate specialist {specialist_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_message_to_specialist(self, specialist_id: str, message: str, 
                                       context: Optional[Dict[str, Any]] = None,
                                       timeout: float = 10.0) -> Dict[str, Any]:
        """Send a message to an AI specialist.
        
        This method handles both socket-based (Greek Chorus) and API-based (Rhetor) specialists.
        
        Args:
            specialist_id: ID of the specialist (e.g., 'athena-ai', 'apollo-ai')
            message: Message content
            context: Optional context
            timeout: Response timeout in seconds (default 10.0)
            
        Returns:
            Response from specialist with success status
        """
        try:
            # Get specialist info
            ai_info = await self.discovery.get_ai_info(specialist_id)
            if not ai_info:
                return {
                    "success": False, 
                    "error": f"Specialist {specialist_id} not found",
                    "response": None
                }
            
            # Check if this is a socket-based AI (Greek Chorus)
            if 'connection' in ai_info and ai_info['connection'].get('port'):
                # Socket-based communication for Greek Chorus AIs
                return await self._send_via_socket(ai_info, message, context, timeout)
            else:
                # API-based communication via Rhetor
                return await self._send_via_api(specialist_id, message, context)
                
        except Exception as e:
            logger.error(f"Failed to send message to {specialist_id}: {e}")
            return {
                "success": False, 
                "error": str(e),
                "response": None
            }
    
    async def get_specialist_conversation_history(self, specialist_id: str, 
                                                limit: int = 10) -> Dict[str, Any]:
        """Get conversation history for a specialist.
        
        Args:
            specialist_id: ID of the specialist
            limit: Maximum number of messages
            
        Returns:
            Conversation history
        """
        # TODO: Implement actual history retrieval from Engram
        raise NotImplementedError(f"GetSpecialistConversationHistory not implemented for {specialist_id}")
    
    async def configure_orchestration(self, settings: Dict[str, Any]) -> bool:
        """Configure AI orchestration settings.
        
        Args:
            settings: New orchestration settings
            
        Returns:
            True if successful
        """
        # TODO: Implement orchestration configuration
        raise NotImplementedError("ConfigureOrchestration not implemented yet")
    
    async def orchestrate_team_chat(
        self,
        topic: str,
        specialists: List[str],
        initial_prompt: str,
        max_rounds: int = 3,
        orchestration_style: str = "collaborative",
        timeout: float = 10.0
    ) -> Dict[str, Any]:
        """Orchestrate a team chat between multiple AI specialists.
        
        This method connects to real Greek Chorus AIs via sockets and coordinates
        their responses for collaborative problem solving.
        
        Args:
            topic: Discussion topic
            specialists: List of specialist IDs to include (if empty, uses all available)
            initial_prompt: Initial prompt to start discussion
            max_rounds: Maximum rounds of discussion (currently uses 1 round)
            orchestration_style: Style of orchestration (collaborative, directive, exploratory)
            timeout: Timeout for each AI response in seconds
            
        Returns:
            Dictionary containing team chat results with responses from all AIs
        """
        logger.info(f"Starting team chat orchestration on topic: {topic}")
        logger.info(f"Requested specialists: {specialists}")
        logger.info(f"Orchestration style: {orchestration_style}")
        
        try:
            # Discover all available specialists
            all_specialists = await self.list_specialists()
            logger.info(f"Found {len(all_specialists)} total specialists")
            
            # Filter for Greek Chorus AIs (those with socket connections on ports 45000+)
            greek_chorus = []
            for spec in all_specialists:
                if 'connection' in spec and spec['connection'].get('port'):
                    port = spec['connection']['port']
                    if 45000 <= port <= 50000:  # Greek Chorus port range
                        greek_chorus.append(spec)
                        logger.info(f"Including Greek Chorus AI: {spec['id']} on port {port}")
            
            logger.info(f"Found {len(greek_chorus)} Greek Chorus AIs")
            
            # If specific specialists requested, filter for those
            if specialists:
                greek_chorus = [s for s in greek_chorus if s['id'] in specialists]
                logger.info(f"Filtered to {len(greek_chorus)} requested specialists")
            
            if not greek_chorus:
                error_msg = "No Greek Chorus AIs available for team chat"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "responses": {}
                }
            
            # Prepare the message with topic context
            message = f"Topic: {topic}\n\n{initial_prompt}"
            
            # Send to each AI concurrently
            tasks = []
            for specialist in greek_chorus:
                logger.info(f"Creating task for {specialist['id']}")
                task = asyncio.create_task(
                    self.send_message_to_specialist(
                        specialist['id'],
                        message,
                        context={"topic": topic, "orchestration_style": orchestration_style},
                        timeout=timeout
                    )
                )
                tasks.append((specialist['id'], specialist.get('role', 'unknown'), task))
            
            # Collect responses with timeout
            responses = {}
            response_count = 0
            error_count = 0
            
            for spec_id, role, task in tasks:
                try:
                    logger.info(f"Waiting for response from {spec_id} (timeout: {timeout}s)")
                    result = await asyncio.wait_for(task, timeout)
                    
                    if result['success']:
                        responses[spec_id] = {
                            "role": role,
                            "response": result['response'],
                            "type": result.get('type', 'unknown')
                        }
                        response_count += 1
                        logger.info(f"Got response from {spec_id}: {len(result['response'])} chars")
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        logger.error(f"{spec_id} failed: {error_msg}")
                        responses[spec_id] = {
                            "role": role,
                            "response": f"Error: {error_msg}",
                            "error": True
                        }
                        error_count += 1
                        
                except asyncio.TimeoutError:
                    logger.warning(f"{spec_id} timed out after {timeout}s")
                    responses[spec_id] = {
                        "role": role,
                        "response": f"Timeout after {timeout} seconds",
                        "error": True
                    }
                    error_count += 1
                except Exception as e:
                    logger.error(f"Unexpected error from {spec_id}: {e}")
                    responses[spec_id] = {
                        "role": role,
                        "response": f"Unexpected error: {str(e)}",
                        "error": True
                    }
                    error_count += 1
            
            # Prepare summary
            success = response_count > 0
            summary = f"Received {response_count} responses from {len(tasks)} specialists"
            if error_count > 0:
                summary += f" ({error_count} errors)"
            
            logger.info(f"Team chat complete: {summary}")
            
            return {
                "success": success,
                "topic": topic,
                "orchestration_style": orchestration_style,
                "responses": responses,
                "summary": summary,
                "response_count": response_count,
                "error_count": error_count,
                "total_specialists": len(tasks)
            }
            
        except Exception as e:
            error_msg = f"Team chat orchestration failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "responses": {}
            }
    
    async def _send_via_socket(self, ai_info: Dict[str, Any], message: str, 
                              context: Optional[Dict[str, Any]] = None,
                              timeout: float = 10.0) -> Dict[str, Any]:
        """Send message via direct socket connection (Greek Chorus AIs).
        
        Args:
            ai_info: AI information including connection details
            message: Message to send
            context: Optional context
            timeout: Socket timeout in seconds (default 10.0)
            
        Returns:
            Response dictionary with success status
        """
        host = ai_info['connection'].get('host', 'localhost')
        port = ai_info['connection']['port']
        specialist_id = ai_info['id']
        
        try:
            # Use the new shared socket client
            from shared.ai.socket_client import AISocketClient
            
            client = AISocketClient(
                default_timeout=timeout,
                connection_timeout=2.0,
                max_retries=0  # No retries for team chat to avoid delays
            )
            
            logger.info(f"Sending message to {specialist_id} at {host}:{port}")
            
            result = await client.send_message(
                host=host,
                port=port,
                message=message,
                context=context,
                timeout=timeout
            )
            
            if result["success"]:
                logger.info(f"Got response from {specialist_id}: {len(result['response'])} chars")
                return {
                    "success": True,
                    "response": result["response"],
                    "specialist_id": specialist_id,
                    "type": "socket",
                    "model": result.get("model", "unknown"),
                    "elapsed_time": result.get("elapsed_time", 0)
                }
            else:
                logger.warning(f"Failed to get response from {specialist_id}: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "response": None,
                    "specialist_id": specialist_id
                }
                
        except Exception as e:
            logger.error(f"Socket communication error for {specialist_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Socket error: {str(e)}",
                "response": None,
                "specialist_id": specialist_id
            }
    
    async def _send_via_api(self, specialist_id: str, message: str,
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send message via Rhetor API.
        
        Args:
            specialist_id: Specialist ID
            message: Message to send
            context: Optional context
            
        Returns:
            Response dictionary with success status
        """
        try:
            # Use aiohttp if available, otherwise fallback to requests
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "specialist_id": specialist_id,
                        "message": message,
                        "context": context or {}
                    }
                    
                    async with session.post(
                        f"{self.hermes_url}/api/chat/{specialist_id}",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "response": data.get('response', ''),
                                "specialist_id": specialist_id,
                                "type": "api"
                            }
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"API error: {response.status} - {error_text}",
                                "response": None
                            }
            except ImportError:
                # Fallback to synchronous requests
                import requests
                payload = {
                    "specialist_id": specialist_id,
                    "message": message,
                    "context": context or {}
                }
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.post(
                        f"{self.hermes_url}/api/chat/{specialist_id}",
                        json=payload,
                        timeout=30
                    )
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "response": data.get('response', ''),
                        "specialist_id": specialist_id,
                        "type": "api"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code} - {response.text}",
                        "response": None
                    }
                    
        except Exception as e:
            logger.error(f"API communication error: {e}")
            return {
                "success": False,
                "error": f"API error: {str(e)}",
                "response": None
            }


# Singleton instance
_integration_instance: Optional[MCPToolsIntegrationUnified] = None


def get_mcp_tools_integration() -> Optional[MCPToolsIntegrationUnified]:
    """Get the singleton MCP tools integration instance.
    
    Returns:
        The MCP tools integration instance or None if not initialized
    """
    return _integration_instance


def set_mcp_tools_integration(integration: MCPToolsIntegrationUnified):
    """Set the singleton MCP tools integration instance.
    
    Args:
        integration: The MCP tools integration instance
    """
    global _integration_instance
    _integration_instance = integration