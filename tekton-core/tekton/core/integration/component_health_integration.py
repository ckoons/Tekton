#!/usr/bin/env python3
"""
Component Health Integration Module

This module integrates the component lifecycle management with metrics,
logging, and health monitoring to provide a comprehensive view of component health.
"""

import asyncio
from .component_health import ComponentHealthAdapter
from .component_health.examples import example, circuit_breaker_example

# Re-export for backward compatibility
__all__ = ['ComponentHealthAdapter']

if __name__ == "__main__":
    asyncio.run(example())