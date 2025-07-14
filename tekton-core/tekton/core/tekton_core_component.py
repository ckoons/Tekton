"""TektonCore component implementation using StandardComponentBase."""
import logging
from typing import List, Dict, Any

from shared.utils.standard_component import StandardComponentBase
from .component_lifecycle import ComponentRegistry
from .heartbeat_monitor import HeartbeatMonitor
from .resource_monitor import ResourceMonitor
from .monitoring_dashboard import MonitoringDashboard

logger = logging.getLogger(__name__)


class TektonCoreComponent(StandardComponentBase):
    """TektonCore system coordination and monitoring component."""
    
    def __init__(self):
        super().__init__(component_name="tekton_core", version="0.1.0")
        self.component_registry = None
        self.heartbeat_monitor = None
        self.resource_monitor = None
        self.monitoring_dashboard = None
        
    async def _component_specific_init(self):
        """Initialize TektonCore-specific services."""
        # Initialize core components
        self.component_registry = ComponentRegistry()
        logger.info("Component registry initialized")
        
        self.heartbeat_monitor = HeartbeatMonitor()
        logger.info("Heartbeat monitor initialized")
        
        self.resource_monitor = ResourceMonitor()
        logger.info("Resource monitor initialized")
        
        # Monitoring dashboard is optional - DISABLED for now due to initialization issues
        try:
            # Temporarily disable monitoring dashboard to keep Tekton Core running
            # self.monitoring_dashboard = MonitoringDashboard()
            # await self.monitoring_dashboard.start()
            # logger.info("Monitoring dashboard initialized")
            self.monitoring_dashboard = None
            logger.info("Monitoring dashboard disabled (temporary fix)")
        except Exception as e:
            logger.warning(f"Monitoring dashboard initialization failed: {e}")
            self.monitoring_dashboard = None
    
    async def _component_specific_cleanup(self):
        """Cleanup TektonCore-specific resources."""
        # Stop monitoring dashboard if running
        if self.monitoring_dashboard:
            try:
                await self.monitoring_dashboard.stop()
                logger.info("Monitoring dashboard stopped")
            except Exception as e:
                logger.warning(f"Error stopping monitoring dashboard: {e}")
    
    def get_capabilities(self) -> List[str]:
        """Get component capabilities."""
        return [
            "system_coordination",
            "component_registry",
            "heartbeat_monitoring",
            "resource_monitoring",
            "system_dashboard"
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "description": "Core system coordination and monitoring",
            "category": "infrastructure"
        }
    
    def get_component_status(self) -> Dict[str, bool]:
        """Get status of all core components."""
        return {
            "registry": self.component_registry is not None,
            "heartbeat_monitor": self.heartbeat_monitor is not None,
            "resource_monitor": self.resource_monitor is not None,
            "monitoring_dashboard": self.monitoring_dashboard is not None
        }
    
    def is_ready(self) -> bool:
        """Check if all core components are ready."""
        status = self.get_component_status()
        # All core components must be ready (monitoring_dashboard is optional)
        return all([
            status["registry"],
            status["heartbeat_monitor"],
            status["resource_monitor"]
        ])