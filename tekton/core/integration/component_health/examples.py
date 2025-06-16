#!/usr/bin/env python3
"""
Component Health Examples Module

Provides examples of using the ComponentHealthAdapter.
"""

import asyncio
import time
from typing import Dict, Any

from ..component_health import ComponentHealthAdapter
from ...lifecycle import ComponentState


async def example():
    """Example usage of component health adapter."""
    # Create adapter
    adapter = ComponentHealthAdapter(
        component_id="example.service",
        component_name="Example Service",
        component_type="service"
    )
    
    # Start adapter
    await adapter.start()
    
    try:
        # Update state to ready
        adapter.update_state(ComponentState.READY.value, reason="startup.completed", details="Initialization complete")
        
        # Register capabilities
        adapter.register_capability(
            capability_name="process_data",
            handler=lambda data: {"processed": True, "data": data},
            level=100,
            description="Process data with full functionality"
        )
        
        # Update metrics
        adapter.update_metrics({
            "cpu_usage": 0.3,
            "memory_usage": 100 * 1024 * 1024,
            "memory_limit": 1024 * 1024 * 1024,
            "request_count": 100,
            "error_count": 5
        })
        
        # Log a request
        adapter.log_request(
            endpoint="/api/example",
            method="GET",
            status_code=200,
            duration=0.05,
            request_id="req-123",
            correlation_id="corr-456",
            context={"user_id": "user-789"}
        )
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Update metrics to trigger state change
        adapter.update_metrics({
            "cpu_usage": 0.8,
            "memory_usage": 800 * 1024 * 1024,
            "memory_limit": 1024 * 1024 * 1024,
            "request_count": 200,
            "error_count": 20
        })
        
        # Wait a bit more
        await asyncio.sleep(2)
        
    finally:
        # Stop adapter
        await adapter.stop()


async def circuit_breaker_example():
    """Example of using circuit breaker."""
    # Create adapter
    adapter = ComponentHealthAdapter(
        component_id="example.service",
        component_name="Example Service",
        component_type="service"
    )
    
    # Start adapter
    await adapter.start()
    
    try:
        # Create circuit breaker
        circuit_breaker = adapter.create_circuit_breaker(
            name="database_access",
            failure_threshold=3,
            recovery_timeout=5.0
        )
        
        # Define operation function
        async def access_database(query: str) -> Dict[str, Any]:
            # Randomly fail for demonstration
            if time.time() % 3 < 1:
                raise Exception("Database access failed")
                
            return {
                "result": f"Data for {query}",
                "timestamp": time.time()
            }
            
        # Try operations with circuit breaker
        for i in range(10):
            try:
                result = await circuit_breaker.execute(access_database, f"query-{i}")
                print(f"Operation succeeded: {result}")
            except Exception as e:
                print(f"Operation failed: {e}")
                
            await asyncio.sleep(1)
            
    finally:
        # Stop adapter
        await adapter.stop()


if __name__ == "__main__":
    asyncio.run(example())
