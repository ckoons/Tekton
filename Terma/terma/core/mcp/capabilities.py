"""
MCP capabilities for Terma.

This module defines the Model Context Protocol capabilities that Terma provides
for terminal management, LLM integration, and system integration.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class TerminalManagementCapability(MCPCapability):
    """Capability for creating, managing, and monitoring terminal sessions."""

    name: str = "terminal_management"
    description: str = "Create, manage, and monitor terminal sessions and commands"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_terminal_session",
            "manage_session_lifecycle",
            "execute_terminal_commands",
            "monitor_session_performance",
            "configure_terminal_settings",
            "backup_session_state"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "terminal_management",
            "provider": "terma",
            "requires_auth": False,
            "rate_limited": True,
            "session_types": ["bash", "zsh", "fish", "python", "node"],
            "pty_support": True,
            "websocket_communication": True,
            "session_persistence": True,
            "shell_environments": ["linux", "macos", "wsl"],
            "features": ["command_history", "session_recovery", "process_monitoring"]
        }


class LLMIntegrationCapability(MCPCapability):
    """Capability for AI-powered terminal assistance and analysis."""

    name: str = "llm_integration"
    description: str = "Provide AI-powered assistance and analysis for terminal operations"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "provide_command_assistance",
            "analyze_terminal_output",
            "suggest_command_improvements",
            "detect_terminal_issues",
            "generate_terminal_workflows",
            "optimize_llm_interactions"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "llm_integration",
            "provider": "terma",
            "requires_auth": False,
            "llm_providers": ["claude", "openai", "local_models"],
            "assistance_types": ["command_help", "error_analysis", "workflow_generation"],
            "output_analysis": ["error_detection", "performance_insights", "security_checks"],
            "interaction_modes": ["real_time", "batch", "on_demand"],
            "context_awareness": True
        }


class SystemIntegrationCapability(MCPCapability):
    """Capability for integrating terminal sessions with Tekton ecosystem."""

    name: str = "system_integration"
    description: str = "Integrate terminal sessions with Tekton ecosystem and system components"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "integrate_with_tekton_components",
            "synchronize_session_data",
            "manage_terminal_security",
            "track_terminal_metrics"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "system_integration",
            "provider": "terma",
            "requires_auth": False,
            "integration_targets": ["hermes", "hephaestus", "engram", "llm_adapter"],
            "data_synchronization": ["session_state", "command_history", "performance_metrics"],
            "security_features": ["access_control", "audit_logging", "permission_management"],
            "metrics_tracking": ["usage_statistics", "performance_data", "error_rates"],
            "event_handling": True
        }


# Export all capabilities
__all__ = [
    "TerminalManagementCapability",
    "LLMIntegrationCapability",
    "SystemIntegrationCapability"
]