"""
Component template utilities for Tekton.

Provides standardized templates for creating new components and
fixing common issues like missing main functions.
"""
import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def create_main_function_template(
    component_name: str,
    default_port: int,
    app_module_path: Optional[str] = None
) -> str:
    """
    Generate standard main function template.
    
    This fixes the common issue of missing main() functions in components
    like Athena and Sophia.
    
    Args:
        component_name: Name of the component
        default_port: Default port number
        app_module_path: Optional custom path to app object (default: component.api.app:app)
        
    Returns:
        Main function template as string
    """
    if app_module_path:
        # Custom app path provided
        module, app_var = app_module_path.rsplit(':', 1)
        import_line = f"from {module} import {app_var} as app"
    else:
        # Default pattern
        import_line = f"from {component_name}.api.app import app"
    
    template = f'''
if __name__ == "__main__":
    import argparse
    import uvicorn
    import os
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Import the FastAPI app
    {import_line}
    
    parser = argparse.ArgumentParser(description="{component_name.title()} API Server")
    parser.add_argument("--port", type=int,
                       default=int(os.environ.get("{component_name.upper()}_PORT", {default_port})),
                       help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                       help="Host to bind the server to")
    parser.add_argument("--reload", action="store_true",
                       help="Enable auto-reload for development")
    args = parser.parse_args()
    
    logger.info(f"Starting {component_name.title()} server on {{args.host}}:{{args.port}}")
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
'''
    return template


def create_fastapi_app_template(
    component_name: str,
    port: int,
    description: str = None
) -> str:
    """
    Create FastAPI app template with proper lifespan management.
    
    Uses the new lifespan pattern instead of deprecated @app.on_event.
    
    Args:
        component_name: Name of the component
        port: Port number
        description: Optional API description
        
    Returns:
        FastAPI app template as string
    """
    if description is None:
        description = f"{component_name.title()} API Server"
    
    template = f'''"""
{component_name.title()} API Server

{description}
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.utils.shutdown import component_lifespan
from shared.utils.startup import component_startup
from shared.utils.logging_setup import setup_component_logger

# Setup logging
logger = setup_component_logger("{component_name}")

# Define startup and cleanup tasks
async def startup_tasks():
    """Initialize {component_name} services."""
    logger.info("Initializing {component_name} services...")
    # Add initialization code here
    
async def cleanup_tasks():
    """Cleanup {component_name} resources."""
    logger.info("Cleaning up {component_name} resources...")
    # Add cleanup code here

# Create FastAPI app with lifespan management
app = FastAPI(
    title="{component_name.title()} API",
    description="{description}",
    version="0.1.0",
    lifespan=component_lifespan(
        "{component_name}",
        startup_tasks,
        [cleanup_tasks],
        port={port}
    )
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .endpoints import router
app.include_router(router)
'''
    return template


def create_health_endpoint_template(component_name: str) -> str:
    """
    Create health check endpoint template.
    
    Args:
        component_name: Name of the component
        
    Returns:
        Health endpoint template as string
    """
    template = f'''"""
Health check endpoints for {component_name}.
"""
from datetime import datetime
from fastapi import APIRouter

from shared.utils.health_check import create_health_response
from shared.utils.env_config import get_component_config

router = APIRouter(tags=["health"])

# Get component configuration
config = get_component_config()

@router.get("/health")
async def health_check():
    """Get component health status."""
    return create_health_response(
        "{component_name}",
        config.get_port("{component_name}") or 8000
    )

@router.get("/api/health")
async def api_health_check():
    """Alternative health check endpoint."""
    return await health_check()
'''
    return template


def create_requirements_template() -> str:
    """
    Create requirements.txt template.
    
    Returns:
        Requirements template as string
    """
    template = '''# Component-specific requirements

# Include shared base requirements
-r ../shared/requirements/base.txt

# FastAPI and server
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0

# Component-specific dependencies
# Add your component-specific packages here
'''
    return template


def create_run_script_template(component_name: str, port: int) -> str:
    """
    Create run script template.
    
    Args:
        component_name: Name of the component
        port: Port number
        
    Returns:
        Bash run script template as string
    """
    comp_upper = component_name.upper()
    
    # Use format() for clean, readable code
    template = """#!/bin/bash

# Run script for {title}

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

# Set default port
{upper}_PORT=${{PORT:-${{{upper}_PORT:-{port}}}}}

# Check if port is already in use
if nc -z localhost ${{{upper}_PORT}} 2>/dev/null; then
    echo "[{name}] Port ${{{upper}_PORT}} is already in use"
    exit 1
fi

# Setup Python path
export PYTHONPATH="${{SCRIPT_DIR}}:${{PYTHONPATH}}"

# Set Tekton root if not already set
if [ -z "${{TEKTON_ROOT}}" ]; then
    export TEKTON_ROOT="$(cd "${{SCRIPT_DIR}}/.." && pwd)"
fi

echo "[{name}] Starting on port ${{{upper}_PORT}}..."

# Run with uvicorn
cd "${{SCRIPT_DIR}}" && uvicorn {name}.api.app:app \\
    --host 0.0.0.0 \\
    --port ${{{upper}_PORT}} \\
    --reload
""".format(
        name=component_name,
        title=component_name.title(),
        upper=comp_upper,
        port=port
    )
    
    return template


def create_component_scaffolding(
    component_name: str,
    port: int,
    include_mcp: bool = False,
    include_database: bool = False,
    include_ui: bool = False
) -> Dict[str, str]:
    """
    Create complete component scaffolding.
    
    Args:
        component_name: Name of the component
        port: Port number
        include_mcp: Whether to include MCP server setup
        include_database: Whether to include database setup
        include_ui: Whether to include UI component
        
    Returns:
        Dictionary mapping file paths to their content
    """
    scaffolding = {}
    
    # Core API files
    scaffolding["api/app.py"] = create_fastapi_app_template(component_name, port)
    scaffolding["api/__init__.py"] = f'"""API package for {component_name}."""\nfrom .app import app\n\n__all__ = ["app"]'
    scaffolding["api/endpoints.py"] = f'''"""
API endpoints for {component_name}.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {{"message": "Welcome to {component_name.title()} API"}}

@router.get("/status")
async def status() -> Dict[str, Any]:
    """Get component status."""
    return {{
        "component": "{component_name}",
        "status": "operational",
        "version": "0.1.0"
    }}
'''
    
    scaffolding["api/models.py"] = f'''"""
Pydantic models for {component_name}.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
'''
    
    # Core logic files
    scaffolding["core/__init__.py"] = f'"""Core logic for {component_name}."""'
    scaffolding["core/engine.py"] = f'''"""
Main engine for {component_name}.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class {component_name.title()}Engine:
    """{component_name.title()} core engine."""
    
    def __init__(self):
        """Initialize the engine."""
        self.initialized = False
        
    async def initialize(self):
        """Initialize the engine."""
        logger.info("Initializing {component_name} engine...")
        # Add initialization logic here
        self.initialized = True
        
    async def shutdown(self):
        """Shutdown the engine."""
        logger.info("Shutting down {component_name} engine...")
        # Add cleanup logic here
        self.initialized = False
'''
    
    # Package files
    scaffolding["__init__.py"] = f'"""{component_name.title()} - Part of the Tekton system."""\n__version__ = "0.1.0"'
    scaffolding["requirements.txt"] = create_requirements_template()
    scaffolding[f"run_{component_name}.sh"] = create_run_script_template(component_name, port)
    
    # Optional MCP files
    if include_mcp:
        scaffolding["api/mcp_server.py"] = f'''"""
FastMCP server for {component_name}.
"""
from shared.utils.mcp_helpers import create_mcp_server, register_mcp_tools
from .mcp_tools import get_mcp_tools

# Create MCP server
mcp_server = create_mcp_server("{component_name}", "0.1.0")

# Register tools
tools = get_mcp_tools()
register_mcp_tools(mcp_server, tools)
'''
    
    # Optional database files
    if include_database:
        scaffolding["models/database.py"] = f'''"""
Database models for {component_name}.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {component_name.title()}Model(Base):
    """Example database model."""
    __tablename__ = "{component_name}_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
'''
        scaffolding["alembic.ini"] = "[alembic]\n# Alembic configuration file"
    
    # Optional UI files
    if include_ui:
        scaffolding[f"ui/{component_name}-component.html"] = f'''<!DOCTYPE html>
<html>
<head>
    <title>{component_name.title()} Component</title>
    <link rel="stylesheet" href="../../../Hephaestus/ui/styles/components.css">
</head>
<body>
    <div class="{component_name}-container">
        <h2>{component_name.title()}</h2>
        <div id="{component_name}-content">
            <!-- Component content here -->
        </div>
    </div>
    <script src="./{component_name}-component.js"></script>
</body>
</html>
'''
    
    return scaffolding


def append_main_to_file(file_path: str, component_name: str, port: int) -> bool:
    """
    Append main function to existing Python file if it doesn't have one.
    
    Args:
        file_path: Path to the Python file
        component_name: Name of the component
        port: Port number
        
    Returns:
        True if main was added, False if already exists
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if file already has main
        if 'if __name__ == "__main__":' in content:
            logger.info(f"File {file_path} already has a main block")
            return False
        
        # Generate main function
        main_template = create_main_function_template(component_name, port)
        
        # Append to file
        with open(file_path, 'a') as f:
            f.write('\n\n')
            f.write(main_template)
        
        logger.info(f"Added main function to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to append main to {file_path}: {e}")
        raise