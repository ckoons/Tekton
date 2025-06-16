"""
MCP capabilities for Ergon Agent and Workflow Management System.

This module defines the Model Context Protocol capabilities that Ergon provides
for agent management, workflow orchestration, and task execution.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class AgentManagementCapability(MCPCapability):
    """Capability for AI agent creation, management, and coordination."""
    
    name = "agent_management"
    description = "Create, manage, and coordinate AI agents for various tasks"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_agent",
            "update_agent",
            "delete_agent",
            "get_agent",
            "list_agents",
            "start_agent",
            "stop_agent",
            "configure_agent",
            "monitor_agent_health",
            "get_agent_capabilities"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "agent_orchestration",
            "provider": "ergon",
            "requires_auth": False,
            "rate_limited": True,
            "agent_types": ["conversational", "task_executor", "knowledge_worker", "specialist"],
            "coordination_patterns": ["master_slave", "peer_to_peer", "hierarchical", "swarm"],
            "communication_protocols": ["direct", "message_passing", "shared_memory", "event_driven"],
            "execution_environments": ["local", "container", "cloud", "hybrid"],
            "lifecycle_states": ["created", "configured", "running", "paused", "stopped", "error"]
        }


class WorkflowManagementCapability(MCPCapability):
    """Capability for workflow definition, execution, and monitoring."""
    
    name = "workflow_management"
    description = "Define, execute, and monitor complex workflows and processes"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_workflow",
            "update_workflow",
            "execute_workflow",
            "get_workflow_status",
            "pause_workflow",
            "resume_workflow",
            "cancel_workflow",
            "get_workflow_history",
            "validate_workflow",
            "clone_workflow"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "process_orchestration",
            "provider": "ergon",
            "requires_auth": False,
            "workflow_types": ["sequential", "parallel", "conditional", "loop", "event_driven"],
            "execution_models": ["synchronous", "asynchronous", "hybrid"],
            "control_structures": ["if_then_else", "while", "for_each", "try_catch"],
            "data_flow": ["pipeline", "shared_state", "message_passing", "event_streaming"],
            "monitoring_granularity": ["step", "task", "workflow", "system"]
        }


class TaskManagementCapability(MCPCapability):
    """Capability for task creation, assignment, and tracking."""
    
    name = "task_management"
    description = "Create, assign, and track tasks within workflows and agents"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_task",
            "assign_task",
            "update_task_status",
            "get_task",
            "list_tasks",
            "prioritize_task",
            "schedule_task",
            "cancel_task",
            "get_task_dependencies",
            "track_task_progress"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "task_orchestration",
            "provider": "ergon",
            "requires_auth": False,
            "task_types": ["computation", "communication", "data_processing", "decision_making"],
            "priority_levels": ["low", "normal", "high", "critical", "urgent"],
            "scheduling_algorithms": ["fifo", "priority", "round_robin", "shortest_job_first"],
            "dependency_types": ["sequential", "parallel", "conditional", "resource"],
            "execution_contexts": ["agent", "workflow", "standalone", "distributed"]
        }


class IntegrationCapability(MCPCapability):
    """Capability for integration with other Tekton components and external systems."""
    
    name = "integration"
    description = "Integrate with Tekton ecosystem and external systems"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "register_with_hermes",
            "sync_with_engram",
            "connect_to_prometheus",
            "integrate_external_api",
            "setup_webhooks",
            "configure_message_routing",
            "health_check",
            "get_integration_status"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "system_integration",
            "provider": "ergon",
            "requires_auth": False,
            "integration_types": ["component", "external_api", "database", "message_queue"],
            "communication_protocols": ["http", "websocket", "grpc", "message_queue"],
            "data_formats": ["json", "xml", "protobuf", "avro"],
            "authentication_methods": ["api_key", "oauth", "token", "certificate"],
            "reliability_patterns": ["retry", "circuit_breaker", "timeout", "bulkhead"]
        }


# Export all capabilities
__all__ = [
    "AgentManagementCapability",
    "WorkflowManagementCapability",
    "TaskManagementCapability",
    "IntegrationCapability"
]