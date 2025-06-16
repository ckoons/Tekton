"""
MCP capabilities for Telos.

This module defines the Model Context Protocol capabilities that Telos provides
for strategic planning, goal management, and decision support.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class StrategicAnalysisCapability(MCPCapability):
    """Capability for strategic analysis and planning operations."""
    
    name: str = "strategic_analysis"
    description: str = "Analyze strategic landscape, feasibility, and outcomes"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "analyze_strategic_landscape",
            "assess_goal_feasibility",
            "predict_planning_outcomes",
            "evaluate_resource_allocation",
            "generate_strategic_insights",
            "optimize_planning_approach"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "strategic_analysis",
            "provider": "telos",
            "requires_auth": False,
            "rate_limited": True,
            "analysis_types": ["competitive", "market", "resource", "capability", "risk"],
            "planning_horizons": ["short_term", "medium_term", "long_term"],
            "assessment_criteria": ["feasibility", "impact", "risk", "cost", "timeline"],
            "insight_categories": ["opportunities", "threats", "strengths", "weaknesses", "trends"]
        }


class GoalManagementCapability(MCPCapability):
    """Capability for strategic goal creation, tracking, and management."""
    
    name: str = "goal_management"
    description: str = "Create, track, and manage strategic goals and objectives"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "create_strategic_goals",
            "track_goal_progress",
            "manage_goal_dependencies",
            "prioritize_objectives",
            "align_component_goals",
            "validate_goal_achievement"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "goal_management",
            "provider": "telos",
            "requires_auth": False,
            "goal_types": ["strategic", "tactical", "operational", "performance"],
            "priority_levels": ["critical", "high", "medium", "low"],
            "tracking_methods": ["milestone", "kpi", "okr", "balanced_scorecard"],
            "alignment_scopes": ["organization", "component", "team", "individual"],
            "validation_criteria": ["smart", "measurable", "achievable", "relevant", "timebound"]
        }


class DecisionSupportCapability(MCPCapability):
    """Capability for strategic decision support and scenario analysis."""
    
    name: str = "decision_support"
    description: str = "Support strategic decision-making and planning"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "support_strategic_decisions",
            "analyze_decision_scenarios",
            "recommend_planning_actions",
            "evaluate_planning_effectiveness"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "decision_support",
            "provider": "telos",
            "requires_auth": False,
            "decision_types": ["strategic", "investment", "resource_allocation", "priority_setting"],
            "analysis_methods": ["scenario", "sensitivity", "monte_carlo", "decision_tree"],
            "recommendation_categories": ["action", "timing", "resource", "risk_mitigation"],
            "effectiveness_metrics": ["goal_achievement", "resource_efficiency", "timeline_adherence", "roi"]
        }


# Export all capabilities
__all__ = [
    "StrategicAnalysisCapability",
    "GoalManagementCapability",
    "DecisionSupportCapability"
]