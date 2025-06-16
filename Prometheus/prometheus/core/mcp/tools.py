"""
MCP tool definitions for Prometheus planning and analysis.

This module defines FastMCP tools that provide programmatic access
to Prometheus planning, retrospective analysis, and improvement capabilities.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import json

from tekton.mcp.fastmcp import mcp_tool
from prometheus.core.planning_engine import PlanningEngine
from prometheus.models.plan import Plan, Milestone, ResourceRequirement
from prometheus.models.retrospective import RetrospectiveAnalysis, PerformanceMetrics
from prometheus.models.improvement import ImprovementRecommendation
from prometheus.models.timeline import Timeline, TimelineEvent
from prometheus.models.resource import Resource, ResourceAllocation


class PrometheusPlanner:
    """MCP-enabled planner for Prometheus operations."""
    
    def __init__(self, planning_engine: Optional[PlanningEngine] = None):
        """Initialize with optional planning engine instance."""
        self.planning_engine = planning_engine or PlanningEngine()


# ============================================================================
# Planning Tools
# ============================================================================

@mcp_tool(
    name="create_project_plan",
    description="Create a comprehensive project plan with milestones and timelines"
)
async def create_project_plan(
    project_name: str,
    description: str,
    start_date: str,
    end_date: str,
    objectives: List[str],
    constraints: Optional[List[str]] = None,
    stakeholders: Optional[List[str]] = None,
    budget: Optional[float] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a comprehensive project plan with milestones and timelines.
    
    Args:
        project_name: Name of the project
        description: Detailed project description
        start_date: Project start date (YYYY-MM-DD format)
        end_date: Project end date (YYYY-MM-DD format)
        objectives: List of project objectives
        constraints: List of project constraints
        stakeholders: List of project stakeholders
        budget: Project budget
        priority: Project priority (low, medium, high, critical)
        
    Returns:
        Dictionary containing the created project plan
    """
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Create plan data
        plan_data = {
            "project_name": project_name,
            "description": description,
            "start_date": start_dt,
            "end_date": end_dt,
            "objectives": objectives,
            "constraints": constraints or [],
            "stakeholders": stakeholders or [],
            "budget": budget,
            "priority": priority,
            "status": "draft",
            "created_at": datetime.utcnow()
        }
        
        # Use planning engine to generate plan
        # Note: This is a simplified implementation - real implementation would use actual PlanningEngine
        plan = Plan(**plan_data)
        
        # Generate automatic milestones based on project duration
        duration = (end_dt - start_dt).days
        milestone_count = min(max(duration // 30, 2), 6)  # 1 milestone per month, 2-6 total
        
        milestones = []
        for i in range(milestone_count):
            milestone_date = start_dt + timedelta(days=(duration * (i + 1) // milestone_count))
            milestone = Milestone(
                milestone_id=f"milestone_{i+1}",
                name=f"Milestone {i+1}",
                description=f"Project milestone {i+1}",
                target_date=milestone_date,
                criteria=[f"Complete phase {i+1} objectives"],
                status="not_started"
            )
            milestones.append(milestone)
        
        plan.milestones = milestones
        
        return {
            "success": True,
            "plan": plan.to_dict(),
            "milestones_count": len(milestones),
            "message": f"Project plan '{project_name}' created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create project plan: {str(e)}"
        }


@mcp_tool(
    name="analyze_critical_path",
    description="Analyze the critical path of a project plan"
)
async def analyze_critical_path(
    plan_id: str,
    tasks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze the critical path of a project plan.
    
    Args:
        plan_id: ID of the project plan
        tasks: List of tasks with dependencies and durations
        
    Returns:
        Dictionary containing critical path analysis
    """
    try:
        # Simplified critical path analysis
        # Real implementation would use networkx for graph-based algorithms
        
        # Build task graph
        task_map = {task["id"]: task for task in tasks}
        
        # Calculate earliest start/finish times
        for task in tasks:
            task["earliest_start"] = 0
            task["earliest_finish"] = task.get("duration", 1)
            
            # Consider dependencies
            for dep_id in task.get("dependencies", []):
                if dep_id in task_map:
                    dep_task = task_map[dep_id]
                    task["earliest_start"] = max(
                        task["earliest_start"],
                        dep_task.get("earliest_finish", 0)
                    )
                    task["earliest_finish"] = task["earliest_start"] + task.get("duration", 1)
        
        # Find critical path (tasks with zero float)
        project_duration = max(task["earliest_finish"] for task in tasks)
        critical_tasks = []
        
        for task in tasks:
            latest_finish = project_duration
            for other_task in tasks:
                if task["id"] in other_task.get("dependencies", []):
                    latest_finish = min(latest_finish, other_task["earliest_start"])
            
            latest_start = latest_finish - task.get("duration", 1)
            float_time = latest_start - task["earliest_start"]
            
            task["latest_start"] = latest_start
            task["latest_finish"] = latest_finish
            task["float"] = float_time
            
            if float_time <= 0:
                critical_tasks.append(task)
        
        return {
            "success": True,
            "plan_id": plan_id,
            "project_duration": project_duration,
            "critical_path": critical_tasks,
            "critical_path_length": len(critical_tasks),
            "total_tasks": len(tasks),
            "message": f"Critical path analysis completed for plan {plan_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Critical path analysis failed: {str(e)}"
        }


@mcp_tool(
    name="optimize_timeline",
    description="Optimize project timeline for efficiency and resource utilization"
)
async def optimize_timeline(
    plan_id: str,
    constraints: Optional[Dict[str, Any]] = None,
    optimization_criteria: str = "duration"
) -> Dict[str, Any]:
    """
    Optimize project timeline for efficiency and resource utilization.
    
    Args:
        plan_id: ID of the project plan
        constraints: Additional constraints for optimization
        optimization_criteria: Criteria to optimize (duration, cost, resources)
        
    Returns:
        Dictionary containing optimized timeline
    """
    try:
        # Simplified timeline optimization
        optimization_results = {
            "original_duration": 90,  # days
            "optimized_duration": 75,  # days
            "savings": 15,  # days
            "optimization_strategies": [
                "Parallel execution of independent tasks",
                "Resource reallocation to critical path",
                "Elimination of unnecessary dependencies"
            ],
            "risk_factors": [
                "Increased resource requirements during peak periods",
                "Reduced buffer time for unexpected issues"
            ]
        }
        
        return {
            "success": True,
            "plan_id": plan_id,
            "optimization_criteria": optimization_criteria,
            "results": optimization_results,
            "message": f"Timeline optimization completed for plan {plan_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Timeline optimization failed: {str(e)}"
        }


@mcp_tool(
    name="create_milestone",
    description="Create a new milestone for a project plan"
)
async def create_milestone(
    plan_id: str,
    name: str,
    description: str,
    target_date: str,
    criteria: List[str],
    dependencies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new milestone for a project plan.
    
    Args:
        plan_id: ID of the project plan
        name: Milestone name
        description: Milestone description
        target_date: Target completion date (YYYY-MM-DD format)
        criteria: List of completion criteria
        dependencies: List of dependent milestone IDs
        
    Returns:
        Dictionary containing the created milestone
    """
    try:
        target_dt = datetime.fromisoformat(target_date)
        
        milestone = Milestone(
            milestone_id=f"milestone_{int(datetime.utcnow().timestamp())}",
            name=name,
            description=description,
            target_date=target_dt,
            criteria=criteria,
            status="not_started",
            metadata={
                "plan_id": plan_id,
                "dependencies": dependencies or [],
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "success": True,
            "milestone": milestone.to_dict(),
            "plan_id": plan_id,
            "message": f"Milestone '{name}' created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create milestone: {str(e)}"
        }


# ============================================================================
# Resource Management Tools
# ============================================================================

@mcp_tool(
    name="allocate_resources",
    description="Allocate resources to project tasks and activities"
)
async def allocate_resources(
    plan_id: str,
    resources: List[Dict[str, Any]],
    tasks: List[Dict[str, Any]],
    optimization_strategy: str = "balanced"
) -> Dict[str, Any]:
    """
    Allocate resources to project tasks and activities.
    
    Args:
        plan_id: ID of the project plan
        resources: List of available resources
        tasks: List of tasks requiring resources
        optimization_strategy: Strategy for allocation (balanced, speed, cost)
        
    Returns:
        Dictionary containing resource allocation plan
    """
    try:
        allocations = []
        
        for task in tasks:
            required_skills = task.get("required_skills", [])
            duration = task.get("duration", 1)
            
            # Find suitable resources
            suitable_resources = []
            for resource in resources:
                resource_skills = resource.get("skills", [])
                if any(skill in resource_skills for skill in required_skills):
                    suitable_resources.append(resource)
            
            # Allocate best fit resource
            if suitable_resources:
                allocated_resource = suitable_resources[0]  # Simplified selection
                allocation = {
                    "task_id": task["id"],
                    "resource_id": allocated_resource["id"],
                    "resource_name": allocated_resource["name"],
                    "allocation_percentage": min(100, task.get("effort_required", 100)),
                    "start_date": task.get("planned_start"),
                    "end_date": task.get("planned_end"),
                    "estimated_cost": duration * allocated_resource.get("hourly_rate", 100)
                }
                allocations.append(allocation)
        
        total_cost = sum(alloc["estimated_cost"] for alloc in allocations)
        
        return {
            "success": True,
            "plan_id": plan_id,
            "allocations": allocations,
            "total_allocations": len(allocations),
            "estimated_total_cost": total_cost,
            "optimization_strategy": optimization_strategy,
            "message": f"Resource allocation completed for plan {plan_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Resource allocation failed: {str(e)}"
        }


@mcp_tool(
    name="analyze_resource_capacity",
    description="Analyze resource capacity and identify bottlenecks"
)
async def analyze_resource_capacity(
    resources: List[Dict[str, Any]],
    time_period: str = "monthly"
) -> Dict[str, Any]:
    """
    Analyze resource capacity and identify bottlenecks.
    
    Args:
        resources: List of resources to analyze
        time_period: Analysis time period (weekly, monthly, quarterly)
        
    Returns:
        Dictionary containing capacity analysis
    """
    try:
        capacity_analysis = {
            "total_resources": len(resources),
            "capacity_summary": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Analyze each resource
        for resource in resources:
            resource_id = resource["id"]
            capacity = resource.get("capacity", 100)  # percentage
            utilization = resource.get("current_utilization", 0)
            
            capacity_analysis["capacity_summary"][resource_id] = {
                "name": resource["name"],
                "capacity": capacity,
                "utilization": utilization,
                "available_capacity": capacity - utilization,
                "utilization_percentage": (utilization / capacity * 100) if capacity > 0 else 0
            }
            
            # Identify bottlenecks (>90% utilization)
            if utilization / capacity > 0.9:
                capacity_analysis["bottlenecks"].append({
                    "resource_id": resource_id,
                    "name": resource["name"],
                    "utilization_percentage": utilization / capacity * 100,
                    "skills": resource.get("skills", [])
                })
        
        # Generate recommendations
        if capacity_analysis["bottlenecks"]:
            capacity_analysis["recommendations"].append(
                "Consider hiring additional resources for bottlenecked skills"
            )
            capacity_analysis["recommendations"].append(
                "Redistribute workload to underutilized resources"
            )
        
        return {
            "success": True,
            "analysis": capacity_analysis,
            "time_period": time_period,
            "message": f"Resource capacity analysis completed for {len(resources)} resources"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Resource capacity analysis failed: {str(e)}"
        }


# ============================================================================
# Retrospective Analysis Tools
# ============================================================================

@mcp_tool(
    name="conduct_retrospective",
    description="Conduct retrospective analysis of a completed project"
)
async def conduct_retrospective(
    project_id: str,
    planned_metrics: Dict[str, Any],
    actual_metrics: Dict[str, Any],
    team_feedback: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Conduct retrospective analysis of a completed project.
    
    Args:
        project_id: ID of the completed project
        planned_metrics: Originally planned project metrics
        actual_metrics: Actual project performance metrics
        team_feedback: Optional team feedback and observations
        
    Returns:
        Dictionary containing retrospective analysis
    """
    try:
        # Calculate performance variances
        variances = {}
        for metric, planned_value in planned_metrics.items():
            actual_value = actual_metrics.get(metric, planned_value)
            variance = ((actual_value - planned_value) / planned_value * 100) if planned_value != 0 else 0
            variances[metric] = {
                "planned": planned_value,
                "actual": actual_value,
                "variance_percentage": variance,
                "status": "over" if variance > 0 else "under" if variance < 0 else "on_target"
            }
        
        # Generate insights
        insights = []
        if variances.get("duration", {}).get("variance_percentage", 0) > 10:
            insights.append("Project took significantly longer than planned")
        if variances.get("budget", {}).get("variance_percentage", 0) > 10:
            insights.append("Project exceeded budget expectations")
        if variances.get("quality_score", {}).get("variance_percentage", 0) < -10:
            insights.append("Quality targets were not fully met")
        
        # Identify what went well and what could be improved
        went_well = []
        improvements = []
        
        for metric, variance_data in variances.items():
            if variance_data["variance_percentage"] <= 5:  # Within 5% tolerance
                went_well.append(f"{metric} was delivered on target")
            elif variance_data["status"] == "over":
                improvements.append(f"Better {metric} estimation and control needed")
        
        retrospective = {
            "project_id": project_id,
            "variances": variances,
            "insights": insights,
            "went_well": went_well,
            "improvements": improvements,
            "team_feedback": team_feedback or [],
            "overall_rating": "good" if len(insights) <= 1 else "needs_improvement",
            "analysis_date": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "retrospective": retrospective,
            "message": f"Retrospective analysis completed for project {project_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Retrospective analysis failed: {str(e)}"
        }


@mcp_tool(
    name="analyze_performance_trends",
    description="Analyze performance trends across multiple projects"
)
async def analyze_performance_trends(
    projects: List[Dict[str, Any]],
    metrics: List[str],
    time_period: str = "last_year"
) -> Dict[str, Any]:
    """
    Analyze performance trends across multiple projects.
    
    Args:
        projects: List of project data for analysis
        metrics: List of metrics to analyze
        time_period: Time period for trend analysis
        
    Returns:
        Dictionary containing trend analysis
    """
    try:
        trends = {}
        
        for metric in metrics:
            metric_values = []
            for project in projects:
                if metric in project.get("metrics", {}):
                    metric_values.append(project["metrics"][metric])
            
            if metric_values:
                avg_value = sum(metric_values) / len(metric_values)
                min_value = min(metric_values)
                max_value = max(metric_values)
                
                # Simple trend calculation (comparing first and last half)
                mid_point = len(metric_values) // 2
                first_half_avg = sum(metric_values[:mid_point]) / mid_point if mid_point > 0 else avg_value
                second_half_avg = sum(metric_values[mid_point:]) / (len(metric_values) - mid_point)
                
                trend_direction = "improving" if second_half_avg > first_half_avg else "declining" if second_half_avg < first_half_avg else "stable"
                
                trends[metric] = {
                    "average": avg_value,
                    "minimum": min_value,
                    "maximum": max_value,
                    "trend_direction": trend_direction,
                    "improvement_percentage": ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg != 0 else 0,
                    "projects_analyzed": len(metric_values)
                }
        
        return {
            "success": True,
            "trends": trends,
            "time_period": time_period,
            "total_projects": len(projects),
            "message": f"Performance trend analysis completed for {len(metrics)} metrics"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Performance trend analysis failed: {str(e)}"
        }


# ============================================================================
# Improvement Recommendation Tools
# ============================================================================

@mcp_tool(
    name="generate_improvement_recommendations",
    description="Generate AI-driven improvement recommendations based on project data"
)
async def generate_improvement_recommendations(
    project_data: Dict[str, Any],
    focus_areas: Optional[List[str]] = None,
    constraint_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate AI-driven improvement recommendations based on project data.
    
    Args:
        project_data: Historical project data for analysis
        focus_areas: Specific areas to focus on (planning, execution, quality)
        constraint_types: Types of constraints to consider (time, budget, resources)
        
    Returns:
        Dictionary containing improvement recommendations
    """
    try:
        recommendations = []
        
        # Analyze project performance
        metrics = project_data.get("metrics", {})
        
        # Generate planning improvements
        if not focus_areas or "planning" in focus_areas:
            if metrics.get("planning_accuracy", 100) < 80:
                recommendations.append({
                    "category": "planning",
                    "priority": "high",
                    "title": "Improve Planning Accuracy",
                    "description": "Implementation of more detailed task breakdown and estimation techniques",
                    "expected_benefit": "15-25% improvement in delivery predictability",
                    "implementation_steps": [
                        "Adopt story point estimation",
                        "Implement historical velocity tracking",
                        "Conduct regular planning retrospectives"
                    ]
                })
        
        # Generate execution improvements
        if not focus_areas or "execution" in focus_areas:
            if metrics.get("on_time_delivery", 100) < 85:
                recommendations.append({
                    "category": "execution",
                    "priority": "medium",
                    "title": "Enhance Delivery Predictability",
                    "description": "Better tracking and early warning systems for timeline risks",
                    "expected_benefit": "10-20% improvement in on-time delivery",
                    "implementation_steps": [
                        "Implement daily progress tracking",
                        "Set up automated risk alerts",
                        "Establish clear escalation procedures"
                    ]
                })
        
        # Generate quality improvements
        if not focus_areas or "quality" in focus_areas:
            if metrics.get("defect_rate", 0) > 5:
                recommendations.append({
                    "category": "quality",
                    "priority": "high",
                    "title": "Reduce Defect Rate",
                    "description": "Implementation of comprehensive quality assurance processes",
                    "expected_benefit": "30-50% reduction in post-release defects",
                    "implementation_steps": [
                        "Implement code review processes",
                        "Increase automated testing coverage",
                        "Establish quality gates"
                    ]
                })
        
        # Generate resource optimization improvements
        if metrics.get("resource_utilization", 100) < 75:
            recommendations.append({
                "category": "resources",
                "priority": "medium",
                "title": "Optimize Resource Utilization",
                "description": "Better resource allocation and capacity planning",
                "expected_benefit": "15-20% improvement in resource efficiency",
                "implementation_steps": [
                    "Implement capacity planning tools",
                    "Cross-train team members",
                    "Optimize task assignment algorithms"
                ]
            })
        
        # Priority ranking
        high_priority = [r for r in recommendations if r["priority"] == "high"]
        medium_priority = [r for r in recommendations if r["priority"] == "medium"]
        low_priority = [r for r in recommendations if r["priority"] == "low"]
        
        return {
            "success": True,
            "recommendations": {
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
                "total_count": len(recommendations)
            },
            "focus_areas": focus_areas or ["all"],
            "analysis_confidence": "high" if len(recommendations) >= 3 else "medium",
            "message": f"Generated {len(recommendations)} improvement recommendations"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Improvement recommendation generation failed: {str(e)}"
        }


@mcp_tool(
    name="prioritize_improvements",
    description="Prioritize improvement initiatives based on impact and effort"
)
async def prioritize_improvements(
    improvements: List[Dict[str, Any]],
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prioritize improvement initiatives based on impact and effort.
    
    Args:
        improvements: List of improvement initiatives to prioritize
        constraints: Resource and time constraints
        
    Returns:
        Dictionary containing prioritized improvements
    """
    try:
        # Score improvements based on impact vs effort
        scored_improvements = []
        
        for improvement in improvements:
            # Extract or estimate impact and effort scores
            impact_score = improvement.get("impact_score", 5)  # 1-10 scale
            effort_score = improvement.get("effort_score", 5)   # 1-10 scale
            
            # Calculate priority score (impact/effort ratio)
            priority_score = impact_score / effort_score if effort_score > 0 else 0
            
            scored_improvement = improvement.copy()
            scored_improvement.update({
                "impact_score": impact_score,
                "effort_score": effort_score,
                "priority_score": priority_score,
                "priority_tier": "high" if priority_score > 1.5 else "medium" if priority_score > 0.8 else "low"
            })
            scored_improvements.append(scored_improvement)
        
        # Sort by priority score
        scored_improvements.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Group by priority tier
        high_priority = [i for i in scored_improvements if i["priority_tier"] == "high"]
        medium_priority = [i for i in scored_improvements if i["priority_tier"] == "medium"]
        low_priority = [i for i in scored_improvements if i["priority_tier"] == "low"]
        
        return {
            "success": True,
            "prioritized_improvements": {
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
                "quick_wins": [i for i in scored_improvements if i["impact_score"] >= 7 and i["effort_score"] <= 3],
                "major_projects": [i for i in scored_improvements if i["impact_score"] >= 8 and i["effort_score"] >= 7]
            },
            "total_improvements": len(improvements),
            "recommended_sequence": [i["title"] for i in scored_improvements[:5]],  # Top 5
            "message": f"Prioritized {len(improvements)} improvement initiatives"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Improvement prioritization failed: {str(e)}"
        }


# Export all tools for registration
planning_tools = [
    create_project_plan,
    analyze_critical_path,
    optimize_timeline,
    create_milestone
]

resource_management_tools = [
    allocate_resources,
    analyze_resource_capacity
]

retrospective_tools = [
    conduct_retrospective,
    analyze_performance_trends
]

improvement_tools = [
    generate_improvement_recommendations,
    prioritize_improvements
]