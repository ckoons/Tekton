"""
Discovery Service for A2A Protocol v2

Implements agent discovery functionality with capability-based search.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from tekton.models.base import TektonBaseModel
from .agent import AgentCard, AgentRegistry, AgentStatus


class AgentQuery(TektonBaseModel):
    """Query parameters for agent discovery"""
    
    # Search criteria
    capabilities: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[List[AgentStatus]] = None
    
    # Filtering
    name_pattern: Optional[str] = None
    organization: Optional[str] = None
    
    # Pagination
    limit: int = 100
    offset: int = 0
    
    # Sorting
    sort_by: str = "name"  # name, status, last_heartbeat
    sort_order: str = "asc"  # asc, desc


class DiscoveryResult(TektonBaseModel):
    """Result of a discovery query"""
    
    agents: List[AgentCard]
    total_count: int
    query: AgentQuery
    timestamp: datetime = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class DiscoveryService:
    """
    Service for discovering agents in the A2A network.
    
    Provides advanced search and filtering capabilities.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
    
    def discover(self, query: AgentQuery) -> DiscoveryResult:
        """
        Discover agents based on query parameters.
        
        Supports filtering by capabilities, methods, tags, status, and more.
        """
        # Start with all online agents
        agents = self.registry.list_online()
        
        # Apply filters
        agents = self._filter_by_capabilities(agents, query.capabilities)
        agents = self._filter_by_methods(agents, query.methods)
        agents = self._filter_by_tags(agents, query.tags)
        agents = self._filter_by_status(agents, query.status)
        agents = self._filter_by_name(agents, query.name_pattern)
        agents = self._filter_by_organization(agents, query.organization)
        
        # Sort results
        agents = self._sort_agents(agents, query.sort_by, query.sort_order)
        
        # Get total count before pagination
        total_count = len(agents)
        
        # Apply pagination
        start = query.offset
        end = start + query.limit
        agents = agents[start:end]
        
        return DiscoveryResult(
            agents=agents,
            total_count=total_count,
            query=query
        )
    
    def find_agent_for_method(self, method: str) -> Optional[AgentCard]:
        """Find the best agent to handle a specific method"""
        agents = self.registry.find_by_method(method)
        
        if not agents:
            return None
        
        # Return the least busy agent
        agents.sort(key=lambda a: (
            0 if a.status == AgentStatus.IDLE else
            1 if a.status == AgentStatus.ACTIVE else
            2
        ))
        
        return agents[0]
    
    def find_agents_for_capability(self, capability: str) -> List[AgentCard]:
        """Find all agents that support a specific capability"""
        return self.registry.find_by_capability(capability)
    
    def get_capability_map(self) -> Dict[str, List[str]]:
        """Get a map of capabilities to agent IDs"""
        capability_map: Dict[str, List[str]] = {}
        
        for agent in self.registry.list_online():
            for capability in agent.capabilities:
                if capability not in capability_map:
                    capability_map[capability] = []
                capability_map[capability].append(agent.id)
        
        return capability_map
    
    def get_method_map(self) -> Dict[str, List[str]]:
        """Get a map of methods to agent IDs"""
        method_map: Dict[str, List[str]] = {}
        
        for agent in self.registry.list_online():
            for method in agent.supported_methods:
                if method not in method_map:
                    method_map[method] = []
                method_map[method].append(agent.id)
        
        return method_map
    
    # Filter methods
    
    def _filter_by_capabilities(
        self,
        agents: List[AgentCard],
        capabilities: Optional[List[str]]
    ) -> List[AgentCard]:
        """Filter agents by required capabilities"""
        if not capabilities:
            return agents
        
        return [
            agent for agent in agents
            if all(agent.supports_capability(cap) for cap in capabilities)
        ]
    
    def _filter_by_methods(
        self,
        agents: List[AgentCard],
        methods: Optional[List[str]]
    ) -> List[AgentCard]:
        """Filter agents by supported methods"""
        if not methods:
            return agents
        
        return [
            agent for agent in agents
            if any(agent.supports_method(method) for method in methods)
        ]
    
    def _filter_by_tags(
        self,
        agents: List[AgentCard],
        tags: Optional[List[str]]
    ) -> List[AgentCard]:
        """Filter agents by tags"""
        if not tags:
            return agents
        
        return [
            agent for agent in agents
            if any(tag in agent.tags for tag in tags)
        ]
    
    def _filter_by_status(
        self,
        agents: List[AgentCard],
        statuses: Optional[List[AgentStatus]]
    ) -> List[AgentCard]:
        """Filter agents by status"""
        if not statuses:
            return agents
        
        return [
            agent for agent in agents
            if agent.status in statuses
        ]
    
    def _filter_by_name(
        self,
        agents: List[AgentCard],
        pattern: Optional[str]
    ) -> List[AgentCard]:
        """Filter agents by name pattern (case-insensitive substring match)"""
        if not pattern:
            return agents
        
        pattern_lower = pattern.lower()
        return [
            agent for agent in agents
            if pattern_lower in agent.name.lower()
        ]
    
    def _filter_by_organization(
        self,
        agents: List[AgentCard],
        organization: Optional[str]
    ) -> List[AgentCard]:
        """Filter agents by organization"""
        if not organization:
            return agents
        
        return [
            agent for agent in agents
            if agent.organization == organization
        ]
    
    def _sort_agents(
        self,
        agents: List[AgentCard],
        sort_by: str,
        sort_order: str
    ) -> List[AgentCard]:
        """Sort agents by specified field"""
        reverse = sort_order == "desc"
        
        if sort_by == "name":
            agents.sort(key=lambda a: a.name.lower(), reverse=reverse)
        elif sort_by == "status":
            # Sort by status priority
            status_priority = {
                AgentStatus.IDLE: 0,
                AgentStatus.ACTIVE: 1,
                AgentStatus.BUSY: 2,
                AgentStatus.ERROR: 3,
                AgentStatus.OFFLINE: 4
            }
            agents.sort(
                key=lambda a: status_priority.get(a.status, 5),
                reverse=reverse
            )
        elif sort_by == "last_heartbeat":
            agents.sort(
                key=lambda a: a.last_heartbeat or datetime.min,
                reverse=reverse
            )
        
        return agents