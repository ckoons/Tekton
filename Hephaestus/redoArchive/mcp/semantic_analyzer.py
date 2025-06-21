"""
Semantic Analyzer Module for Hephaestus UI DevTools - Phase 2

This module analyzes HTML files directly from disk to identify semantic gaps,
score semantic completeness, and provide recommendations for improvement.

NO BROWSER REQUIRED - Pure file-based analysis!
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup

# Semantic patterns we're looking for
SEMANTIC_PATTERNS = {
    "navigation": {
        "required": ["data-tekton-nav", "data-tekton-nav-item"],
        "recommended": ["data-tekton-nav-state", "data-tekton-nav-group"],
        "weight": 0.2
    },
    "components": {
        "required": ["data-tekton-component", "data-component"],
        "recommended": ["data-tekton-area", "data-tekton-zone"],
        "weight": 0.3
    },
    "interactions": {
        "required": ["data-tekton-action"],
        "recommended": ["data-tekton-trigger", "data-tekton-target"],
        "weight": 0.2
    },
    "state": {
        "required": ["data-tekton-state"],
        "recommended": ["data-tekton-status", "data-tekton-loading"],
        "weight": 0.15
    },
    "identity": {
        "required": ["data-tekton-id"],
        "recommended": ["data-tekton-name", "data-tekton-type"],
        "weight": 0.15
    }
}


def find_component_html_file(component_name: str, base_path: Optional[str] = None) -> Optional[Path]:
    """
    Find the HTML file for a given component
    
    Args:
        component_name: Name of the component (e.g., 'rhetor')
        base_path: Base path to search from (defaults to UI components directory)
        
    Returns:
        Path to the HTML file if found, None otherwise
    """
    if base_path is None:
        base_path = "/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components"
    
    # Common patterns for component HTML files
    patterns = [
        f"{component_name}/{component_name}-component.html",
        f"{component_name}/index.html",
        f"{component_name}.html"
    ]
    
    base = Path(base_path)
    for pattern in patterns:
        file_path = base / pattern
        if file_path.exists():
            return file_path
    
    return None


def analyze_semantic_coverage(html_content: str) -> Dict[str, Any]:
    """
    Analyze the semantic coverage of HTML content
    
    Args:
        html_content: HTML content to analyze
        
    Returns:
        Analysis results including coverage scores and missing tags
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    results = {
        "total_elements": 0,
        "tagged_elements": 0,
        "coverage_by_category": {},
        "missing_required": [],
        "missing_recommended": [],
        "found_tags": [],
        "score": 0.0
    }
    
    # Count total elements (excluding script/style)
    all_elements = soup.find_all(lambda tag: tag.name not in ['script', 'style', 'meta', 'link'])
    results["total_elements"] = len(all_elements)
    
    # Find all elements with data-tekton attributes
    def has_tekton_attrs(tag):
        """Check if tag has any data-tekton attributes"""
        if not tag.attrs:
            return False
        return any(attr.startswith('data-tekton-') for attr in tag.attrs.keys())
    
    tagged_elements = soup.find_all(has_tekton_attrs)
    results["tagged_elements"] = len(tagged_elements)
    
    # Collect all found semantic tags
    found_attrs = set()
    for element in tagged_elements:
        for attr in element.attrs:
            if attr.startswith('data-tekton-') or attr == 'data-component':
                found_attrs.add(attr)
    
    results["found_tags"] = sorted(list(found_attrs))
    
    # Analyze coverage by category
    total_score = 0.0
    
    for category, patterns in SEMANTIC_PATTERNS.items():
        category_results = {
            "required_found": 0,
            "required_total": len(patterns["required"]),
            "recommended_found": 0,
            "recommended_total": len(patterns["recommended"]),
            "score": 0.0
        }
        
        # Check required patterns
        for pattern in patterns["required"]:
            if pattern in found_attrs:
                category_results["required_found"] += 1
            else:
                results["missing_required"].append(f"{category}: {pattern}")
        
        # Check recommended patterns
        for pattern in patterns["recommended"]:
            if pattern in found_attrs:
                category_results["recommended_found"] += 1
            else:
                results["missing_recommended"].append(f"{category}: {pattern}")
        
        # Calculate category score
        required_score = (category_results["required_found"] / category_results["required_total"]) if category_results["required_total"] > 0 else 0
        recommended_score = (category_results["recommended_found"] / category_results["recommended_total"]) if category_results["recommended_total"] > 0 else 0
        
        # Required tags are worth 70%, recommended 30%
        category_results["score"] = (required_score * 0.7) + (recommended_score * 0.3)
        
        results["coverage_by_category"][category] = category_results
        total_score += category_results["score"] * patterns["weight"]
    
    results["score"] = round(total_score, 3)
    
    return results


def generate_recommendations(analysis: Dict[str, Any], component_name: str) -> List[Dict[str, Any]]:
    """
    Generate specific recommendations based on analysis results
    
    Args:
        analysis: Results from analyze_semantic_coverage
        component_name: Name of the component being analyzed
        
    Returns:
        List of recommendations with priority and examples
    """
    recommendations = []
    
    # High priority: Missing required tags
    if analysis["missing_required"]:
        for missing in analysis["missing_required"]:
            category, tag = missing.split(": ")
            recommendations.append({
                "priority": "high",
                "category": category,
                "tag": tag,
                "message": f"Add {tag} to {category} elements",
                "example": get_tag_example(tag, component_name),
                "impact": "Required for proper semantic structure"
            })
    
    # Medium priority: Low coverage
    if analysis["score"] < 0.5:
        recommendations.append({
            "priority": "high",
            "category": "overall",
            "tag": None,
            "message": f"Low semantic coverage ({analysis['score']:.1%}). Consider comprehensive tagging.",
            "example": None,
            "impact": "Improves discoverability and automation"
        })
    
    # Low priority: Missing recommended tags
    for missing in analysis["missing_recommended"][:3]:  # Limit to top 3
        category, tag = missing.split(": ")
        recommendations.append({
            "priority": "medium",
            "category": category,
            "tag": tag,
            "message": f"Consider adding {tag} to enhance {category}",
            "example": get_tag_example(tag, component_name),
            "impact": "Enhances semantic richness"
        })
    
    # Element coverage recommendation
    coverage_percent = (analysis["tagged_elements"] / analysis["total_elements"] * 100) if analysis["total_elements"] > 0 else 0
    if coverage_percent < 20:
        recommendations.append({
            "priority": "high",
            "category": "coverage",
            "tag": None,
            "message": f"Only {coverage_percent:.0f}% of elements have semantic tags",
            "example": None,
            "impact": "Most elements lack semantic meaning"
        })
    
    return recommendations


def get_tag_example(tag: str, component_name: str) -> str:
    """
    Get example usage for a semantic tag
    
    Args:
        tag: The semantic tag
        component_name: Component context
        
    Returns:
        Example HTML snippet
    """
    examples = {
        "data-tekton-nav": f'<nav data-tekton-nav="main">',
        "data-tekton-nav-item": f'<li data-tekton-nav-item="{component_name}">',
        "data-tekton-component": f'<div data-tekton-component="{component_name}">',
        "data-tekton-area": f'<section data-tekton-area="{component_name}-content">',
        "data-tekton-action": f'<button data-tekton-action="submit">',
        "data-tekton-state": f'<div data-tekton-state="active">',
        "data-tekton-id": f'<div data-tekton-id="{component_name}-{"{unique-id}"}">',
    }
    
    return examples.get(tag, f'<element {tag}="value">')


async def analyze_component(component_name: str) -> Dict[str, Any]:
    """
    Main entry point for analyzing a component's semantic structure
    
    Args:
        component_name: Name of the component to analyze
        
    Returns:
        Complete analysis with coverage, scores, and recommendations
    """
    result = {
        "component": component_name,
        "file_path": None,
        "analysis": None,
        "recommendations": [],
        "error": None
    }
    
    try:
        # Find the component HTML file
        file_path = find_component_html_file(component_name)
        if not file_path:
            result["error"] = f"Could not find HTML file for component '{component_name}'"
            return result
        
        result["file_path"] = str(file_path)
        
        # Read and analyze the HTML
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Perform semantic analysis
        analysis = analyze_semantic_coverage(html_content)
        result["analysis"] = analysis
        
        # Generate recommendations
        recommendations = generate_recommendations(analysis, component_name)
        result["recommendations"] = recommendations
        
        # Add summary
        result["summary"] = {
            "score": analysis["score"],
            "grade": get_grade(analysis["score"]),
            "tagged_elements": f"{analysis['tagged_elements']}/{analysis['total_elements']}",
            "missing_required_count": len(analysis["missing_required"]),
            "recommendation_count": len(recommendations)
        }
        
    except Exception as e:
        result["error"] = f"Analysis failed: {str(e)}"
    
    return result


def get_grade(score: float) -> str:
    """Convert score to letter grade"""
    if score >= 0.9:
        return "A"
    elif score >= 0.8:
        return "B"
    elif score >= 0.7:
        return "C"
    elif score >= 0.6:
        return "D"
    else:
        return "F"