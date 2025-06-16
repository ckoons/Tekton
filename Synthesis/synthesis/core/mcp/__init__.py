"""
Synthesis MCP (Model Context Protocol) integration.

This module provides MCP capabilities and tools for Synthesis's data synthesis,
integration orchestration, and workflow composition functionality.
"""

from .capabilities import (
    DataSynthesisCapability,
    IntegrationOrchestrationCapability,
    WorkflowCompositionCapability
)

from .tools import (
    data_synthesis_tools,
    integration_orchestration_tools,
    workflow_composition_tools
)


def get_all_capabilities():
    """Get all Synthesis MCP capabilities."""
    return [
        DataSynthesisCapability,
        IntegrationOrchestrationCapability,
        WorkflowCompositionCapability
    ]


def get_all_tools():
    """Get all Synthesis MCP tools."""
    return data_synthesis_tools + integration_orchestration_tools + workflow_composition_tools


__all__ = [
    "DataSynthesisCapability",
    "IntegrationOrchestrationCapability", 
    "WorkflowCompositionCapability",
    "data_synthesis_tools",
    "integration_orchestration_tools",
    "workflow_composition_tools",
    "get_all_capabilities",
    "get_all_tools"
]