#!/usr/bin/env python3
"""
Phase Models - Data models for execution phases.

This module contains enum definitions and data models used by the phase
management system.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set, Callable


class PhaseStatus(str, Enum):
    """Phase execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
