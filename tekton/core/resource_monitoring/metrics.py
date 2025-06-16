#!/usr/bin/env python3
"""
Resource metrics data model and utility functions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class ResourceMetrics:
    """
    Current resource usage metrics.
    
    Attributes:
        timestamp: When the metrics were collected
        cpu_percent: CPU usage percentage
        memory_percent: Memory usage percentage
        disk_percent: Disk usage percentage by mount point
        network_mbps: Network throughput in Mbps by interface
        gpu_percent: GPU usage percentage by device (if available)
        component_metrics: Component-specific metrics
    """
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: Dict[str, float]
    network_mbps: Dict[str, float]
    gpu_percent: Optional[Dict[str, float]] = None
    component_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    @property
    def as_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_percent": self.disk_percent,
            "network_mbps": self.network_mbps,
            "gpu_percent": self.gpu_percent,
            "component_metrics": self.component_metrics
        }
