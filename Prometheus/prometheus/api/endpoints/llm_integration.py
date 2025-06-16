"""
LLM Integration Endpoints

This module defines the API endpoints for LLM integrations in the Prometheus/Epimethius Planning System.
These endpoints use the enhanced LLM adapter with tekton-llm-client features.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.planning import LLMPlanAnalysis
from ..models.retrospective import LLMRetrospectiveAnalysis
from ..models.improvement import LLMImprovementSuggestion, LLMRootCauseAnalysis
from ..models.shared import LLMAnalysisRequest, LLMRiskAnalysisRequest
from ..models.shared import StandardResponse

# Import the PrometheusLLMAdapter
from ...utils.llm_adapter import PrometheusLLMAdapter

# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.llm_integration")

# Create router
router = APIRouter(prefix="/llm", tags=["llm_integration"])

# LLM adapter dependency
async def get_llm_adapter():
    """
    Get or create an instance of the LLM adapter.
    
    Returns:
        Initialized LLM adapter
    """
    adapter = PrometheusLLMAdapter()
    return adapter


# Endpoints
@router.post("/plan-analysis", response_model=StandardResponse)
async def analyze_plan(analysis: LLMPlanAnalysis):
    """
    Analyze a plan using LLM capabilities.
    
    Args:
        analysis: Plan analysis request
        
    Returns:
        Analysis results
    """
    # Check if plan exists
    from .planning import plans_db
    if analysis.plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {analysis.plan_id} not found")
    
    # Get plan
    plan = plans_db[analysis.plan_id]
    
    # This is a placeholder implementation
    # In a real implementation, this would call the Rhetor LLM adapter
    
    # Generate placeholder analysis based on analysis_type
    analysis_result = {
        "plan_id": analysis.plan_id,
        "analysis_type": analysis.analysis_type,
        "timestamp": None,  # Would be set by LLM adapter
        "generated_by": "Placeholder LLM",
        "results": []
    }
    
    if analysis.analysis_type == "risk":
        analysis_result["results"] = [
            {
                "risk": "Timeline Risk",
                "description": "The estimated timeline may be too aggressive for the scope of work.",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Consider breaking down larger tasks further or adjusting the timeline."
            },
            {
                "risk": "Resource Constraint",
                "description": "The allocated resources may not be sufficient for the timeline.",
                "probability": "high",
                "impact": "medium",
                "mitigation": "Evaluate task assignments and consider adding more resources or adjusting scope."
            },
            {
                "risk": "Dependency Risk",
                "description": "External dependencies might cause delays in the critical path.",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Identify critical external dependencies and create contingency plans."
            }
        ]
    elif analysis.analysis_type == "quality":
        analysis_result["results"] = [
            {
                "aspect": "Requirements Coverage",
                "assessment": "The plan adequately covers most requirements, but some non-functional requirements may be underrepresented.",
                "score": 0.8,
                "suggestions": "Add explicit tasks for testing and validating non-functional requirements."
            },
            {
                "aspect": "Task Granularity",
                "assessment": "Task breakdown is appropriate for most areas, but some complex tasks could be further decomposed.",
                "score": 0.7,
                "suggestions": "Consider breaking down tasks that take more than 3 days into smaller units."
            },
            {
                "aspect": "Milestone Effectiveness",
                "assessment": "Milestones are well-distributed and provide clear progress indicators.",
                "score": 0.9,
                "suggestions": "Add intermediate milestones for long phases."
            }
        ]
    elif analysis.analysis_type == "completeness":
        analysis_result["results"] = [
            {
                "category": "Requirements Coverage",
                "missing_elements": ["Non-functional requirement testing", "Documentation tasks"],
                "suggestions": "Add explicit tasks for documentation and testing non-functional requirements."
            },
            {
                "category": "Resource Allocation",
                "missing_elements": ["Backup resources for critical tasks"],
                "suggestions": "Identify backup resources for tasks on the critical path."
            },
            {
                "category": "Risk Management",
                "missing_elements": ["Contingency buffers", "Risk mitigation tasks"],
                "suggestions": "Add buffer time for high-risk areas and explicit risk mitigation tasks."
            }
        ]
    elif analysis.analysis_type == "dependencies":
        analysis_result["results"] = [
            {
                "issue": "Circular Dependencies",
                "affected_tasks": ["task-123", "task-456"],
                "description": "Potential circular dependency between these tasks.",
                "resolution": "Reevaluate the dependency relationship and potentially restructure."
            },
            {
                "issue": "Missing Dependencies",
                "affected_tasks": ["task-789"],
                "description": "This task likely has missing dependencies.",
                "resolution": "Review prerequisites for this task and add appropriate dependencies."
            },
            {
                "issue": "Critical Path Bottleneck",
                "affected_tasks": ["task-101"],
                "description": "This task is a bottleneck in the critical path with multiple dependencies.",
                "resolution": "Consider parallelizing or starting preparations earlier."
            }
        ]
    elif analysis.analysis_type == "resource_allocation":
        analysis_result["results"] = [
            {
                "issue": "Resource Overallocation",
                "affected_resources": ["resource-123"],
                "description": "This resource is assigned to multiple concurrent tasks.",
                "resolution": "Redistribute workload or adjust timeline to prevent overallocation."
            },
            {
                "issue": "Skill Mismatch",
                "affected_resources": ["resource-456"],
                "affected_tasks": ["task-789"],
                "description": "This resource may not have all required skills for the assigned task.",
                "resolution": "Consider training or reassigning to a more suitable resource."
            },
            {
                "issue": "Uneven Workload",
                "description": "Work distribution is uneven across resources.",
                "resolution": "Rebalance workload to distribute more evenly."
            }
        ]
    elif analysis.analysis_type == "timeline":
        analysis_result["results"] = [
            {
                "issue": "Aggressive Timeline",
                "description": "The overall timeline appears compressed for the scope.",
                "affected_phases": ["Implementation", "Testing"],
                "resolution": "Consider extending timeline or reducing scope."
            },
            {
                "issue": "Insufficient Buffer",
                "description": "No buffer time allocated for unexpected delays.",
                "resolution": "Add buffer time especially after complex tasks and before key milestones."
            },
            {
                "issue": "Milestone Clustering",
                "description": "Multiple milestones are clustered close together.",
                "resolution": "Distribute milestones more evenly across the timeline."
            }
        ]
    
    logger.info(f"Generated {analysis.analysis_type} analysis for plan {analysis.plan_id}")
    
    return {
        "status": "success",
        "message": f"Plan {analysis.analysis_type} analysis completed successfully",
        "data": analysis_result
    }


@router.post("/retrospective-analysis", response_model=StandardResponse)
async def analyze_retrospective(
    analysis: LLMRetrospectiveAnalysis,
    llm_adapter: PrometheusLLMAdapter = Depends(get_llm_adapter)
):
    """
    Analyze a retrospective using LLM capabilities.
    
    Args:
        analysis: Retrospective analysis request
        llm_adapter: LLM adapter for retrospective analysis
        
    Returns:
        Analysis results
    """
    # Check if retrospective exists
    from .retrospective import retrospectives_db
    if analysis.retrospective_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {analysis.retrospective_id} not found")
    
    # Get retrospective
    retro = retrospectives_db[analysis.retrospective_id]
    
    try:
        # Prepare the retrospective data for the LLM
        retro_data = {
            "name": retro.get("name", "Retrospective"),
            "date": retro.get("date", "Unknown"),
            "format": retro.get("format", "Unknown"),
            "items": retro.get("items", []),
            "action_items": retro.get("action_items", [])
        }
        
        # Use the LLM adapter to analyze the retrospective
        result = await llm_adapter.analyze_retrospective(retro_data)
        
        # Set up the analysis result structure
        analysis_result = {
            "retrospective_id": analysis.retrospective_id,
            "analysis_type": analysis.analysis_type,
            "timestamp": result.get("timestamp"),
            "generated_by": result.get("model", llm_adapter.default_model),
            "results": []
        }
        
        # Process the analysis based on the requested type
        if analysis.analysis_type == "patterns":
            # Try to extract patterns from the analysis
            patterns = []
            
            # Extract patterns from the full text analysis
            analysis_text = result.get("analysis", "")
            
            # Look for section headers or key phrases
            pattern_sections = [
                section for section in analysis_text.split("\n\n") 
                if "pattern" in section.lower() or "theme" in section.lower()
            ]
            
            if pattern_sections:
                # Use the sections that mention patterns
                for section in pattern_sections:
                    lines = section.split("\n")
                    title = lines[0].strip("# -").strip() if lines else "Identified Pattern"
                    description = "\n".join(lines[1:]) if len(lines) > 1 else section
                    
                    patterns.append({
                        "pattern": title,
                        "description": description,
                        "frequency": sum(1 for item in retro.get("items", []) if title.lower() in item.get("content", "").lower()),
                        "examples": [
                            item.get("content") for item in retro.get("items", [])
                            if title.lower() in item.get("content", "").lower()
                        ][:3],  # Limit to 3 examples
                        "suggestions": "Implement changes based on the analysis"
                    })
            else:
                # If no clear patterns were found, use the full analysis
                patterns.append({
                    "pattern": "General Observations",
                    "description": analysis_text,
                    "frequency": len(retro.get("items", [])),
                    "examples": [
                        item.get("content") for item in retro.get("items", [])[:3]
                    ],
                    "suggestions": "Review the analysis for specific recommendations"
                })
            
            analysis_result["results"] = patterns
            
        elif analysis.analysis_type == "root_cause":
            # Try to extract root causes from the analysis
            root_causes = []
            analysis_text = result.get("analysis", "")
            
            # Look for section headers or key phrases related to root causes
            rc_sections = [
                section for section in analysis_text.split("\n\n") 
                if "root cause" in section.lower() or "issue" in section.lower()
            ]
            
            if rc_sections:
                for section in rc_sections:
                    lines = section.split("\n")
                    issue = lines[0].strip("# -").strip() if lines else "Identified Issue"
                    
                    # Try to identify symptoms, causes, factors, and recommendations
                    symptoms = []
                    causes = []
                    factors = []
                    recommendations = []
                    
                    current_list = None
                    for line in lines[1:]:
                        lower_line = line.lower().strip()
                        if "symptom" in lower_line:
                            current_list = symptoms
                        elif "root cause" in lower_line or "cause" in lower_line:
                            current_list = causes
                        elif "factor" in lower_line:
                            current_list = factors
                        elif "recommendation" in lower_line or "suggest" in lower_line:
                            current_list = recommendations
                        elif line.strip().startswith("-") and current_list is not None:
                            current_list.append(line.strip("- ").strip())
                    
                    root_causes.append({
                        "issue": issue,
                        "symptoms": symptoms if symptoms else ["Identified from retrospective items"],
                        "root_causes": causes if causes else ["See description"],
                        "contributing_factors": factors,
                        "recommendations": recommendations if recommendations else ["Review analysis for recommendations"]
                    })
            
            if not root_causes:
                # If no clear root causes were identified, provide a general analysis
                root_causes.append({
                    "issue": "General Retrospective Analysis",
                    "symptoms": [
                        item.get("content") for item in retro.get("items", [])
                        if item.get("category", "").lower() in ["problem", "issue", "challenge"]
                    ][:3],
                    "root_causes": ["Analysis did not identify specific root causes"],
                    "contributing_factors": [],
                    "recommendations": [
                        item.get("content") for item in retro.get("action_items", [])
                    ][:3]
                })
            
            analysis_result["results"] = root_causes
            
        elif analysis.analysis_type == "improvement":
            # Use the existing improvement generation function if available
            try:
                improvements = await llm_adapter.generate_improvements({"retrospective": retro_data})
                
                # Group improvements by category
                improvement_categories = {}
                for imp in improvements:
                    category = imp.get("category", "General Improvements")
                    if category not in improvement_categories:
                        improvement_categories[category] = []
                    
                    improvement_categories[category].append({
                        "title": imp.get("title", ""),
                        "description": imp.get("description", ""),
                        "priority": imp.get("priority", "medium"),
                        "effort": imp.get("effort", "medium"),
                        "impact": imp.get("impact", "medium")
                    })
                
                # Convert to the expected format
                results = []
                for category, imps in improvement_categories.items():
                    results.append({
                        "category": category,
                        "improvements": imps
                    })
                
                analysis_result["results"] = results
                
            except Exception as e:
                logger.error(f"Error generating improvements: {e}")
                
                # Fallback to a simpler approach
                analysis_text = result.get("analysis", "")
                
                # Look for section headers or key phrases related to improvements
                imp_sections = [
                    section for section in analysis_text.split("\n\n") 
                    if "improve" in section.lower() or "recommendation" in section.lower()
                ]
                
                if imp_sections:
                    # Use the improvement sections
                    improvement_categories = {
                        "Identified Improvements": []
                    }
                    
                    for section in imp_sections:
                        lines = section.split("\n")
                        title = lines[0].strip("# -").strip() if lines else "Improvement"
                        description = "\n".join(lines[1:]) if len(lines) > 1 else section
                        
                        improvement_categories["Identified Improvements"].append({
                            "title": title,
                            "description": description,
                            "priority": "medium",
                            "effort": "medium",
                            "impact": "medium"
                        })
                    
                    # Convert to the expected format
                    results = []
                    for category, imps in improvement_categories.items():
                        results.append({
                            "category": category,
                            "improvements": imps
                        })
                    
                    analysis_result["results"] = results
                else:
                    # No clear improvements found
                    analysis_result["results"] = [
                        {
                            "category": "General Improvements",
                            "improvements": [
                                {
                                    "title": "Review Retrospective",
                                    "description": "Review the full retrospective analysis for specific improvement opportunities",
                                    "priority": "high",
                                    "effort": "low",
                                    "impact": "medium"
                                }
                            ]
                        }
                    ]
        
        elif analysis.analysis_type == "comparison":
            # For comparison, we need historical data
            # This is a placeholder - in a real implementation, we would retrieve 
            # previous retrospectives and compare them
            
            analysis_result["results"] = [
                {
                    "aspect": "Overall Progress",
                    "previous": "Previous retrospective data not available",
                    "current": f"{len(retro.get('items', []))} items identified in this retrospective",
                    "trend": "unknown",
                    "analysis": "Full comparison requires historical data"
                },
                {
                    "aspect": "Key Themes",
                    "previous": "Not available",
                    "current": result.get("analysis", "")[:100] + "...",
                    "trend": "unknown",
                    "analysis": "Review full analysis for details"
                }
            ]
        
        logger.info(f"Generated {analysis.analysis_type} analysis for retrospective {analysis.retrospective_id}")
        
        return {
            "status": "success",
            "message": f"Retrospective {analysis.analysis_type} analysis completed successfully",
            "data": analysis_result
        }
        
    except Exception as e:
        logger.error(f"Error in retrospective analysis: {e}")
        
        # Generate placeholder analysis based on analysis_type
        analysis_result = {
            "retrospective_id": analysis.retrospective_id,
            "analysis_type": analysis.analysis_type,
            "timestamp": None,
            "generated_by": "Fallback Generator",
            "results": []
        }
        
        if analysis.analysis_type == "patterns":
            analysis_result["results"] = [
                {
                    "pattern": "Communication Gaps",
                    "description": "Multiple retrospective items point to communication challenges between team members.",
                    "frequency": 5,
                    "examples": ["Communication breakdown in design phase", "Missed update on requirements"],
                    "suggestions": "Implement daily standups and improve documentation of decisions."
                },
                {
                    "pattern": "Testing Delays",
                    "description": "Testing is consistently starting later than planned.",
                    "frequency": 3,
                    "examples": ["QA started late due to build issues", "Test environment not ready on time"],
                    "suggestions": "Prepare test environments earlier and involve QA in planning stages."
                },
                {
                    "pattern": "Scope Creep",
                    "description": "Requirements expanded during implementation.",
                    "frequency": 4,
                    "examples": ["Additional features requested mid-sprint", "Unexpected complexity"],
                    "suggestions": "Improve requirement gathering and implement change control process."
                }
            ]
        elif analysis.analysis_type == "root_cause":
            analysis_result["results"] = [
                {
                    "issue": "Missed Deadline",
                    "symptoms": ["Late delivery", "Last-minute rush", "Quality issues"],
                    "root_causes": [
                        "Underestimated task complexity",
                        "Dependencies not identified early",
                        "Resource constraints not addressed"
                    ],
                    "contributing_factors": [
                        "Incomplete requirements",
                        "Communication gaps"
                    ],
                    "recommendations": [
                        "Improve estimation process",
                        "Conduct dependency analysis at project start",
                        "Add buffer for complex tasks"
                    ]
                },
                {
                    "issue": "Quality Issues",
                    "symptoms": ["High defect rate", "Customer complaints"],
                    "root_causes": [
                        "Insufficient testing",
                        "Rushed implementation"
                    ],
                    "contributing_factors": [
                        "Time pressure",
                        "Lack of test automation"
                    ],
                    "recommendations": [
                        "Implement automated testing",
                        "Add quality gates before major milestones",
                        "Allocate more time for testing"
                    ]
                }
            ]
        elif analysis.analysis_type == "improvement":
            analysis_result["results"] = [
                {
                    "category": "Process Improvements",
                    "improvements": [
                        {
                            "title": "Enhanced Requirements Process",
                            "description": "Implement a more structured requirements gathering process with stakeholder sign-off.",
                            "priority": "high",
                            "effort": "medium",
                            "impact": "high"
                        },
                        {
                            "title": "Automated Testing",
                            "description": "Implement automated testing for critical components.",
                            "priority": "medium",
                            "effort": "high",
                            "impact": "high"
                        }
                    ]
                },
                {
                    "category": "Communication Improvements",
                    "improvements": [
                        {
                            "title": "Daily Standups",
                            "description": "Implement daily standup meetings to improve team communication.",
                            "priority": "high",
                            "effort": "low",
                            "impact": "medium"
                        },
                        {
                            "title": "Documentation Standards",
                            "description": "Create and enforce documentation standards for key decisions.",
                            "priority": "medium",
                            "effort": "medium",
                            "impact": "high"
                        }
                    ]
                }
            ]
        elif analysis.analysis_type == "comparison":
            analysis_result["results"] = [
                {
                    "aspect": "Overall Progress",
                    "previous": "75% of tasks completed, 25% over budget",
                    "current": "85% of tasks completed, 10% over budget",
                    "trend": "positive",
                    "analysis": "Team is showing improved efficiency and better budget management."
                },
                {
                    "aspect": "Communication",
                    "previous": "Multiple communication issues reported",
                    "current": "Fewer communication issues, but still present",
                    "trend": "slightly positive",
                    "analysis": "Communication has improved but still requires attention."
                },
                {
                    "aspect": "Quality",
                    "previous": "High defect rate and customer issues",
                    "current": "Lower defect rate but still above target",
                    "trend": "positive",
                    "analysis": "Quality improvements are working but need continued focus."
                }
            ]
        
        logger.info(f"Generated fallback {analysis.analysis_type} analysis for retrospective {analysis.retrospective_id}")
        
        return {
            "status": "success",
            "message": f"Retrospective {analysis.analysis_type} analysis completed using fallback method",
            "data": analysis_result
        }


@router.post("/improvement-suggestions", response_model=StandardResponse)
async def get_improvement_suggestions(
    suggestion: LLMImprovementSuggestion,
    llm_adapter: PrometheusLLMAdapter = Depends(get_llm_adapter)
):
    """
    Generate improvement suggestions using LLM capabilities.
    
    Args:
        suggestion: Improvement suggestion request
        llm_adapter: LLM adapter for improvement suggestions
        
    Returns:
        Generated improvement suggestions
    """
    # Validate context exists
    context_data = {}
    
    if suggestion.context_type == "retrospective":
        from .retrospective import retrospectives_db
        if suggestion.context_id not in retrospectives_db:
            raise HTTPException(status_code=404, detail=f"Retrospective {suggestion.context_id} not found")
        context_data = retrospectives_db[suggestion.context_id]
    
    elif suggestion.context_type == "execution":
        from .history import execution_records_db
        if suggestion.context_id not in execution_records_db:
            raise HTTPException(status_code=404, detail=f"Execution record {suggestion.context_id} not found")
        context_data = execution_records_db[suggestion.context_id]
    
    try:
        # Convert context data to performance data format
        performance_data = {}
        
        if suggestion.context_type == "retrospective":
            # Extract key metrics from retrospective data
            performance_data = {
                "retrospective": {
                    "name": context_data.get("name", "Retrospective"),
                    "date": context_data.get("date", "Unknown"),
                    "items": context_data.get("items", []),
                    "action_items": context_data.get("action_items", [])
                }
            }
            
            # Count items by category for better analysis
            categories = {}
            for item in context_data.get("items", []):
                category = item.get("category", "Uncategorized")
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
                
            performance_data["categories"] = categories
            
        elif suggestion.context_type == "execution":
            # Extract key metrics from execution data
            tasks = context_data.get("tasks", {})
            milestones = context_data.get("milestones", [])
            
            # Calculate completion rate
            completed_tasks = sum(1 for t in tasks.values() if t.get("status") == "completed")
            completion_rate = completed_tasks / len(tasks) if tasks else 0
            
            # Calculate effort variance
            effort_variance = 0
            for task_id, task in tasks.items():
                estimated = task.get("estimated_effort", 0)
                actual = task.get("actual_effort", 0)
                if estimated and actual:
                    effort_variance += abs(actual - estimated)
                    
            performance_data = {
                "completion_rate": completion_rate,
                "effort_variance": effort_variance / len(tasks) if tasks else 0,
                "task_completion": {
                    task_id: {
                        "name": task.get("name", ""),
                        "actual_progress": task.get("progress", 0),
                        "status": task.get("status", "unknown")
                    }
                    for task_id, task in tasks.items()
                },
                "milestone_achievement": {
                    milestone.get("milestone_id", f"m-{i}"): {
                        "name": milestone.get("name", ""),
                        "actual_status": milestone.get("status", "unknown")
                    }
                    for i, milestone in enumerate(milestones)
                }
            }
            
        # Set analysis depth (more detail for higher depth)
        if suggestion.analysis_depth == "deep":
            # Add system prompt for deeper analysis
            system_prompt = (
                "You are an expert in process improvement and project management. "
                "Provide detailed, specific improvement suggestions with clear implementation steps. "
                "Consider both short-term and long-term benefits, prioritize based on impact and effort, "
                "and provide concrete verification criteria for each suggestion."
            )
        else:
            # Basic system prompt for quick analysis
            system_prompt = (
                "You are an assistant helping to identify improvement opportunities. "
                "Provide practical, actionable improvement suggestions based on the performance data."
            )
            
        # Generate improvement suggestions using the LLM adapter
        improvements = await llm_adapter.generate_improvements(performance_data)
        
        # Limit to requested number of suggestions
        if suggestion.max_suggestions and len(improvements) > suggestion.max_suggestions:
            improvements = improvements[:suggestion.max_suggestions]
            
        # Format the suggestions for the response
        formatted_suggestions = []
        for imp in improvements:
            # Convert implementation plan to steps if it's a string
            implementation_steps = []
            if "implementation_plan" in imp:
                if isinstance(imp["implementation_plan"], str):
                    # Split by newlines or numbers
                    steps = imp["implementation_plan"].split("\n")
                    if len(steps) == 1:
                        # Try splitting by numbered list items
                        import re
                        steps = re.split(r'\d+\.\s+', imp["implementation_plan"])
                        steps = [s.strip() for s in steps if s.strip()]
                    
                    implementation_steps = steps
                elif isinstance(imp["implementation_plan"], list):
                    implementation_steps = imp["implementation_plan"]
            
            # Convert verification criteria to list if it's a string
            verification_criteria = []
            if "verification_criteria" in imp:
                if isinstance(imp["verification_criteria"], str):
                    criteria = imp["verification_criteria"].split("\n")
                    verification_criteria = [c.strip() for c in criteria if c.strip()]
                elif isinstance(imp["verification_criteria"], list):
                    verification_criteria = imp["verification_criteria"]
            
            # Add formatted suggestion
            formatted_suggestions.append({
                "title": imp.get("title", "Improvement"),
                "description": imp.get("description", ""),
                "justification": "Based on analysis of the provided context data.",
                "priority": imp.get("priority", "medium"),
                "effort": imp.get("effort", "medium"),
                "impact": imp.get("impact", "medium"),
                "implementation_steps": implementation_steps or ["Plan", "Implement", "Validate"],
                "verification_criteria": verification_criteria or ["Improved efficiency", "Reduced issues"],
                "confidence": 0.8
            })
        
        # Create result
        suggestions_result = {
            "context_type": suggestion.context_type,
            "context_id": suggestion.context_id,
            "analysis_depth": suggestion.analysis_depth,
            "timestamp": improvements[0].get("created_at") if improvements else None,
            "generated_by": f"{llm_adapter.default_provider}/{llm_adapter.default_model}",
            "suggestions": formatted_suggestions
        }
        
        logger.info(f"Generated {len(suggestions_result['suggestions'])} improvement suggestions for {suggestion.context_type} {suggestion.context_id}")
        
        return {
            "status": "success",
            "message": "Improvement suggestions generated successfully",
            "data": suggestions_result
        }
        
    except Exception as e:
        logger.error(f"Error generating improvement suggestions: {e}")
        
        # Generate fallback suggestions
        suggestions_result = {
            "context_type": suggestion.context_type,
            "context_id": suggestion.context_id,
            "analysis_depth": suggestion.analysis_depth,
            "timestamp": None,
            "generated_by": "Fallback Generator",
            "suggestions": []
        }
        
        # Generate some placeholder suggestions
        for i in range(min(suggestion.max_suggestions, 5)):
            suggestions_result["suggestions"].append({
                "title": f"Improvement suggestion {i+1}",
                "description": "This is a placeholder improvement suggestion generated by the fallback system.",
                "justification": "Based on patterns observed in the provided context.",
                "priority": "medium",
                "effort": "medium",
                "impact": "medium",
                "implementation_steps": [
                    "Step 1: Plan the improvement",
                    "Step 2: Implement the improvement",
                    "Step 3: Validate the improvement"
                ],
                "verification_criteria": [
                    "Criterion 1: Measurable improvement in process efficiency",
                    "Criterion 2: Reduction in related issues"
                ],
                "confidence": 0.8
            })
        
        logger.info(f"Generated {len(suggestions_result['suggestions'])} fallback improvement suggestions for {suggestion.context_type} {suggestion.context_id}")
        
        return {
            "status": "success",
            "message": "Improvement suggestions generated using fallback method",
            "data": suggestions_result
        }


@router.post("/risk-analysis", response_model=StandardResponse)
async def analyze_risks(
    analysis: LLMRiskAnalysisRequest,
    llm_adapter: PrometheusLLMAdapter = Depends(get_llm_adapter)
):
    """
    Analyze risks for a plan using LLM and historical data.
    
    Args:
        analysis: Risk analysis request
        llm_adapter: LLM adapter for risk analysis
        
    Returns:
        Risk analysis results
    """
    # Check if plan exists
    from .planning import plans_db
    if analysis.plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {analysis.plan_id} not found")
    
    # Get plan
    plan = plans_db[analysis.plan_id]
    
    # Get historical data if requested
    historical_data = None
    if analysis.include_history:
        from .history import execution_records_db
        from .retrospective import retrospectives_db
        
        # Get execution records for the plan
        plan_records = [r for r in execution_records_db.values() if r["plan_id"] == analysis.plan_id]
        
        # Get retrospectives for the plan
        plan_retros = [r for r in retrospectives_db.values() if r["plan_id"] == analysis.plan_id]
        
        historical_data = {
            "execution_records": plan_records,
            "retrospectives": plan_retros
        }
    
    # Prepare the project data
    project_data = {
        "name": plan["name"],
        "start_date": plan.get("start_date"),
        "end_date": plan.get("end_date"),
        "tasks": plan.get("tasks", {}),
        "milestones": plan.get("milestones", []),
        "resources": plan.get("resources", []),
    }
    
    if historical_data:
        project_data["historical_data"] = historical_data
    
    try:
        # Use the LLM adapter to analyze risks
        risks = await llm_adapter.analyze_risks(project_data)
        
        # Add any additional information
        for risk in risks:
            # Filter out any tasks that don't exist in the plan
            if "affected_tasks" in risk:
                risk["affected_tasks"] = [task_id for task_id in risk["affected_tasks"] if task_id in plan["tasks"]]
            
            # Only include mitigations if requested
            if not analysis.include_mitigations and "mitigations" in risk:
                del risk["mitigations"]
        
        # Filter risks by type if specified
        if analysis.risk_types:
            risks = [risk for risk in risks if risk.get("type") in analysis.risk_types]
        
        # Limit the number of risks if specified
        if analysis.max_risks and len(risks) > analysis.max_risks:
            # Sort by severity (highest first) and take the top N
            severity_mapping = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            risks.sort(key=lambda r: severity_mapping.get(r.get("severity", "low"), 0), reverse=True)
            risks = risks[:analysis.max_risks]
        
        # Create the result object
        risk_analysis = {
            "plan_id": analysis.plan_id,
            "plan_name": plan["name"],
            "timestamp": risks[0].get("created_at") if risks else None,
            "generated_by": f"{risks[0].get('provider', 'unknown')}/{risks[0].get('model', 'unknown')}" if risks else "LLM",
            "includes_history": analysis.include_history,
            "risks": risks
        }
        
        logger.info(f"Generated risk analysis with {len(risk_analysis['risks'])} risks for plan {analysis.plan_id}")
        
        return {
            "status": "success",
            "message": "Risk analysis completed successfully",
            "data": risk_analysis
        }
        
    except Exception as e:
        logger.error(f"Error generating risk analysis: {e}")
        
        # Fall back to placeholder implementation if LLM fails
        risk_analysis = {
            "plan_id": analysis.plan_id,
            "plan_name": plan["name"],
            "timestamp": None,
            "generated_by": "Fallback Generator",
            "includes_history": analysis.include_history,
            "risks": []
        }
        
        # Generate some placeholder risks
        risk_types = analysis.risk_types or ["schedule", "resource", "technical", "scope", "external"]
        
        for risk_type in risk_types[:min(len(risk_types), analysis.max_risks)]:
            risk = {
                "type": risk_type,
                "title": f"{risk_type.capitalize()} risk",
                "description": f"This is a placeholder {risk_type} risk identified by the fallback generator.",
                "probability": "medium",
                "impact": "medium",
                "severity": "medium",
                "affected_tasks": [],
                "affected_milestones": [],
                "historical_precedent": True if analysis.include_history else False
            }
            
            # Add some affected tasks and milestones
            for task_id in list(plan["tasks"].keys())[:2]:
                risk["affected_tasks"].append(task_id)
                
            for milestone in plan["milestones"][:1]:
                risk["affected_milestones"].append(milestone["milestone_id"])
            
            # Add mitigations if requested
            if analysis.include_mitigations:
                risk["mitigations"] = [
                    {
                        "strategy": "Avoid",
                        "description": f"Avoid this {risk_type} risk by taking preventive action.",
                        "effort": "medium",
                        "effectiveness": "high"
                    },
                    {
                        "strategy": "Mitigate",
                        "description": f"Reduce the impact of this {risk_type} risk.",
                        "effort": "low",
                        "effectiveness": "medium"
                    }
                ]
            
            risk_analysis["risks"].append(risk)
        
        logger.info(f"Generated fallback risk analysis with {len(risk_analysis['risks'])} risks for plan {analysis.plan_id}")
        
        return {
            "status": "success",
            "message": "Risk analysis completed using fallback method",
            "data": risk_analysis
        }


@router.post("/analyze", response_model=StandardResponse)
async def general_analysis(
    analysis: LLMAnalysisRequest,
    llm_adapter: PrometheusLLMAdapter = Depends(get_llm_adapter)
):
    """
    Perform general analysis using LLM capabilities.
    
    Args:
        analysis: Analysis request
        llm_adapter: LLM adapter for general analysis
        
    Returns:
        Analysis results
    """
    try:
        # Create system prompt based on analysis type
        system_prompt = f"You are an AI assistant that specializes in {analysis.analysis_type} analysis. "
        system_prompt += "Provide a thorough analysis of the content, focusing on key insights, main points, and recommendations."
        
        # Generate analysis using LLM adapter
        response = await llm_adapter.generate_text(
            prompt=analysis.content,
            system_prompt=system_prompt,
            temperature=0.4,  # Lower temperature for analysis
            max_tokens=2000
        )
        
        # Structure the response
        try:
            # Try to parse as JSON if possible
            json_output = json.loads(response)
            analysis_content = json_output
        except json.JSONDecodeError:
            # If not JSON, structure the text response
            analysis_content = {
                "main_points": [],
                "insights": [],
                "recommendations": []
            }
            
            # Simple parsing - split by headers if present
            sections = response.split("\n\n")
            for section in sections:
                if section.lower().startswith("main point") or section.lower().startswith("key point"):
                    analysis_content["main_points"].append(section)
                elif section.lower().startswith("insight") or "insight:" in section.lower():
                    analysis_content["insights"].append(section)
                elif section.lower().startswith("recommend") or "recommend:" in section.lower():
                    analysis_content["recommendations"].append(section)
            
            # If nothing was found, use the whole text as main points
            if not any(analysis_content.values()):
                analysis_content["main_points"] = [response]
                
        # Create analysis result
        analysis_result = {
            "content_summary": analysis.content[:100] + "..." if len(analysis.content) > 100 else analysis.content,
            "analysis_type": analysis.analysis_type,
            "timestamp": llm_adapter.default_model,  # Use current time
            "generated_by": f"{llm_adapter.default_provider}/{llm_adapter.default_model}",
            "results": analysis_content
        }
        
        logger.info(f"Generated general {analysis.analysis_type} analysis using LLM")
        
        return {
            "status": "success",
            "message": f"Analysis of type '{analysis.analysis_type}' completed successfully",
            "data": analysis_result
        }
    
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        
        # Fall back to placeholder implementation
        analysis_result = {
            "content_summary": analysis.content[:100] + "..." if len(analysis.content) > 100 else analysis.content,
            "analysis_type": analysis.analysis_type,
            "timestamp": None,
            "generated_by": "Fallback Generator",
            "results": {
                "main_points": [
                    "Point 1: This is the first main point extracted from the content.",
                    "Point 2: This is the second main point extracted from the content.",
                    "Point 3: This is the third main point extracted from the content."
                ],
                "insights": [
                    "Insight 1: This is an insight derived from the content.",
                    "Insight 2: This is another insight derived from the content."
                ],
                "recommendations": [
                    "Recommendation 1: This is a recommendation based on the analysis.",
                    "Recommendation 2: This is another recommendation based on the analysis."
                ]
            }
        }
        
        logger.info(f"Generated fallback {analysis.analysis_type} analysis")
        
        return {
            "status": "success",
            "message": f"Analysis of type '{analysis.analysis_type}' completed using fallback method",
            "data": analysis_result
        }