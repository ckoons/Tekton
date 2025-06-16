#!/usr/bin/env python3
"""
Heartbeat Monitor - Hermes connection monitoring and reconnection.

This module provides functionality to monitor the connection to Hermes
and automatically re-register components if Hermes restarts.

This file is maintained for backward compatibility.
Use tekton.core.heartbeat instead for new code.
"""

import asyncio
import logging
import os
import signal
import sys
import time
from typing import Dict, List, Any, Optional, Callable, Set

# Re-export from the new module structure
from .heartbeat.monitor import HeartbeatMonitor
from .heartbeat.client import ComponentHeartbeat
from .heartbeat.component_state import ComponentHealthMetrics
from .heartbeat.metrics import collect_component_metrics, aggregate_health_metrics
from .lifecycle import ComponentState

# Configure logging
logger = logging.getLogger(__name__)


# Example usage with backwards compatibility
async def example():
    """Example usage of enhanced heartbeat monitor."""
    # Create component heartbeat with custom configuration
    heartbeat = ComponentHeartbeat(
        component_id="example.service",
        component_name="Example Service",
        component_type="api",             # Component type affects metrics collection
        heartbeat_interval=10,            # Custom heartbeat interval
        capabilities=[
            {
                "name": "example_capability",
                "description": "Example capability",
                "parameters": {
                    "param1": "string",
                    "param2": "number"
                }
            }
        ],
        metadata={
            "description": "Example component for testing",
            "version": "0.1.0",
            "owner": "tekton-team"
        },
        enable_metrics=True              # Enable metrics collection
    )
    
    # Define a metrics provider function
    def get_system_metrics():
        import random
        # Simulate collecting system metrics
        return {
            "cpu_usage": 0.2 + random.random() * 0.1,        # 20-30% CPU
            "memory_usage": 0.3 + random.random() * 0.1,     # 30-40% Memory
            "request_latency": 50 + random.random() * 10,    # 50-60ms latency
        }
    
    # Add metrics provider
    heartbeat.add_metrics_provider(get_system_metrics)
    
    # Start heartbeat
    result = await heartbeat.start()
    if not result:
        logger.error("Failed to start heartbeat monitor")
        return
    
    try:
        # Simulate component operation with state transitions
        logger.info("Running heartbeat monitor with enhanced state management...")
        
        # Update some custom metrics
        heartbeat.update_custom_metrics({
            "active_connections": 5,
            "queue_depth": 2
        })
        
        # Run for a while
        await asyncio.sleep(10)
        
        # Simulate active state
        heartbeat.set_state(ComponentState.ACTIVE.value, 
                           reason="startup.normal_startup", 
                           details="Component is now processing requests")
        logger.info("Component is now ACTIVE")
        
        # Update metrics to simulate increasing load
        heartbeat.update_custom_metrics({
            "active_connections": 12,
            "queue_depth": 5,
            "throughput": 25.5
        })
        
        # Run for a while more
        await asyncio.sleep(10)
        
        # Simulate temporary degradation
        heartbeat.set_state(ComponentState.DEGRADED.value,
                           reason="degradation.resource_exhaustion",
                           details="High memory usage detected")
        logger.info("Component is now DEGRADED")
        
        # Update metrics to simulate recovery
        heartbeat.update_custom_metrics({
            "active_connections": 8,
            "queue_depth": 3,
            "throughput": 18.2
        })
        
        # Run for a while more
        await asyncio.sleep(10)
        
        # Simulate recovery
        heartbeat.set_state(ComponentState.ACTIVE.value,
                           reason="recovery.resource_restored",
                           details="Memory usage returned to normal")
        logger.info("Component recovered to ACTIVE state")
        
        # Run for a final period
        await asyncio.sleep(10)
        
    finally:
        # Set stopping state before actual stop
        heartbeat.set_state(ComponentState.STOPPING.value, 
                          reason="shutdown.normal",
                          details="Component shutting down normally")
        
        # Stop heartbeat
        await heartbeat.stop()
        logger.info("Heartbeat monitor stopped")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the example
    asyncio.run(example())