"""
Synthesis - Execution and Integration Engine for Tekton

This package provides execution capabilities for the Tekton ecosystem,
handling process execution, workflow management, and integration with external systems.
"""

__version__ = "1.0.0"
__author__ = "Tekton Team"

# Import core components for easier access
from .core.execution_models import (
    ExecutionStage, ExecutionStatus, ExecutionPriority,
    ExecutionResult, ExecutionPlan, ExecutionContext
)
from .core.execution_engine import ExecutionEngine

# Version information tuple
VERSION = (1, 0, 0)
VERSION_STRING = ".".join(str(x) for x in VERSION)

# Set default logging handler to avoid "No handler found" warnings
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())