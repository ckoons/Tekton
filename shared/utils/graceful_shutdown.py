"""
Graceful Shutdown Handler for Tekton Components

Provides standardized shutdown handling across all Tekton components.
"""
import asyncio
import signal
import logging
import aiohttp
from typing import Optional, Callable, List
from datetime import datetime

from landmarks import architecture_decision, integration_point, performance_boundary

try:
    from shared.urls import hermes_url as get_hermes_url
except ImportError:
    get_hermes_url = None

logger = logging.getLogger(__name__)

@architecture_decision(
    title="Graceful shutdown pattern",
    rationale="Ensure components clean up properly and notify Hermes before terminating",
    alternatives_considered=["Immediate termination", "Systemd-only management", "K8s lifecycle hooks"],
    impacts=["reliability", "data_integrity", "component_coordination"],
    decided_by="team"
)
class GracefulShutdown:
    """Handles graceful shutdown for Tekton components"""
    
    def __init__(self, component_name: str, port: int, hermes_url: str = None):
        self.component_name = component_name
        self.port = port
        if hermes_url:
            self.hermes_url = hermes_url
        elif get_hermes_url:
            self.hermes_url = get_hermes_url("")
        else:
            self.hermes_url = "http://localhost:8001"
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False
        self.shutdown_event = asyncio.Event()
        
    def add_handler(self, handler: Callable):
        """Add a cleanup handler to run during shutdown"""
        self.shutdown_handlers.append(handler)
        
    @integration_point(
        title="Hermes shutdown notification",
        target_component="Hermes",
        protocol="REST",
        data_flow="Component status update -> Hermes registry",
        critical=True
    )
    @performance_boundary(
        title="Shutdown notification timeout",
        sla="<2 seconds",
        optimization_notes="Short timeout to prevent hanging during shutdown"
    )
    async def notify_hermes_shutdown(self):
        """Notify Hermes that we're shutting down"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "component": self.component_name,
                    "port": self.port,
                    "status": "shutting_down",
                    "timestamp": datetime.now().isoformat()
                }
                async with session.post(
                    f"{self.hermes_url}/api/components/status",
                    json=payload,
                    timeout=2
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Notified Hermes of {self.component_name} shutdown")
                    else:
                        logger.warning(f"Failed to notify Hermes: HTTP {resp.status}")
        except Exception as e:
            logger.warning(f"Could not notify Hermes of shutdown: {e}")
    
    async def shutdown(self, sig: Optional[signal.Signals] = None):
        """Perform graceful shutdown"""
        if self.is_shutting_down:
            return
            
        self.is_shutting_down = True
        
        if sig:
            logger.info(f"Received signal {sig.name}, starting graceful shutdown of {self.component_name}")
        else:
            logger.info(f"Starting graceful shutdown of {self.component_name}")
        
        # Notify Hermes
        await self.notify_hermes_shutdown()
        
        # Run custom cleanup handlers
        for handler in self.shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
                logger.info(f"Executed shutdown handler: {handler.__name__}")
            except Exception as e:
                logger.error(f"Error in shutdown handler {handler.__name__}: {e}")
        
        # Set shutdown event
        self.shutdown_event.set()
        
        # Give a brief moment for final cleanup
        await asyncio.sleep(0.5)
        
        logger.info(f"{self.component_name} shutdown complete")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        loop = asyncio.get_event_loop()
        
        # Handle SIGTERM and SIGINT
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(s))
            )
        
        logger.info(f"Signal handlers configured for {self.component_name}")
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self.shutdown_event.wait()

# FastAPI integration helper
def add_fastapi_shutdown(app, shutdown_handler: GracefulShutdown):
    """Add graceful shutdown to a FastAPI app"""
    
    @app.on_event("startup")
    async def startup():
        shutdown_handler.setup_signal_handlers()
    
    @app.on_event("shutdown")
    async def shutdown():
        if not shutdown_handler.is_shutting_down:
            await shutdown_handler.shutdown()

# Example usage for a component
async def create_shutdown_handler(
    component_name: str,
    port: int,
    cleanup_coroutines: Optional[List[Callable]] = None
) -> GracefulShutdown:
    """Create a configured shutdown handler"""
    handler = GracefulShutdown(component_name, port)
    
    # Add any cleanup coroutines
    if cleanup_coroutines:
        for cleanup in cleanup_coroutines:
            handler.add_handler(cleanup)
    
    return handler