"""Ergon component implementation using StandardComponentBase."""
import logging
import os
from typing import List, Dict, Any
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase
from ergon.core.database.engine import get_db_session, init_db
from ergon.core.memory.service import MemoryService
from ergon.core.a2a_client import A2AClient
from ergon.core.agents.generator import AgentGenerator
from ergon.core.agents.runner import AgentRunner
from ergon.utils.config.settings import settings

logger = logging.getLogger(__name__)

class ErgonComponent(StandardComponentBase):
    """Ergon agent system component with specialized task execution capabilities."""
    
    def __init__(self):
        super().__init__(component_name="ergon", version="0.1.0")
        # Component-specific attributes - initialized in proper order
        self.db_path = None
        self.memory_service = None
        self.terminal_memory = None
        self.a2a_client = None
        self.agent_generator = None
        self.agent_runner = None
        self.mcp_bridge = None
        
    async def _component_specific_init(self):
        """Initialize Ergon-specific services in dependency order."""
        # Critical components in proper initialization order
        
        # 1. Database first (other services depend on it)
        data_dir = Path(self.global_config.get_data_dir("ergon"))
        self.db_path = data_dir / "ergon.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update settings database path and initialize if needed
        settings.database_url = f"sqlite:///{self.db_path}"
        if not os.path.exists(str(self.db_path)):
            init_db()
            logger.info(f"Database initialized at {self.db_path}")
        else:
            logger.info(f"Database exists at {self.db_path}")
        
        # 2. Memory services next (agents need memory)
        self.memory_service = MemoryService()
        self.terminal_memory = MemoryService()  # Separate instance for terminal
        logger.info("Memory services initialized")
        
        # 3. A2A client (for inter-agent communication)
        try:
            self.a2a_client = A2AClient()
            # A2A client may need async initialization
            if hasattr(self.a2a_client, 'initialize'):
                await self.a2a_client.initialize()
            logger.info("A2A client initialized")
        except Exception as e:
            logger.warning(f"A2A client initialization failed: {e}")
            self.a2a_client = None
        
        # 4. Agent services last (depend on database, memory, and A2A)
        try:
            self.agent_generator = AgentGenerator()
            logger.info("Agent generator initialized")
        except Exception as e:
            logger.warning(f"Agent generator initialization failed: {e}")
            self.agent_generator = None
        
        try:
            # AgentRunner may need additional configuration
            self.agent_runner = AgentRunner
            logger.info("Agent runner initialized")
        except Exception as e:
            logger.warning(f"Agent runner initialization failed: {e}")
            self.agent_runner = None
        
        logger.info("Ergon component core initialization completed")
    
    async def _component_specific_cleanup(self):
        """Cleanup Ergon-specific resources in reverse dependency order."""
        
        # Cleanup agent services first
        if self.agent_runner:
            try:
                # AgentRunner cleanup if it has cleanup methods
                if hasattr(self.agent_runner, 'cleanup'):
                    await self.agent_runner.cleanup()
                logger.info("Agent runner cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up agent runner: {e}")
        
        if self.agent_generator:
            try:
                # AgentGenerator cleanup if it has cleanup methods
                if hasattr(self.agent_generator, 'cleanup'):
                    await self.agent_generator.cleanup()
                logger.info("Agent generator cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up agent generator: {e}")
        
        # Cleanup A2A client
        if self.a2a_client:
            try:
                if hasattr(self.a2a_client, 'cleanup'):
                    await self.a2a_client.cleanup()
                elif hasattr(self.a2a_client, 'close'):
                    await self.a2a_client.close()
                logger.info("A2A client cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up A2A client: {e}")
        
        # Cleanup MCP bridge
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("MCP bridge cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP bridge: {e}")
        
        # Cleanup memory services
        if self.memory_service:
            try:
                if hasattr(self.memory_service, 'cleanup'):
                    await self.memory_service.cleanup()
                logger.info("Memory service cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up memory service: {e}")
        
        if self.terminal_memory:
            try:
                if hasattr(self.terminal_memory, 'cleanup'):
                    await self.terminal_memory.cleanup()
                logger.info("Terminal memory cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up terminal memory: {e}")
        
        # Database connections are handled by the database engine
        logger.info("Database cleanup completed")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        capabilities = [
            "agent_creation",
            "agent_execution", 
            "memory_integration",
            "specialized_tasks"
        ]
        
        if self.a2a_client:
            capabilities.append("a2a_communication")
        
        if self.mcp_bridge:
            capabilities.append("mcp_bridge")
            
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "Agent system for specialized task execution",
            "database": str(self.db_path) if self.db_path else None,
            "category": "execution",
            "a2a_enabled": bool(self.a2a_client),
            "memory_enabled": bool(self.memory_service),
            "agent_generator_enabled": bool(self.agent_generator),
            "mcp_enabled": bool(self.mcp_bridge)
        }
        
        return metadata


# Convenience functions for backward compatibility during migration
def get_memory_service():
    """Get memory service through component (compatibility function)."""
    try:
        # This will be updated to access through app.state.component
        logger.warning("Using compatibility get_memory_service() - consider accessing through component directly")
        # For now, return a new instance as fallback
        return MemoryService()
    except Exception as e:
        logger.warning(f"Could not access memory service through component: {e}")
        return MemoryService()

def get_terminal_memory():
    """Get terminal memory through component (compatibility function)."""
    try:
        # This will be updated to access through app.state.component
        logger.warning("Using compatibility get_terminal_memory() - consider accessing through component directly")
        # For now, return a new instance as fallback
        return MemoryService()
    except Exception as e:
        logger.warning(f"Could not access terminal memory through component: {e}")
        return MemoryService()

def get_a2a_client():
    """Get A2A client through component (compatibility function)."""
    try:
        # This will be updated to access through app.state.component
        logger.warning("Using compatibility get_a2a_client() - consider accessing through component directly")
        # For now, return None as fallback
        return None
    except Exception as e:
        logger.warning(f"Could not access A2A client through component: {e}")
        return None