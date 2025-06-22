"""Synthesis component implementation using StandardComponentBase."""
import logging
from typing import List, Dict, Any

from shared.utils.standard_component import StandardComponentBase
from landmarks import architecture_decision, state_checkpoint, integration_point

logger = logging.getLogger(__name__)


@architecture_decision(
    title="Central execution hub",
    rationale="Synthesis serves as the execution engine for Tekton, coordinating plan implementation across components",
    alternatives_considered=["Distributed execution", "Component-local execution", "External workflow engine"])
@state_checkpoint(
    title="Execution engine state",
    state_type="ephemeral",
    persistence=False,
    consistency_requirements="Active execution tracking must survive brief restarts",
    recovery_strategy="Cancel incomplete executions on restart, restore from execution history"
)
class SynthesisComponent(StandardComponentBase):
    """Synthesis execution and integration engine component."""
    
    def __init__(self):
        super().__init__(component_name="synthesis", version="0.1.0")
        self.execution_engine = None
        self.event_manager = None
        self.ws_manager = None
        self.mcp_bridge = None
        self.initialized = False
        
    async def _component_specific_init(self):
        """Initialize Synthesis-specific services."""
        # Import here to avoid circular imports
        from synthesis.core.execution_engine import ExecutionEngine
        from synthesis.core.events import EventManager, WebSocketManager
        
        try:
            # Create execution engine
            self.execution_engine = ExecutionEngine()
            logger.info("Execution engine initialized successfully")
            
            # Create event manager
            self.event_manager = EventManager.get_instance()
            logger.info("Event manager initialized successfully")
            
            # Create WebSocket manager
            self.ws_manager = WebSocketManager()
            logger.info("WebSocket manager initialized successfully")
            
            # Mark as initialized
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing Synthesis services: {e}")
            raise
    
    async def _component_specific_cleanup(self):
        """Cleanup Synthesis-specific resources."""
        # Shutdown MCP bridge if available
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("Hermes MCP Bridge shutdown complete")
            except Exception as e:
                logger.warning(f"Error shutting down MCP bridge: {e}")
        
        # Shutdown execution engine if needed
        if self.execution_engine:
            try:
                # Cancel any active executions
                for execution_id in list(self.execution_engine.active_executions.keys()):
                    await self.execution_engine.cancel_execution(execution_id)
                logger.info("Active executions cancelled")
            except Exception as e:
                logger.warning(f"Error cancelling active executions: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "code_generation",
            "integration",
            "execution",
            "event_streaming",
            "metric_tracking"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "Execution and integration engine for Tekton",
            "category": "execution",
            "websocket_endpoint": "/ws",
            "documentation": "/api/v1/docs"
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get detailed component status."""
        status = {
            "execution_engine": self.execution_engine is not None,
            "event_manager": self.event_manager is not None,
            "ws_manager": self.ws_manager is not None,
            "mcp_bridge": self.mcp_bridge is not None
        }
        
        if self.execution_engine:
            status.update({
                "active_executions": len(self.execution_engine.active_executions),
                "execution_capacity": self.execution_engine.max_concurrent_executions,
                "execution_load": len(self.execution_engine.active_executions) / self.execution_engine.max_concurrent_executions,
                "total_executions": len(self.execution_engine.execution_history)
            })
        
        return status
    
    @integration_point(
    title="Synthesis MCP bridge",
    target_component="Hermes",
    protocol="Internal API",
    data_flow="Execution commands → Engine → Status updates"
)
    async def initialize_mcp_bridge(self):
        """Initialize the MCP bridge after component startup."""
        try:
            from synthesis.core.mcp.hermes_bridge import SynthesisMCPBridge
            self.mcp_bridge = SynthesisMCPBridge(self.execution_engine)
            await self.mcp_bridge.initialize()
            logger.info("Hermes MCP Bridge initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Hermes MCP Bridge: {e}")
            # MCP bridge is optional, so we don't raise