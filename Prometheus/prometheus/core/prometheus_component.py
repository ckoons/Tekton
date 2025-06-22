"""
Prometheus component implementation using StandardComponentBase.

This module implements the Prometheus planning system component
following the standardized patterns.
"""
import logging
from typing import List, Dict, Any, Optional

from shared.utils.standard_component import StandardComponentBase
from prometheus.core.planning_engine import PlanningEngine
from prometheus.api.fastmcp_endpoints import fastmcp_server
from landmarks import architecture_decision, state_checkpoint, integration_point

logger = logging.getLogger("prometheus")


@architecture_decision(
    title="Dual-nature planning system",
    rationale="Combines Prometheus (forward planning) and Epimethius (retrospective analysis) for comprehensive project management",
    alternatives=["Separate planning and retrospective components", "Traditional project management tools"],
    decision_date="2024-01-15"
)
@state_checkpoint(
    title="Planning engine state",
    state_type="service",
    persistence=True,
    consistency_requirements="Planning data must be consistent across restarts",
    recovery_strategy="Restore from persisted plan storage"
)
class PrometheusComponent(StandardComponentBase):
    """
    Prometheus planning system component.
    
    Implements strategic planning and retrospective analysis capabilities
    following Tekton's standardized component patterns.
    """
    
    def __init__(self):
        """Initialize Prometheus component."""
        super().__init__(
            component_name="prometheus",
            version="0.1.0"
        )
        self.planning_engine = None
        self.fastmcp_server = fastmcp_server
        
    @integration_point(
        title="Planning engine initialization",
        target_component="PlanningEngine",
        protocol="Internal API",
        data_flow="Plans flow from objectives through reasoning iterations to structured output"
    )
    async def _component_specific_init(self):
        """Initialize Prometheus-specific components."""
        # Initialize planning engine
        self.planning_engine = PlanningEngine(component_id="prometheus.planning")
        await self.planning_engine.initialize(data_dir=self.data_dir)
        self.logger.info("Planning engine initialized")
        
        # Store planning engine in global config for access by endpoints
        self.global_config.set_service('prometheus_planning_engine', self.planning_engine)
        
        # Initialize FastMCP server
        try:
            await self.fastmcp_server.startup()
            self.logger.info("FastMCP server initialized successfully")
        except Exception as e:
            self.logger.warning(f"FastMCP server initialization failed: {e}")
            # Non-critical, continue startup
    
    async def _initialize_mcp(self):
        """Initialize MCP bridge for Prometheus."""
        if not self.global_config.mcp_enabled:
            return
            
        try:
            await self._initialize_mcp_bridge(
                'prometheus.core.mcp.hermes_bridge.PrometheusMCPBridge'
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP bridge: {e}")
            # Non-critical, continue without MCP
    
    async def _component_specific_cleanup(self):
        """Cleanup Prometheus-specific components."""
        # Shutdown FastMCP server
        try:
            await self.fastmcp_server.shutdown()
            self.logger.info("FastMCP server shut down successfully")
        except Exception as e:
            self.logger.warning(f"FastMCP server shutdown failed: {e}")
        
        # Cleanup planning engine if it has cleanup method
        if self.planning_engine and hasattr(self.planning_engine, 'cleanup'):
            await self.planning_engine.cleanup()
        
        # Remove from service registry
        self.global_config.remove_service('prometheus_planning_engine')
    
    def _get_component_health(self) -> Optional[Dict[str, Any]]:
        """Get Prometheus-specific health information."""
        health_info = {
            "planning_engine": "initialized" if self.planning_engine else "not_initialized",
            "fastmcp_server": "running" if self.fastmcp_server else "not_running",
        }
        
        # Add planning engine stats if available
        if self.planning_engine and hasattr(self.planning_engine, 'get_stats'):
            health_info["planning_stats"] = self.planning_engine.get_stats()
            
        return health_info
    
    def get_capabilities(self) -> List[str]:
        """Get Prometheus capabilities."""
        return [
            "strategic_planning",
            "goal_management", 
            "retrospective_analysis",
            "timeline_tracking",
            "resource_optimization"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get Prometheus metadata for registration."""
        return {
            "description": "Strategic planning and goal management system for Tekton ecosystem",
            "category": "planning",
            "dual_nature": "Prometheus (forward planning) + Epimethius (retrospective analysis)"
        }