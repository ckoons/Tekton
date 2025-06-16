#!/usr/bin/env python3
"""
Prometheus Metrics Module

This module provides utilities for working with Prometheus metrics
in the Tekton system.
"""

import time
import asyncio
import logging
from typing import Dict, Optional, Any, List

from ..logging_integration import get_logger, LogCategory
from .metrics_manager import MetricsManager
from .metrics_registry import MetricsRegistry

# Configure logger
logger = get_logger("tekton.prometheus")

# Global registry of metrics managers
_metrics_managers: Dict[str, MetricsManager] = {}


def get_metrics_manager(component_id: str) -> MetricsManager:
    """
    Get or create a metrics manager for a component.
    
    Args:
        component_id: Component ID
        
    Returns:
        Metrics manager for component
    """
    if component_id not in _metrics_managers:
        _metrics_managers[component_id] = MetricsManager(component_id)
    return _metrics_managers[component_id]


async def start_all_metrics_managers() -> None:
    """Start all metrics managers."""
    for manager in _metrics_managers.values():
        await manager.start()


async def stop_all_metrics_managers() -> None:
    """Stop all metrics managers."""
    for manager in _metrics_managers.values():
        await manager.stop()


def get_all_metrics() -> Dict[str, Dict[str, Any]]:
    """
    Get all metrics from all managers.
    
    Returns:
        Dictionary of component metrics
    """
    return {
        component_id: manager.registry.to_dict()
        for component_id, manager in _metrics_managers.items()
    }


def get_prometheus_metrics() -> str:
    """
    Get all metrics in Prometheus format.
    
    Returns:
        Prometheus format string
    """
    return "\n\n".join([
        f"# HELP tekton_component_info Information about Tekton component\n"
        f"# TYPE tekton_component_info gauge\n"
        f"tekton_component_info{{component_id=\"{component_id}\"}} 1\n"
        f"{manager.registry.to_prometheus()}"
        for component_id, manager in _metrics_managers.items()
    ])


# Example usage
async def example():
    """Example of Prometheus metrics integration."""
    # Create metrics manager
    metrics = get_metrics_manager("example.component")
    
    # Start metrics reporting
    await metrics.start()
    
    try:
        # Create some metrics
        request_count = metrics.registry.create_counter(
            name="custom_request_count",
            description="Custom request count",
            category="business",
            unit="requests"
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
    asyncio.run(example())