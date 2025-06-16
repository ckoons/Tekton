"""
Graceful shutdown utilities for Tekton components.

Provides coordinated shutdown with cleanup tasks, signal handling,
and FastAPI lifespan integration using the new pattern.
"""
import asyncio
import logging
import signal
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict, Any

from shared.utils.errors import ShutdownError
from shared.utils.startup import component_startup

logger = logging.getLogger(__name__)


@dataclass
class ShutdownMetrics:
    """Metrics collected during component shutdown."""
    component_name: str
    cleanup_tasks_total: int = 0
    cleanup_tasks_completed: int = 0
    cleanup_errors: List[str] = field(default_factory=list)
    total_time: float = 0.0
    timeout_occurred: bool = False


class GracefulShutdown:
    """
    Coordinated graceful shutdown for Tekton components.
    
    Handles signal processing, cleanup task management, and metrics collection.
    """
    
    def __init__(self, component_name: str):
        """
        Initialize GracefulShutdown.
        
        Args:
            component_name: Name of the component for logging
        """
        self.component_name = component_name
        self.shutdown_event = asyncio.Event()
        self.cleanup_tasks: List[Callable] = []
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"[{self.component_name}] Received signal {signum}, initiating graceful shutdown")
        self.shutdown_event.set()
    
    def register_cleanup(self, cleanup_func: Callable):
        """
        Register a cleanup function to run during shutdown.
        
        Args:
            cleanup_func: Async function to call during shutdown
        """
        self.cleanup_tasks.append(cleanup_func)
    
    async def shutdown_sequence(self, timeout: int = 10) -> ShutdownMetrics:
        """
        Execute graceful shutdown sequence.
        
        Args:
            timeout: Maximum time to wait for cleanup tasks
            
        Returns:
            ShutdownMetrics with shutdown statistics
        """
        metrics = ShutdownMetrics(
            component_name=self.component_name,
            cleanup_tasks_total=len(self.cleanup_tasks)
        )
        start_time = time.time()
        
        logger.info(f"[{self.component_name}] Starting graceful shutdown...")
        
        if not self.cleanup_tasks:
            logger.info(f"[{self.component_name}] No cleanup tasks registered")
            metrics.total_time = time.time() - start_time
            return metrics
        
        try:
            # Create coroutines for all cleanup tasks
            cleanup_coroutines = []
            for task in self.cleanup_tasks:
                cleanup_coroutines.append(self._run_cleanup_task(task, metrics))
            
            # Run all cleanup tasks in parallel with timeout
            await asyncio.wait_for(
                asyncio.gather(*cleanup_coroutines, return_exceptions=True),
                timeout=timeout
            )
            
        except asyncio.TimeoutError:
            logger.warning(f"[{self.component_name}] Shutdown timeout after {timeout}s")
            metrics.timeout_occurred = True
        
        metrics.total_time = time.time() - start_time
        
        logger.info(
            f"[{self.component_name}] Graceful shutdown complete. "
            f"Tasks: {metrics.cleanup_tasks_completed}/{metrics.cleanup_tasks_total}, "
            f"Time: {metrics.total_time:.2f}s"
        )
        
        return metrics
    
    async def _run_cleanup_task(self, task: Callable, metrics: ShutdownMetrics):
        """Run a single cleanup task with error handling."""
        try:
            await task()
            metrics.cleanup_tasks_completed += 1
        except Exception as e:
            error_msg = f"Cleanup task {task.__name__ if hasattr(task, '__name__') else 'unknown'} failed: {e}"
            logger.error(f"[{self.component_name}] {error_msg}")
            metrics.cleanup_errors.append(error_msg)




def create_shutdown_handler(
    component_name: str,
    cleanup_funcs: List[Callable],
    timeout: int = 10
) -> Callable:
    """
    Create a standardized shutdown handler function.
    
    Args:
        component_name: Name of the component
        cleanup_funcs: List of cleanup functions to execute
        timeout: Shutdown timeout in seconds
        
    Returns:
        Async shutdown handler function
    """
    async def shutdown_handler():
        """Generated shutdown handler."""
        shutdown = GracefulShutdown(component_name)
        
        for func in cleanup_funcs:
            shutdown.register_cleanup(func)
        
        metrics = await shutdown.shutdown_sequence(timeout=timeout)
        
        if metrics.timeout_occurred:
            raise ShutdownError(
                f"Shutdown timeout after {timeout}s",
                component_name,
                "SHUTDOWN_TIMEOUT"
            )
        
        return metrics
    
    return shutdown_handler


# Helper function for common cleanup tasks

async def cleanup_aiohttp_session(session):
    """Cleanup aiohttp client session."""
    if session and not session.closed:
        await session.close()
        # Wait for connections to close
        await asyncio.sleep(0.25)


async def cleanup_database_pool(pool):
    """Cleanup database connection pool."""
    if pool:
        await pool.close()


async def cleanup_background_tasks(tasks: List[asyncio.Task]):
    """Cancel and await background tasks."""
    for task in tasks:
        if not task.done():
            task.cancel()
    
    # Wait for all tasks to complete cancellation
    await asyncio.gather(*tasks, return_exceptions=True)