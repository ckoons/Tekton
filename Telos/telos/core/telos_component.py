"""Telos component implementation using StandardComponentBase."""
import logging
import os
from typing import List, Dict, Any

from shared.utils.standard_component import StandardComponentBase
from telos.core.requirements_manager import RequirementsManager
from telos.prometheus_connector import TelosPrometheusConnector

logger = logging.getLogger(__name__)


class TelosComponent(StandardComponentBase):
    """Telos requirements tracking and validation component."""
    
    def __init__(self):
        super().__init__(component_name="telos", version="0.1.0")
        self.requirements_manager = None
        self.prometheus_connector = None
        self.mcp_bridge = None
        
    async def _component_specific_init(self):
        """Initialize Telos-specific services."""
        # Get storage directory from global config
        storage_dir = self.global_config.get_data_dir("telos/requirements")
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize requirements manager
        self.requirements_manager = RequirementsManager(storage_dir=storage_dir)
        self.requirements_manager.load_projects()
        logger.info(f"Requirements manager initialized with {len(self.requirements_manager.projects)} projects")
        
        # Initialize Prometheus connector
        self.prometheus_connector = TelosPrometheusConnector(self.requirements_manager)
        try:
            await self.prometheus_connector.initialize()
            logger.info("Prometheus connector initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Prometheus connector: {e}")
            # Prometheus connector is optional, so we continue
    
    async def _component_specific_cleanup(self):
        """Cleanup Telos-specific resources."""
        # Shutdown MCP bridge if available
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.shutdown()
                logger.info("Hermes MCP Bridge shutdown complete")
            except Exception as e:
                logger.warning(f"Error shutting down MCP bridge: {e}")
        
        # Shutdown Prometheus connector
        if self.prometheus_connector:
            try:
                await self.prometheus_connector.shutdown()
                logger.info("Prometheus connector shutdown complete")
            except Exception as e:
                logger.warning(f"Error shutting down Prometheus connector: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "requirements_tracking",
            "requirement_validation",
            "requirement_tracing",
            "prometheus_integration",
            "llm_refinement",
            "export_import"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "Product Requirements, Goals and User Communication",
            "category": "planning",
            "prometheus_available": self.prometheus_connector.prometheus_available if self.prometheus_connector else False,
            "project_count": len(self.requirements_manager.projects) if self.requirements_manager else 0
        }
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get detailed component status."""
        return {
            "requirements_manager": self.requirements_manager is not None,
            "prometheus_connector": self.prometheus_connector is not None,
            "prometheus_available": self.prometheus_connector.prometheus_available if self.prometheus_connector else False,
            "project_count": len(self.requirements_manager.projects) if self.requirements_manager else 0,
            "storage_dir": self.requirements_manager.storage_dir if self.requirements_manager else None
        }