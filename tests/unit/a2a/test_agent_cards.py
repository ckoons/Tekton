"""
Unit tests for Agent Card and Registry in A2A Protocol v0.2.1
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from tekton.a2a.agent import AgentCard, AgentRegistry, AgentStatus


class TestAgentCard:
    """Test Agent Card functionality"""
    
    def test_create_agent_card(self):
        """Test creating an agent card"""
        card = AgentCard.create(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            capabilities=["test", "example"],
            supported_methods=["test.method1", "test.method2"]
        )
        
        assert card.id.startswith("agent-")
        assert card.name == "Test Agent"
        assert card.description == "A test agent"
        assert card.version == "1.0.0"
        assert card.capabilities == ["test", "example"]
        assert card.supported_methods == ["test.method1", "test.method2"]
        assert card.status == AgentStatus.IDLE
        assert card.protocol_version == "0.2.1"
    
    def test_agent_card_with_optional_fields(self):
        """Test creating an agent card with optional fields"""
        card = AgentCard.create(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            capabilities=["test"],
            supported_methods=["test.method"],
            author="Test Author",
            organization="Test Org",
            homepage="https://example.com",
            tags=["testing", "example"],
            endpoint="http://localhost:8000"
        )
        
        assert card.author == "Test Author"
        assert card.organization == "Test Org"
        assert card.homepage == "https://example.com"
        assert card.tags == ["testing", "example"]
        assert card.endpoint == "http://localhost:8000"
    
    def test_update_heartbeat(self):
        """Test updating agent heartbeat"""
        card = AgentCard.create(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            capabilities=["test"],
            supported_methods=["test.method"]
        )
        
        # Initially no heartbeat
        assert card.last_heartbeat is None
        
        # Update heartbeat
        card.update_heartbeat()
        assert card.last_heartbeat is not None
        assert isinstance(card.last_heartbeat, datetime)
    
    def test_is_online(self):
        """Test checking if agent is online"""
        card = AgentCard.create(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            capabilities=["test"],
            supported_methods=["test.method"]
        )
        
        # Not online without heartbeat
        assert not card.is_online()
        
        # Online after heartbeat
        card.update_heartbeat()
        assert card.is_online()
        
        # Not online if heartbeat is old
        card.last_heartbeat = datetime.utcnow() - timedelta(seconds=120)
        assert not card.is_online(timeout_seconds=60)
        assert card.is_online(timeout_seconds=180)
    
    def test_supports_capability(self):
        """Test checking capability support"""
        card = AgentCard.create(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            capabilities=["test", "example", "demo"],
            supported_methods=["test.method"]
        )
        
        assert card.supports_capability("test")
        assert card.supports_capability("example")
        assert card.supports_capability("demo")
        assert not card.supports_capability("missing")
    
    def test_supports_method(self):
        """Test checking method support"""
        card = AgentCard.create(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            capabilities=["test"],
            supported_methods=["test.method1", "test.method2", "example.method"]
        )
        
        assert card.supports_method("test.method1")
        assert card.supports_method("test.method2")
        assert card.supports_method("example.method")
        assert not card.supports_method("missing.method")


class TestAgentRegistry:
    """Test Agent Registry functionality"""
    
    def create_test_agent(self, name: str, capabilities: List[str] = None) -> AgentCard:
        """Helper to create a test agent"""
        return AgentCard.create(
            name=name,
            description=f"{name} description",
            version="1.0.0",
            capabilities=capabilities or ["test"],
            supported_methods=["test.method"]
        )
    
    def test_register_agent(self):
        """Test registering an agent"""
        registry = AgentRegistry()
        agent = self.create_test_agent("Test Agent")
        
        # Register agent
        registry.register(agent)
        
        # Check agent is registered
        assert agent.id in registry._agents
        assert agent.status == AgentStatus.ACTIVE
        assert agent.last_heartbeat is not None
    
    def test_unregister_agent(self):
        """Test unregistering an agent"""
        registry = AgentRegistry()
        agent = self.create_test_agent("Test Agent")
        
        # Register and then unregister
        registry.register(agent)
        removed_agent = registry.unregister(agent.id)
        
        assert removed_agent == agent
        assert agent.id not in registry._agents
    
    def test_unregister_nonexistent_agent(self):
        """Test unregistering a non-existent agent returns None"""
        registry = AgentRegistry()
        
        removed_agent = registry.unregister("nonexistent-id")
        assert removed_agent is None
    
    def test_get_agent(self):
        """Test getting an agent by ID"""
        registry = AgentRegistry()
        agent = self.create_test_agent("Test Agent")
        
        registry.register(agent)
        retrieved = registry.get(agent.id)
        
        assert retrieved == agent
    
    def test_get_nonexistent_agent(self):
        """Test getting a non-existent agent returns None"""
        registry = AgentRegistry()
        
        retrieved = registry.get("nonexistent-id")
        assert retrieved is None
    
    def test_list_all_agents(self):
        """Test listing all agents"""
        registry = AgentRegistry()
        
        # Register multiple agents
        agents = [
            self.create_test_agent("Agent 1"),
            self.create_test_agent("Agent 2"),
            self.create_test_agent("Agent 3")
        ]
        
        for agent in agents:
            registry.register(agent)
        
        all_agents = registry.list_all()
        assert len(all_agents) == 3
        assert all(agent in all_agents for agent in agents)
    
    def test_list_online_agents(self):
        """Test listing only online agents"""
        registry = AgentRegistry(heartbeat_timeout=60)
        
        # Register agents
        online_agent = self.create_test_agent("Online Agent")
        offline_agent = self.create_test_agent("Offline Agent")
        
        registry.register(online_agent)
        registry.register(offline_agent)
        
        # Make one agent offline
        offline_agent.last_heartbeat = datetime.utcnow() - timedelta(seconds=120)
        
        online_agents = registry.list_online()
        assert len(online_agents) == 1
        assert online_agents[0] == online_agent
    
    def test_find_by_capability(self):
        """Test finding agents by capability"""
        registry = AgentRegistry()
        
        # Register agents with different capabilities
        agent1 = self.create_test_agent("Agent 1", ["capability1", "capability2"])
        agent2 = self.create_test_agent("Agent 2", ["capability2", "capability3"])
        agent3 = self.create_test_agent("Agent 3", ["capability3", "capability4"])
        
        for agent in [agent1, agent2, agent3]:
            registry.register(agent)
        
        # Find by capability
        agents_with_cap2 = registry.find_by_capability("capability2")
        assert len(agents_with_cap2) == 2
        assert agent1 in agents_with_cap2
        assert agent2 in agents_with_cap2
        
        agents_with_cap4 = registry.find_by_capability("capability4")
        assert len(agents_with_cap4) == 1
        assert agent3 in agents_with_cap4
        
        agents_with_missing = registry.find_by_capability("missing")
        assert len(agents_with_missing) == 0
    
    def test_find_by_method(self):
        """Test finding agents by supported method"""
        registry = AgentRegistry()
        
        # Create agents with specific methods
        agent1 = AgentCard.create(
            name="Agent 1",
            description="Test agent 1",
            version="1.0.0",
            capabilities=["test"],
            supported_methods=["method.a", "method.b"]
        )
        
        agent2 = AgentCard.create(
            name="Agent 2",
            description="Test agent 2",
            version="1.0.0",
            capabilities=["test"],
            supported_methods=["method.b", "method.c"]
        )
        
        registry.register(agent1)
        registry.register(agent2)
        
        # Find by method
        agents_with_method_b = registry.find_by_method("method.b")
        assert len(agents_with_method_b) == 2
        
        agents_with_method_a = registry.find_by_method("method.a")
        assert len(agents_with_method_a) == 1
        assert agents_with_method_a[0] == agent1
    
    def test_find_by_tags(self):
        """Test finding agents by tags"""
        registry = AgentRegistry()
        
        # Create agents with tags
        agent1 = self.create_test_agent("Agent 1")
        agent1.tags = ["tag1", "tag2"]
        
        agent2 = self.create_test_agent("Agent 2")
        agent2.tags = ["tag2", "tag3"]
        
        agent3 = self.create_test_agent("Agent 3")
        agent3.tags = ["tag3", "tag4"]
        
        for agent in [agent1, agent2, agent3]:
            registry.register(agent)
        
        # Find by tags
        agents_with_tag2 = registry.find_by_tags(["tag2"])
        assert len(agents_with_tag2) == 2
        assert agent1 in agents_with_tag2
        assert agent2 in agents_with_tag2
        
        agents_with_tags = registry.find_by_tags(["tag1", "tag4"])
        assert len(agents_with_tags) == 2
        assert agent1 in agents_with_tags
        assert agent3 in agents_with_tags
    
    def test_update_heartbeat(self):
        """Test updating agent heartbeat"""
        registry = AgentRegistry()
        agent = self.create_test_agent("Test Agent")
        
        registry.register(agent)
        initial_heartbeat = agent.last_heartbeat
        
        # Wait a bit and update heartbeat
        import time
        time.sleep(0.1)
        
        success = registry.update_heartbeat(agent.id)
        assert success
        assert agent.last_heartbeat > initial_heartbeat
    
    def test_update_heartbeat_nonexistent(self):
        """Test updating heartbeat for non-existent agent"""
        registry = AgentRegistry()
        
        success = registry.update_heartbeat("nonexistent-id")
        assert not success
    
    def test_update_status(self):
        """Test updating agent status"""
        registry = AgentRegistry()
        agent = self.create_test_agent("Test Agent")
        
        registry.register(agent)
        assert agent.status == AgentStatus.ACTIVE
        
        # Update status
        success = registry.update_status(agent.id, AgentStatus.BUSY)
        assert success
        assert agent.status == AgentStatus.BUSY
        
        success = registry.update_status(agent.id, AgentStatus.ERROR)
        assert success
        assert agent.status == AgentStatus.ERROR
    
    def test_cleanup_offline(self):
        """Test cleaning up offline agents"""
        registry = AgentRegistry(heartbeat_timeout=60)
        
        # Register agents
        online_agent = self.create_test_agent("Online Agent")
        offline_agent1 = self.create_test_agent("Offline Agent 1")
        offline_agent2 = self.create_test_agent("Offline Agent 2")
        
        for agent in [online_agent, offline_agent1, offline_agent2]:
            registry.register(agent)
        
        # Make some agents offline
        offline_agent1.last_heartbeat = datetime.utcnow() - timedelta(seconds=120)
        offline_agent2.last_heartbeat = datetime.utcnow() - timedelta(seconds=180)
        
        # Cleanup offline agents
        removed_ids = registry.cleanup_offline()
        
        assert len(removed_ids) == 2
        assert offline_agent1.id in removed_ids
        assert offline_agent2.id in removed_ids
        
        # Check remaining agents
        remaining = registry.list_all()
        assert len(remaining) == 1
        assert remaining[0] == online_agent