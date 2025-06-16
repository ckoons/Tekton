"""
MCP capability definitions for Metis task management.

This module defines the FastMCP capabilities that group related
task management tools.
"""

from tekton.mcp.fastmcp import mcp_capability


# Task Management Capability - Core CRUD operations for tasks
@mcp_capability(
    name="task_management",
    description="Core task management operations including creation, reading, updating, and deletion of tasks"
)
class TaskManagementCapability:
    """Capability for basic task CRUD operations."""
    name: str = "task_management"
    description: str = "Core task management operations including creation, reading, updating, and deletion of tasks"
    version: str = "1.0.0"


# Dependency Management Capability - Task dependency and relationship management
@mcp_capability(
    name="dependency_management", 
    description="Task dependency management including creation and analysis of task relationships and dependencies"
)
class DependencyManagementCapability:
    """Capability for task dependency management."""
    name: str = "dependency_management"
    description: str = "Task dependency management including creation and analysis of task relationships and dependencies"
    version: str = "1.0.0"


# Task Analytics Capability - Analysis and reporting on tasks
@mcp_capability(
    name="task_analytics",
    description="Task analytics and reporting including complexity analysis, status tracking, and performance metrics"
)
class TaskAnalyticsCapability:
    """Capability for task analysis and reporting."""
    name: str = "task_analytics"
    description: str = "Task analytics and reporting including complexity analysis, status tracking, and performance metrics"
    version: str = "1.0.0"


# Telos Integration Capability - Requirements integration
@mcp_capability(
    name="telos_integration",
    description="Integration with Telos requirements management system for importing and linking requirements to tasks"
)
class TelosIntegrationCapability:
    """Capability for Telos requirements integration."""
    name: str = "telos_integration"
    description: str = "Integration with Telos requirements management system for importing and linking requirements to tasks"
    version: str = "1.0.0"