#!/usr/bin/env python3
"""
Resource monitoring configuration classes.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ResourceThreshold:
    """
    Thresholds for resource monitoring alerts.
    
    Attributes:
        warning: Warning threshold value
        critical: Critical threshold value
    """
    warning: float
    critical: float
    

@dataclass
class ResourceConfig:
    """
    Configuration for resource monitoring.
    
    Attributes:
        cpu_threshold: CPU usage threshold
        memory_threshold: Memory usage threshold
        disk_threshold: Disk usage threshold
        network_threshold_mbps: Network throughput threshold in Mbps
        gpu_threshold: GPU usage threshold (if available)
        check_interval_seconds: How often to check resource usage
        alert_cooldown_seconds: Time between repeated alerts
        retention_hours: How long to keep historical metrics
        component_thresholds: Component-specific thresholds
    """
    cpu_threshold: ResourceThreshold = field(default_factory=lambda: ResourceThreshold(70.0, 90.0))
    memory_threshold: ResourceThreshold = field(default_factory=lambda: ResourceThreshold(75.0, 90.0))
    disk_threshold: ResourceThreshold = field(default_factory=lambda: ResourceThreshold(80.0, 95.0))
    network_threshold_mbps: ResourceThreshold = field(default_factory=lambda: ResourceThreshold(100.0, 200.0))
    gpu_threshold: ResourceThreshold = field(default_factory=lambda: ResourceThreshold(70.0, 90.0))
    check_interval_seconds: float = 5.0
    alert_cooldown_seconds: float = 300.0  # 5 minutes between repeated alerts
    retention_hours: int = 24
    
    # Component-specific thresholds
    component_thresholds: Dict[str, Dict[str, ResourceThreshold]] = field(default_factory=dict)
