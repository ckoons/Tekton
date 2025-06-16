"""
MCP Module for Budget

This module provides Model Context Protocol (MCP) support 
for the Budget component using FastMCP.
"""

# Import standardized exports
from .tools import (
    # Budget Management
    allocate_budget,
    check_budget,
    record_usage,
    get_budget_status,
    
    # Model Recommendations
    get_model_recommendations,
    route_with_budget_awareness,
    
    # Analytics
    get_usage_analytics,
    
    # Registration functions
    register_budget_tools,
    register_analytics_tools,
    get_all_tools,
    get_all_capabilities
)