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
from fastapi.responses import JSONResponse, PlainTextResponse
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
    ui_capture, ui_navigate, ui_interact, ui_sandbox, ui_analyze, ui_validate, ui_batch, ui_list_areas, ui_help, ui_recommend_approach, 
    ui_semantic_analysis, ui_semantic_scan, ui_semantic_patterns,
    ui_component_map, ui_architecture_scan, ui_dependency_graph,
    ui_screenshot, ui_visual_diff, ui_capture_all_components,
    ui_workflow,
    browser_manager
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
    "ui_recommend_approach": {
        "name": "ui_recommend_approach",
        "description": "Get intelligent recommendations for optimal tool path (Phase 1 enhancement)",
        "category": "ui",
        "tags": ["ui", "recommendation", "routing", "intelligence"],
        "parameters": {
            "target_description": {
                "type": "string",
                "description": "Description of what you want to modify (e.g., 'chat interface', 'navigation button')",
                "required": True
            },
            "intended_change": {
                "type": "string", 
                "description": "What you want to do (e.g., 'add semantic tags', 'change text', 'add element')",
                "required": True
            },
            "area": {
                "type": "string",
                "description": "UI area to work in",
                "required": False,
                "default": "hephaestus"
            }
        }
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
    "ui_navigate": {
        "name": "ui_navigate",
        "description": "Navigate to a specific component by clicking its nav item",
        "category": "ui",
        "tags": ["ui", "navigation", "components"],
        "parameters": {
            "component": {
                "type": "string",
                "description": "Component name to navigate to (e.g., 'rhetor', 'prometheus')",
                "required": True
            },
            "wait_for_load": {
                "type": "boolean",
                "description": "Whether to wait for component to fully load",
                "required": False,
                "default": True
            },
            "timeout": {
                "type": "integer",
                "description": "Maximum time to wait for component load (ms)",
                "required": False,
                "default": 10000
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
    "ui_validate": {
        "name": "ui_validate",
        "description": "Validate UI instrumentation and semantic tagging",
        "category": "ui",
        "tags": ["ui", "validation", "testing", "quality"],
        "parameters": {
            "scope": {
                "type": "string",
                "description": "Validation scope: 'current', 'navigation', or 'all'",
                "required": False,
                "default": "current",
                "enum": ["current", "navigation", "all"]
            },
            "checks": {
                "type": "array",
                "description": "Specific checks to run (defaults to all)",
                "required": False,
                "items": {"type": "string"}
            },
            "detailed": {
                "type": "boolean",
                "description": "Include detailed findings in report",
                "required": False,
                "default": False
            }
        }
    },
    "ui_batch": {
        "name": "ui_batch",
        "description": "Execute multiple UI operations in batch with atomic support",
        "category": "ui",
        "tags": ["ui", "batch", "atomic", "operations"],
        "parameters": {
            "area": {
                "type": "string",
                "description": "UI area to operate on (e.g., 'hephaestus')",
                "required": True
            },
            "operations": {
                "type": "array",
                "description": "List of operations to perform",
                "required": True,
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["rename", "remove", "add_class", "remove_class", "style", "navigate", "click"]
                        }
                    }
                }
            },
            "atomic": {
                "type": "boolean",
                "description": "If true, all operations must succeed or all are rolled back",
                "required": False,
                "default": True
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
    },
    # Phase 2 semantic analysis tools
    "ui_semantic_analysis": {
        "name": "ui_semantic_analysis",
        "description": "Analyze semantic structure of a component HTML file (Phase 2)",
        "category": "semantic",
        "tags": ["semantic", "analysis", "structure", "validation"],
        "parameters": {
            "component": {
                "type": "string",
                "description": "Component name to analyze (e.g., 'rhetor')",
                "required": True
            },
            "detailed": {
                "type": "boolean",
                "description": "Include detailed findings and recommendations",
                "required": False,
                "default": True
            }
        }
    },
    "ui_semantic_scan": {
        "name": "ui_semantic_scan",
        "description": "Scan multiple components for semantic health",
        "category": "semantic",
        "tags": ["semantic", "scan", "batch", "health"],
        "parameters": {
            "components": {
                "type": "array",
                "description": "List of components to scan (None = scan all)",
                "required": False,
                "items": {"type": "string"}
            },
            "min_score": {
                "type": "number",
                "description": "Minimum score threshold for reporting issues",
                "required": False,
                "default": 0.7
            }
        }
    },
    "ui_semantic_patterns": {
        "name": "ui_semantic_patterns",
        "description": "Get documentation of semantic patterns used by Tekton",
        "category": "semantic",
        "tags": ["semantic", "patterns", "documentation", "best-practices"],
        "parameters": {}
    },
    # Phase 3 component architecture mapping tools
    "ui_component_map": {
        "name": "ui_component_map",
        "description": "Analyze relationships for a single component (Phase 3)",
        "category": "architecture",
        "tags": ["architecture", "relationships", "mapping", "dependencies"],
        "parameters": {
            "component": {
                "type": "string",
                "description": "Component name to analyze (e.g., 'rhetor', 'hermes')",
                "required": True
            }
        }
    },
    "ui_architecture_scan": {
        "name": "ui_architecture_scan",
        "description": "Perform system-wide architecture scan",
        "category": "architecture",
        "tags": ["architecture", "system", "scan", "analysis"],
        "parameters": {
            "components": {
                "type": "array",
                "description": "List of components to analyze (None = scan all)",
                "required": False,
                "items": {"type": "string"}
            },
            "max_components": {
                "type": "integer",
                "description": "Maximum number of components to analyze",
                "required": False,
                "default": 20
            }
        }
    },
    "ui_dependency_graph": {
        "name": "ui_dependency_graph",
        "description": "Generate dependency graph visualization",
        "category": "architecture",
        "tags": ["architecture", "graph", "visualization", "dependencies"],
        "parameters": {
            "format": {
                "type": "string",
                "description": "Output format: 'ascii', 'json', or 'mermaid'",
                "required": False,
                "default": "ascii",
                "enum": ["ascii", "json", "mermaid"]
            },
            "focus": {
                "type": "string",
                "description": "Optional component to focus on",
                "required": False
            }
        }
    },
    # Phase 4 screenshot tools
    "ui_screenshot": {
        "name": "ui_screenshot",
        "description": "Take a screenshot of the Tekton UI (Phase 4 - CIs can take their own screenshots!)",
        "category": "capture",
        "tags": ["screenshot", "visual", "capture", "image"],
        "parameters": {
            "component": {
                "type": "string",
                "description": "Specific component to capture (None = entire Hephaestus)",
                "required": False
            },
            "full_page": {
                "type": "boolean",
                "description": "Capture full scrollable area or just viewport",
                "required": False,
                "default": True
            },
            "highlight": {
                "type": "string",
                "description": "CSS selector to highlight before capture",
                "required": False
            },
            "save_to_file": {
                "type": "boolean",
                "description": "Save to file in addition to returning base64",
                "required": False,
                "default": False
            }
        }
    },
    "ui_visual_diff": {
        "name": "ui_visual_diff",
        "description": "Compare UI state before and after an action",
        "category": "analysis",
        "tags": ["visual", "diff", "comparison", "testing"],
        "parameters": {
            "before_action": {
                "type": "object",
                "description": "Action to perform before first screenshot",
                "required": True
            },
            "after_action": {
                "type": "object",
                "description": "Action to perform before second screenshot",
                "required": True
            },
            "highlight_changes": {
                "type": "boolean",
                "description": "Whether to highlight what changed",
                "required": False,
                "default": True
            }
        }
    },
    "ui_capture_all_components": {
        "name": "ui_capture_all_components",
        "description": "Take screenshots of all Tekton components in sequence",
        "category": "capture",
        "tags": ["screenshot", "batch", "documentation", "all"],
        "parameters": {}
    },
    "ui_workflow": {
        "name": "ui_workflow",
        "description": "Smart UI workflow that handles common patterns automatically - eliminates area/component confusion!",
        "category": "workflow",
        "tags": ["workflow", "automation", "smart", "composite"],
        "parameters": {
            "workflow": {
                "type": "string",
                "description": "Type of workflow: modify_component, add_to_component, verify_component, debug_component",
                "required": True,
                "enum": ["modify_component", "add_to_component", "verify_component", "debug_component"]
            },
            "component": {
                "type": "string",
                "description": "Component to work with (rhetor, hermes, apollo, etc.)",
                "required": True
            },
            "changes": {
                "type": "array",
                "description": "List of changes for modify/add workflows",
                "required": False,
                "items": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string"},
                        "content": {"type": "string"},
                        "action": {
                            "type": "string",
                            "enum": ["replace", "append", "prepend", "after", "before"]
                        }
                    }
                }
            },
            "selector": {
                "type": "string",
                "description": "Optional specific selector to target",
                "required": False
            },
            "debug": {
                "type": "boolean",
                "description": "Show detailed step-by-step progress",
                "required": False,
                "default": False
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
        "ui_recommend_approach": ui_recommend_approach,
        "ui_capture": ui_capture,
        "ui_navigate": ui_navigate,
        "ui_interact": ui_interact,
        "ui_sandbox": ui_sandbox,
        "ui_analyze": ui_analyze,
        "ui_validate": ui_validate,
        "ui_batch": ui_batch,
        "ui_help": ui_help,
        # Phase 2 semantic tools
        "ui_semantic_analysis": ui_semantic_analysis,
        "ui_semantic_scan": ui_semantic_scan,
        "ui_semantic_patterns": ui_semantic_patterns,
        # Phase 3 architecture mapping tools
        "ui_component_map": ui_component_map,
        "ui_architecture_scan": ui_architecture_scan,
        "ui_dependency_graph": ui_dependency_graph,
        # Phase 4 screenshot tools
        "ui_screenshot": ui_screenshot,
        "ui_visual_diff": ui_visual_diff,
        "ui_capture_all_components": ui_capture_all_components,
        # Phase 4 workflow improvements
        "ui_workflow": ui_workflow
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


@app.get("/help")
async def get_help(format: str = "json"):
    """Self-documenting help endpoint with runtime validation."""
    
    # Hardcoded documentation (source of truth)
    help_data = {
        "overview": "Hephaestus UI DevTools MCP Server",
        "version": VERSION,
        "base_url": f"http://localhost:{MCP_PORT}",
        "endpoints": {
            "/health": "Check if DevTools are running",
            "/ready": "Check if browser is initialized", 
            "/help": "This help message (add ?format=text for readable version)",
            "/api/mcp/v2/execute": "Execute UI DevTools commands",
            "/api/mcp/v2/capabilities": "Get MCP capabilities",
            "/api/mcp/v2/tools": "List available tools"
        },
        "tools": {
            "ui_capture": {
                "description": "Capture UI structure and content (no screenshots by default)",
                "parameters": {
                    "required": [],
                    "optional": ["area", "selector", "include_screenshot"],
                    "types": {
                        "area": "string: 'hephaestus' (default), 'rhetor', 'navigation', etc.",
                        "selector": "string: CSS selector like '[data-component=\"budget\"]'",
                        "include_screenshot": "boolean: false (default)"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_capture","arguments":{"area":"rhetor"}}\'',
                "common_uses": ["Check current UI state", "Find elements", "Verify changes"],
                "note": "Use 'area':'hephaestus' to capture entire UI"
            },
            "ui_sandbox": {
                "description": "Test UI changes safely with preview mode",
                "parameters": {
                    "required": ["area", "changes"],
                    "optional": ["preview", "validate"],
                    "types": {
                        "area": "string: UI area (NOT 'component'!)",
                        "changes": "array: List of change operations",
                        "preview": "boolean: true (default) - test without applying",
                        "validate": "boolean: false (default) - validate changes"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_sandbox","arguments":{"area":"hephaestus","changes":[{"type":"text","selector":".nav-label","content":"New Text","action":"replace"}],"preview":true}}\'',
                "note": "⚠️ Use 'area' not 'component' - this is the #1 mistake!",
                "change_types": {
                    "text": "Replace/modify text content only",
                    "html": "Replace/modify HTML structure", 
                    "css": "Add CSS rules (use 'content' for full CSS or 'property'/'value' for single rule)"
                },
                "actions": ["replace", "append", "prepend", "after", "before"]
            },
            "ui_navigate": {
                "description": "Navigate to a specific component by clicking its nav item",
                "parameters": {
                    "required": ["component"],
                    "optional": ["wait_for_load", "timeout"],
                    "types": {
                        "component": "string: Component name (e.g., 'rhetor', 'prometheus')",
                        "wait_for_load": "boolean: true (default) - wait for component to load",
                        "timeout": "integer: 10000 (default) - max wait time in ms"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_navigate","arguments":{"component":"rhetor"}}\'',
                "note": "Essential for working with components - must navigate before capture/modify"
            },
            "ui_interact": {
                "description": "Interact with UI elements (click, type, focus)",
                "parameters": {
                    "required": ["area", "action", "selector"],
                    "optional": ["value"],
                    "types": {
                        "area": "string: UI area",
                        "action": "string: 'click', 'type', 'focus', 'hover'",
                        "selector": "string: CSS selector",
                        "value": "string: For 'type' action"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_interact","arguments":{"area":"rhetor","action":"click","selector":"button[data-tekton-chat-send]"}}\'',
            },
            "ui_analyze": {
                "description": "Check for frameworks and UI patterns",
                "parameters": {
                    "required": ["area"],
                    "optional": ["deep_scan"],
                    "types": {
                        "area": "string: UI area to analyze",
                        "deep_scan": "boolean: false (default)"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_analyze","arguments":{"area":"rhetor","deep_scan":false}}\''
            },
            "ui_validate": {
                "description": "Validate UI instrumentation and semantic tagging",
                "parameters": {
                    "required": [],
                    "optional": ["scope", "checks", "detailed"],
                    "types": {
                        "scope": "string: 'current', 'navigation', or 'all'",
                        "checks": "array: ['semantic-tags', 'navigation', 'data-attributes', 'component-structure']",
                        "detailed": "boolean: false (default) - include detailed findings"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_validate","arguments":{"scope":"current"}}\'',
                "note": "Essential for verifying instrumentation quality"
            },
            "ui_batch": {
                "description": "Execute multiple UI operations in batch with atomic support",
                "parameters": {
                    "required": ["area", "operations"],
                    "optional": ["atomic"],
                    "types": {
                        "area": "string: UI area (e.g., 'hephaestus')",
                        "operations": "array: List of operations to perform",
                        "atomic": "boolean: true (default) - all succeed or all fail"
                    }
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_batch","arguments":{"area":"hephaestus","operations":[{"action":"rename","from":"Budget","to":"Penia"}]}}\'',
                "actions": ["rename", "remove", "add_class", "remove_class", "style", "navigate", "click"]
            },
            "ui_list_areas": {
                "description": "List all available UI areas",
                "parameters": {
                    "required": [],
                    "optional": []
                },
                "example": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_list_areas","arguments":{}}\''
            }
        },
        "common_errors": {
            "parameter_mismatch": {
                "error": "ui_sandbox() got an unexpected keyword argument 'component'",
                "fix": "Use 'area' instead of 'component' for ui_sandbox"
            },
            "empty_captures": {
                "error": "element_count: 0",
                "fix": "Try broader selector or use 'area': 'hephaestus' for full UI"
            },
            "moving_elements": {
                "error": "Can't move elements between containers easily",
                "fix": "For structural moves, edit HTML directly"
            },
            "browser_not_ready": {
                "error": "Browser not initialized",
                "fix": "Wait a moment or check /ready endpoint"
            }
        },
        "gotchas": {
            "area_only": "ALL tools use 'area' parameter, NOT 'component'",
            "preview_default": "ui_sandbox defaults to preview=true, changes won't apply unless preview=false",
            "selector_escaping": "Quotes in selectors need escaping: '[data-component=\"rhetor\"]'",
            "css_format": "CSS changes can use either full rules or property/value pairs"
        },
        "quick_reference": {
            "capture_all": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_capture","arguments":{"area":"hephaestus"}}\'',
            "preview_change": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_sandbox","arguments":{"area":"hephaestus","changes":[{"type":"text","selector":".nav-label","content":"Test","action":"replace"}],"preview":true}}\'',
            "check_health": 'curl http://localhost:8088/health',
            "list_areas": 'curl -X POST http://localhost:8088/api/mcp/v2/execute -d \'{"tool_name":"ui_list_areas","arguments":{}}\''
        }
    }
    
    # Runtime validation (simple but effective)
    validation_results = {}
    
    # Map of actual tool functions
    tool_functions = {
        "ui_list_areas": ui_list_areas,
        "ui_recommend_approach": ui_recommend_approach,
        "ui_capture": ui_capture,
        "ui_navigate": ui_navigate,
        "ui_interact": ui_interact,
        "ui_sandbox": ui_sandbox,
        "ui_analyze": ui_analyze,
        "ui_validate": ui_validate,
        "ui_batch": ui_batch,
        "ui_help": ui_help,
        # Phase 2 semantic tools
        "ui_semantic_analysis": ui_semantic_analysis,
        "ui_semantic_scan": ui_semantic_scan,
        "ui_semantic_patterns": ui_semantic_patterns,
        # Phase 3 architecture mapping tools
        "ui_component_map": ui_component_map,
        "ui_architecture_scan": ui_architecture_scan,
        "ui_dependency_graph": ui_dependency_graph,
        # Phase 4 screenshot tools
        "ui_screenshot": ui_screenshot,
        "ui_visual_diff": ui_visual_diff,
        "ui_capture_all_components": ui_capture_all_components,
        # Phase 4 workflow improvements
        "ui_workflow": ui_workflow
    }
    
    # Check if documented tools exist
    for tool_name in help_data["tools"]:
        if tool_name in tool_functions:
            validation_results[tool_name] = "✓ Available"
        else:
            validation_results[tool_name] = "⚠️ Not found in runtime"
            help_data["tools"][tool_name]["warning"] = "Tool may not be available"
    
    help_data["runtime_validation"] = validation_results
    
    # Format response
    if format == "text":
        return PlainTextResponse(format_help_as_text(help_data))
    return JSONResponse(help_data)


def format_help_as_text(help_data):
    """Convert help data to readable text format."""
    lines = [
        f"# {help_data['overview']} v{help_data['version']}",
        f"Base URL: {help_data['base_url']}\n",
        "## Available Endpoints\n"
    ]
    
    for endpoint, desc in help_data['endpoints'].items():
        lines.append(f"  {endpoint:<30} - {desc}")
    
    lines.append("\n## Available Tools\n")
    
    for tool_name, tool_info in help_data['tools'].items():
        validation = help_data['runtime_validation'].get(tool_name, "?")
        lines.append(f"### {tool_name} {validation}")
        lines.append(f"{tool_info['description']}")
        
        if tool_info['parameters']['required']:
            lines.append(f"Required: {', '.join(tool_info['parameters']['required'])}")
        else:
            lines.append("Required: (none)")
            
        if tool_info['parameters']['optional']:
            lines.append(f"Optional: {', '.join(tool_info['parameters']['optional'])}")
            
        if 'note' in tool_info:
            lines.append(f"\n{tool_info['note']}")
            
        lines.append(f"\nExample:\n{tool_info['example']}\n")
    
    lines.append("\n## Common Errors\n")
    for error_key, error_info in help_data['common_errors'].items():
        lines.append(f"❌ {error_info['error']}")
        lines.append(f"   ✅ Fix: {error_info['fix']}\n")
    
    lines.append("\n## Gotchas to Remember\n")
    for gotcha_key, gotcha_text in help_data['gotchas'].items():
        lines.append(f"⚠️  {gotcha_text}")
    
    lines.append("\n## Quick Reference (Copy & Paste)\n")
    for ref_key, ref_cmd in help_data['quick_reference'].items():
        lines.append(f"{ref_key}:")
        lines.append(f"  {ref_cmd}\n")
    
    return "\n".join(lines)


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