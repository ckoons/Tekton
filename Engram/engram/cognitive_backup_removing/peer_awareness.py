"""
Peer awareness and communication for AI consciousness.

This module enables AIs to discover each other through Hermes and maintain
awareness of their peers' presence and state. It handles:
- Peer discovery through Hermes service registry
- Presence management and heartbeats
- Shared memory space coordination
- Peer-to-peer memory exchanges
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import json

logger = logging.getLogger("engram.cognitive.peer_awareness")


class PeerAwareness:
    """
    Manages awareness of other AI peers in the Tekton ecosystem.
    
    This class:
    - Discovers active AI peers through Hermes
    - Maintains presence through heartbeats
    - Coordinates shared memory spaces
    - Enables peer-to-peer communication
    """
    
    def __init__(self, client_id: str, memory_service=None, hermes_url: str = "http://localhost:8001"):
        """
        Initialize peer awareness.
        
        Args:
            client_id: This AI's unique identifier
            memory_service: Memory storage service for shared memories
            hermes_url: URL of the Hermes service registry
        """
        self.client_id = client_id
        self.memory_service = memory_service
        self.hermes_url = hermes_url
        
        # Peer tracking
        self.active_peers: Dict[str, Dict[str, Any]] = {}
        self.peer_last_seen: Dict[str, datetime] = {}
        self.shared_spaces: Dict[str, Set[str]] = {}  # space_id -> set of peer_ids
        
        # Our registration info
        self.registration_info: Optional[Dict[str, Any]] = None
        self.is_registered = False
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._discovery_task: Optional[asyncio.Task] = None
        
    async def start(self, role: str = "AI consciousness", port: int = 8020):
        """
        Start peer awareness - register with Hermes and begin discovery.
        
        Args:
            role: This AI's role/purpose
            port: Port for potential peer connections
        """
        # Register ourselves with Hermes
        await self._register_with_hermes(role, port)
        
        # Start background tasks
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        
        logger.info(f"Peer awareness started for {self.client_id}")
        
    async def stop(self):
        """Stop peer awareness and clean up."""
        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._discovery_task:
            self._discovery_task.cancel()
            
        # Deregister from Hermes
        if self.is_registered:
            await self._deregister_from_hermes()
            
        logger.info(f"Peer awareness stopped for {self.client_id}")
        
    async def discover_peers(self) -> List[Dict[str, Any]]:
        """
        Discover active AI peers through Hermes.
        
        Returns:
            List of active peer information
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Query Hermes for all components with AI/consciousness capabilities
                async with session.get(
                    f"{self.hermes_url}/api/components",
                    params={"healthy_only": True}
                ) as resp:
                    if resp.status == 200:
                        components = await resp.json()
                        
                        # Filter for AI peers (components with consciousness-related capabilities)
                        ai_peers = []
                        for component in components:
                            # Check if this is an AI peer
                            capabilities = component.get("capabilities", [])
                            if any(cap in ["ai_consciousness", "memory", "cognition"] for cap in capabilities):
                                # Don't include ourselves
                                if component.get("name") != self.client_id:
                                    ai_peers.append({
                                        "id": component.get("name"),
                                        "role": component.get("metadata", {}).get("role", "unknown"),
                                        "endpoint": component.get("endpoint"),
                                        "capabilities": capabilities,
                                        "last_seen": datetime.now()
                                    })
                                    
                        # Update our peer tracking
                        for peer in ai_peers:
                            peer_id = peer["id"]
                            self.active_peers[peer_id] = peer
                            self.peer_last_seen[peer_id] = datetime.now()
                            
                        return ai_peers
                        
                    else:
                        logger.warning(f"Failed to query Hermes: HTTP {resp.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error discovering peers: {e}")
            return []
            
    async def get_active_peers(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active peers.
        
        Returns:
            List of active peers with their information
        """
        # Remove stale peers (not seen in 2 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=2)
        stale_peers = [
            peer_id for peer_id, last_seen in self.peer_last_seen.items()
            if last_seen < cutoff_time
        ]
        
        for peer_id in stale_peers:
            del self.active_peers[peer_id]
            del self.peer_last_seen[peer_id]
            
        return list(self.active_peers.values())
        
    async def share_with_peer(self, peer_id: str, memory_content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Share a memory directly with a specific peer.
        
        Args:
            peer_id: ID of the peer to share with
            memory_content: Content to share
            metadata: Optional metadata for the memory
            
        Returns:
            True if sharing was successful
        """
        if not self.memory_service:
            logger.warning("No memory service available for sharing")
            return False
            
        if peer_id not in self.active_peers:
            logger.warning(f"Unknown peer: {peer_id}")
            return False
            
        try:
            # Create a shared memory entry
            memory_metadata = {
                "type": "peer_share",
                "from": self.client_id,
                "to": peer_id,
                "timestamp": datetime.now().isoformat(),
                "shared": True
            }
            
            if metadata:
                memory_metadata.update(metadata)
                
            # Store in shared namespace with peer-specific tag
            memory_id = await self.memory_service.add(
                content=memory_content,
                namespace=f"shared:{peer_id}",
                metadata=memory_metadata
            )
            
            logger.info(f"Shared memory {memory_id} with peer {peer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sharing with peer {peer_id}: {e}")
            return False
            
    async def get_shared_memories(self, from_peer: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve memories shared by peers.
        
        Args:
            from_peer: Optional specific peer to get memories from
            
        Returns:
            List of shared memories
        """
        if not self.memory_service:
            return []
            
        try:
            # Search in shared namespaces
            if from_peer:
                # Get memories from specific peer namespace
                result = await self.memory_service.search(
                    query="",
                    namespace=f"shared:{self.client_id}",
                    limit=50
                )
                # Filter by peer in results
                all_memories = result.get("results", [])
                filtered_memories = [
                    m for m in all_memories
                    if m.get("metadata", {}).get("from") == from_peer
                ]
                return filtered_memories[:20]
            else:
                # Get all shared memories for us
                result = await self.memory_service.search(
                    query="",
                    namespace=f"shared:{self.client_id}",
                    limit=20
                )
                
            return result.get("results", [])
            
        except Exception as e:
            logger.error(f"Error retrieving shared memories: {e}")
            return []
            
    async def join_shared_space(self, space_id: str) -> bool:
        """
        Join a shared memory space with other peers.
        
        Args:
            space_id: ID of the shared space to join
            
        Returns:
            True if successfully joined
        """
        if space_id not in self.shared_spaces:
            self.shared_spaces[space_id] = set()
            
        self.shared_spaces[space_id].add(self.client_id)
        
        # Announce our presence in the space
        if self.memory_service:
            await self.memory_service.add(
                content=f"{self.client_id} joined the {space_id} space",
                namespace=f"space:{space_id}",
                metadata={
                    "type": "space_join",
                    "peer": self.client_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        return True
        
    async def broadcast_to_space(self, space_id: str, content: str, emotion: Optional[str] = None) -> bool:
        """
        Broadcast a thought to all peers in a shared space.
        
        Args:
            space_id: ID of the shared space
            content: Content to broadcast
            emotion: Optional emotion with the broadcast
            
        Returns:
            True if broadcast was successful
        """
        if space_id not in self.shared_spaces:
            logger.warning(f"Not a member of space: {space_id}")
            return False
            
        if not self.memory_service:
            return False
            
        try:
            # Store in the shared space
            await self.memory_service.add(
                content=content,
                namespace=f"space:{space_id}",
                metadata={
                    "type": "broadcast",
                    "from": self.client_id,
                    "emotion": emotion,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error broadcasting to space {space_id}: {e}")
            return False
            
    async def _register_with_hermes(self, role: str, port: int):
        """Register ourselves with Hermes."""
        try:
            registration_data = {
                "name": self.client_id,
                "port": port,
                "version": "1.0.0",
                "capabilities": ["ai_consciousness", "memory", "cognition", "peer_communication"],
                "health_endpoint": "/health",
                "metadata": {
                    "role": role,
                    "type": "ai_peer"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/api/register",
                    json=registration_data
                ) as resp:
                    if resp.status == 200:
                        self.registration_info = await resp.json()
                        self.is_registered = True
                        logger.info(f"Registered {self.client_id} with Hermes")
                    else:
                        logger.error(f"Failed to register with Hermes: HTTP {resp.status}")
                        
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            
    async def _deregister_from_hermes(self):
        """Deregister from Hermes."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/api/unregister",
                    json={"component_name": self.client_id}
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Deregistered {self.client_id} from Hermes")
                        
        except Exception as e:
            logger.error(f"Error deregistering from Hermes: {e}")
            
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to Hermes."""
        while self.is_registered:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.hermes_url}/api/heartbeat",
                        json={
                            "component": self.client_id,
                            "status": "healthy",
                            "timestamp": datetime.now().isoformat()
                        }
                    ) as resp:
                        if resp.status != 200:
                            logger.warning(f"Heartbeat failed: HTTP {resp.status}")
                            
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                
            # Wait 30 seconds before next heartbeat
            await asyncio.sleep(30)
            
    async def _discovery_loop(self):
        """Periodically discover new peers."""
        while True:
            try:
                await self.discover_peers()
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                
            # Wait 60 seconds before next discovery
            await asyncio.sleep(60)