"""
Startup utilities for Tekton components.

Provides standardized component startup with metrics, error handling,
and the critical socket release fix for macOS.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional
import psutil
import os

logger = logging.getLogger(__name__)


@dataclass
class StartupMetrics:
    """Metrics collected during component startup."""
    import_time: float = 0.0
    init_time: float = 0.0
    connection_time: float = 0.0
    registration_time: float = 0.0
    total_time: float = 0.0
    dependency_status: Dict[str, bool] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)


class StartupError(Exception):
    """Component startup failure."""
    def __init__(self, message: str, component: str, error_code: Optional[str] = None):
        self.component = component
        self.error_code = error_code
        super().__init__(f"[{component}] {message}")


async def component_startup(
    component_name: str,
    startup_func: Callable,
    timeout: int = 30,
    collect_metrics: bool = True,
    port: Optional[int] = None
) -> StartupMetrics:
    """
    Standard component startup with timeout, error handling, and metrics.
    
    Args:
        component_name: Name of the component starting up
        startup_func: Async function to execute during startup
        timeout: Maximum time to wait for startup (seconds)
        collect_metrics: Whether to collect detailed startup metrics
        port: Optional port number for socket release fix
        
    Returns:
        StartupMetrics object with timing and resource information
        
    Raises:
        StartupError: If startup fails or times out
    """
    metrics = StartupMetrics()
    start_time = time.time()
    
    try:
        logger.info(f"Starting {component_name}...")
        
        # Track initialization phases
        if collect_metrics:
            metrics.import_time = time.time() - start_time
            
            # Collect initial resource usage
            process = psutil.Process(os.getpid())
            metrics.resource_usage['initial_memory'] = process.memory_info().rss / 1024 / 1024  # MB
            metrics.resource_usage['initial_cpu'] = process.cpu_percent()
        
        # Execute startup with timeout
        init_start = time.time()
        await asyncio.wait_for(startup_func(), timeout=timeout)
        metrics.init_time = time.time() - init_start
        
        # Critical socket release fix for macOS
        # This prevents "Address already in use" errors on restart
        if port:
            logger.debug(f"Applying socket release fix for port {port}")
            await asyncio.sleep(0.5)
        
        # Collect final metrics
        if collect_metrics:
            process = psutil.Process(os.getpid())
            metrics.resource_usage['final_memory'] = process.memory_info().rss / 1024 / 1024  # MB
            metrics.resource_usage['final_cpu'] = process.cpu_percent()
            metrics.resource_usage['memory_increase'] = (
                metrics.resource_usage['final_memory'] - 
                metrics.resource_usage['initial_memory']
            )
        
        metrics.total_time = time.time() - start_time
        logger.info(
            f"{component_name} started successfully in {metrics.total_time:.2f}s "
            f"(init: {metrics.init_time:.2f}s)"
        )
        
        return metrics
        
    except asyncio.TimeoutError:
        logger.error(f"{component_name} startup timeout after {timeout}s")
        raise StartupError(f"Startup timeout after {timeout}s", component_name, "TIMEOUT")
    except Exception as e:
        logger.error(f"{component_name} startup failed: {e}")
        raise StartupError(str(e), component_name, "STARTUP_FAILED")


async def check_dependencies(
    component_name: str,
    dependencies: Dict[str, str],
    timeout: int = 5
) -> Dict[str, bool]:
    """
    Check if required dependencies are available.
    
    Args:
        component_name: Name of the component checking dependencies
        dependencies: Dict of dependency_name -> url to check
        timeout: Timeout for each dependency check
        
    Returns:
        Dict of dependency_name -> availability status
    """
    import aiohttp
    
    results = {}
    
    async def check_dependency(name: str, url: str) -> tuple[str, bool]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    return name, response.status == 200
        except Exception as e:
            logger.debug(f"Dependency {name} check failed: {e}")
            return name, False
    
    # Check all dependencies in parallel
    tasks = [check_dependency(name, url) for name, url in dependencies.items()]
    check_results = await asyncio.gather(*tasks)
    
    for name, status in check_results:
        results[name] = status
        if not status:
            logger.warning(f"[{component_name}] Dependency {name} is not available")
    
    return results


def create_startup_handler(
    component_name: str,
    port: int,
    dependencies: Optional[Dict[str, str]] = None
) -> Callable:
    """
    Create a standardized startup handler for FastAPI apps.
    
    Args:
        component_name: Name of the component
        port: Port number for the component
        dependencies: Optional dict of dependencies to check
        
    Returns:
        Async startup handler function
    """
    async def startup_handler():
        """Generated startup handler."""
        logger.info(f"Initializing {component_name} on port {port}")
        
        # Check dependencies if provided
        if dependencies:
            dep_status = await check_dependencies(component_name, dependencies)
            if not all(dep_status.values()):
                logger.warning(f"Some dependencies are unavailable: {dep_status}")
        
        # Apply socket release fix
        await asyncio.sleep(0.1)
        
        logger.info(f"{component_name} initialization complete")
    
    return startup_handler


# Utility function for quick component startup
async def quick_component_startup(
    component_name: str,
    port: int,
    register_func: Optional[Callable] = None,
    hermes_url: str = "http://localhost:8001"
) -> None:
    """
    Quick startup helper for simple components.
    
    Args:
        component_name: Name of the component
        port: Port number
        register_func: Optional registration function
        hermes_url: URL for Hermes registration
    """
    try:
        # Basic startup logging
        logger.info(f"Starting {component_name} on port {port}")
        
        # Register with Hermes if function provided
        if register_func:
            try:
                await register_func(component_name, port, hermes_url)
                logger.info(f"{component_name} registered with Hermes")
            except Exception as e:
                logger.warning(f"Failed to register with Hermes: {e}")
        
        # Socket release fix
        await asyncio.sleep(0.5)
        
    except Exception as e:
        raise StartupError(f"Quick startup failed: {e}", component_name)