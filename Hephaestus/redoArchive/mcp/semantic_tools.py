"""
Semantic Analysis Tools for Hephaestus UI DevTools - Phase 2

MCP tool endpoints for semantic analysis functionality.
"""

from typing import Dict, Any, List, Optional
from .semantic_analyzer import analyze_component, find_component_html_file, SEMANTIC_PATTERNS


async def ui_semantic_analysis(
    component: str,
    detailed: bool = True
) -> Dict[str, Any]:
    """
    Analyze semantic structure of a component (Phase 2)
    
    Args:
        component: Component name to analyze (e.g., 'rhetor')
        detailed: Include detailed findings and recommendations
        
    Returns:
        Semantic analysis report with coverage scores
    """
    # Run the analysis
    analysis_result = await analyze_component(component)
    
    # Format the response
    result = {
        "component": component,
        "phase": "2",
        "tool": "semantic_analysis"
    }
    
    if analysis_result["error"]:
        result["error"] = analysis_result["error"]
        return result
    
    # Add core results
    result["file_analyzed"] = analysis_result["file_path"]
    result["semantic_score"] = analysis_result["analysis"]["score"]
    result["grade"] = analysis_result["summary"]["grade"]
    result["elements_tagged"] = analysis_result["summary"]["tagged_elements"]
    
    if detailed:
        # Include detailed analysis
        result["coverage_breakdown"] = analysis_result["analysis"]["coverage_by_category"]
        result["found_tags"] = analysis_result["analysis"]["found_tags"]
        result["missing_required"] = analysis_result["analysis"]["missing_required"]
        result["recommendations"] = analysis_result["recommendations"][:5]  # Top 5 recommendations
    else:
        # Just summary
        result["summary"] = {
            "missing_required_count": analysis_result["summary"]["missing_required_count"],
            "recommendation_count": analysis_result["summary"]["recommendation_count"]
        }
    
    # Add quick fix suggestions
    if analysis_result["recommendations"]:
        high_priority = [r for r in analysis_result["recommendations"] if r["priority"] == "high"]
        if high_priority:
            result["quick_fixes"] = high_priority[:3]
    
    return result


async def ui_semantic_scan(
    components: Optional[List[str]] = None,
    min_score: float = 0.7
) -> Dict[str, Any]:
    """
    Scan multiple components and report semantic health
    
    Args:
        components: List of components to scan (None = scan all)
        min_score: Minimum score threshold for reporting issues
        
    Returns:
        Summary of semantic health across components
    """
    import os
    from pathlib import Path
    
    result = {
        "tool": "semantic_scan",
        "phase": "2",
        "components_scanned": [],
        "issues_found": [],
        "summary": {}
    }
    
    # If no components specified, scan all in the UI directory
    if components is None:
        base_path = Path("/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components")
        components = [d.name for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    # Scan each component
    total_score = 0
    below_threshold = []
    
    for component_name in components:
        try:
            analysis = await analyze_component(component_name)
            
            if not analysis["error"]:
                score = analysis["analysis"]["score"]
                total_score += score
                
                result["components_scanned"].append({
                    "name": component_name,
                    "score": score,
                    "grade": analysis["summary"]["grade"],
                    "tagged": analysis["summary"]["tagged_elements"]
                })
                
                if score < min_score:
                    below_threshold.append(component_name)
                    result["issues_found"].append({
                        "component": component_name,
                        "score": score,
                        "missing_required": len(analysis["analysis"]["missing_required"]),
                        "top_issue": analysis["analysis"]["missing_required"][0] if analysis["analysis"]["missing_required"] else None
                    })
            else:
                result["components_scanned"].append({
                    "name": component_name,
                    "error": analysis["error"]
                })
                
        except Exception as e:
            result["components_scanned"].append({
                "name": component_name,
                "error": str(e)
            })
    
    # Calculate summary
    successful_scans = [c for c in result["components_scanned"] if "score" in c]
    if successful_scans:
        avg_score = total_score / len(successful_scans)
        result["summary"] = {
            "average_score": round(avg_score, 3),
            "components_below_threshold": len(below_threshold),
            "threshold": min_score,
            "components_needing_attention": below_threshold
        }
    
    return result


async def ui_semantic_patterns() -> Dict[str, Any]:
    """
    Get information about semantic patterns and best practices
    
    Returns:
        Documentation of semantic patterns used by Tekton
    """
    result = {
        "tool": "semantic_patterns",
        "phase": "2",
        "patterns": {}
    }
    
    # Transform patterns into documentation format
    for category, pattern_info in SEMANTIC_PATTERNS.items():
        result["patterns"][category] = {
            "description": get_category_description(category),
            "weight": f"{pattern_info['weight']*100:.0f}%",
            "required_tags": pattern_info["required"],
            "recommended_tags": pattern_info["recommended"],
            "examples": get_category_examples(category)
        }
    
    result["scoring"] = {
        "formula": "weighted average of category scores",
        "required_weight": "70% of category score",
        "recommended_weight": "30% of category score",
        "grade_scale": {
            "A": "90-100%",
            "B": "80-89%",
            "C": "70-79%",
            "D": "60-69%",
            "F": "Below 60%"
        }
    }
    
    return result


def get_category_description(category: str) -> str:
    """Get description for a semantic category"""
    descriptions = {
        "navigation": "Elements involved in UI navigation and menu structures",
        "components": "Major UI components and their boundaries",
        "interactions": "Interactive elements like buttons and forms",
        "state": "Elements that indicate or manage state",
        "identity": "Unique identification of elements"
    }
    return descriptions.get(category, f"{category} elements")


def get_category_examples(category: str) -> List[str]:
    """Get example usage for a category"""
    examples = {
        "navigation": [
            '<nav data-tekton-nav="main">',
            '<li data-tekton-nav-item="rhetor" data-tekton-nav-state="active">'
        ],
        "components": [
            '<div data-tekton-component="rhetor" data-tekton-area="llm">',
            '<section data-tekton-zone="chat-interface">'
        ],
        "interactions": [
            '<button data-tekton-action="send-message">',
            '<input data-tekton-trigger="search">'
        ],
        "state": [
            '<div data-tekton-state="loading">',
            '<span data-tekton-status="connected">'
        ],
        "identity": [
            '<div data-tekton-id="rhetor-main-panel">',
            '<form data-tekton-name="chat-form" data-tekton-type="input">'
        ]
    }
    return examples.get(category, [])