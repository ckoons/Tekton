"""
Recommendation Tools Module for Hephaestus UI DevTools

This module contains functions for analyzing user requests and recommending
the optimal approach (DevTools vs file editing) based on the target and context.
"""

from typing import Dict, Any

from .browser_manager import browser_manager
from .capture_tools import ui_capture


async def ui_recommend_approach(
    target_description: str,
    intended_change: str,
    area: str = "hephaestus"
) -> Dict[str, Any]:
    """
    Phase 1: Analyze request and recommend optimal tool path with confidence scoring
    
    Args:
        target_description: Description of what you want to modify (e.g., "chat interface", "navigation button")
        intended_change: What you want to do (e.g., "add semantic tags", "change text", "add element")
        area: UI area to work in
    
    Returns:
        Recommendation with reasoning and specific guidance
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "target": target_description,
        "change": intended_change,
        "area": area,
        "recommended_tool": "devtools",
        "confidence": 0.0,
        "reasoning": "",
        "specific_guidance": "",
        "fallback_strategy": "",
        "file_locations": []
    }
    
    # Capture current area to analyze
    try:
        capture_result = await ui_capture(area=area)
        dynamic_analysis = capture_result.get("dynamic_analysis", {})
    except Exception as e:
        result["recommended_tool"] = "file_editing"
        result["confidence"] = 0.9
        result["reasoning"] = f"Could not access UI area '{area}': {str(e)}. File editing is safer."
        result["specific_guidance"] = f"Edit the {area}-component.html file directly"
        return result
    
    # Analyze the request
    target_lower = target_description.lower()
    change_lower = intended_change.lower()
    
    # Pattern matching for common scenarios
    dynamic_keywords = ["chat", "form", "input", "panel", "content", "interface", "workspace"]
    navigation_keywords = ["nav", "button", "link", "menu", "header", "footer"]
    semantic_keywords = ["semantic", "tag", "attribute", "data-tekton"]
    
    # Check if target involves dynamic content
    involves_dynamic = any(keyword in target_lower for keyword in dynamic_keywords)
    involves_navigation = any(keyword in target_lower for keyword in navigation_keywords)
    involves_semantics = any(keyword in change_lower for keyword in semantic_keywords)
    
    # Factor in dynamic analysis
    content_type = dynamic_analysis.get("content_type", "static")
    dynamic_areas = dynamic_analysis.get("dynamic_areas", [])
    
    # Decision logic
    if content_type == "static" and not involves_dynamic:
        # Static content, safe for DevTools
        result["recommended_tool"] = "devtools"
        result["confidence"] = 0.95
        result["reasoning"] = "Static content area with no dynamic loading detected. DevTools are ideal."
        result["specific_guidance"] = f"Use ui_sandbox with area='{area}' and appropriate selectors"
    
    elif involves_navigation and not involves_dynamic:
        # Navigation elements, usually safe for DevTools
        result["recommended_tool"] = "devtools"
        result["confidence"] = 0.9
        result["reasoning"] = "Navigation elements are typically static and well-suited for DevTools"
        result["specific_guidance"] = "Target navigation elements with selectors like .nav-label or [data-tekton-nav]"
    
    elif involves_dynamic or content_type == "dynamic":
        # Dynamic content, recommend file editing
        result["recommended_tool"] = "file_editing"
        result["confidence"] = 0.85
        result["reasoning"] = "Target involves dynamic content areas that DevTools cannot see reliably"
        result["specific_guidance"] = f"Edit {area}-component.html directly for component interior content"
        
        # Add specific file locations if available
        if dynamic_areas:
            for da in dynamic_areas:
                if area in da.get("file_location", ""):
                    result["file_locations"].append(da["file_location"])
    
    elif content_type == "hybrid":
        # Hybrid content, depends on specific target
        if involves_navigation or involves_semantics:
            result["recommended_tool"] = "devtools"
            result["confidence"] = 0.75
            result["reasoning"] = "Hybrid content but targeting navigation/semantic elements that DevTools can handle"
            result["specific_guidance"] = "Try DevTools first, fall back to file editing if elements not found"
        else:
            result["recommended_tool"] = "file_editing"
            result["confidence"] = 0.8
            result["reasoning"] = "Hybrid content and target description suggests component interior work"
            result["specific_guidance"] = f"Edit {area}-component.html for better access to component internals"
    
    else:
        # Default fallback
        result["recommended_tool"] = "devtools"
        result["confidence"] = 0.6
        result["reasoning"] = "Default recommendation - try DevTools first as it's safer"
        result["specific_guidance"] = "Start with DevTools, switch to file editing if needed"
    
    # Build fallback strategy
    if result["recommended_tool"] == "devtools":
        result["fallback_strategy"] = f"If DevTools fails to find elements, try file editing {area}-component.html"
    else:
        result["fallback_strategy"] = f"If file editing is too complex, try DevTools with area='{area}' first"
    
    # Add file locations if not already specified
    if not result["file_locations"] and area != "hephaestus":
        result["file_locations"] = [f"{area}-component.html"]
    
    # Time estimates
    if result["recommended_tool"] == "devtools":
        result["time_estimate"] = "~30 seconds with DevTools, ~5 minutes with file editing"
    else:
        result["time_estimate"] = "~5 minutes with file editing, DevTools may not work"
    
    return result