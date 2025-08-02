"""Ergon component implementation using StandardComponentBase.

Ergon v2 is Tekton's CI-in-the-loop reusability expert and autonomous development orchestrator.
It catalogs, analyzes, configures, and autonomously builds solutions while learning from 
patterns to automate development expertise.
"""
import logging
import os
from typing import List, Dict, Any
from pathlib import Path
from enum import Enum

from shared.utils.standard_component import StandardComponentBase
from .database.engine import get_db_session, init_db
from .memory.service import MemoryService
from .a2a_client import A2AClient
from .agents.generator import AgentGenerator
from .agents.runner import AgentRunner
from .mcp.tool_discovery import MCPToolDiscovery
from .repository import SolutionRepository
from .memory.workflow_memory import WorkflowMemory
from ..utils.config.settings import settings
from landmarks import architecture_decision, state_checkpoint, danger_zone, integration_point, performance_boundary

logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Levels of autonomy for Ergon's CI-in-the-loop operations."""
    ADVISORY = "advisory"        # Just recommendations
    ASSISTED = "assisted"        # User approves each step  
    GUIDED = "guided"           # User approves major decisions
    AUTONOMOUS = "autonomous"    # Full autonomy within sprint

@architecture_decision(
    title="CI-in-the-Loop Architecture",
    rationale="Transform from human-in-the-loop to CI-in-the-loop development, enabling 50x productivity gains by automating Casey's expertise",
    alternatives_considered=["Traditional agent builder", "Simple registry", "Manual configuration only"],
    decided_by="Casey"
)
@state_checkpoint(
    title="Ergon Workflow Memory State",
    state_type="persistent",
    persistence=True,
    consistency_requirements="Workflow patterns and decisions must be preserved across sessions for learning",
    recovery_strategy="Restore from PostgreSQL with JSONB fields for flexible evolution"
)
@danger_zone(
    title="Autonomous Development Authority",
    risk_level="high",
    risks=["Autonomous code generation", "Direct repository modification", "Automatic dependency installation"],
    mitigations=["Progressive autonomy levels", "User approval workflows", "Full audit trails", "Sandbox testing"],
    review_required=True
)
@integration_point(
    title="Multi-CI Orchestration",
    target_component="All Tekton components",
    protocol="MCP and Socket communication",
    data_flow="Ergon -> MCP/Socket -> Other CIs -> Results -> Ergon learning"
)
@performance_boundary(
    title="GitHub Analysis Performance",
    sla="<5s for repository scan, 10 repos/minute throughput",
    metrics={"memory": "2GB", "cpu": "2 cores", "cache_ttl": "24h"},
    optimization_notes="Cache analysis results, background processing for large repos"
)
class ErgonComponent(StandardComponentBase):
    """Ergon v2: CI-in-the-Loop Reuse Specialist and Autonomous Builder."""
    
    def __init__(self):
        super().__init__(component_name="ergon", version="0.2.0")
        # Existing component attributes
        self.db_path = None
        self.memory_service = None
        self.terminal_memory = None
        self.a2a_client = None
        self.agent_generator = None
        self.agent_runner = None
        self.mcp_bridge = None
        
        # V2 Core subsystems (initialized in _component_specific_init)
        self.solution_registry = None
        self.github_analyzer = None
        self.configuration_engine = None
        self.workflow_memory = None
        self.autonomy_manager = None
        self.ci_orchestrator = None
        self.metrics_engine = None
        self.tool_discovery = None     # MCP tool discovery
        
        # V2 Runtime state
        self.current_autonomy_level = AutonomyLevel.ADVISORY
        self.active_workflows = {}
        self.learning_enabled = True
        
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
        
        # Initialize V2 subsystems
        logger.info("Initializing Ergon v2 CI-in-the-loop subsystems")
        
        # Initialize core v2 subsystems (placeholders for now)
        await self._init_solution_registry()
        await self._init_github_analyzer()
        await self._init_configuration_engine()
        await self._init_workflow_memory()
        await self._init_autonomy_manager()
        await self._init_ci_orchestrator()
        await self._init_metrics_engine()
        
        # Import existing Tekton tools into registry
        await self._import_tekton_tools()
        
        # Initialize MCP tool discovery
        await self._init_mcp_tool_discovery()
        
        logger.info("Ergon v2 initialization complete - ready to automate development")
    
    async def _init_solution_registry(self):
        """Initialize the solution registry for cataloging reusable components."""
        try:
            self.solution_registry = SolutionRepository()
            logger.info("Solution registry initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize solution registry: {e}")
            self.solution_registry = None
    
    async def _init_github_analyzer(self):
        """Initialize GitHub analyzer for deep repository understanding."""
        # TODO: Implement GitHub analyzer
        logger.info("GitHub analyzer initialization placeholder")
    
    async def _init_configuration_engine(self):
        """Initialize configuration engine for wrapper and adapter generation."""
        # TODO: Implement configuration engine
        logger.info("Configuration engine initialization placeholder")
    
    async def _init_workflow_memory(self):
        """Initialize workflow memory for capturing and replaying patterns."""
        try:
            self.workflow_memory = WorkflowMemory(self)
            await self.workflow_memory.start_analysis()
            logger.info("Workflow memory initialized with pattern analysis")
        except Exception as e:
            logger.warning(f"Failed to initialize workflow memory: {e}")
            self.workflow_memory = None
    
    async def _init_autonomy_manager(self):
        """Initialize autonomy manager for progressive automation levels."""
        # TODO: Implement autonomy manager
        logger.info("Autonomy manager initialization placeholder")
    
    async def _init_ci_orchestrator(self):
        """Initialize CI orchestrator for coordinating multi-CI workflows."""
        # TODO: Implement CI orchestrator
        logger.info("CI orchestrator initialization placeholder")
    
    async def _init_metrics_engine(self):
        """Initialize metrics engine for tracking productivity improvements."""
        # TODO: Implement metrics engine
        logger.info("Metrics engine initialization placeholder")
    
    async def _import_tekton_tools(self):
        """Import existing Tekton components into the solution registry."""
        # TODO: Scan Tekton components and import into registry
        logger.info("Importing Tekton tools placeholder")
    
    async def _init_mcp_tool_discovery(self):
        """Initialize MCP tool discovery service."""
        try:
            self.tool_discovery = MCPToolDiscovery(self)
            await self.tool_discovery.start_discovery()
            logger.info("MCP tool discovery service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize MCP tool discovery: {e}")
            self.tool_discovery = None
    
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
        
        # Cleanup v2 resources
        logger.info("Cleaning up Ergon v2 resources")
        
        # Stop MCP tool discovery
        if self.tool_discovery:
            try:
                await self.tool_discovery.stop_discovery()
                logger.info("MCP tool discovery cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP tool discovery: {e}")
        
        # Stop workflow memory analysis
        if self.workflow_memory:
            try:
                await self.workflow_memory.stop_analysis()
                logger.info("Workflow memory analysis stopped")
            except Exception as e:
                logger.warning(f"Error stopping workflow memory analysis: {e}")
        
        logger.info("Ergon v2 cleanup complete")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        # Original capabilities
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
        
        # V2 capabilities
        capabilities.extend([
            "solution_registry",
            "github_analysis", 
            "configuration_generation",
            "workflow_automation",
            "ci_orchestration",
            "autonomous_building",
            "pattern_learning",
            "metrics_tracking",
            "tool_chat",
            "team_chat"
        ])
            
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "CI-in-the-Loop Reuse Specialist and Autonomous Development Orchestrator",
            "database": str(self.db_path) if self.db_path else None,
            "category": "execution",
            "type": "execution_specialist",
            "a2a_enabled": bool(self.a2a_client),
            "memory_enabled": bool(self.memory_service),
            "agent_generator_enabled": bool(self.agent_generator),
            "mcp_enabled": bool(self.mcp_bridge),
            "responsibilities": [
                "Catalog and analyze reusable solutions",
                "Generate configurations and wrappers",
                "Orchestrate autonomous development workflows",
                "Learn from development patterns",
                "Coordinate multi-CI collaborations",
                "Track productivity improvements"
            ],
            "autonomy_level": self.current_autonomy_level.value,
            "learning_enabled": self.learning_enabled,
            "socket_port": 8102,
            "ui_theme": "purple"
        }
        
        return metadata
    
    async def set_autonomy_level(self, level: AutonomyLevel, reason: str = None):
        """Set the current autonomy level for Ergon's operations."""
        old_level = self.current_autonomy_level
        self.current_autonomy_level = level
        
        logger.info(f"Autonomy level changed from {old_level.value} to {level.value}")
        if reason:
            logger.info(f"Reason: {reason}")
        
        # Track this in metrics
        if self.metrics_engine:
            # await self.metrics_engine.track_autonomy_change(old_level, level, reason)
            pass
    
    async def automate_casey(self, project_description: str, autonomy_level: AutonomyLevel = None):
        """The ultimate goal - automate Casey's development expertise.
        
        Args:
            project_description: Description of what to build
            autonomy_level: Override default autonomy level for this project
        """
        if autonomy_level:
            await self.set_autonomy_level(autonomy_level, f"Project request: {project_description[:50]}...")
        
        logger.info(f"Starting automated development with {self.current_autonomy_level.value} autonomy")
        logger.info(f"Project: {project_description}")
        
        # TODO: Implement the full automation workflow
        # 1. Analyze requirements
        # 2. Find similar past workflows  
        # 3. Adapt workflow to current needs
        # 4. Execute with appropriate autonomy
        # 5. Learn from execution
        
        return {
            "status": "not_implemented",
            "message": "Automation workflow coming in Phase 3"
        }


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