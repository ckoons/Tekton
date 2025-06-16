"""
JSON formatter for converting CLI output to structured JSON

This allows the CLI output to be consumed by the GUI wrapper
"""

import json
from typing import Any, Dict, List, Union, Optional
from datetime import datetime

def format_output(data: Any) -> Dict[str, Any]:
    """Format CLI output as structured JSON for GUI consumption"""
    
    # If already a dict, work with that
    if isinstance(data, dict):
        return data
        
    # Handle agent list
    if hasattr(data, "__iter__") and not isinstance(data, (str, bytes, dict)):
        # Check if these are agents
        if all(hasattr(item, "id") and hasattr(item, "name") for item in data):
            return {
                "success": True,
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "description": agent.description or "",
                        "model_name": agent.model_name,
                        "agent_type": getattr(agent, "agent_type", "standard"),
                        "created_at": agent.created_at.isoformat() if agent.created_at else None
                    }
                    for agent in data
                ]
            }
        
        # Generic list
        return {
            "success": True,
            "items": [format_item(item) for item in data]
        }
    
    # Handle single agent
    if hasattr(data, "id") and hasattr(data, "name"):
        return {
            "success": True,
            "agent": {
                "id": data.id,
                "name": data.name,
                "description": data.description or "",
                "model_name": data.model_name,
                "agent_type": getattr(data, "agent_type", "standard"),
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
        }
        
    # Handle string responses (like from run_agent)
    if isinstance(data, str):
        return {
            "success": True,
            "message": data
        }
    
    # Handle boolean responses
    if isinstance(data, bool):
        return {
            "success": data
        }
    
    # Handle None
    if data is None:
        return {
            "success": True
        }
    
    # Generic object
    return {
        "success": True,
        "data": format_item(data)
    }

def format_item(item: Any) -> Any:
    """Format a single item for JSON output"""
    
    # Handle datetime
    if isinstance(item, datetime):
        return item.isoformat()
    
    # Handle objects with __dict__
    if hasattr(item, "__dict__"):
        return {k: format_item(v) for k, v in item.__dict__.items() 
                if not k.startswith("_")}
    
    # Handle other iterables
    if hasattr(item, "__iter__") and not isinstance(item, (str, bytes, dict)):
        return [format_item(i) for i in item]
    
    # Handle dictionaries
    if isinstance(item, dict):
        return {k: format_item(v) for k, v in item.items()}
    
    # Return simple types as-is
    return item