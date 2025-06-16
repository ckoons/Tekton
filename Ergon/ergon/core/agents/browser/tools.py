import os
import sys
import asyncio
from typing import Dict, List, Optional, Any

# Try to import TektonBaseModel, fall back to regular BaseModel if not available
try:
    # Add Tekton root to path if not already present
    tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
    if tekton_root not in sys.path:
        sys.path.insert(0, tekton_root)
    from tekton.models.base import TektonBaseModel
except ImportError:
    # Fallback to regular BaseModel if TektonBaseModel is not available
    from pydantic import BaseModel as TektonBaseModel

from pydantic import Field
import json

class BrowserActions(TektonBaseModel):
    navigate: str = Field(..., description="Navigate to a specific URL")
    get_text: str = Field(..., description="Get visible text from the current page")
    get_html: str = Field(..., description="Get HTML from the current page")
    click: str = Field(..., description="Click on an element using selector")
    type: str = Field(..., description="Type text into an element using selector")
    screenshot: str = Field(..., description="Take screenshot of the current page")
    scroll: str = Field(..., description="Scroll the page (up, down, or to element)")
    wait: str = Field(..., description="Wait for specified milliseconds")
    get_element: str = Field(..., description="Get element information using selector")

# Tool definitions for LLM to use
BROWSER_TOOLS = [
    {
        "name": "browse_navigate",
        "description": "Navigate to a URL in the browser",
        "function_def": {
            "name": "browse_navigate",
            "description": "Navigate to a URL in the browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "name": "browse_get_text",
        "description": "Get all text content from the current page",
        "function_def": {
            "name": "browse_get_text",
            "description": "Get all text content from the current page",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "name": "browse_get_html",
        "description": "Get the HTML source of the current page",
        "function_def": {
            "name": "browse_get_html",
            "description": "Get the HTML source of the current page",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "name": "browse_click",
        "description": "Click on an element using CSS selector",
        "function_def": {
            "name": "browse_click",
            "description": "Click on an element using CSS selector",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element to click"
                    }
                },
                "required": ["selector"]
            }
        }
    },
    {
        "name": "browse_type",
        "description": "Type text into a field using CSS selector",
        "function_def": {
            "name": "browse_type",
            "description": "Type text into a field using CSS selector",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the input field"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type into the field"
                    }
                },
                "required": ["selector", "text"]
            }
        }
    },
    {
        "name": "browse_screenshot",
        "description": "Take a screenshot of the current page",
        "function_def": {
            "name": "browse_screenshot",
            "description": "Take a screenshot of the current page",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to save the screenshot (optional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "name": "browse_scroll",
        "description": "Scroll the page up, down, or to an element",
        "function_def": {
            "name": "browse_scroll",
            "description": "Scroll the page up, down, or to an element",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "Direction to scroll: 'up', 'down', or 'to_element'"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element to scroll to (only used with 'to_element')"
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Amount to scroll in pixels (only used with 'up' or 'down')"
                    }
                },
                "required": ["direction"]
            }
        }
    },
    {
        "name": "browse_wait",
        "description": "Wait for a specified amount of time in milliseconds",
        "function_def": {
            "name": "browse_wait",
            "description": "Wait for a specified amount of time in milliseconds",
            "parameters": {
                "type": "object",
                "properties": {
                    "milliseconds": {
                        "type": "integer",
                        "description": "Time to wait in milliseconds"
                    }
                },
                "required": ["milliseconds"]
            }
        }
    },
    {
        "name": "browse_get_element",
        "description": "Get information about an element using CSS selector",
        "function_def": {
            "name": "browse_get_element",
            "description": "Get information about an element using CSS selector",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element"
                    }
                },
                "required": ["selector"]
            }
        }
    }
]