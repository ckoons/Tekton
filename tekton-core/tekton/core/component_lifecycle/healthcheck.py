#!/usr/bin/env python3
"""
Component Health Check Module

This module provides functionality for monitoring component health 
and handling heartbeats from components.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

from ..lifecycle import ComponentState
from ..registry import _save_registrations
from .heartbeat import process_heartbeat
from .monitor import monitor_component_health
from .recovery import attempt_component_recovery

logger = logging.getLogger("tekton.component_lifecycle.healthcheck")

# Re-export key functions to maintain backward compatibility
__all__ = [
    "monitor_component_health",
    "process_heartbeat",
    "attempt_component_recovery"
]
