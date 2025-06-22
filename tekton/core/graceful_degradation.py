#!/usr/bin/env python3
"""
Graceful Degradation Module

This module provides capabilities for implementing graceful degradation
when components become unavailable or performance degrades.
"""

import time
import asyncio
import logging
import random
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, TypeVar, Union, Tuple, Set

from .lifecycle import ComponentState
from landmarks import architecture_decision, performance_boundary, integration_point

logger = logging.getLogger("tekton.graceful_degradation")

# Generic type for function return values
T = TypeVar("T")

class CircuitBreakerState(Enum):
    """Circuit breaker state for implementing the circuit breaker pattern."""
    CLOSED = "closed"       # Normal operation, requests go through
    OPEN = "open"           # Failed state, requests are rejected
    HALF_OPEN = "half_open" # Testing state, limited requests go through


@architecture_decision(
    title="Circuit breaker pattern",
    rationale="Prevent cascading failures by automatically failing fast when errors exceed threshold",
    alternatives_considered=["Retry with backoff", "Hard failures", "Rate limiting"])
class CircuitBreaker:
    """
    Implements the circuit breaker pattern for graceful degradation.
    
    Automatically tracks failure rates and opens the circuit when
    too many failures occur, preventing cascading failures.
    """
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 30.0,
                 half_open_max_calls: int = 3):
        """
        Initialize a circuit breaker.
        
        Args:
            name: Name for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before trying recovery
            half_open_max_calls: Maximum calls to allow in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        # State tracking
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
        self.open_time = 0
        self.half_open_calls = 0
        
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function
            
        Raises:
            CircuitBreakerError: If the circuit is open
        """
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.open_time > self.recovery_timeout:
                logger.info(f"Circuit {self.name} transitioning from OPEN to HALF_OPEN")
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise CircuitBreakerError(f"Circuit {self.name} is OPEN")
                
        # If half-open, check if we can allow this call
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise CircuitBreakerError(f"Circuit {self.name} is HALF_OPEN with max calls reached")
            
            self.half_open_calls += 1
        
        # Execute the function
        try:
            start_time = time.time()
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Record success
            self.last_success_time = time.time()
            execution_time = self.last_success_time - start_time
            
            # If half-open and successful, close the circuit
            if self.state == CircuitBreakerState.HALF_OPEN:
                logger.info(f"Circuit {self.name} recovered, transitioning from HALF_OPEN to CLOSED")
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
            
            # Reset failure count after success in closed state
            if self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0
                
            return result
            
        except Exception as e:
            # Record failure
            self.last_failure_time = time.time()
            self.failure_count += 1
            
            # If half-open, go back to open
            if self.state == CircuitBreakerState.HALF_OPEN:
                logger.warning(f"Circuit {self.name} failed in HALF_OPEN state, returning to OPEN")
                self.state = CircuitBreakerState.OPEN
                self.open_time = time.time()
            
            # If closed but exceeded threshold, open the circuit
            elif self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit {self.name} exceeded failure threshold, transitioning to OPEN")
                self.state = CircuitBreakerState.OPEN
                self.open_time = time.time()
            
            # Re-raise the original exception
            raise


class CircuitBreakerError(Exception):
    """Exception raised when a circuit breaker is open."""
    pass


class CapabilityFallback:
    """
    Manages fallback options for component capabilities.
    
    Provides a way to register multiple fallback options for a capability
    with automatic selection based on availability and capability level.
    """
    
    def __init__(self, 
                component_id: str, 
                capability_name: str):
        """
        Initialize a capability fallback.
        
        Args:
            component_id: ID of the component
            capability_name: Name of the capability
        """
        self.component_id = component_id
        self.capability_name = capability_name
        self.fallbacks: Dict[str, Dict[str, Any]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
    def register_fallback(self, 
                         provider_id: str, 
                         handler: Callable,
                         level: int = 100,
                         description: Optional[str] = None) -> None:
        """
        Register a fallback handler.
        
        Args:
            provider_id: ID of the provider component
            handler: Function to call for fallback
            level: Capability level (higher is better)
            description: Optional description
        """
        self.fallbacks[provider_id] = {
            "handler": handler,
            "level": level,
            "description": description or f"Fallback for {self.capability_name} from {provider_id}",
            "last_success": 0,
            "last_failure": 0
        }
        
        # Create circuit breaker
        self.circuit_breakers[provider_id] = CircuitBreaker(
            name=f"{self.component_id}.{self.capability_name}.{provider_id}")
            
        logger.info(f"Registered fallback for {self.component_id}.{self.capability_name} from {provider_id} (level {level})")
        
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the capability with fallback support.
        
        Args:
            *args: Arguments for the handler
            **kwargs: Keyword arguments for the handler
            
        Returns:
            Result from handler
            
        Raises:
            NoFallbackAvailableError: If no fallback is available
        """
        if not self.fallbacks:
            raise NoFallbackAvailableError(f"No fallbacks registered for {self.component_id}.{self.capability_name}")
            
        # Sort fallbacks by level (highest first)
        sorted_fallbacks = sorted(
            self.fallbacks.items(), 
            key=lambda x: x[1]["level"], 
            reverse=True
        )
        
        last_error = None
        
        # Try fallbacks in order
        for provider_id, fallback in sorted_fallbacks:
            handler = fallback["handler"]
            circuit_breaker = self.circuit_breakers[provider_id]
            
            try:
                # Execute with circuit breaker
                result = await circuit_breaker.execute(handler, *args, **kwargs)
                
                # Record success
                fallback["last_success"] = time.time()
                
                return result
                
            except CircuitBreakerError as e:
                # Circuit is open, try next fallback
                logger.debug(f"Circuit breaker for {provider_id} is open, trying next fallback")
                last_error = e
                continue
                
            except Exception as e:
                # Handler failed, record failure
                fallback["last_failure"] = time.time()
                logger.warning(f"Fallback {provider_id} for {self.component_id}.{self.capability_name} failed: {e}")
                last_error = e
                continue
        
        # All fallbacks failed
        raise NoFallbackAvailableError(
            f"All fallbacks for {self.component_id}.{self.capability_name} failed") from last_error


class NoFallbackAvailableError(Exception):
    """Exception raised when no fallback is available."""
    pass


@integration_point(
    title="Graceful degradation registry",
    target_component="All Tekton components",
    protocol="Internal API",
    data_flow="Component requests → Manager → Fallback selection → Handler execution"
)
class GracefulDegradationManager:
    """
    Manager for graceful degradation across components.
    
    Provides a central registry for fallbacks and circuit breakers.
    """
    
    def __init__(self):
        """Initialize the graceful degradation manager."""
        self.capability_fallbacks: Dict[str, Dict[str, CapabilityFallback]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
    def register_capability_fallback(self,
                                  component_id: str,
                                  capability_name: str,
                                  provider_id: str,
                                  handler: Callable,
                                  level: int = 100) -> None:
        """
        Register a fallback for a capability.
        
        Args:
            component_id: ID of the component
            capability_name: Name of the capability
            provider_id: ID of the provider component
            handler: Function to call for fallback
            level: Capability level (higher is better)
        """
        # Initialize component entry if needed
        if component_id not in self.capability_fallbacks:
            self.capability_fallbacks[component_id] = {}
            
        # Initialize capability fallback if needed
        if capability_name not in self.capability_fallbacks[component_id]:
            self.capability_fallbacks[component_id][capability_name] = CapabilityFallback(
                component_id=component_id,
                capability_name=capability_name
            )
            
        # Register fallback
        fallback = self.capability_fallbacks[component_id][capability_name]
        fallback.register_fallback(
            provider_id=provider_id,
            handler=handler,
            level=level
        )
        
    def register_circuit_breaker(self,
                              name: str,
                              failure_threshold: int = 5,
                              recovery_timeout: float = 30.0) -> CircuitBreaker:
        """
        Register a circuit breaker.
        
        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening
            recovery_timeout: Time before recovery attempt
            
        Returns:
            The created circuit breaker
        """
        circuit_breaker = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        
        self.circuit_breakers[name] = circuit_breaker
        return circuit_breaker
        
    async def execute_with_fallback(self,
                               component_id: str,
                               capability_name: str,
                               *args, **kwargs) -> Any:
        """
        Execute a capability with fallback support.
        
        Args:
            component_id: ID of the component
            capability_name: Name of the capability
            *args: Arguments for the handler
            **kwargs: Keyword arguments for the handler
            
        Returns:
            Result from handler
            
        Raises:
            NoFallbackAvailableError: If no fallback is available
        """
        # Check if fallback exists
        if (component_id not in self.capability_fallbacks or
            capability_name not in self.capability_fallbacks[component_id]):
            raise NoFallbackAvailableError(
                f"No fallbacks registered for {component_id}.{capability_name}")
                
        # Execute with fallback
        fallback = self.capability_fallbacks[component_id][capability_name]
        return await fallback.execute(*args, **kwargs)
        
    def get_fallback_status(self, 
                         component_id: Optional[str] = None,
                         capability_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of registered fallbacks.
        
        Args:
            component_id: Optional component ID filter
            capability_name: Optional capability name filter
            
        Returns:
            Status information for fallbacks
        """
        result = {
            "components": {},
            "total_fallbacks": 0
        }
        
        # Filter by component if specified
        components = [component_id] if component_id else self.capability_fallbacks.keys()
        
        for comp_id in components:
            if comp_id not in self.capability_fallbacks:
                continue
                
            result["components"][comp_id] = {"capabilities": {}}
            
            # Filter by capability if specified
            capabilities = ([capability_name] if capability_name and capability_name in self.capability_fallbacks[comp_id]
                           else self.capability_fallbacks[comp_id].keys())
                           
            for cap_name in capabilities:
                if cap_name not in self.capability_fallbacks[comp_id]:
                    continue
                    
                fallback = self.capability_fallbacks[comp_id][cap_name]
                
                # Get status
                providers = []
                for provider_id, fb_info in fallback.fallbacks.items():
                    circuit_breaker = fallback.circuit_breakers[provider_id]
                    
                    providers.append({
                        "provider_id": provider_id,
                        "level": fb_info["level"],
                        "circuit_state": circuit_breaker.state.value,
                        "last_success": fb_info["last_success"],
                        "last_failure": fb_info["last_failure"],
                        "failure_count": circuit_breaker.failure_count
                    })
                    
                    result["total_fallbacks"] += 1
                
                result["components"][comp_id]["capabilities"][cap_name] = {
                    "providers": providers,
                    "provider_count": len(providers)
                }
        
        return result


# Example usage
async def example():
    """Example of graceful degradation."""
    # Create manager
    manager = GracefulDegradationManager()
    
    # Define fallback handlers
    async def primary_handler(value):
        if random.random() < 0.3:
            raise Exception("Primary handler failed")
        return f"Primary: {value}"
    
    async def secondary_handler(value):
        if random.random() < 0.2:
            raise Exception("Secondary handler failed")
        return f"Secondary: {value}"
    
    async def tertiary_handler(value):
        return f"Tertiary: {value}"
    
    # Register fallbacks
    manager.register_capability_fallback(
        component_id="example.service",
        capability_name="process",
        provider_id="primary",
        handler=primary_handler,
        level=100
    )
    
    manager.register_capability_fallback(
        component_id="example.service",
        capability_name="process",
        provider_id="secondary",
        handler=secondary_handler,
        level=50
    )
    
    manager.register_capability_fallback(
        component_id="example.service",
        capability_name="process",
        provider_id="tertiary",
        handler=tertiary_handler,
        level=10
    )
    
    # Execute with fallback
    for i in range(10):
        try:
            result = await manager.execute_with_fallback(
                component_id="example.service",
                capability_name="process",
                value=f"Test {i}"
            )
            print(f"Result {i}: {result}")
        except NoFallbackAvailableError as e:
            print(f"All fallbacks failed: {e}")
            
    # Get status
    status = manager.get_fallback_status()
    print(f"Fallback status: {status}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run example
    asyncio.run(example())