"""
Terma MCP (Model Context Protocol) integration.

This module provides MCP capabilities and tools for Terma's terminal management,
LLM integration, and system integration functionality.
"""

from .capabilities import (
    TerminalManagementCapability,
    LLMIntegrationCapability,
    SystemIntegrationCapability
)

from .tools import (
    terminal_management_tools,
    llm_integration_tools,
    system_integration_tools
)


def get_all_capabilities():
    """Get all Terma MCP capabilities."""
    return [
        TerminalManagementCapability,
        LLMIntegrationCapability,
        SystemIntegrationCapability
    ]


def get_all_tools():
    """Get all Terma MCP tools."""
    return terminal_management_tools + llm_integration_tools + system_integration_tools


__all__ = [
    "TerminalManagementCapability",
    "LLMIntegrationCapability", 
    "SystemIntegrationCapability",
    "terminal_management_tools",
    "llm_integration_tools",
    "system_integration_tools",
    "get_all_capabilities",
    "get_all_tools"
]