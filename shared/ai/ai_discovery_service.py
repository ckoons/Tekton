"""
AI Discovery Service for Tekton Platform

Provides MCP-like discovery and introspection capabilities for AI specialists.
This allows clients like aish to discover available AIs, their capabilities,
and interact with them dynamically.
"""
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path

# Registry client removed - using fixed port discovery
from shared.utils.ai_port_utils import get_ai_port, AI_PORT_MAP
from landmarks import api_contract, integration_point, architecture_decision

logger = logging.getLogger(__name__)


@architecture_decision(
    title="AI Discovery Service",
    rationale="Provide MCP-like discovery for AI specialists enabling dynamic client integration",
    alternatives_considered=["Static configuration", "Manual AI listing", "Component-specific discovery"],
    impacts=["dynamic_discovery", "client_flexibility", "ai_introspection"]
)
class AIDiscoveryService:
    """
    Service for discovering and introspecting AI specialists in the Tekton platform.
    
    This provides a unified interface for clients to:
    - Discover available AI specialists
    - Query their capabilities and roles
    - Get connection information
    - Monitor AI health and performance
    """
    
    def __init__(self):
        """Initialize the AI Discovery Service."""
        # Registry removed - using fixed port mappings from ai_port_utils
        self._fixed_ports = AI_PORT_MAP
        self._capability_cache = {}
        self._last_cache_update = 0
        self._cache_ttl = 60  # Cache for 1 minute
        
    @api_contract(
        title="List Available AIs",
        endpoint="list_ais",
        method="GET",
        response_schema={
            "ais": [{
                "id": "string",
                "name": "string", 
                "component": "string",
                "status": "string",
                "roles": ["string"],
                "capabilities": ["string"],
                "connection": {"host": "string", "port": "int"}
            }]
        }
    )
    async def list_ais(self, role: Optional[str] = None, 
                      capability: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available AI specialists with optional filtering.
        
        Args:
            role: Filter by role (e.g., 'code-analysis', 'planning')
            capability: Filter by capability (e.g., 'streaming', 'structured-output')
            
        Returns:
            Dictionary with list of AI specialists
        """
        # Return fixed port mappings as list
        all_ais = [
            {'id': ai_id, 'port': port, 'host': 'localhost', 'status': 'unknown'}
            for ai_id, port in self._fixed_ports.items()
        ]
        ai_list = []
        
        for ai_data in all_ais:
            # Get detailed info for each AI
            ai_id = ai_data['id']
            ai_info = await self.get_ai_info(ai_id)
            
            # Apply filters if specified
            if role and role not in ai_info.get('roles', []):
                continue
            if capability and capability not in ai_info.get('capabilities', []):
                continue
                
            ai_list.append(ai_info)
        
        return {"ais": ai_list}
    
    @api_contract(
        title="Get AI Information",
        endpoint="get_ai_info/{ai_id}",
        method="GET",
        response_schema={
            "id": "string",
            "name": "string",
            "component": "string",
            "status": "string",
            "roles": ["string"],
            "capabilities": ["string"],
            "model": "string",
            "context_window": "int",
            "max_tokens": "int",
            "connection": {"host": "string", "port": "int"},
            "performance": {
                "avg_response_time": "float",
                "success_rate": "float",
                "total_requests": "int"
            }
        }
    )
    async def get_ai_info(self, ai_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific AI specialist.
        
        Args:
            ai_id: AI identifier
            
        Returns:
            Detailed AI information
        """
        # Get basic info from registry
        # Get socket info from fixed ports
        port = self._fixed_ports.get(ai_id)
        socket_info = ('localhost', port) if port else None
        if not socket_info:
            return {"error": f"AI {ai_id} not found"}
        
        # Get registry data
        # Return fixed port mappings as list
        all_ais = [
            {'id': ai_id, 'port': port, 'host': 'localhost', 'status': 'unknown'}
            for ai_id, port in self._fixed_ports.items()
        ]
        # Find AI in list
        ai_data = next((ai for ai in all_ais if ai['id'] == ai_id), {})
        
        # Try to get live info from the AI
        live_info = await self._query_ai_info(ai_id, socket_info)
        
        # Combine all information
        info = {
            "id": ai_id,
            "name": ai_data.get('component', ai_id),
            "component": ai_data.get('component', 'unknown'),
            "status": "healthy" if live_info else "unreachable",
            "roles": self._get_ai_roles(ai_id, ai_data),
            "capabilities": self._get_ai_capabilities(ai_id, ai_data, live_info),
            "model": live_info.get('model', 'llama3.3:70b') if live_info else 'unknown',
            "context_window": live_info.get('context_window', 100000) if live_info else None,
            "max_tokens": live_info.get('max_tokens', 4000) if live_info else None,
            "connection": {
                "host": socket_info[0],
                "port": socket_info[1]
            },
            "performance": self._get_ai_performance(ai_id)
        }
        
        # Add any metadata
        if ai_data.get('metadata'):
            info['metadata'] = ai_data['metadata']
            
        return info
    
    async def discover_by_capability(self, required_capabilities: List[str]) -> List[Dict[str, Any]]:
        """
        Discover AIs that have all required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            List of matching AIs
        """
        all_ais = await self.list_ais()
        matching = []
        
        for ai in all_ais['ais']:
            ai_caps = set(ai.get('capabilities', []))
            if all(cap in ai_caps for cap in required_capabilities):
                matching.append(ai)
                
        return matching
    
    async def test_ai_connection(self, ai_id: str) -> Dict[str, Any]:
        """
        Test connection to an AI specialist.
        
        Args:
            ai_id: AI identifier
            
        Returns:
            Connection test results
        """
        # Get socket info from fixed ports
        port = self._fixed_ports.get(ai_id)
        socket_info = ('localhost', port) if port else None
        if not socket_info:
            return {
                "ai_id": ai_id,
                "reachable": False,
                "error": "Not found in registry"
            }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Try to connect and send a ping
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(socket_info[0], socket_info[1]),
                timeout=5.0
            )
            
            # Send ping message
            ping_msg = json.dumps({"type": "ping"}) + "\n"
            writer.write(ping_msg.encode())
            await writer.drain()
            
            # Read response
            response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            writer.close()
            await writer.wait_closed()
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "ai_id": ai_id,
                "reachable": True,
                "response_time": response_time,
                "socket": f"{socket_info[0]}:{socket_info[1]}"
            }
            
        except Exception as e:
            return {
                "ai_id": ai_id,
                "reachable": False,
                "error": str(e),
                "socket": f"{socket_info[0]}:{socket_info[1]}"
            }
    
    async def get_ai_schema(self, ai_id: str) -> Dict[str, Any]:
        """
        Get the interaction schema for an AI specialist.
        
        This provides information about:
        - Message formats the AI accepts
        - Available commands/types
        - Response formats
        - Special features
        
        Args:
            ai_id: AI identifier
            
        Returns:
            AI interaction schema
        """
        # Get socket info from fixed ports
        port = self._fixed_ports.get(ai_id)
        socket_info = ('localhost', port) if port else None
        if not socket_info:
            return {"error": f"AI {ai_id} not found"}
        
        # Standard schema that all AIs should support
        base_schema = {
            "ai_id": ai_id,
            "message_types": {
                "chat": {
                    "description": "Standard chat/completion request",
                    "required": ["content"],
                    "optional": ["temperature", "max_tokens", "system_prompt"]
                },
                "info": {
                    "description": "Get AI information",
                    "required": [],
                    "optional": []
                },
                "ping": {
                    "description": "Test connection",
                    "required": [],
                    "optional": []
                }
            },
            "response_format": {
                "chat": {
                    "content": "string",
                    "model": "string",
                    "usage": {"prompt_tokens": "int", "completion_tokens": "int"}
                },
                "info": {
                    "model": "string",
                    "capabilities": ["string"],
                    "context_window": "int"
                },
                "ping": {
                    "pong": "boolean",
                    "timestamp": "float"
                }
            }
        }
        
        # Try to get AI-specific schema
        try:
            specific_schema = await self._query_ai_schema(ai_id, socket_info)
            if specific_schema:
                base_schema.update(specific_schema)
        except Exception as e:
            logger.warning(f"Could not get schema from {ai_id}: {e}")
            
        return base_schema
    
    def create_discovery_manifest(self) -> Dict[str, Any]:
        """
        Create a discovery manifest for the entire AI platform.
        
        This is similar to MCP's manifest concept, providing a complete
        description of available AI services.
        
        Returns:
            Platform AI manifest
        """
        manifest = {
            "platform": "Tekton AI Platform",
            "version": "1.0.0",
            "discovery_service": {
                "version": "1.0.0",
                "endpoints": {
                    "list_ais": "/ai/discovery/list",
                    "get_ai_info": "/ai/discovery/info/{ai_id}",
                    "test_connection": "/ai/discovery/test/{ai_id}",
                    "get_schema": "/ai/discovery/schema/{ai_id}"
                }
            },
            "ai_registry": {
                "total_ais": len(self._fixed_ports),
                "roles": self._get_all_roles(),
                "capabilities": self._get_all_capabilities()
            },
            "interaction_protocol": {
                "transport": "TCP Socket",
                "format": "JSON-RPC over newline-delimited JSON",
                "default_port_range": "45000-50000"
            }
        }
        
        return manifest
    
    # Helper methods
    
    async def _query_ai_info(self, ai_id: str, socket_info: tuple) -> Optional[Dict[str, Any]]:
        """Query live information from an AI."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(socket_info[0], socket_info[1]),
                timeout=2.0
            )
            
            # Send info request
            info_msg = json.dumps({"type": "info"}) + "\n"
            writer.write(info_msg.encode())
            await writer.drain()
            
            # Read response
            response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            writer.close()
            await writer.wait_closed()
            
            return json.loads(response.decode())
            
        except Exception as e:
            logger.debug(f"Could not query info from {ai_id}: {e}")
            return None
    
    async def _query_ai_schema(self, ai_id: str, socket_info: tuple) -> Optional[Dict[str, Any]]:
        """Query schema information from an AI."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(socket_info[0], socket_info[1]),
                timeout=2.0
            )
            
            # Send schema request
            schema_msg = json.dumps({"type": "schema"}) + "\n"
            writer.write(schema_msg.encode())
            await writer.drain()
            
            # Read response
            response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            writer.close()
            await writer.wait_closed()
            
            return json.loads(response.decode())
            
        except Exception:
            return None
    
    def _get_ai_roles(self, ai_id: str, ai_data: Dict[str, Any]) -> List[str]:
        """Get roles for an AI from metadata."""
        # Return empty list - roles should come from AI metadata
        return ai_data.get('roles', [])
    
    def _get_ai_capabilities(self, ai_id: str, ai_data: Dict[str, Any], 
                           live_info: Optional[Dict[str, Any]]) -> List[str]:
        """Get capabilities for an AI from metadata."""
        if live_info and 'capabilities' in live_info:
            return live_info['capabilities']
            
        # Return from ai_data or empty list
        return ai_data.get('capabilities', [])
    
    def _get_ai_performance(self, ai_id: str) -> Dict[str, float]:
        """Get performance metrics for an AI."""
        # TODO: Implement actual performance tracking
        return {
            "avg_response_time": 0.5,
            "success_rate": 0.95,
            "total_requests": 0
        }
    
    def _get_all_roles(self) -> List[str]:
        """Get all available roles in the platform."""
        return [
            'code-analysis', 'planning', 'orchestration', 'knowledge-synthesis',
            'memory', 'messaging', 'learning', 'agent-coordination',
            'specialist-management', 'workflow-design', 'general'
        ]
    
    def _get_all_capabilities(self) -> List[str]:
        """Get all available capabilities in the platform."""
        return [
            'streaming', 'structured-output', 'function-calling',
            'code-generation', 'code-analysis', 'planning',
            'memory-access', 'multi-turn', 'context-aware',
            'tool-use', 'reasoning', 'synthesis'
        ]