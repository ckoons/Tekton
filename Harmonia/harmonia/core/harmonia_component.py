"""Harmonia component implementation using StandardComponentBase."""
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase
from harmonia.core.state import StateManager
from harmonia.core.component import ComponentRegistry
from harmonia.core.engine import WorkflowEngine
from harmonia.core.startup_instructions import StartUpInstructions
from harmonia.core.workflow_startup import WorkflowEngineStartup
from landmarks import architecture_decision, state_checkpoint, danger_zone

logger = logging.getLogger(__name__)

@architecture_decision(
    title="Workflow orchestration system",
    rationale="Harmonia provides centralized workflow management and cross-component coordination for complex multi-step processes",
    alternatives_considered=["Per-component workflows", "External workflow manager", "Manual coordination"])
@state_checkpoint(
    title="Workflow state persistence",
    state_type="persistent",
    persistence=True,
    consistency_requirements="Workflow state must survive restarts to enable resumption",
    recovery_strategy="Load workflow state from disk/database, resume paused executions"
)
class HarmoniaComponent(StandardComponentBase):
    """Harmonia workflow orchestration component with state management and event streaming."""
    
    def __init__(self):
        super().__init__(component_name="harmonia", version="0.1.0")
        # Component-specific attributes - initialized in dependency order
        self.base_dir = None
        self.state_manager = None
        self.component_registry = None
        self.workflow_engine = None
        self.connection_manager = None
        self.event_manager = None
        self.startup_instructions = None
        self.mcp_bridge = None
        
    @danger_zone(
        title="Complex initialization sequence",
        risk_level="high",
        risks=["Initialization order dependencies", "State corruption on partial init", "Resource leaks"],
        mitigations=["Ordered initialization", "Rollback on failure", "Resource tracking"],
        review_required=True
    )
    async def _component_specific_init(self):
        """Initialize Harmonia-specific services in critical dependency order."""
        # Critical initialization sequence
        
        # 1. Set up data directory structure
        self.base_dir = Path(self.global_config.get_data_dir("harmonia"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for workflows, templates, state, etc.
        subdirs = ["workflows", "templates", "state", "checkpoints", "events"]
        for subdir in subdirs:
            (self.base_dir / subdir).mkdir(exist_ok=True)
        logger.info(f"Data directory structure created at {self.base_dir}")
        
        # 2. Load or create startup instructions (critical for workflow initialization)
        try:
            instructions_file = self.base_dir / "startup_instructions.json"
            if instructions_file.exists():
                logger.info(f"Loading startup instructions from {instructions_file}")
                self.startup_instructions = StartUpInstructions.from_file(str(instructions_file))
            else:
                # Create default startup instructions
                hermes_url = os.environ.get("HERMES_URL", "http://localhost:8001")
                log_level = os.environ.get("LOG_LEVEL", "INFO")
                
                self.startup_instructions = StartUpInstructions(
                    data_directory=str(self.base_dir),
                    hermes_url=hermes_url,
                    log_level=log_level,
                    auto_register=True,
                    initialize_db=True,
                    load_previous_state=True
                )
                logger.info("Created default startup instructions")
        except Exception as e:
            logger.error(f"Error with startup instructions: {e}")
            # Create minimal fallback instructions
            self.startup_instructions = StartUpInstructions(
                data_directory=str(self.base_dir),
                hermes_url="http://localhost:8001",
                log_level="INFO",
                auto_register=False,
                initialize_db=True,
                load_previous_state=False
            )
        
        # 3. Initialize StateManager first (foundation for everything)
        try:
            # StateManager initialization might be handled by WorkflowEngineStartup
            # For now, we'll let WorkflowEngineStartup handle it
            logger.info("StateManager will be initialized with WorkflowEngine")
        except Exception as e:
            logger.error(f"StateManager preparation failed: {e}")
            raise
        
        # 4. Initialize ComponentRegistry next (needed for workflow registration)
        try:
            self.component_registry = ComponentRegistry()
            logger.info("ComponentRegistry initialized")
        except Exception as e:
            logger.error(f"ComponentRegistry initialization failed: {e}")
            # ComponentRegistry is critical, but we can continue with limited functionality
            self.component_registry = None
        
        # 5. Initialize WorkflowEngine with StartupInstructions (core orchestration)
        try:
            startup = WorkflowEngineStartup(self.startup_instructions)
            self.workflow_engine = await startup.initialize()
            
            # Extract state_manager from workflow_engine if not separately initialized
            if hasattr(self.workflow_engine, 'state_manager'):
                self.state_manager = self.workflow_engine.state_manager
            
            # Update component_registry reference if engine has its own
            if hasattr(self.workflow_engine, 'component_registry'):
                self.component_registry = self.workflow_engine.component_registry
                
            logger.info("WorkflowEngine initialized successfully with StartupInstructions")
        except Exception as e:
            logger.error(f"WorkflowEngine initialization failed: {e}")
            # WorkflowEngine is critical - re-raise
            raise
        
        # 6. Initialize Connection/Event managers last (UI layer)
        # These will be initialized in the app.py as they're tightly coupled to FastAPI
        self.connection_manager = None  # Will be set by app
        self.event_manager = None      # Will be set by app
        
        logger.info("Harmonia component core initialization completed")
    
    async def _component_specific_cleanup(self):
        """Cleanup Harmonia-specific resources with proper workflow shutdown."""
        
        # 1. Gracefully shutdown active workflows
        if self.workflow_engine:
            try:
                # Get active workflow executions
                if hasattr(self.workflow_engine, 'active_executions'):
                    active_count = len(self.workflow_engine.active_executions)
                    if active_count > 0:
                        logger.info(f"Gracefully shutting down {active_count} active workflows")
                        # Pause or cancel active workflows
                        for execution_id in list(self.workflow_engine.active_executions.keys()):
                            try:
                                await self.workflow_engine.pause_workflow(execution_id)
                                logger.info(f"Paused workflow execution {execution_id}")
                            except Exception as e:
                                logger.warning(f"Error pausing workflow {execution_id}: {e}")
                
                logger.info("WorkflowEngine cleanup completed")
            except Exception as e:
                logger.warning(f"Error during WorkflowEngine cleanup: {e}")
        
        # 2. Close WebSocket connections (handled by connection_manager)
        if self.connection_manager:
            try:
                # Connection manager cleanup is handled in app.py
                logger.info("Connection manager will be cleaned up by app")
            except Exception as e:
                logger.warning(f"Error noting connection manager cleanup: {e}")
        
        # 3. Persist state before shutdown
        if self.state_manager:
            try:
                # Trigger any state persistence operations
                if hasattr(self.state_manager, 'persist_state'):
                    await self.state_manager.persist_state()
                    logger.info("State persisted before shutdown")
            except Exception as e:
                logger.warning(f"Error persisting state: {e}")
        
        # 4. Cleanup MCP bridge
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("MCP bridge cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP bridge: {e}")
        
        # 5. Unregister event handlers (if needed)
        # Event handlers are typically cleaned up with their associated objects
        logger.info("Event handlers cleaned up with associated services")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        capabilities = [
            "workflow_orchestration",
            "state_management",
            "event_streaming",
            "component_coordination"
        ]
        
        if self.workflow_engine:
            capabilities.append("workflow_execution")
            
        if self.component_registry:
            capabilities.append("component_registry")
        
        if self.mcp_bridge:
            capabilities.append("mcp_bridge")
            
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "Workflow orchestration and state management service",
            "category": "workflow",
            "data_directory": str(self.base_dir) if self.base_dir else None,
            "workflow_engine_initialized": bool(self.workflow_engine),
            "state_manager_initialized": bool(self.state_manager),
            "component_registry_initialized": bool(self.component_registry),
            "startup_instructions_loaded": bool(self.startup_instructions),
            "event_types": ["workflow_started", "workflow_completed", "workflow_failed", 
                          "task_started", "task_completed", "task_failed"]
        }
        
        # Add active workflow count if available
        if self.workflow_engine and hasattr(self.workflow_engine, 'active_executions'):
            metadata["active_workflows"] = len(self.workflow_engine.active_executions)
            
        return metadata


# Connection and Event managers that will be used in app.py
class ConnectionManager:
    """Manages active WebSocket connections for Harmonia."""
    def __init__(self):
        """Initialize the connection manager."""
        from typing import Set
        from uuid import UUID
        self.active_connections: Dict[UUID, Any] = {}  # WebSocket type imported in app
        self.subscriptions: Dict[UUID, Set[UUID]] = {}
        
    async def cleanup(self):
        """Cleanup all connections."""
        # Disconnect all clients
        for client_id in list(self.active_connections.keys()):
            self.disconnect(client_id)
        logger.info("All WebSocket connections closed")
    
    def disconnect(self, client_id):
        """Disconnect a client."""
        self.active_connections.pop(client_id, None)
        self.subscriptions.pop(client_id, None)


class EventManager:
    """Manages event streams for Server-Sent Events."""
    def __init__(self):
        """Initialize the event manager."""
        import asyncio
        from uuid import UUID
        self.event_queues: Dict[UUID, asyncio.Queue] = {}
        
    async def cleanup(self):
        """Cleanup all event queues."""
        # Clear all queues
        self.event_queues.clear()
        logger.info("All event queues cleared")