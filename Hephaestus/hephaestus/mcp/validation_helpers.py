"""
Parameter validation helpers for UI DevTools

Provides helpful error messages and suggestions when parameters are wrong.
"""
from typing import Dict, List, Any, Optional
import difflib
from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("ui_validation")


def suggest_similar(wrong_value: str, valid_values: List[str], cutoff: float = 0.6) -> Optional[str]:
    """Find the most similar valid value"""
    matches = difflib.get_close_matches(wrong_value, valid_values, n=1, cutoff=cutoff)
    return matches[0] if matches else None


def validate_tool_parameters(
    tool_name: str,
    provided_params: Dict[str, Any],
    valid_params: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate parameters for a tool and provide helpful error messages
    
    Args:
        tool_name: Name of the tool being called
        provided_params: Parameters provided by the user
        valid_params: Dictionary of valid parameter names and their specs
        
    Returns:
        Dict with validation results
    """
    result = {"valid": True, "errors": [], "warnings": [], "suggestions": {}}
    
    # Check for unknown parameters
    unknown_params = [p for p in provided_params if p not in valid_params]
    
    if unknown_params:
        for param in unknown_params:
            error_msg = f"Unknown parameter '{param}'"
            
            # Find similar valid parameter
            suggestion = suggest_similar(param, list(valid_params.keys()))
            if suggestion:
                error_msg += f" - did you mean '{suggestion}'?"
                result["suggestions"][param] = suggestion
            
            result["errors"].append(error_msg)
        
        # Add helpful context based on tool and common mistakes
        if tool_name == "ui_capture" and "selector" in unknown_params:
            result["errors"].append(
                "💡 Tip: ui_capture doesn't take 'selector' parameter. "
                "To capture specific elements, first capture the area then search the HTML."
            )
        
        if tool_name == "ui_sandbox" and "component" in unknown_params:
            result["errors"].append(
                "💡 Tip: ui_sandbox uses 'area' not 'component'. "
                "After navigating to a component, use area='content' for modifications."
            )
    
    # Check for required parameters
    for param_name, param_spec in valid_params.items():
        if param_spec.get("required", False) and param_name not in provided_params:
            result["errors"].append(f"Required parameter '{param_name}' is missing")
    
    # Validate parameter types and values
    for param_name, param_value in provided_params.items():
        if param_name in valid_params:
            spec = valid_params[param_name]
            
            # Type validation
            expected_type = spec.get("type")
            if expected_type:
                if not validate_type(param_value, expected_type):
                    result["errors"].append(
                        f"Parameter '{param_name}' should be {expected_type}, got {type(param_value).__name__}"
                    )
            
            # Enum validation
            if "enum" in spec and param_value not in spec["enum"]:
                result["errors"].append(
                    f"Parameter '{param_name}' must be one of: {', '.join(spec['enum'])}"
                )
                suggestion = suggest_similar(str(param_value), spec["enum"])
                if suggestion:
                    result["suggestions"][param_name] = suggestion
    
    # Check for deprecated patterns
    if tool_name == "ui_visual_diff":
        if "before_state" in provided_params or "after_state" in provided_params:
            result["warnings"].append(
                "⚠️  Parameters 'before_state' and 'after_state' are deprecated. "
                "Use 'before_action' and 'after_action' instead."
            )
    
    result["valid"] = len(result["errors"]) == 0
    
    return result


def validate_type(value: Any, expected_type: str) -> bool:
    """Validate that a value matches the expected type"""
    type_map = {
        "string": str,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict
    }
    
    expected = type_map.get(expected_type, str)
    return isinstance(value, expected)


def format_validation_error(validation_result: Dict[str, Any]) -> str:
    """Format validation results into a helpful error message"""
    if validation_result["valid"]:
        return ""
    
    parts = ["Parameter validation failed:"]
    
    # Add errors
    for error in validation_result["errors"]:
        parts.append(f"  ❌ {error}")
    
    # Add warnings
    for warning in validation_result["warnings"]:
        parts.append(f"  ⚠️  {warning}")
    
    # Add suggestions
    if validation_result["suggestions"]:
        parts.append("\nSuggestions:")
        for param, suggestion in validation_result["suggestions"].items():
            parts.append(f"  💡 '{param}' → '{suggestion}'")
    
    return "\n".join(parts)


def smart_area_detection(component: Optional[str] = None, area: Optional[str] = None) -> str:
    """
    Smart detection of which area to use based on context
    
    This helps avoid the common confusion where users provide a component
    when they should use area='content'
    """
    if area:
        return area
    
    if component:
        # User probably means content area for component modifications
        logger.info(f"Auto-detected: Using area='content' for {component} modifications")
        return "content"
    
    # Default to hephaestus (full page)
    return "hephaestus"