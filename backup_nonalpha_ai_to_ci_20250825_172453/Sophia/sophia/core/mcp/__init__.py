"""
Sophia MCP (Model Context Protocol) integration.

This module provides MCP capabilities and tools for Sophia's ML/AI analysis,
research management, and intelligence measurement features.
"""

from .capabilities import (
    MLAnalysisCapability,
    ResearchManagementCapability,
    IntelligenceMeasurementCapability
)

from .tools import (
    ml_analysis_tools,
    research_management_tools,
    intelligence_measurement_tools
)


def get_all_capabilities():
    """Get all Sophia MCP capabilities."""
    return [
        MLAnalysisCapability,
        ResearchManagementCapability,
        IntelligenceMeasurementCapability
    ]


def get_all_tools(ml_engine=None):
    """Get all Sophia MCP tools."""
    # Note: ml_engine parameter is for compatibility with hermes_bridge
    # Sophia's tools are pre-defined and don't need the engine
    tools = ml_analysis_tools + research_management_tools + intelligence_measurement_tools
    
    # Convert MCPTool objects to dictionaries for hermes_bridge compatibility
    tool_dicts = []
    for tool in tools:
        tool_dict = {
            'name': tool.name,
            'description': tool.description,
            'input_schema': tool.input_schema,
            'output_schema': getattr(tool, 'output_schema', {}),
            'handler': tool.handler,
            'tags': getattr(tool, 'tags', []),
            'category': getattr(tool, 'category', 'general')
        }
        tool_dicts.append(tool_dict)
    
    return tool_dicts


__all__ = [
    "MLAnalysisCapability",
    "ResearchManagementCapability",
    "IntelligenceMeasurementCapability",
    "ml_analysis_tools",
    "research_management_tools",
    "intelligence_measurement_tools",
    "get_all_capabilities",
    "get_all_tools"
]