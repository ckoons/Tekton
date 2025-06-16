"""
MCP capabilities for Synthesis.

This module defines the Model Context Protocol capabilities that Synthesis provides
for data synthesis, integration orchestration, and workflow composition.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class DataSynthesisCapability(MCPCapability):
    """Capability for data synthesis and unification across components."""
    
    name: str = "data_synthesis"
    description: str = "Synthesize and unify data from multiple components and sources"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "synthesize_component_data",
            "create_unified_report",
            "merge_data_streams",
            "detect_data_conflicts",
            "optimize_data_flow",
            "validate_synthesis_quality"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "data_synthesis",
            "provider": "synthesis",
            "requires_auth": False,
            "rate_limited": True,
            "synthesis_types": ["component_data", "metrics", "logs", "events"],
            "data_formats": ["json", "csv", "metrics", "time_series"],
            "aggregation_methods": ["merge", "average", "sum", "join", "union"],
            "quality_metrics": ["completeness", "consistency", "accuracy", "freshness"]
        }


class IntegrationOrchestrationCapability(MCPCapability):
    """Capability for orchestrating complex component integrations."""
    
    name: str = "integration_orchestration"
    description: str = "Orchestrate and manage complex integrations between components"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "orchestrate_component_integration",
            "design_integration_workflow",
            "monitor_integration_health",
            "resolve_integration_conflicts",
            "optimize_integration_performance",
            "validate_integration_completeness"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "integration_orchestration",
            "provider": "synthesis",
            "requires_auth": False,
            "integration_patterns": ["point_to_point", "hub_spoke", "event_driven", "api_gateway"],
            "orchestration_modes": ["synchronous", "asynchronous", "batch", "streaming"],
            "monitoring_levels": ["basic", "detailed", "comprehensive"],
            "conflict_resolution": ["automatic", "manual", "priority_based", "consensus"]
        }


class WorkflowCompositionCapability(MCPCapability):
    """Capability for composing and executing multi-component workflows."""
    
    name: str = "workflow_composition"
    description: str = "Compose and execute complex workflows across multiple components"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "compose_multi_component_workflow",
            "execute_composed_workflow",
            "analyze_workflow_performance",
            "optimize_workflow_execution"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "workflow_composition",
            "provider": "synthesis",
            "requires_auth": False,
            "workflow_types": ["sequential", "parallel", "conditional", "iterative"],
            "execution_modes": ["immediate", "scheduled", "triggered", "continuous"],
            "composition_patterns": ["pipeline", "fan_out", "fan_in", "scatter_gather"],
            "optimization_goals": ["speed", "reliability", "cost", "resource_efficiency"]
        }


# Export all capabilities
__all__ = [
    "DataSynthesisCapability",
    "IntegrationOrchestrationCapability",
    "WorkflowCompositionCapability"
]