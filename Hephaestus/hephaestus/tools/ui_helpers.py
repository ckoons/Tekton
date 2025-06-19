"""
UI Helper improvements - Better error messages and parameter validation
"""
from typing import Dict, List, Any, Optional
import difflib

def suggest_similar(wrong_param: str, valid_params: List[str], cutoff: float = 0.6) -> Optional[str]:
    """Find the most similar valid parameter"""
    matches = difflib.get_close_matches(wrong_param, valid_params, n=1, cutoff=cutoff)
    return matches[0] if matches else None

def validate_parameters(provided: Dict[str, Any], valid: List[str], tool_name: str) -> Dict[str, Any]:
    """
    Validate parameters and provide helpful error messages
    """
    invalid_params = [p for p in provided if p not in valid]
    
    if not invalid_params:
        return {"valid": True}
    
    # Build helpful error message
    error_parts = [f"Invalid parameters for {tool_name}:"]
    
    for param in invalid_params:
        suggestion = suggest_similar(param, valid)
        if suggestion:
            error_parts.append(f"  ❌ '{param}' - did you mean '{suggestion}'?")
        else:
            error_parts.append(f"  ❌ '{param}' - not recognized")
    
    error_parts.append(f"\n✅ Valid parameters: {', '.join(valid)}")
    
    # Add common mistakes
    if tool_name == "ui_capture" and "selector" in invalid_params:
        error_parts.append("\n💡 Tip: ui_capture doesn't take 'selector'. Try 'wait_for_selector' or capture the area first, then search the HTML.")
    
    if tool_name == "ui_sandbox" and "component" in invalid_params:
        error_parts.append("\n💡 Tip: ui_sandbox uses 'area' not 'component'. After navigating to a component, use area='content'.")
    
    return {
        "valid": False,
        "error": "\n".join(error_parts),
        "invalid_params": invalid_params,
        "suggestions": {p: suggest_similar(p, valid) for p in invalid_params}
    }

def smart_area_detection(component: Optional[str] = None, area: Optional[str] = None) -> str:
    """
    Smart detection of which area to use based on context
    """
    if area:
        return area
    
    if component:
        # User probably means content area for component modifications
        print(f"📍 Auto-detected: Using area='content' for {component} modifications")
        return "content"
    
    # Default to content
    return "content"

def format_response_with_visual_hint(result: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
    """
    Add visual hints to responses for better understanding
    """
    if result.get("status") != "success":
        return result
    
    # Add visual hints based on tool
    if tool_name == "ui_navigate":
        component = result.get("component", "unknown")
        result["visual_hint"] = f"""
Navigation: [{component}] ← clicked
Status: ✅ Success
Next: Use area='content' to modify the component
"""
    
    elif tool_name == "ui_capture":
        area = result.get("area", "unknown")
        element_count = len(result.get("result", {}).get("structure", {}).get("elements", []))
        result["visual_hint"] = f"""
Captured: {area} area
Elements: {element_count} found
Tip: Look in result['result']['structure']['elements']
"""
    
    elif tool_name == "ui_sandbox":
        changes = result.get("changes", [])
        result["visual_hint"] = f"""
Modified: {len(changes)} elements
Status: ✅ Applied
Tip: Take a screenshot to verify!
"""
    
    return result