"""
FastMCP endpoints for Telos API.

This module provides FastMCP endpoints for requirements management, tracing,
validation, and Prometheus integration using the parallel implementation approach.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tekton.mcp.fastmcp.utils.endpoints import create_mcp_router, add_standard_mcp_endpoints
from tekton.mcp.fastmcp.registry import FastMCPRegistry
from tekton.mcp.fastmcp.client import FastMCPClient

from ..core.mcp.tools import (
    requirements_management_tools,
    requirement_tracing_tools,
    requirement_validation_tools,
    prometheus_integration_tools
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telos.fastmcp")

# Global registry for FastMCP tools
fastmcp_registry = FastMCPRegistry()

# Global instances for dependency injection
requirements_manager = None
prometheus_connector = None


class FastMCPAdapter:
    """Adapter for integrating FastMCP with Telos services."""
    
    def __init__(self, requirements_manager_instance=None, prometheus_connector_instance=None):
        """Initialize the FastMCP adapter with dependencies."""
        self.requirements_manager = requirements_manager_instance
        self.prometheus_connector = prometheus_connector_instance
        
    async def get_requirements_manager(self):
        """Get the requirements manager instance for dependency injection."""
        return self.requirements_manager
        
    async def get_prometheus_connector(self):
        """Get the Prometheus connector for dependency injection."""
        return self.prometheus_connector


# Global adapter instance
fastmcp_adapter = FastMCPAdapter()


def get_requirements_manager_dependency():
    """Dependency for injecting RequirementsManager into FastMCP tools."""
    async def _get_requirements_manager():
        return await fastmcp_adapter.get_requirements_manager()
    return _get_requirements_manager


def get_prometheus_connector_dependency():
    """Dependency for injecting PrometheusConnector into FastMCP tools."""
    async def _get_prometheus_connector():
        return await fastmcp_adapter.get_prometheus_connector()
    return _get_prometheus_connector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for FastMCP initialization."""
    logger.info("Starting Telos FastMCP server...")
    
    # Initialize requirements manager and prometheus connector
    global requirements_manager, prometheus_connector
    
    try:
        # Import and initialize core components
        from ..core.requirements_manager import RequirementsManager
        from ..prometheus_connector import TelosPrometheusConnector
        
        # Load environment variables for configuration
        storage_dir = os.environ.get("TELOS_STORAGE_DIR", os.path.join(os.getcwd(), "data", "requirements"))
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize requirements manager
        requirements_manager = RequirementsManager(storage_dir=storage_dir)
        requirements_manager.load_projects()
        
        # Initialize Prometheus connector
        prometheus_connector = TelosPrometheusConnector(requirements_manager)
        try:
            await prometheus_connector.initialize()
        except Exception as e:
            logger.warning(f"Failed to initialize Prometheus connector: {e}")
        
        # Update adapter with initialized instances
        fastmcp_adapter.requirements_manager = requirements_manager
        fastmcp_adapter.prometheus_connector = prometheus_connector
        
        # Register all tools with dependency injection
        all_tools = (requirements_management_tools + requirement_tracing_tools + 
                    requirement_validation_tools + prometheus_integration_tools)
        
        for tool in all_tools:
            # Create dependency injection for requirements_manager
            if hasattr(tool, '__annotations__') and 'requirements_manager' in tool.__annotations__:
                fastmcp_registry.register_dependency('requirements_manager', get_requirements_manager_dependency())
            
            # Create dependency injection for prometheus_connector
            if hasattr(tool, '__annotations__') and 'prometheus_connector' in tool.__annotations__:
                fastmcp_registry.register_dependency('prometheus_connector', get_prometheus_connector_dependency())
        
        # Register tools
        fastmcp_registry.register_tools(all_tools)
        
        logger.info(f"Registered {len(all_tools)} FastMCP tools for Telos")
        logger.info("Telos FastMCP server initialization completed")
        
    except Exception as e:
        logger.error(f"Failed to initialize Telos FastMCP server: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Telos FastMCP server...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Telos FastMCP API",
    description="FastMCP API for Telos Requirements Management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP router
mcp_router = create_mcp_router(fastmcp_registry)

# Add standard MCP endpoints
add_standard_mcp_endpoints(mcp_router, fastmcp_registry)

# Add custom health endpoint
@mcp_router.get("/health")
async def fastmcp_health():
    """Health check endpoint for FastMCP."""
    return {
        "status": "healthy",
        "service": "telos-fastmcp",
        "version": "1.0.0",
        "tools_registered": len(fastmcp_registry.tools),
        "capabilities_registered": len(fastmcp_registry.capabilities),
        "requirements_manager_available": requirements_manager is not None,
        "prometheus_connector_available": prometheus_connector is not None
    }

# Add workflow execution endpoint for complex operations
@mcp_router.post("/workflow")
async def execute_workflow(
    workflow_name: str,
    parameters: Dict[str, Any]
):
    """Execute predefined workflows for complex Telos operations."""
    try:
        if workflow_name == "create_project_with_requirements":
            # Create project and add multiple requirements
            project_data = parameters.get("project", {})
            requirements_data = parameters.get("requirements", [])
            
            # Create project
            from ..core.mcp.tools import create_project
            project_result = await create_project(
                name=project_data.get("name"),
                description=project_data.get("description"),
                metadata=project_data.get("metadata"),
                requirements_manager=requirements_manager
            )
            
            if "error" in project_result:
                return project_result
            
            project_id = project_result["project_id"]
            created_requirements = []
            
            # Add requirements
            from ..core.mcp.tools import create_requirement
            for req_data in requirements_data:
                req_result = await create_requirement(
                    project_id=project_id,
                    title=req_data.get("title"),
                    description=req_data.get("description"),
                    requirement_type=req_data.get("requirement_type", "functional"),
                    priority=req_data.get("priority", "medium"),
                    status=req_data.get("status", "new"),
                    tags=req_data.get("tags"),
                    parent_id=req_data.get("parent_id"),
                    dependencies=req_data.get("dependencies"),
                    metadata=req_data.get("metadata"),
                    requirements_manager=requirements_manager
                )
                
                if "error" not in req_result:
                    created_requirements.append(req_result)
            
            return {
                "workflow": "create_project_with_requirements",
                "project": project_result,
                "requirements": created_requirements,
                "status": "completed"
            }
        
        elif workflow_name == "validate_and_analyze_project":
            # Validate project and analyze for planning
            project_id = parameters.get("project_id")
            
            if not project_id:
                return {"error": "project_id required for this workflow"}
            
            results = {}
            
            # Validate project
            from ..core.mcp.tools import validate_project
            validation_result = await validate_project(
                project_id=project_id,
                check_completeness=parameters.get("check_completeness", True),
                check_verifiability=parameters.get("check_verifiability", True),
                check_clarity=parameters.get("check_clarity", True),
                requirements_manager=requirements_manager
            )
            results["validation"] = validation_result
            
            # Analyze for planning if Prometheus is available
            if prometheus_connector:
                from ..core.mcp.tools import analyze_requirements
                analysis_result = await analyze_requirements(
                    project_id=project_id,
                    requirements_manager=requirements_manager,
                    prometheus_connector=prometheus_connector
                )
                results["analysis"] = analysis_result
            
            return {
                "workflow": "validate_and_analyze_project",
                "results": results,
                "status": "completed"
            }
        
        elif workflow_name == "bulk_requirement_update":
            # Update multiple requirements at once
            project_id = parameters.get("project_id")
            updates = parameters.get("updates", [])  # List of {requirement_id, updates}
            
            if not project_id:
                return {"error": "project_id required for this workflow"}
            
            results = []
            from ..core.mcp.tools import update_requirement
            
            for update_data in updates:
                requirement_id = update_data.get("requirement_id")
                update_fields = update_data.get("updates", {})
                
                if not requirement_id:
                    continue
                
                result = await update_requirement(
                    project_id=project_id,
                    requirement_id=requirement_id,
                    requirements_manager=requirements_manager,
                    **update_fields
                )
                results.append(result)
            
            return {
                "workflow": "bulk_requirement_update",
                "results": results,
                "status": "completed"
            }
        
        elif workflow_name == "trace_analysis":
            # Analyze requirement traces and dependencies
            project_id = parameters.get("project_id")
            
            if not project_id:
                return {"error": "project_id required for this workflow"}
            
            # Get all traces
            from ..core.mcp.tools import list_traces
            traces_result = await list_traces(
                project_id=project_id,
                requirements_manager=requirements_manager
            )
            
            if "error" in traces_result:
                return traces_result
            
            traces = traces_result.get("traces", [])
            
            # Analyze trace patterns
            trace_analysis = {
                "total_traces": len(traces),
                "trace_types": {},
                "most_connected_requirements": {},
                "orphaned_requirements": []
            }
            
            # Count trace types
            for trace in traces:
                trace_type = trace.get("trace_type")
                trace_analysis["trace_types"][trace_type] = trace_analysis["trace_types"].get(trace_type, 0) + 1
            
            # TODO: Add more sophisticated trace analysis
            
            return {
                "workflow": "trace_analysis",
                "analysis": trace_analysis,
                "traces": traces,
                "status": "completed"
            }
        
        else:
            return {"error": f"Unknown workflow: {workflow_name}"}
    
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_name}: {e}")
        return {"error": f"Failed to execute workflow: {str(e)}"}

# Include MCP router
app.include_router(mcp_router, prefix="/api/mcp/v2")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing FastMCP service information."""
    return {
        "service": "telos-fastmcp",
        "version": "1.0.0",
        "description": "FastMCP API for Telos Requirements Management",
        "tools_registered": len(fastmcp_registry.tools),
        "capabilities_registered": len(fastmcp_registry.capabilities),
        "endpoints": ["/api/mcp/v2/capabilities", "/api/mcp/v2/tools", "/api/mcp/v2/process", "/api/mcp/v2/health"]
    }

# Health endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "telos-fastmcp",
        "version": "1.0.0",
        "requirements_manager_available": requirements_manager is not None,
        "prometheus_connector_available": prometheus_connector is not None
    }


if __name__ == "__main__":
    import uvicorn
    from tekton.utils.port_config import get_telos_port
    
    port = get_telos_port() + 1  # Use a different port for FastMCP server
    logger.info(f"Starting Telos FastMCP server on port {port}")
    
    uvicorn.run(
        "telos.api.fastmcp_endpoints:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )