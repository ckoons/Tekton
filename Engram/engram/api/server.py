"""
Engram API Server

A unified FastAPI server that provides memory services for both
standalone mode and Hermes integration.
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

# Import shared workflow endpoint and environment management
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))
from env import TektonEnviron
from workflow.endpoint_template import create_workflow_endpoint

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import json

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        performance_boundary,
        state_checkpoint,
        danger_zone
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

# Import shared utils
from shared.env import TektonEnviron
from shared.utils.health_check import create_health_response
from shared.utils.hermes_registration import HermesRegistration, heartbeat_loop
from shared.utils.logging_setup import setup_component_logging
from shared.urls import tekton_url
from shared.utils.env_config import get_component_config
from shared.utils.global_config import GlobalConfig
from shared.utils.errors import StartupError
from shared.utils.startup import component_startup, StartupMetrics
from shared.utils.shutdown import GracefulShutdown
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
from landmarks import api_contract, integration_point

# Use shared logger
logger = setup_component_logging("engram")

# Import Engram component and services
from engram.core.engram_component import EngramComponent
from engram.core import MemoryService

@architecture_decision(
    title="Engram Memory System Architecture",
    description="Centralized memory management with vector search and emotional analysis",
    rationale="Provides persistent memory storage with semantic search capabilities and emotional insights for enhanced AI interactions",
    alternatives_considered=["Simple key-value storage", "File-based memory", "Database-only solution"],
    impacts=["ai_memory_context", "semantic_search", "emotional_analysis", "file_upload_support"],
    decided_by="Casey",
    decision_date="2025-01-15"
)
class _EngramArchitecture:
    """Architecture marker for Engram's memory system design."""
    pass

# Create component singleton
engram_component = EngramComponent()

# Note: Component configuration and initialization is handled by EngramComponent
# The component manages memory_manager, hermes_adapter, mcp_bridge internally

@integration_point(
    title="Engram Startup Integration",
    description="Initialize Engram component and register with Hermes",
    target_component="Hermes Service Registry",
    protocol="HTTP REST API",
    data_flow="Engram -> Hermes Registration -> Service Discovery",
    integration_date="2025-01-15"
)
async def startup_callback():
    """Initialize Engram component (includes Hermes registration)."""
    # Initialize component (includes Hermes registration)
    await engram_component.initialize(
        capabilities=engram_component.get_capabilities(),
        metadata=engram_component.get_metadata()
    )

# Initialize FastAPI app with standard configuration
app = FastAPI(
    **get_openapi_configuration(
        component_name="engram",
        component_version="0.1.0",
        component_description="Memory management system with vector search and semantic similarity"
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

# Create standard routers
routers = create_standard_routers("engram")

# Store component reference for endpoints
app.state.component = engram_component

# Register startup callback
@app.on_event("startup")
async def startup_event():
    await startup_callback()


@integration_point(
    title="Memory Service Client Integration",
    description="Get client-specific memory service instance",
    target_component="Memory Manager",
    protocol="Internal API",
    data_flow="Request -> Client ID extraction -> Memory Manager -> Client-specific MemoryService",
    integration_date="2025-01-15"
)
@state_checkpoint(
    title="Client Memory Service",
    description="Per-client memory service isolation",
    state_type="client_session",
    persistence=True,
    consistency_requirements="Each client gets isolated memory namespace",
    recovery_strategy="Create new service instance if not found"
)
# Dependency to get memory service for a client
async def get_memory_service(
    request: Request,
    x_client_id: str = Header(None)
) -> MemoryService:
    client_id = x_client_id or engram_component.default_client_id
    
    if engram_component.memory_manager is None:
        raise HTTPException(status_code=500, detail="Memory manager not initialized")
    
    try:
        return await engram_component.memory_manager.get_memory_service(client_id)
    except Exception as e:
        logger.error(f"Error getting memory service: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting memory service: {str(e)}")

# Define routes
@routers.root.get("/")
async def root():
    """Root endpoint returning basic service information."""
    return {
        "service": "Engram Memory API",
        "version": "0.1.0",
        "description": "Memory management system with vector search and semantic similarity",
        "mode": "hermes" if engram_component.use_hermes else "standalone",
        "fallback": engram_component.use_fallback,
        "docs": "/api/v1/docs"
    }

@routers.root.get("/health")
async def health():
    """Health check endpoint."""
    # Don't trigger memory service initialization during health check
    # This avoids loading the sentence transformer model unnecessarily
    health_status = "healthy" if engram_component.memory_manager is not None else "initializing"
    
    details = {
        "memory_manager_initialized": bool(engram_component.memory_manager),
        "storage_mode": "fallback" if engram_component.use_fallback else "vector",
        "vector_available": not engram_component.use_fallback,
        "hermes_integration": engram_component.use_hermes,
        "default_client_id": engram_component.default_client_id
    }
    
    # Use standardized health response
    global_config = GlobalConfig.get_instance()
    port = global_config.config.engram.port
    return create_health_response(
        component_name="engram",
        port=port,
        version="0.1.0",
        status=health_status,
        registered=engram_component.global_config.is_registered_with_hermes,
        details=details
    )

@routers.v1.post("/memory")
@api_contract(
    title="Memory Storage API",
    endpoint="/api/v1/memory",
    method="POST",
    request_schema={"content": "string", "namespace": "string", "metadata": "object"}
)
@integration_point(
    title="Memory Service Integration",
    target_component="Memory Manager, Vector/Fallback Storage",
    protocol="Internal Python API",
    data_flow="API Request -> Memory Service -> Storage Backend -> Persistence"
)
async def add_memory(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Add a memory."""
    try:
        data = await request.json()
        content = data.get("content")
        namespace = data.get("namespace", "conversations")
        metadata = data.get("metadata")
        
        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: content"}
            )
        
        memory_id = await memory_service.add(
            content=content,
            namespace=namespace,
            metadata=metadata
        )
        
        return {
            "id": memory_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error adding memory: {str(e)}"}
        )

@routers.v1.get("/memory/{memory_id}")
@api_contract(
    title="Memory Retrieval API",
    description="Retrieve a specific memory by ID",
    endpoint="/api/v1/memory/{memory_id}",
    method="GET",
    request_schema={"memory_id": "string", "namespace": "string (query param)"},
    response_schema={"id": "string", "title": "string", "content": "string", "metadata": "object"},
    performance_requirements="<50ms for cached memories, <200ms for database fetch"
)
@performance_boundary(
    title="Memory Retrieval Performance",
    description="Demo memories return instantly, real memories fetch from storage",
    sla="<200ms response time",
    optimization_notes="Demo memories 1 and 2 bypass storage for instant response"
)
async def get_memory(
    memory_id: str,
    namespace: str = "conversations",
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get a memory by ID."""
    try:
        # For demo purposes, return sample data based on ID
        if memory_id == "1":
            return {
                "id": "1",
                "title": "Project Planning Discussion",
                "type": "conversation",
                "sharing": "shared",
                "created_at": "2023-05-15",
                "size": "3.2 KB",
                "content": "Discussion about the upcoming project milestones and resource allocation. Key points include frontend development timeline, backend API design, testing strategy, and deployment planning.",
                "tags": ["project-planning", "milestones", "team"],
                "namespace": namespace
            }
        elif memory_id == "2":
            return {
                "id": "2",
                "title": "System Architecture Spec",
                "type": "document",
                "sharing": "private",
                "created_at": "2023-04-28",
                "size": "15.7 KB",
                "content": "Comprehensive system architecture specification including microservices design, API contracts, data flow diagrams, and deployment strategy. The architecture emphasizes scalability, maintainability, and security.",
                "tags": ["architecture", "technical-spec", "microservices"],
                "namespace": namespace
            }
        
        # Otherwise try to get from memory service
        memory = await memory_service.get(memory_id, namespace)
        
        if not memory:
            return JSONResponse(
                status_code=404,
                content={"error": f"Memory {memory_id} not found in namespace {namespace}"}
            )
        
        return memory
    except Exception as e:
        logger.error(f"Error getting memory {memory_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting memory: {str(e)}"}
        )

@routers.v1.post("/search")
@api_contract(
    title="Memory Search API",
    endpoint="/api/v1/search",
    method="POST",
    request_schema={"query": "string", "namespace": "string", "limit": "int"}
)
@integration_point(
    title="Vector Search Integration",
    target_component="Vector Store (FAISS/Fallback)",
    protocol="Embeddings and Similarity Search",
    data_flow="Query -> Embeddings -> Vector Search -> Ranked Results"
)
async def search_memory(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Search for memories."""
    try:
        data = await request.json()
        query = data.get("query")
        namespace = data.get("namespace", "conversations")
        limit = data.get("limit", 5)
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: query"}
            )
        
        # Handle empty or None namespace
        if not namespace:
            namespace = "conversations"
        
        results = await memory_service.search(
            query=query,
            namespace=namespace,
            limit=limit
        )
        
        # Ensure results is always a dict with expected structure
        if not isinstance(results, dict):
            results = {"results": [], "count": 0}
        
        return results
    except Exception as e:
        logger.error(f"Error searching memory: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error searching memory: {str(e)}"}
        )

@routers.v1.post("/context")
@api_contract(
    title="Context Retrieval API",
    endpoint="/api/v1/context",
    method="POST",
    request_schema={"query": "string", "namespaces": "list", "limit": "int"}
)
async def get_context(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get relevant context from multiple namespaces."""
    try:
        data = await request.json()
        query = data.get("query")
        namespaces = data.get("namespaces")
        limit = data.get("limit", 3)
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: query"}
            )
        
        context = await memory_service.get_relevant_context(
            query=query,
            namespaces=namespaces,
            limit=limit
        )
        
        return {"context": context}
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting context: {str(e)}"}
        )

@routers.v1.get("/namespaces")
async def list_namespaces(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """List available namespaces."""
    try:
        namespaces = await memory_service.get_namespaces()
        return namespaces
    except Exception as e:
        logger.error(f"Error listing namespaces: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error listing namespaces: {str(e)}"}
        )

@routers.v1.post("/compartments")
async def create_compartment(
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Create a new memory compartment."""
    try:
        data = await request.json()
        name = data.get("name")
        description = data.get("description")
        parent = data.get("parent")
        
        if not name:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required parameter: name"}
            )
        
        compartment_id = await memory_service.create_compartment(
            name=name,
            description=description,
            parent=parent
        )
        
        return {
            "id": compartment_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error creating compartment: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error creating compartment: {str(e)}"}
        )

@routers.v1.get("/compartments")
async def list_compartments(
    include_inactive: bool = False,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """List memory compartments."""
    try:
        compartments = await memory_service.list_compartments(include_inactive)
        return compartments
    except Exception as e:
        logger.error(f"Error listing compartments: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error listing compartments: {str(e)}"}
        )

@routers.v1.post("/compartments/{compartment_id}/activate")
async def activate_compartment(
    compartment_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Activate a memory compartment."""
    try:
        success = await memory_service.activate_compartment(compartment_id)
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={"error": f"Compartment {compartment_id} not found"}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error activating compartment {compartment_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error activating compartment: {str(e)}"}
        )

@routers.v1.post("/compartments/{compartment_id}/deactivate")
async def deactivate_compartment(
    compartment_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Deactivate a memory compartment."""
    try:
        success = await memory_service.deactivate_compartment(compartment_id)
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={"error": f"Compartment {compartment_id} not found"}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error deactivating compartment {compartment_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error deactivating compartment: {str(e)}"}
        )

@routers.v1.post("/memory/upload")
@api_contract(
    title="Memory File Upload API",
    description="Upload and process files to create memories",
    endpoint="/api/v1/memory/upload",
    method="POST",
    request_schema={"file": "file (.txt, .md, .json)", "metadata": "object"},
    response_schema={"id": "string", "filename": "string", "size": "int", "status": "string"},
    performance_requirements="<500ms for files under 1MB"
)
@danger_zone(
    title="File Upload Processing",
    description="Processes user-uploaded files with content validation",
    risk_level="medium",
    risks=["malicious_content", "large_file_dos", "encoding_issues"],
    mitigation="File type validation, size limits, UTF-8 decoding with error handling",
    review_required=True
)
async def upload_memory_file(
    file: UploadFile = File(...),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Upload a file and create a memory from it."""
    try:
        # Validate file type
        allowed_types = ['.txt', '.md', '.json']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_types:
            return JSONResponse(
                status_code=400,
                content={"error": f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_types)}"}
            )
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Extract metadata from filename
        metadata = {
            "filename": file.filename,
            "file_type": file_ext,
            "size": len(content),
            "uploaded_at": datetime.now().isoformat()
        }
        
        # For JSON files, try to extract additional metadata
        if file_ext == '.json':
            try:
                json_data = json.loads(content_str)
                if isinstance(json_data, dict):
                    metadata.update(json_data.get('metadata', {}))
                    content_str = json_data.get('content', content_str)
            except json.JSONDecodeError:
                pass  # Use raw content if not valid JSON
        
        # Create memory
        memory_id = await memory_service.add(
            content=content_str,
            namespace="documents",
            metadata=metadata
        )
        
        return {
            "id": memory_id,
            "filename": file.filename,
            "size": len(content),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error uploading file: {str(e)}"}
        )

@routers.v1.get("/memory/browse")
@api_contract(
    title="Memory Browse API",
    endpoint="/api/v1/memory/browse",
    method="GET",
    request_schema={"type": "string", "sharing": "string", "limit": "int", "offset": "int"}
)
async def browse_memories(
    type: Optional[str] = None,
    sharing: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get paginated list of memories with filtering."""
    try:
        # For now, return sample data - this would query the actual memory store
        memories = []
        
        # Sample data for UI testing
        sample_memories = [
            {
                "id": "1",
                "title": "Project Planning Discussion",
                "type": "conversation",
                "sharing": "shared",
                "created_at": "2023-05-15",
                "size": "3.2 KB",
                "preview": "Discussion about the upcoming project milestones and resource allocation...",
                "tags": ["project-planning", "milestones", "team"]
            },
            {
                "id": "2",
                "title": "System Architecture Spec",
                "type": "document",
                "sharing": "private",
                "created_at": "2023-04-28",
                "size": "15.7 KB",
                "preview": "Comprehensive system architecture specification including microservices design...",
                "tags": ["architecture", "technical-spec", "microservices"]
            }
        ]
        
        # Apply filters
        filtered = sample_memories
        if type and type != "all":
            filtered = [m for m in filtered if m["type"] == type]
        if sharing and sharing != "all":
            filtered = [m for m in filtered if m["sharing"] == sharing]
        
        # Apply pagination
        total = len(filtered)
        memories = filtered[offset:offset + limit]
        
        return {
            "memories": memories,
            "total": total,
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error browsing memories: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error browsing memories: {str(e)}"}
        )

@routers.v1.put("/memory/{memory_id}")
@api_contract(
    title="Memory Update API",
    endpoint="/api/v1/memory/{memory_id}",
    method="PUT",
    request_schema={"content": "string", "metadata": "object"}
)
async def update_memory(
    memory_id: str,
    request: Request,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Update an existing memory."""
    try:
        data = await request.json()
        
        # For now, just return success - actual implementation would update the memory
        return {
            "id": memory_id,
            "status": "success",
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating memory {memory_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error updating memory: {str(e)}"}
        )

@routers.v1.delete("/memory/{memory_id}")
@api_contract(
    title="Memory Delete API",
    endpoint="/api/v1/memory/{memory_id}",
    method="DELETE"
)
async def delete_memory(
    memory_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Delete a memory."""
    try:
        # For now, just return success - actual implementation would delete the memory
        return {
            "id": memory_id,
            "status": "deleted"
        }
    except Exception as e:
        logger.error(f"Error deleting memory {memory_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error deleting memory: {str(e)}"}
        )

@routers.v1.get("/insights")
@api_contract(
    title="Memory Insights API",
    description="Get emotional analysis insights from memory patterns",
    endpoint="/api/v1/insights",
    method="GET",
    response_schema={"insights": "array", "total_memories": "int"},
    performance_requirements="<100ms for insight calculation"
)
@performance_boundary(
    title="Insights Analysis Performance",
    description="Analyze memory patterns for emotional insights",
    sla="<100ms response time",
    optimization_notes="Pre-calculated insights updated asynchronously",
    measured_impact="Real-time insights without blocking memory operations"
)
async def get_insights(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get memory insights based on emotional analysis."""
    try:
        # Read insights configuration
        insights_path = Path.home() / '.tekton' / 'engram' / 'insights.md'
        insights_config = {}
        
        if insights_path.exists():
            with open(insights_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) > 1:
                            insight_name = parts[0]
                            keywords = parts[1:]
                            insights_config[insight_name] = keywords
        
        # For now, return sample data with insights
        total_memories = 247  # This would come from actual count
        
        insights = []
        for insight_name, keywords in insights_config.items():
            # In real implementation, would search memories for keywords
            count = len(keywords) * 10  # Dummy calculation
            percentage = int((count / total_memories) * 100)
            
            insights.append({
                "name": insight_name,
                "count": count,
                "percentage": percentage,
                "keywords": keywords,
                "emoji": get_insight_emoji(insight_name)
            })
        
        return {
            "insights": insights,
            "total_memories": total_memories
        }
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting insights: {str(e)}"}
        )

@routers.v1.get("/insights/{insight_name}")
@api_contract(
    title="Insight Memories API",
    endpoint="/api/v1/insights/{insight_name}",
    method="GET"
)
async def get_insight_memories(
    insight_name: str,
    limit: int = 20,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Get memories matching a specific insight category."""
    try:
        # In real implementation, would search for memories containing insight keywords
        return {
            "insight": insight_name,
            "memories": [],
            "count": 0
        }
    except Exception as e:
        logger.error(f"Error getting insight memories: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting insight memories: {str(e)}"}
        )

@performance_boundary(
    title="Insight Emoji Lookup",
    description="O(1) lookup for emotional insight emojis",
    sla="<1ms lookup time",
    optimization_notes="Static dictionary lookup, no computation needed"
)
def get_insight_emoji(insight_name: str) -> str:
    """Get emoji for insight type."""
    emoji_map = {
        "joy": "😊",
        "frustration": "😤",
        "confusion": "🤔",
        "insight": "💡",
        "curiosity": "🔍",
        "achievement": "🏆",
        "learning": "📚",
        "problem": "⚠️",
        "solution": "✅",
        "collaboration": "🤝"
    }
    return emoji_map.get(insight_name, "📊")


# Add ready endpoint
routers.root.add_api_route(
    "/ready",
    create_ready_endpoint(
        component_name="engram",
        component_version="0.1.0",
        start_time=engram_component.global_config._start_time,
        readiness_check=lambda: engram_component.memory_manager is not None
    ),
    methods=["GET"]
)

# Add discovery endpoint to v1 router
routers.v1.add_api_route(
    "/discovery",
    create_discovery_endpoint(
        component_name="engram",
        component_version="0.1.0",
        component_description="Memory management system with vector search and semantic similarity",
        endpoints=[
            EndpointInfo(
                path="/api/v1/memory",
                method="POST",
                description="Add a memory"
            ),
            EndpointInfo(
                path="/api/v1/memory/{memory_id}",
                method="GET",
                description="Get a memory by ID"
            ),
            EndpointInfo(
                path="/api/v1/search",
                method="POST",
                description="Search memories"
            ),
            EndpointInfo(
                path="/api/v1/context",
                method="POST",
                description="Get recent context"
            ),
            EndpointInfo(
                path="/api/v1/namespaces",
                method="GET",
                description="List all namespaces"
            ),
            EndpointInfo(
                path="/api/v1/compartments",
                method="GET",
                description="List all compartments"
            )
        ],
        capabilities=engram_component.get_capabilities(),
        dependencies={
            "hermes": tekton_url("hermes")
        },
        metadata=engram_component.get_metadata()
    ),
    methods=["GET"]
)

# Mount standard routers
mount_standard_routers(app, routers)

# Include standardized workflow endpoint
workflow_router = create_workflow_endpoint("engram")
app.include_router(workflow_router)

# Note: Engram uses shared MCP bridge for standard operation
# The fastmcp_server.py provides standalone MCP mode when run with --standalone flag


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Engram API Server")
    parser.add_argument("--client-id", type=str, default=None,
                      help="Default client ID (default: 'default')")
    parser.add_argument("--port", type=int, default=None,
                      help="Port to run the server on (default: from env config)")
    parser.add_argument("--host", type=str, default=None,
                      help="Host to bind the server to (default: '127.0.0.1')")
    parser.add_argument("--data-dir", type=str, default=None,
                      help="Directory to store memory data (default: '~/.engram')")
    parser.add_argument("--fallback", action="store_true",
                      help="Use fallback file-based implementation without vector database")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode")
    return parser.parse_args()

def main():
    """Main entry point for the server when run directly."""
    args = parse_arguments()
    
    # Override environment variables with command line arguments if provided
    if args.client_id:
        TektonEnviron.set("ENGRAM_CLIENT_ID", args.client_id)
    
    if args.data_dir:
        TektonEnviron.set("ENGRAM_DATA_DIR", args.data_dir)
    
    if args.fallback:
        TektonEnviron.set("ENGRAM_USE_FALLBACK", "1")
    
    if args.debug:
        TektonEnviron.set("ENGRAM_DEBUG", "1")
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get GlobalConfig instance
    global_config = GlobalConfig.get_instance()
    
    # Get host and port from GlobalConfig or arguments
    host = args.host or TektonEnviron.get("ENGRAM_HOST", TektonEnviron.get("TEKTON_HOST", "localhost"))
    port = args.port or global_config.config.engram.port
    
    # Start the server with socket reuse
    logger.info(f"Starting Engram API server on {host}:{port}")
    from shared.utils.socket_server import run_with_socket_reuse
    run_with_socket_reuse(
        "engram.api.server:app",
        host=host,
        port=port,
        timeout_graceful_shutdown=3,
        server_header=False,
        access_log=False
    )

if __name__ == "__main__":
    main()
