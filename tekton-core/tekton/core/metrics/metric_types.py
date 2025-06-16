#!/usr/bin/env python3
"""
Metric Types Module

This module defines standard metric types, categories, and units
for use in the Tekton metrics system.
"""

from enum import Enum


class MetricType(Enum):
    """Standard metric types for Tekton components."""
    COUNTER = "counter"       # Cumulative value that only increases
    GAUGE = "gauge"           # Value that can increase or decrease
    HISTOGRAM = "histogram"   # Distribution of values
    SUMMARY = "summary"       # Summary statistics (mean, percentiles)
    RATE = "rate"             # Rate of change over time


class MetricCategory(Enum):
    """Standard metric categories for Tekton components."""
    PERFORMANCE = "performance"     # Performance metrics
    RESOURCE = "resource"           # Resource usage metrics
    THROUGHPUT = "throughput"       # Throughput metrics
    LATENCY = "latency"             # Latency metrics
    ERROR = "error"                 # Error metrics
    BUSINESS = "business"           # Business metrics
    SYSTEM = "system"               # System metrics
    COMPONENT = "component"         # Component-specific metrics
    DEPENDENCY = "dependency"       # Dependency metrics


class MetricUnit(Enum):
    """Standard metric units for Tekton components."""
    NONE = "none"                # No unit
    BYTES = "bytes"              # Bytes
    SECONDS = "seconds"          # Seconds
    MILLISECONDS = "ms"          # Milliseconds
    MICROSECONDS = "us"          # Microseconds
    PERCENTAGE = "percent"       # Percentage
    COUNT = "count"              # Count
    OPERATIONS = "ops"           # Operations
    REQUESTS = "requests"        # Requests
    ERRORS = "errors"            # Errors
    KILOBYTES = "kb"             # Kilobytes
    MEGABYTES = "mb"             # Megabytes
    GIGABYTES = "gb"             # Gigabytes