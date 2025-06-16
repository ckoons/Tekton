#!/usr/bin/env python3
"""
Metrics Integration Module

This module provides standardized metrics collection, aggregation,
and integration with the monitoring system for all Tekton components.

This module is maintained for backward compatibility.
New code should use the metrics package directly.
"""

import asyncio
from typing import Dict, Optional, Any, List

# Re-export all types from the metrics package
from .metrics.metric_types import MetricType, MetricCategory, MetricUnit
from .metrics.metrics import Metric, Counter, Gauge, Histogram, Timer
from .metrics.metrics_registry import MetricsRegistry
from .metrics.metrics_manager import MetricsManager
from .metrics.prometheus import get_metrics_manager, start_all_metrics_managers, stop_all_metrics_managers

# For backward compatibility
def example():
    """Example of metrics integration."""
    return asyncio.run(_example())


async def _example():
    """Example of metrics integration."""
    # Create metrics manager
    metrics = get_metrics_manager("example.component")
    
    # Start metrics reporting
    await metrics.start()
    
    try:
        # Create some metrics
        request_count = metrics.registry.create_counter(
            name="custom_request_count",
            description="Custom request count",
            category=MetricCategory.BUSINESS,
            unit=MetricUnit.REQUESTS
        )
        
        # Increment counter
        request_count.increment()
        
        # Record a request
        metrics.record_request(endpoint="/api/test", duration=0.1, status_code=200)
        
        # Record an error
        metrics.record_request(endpoint="/api/error", duration=0.5, status_code=500, is_error=True)
        
        # Use a timer
        timer = metrics.create_request_timer(endpoint="/api/timed")
        with timer:
            # Simulate work
            await asyncio.sleep(0.2)
            
        # Wait a bit to allow metrics to be reported
        await asyncio.sleep(2)
        
    finally:
        # Stop metrics reporting
        await metrics.stop()


if __name__ == "__main__":
    asyncio.run(_example())