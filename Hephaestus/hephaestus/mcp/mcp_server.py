"""
Hephaestus UI DevTools MCP Server
"""

import asyncio
import inspect
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
hephaestus_root = os.path.dirname(os.path.dirname(current_dir))
tekton_root = os.path.dirname(hephaestus_root)
sys.path.insert(0, hephaestus_root)
sys.path.insert(0, tekton_root)

from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
# Initialize logger
logger = setup_component_logging("hephaestus_mcp")

from hephaestus.mcp.ui_tools_v2 import (
    ui_capture, ui_interact, ui_sandbox, ui_analyze, ui_list_areas, ui_help, browser_manager
)

# Debug imports
logger.info(f"Imported ui_capture type: {type(ui_capture)}")
logger.info(f"Imported ui_interact type: {type(ui_interact)}")
logger.info(f"Imported ui_sandbox type: {type(ui_sandbox)}")
logger.info(f"Imported ui_analyze type: {type(ui_analyze)}")

# Import configuration
from shared.utils.global_config import GlobalConfig

# MCP Server configuration
global_config = GlobalConfig.get_instance()
MCP_PORT = global_config.config.hephaestus.mcp_port
COMPONENT_NAME = "hephaestus_ui_devtools"
VERSION = "0.1.0"

# Global state
hermes_registration: Optional[HermesRegistration] = None
heartbeat_task: Optional[asyncio.Task] = None


# Tool metadata for MCP
TOOL_METADATA = {
    "ui_list_areas": {
        "name": "ui_list_areas",
        "description": "List all available UI areas in Hephaestus",
        "category": "ui",
        "tags": ["ui", "discovery", "areas"],
        "parameters": {}
    },
    "ui_capture": {
        "name": "ui_capture",
        "description": "Capture UI state from Hephaestus UI without screenshots",
        "category": "ui",
        "tags": ["ui", "capture", "analysis"],
        "parameters": {
            "area": {
                "type": "string",
                "description": "UI area name (e.g., 'rhetor', 'navigation', 'content'). Use 'hephaestus' for entire UI",
                "required": False,
                "default": "hephaestus"
            },
            "selector": {
                "type": "string",
                "description": "Optional CSS selector to focus on specific elements within the area",
                "required": False
            },
            "include_screenshot": {
                "type": "boolean",
                "description": "Whether to include a visual screenshot",
                "required": False,
                "default": False
            }
        }
    },
    "ui_interact": {
        "name": "ui_interact",
        "description": "Interact with UI elements in Hephaestus",
        "category": "ui",
        "tags": ["ui", "interaction", "automation"],
        "parameters": {
            "area": {
                "type": "string",
                "description": "UI area name (use 'hephaestus' for general interactions)",
                "required": True
            },
            "action": {
                "type": "string",
                "description": "Type of action ('click', 'type', 'select', 'hover')",
                "required": True,
                "enum": ["click", "type", "select", "hover"]
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for the element",
                "required": True
            },
            "value": {
                "type": "string",
                "description": "Value for type/select actions",
                "required": False
            },
            "capture_changes": {
                "type": "boolean",
                "description": "Whether to capture before/after state",
                "required": False,
                "default": True
            }
        }
    },
    "ui_sandbox": {
        "name": "ui_sandbox",
        "description": "Test UI changes in a sandboxed environment",
        "category": "ui",
        "tags": ["ui", "sandbox", "testing", "safety"],
        "parameters": {
            "area": {
                "type": "string",
                "description": "UI area to modify (use 'hephaestus' for general changes)",
                "required": True
            },
            "changes": {
                "type": "array",
                "description": "List of changes to apply",
                "required": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["html", "css", "js"]
                        },
                        "selector": {
                            "type": "string"
                        },
                        "content": {
                            "type": "string"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["replace", "append", "prepend", "after", "before"]
                        }
                    }
                }
            },
            "preview": {
                "type": "boolean",
                "description": "Whether to preview changes without applying",
                "required": False,
                "default": True
            }
        }
    },
    "ui_analyze": {
        "name": "ui_analyze",
        "description": "Analyze UI structure and patterns",
        "category": "ui",
        "tags": ["ui", "analysis", "structure"],
        "parameters": {
            "area": {
                "type": "string",
                "description": "UI area to analyze",
                "required": False,
                "default": "hephaestus"
            },
            "deep_scan": {
                "type": "boolean",
                "description": "Whether to perform deep analysis",
                "required": False,
                "default": False
            }
        }
    },
    "ui_help": {
        "name": "ui_help",
        "description": "Get help about UI DevTools usage - your guide to success!",
        "category": "ui",
        "tags": ["ui", "help", "guidance", "documentation"],
        "parameters": {
            "topic": {
                "type": "string",
                "description": "Specific help topic: 'areas', 'selectors', 'frameworks', 'errors', 'tasks', 'architecture'",
                "required": False,
                "enum": ["areas", "selectors", "frameworks", "errors", "tasks", "architecture"]
            }
        }
    }
}


# FastAPI lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global hermes_registration, heartbeat_task
    
    logger.info(f"Starting hephaestus_ui_devtools MCP server on port {MCP_PORT}")
    
    # Initialize browser manager
    await browser_manager.initialize()
    
    # Note: Hermes registration is handled by HephaestusComponent
    # The MCP server runs as a subprocess and doesn't need separate registration
    logger.info("MCP DevTools server initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down hephaestus_ui_devtools MCP server")
    
    # Clean up browser
    await browser_manager.cleanup()


# Create FastAPI app
app = FastAPI(
    title="hephaestus_ui_devtools MCP Server",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP router
mcp_router = APIRouter(prefix="/api/mcp/v2")


@mcp_router.get("/capabilities")
async def get_capabilities():
    """Get MCP capabilities"""
    return {
        "name": "hephaestus_ui_devtools",
        "version": "0.1.0",
        "description": "UI DevTools for safe UI manipulation",
        "tools": list(TOOL_METADATA.keys()),
        "metadata": {
            "category": "devtools",
            "mcp_version": "2.0"
        }
    }


@mcp_router.get("/tools")
async def get_tools():
    """Get available tools"""
    return {
        "tools": TOOL_METADATA
    }


@mcp_router.post("/execute")
async def execute_tool(request_data: Dict[str, Any]):
    """Execute a tool"""
    tool_name = request_data.get("tool_name")
    arguments = request_data.get("arguments", {})
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="tool_name is required")
    
    # Map tool names to functions
    tool_functions = {
        "ui_list_areas": ui_list_areas,
        "ui_capture": ui_capture,
        "ui_interact": ui_interact,
        "ui_sandbox": ui_sandbox,
        "ui_analyze": ui_analyze,
        "ui_help": ui_help
    }
    
    if tool_name not in tool_functions:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    tool_func = tool_functions[tool_name]
    
    try:
        # Debug logging
        logger.info(f"Executing tool '{tool_name}' with arguments: {arguments}")
        logger.info(f"Tool function type: {type(tool_func)}")
        
        # Validate required parameters
        tool_meta = TOOL_METADATA[tool_name]
        for param_name, param_info in tool_meta["parameters"].items():
            if param_info.get("required", False) and param_name not in arguments:
                raise HTTPException(
                    status_code=400,
                    detail=f"Required parameter '{param_name}' not provided"
                )
        
        # Execute tool - all our tools are async
        result = await tool_func(**arguments)
        
        return {
            "status": "success",
            "result": result,
            "error": None
        }
    
    except Exception as e:
        import traceback
        logger.error(f"Error executing tool '{tool_name}': {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "result": None,
            "error": str(e)
        }


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "component": "hephaestus_ui_devtools",
        "version": "0.1.0",
        "port": MCP_PORT,
        "registered": False  # MCP server doesn't register separately
    }


@app.get("/ready")
async def ready_check():
    """Readiness check endpoint"""
    # Check if browser is initialized
    browser_ready = browser_manager.browser is not None
    
    return {
        "ready": browser_ready,
        "component": "hephaestus_ui_devtools",
        "version": "0.1.0",
        "checks": {
            "browser": browser_ready
        }
    }


# Add MCP router to app
app.include_router(mcp_router)


def main():
    """Run the MCP server"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()