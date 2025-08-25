"""
Rhetor MCP (Model Context Protocol) integration.

This module provides MCP capabilities and tools for Rhetor's LLM management,
prompt engineering, context management, and CI orchestration features.
"""

from .capabilities import (
    LLMManagementCapability,
    PromptEngineeringCapability,
    ContextManagementCapability,
    CIOrchestrationCapability
)

from .tools import (
    llm_management_tools,
    prompt_engineering_tools,
    context_management_tools,
    ai_orchestration_tools
)


def get_all_capabilities():
    """Get all Rhetor MCP capabilities."""
    return [
        LLMManagementCapability,
        PromptEngineeringCapability,
        ContextManagementCapability,
        CIOrchestrationCapability
    ]


def get_all_tools():
    """Get all Rhetor MCP tools."""
    return llm_management_tools + prompt_engineering_tools + context_management_tools + ai_orchestration_tools


__all__ = [
    "LLMManagementCapability",
    "PromptEngineeringCapability", 
    "ContextManagementCapability",
    "AIOrchestrationCapability",
    "llm_management_tools",
    "prompt_engineering_tools",
    "context_management_tools",
    "ai_orchestration_tools",
    "get_all_capabilities",
    "get_all_tools"
]