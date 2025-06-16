"""
Telos MCP (Model Context Protocol) integration.

This module provides MCP capabilities and tools for Telos's strategic planning,
goal management, and decision support functionality.
"""

from .capabilities import (
    StrategicAnalysisCapability,
    GoalManagementCapability,
    DecisionSupportCapability
)

from .tools import (
    requirements_management_tools,
    requirement_tracing_tools,
    requirement_validation_tools,
    prometheus_integration_tools
)


def get_all_capabilities():
    """Get all Telos MCP capabilities."""
    return [
        StrategicAnalysisCapability,
        GoalManagementCapability,
        DecisionSupportCapability
    ]


def get_all_tools():
    """Get all Telos MCP tools."""
    return (requirements_management_tools + requirement_tracing_tools + 
            requirement_validation_tools + prometheus_integration_tools)


__all__ = [
    "StrategicAnalysisCapability",
    "GoalManagementCapability", 
    "DecisionSupportCapability",
    "requirements_management_tools",
    "requirement_tracing_tools",
    "requirement_validation_tools",
    "prometheus_integration_tools",
    "get_all_capabilities",
    "get_all_tools"
]