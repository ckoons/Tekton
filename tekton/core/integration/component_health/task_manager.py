#!/usr/bin/env python3
"""
Task Manager Module

Manages component tasks, timeouts, and circuit breakers.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set, Union

from ...logging_integration import LogCategory, LogLevel
from ...graceful_degradation import CircuitBreaker

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages component tasks, timeouts, and circuit breakers.
    """
    
    def __init__(self, 
                component_id: str,
                metrics_manager,
                logger):
        """
        Initialize task manager.
        
        Args:
            component_id: Component ID
            metrics_manager: Metrics manager instance
            logger: Logger instance
        """
        self.component_id = component_id
        self.metrics_manager = metrics_manager
        self.logger = logger
        self.tasks = set()
        
    def run_task(self, coro, *args, **kwargs) -> asyncio.Task:
        """
        Run a coroutine as a task and track it.
        
        Args:
            coro: Coroutine to run
            *args: Arguments for coroutine
            **kwargs: Keyword arguments for coroutine
            
        Returns:
            Task object
        """
        task = asyncio.create_task(coro(*args, **kwargs))
        self.tasks.add(task)
        
        # Clean up task when done
        task.add_done_callback(lambda t: self.tasks.remove(t) if t in self.tasks else None)
        
        return task
        
    async def shutdown_tasks(self) -> None:
        """Cancel all tasks and wait for them to complete."""
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        
    async def call_with_timeout(self, 
                           func: Callable, 
                           *args, 
                           timeout: float = 10.0, 
                           fallback: Optional[Callable] = None, 
                           **kwargs) -> Any:
        """
        Call a function with timeout and optional fallback.
        
        Args:
            func: Function to call
            *args: Arguments for function
            timeout: Timeout in seconds
            fallback: Optional fallback function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            asyncio.TimeoutError: If the function times out and no fallback is provided
        """
        try:
            # Create a timer
            operation_name = func.__name__ if hasattr(func, "__name__") else "operation"
            timer = self.metrics_manager.metrics_manager.create_request_timer(endpoint=operation_name)
            
            # Call function with timeout
            with timer:
                if asyncio.iscoroutinefunction(func):
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                else:
                    return func(*args, **kwargs)
        except asyncio.TimeoutError:
            # Increment timeout counter
            timeout_counter = self.metrics_manager.metrics_manager.registry.get("timeout_count", {"operation": operation_name})
            if not timeout_counter:
                timeout_counter = self.metrics_manager.metrics_manager.registry.create_counter(
                    name="timeout_count",
                    description="Number of operation timeouts",
                    labels={"operation": operation_name}
                )
            timeout_counter.increment()
            
            # Log timeout
            self.logger.warning(
                f"Operation {operation_name} timed out after {timeout} seconds",
                category=LogCategory.PERFORMANCE,
                context={
                    "timeout": timeout,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            
            # Call fallback if provided
            if fallback:
                return await self._call_fallback(fallback, operation_name, args, kwargs)
            else:
                raise
        except Exception as e:
            # Increment error counter
            error_counter = self.metrics_manager.metrics_manager.registry.get("error_count", {"operation": operation_name})
            if not error_counter:
                error_counter = self.metrics_manager.metrics_manager.registry.create_counter(
                    name="error_count",
                    description="Number of operation errors",
                    labels={"operation": operation_name}
                )
            error_counter.increment()
            
            # Log error
            self.logger.error(
                f"Operation {operation_name} failed: {e}",
                category=LogCategory.ERROR,
                exception=e
            )
            
            # Call fallback if provided
            if fallback:
                return await self._call_fallback(fallback, operation_name, args, kwargs)
            else:
                raise
                
    async def _call_fallback(self, fallback: Callable, operation_name: str, args, kwargs):
        """Helper method to call fallback function."""
        try:
            if asyncio.iscoroutinefunction(fallback):
                return await fallback(*args, **kwargs)
            else:
                return fallback(*args, **kwargs)
        except Exception as e:
            self.logger.error(
                f"Fallback for {operation_name} failed: {e}",
                category=LogCategory.ERROR,
                exception=e
            )
            raise
            
    def create_circuit_breaker(self, 
                           name: str, 
                           failure_threshold: int = 5,
                           recovery_timeout: float = 30.0) -> CircuitBreaker:
        """
        Create a circuit breaker for a operation.
        
        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before trying recovery
            
        Returns:
            Circuit breaker
        """
        # Create circuit breaker
        circuit_breaker = CircuitBreaker(
            name=f"{self.component_id}.{name}",
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        
        # Log circuit breaker creation
        self.logger.info(
            f"Created circuit breaker: {name}",
            category=LogCategory.COMPONENT,
            context={
                "failure_threshold": failure_threshold,
                "recovery_timeout": recovery_timeout
            }
        )
        
        return circuit_breaker
