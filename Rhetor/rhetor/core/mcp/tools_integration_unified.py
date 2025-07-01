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
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path)))))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.ai.registry_client import AIRegistryClient
from shared.ai.ai_discovery_service import AIDiscoveryService

logger = logging.getLogger(__name__)


class RoutingEngine:
    """Simple routing engine for AI orchestration configuration."""
    
    def __init__(self):
        self.configuration = {
            "routing_mode": "role_based",
            "fallback_chain": [],
            "context_weight": 0.5,
            "load_threshold": 100,
            "custom_rules": []
        }
        self.specialist_weights = {}
    
    async def get_configuration(self) -> Dict[str, Any]:
        """Get current routing configuration."""
        return self.configuration.copy()
    
    async def update_configuration(self, new_config: Dict[str, Any]):
        """Update routing configuration."""
        self.configuration.update(new_config)
    
    async def update_specialist_weight(self, specialist_id: str, context_weight: float):
        """Update context weight for a specialist."""
        self.specialist_weights[specialist_id] = context_weight


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
        
        # Initialize routing engine (placeholder for now)
        self.routing_engine = RoutingEngine()
        
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
                                                limit: int = 10,
                                                context_id: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation history for a specialist from Engram.
        
        This method queries Engram's memory system for conversations involving
        a specific AI specialist, supporting bidirectional memory flow.
        
        Args:
            specialist_id: ID of the specialist (e.g., 'apollo-ai')
            limit: Maximum number of conversations to retrieve
            context_id: Optional specific context/conversation ID
            
        Returns:
            Dictionary containing conversation history with metadata
        """
        try:
            import httpx
            
            # Engram API endpoint - using standard port from port_assignments.md
            engram_url = "http://localhost:8000"  # Engram's official port
            
            # Build query for specialist conversations
            query = f"specialist:{specialist_id}"
            if context_id:
                query += f" context:{context_id}"
            
            # Query Engram for relevant conversations
            async with httpx.AsyncClient() as client:
                # Search for conversations involving this specialist
                response = await client.post(
                    f"{engram_url}/api/v1/search",
                    json={
                        "query": query,
                        "namespace": "conversations",
                        "limit": limit * 10  # Get more to filter
                    },
                    timeout=httpx.Timeout(10.0)
                )
                
                if response.status_code != 200:
                    logger.error(f"Engram query failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Failed to query Engram: {response.status_code}",
                        "conversations": []
                    }
                
                data = response.json()
                memories = data.get("results", [])
                
                # Process and structure conversations
                conversations = []
                conversation_map = {}
                
                for memory in memories:
                    content = memory.get("content", {})
                    metadata = memory.get("metadata", {})
                    
                    # Check if this memory involves our specialist
                    if specialist_id in str(content) or specialist_id in str(metadata):
                        conv_id = metadata.get("conversation_id", f"conv_{memory.get('id', 'unknown')}")
                        
                        if conv_id not in conversation_map:
                            conversation_map[conv_id] = {
                                "conversation_id": conv_id,
                                "specialist_id": specialist_id,
                                "messages": [],
                                "metadata": {
                                    "created_at": memory.get("created_at"),
                                    "context": metadata.get("context", {}),
                                    "score": memory.get("score", 0.0)
                                }
                            }
                        
                        # Add messages if content is a conversation
                        if isinstance(content, list):
                            conversation_map[conv_id]["messages"].extend(content)
                        elif isinstance(content, dict):
                            conversation_map[conv_id]["messages"].append(content)
                        else:
                            # Single message
                            conversation_map[conv_id]["messages"].append({
                                "role": "assistant" if specialist_id in str(content) else "user",
                                "content": str(content),
                                "specialist_id": specialist_id if specialist_id in str(content) else None
                            })
                
                # Convert to list and sort by relevance
                conversations = list(conversation_map.values())
                conversations.sort(key=lambda x: x["metadata"].get("score", 0), reverse=True)
                
                # Limit results
                conversations = conversations[:limit]
                
                # Get additional context from Engram if available
                if conversations and context_id:
                    # Query for related memories
                    related_response = await client.post(
                        f"{engram_url}/api/v1/search",
                        json={
                            "query": f"related:{context_id}",
                            "namespace": "context",
                            "limit": 5
                        }
                    )
                    
                    if related_response.status_code == 200:
                        related_data = related_response.json()
                        related_memories = related_data.get("results", [])
                        
                        # Add related context to conversations
                        for conv in conversations:
                            conv["related_context"] = [
                                {
                                    "content": mem.get("content"),
                                    "relevance": mem.get("score", 0.0)
                                }
                                for mem in related_memories
                            ]
                
                return {
                    "success": True,
                    "specialist_id": specialist_id,
                    "conversation_count": len(conversations),
                    "conversations": conversations,
                    "query_metadata": {
                        "limit": limit,
                        "context_id": context_id,
                        "total_memories_searched": len(memories),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
        except httpx.ConnectError:
            logger.error(f"Failed to connect to Engram at http://localhost:8004")
            return {
                "success": False,
                "error": "Engram service unavailable",
                "conversations": []
            }
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversations": []
            }
    
    async def configure_orchestration(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure AI orchestration settings with context-aware routing.
        
        This method implements a hierarchical routing strategy:
        1. Best-fit routing: Analyze request to determine optimal specialist
        2. Context-aware routing: Use conversation history/context
        3. Capability-based routing: Match required capabilities
        4. Load-based routing: Distribute work evenly
        5. Role-based routing: Default fallback
        
        Args:
            settings: Dictionary containing orchestration configuration:
                - routing_mode: 'best_fit', 'context_aware', 'capability', 'load_balanced', 'role_based'
                - fallback_chain: List of specialist IDs for fallback
                - context_weight: Weight for context-aware decisions (0.0-1.0)
                - load_threshold: Max requests before load balancing
                - custom_rules: List of custom routing rules
                
        Returns:
            Dictionary with success status and applied configuration
        """
        try:
            # Validate settings
            routing_mode = settings.get('routing_mode', 'best_fit')
            valid_modes = ['best_fit', 'context_aware', 'capability', 'load_balanced', 'role_based']
            
            if routing_mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid routing mode: {routing_mode}. Valid modes: {valid_modes}"
                }
            
            # Get current configuration from routing engine
            current_config = await self.routing_engine.get_configuration()
            
            # Build new configuration
            new_config = {
                "routing_mode": routing_mode,
                "fallback_chain": settings.get('fallback_chain', []),
                "context_weight": min(1.0, max(0.0, settings.get('context_weight', 0.5))),
                "load_threshold": settings.get('load_threshold', 100),
                "custom_rules": settings.get('custom_rules', []),
                "capability_requirements": settings.get('capability_requirements', {}),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Apply custom routing rules
            custom_rules = []
            for rule in settings.get('custom_rules', []):
                if self._validate_routing_rule(rule):
                    custom_rules.append({
                        "condition": rule.get('condition'),
                        "action": rule.get('action'),
                        "priority": rule.get('priority', 0),
                        "description": rule.get('description', '')
                    })
            
            new_config['custom_rules'] = custom_rules
            
            # Store configuration in the routing engine
            await self.routing_engine.update_configuration(new_config)
            
            # If context-aware routing is enabled, pre-load context weights
            if routing_mode == 'context_aware' or routing_mode == 'best_fit':
                await self._update_context_weights(new_config)
            
            # Log configuration change
            logger.info(f"Updated orchestration configuration: mode={routing_mode}, "
                       f"rules={len(custom_rules)}, fallback_chain={new_config['fallback_chain']}")
            
            return {
                "success": True,
                "configuration": new_config,
                "previous_config": current_config,
                "changes_applied": {
                    "routing_mode": routing_mode != current_config.get('routing_mode'),
                    "custom_rules": len(custom_rules),
                    "fallback_updated": new_config['fallback_chain'] != current_config.get('fallback_chain', [])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to configure orchestration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_routing_rule(self, rule: Dict[str, Any]) -> bool:
        """Validate a custom routing rule."""
        required_fields = ['condition', 'action']
        if not all(field in rule for field in required_fields):
            return False
        
        # Validate condition
        condition = rule['condition']
        valid_conditions = ['contains', 'matches', 'context_has', 'capability_required']
        if condition.get('type') not in valid_conditions:
            return False
        
        # Validate action
        action = rule['action']
        valid_actions = ['route_to', 'exclude', 'prefer', 'require_capability']
        if action.get('type') not in valid_actions:
            return False
        
        return True
    
    async def _update_context_weights(self, config: Dict[str, Any]):
        """Update context weights for context-aware routing."""
        try:
            # Get recent conversations from Engram
            all_ais = await self.discovery.list_ais()
            
            for ai in all_ais.get('ais', []):
                ai_id = ai['id']
                
                # Get conversation history
                history = await self.get_specialist_conversation_history(
                    ai_id, 
                    limit=20
                )
                
                if history['success'] and history['conversations']:
                    # Calculate context weight based on recent interactions
                    total_score = sum(
                        conv['metadata'].get('score', 0.0) 
                        for conv in history['conversations']
                    )
                    avg_score = total_score / len(history['conversations'])
                    
                    # Update routing engine with context weight
                    await self.routing_engine.update_specialist_weight(
                        ai_id,
                        context_weight=avg_score * config['context_weight']
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to update context weights: {e}")
    
    async def send_message_to_specialist_stream(self, specialist_id: str, message: str,
                                              context: Optional[Dict[str, Any]] = None,
                                              timeout: float = 30.0) -> AsyncIterator[Dict[str, Any]]:
        """Stream a message response from an AI specialist.
        
        This method provides real-time streaming responses from specialists,
        enabling progressive UI updates and reduced perceived latency.
        
        Args:
            specialist_id: ID of the specialist
            message: Message content
            context: Optional context
            timeout: Response timeout in seconds
            
        Yields:
            Dictionary chunks containing:
                - type: 'chunk', 'metadata', 'complete', 'error'
                - content: The text content (for chunks)
                - metadata: Enhanced metadata (tokens, reasoning depth, etc.)
        """
        try:
            # Get specialist info
            ai_info = await self.discovery.get_ai_info(specialist_id)
            if not ai_info:
                yield {
                    "type": "error",
                    "error": f"Specialist {specialist_id} not found"
                }
                return
            
            # Check if this is a socket-based AI
            if 'connection' in ai_info and ai_info['connection'].get('port'):
                # Stream via socket
                async for chunk in self._stream_via_socket(ai_info, message, context, timeout):
                    yield chunk
            else:
                # No streaming support for API-based specialists yet
                # Fall back to single response
                result = await self._send_via_api(specialist_id, message, context)
                
                if result['success']:
                    # Simulate streaming by chunking the response
                    content = result['response']
                    chunk_size = 50
                    
                    for i in range(0, len(content), chunk_size):
                        yield {
                            "type": "chunk",
                            "content": content[i:i+chunk_size],
                            "specialist_id": specialist_id
                        }
                        await asyncio.sleep(0.05)  # Small delay for effect
                    
                    yield {
                        "type": "complete",
                        "specialist_id": specialist_id,
                        "total_length": len(content)
                    }
                else:
                    yield {
                        "type": "error",
                        "error": result.get('error', 'Unknown error'),
                        "specialist_id": specialist_id
                    }
                    
        except Exception as e:
            logger.error(f"Streaming error for {specialist_id}: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "specialist_id": specialist_id
            }
    
    async def _stream_via_socket(self, ai_info: Dict[str, Any], message: str,
                                context: Optional[Dict[str, Any]] = None,
                                timeout: float = 30.0) -> AsyncIterator[Dict[str, Any]]:
        """Stream response via socket connection."""
        host = ai_info['connection'].get('host', 'localhost')
        port = ai_info['connection']['port']
        specialist_id = ai_info['id']
        
        try:
            from shared.ai.socket_client import AISocketClient
            
            client = AISocketClient(
                default_timeout=timeout,
                connection_timeout=2.0
            )
            
            chunk_count = 0
            total_tokens = 0
            
            async for chunk in client.send_message_stream(
                host=host,
                port=port,
                message=message,
                context=context,
                timeout=timeout
            ):
                chunk_count += 1
                
                # Estimate tokens
                if chunk.content:
                    tokens = len(chunk.content) // 4
                    total_tokens += tokens
                
                # Yield chunk with enhanced metadata
                if chunk.is_final:
                    yield {
                        "type": "complete",
                        "specialist_id": specialist_id,
                        "metadata": {
                            "total_chunks": chunk_count,
                            "total_tokens": total_tokens,
                            "model": chunk.metadata.get('model', ai_info.get('model')),
                            **chunk.metadata
                        }
                    }
                else:
                    yield {
                        "type": "chunk",
                        "content": chunk.content,
                        "specialist_id": specialist_id,
                        "metadata": {
                            "chunk_index": chunk_count,
                            "tokens_so_far": total_tokens,
                            **chunk.metadata
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Socket streaming error for {specialist_id}: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "specialist_id": specialist_id
            }
    
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