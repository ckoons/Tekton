"""
MCP capabilities for Harmonia Workflow Orchestration System.

This module defines the Model Context Protocol capabilities that Harmonia provides
for workflow definition, template management, execution, and component integration.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class WorkflowDefinitionCapability(MCPCapability):
    """Capability for workflow design, definition, and management."""
    
    name = "workflow_definition"
    description = "Design, define, and manage complex workflow structures"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_workflow_definition",
            "update_workflow_definition", 
            "delete_workflow_definition",
            "get_workflow_definition",
            "list_workflow_definitions",
            "validate_workflow_definition",
            "version_workflow_definition",
            "export_workflow_definition",
            "import_workflow_definition"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "workflow_design",
            "provider": "harmonia",
            "requires_auth": False,
            "rate_limited": True,
            "workflow_patterns": ["sequential", "parallel", "conditional", "event_driven", "state_machine"],
            "definition_formats": ["yaml", "json", "dsl", "graphical"],
            "validation_levels": ["syntax", "semantic", "resource", "compatibility"],
            "versioning_strategy": ["semantic", "incremental", "date_based"],
            "complexity_levels": ["simple", "moderate", "complex", "enterprise"]
        }


class WorkflowExecutionCapability(MCPCapability):
    """Capability for workflow execution, monitoring, and control."""
    
    name = "workflow_execution"
    description = "Execute, monitor, and control workflow instances"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "execute_workflow",
            "cancel_workflow",
            "pause_workflow",
            "resume_workflow",
            "get_workflow_status",
            "list_workflow_executions",
            "get_execution_history",
            "restart_workflow",
            "get_execution_logs"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "workflow_runtime",
            "provider": "harmonia",
            "requires_auth": False,
            "execution_modes": ["synchronous", "asynchronous", "scheduled", "event_triggered"],
            "runtime_environments": ["local", "distributed", "cloud", "hybrid"],
            "monitoring_granularity": ["step", "task", "workflow", "system"],
            "control_operations": ["start", "stop", "pause", "resume", "restart", "abort"],
            "state_persistence": ["memory", "database", "file", "distributed_cache"]
        }


class TemplateManagementCapability(MCPCapability):
    """Capability for workflow template creation and management."""
    
    name = "template_management"
    description = "Create, manage, and instantiate workflow templates"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_workflow_template",
            "instantiate_template",
            "list_workflow_templates",
            "update_template",
            "delete_template",
            "validate_template",
            "share_template",
            "import_template",
            "export_template"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "template_system",
            "provider": "harmonia",
            "requires_auth": False,
            "template_types": ["basic", "parametric", "conditional", "reusable", "library"],
            "parameterization": ["static", "dynamic", "computed", "user_input"],
            "sharing_scopes": ["private", "team", "organization", "public"],
            "template_categories": ["data_processing", "ml_pipeline", "integration", "automation"],
            "instantiation_modes": ["immediate", "scheduled", "on_demand", "event_triggered"]
        }


class ComponentIntegrationCapability(MCPCapability):
    """Capability for integrating with Tekton components and external systems."""
    
    name = "component_integration"
    description = "Integrate workflows with Tekton components and external systems"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "list_available_components",
            "get_component_actions",
            "execute_component_action",
            "register_custom_component",
            "configure_integration",
            "test_integration",
            "monitor_component_health",
            "sync_component_state"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "system_integration",
            "provider": "harmonia",
            "requires_auth": False,
            "supported_components": ["hermes", "ergon", "engram", "prometheus", "athena", "rhetor"],
            "integration_patterns": ["direct_call", "message_passing", "event_subscription", "polling"],
            "data_exchange": ["json", "xml", "binary", "stream"],
            "error_handling": ["retry", "fallback", "circuit_breaker", "dead_letter"],
            "authentication": ["none", "api_key", "oauth", "certificate", "token"]
        }


# Export all capabilities
__all__ = [
    "WorkflowDefinitionCapability",
    "WorkflowExecutionCapability",
    "TemplateManagementCapability",
    "ComponentIntegrationCapability"
]