"""
Utility functions for metrics module.
"""

from typing import Dict, Any, Union, List

def session_to_dict(session_data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """Convert session data to dictionary format.
    
    Args:
        session_data: Session data object or dict
        
    Returns:
        Dictionary representation of session data
    """
    return session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
    
def sessions_to_dicts(sessions: List[Union[Dict[str, Any], Any]]) -> List[Dict[str, Any]]:
    """Convert a list of session data objects to dictionary format.
    
    Args:
        sessions: List of session data objects or dicts
        
    Returns:
        List of dictionaries
    """
    return [session_to_dict(session) for session in sessions]

def interpret_bifurcation_proximity(bpi: float) -> str:
    """Interpret the bifurcation proximity index value.
    
    Args:
        bpi: Bifurcation proximity index
        
    Returns:
        Human-readable interpretation
    """
    if bpi > 0.8:
        return "Very high proximity to bifurcation - system is likely at the edge of a capability threshold"
    elif bpi > 0.6:
        return "High proximity to bifurcation - system may be approaching a capability threshold"
    elif bpi > 0.4:
        return "Moderate proximity to bifurcation - some indicators of approaching threshold"
    elif bpi > 0.2:
        return "Low proximity to bifurcation - system is in a relatively stable region"
    else:
        return "Very low proximity to bifurcation - system is in a highly stable region"

def interpret_parameter_sensitivity(sensitivity: float, non_linearity: float) -> str:
    """Interpret parameter sensitivity and non-linearity.
    
    Args:
        sensitivity: Normalized sensitivity value
        non_linearity: Non-linearity score
        
    Returns:
        Human-readable interpretation
    """
    sensitivity_abs = abs(sensitivity)
    
    if sensitivity_abs < 0.1:
        sens_text = "very low sensitivity"
    elif sensitivity_abs < 0.3:
        sens_text = "low sensitivity"
    elif sensitivity_abs < 0.5:
        sens_text = "moderate sensitivity"
    elif sensitivity_abs < 0.8:
        sens_text = "high sensitivity"
    else:
        sens_text = "very high sensitivity"
        
    if non_linearity < 0.2:
        nl_text = "linear response"
    elif non_linearity < 0.5:
        nl_text = "somewhat non-linear response"
    elif non_linearity < 0.8:
        nl_text = "highly non-linear response"
    else:
        nl_text = "extremely non-linear response (potential catastrophe point)"
        
    direction = "positive" if sensitivity > 0 else "negative"
    
    return f"Parameter shows {sens_text} with {direction} correlation and {nl_text}"

def interpret_hysteresis(hysteresis_index: float) -> str:
    """Interpret hysteresis index value.
    
    Args:
        hysteresis_index: Hysteresis index value
        
    Returns:
        Human-readable interpretation
    """
    if hysteresis_index < 0.1:
        return "Minimal hysteresis - system behaves similarly whether parameter is increasing or decreasing"
    elif hysteresis_index < 0.3:
        return "Mild hysteresis - system shows some path dependence"
    elif hysteresis_index < 0.5:
        return "Moderate hysteresis - clear evidence of path dependence"
    elif hysteresis_index < 0.7:
        return "Strong hysteresis - system shows significant memory effects"
    else:
        return "Extreme hysteresis - system behavior strongly depends on parameter history (strong evidence of fold catastrophe)"