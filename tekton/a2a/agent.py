"""
Agent Management for A2A Protocol v2

Implements Agent Cards, Agent Registry, and Agent Status tracking according
to the A2A Protocol v0.2.1 specification.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4

from tekton.models.base import TektonBaseModel


class AgentStatus(str, Enum):
    """Agent availability status"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class AgentCard(TektonBaseModel):
    """
    Agent Card according to A2A Protocol v0.2.1 specification.
    
    Describes an agent's identity, capabilities, and metadata.
    """
    
    # Required fields
    id: str
    name: str
    description: str
    version: str
    
    # Capabilities
    capabilities: List[str]
    supported_methods: List[str]
    
    # Optional metadata
    author: Optional[str] = None
    organization: Optional[str] = None
    homepage: Optional[str] = None
    tags: List[str] = []
    
    # Runtime information
    status: AgentStatus = AgentStatus.IDLE
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    # A2A specific
    endpoint: Optional[str] = None
    protocol_version: str = "0.2.1"
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        version: str,
        capabilities: List[str],
        supported_methods: List[str],
        **kwargs
    ) -> 'AgentCard':
        """Create a new Agent Card with generated ID"""
        return cls(
            id=f"agent-{uuid4()}",
            name=name,
            description=description,
            version=version,
            capabilities=capabilities,
            supported_methods=supported_methods,
            **kwargs
        )
    
    def update_heartbeat(self) -> None:
        """Update the last heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow()
    
    def is_online(self, timeout_seconds: int = 60) -> bool:
        """Check if agent is considered online based on heartbeat"""
        if self.last_heartbeat is None:
            return False
        
        elapsed = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return elapsed < timeout_seconds
    
    def supports_capability(self, capability: str) -> bool:
        """Check if agent supports a specific capability"""
        return capability in self.capabilities
    
    def supports_method(self, method: str) -> bool:
        """Check if agent supports a specific JSON-RPC method"""
        return method in self.supported_methods


class AgentRegistry:
    """
    Registry for managing agents in the A2A system.
    
    Provides registration, discovery, and health monitoring for agents.
    """
    
    def __init__(self, heartbeat_timeout: int = 60):
        self._agents: Dict[str, AgentCard] = {}
        self._heartbeat_timeout = heartbeat_timeout
    
    def register(self, agent: AgentCard) -> None:
        """Register an agent in the registry"""
        agent.update_heartbeat()
        agent.status = AgentStatus.ACTIVE
        self._agents[agent.id] = agent
    
    def unregister(self, agent_id: str) -> Optional[AgentCard]:
        """Unregister an agent from the registry"""
        return self._agents.pop(agent_id, None)
    
    def get(self, agent_id: str) -> Optional[AgentCard]:
        """Get an agent by ID"""
        return self._agents.get(agent_id)
    
    def list_all(self) -> List[AgentCard]:
        """List all registered agents"""
        return list(self._agents.values())
    
    def list_online(self) -> List[AgentCard]:
        """List all online agents"""
        return [
            agent for agent in self._agents.values()
            if agent.is_online(self._heartbeat_timeout)
        ]
    
    def find_by_capability(self, capability: str) -> List[AgentCard]:
        """Find agents that support a specific capability"""
        return [
            agent for agent in self._agents.values()
            if agent.supports_capability(capability) and agent.is_online(self._heartbeat_timeout)
        ]
    
    def find_by_method(self, method: str) -> List[AgentCard]:
        """Find agents that support a specific JSON-RPC method"""
        return [
            agent for agent in self._agents.values()
            if agent.supports_method(method) and agent.is_online(self._heartbeat_timeout)
        ]
    
    def find_by_tags(self, tags: List[str]) -> List[AgentCard]:
        """Find agents that have any of the specified tags"""
        return [
            agent for agent in self._agents.values()
            if any(tag in agent.tags for tag in tags) and agent.is_online(self._heartbeat_timeout)
        ]
    
    def update_heartbeat(self, agent_id: str) -> bool:
        """Update an agent's heartbeat timestamp"""
        agent = self._agents.get(agent_id)
        if agent:
            agent.update_heartbeat()
            return True
        return False
    
    def update_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update an agent's status"""
        agent = self._agents.get(agent_id)
        if agent:
            agent.status = status
            return True
        return False
    
    def cleanup_offline(self) -> List[str]:
        """Remove offline agents and return their IDs"""
        offline_ids = [
            agent_id for agent_id, agent in self._agents.items()
            if not agent.is_online(self._heartbeat_timeout)
        ]
        
        for agent_id in offline_ids:
            self._agents.pop(agent_id)
        
        return offline_ids