"""
MCP capability definitions for Prometheus planning and analysis.

This module defines the FastMCP capabilities that group related
planning and analysis tools.
"""

from tekton.mcp.fastmcp.decorators import mcp_capability


# Planning Capability - Project planning and timeline creation
@mcp_capability(
    name="planning",
    description="Project planning and timeline management including plan creation, milestone tracking, and timeline optimization"
)
class PlanningCapability:
    """Capability for project planning and timeline management."""
    pass


# Retrospective Analysis Capability - Analysis of completed work and performance
@mcp_capability(
    name="retrospective_analysis", 
    description="Retrospective analysis of completed projects including performance metrics, lessons learned, and improvement identification"
)
class RetrospectiveAnalysisCapability:
    """Capability for retrospective analysis and performance review."""
    pass


# Resource Management Capability - Resource allocation and optimization
@mcp_capability(
    name="resource_management",
    description="Resource allocation and management including capacity planning, resource optimization, and constraint analysis"
)
class ResourceManagementCapability:
    """Capability for resource allocation and management."""
    pass


# Improvement Recommendations Capability - AI-driven improvement suggestions
@mcp_capability(
    name="improvement_recommendations",
    description="AI-driven improvement recommendations including process optimization, efficiency improvements, and best practice suggestions"
)
class ImprovementRecommendationsCapability:
    """Capability for generating improvement recommendations."""
    pass