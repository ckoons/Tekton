"""Budget component implementation using StandardComponentBase."""
import logging
from typing import List, Dict, Any
from pathlib import Path

from shared.utils.standard_component import StandardComponentBase
from budget.core.engine import BudgetEngine
from budget.data.repository import db_manager
from budget.api.websocket_server import ConnectionManager
from landmarks import architecture_decision, state_checkpoint, integration_point

logger = logging.getLogger(__name__)

@architecture_decision(
    title="Centralized budget management",
    rationale="Implement unified budget tracking and enforcement across all Tekton components to prevent cost overruns",
    alternatives_considered=["Per-component budgets", "External cost tracking", "No budget enforcement"])
@state_checkpoint(
    title="Budget database state",
    state_type="persistent",
    persistence=True,
    consistency_requirements="ACID compliance for financial tracking",
    recovery_strategy="Restore from SQLite database with transaction logs"
)
class BudgetComponent(StandardComponentBase):
    """Budget management component with financial tracking and MCP support."""
    
    def __init__(self):
        super().__init__(component_name="penia", version="0.1.0")
        # Component-specific attributes
        self.budget_engine = None
        self.connection_manager = None
        self.mcp_bridge = None
        self.db_path = None
        
    async def _component_specific_init(self):
        """Initialize Budget-specific services."""
        # Critical components - fail if these don't work
        
        # Set database path using GlobalConfig
        data_dir = Path(self.global_config.get_data_dir("budget"))
        self.db_path = data_dir / "budget.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set database path for the manager and initialize
        db_manager.connection_string = f"sqlite:///{self.db_path}"
        db_manager.initialize()
        logger.info(f"Database initialized at {self.db_path}")
        
        # Initialize budget engine
        self.budget_engine = BudgetEngine()
        logger.info("Budget engine initialized")
        
        # Initialize WebSocket connection manager
        self.connection_manager = ConnectionManager()
        logger.info("WebSocket connection manager initialized")
        
        # Optional components - warn but continue
        try:
            # MCP tools initialization - will be completed in startup_callback
            # This is just preparation
            logger.info("Budget component core initialization completed")
        except Exception as e:
            logger.warning(f"Optional component initialization failed: {e}")
    
    async def _component_specific_cleanup(self):
        """Cleanup Budget-specific resources."""
        # Cleanup WebSocket connections
        if self.connection_manager:
            try:
                self.connection_manager.cleanup()
                logger.info("WebSocket connections cleaned up")
            except Exception as e:
                logger.warning(f"Error during WebSocket cleanup: {e}")
        
        # Cleanup MCP bridge
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("MCP bridge cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP bridge: {e}")
        
        # Cleanup database connections
        try:
            db_manager.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.warning(f"Error closing database: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        capabilities = [
            "budget_allocation",
            "cost_tracking", 
            "usage_monitoring",
            "assistant_service",
            "websocket_support"
        ]
        
        if self.mcp_bridge:
            capabilities.append("mcp_bridge")
            
        return capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        metadata = {
            "description": "Budget management and cost tracking component",
            "websocket_endpoint": "/ws",
            "database": str(self.db_path) if self.db_path else None,
            "assistant": "enabled",
            "mcp_enabled": bool(self.mcp_bridge)
        }
        
        return metadata


@integration_point(
    title="Budget engine access",
    target_component="BudgetEngine",
    protocol="Internal API",
    data_flow="Component → BudgetEngine → Database"
)
def get_budget_engine() -> BudgetEngine:
    """
    Convenience function to get budget engine through component.
    This maintains compatibility with existing code during migration.
    """
    try:
        # Try to get from FastAPI app state
        from starlette.applications import Starlette
        from starlette.requests import Request
        import contextvars
        
        # This is a temporary compatibility function
        # In the future, all access should go through app.state.component.budget_engine
        logger.warning("Using compatibility get_budget_engine() - consider accessing through component directly")
        
        # For now, return the singleton instance
        from budget.core.engine import budget_engine
        return budget_engine
        
    except Exception as e:
        logger.warning(f"Could not access budget engine through component, using singleton: {e}")
        # Fallback to singleton pattern
        from budget.core.engine import budget_engine
        return budget_engine
