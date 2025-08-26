#!/usr/bin/env python3
"""
Response Monitor - Detects sundown responses and sets fresh start flag
"""

from typing import Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from aish.src.registry.ci_registry import get_registry


def check_sundown_response(ci_name: str, message: str, response: str) -> bool:
    """
    Check if this is a response to a sundown prompt.
    
    Args:
        ci_name: CI name
        message: Original message sent
        response: CI's response
        
    Returns:
        True if this was a sundown response
    """
    sundown_indicators = [
        "[SYSTEM: Approaching token limit",
        "Please summarize:",
        "What you've been working on",
        "What should continue tomorrow",
        "SUNSET_PROTOCOL",
        "Time to wrap up"
    ]
    
    # Check if the message contained sundown prompt
    is_sundown = any(indicator in message for indicator in sundown_indicators)
    
    # Also check response for summary indicators
    summary_indicators = [
        "been working on",
        "continue tomorrow",
        "summarize",
        "wrap up",
        "next session",
        "when we resume"
    ]
    
    has_summary = any(indicator.lower() in response.lower() for indicator in summary_indicators)
    
    return is_sundown or has_summary


def handle_post_response(ci_name: str, message: str, response: str):
    """
    Handle post-response actions like setting fresh start after sundown.
    
    Args:
        ci_name: CI name
        message: Original message
        response: CI's response
    """
    registry = get_registry()
    
    # Check if this was a sundown response
    if check_sundown_response(ci_name, message, response):
        print(f"[Response Monitor] Detected sundown response from {ci_name}")
        
        # NOW set fresh start for next interaction
        registry.set_needs_fresh_start(ci_name, True)
        print(f"[Response Monitor] Set needs_fresh_start = True for {ci_name}")
        print(f"[Response Monitor] Next message will start fresh without --continue")
        
        # Store the summary as sunrise context
        registry.update_sunrise_context(ci_name, response)
        print(f"[Response Monitor] Stored summary for sunrise context")
        
        return True
    
    return False


def get_response_monitor():
    """Get response monitor singleton."""
    return {
        'check_sundown': check_sundown_response,
        'handle_response': handle_post_response
    }