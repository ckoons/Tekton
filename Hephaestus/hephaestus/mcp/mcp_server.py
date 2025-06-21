"""
Hephaestus UI DevTools MCP Server v2.0
Clean implementation that imports from ui_dev_tools
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
hephaestus_root = os.path.dirname(os.path.dirname(current_dir))
tekton_root = os.path.dirname(hephaestus_root)
sys.path.insert(0, hephaestus_root)
sys.path.insert(0, tekton_root)

# Import Hermes registration
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging

# Initialize logger
logger = setup_component_logging("hephaestus_mcp")

# Import UI DevTools
sys.path.insert(0, os.path.join(hephaestus_root, "ui_dev_tools"))
from ui_dev_tools.tools.code_reader import CodeReader
from ui_dev_tools.tools.browser_verifier import BrowserVerifier
from ui_dev_tools.tools.comparator import Comparator
from ui_dev_tools.tools.navigator import Navigator
from ui_dev_tools.tools.safe_tester import SafeTester

# Import configuration
from shared.utils.global_config import GlobalConfig

# MCP Server configuration
global_config = GlobalConfig.get_instance()
MCP_PORT = global_config.config.hephaestus.mcp_port
COMPONENT_NAME = "hephaestus_ui_devtools"
VERSION = "2.0.0"

# Global state
hermes_registration: Optional[HermesRegistration] = None
heartbeat_task: Optional[asyncio.Task] = None

# Tool instances (created on startup)
code_reader: Optional[CodeReader] = None
browser_verifier: Optional[BrowserVerifier] = None
comparator: Optional[Comparator] = None
navigator: Optional[Navigator] = None
safe_tester: Optional[SafeTester] = None


class ToolRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolResponse(BaseModel):
    """Response model for tool execution"""
    tool: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global hermes_registration, heartbeat_task
    global code_reader, browser_verifier, comparator, navigator, safe_tester
    
    # Startup
    logger.info(f"Starting Hephaestus UI DevTools MCP Server v{VERSION}")
    
    # Initialize tools
    code_reader = CodeReader()
    browser_verifier = BrowserVerifier()
    comparator = Comparator()
    navigator = Navigator()
    safe_tester = SafeTester()
    logger.info("All tools initialized")
    
    # Register with Hermes
    try:
        hermes_registration = HermesRegistration(
            component_name=COMPONENT_NAME,
            host="localhost",
            port=MCP_PORT,
            component_type="tool_server",
            capabilities=["ui_devtools", "code_analysis", "browser_verification"],
            metadata={
                "version": VERSION,
                "tools": ["code_reader", "browser_verifier", "comparator", "navigator", "safe_tester"]
            }
        )
        
        if await hermes_registration.register():
            logger.info("Successfully registered with Hermes")
            heartbeat_task = asyncio.create_task(
                heartbeat_loop(hermes_registration, interval=30)
            )
        else:
            logger.warning("Failed to register with Hermes, continuing anyway")
    except Exception as e:
        logger.warning(f"Hermes registration error: {e}, continuing anyway")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Hephaestus UI DevTools MCP Server")
    
    # Cancel heartbeat
    if heartbeat_task and not heartbeat_task.done():
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
    
    # Deregister from Hermes
    if hermes_registration:
        await hermes_registration.deregister()
    
    # Cleanup browser resources
    if browser_verifier:
        await browser_verifier.cleanup()
    if comparator:
        await comparator.browser_verifier.cleanup()
    if navigator:
        await navigator.cleanup()
    if safe_tester:
        await safe_tester.cleanup()


# Create FastAPI app
app = FastAPI(
    title="Hephaestus UI DevTools MCP Server",
    version=VERSION,
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Hephaestus UI DevTools MCP Server",
        "version": VERSION,
        "status": "running",
        "tools": [
            "code_reader",
            "browser_verifier", 
            "comparator",
            "navigator",
            "safe_tester"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "component": COMPONENT_NAME,
        "version": VERSION
    }


@app.post("/api/mcp/v2/execute")
async def execute_tool(request: ToolRequest):
    """Execute a UI DevTools tool"""
    try:
        tool_name = request.tool_name
        args = request.arguments
        
        logger.info(f"Executing tool: {tool_name} with args: {args}")
        
        # Route to appropriate tool
        if tool_name.startswith("code_"):
            result = await execute_code_reader(tool_name, args)
        elif tool_name.startswith("browser_"):
            result = await execute_browser_verifier(tool_name, args)
        elif tool_name.startswith("compare_"):
            result = await execute_comparator(tool_name, args)
        elif tool_name.startswith("navigate_"):
            result = await execute_navigator(tool_name, args)
        elif tool_name.startswith("test_"):
            result = await execute_safe_tester(tool_name, args)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown tool: {tool_name}"
            )
        
        # Convert result to response
        return JSONResponse(content=result.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "tool": request.tool_name,
                "status": "error",
                "error": str(e)
            }
        )


# Tool execution functions
async def execute_code_reader(tool_name: str, args: Dict[str, Any]):
    """Execute CodeReader tools"""
    component = args.get("component_name", args.get("component"))
    
    if tool_name == "code_read_component":
        return code_reader.read_component(component)
    elif tool_name == "code_list_semantic_tags":
        return code_reader.list_semantic_tags(component)
    elif tool_name == "code_get_structure":
        return code_reader.get_component_structure(component)
    elif tool_name == "code_list_components":
        return code_reader.list_components()
    else:
        raise HTTPException(400, f"Unknown CodeReader tool: {tool_name}")


async def execute_browser_verifier(tool_name: str, args: Dict[str, Any]):
    """Execute BrowserVerifier tools"""
    component = args.get("component_name", args.get("component"))
    
    if tool_name == "browser_verify_loaded":
        return await browser_verifier.verify_component_loaded(component)
    elif tool_name == "browser_get_semantic_tags":
        return await browser_verifier.get_dom_semantic_tags(component)
    elif tool_name == "browser_capture_state":
        return await browser_verifier.capture_dom_state(component)
    else:
        raise HTTPException(400, f"Unknown BrowserVerifier tool: {tool_name}")


async def execute_comparator(tool_name: str, args: Dict[str, Any]):
    """Execute Comparator tools"""
    component = args.get("component_name", args.get("component"))
    
    if tool_name == "compare_component":
        return await comparator.compare_component(component)
    elif tool_name == "compare_diagnose_missing":
        return await comparator.diagnose_missing_tags(component)
    elif tool_name == "compare_suggest_fixes":
        return await comparator.suggest_fixes(component)
    else:
        raise HTTPException(400, f"Unknown Comparator tool: {tool_name}")


async def execute_navigator(tool_name: str, args: Dict[str, Any]):
    """Execute Navigator tools"""
    component = args.get("component_name", args.get("component"))
    
    if tool_name == "navigate_to_component":
        wait_for_ready = args.get("wait_for_ready", True)
        return await navigator.navigate_to_component(component, wait_for_ready)
    elif tool_name == "navigate_get_current":
        return await navigator.get_current_component()
    elif tool_name == "navigate_list_components":
        return await navigator.list_navigable_components()
    else:
        raise HTTPException(400, f"Unknown Navigator tool: {tool_name}")


async def execute_safe_tester(tool_name: str, args: Dict[str, Any]):
    """Execute SafeTester tools"""
    component = args.get("component_name", args.get("component"))
    changes = args.get("changes", [])
    
    if tool_name == "test_preview_changes":
        return await safe_tester.preview_change(component, changes)
    elif tool_name == "test_in_sandbox":
        return await safe_tester.test_in_sandbox(component, changes)
    elif tool_name == "test_validate_changes":
        return await safe_tester.validate_change(component, changes)
    elif tool_name == "test_rollback":
        return await safe_tester.rollback_changes(component)
    else:
        raise HTTPException(400, f"Unknown SafeTester tool: {tool_name}")


@app.get("/api/mcp/v2/tools")
async def list_tools():
    """List all available tools"""
    tools = [
        # CodeReader tools
        {
            "name": "code_read_component",
            "description": "Read component source files (the truth)",
            "category": "code",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "code_list_semantic_tags",
            "description": "Extract all data-tekton-* attributes from source",
            "category": "code",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "code_get_structure",
            "description": "Get component HTML structure",
            "category": "code",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "code_list_components",
            "description": "List all available components",
            "category": "code",
            "parameters": {}
        },
        
        # BrowserVerifier tools
        {
            "name": "browser_verify_loaded",
            "description": "Check if component is loaded in DOM",
            "category": "browser",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "browser_get_semantic_tags",
            "description": "Extract semantic tags from DOM (the reality)",
            "category": "browser",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "browser_capture_state",
            "description": "Capture current DOM structure",
            "category": "browser",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        
        # Comparator tools
        {
            "name": "compare_component",
            "description": "Compare source code vs browser DOM",
            "category": "analysis",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "compare_diagnose_missing",
            "description": "Diagnose why tags might be missing",
            "category": "analysis",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        {
            "name": "compare_suggest_fixes",
            "description": "Suggest fixes based on comparison",
            "category": "analysis",
            "parameters": {"component_name": {"type": "string", "required": True}}
        },
        
        # Navigator tools
        {
            "name": "navigate_to_component",
            "description": "Navigate to a component reliably",
            "category": "navigation",
            "parameters": {
                "component_name": {"type": "string", "required": True},
                "wait_for_ready": {"type": "boolean", "default": True}
            }
        },
        {
            "name": "navigate_get_current",
            "description": "Get currently loaded component",
            "category": "navigation",
            "parameters": {}
        },
        {
            "name": "navigate_list_components",
            "description": "List all navigable components",
            "category": "navigation",
            "parameters": {}
        },
        
        # SafeTester tools
        {
            "name": "test_preview_changes",
            "description": "Preview changes without applying them",
            "category": "testing",
            "parameters": {
                "component_name": {"type": "string", "required": True},
                "changes": {"type": "array", "required": True}
            }
        },
        {
            "name": "test_in_sandbox",
            "description": "Test changes in isolated sandbox",
            "category": "testing",
            "parameters": {
                "component_name": {"type": "string", "required": True},
                "changes": {"type": "array", "required": True}
            }
        },
        {
            "name": "test_validate_changes",
            "description": "Validate if changes are safe",
            "category": "testing",
            "parameters": {
                "component_name": {"type": "string", "required": True},
                "changes": {"type": "array", "required": True}
            }
        },
        {
            "name": "test_rollback",
            "description": "Rollback to previous state",
            "category": "testing",
            "parameters": {"component_name": {"type": "string", "required": True}}
        }
    ]
    
    return {"tools": tools, "count": len(tools)}


if __name__ == "__main__":
    logger.info(f"Starting UI DevTools MCP Server on port {MCP_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=MCP_PORT)