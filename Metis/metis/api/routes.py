"""
API routes for Metis

This module defines the FastAPI routes for the Metis API, mapping HTTP
endpoints to controller methods.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, WebSocket, status, Request

from metis.api.controllers import TaskController
from metis.api.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskDetailResponse, DependencyCreate, DependencyUpdate,
    DependencyResponse, DependencyListResponse, SubtaskCreate,
    SubtaskUpdate, RequirementRefCreate, RequirementRefUpdate,
    ApiResponse, WebSocketMessage, WebSocketRegistration
)
from metis.core.mcp.tools import decompose_task as mcp_decompose_task


# Create router
router = APIRouter(prefix="/api/v1")


# Dependency for getting the controller
def get_task_controller(request: Request) -> TaskController:
    """Get the TaskController instance from the component."""
    component = request.app.state.component
    if not component or not component.task_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Component not initialized"
        )
    # Create controller with component's task manager
    return TaskController(component.task_manager)


# Task routes

@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task with the given data",
    tags=["Tasks"]
)
async def create_task(
    task_create: TaskCreate,
    controller: TaskController = Depends(get_task_controller)
):
    """Create a new task."""
    return await controller.create_task(task_create)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get a task by ID",
    description="Get detailed information about a specific task",
    tags=["Tasks"]
)
async def get_task(
    task_id: str = Path(..., title="The ID of the task to get"),
    controller: TaskController = Depends(get_task_controller)
):
    """Get a task by ID."""
    return await controller.get_task(task_id)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update a task with the given data",
    tags=["Tasks"]
)
async def update_task(
    task_update: TaskUpdate,
    task_id: str = Path(..., title="The ID of the task to update"),
    controller: TaskController = Depends(get_task_controller)
):
    """Update a task."""
    return await controller.update_task(task_id, task_update)


@router.delete(
    "/tasks/{task_id}",
    response_model=ApiResponse,
    summary="Delete a task",
    description="Delete a task by ID",
    tags=["Tasks"]
)
async def delete_task(
    task_id: str = Path(..., title="The ID of the task to delete"),
    controller: TaskController = Depends(get_task_controller)
):
    """Delete a task."""
    return await controller.delete_task(task_id)


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List tasks",
    description="List tasks with optional filtering",
    tags=["Tasks"]
)
async def list_tasks(
    status: Optional[str] = Query(None, title="Filter by status"),
    priority: Optional[str] = Query(None, title="Filter by priority"),
    assignee: Optional[str] = Query(None, title="Filter by assignee"),
    tag: Optional[str] = Query(None, title="Filter by tag"),
    search: Optional[str] = Query(None, title="Search term for title/description"),
    page: int = Query(1, title="Page number", ge=1),
    page_size: int = Query(50, title="Page size", ge=1, le=100),
    controller: TaskController = Depends(get_task_controller)
):
    """List tasks with filtering."""
    return await controller.list_tasks(
        status=status,
        priority=priority,
        assignee=assignee,
        tag=tag,
        search=search,
        page=page,
        page_size=page_size
    )


# Subtask routes

@router.post(
    "/tasks/{task_id}/subtasks",
    response_model=TaskResponse,
    summary="Add a subtask",
    description="Add a subtask to a task",
    tags=["Subtasks"]
)
async def add_subtask(
    subtask_create: SubtaskCreate,
    task_id: str = Path(..., title="The ID of the parent task"),
    controller: TaskController = Depends(get_task_controller)
):
    """Add a subtask to a task."""
    return await controller.add_subtask(task_id, subtask_create)


@router.put(
    "/tasks/{task_id}/subtasks/{subtask_id}",
    response_model=TaskResponse,
    summary="Update a subtask",
    description="Update a subtask within a task",
    tags=["Subtasks"]
)
async def update_subtask(
    subtask_update: SubtaskUpdate,
    task_id: str = Path(..., title="The ID of the parent task"),
    subtask_id: str = Path(..., title="The ID of the subtask to update"),
    controller: TaskController = Depends(get_task_controller)
):
    """Update a subtask."""
    return await controller.update_subtask(task_id, subtask_id, subtask_update)


@router.delete(
    "/tasks/{task_id}/subtasks/{subtask_id}",
    response_model=TaskResponse,
    summary="Remove a subtask",
    description="Remove a subtask from a task",
    tags=["Subtasks"]
)
async def remove_subtask(
    task_id: str = Path(..., title="The ID of the parent task"),
    subtask_id: str = Path(..., title="The ID of the subtask to remove"),
    controller: TaskController = Depends(get_task_controller)
):
    """Remove a subtask from a task."""
    return await controller.remove_subtask(task_id, subtask_id)


# Requirement reference routes

@router.post(
    "/tasks/{task_id}/requirements",
    response_model=TaskResponse,
    summary="Add a requirement reference",
    description="Add a requirement reference to a task",
    tags=["Requirements"]
)
async def add_requirement_ref(
    req_ref_create: RequirementRefCreate,
    task_id: str = Path(..., title="The ID of the task"),
    controller: TaskController = Depends(get_task_controller)
):
    """Add a requirement reference to a task."""
    return await controller.add_requirement_ref(task_id, req_ref_create)


@router.put(
    "/tasks/{task_id}/requirements/{ref_id}",
    response_model=TaskResponse,
    summary="Update a requirement reference",
    description="Update a requirement reference within a task",
    tags=["Requirements"]
)
async def update_requirement_ref(
    req_ref_update: RequirementRefUpdate,
    task_id: str = Path(..., title="The ID of the task"),
    ref_id: str = Path(..., title="The ID of the requirement reference to update"),
    controller: TaskController = Depends(get_task_controller)
):
    """Update a requirement reference."""
    return await controller.update_requirement_ref(task_id, ref_id, req_ref_update)


@router.delete(
    "/tasks/{task_id}/requirements/{ref_id}",
    response_model=TaskResponse,
    summary="Remove a requirement reference",
    description="Remove a requirement reference from a task",
    tags=["Requirements"]
)
async def remove_requirement_ref(
    task_id: str = Path(..., title="The ID of the task"),
    ref_id: str = Path(..., title="The ID of the requirement reference to remove"),
    controller: TaskController = Depends(get_task_controller)
):
    """Remove a requirement reference from a task."""
    return await controller.remove_requirement_ref(task_id, ref_id)


# Dependency routes

@router.post(
    "/dependencies",
    response_model=DependencyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a dependency",
    description="Create a dependency between two tasks",
    tags=["Dependencies"]
)
async def create_dependency(
    dependency_create: DependencyCreate,
    controller: TaskController = Depends(get_task_controller)
):
    """Create a dependency between tasks."""
    return await controller.create_dependency(dependency_create)


@router.get(
    "/dependencies/{dependency_id}",
    response_model=DependencyResponse,
    summary="Get a dependency",
    description="Get a dependency by ID",
    tags=["Dependencies"]
)
async def get_dependency(
    dependency_id: str = Path(..., title="The ID of the dependency to get"),
    controller: TaskController = Depends(get_task_controller)
):
    """Get a dependency by ID."""
    return await controller.get_dependency(dependency_id)


@router.put(
    "/dependencies/{dependency_id}",
    response_model=DependencyResponse,
    summary="Update a dependency",
    description="Update a dependency with the given data",
    tags=["Dependencies"]
)
async def update_dependency(
    dependency_update: DependencyUpdate,
    dependency_id: str = Path(..., title="The ID of the dependency to update"),
    controller: TaskController = Depends(get_task_controller)
):
    """Update a dependency."""
    return await controller.update_dependency(dependency_id, dependency_update)


@router.delete(
    "/dependencies/{dependency_id}",
    response_model=ApiResponse,
    summary="Delete a dependency",
    description="Delete a dependency by ID",
    tags=["Dependencies"]
)
async def delete_dependency(
    dependency_id: str = Path(..., title="The ID of the dependency to delete"),
    controller: TaskController = Depends(get_task_controller)
):
    """Delete a dependency."""
    return await controller.delete_dependency(dependency_id)


@router.get(
    "/dependencies",
    response_model=DependencyListResponse,
    summary="List dependencies",
    description="List dependencies with optional filtering",
    tags=["Dependencies"]
)
async def list_dependencies(
    task_id: Optional[str] = Query(None, title="Filter by task ID"),
    dependency_type: Optional[str] = Query(None, title="Filter by dependency type"),
    controller: TaskController = Depends(get_task_controller)
):
    """List dependencies with filtering."""
    return await controller.list_dependencies(
        task_id=task_id,
        dependency_type=dependency_type
    )


@router.get(
    "/tasks/{task_id}/dependencies",
    response_model=DependencyListResponse,
    summary="List task dependencies",
    description="List dependencies for a specific task",
    tags=["Dependencies"]
)
async def list_task_dependencies(
    task_id: str = Path(..., title="The ID of the task"),
    controller: TaskController = Depends(get_task_controller)
):
    """List dependencies for a specific task."""
    return await controller.list_dependencies(task_id=task_id)


# Telos integration routes

@router.get(
    "/telos/requirements",
    response_model=Dict[str, Any],
    summary="Search Telos requirements",
    description="Search for requirements in the Telos system",
    tags=["Telos Integration"]
)
async def search_telos_requirements(
    query: Optional[str] = Query(None, title="Search query"),
    status: Optional[str] = Query(None, title="Filter by status"),
    category: Optional[str] = Query(None, title="Filter by category"),
    page: int = Query(1, title="Page number", ge=1),
    page_size: int = Query(50, title="Page size", ge=1, le=100),
    controller: TaskController = Depends(get_task_controller)
):
    """Search for requirements in Telos."""
    requirements, total = await controller.task_manager.search_telos_requirements(
        query=query,
        status=status,
        category=category,
        page=page,
        page_size=page_size
    )
    
    return {
        "success": True,
        "requirements": requirements,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post(
    "/telos/requirements/{requirement_id}/import",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import Telos requirement as task",
    description="Import a requirement from Telos as a new task",
    tags=["Telos Integration"]
)
async def import_requirement_as_task(
    requirement_id: str = Path(..., title="The ID of the requirement to import"),
    controller: TaskController = Depends(get_task_controller)
):
    """Import a requirement from Telos as a new task."""
    task = await controller.task_manager.import_requirement_as_task(requirement_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement not found: {requirement_id}"
        )
    
    # Convert to response schema
    return controller._task_to_response(task)


# AI-powered endpoints

@router.post(
    "/tasks/{task_id}/decompose",
    response_model=Dict[str, Any],
    summary="Decompose task using AI",
    description="Break down a task into subtasks using AI-powered decomposition",
    tags=["AI Features"]
)
async def decompose_task(
    task_id: str = Path(..., title="The ID of the task to decompose"),
    depth: int = Query(2, title="Maximum decomposition depth", ge=1, le=5),
    max_subtasks: int = Query(10, title="Maximum number of subtasks", ge=1, le=20),
    auto_create: bool = Query(True, title="Automatically create subtasks"),
    controller: TaskController = Depends(get_task_controller)
):
    """Decompose a task into subtasks using AI."""
    result = await mcp_decompose_task(
        task_id=task_id,
        depth=depth,
        max_subtasks=max_subtasks,
        auto_create=auto_create
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Task decomposition failed")
        )
    
    return result


@router.post(
    "/tasks/{task_id}/analyze-complexity",
    response_model=Dict[str, Any],
    summary="Analyze task complexity using AI",
    description="Get AI-powered analysis of task complexity",
    tags=["AI Features"]
)
async def analyze_task_complexity(
    task_id: str = Path(..., title="The ID of the task to analyze"),
    include_subtasks: bool = Query(True, title="Include subtasks in analysis"),
    controller: TaskController = Depends(get_task_controller)
):
    """Analyze task complexity using AI."""
    from metis.core.mcp.tools import analyze_task_complexity as mcp_analyze_complexity
    
    result = await mcp_analyze_complexity(
        task_id=task_id,
        include_subtasks=include_subtasks
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Complexity analysis failed")
        )
    
    return result


@router.post(
    "/tasks/suggest-order",
    response_model=Dict[str, Any],
    summary="Suggest optimal task execution order",
    description="Get AI-powered suggestions for task execution order",
    tags=["AI Features"]
)
async def suggest_task_order(
    task_ids: Optional[List[str]] = Body(None, title="List of task IDs to order"),
    status_filter: Optional[str] = Query(None, title="Filter by status", enum=["pending", "in_progress", "completed", "blocked"]),
    controller: TaskController = Depends(get_task_controller)
):
    """Suggest optimal task execution order using AI."""
    from metis.core.mcp.tools import suggest_task_order as mcp_suggest_order
    
    result = await mcp_suggest_order(
        task_ids=task_ids,
        status_filter=status_filter
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Task ordering failed")
        )
    
    return result


@router.post(
    "/tasks/{task_id}/telos/requirements/{requirement_id}",
    response_model=TaskResponse,
    summary="Add Telos requirement reference",
    description="Add a reference to a Telos requirement to a task",
    tags=["Telos Integration"]
)
async def add_telos_requirement_ref(
    task_id: str = Path(..., title="The ID of the task"),
    requirement_id: str = Path(..., title="The ID of the requirement to reference")
):
    """Add a reference to a Telos requirement to a task."""
    req_ref, task = await task_manager.import_requirement(requirement_id, task_id)
    
    if not req_ref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement not found: {requirement_id}"
        )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}"
        )
    
    # Convert to response schema
    from metis.api.controllers import TaskController
    controller = TaskController(task_manager)
    return controller._task_to_response(task)


# AI-powered endpoints

@router.post(
    "/tasks/{task_id}/decompose",
    response_model=Dict[str, Any],
    summary="Decompose task using AI",
    description="Break down a task into subtasks using AI-powered decomposition",
    tags=["AI Features"]
)
async def decompose_task(
    task_id: str = Path(..., title="The ID of the task to decompose"),
    depth: int = Query(2, title="Maximum decomposition depth", ge=1, le=5),
    max_subtasks: int = Query(10, title="Maximum number of subtasks", ge=1, le=20),
    auto_create: bool = Query(True, title="Automatically create subtasks"),
    controller: TaskController = Depends(get_task_controller)
):
    """Decompose a task into subtasks using AI."""
    result = await mcp_decompose_task(
        task_id=task_id,
        depth=depth,
        max_subtasks=max_subtasks,
        auto_create=auto_create
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Task decomposition failed")
        )
    
    return result


@router.post(
    "/tasks/{task_id}/analyze-complexity",
    response_model=Dict[str, Any],
    summary="Analyze task complexity using AI",
    description="Get AI-powered analysis of task complexity",
    tags=["AI Features"]
)
async def analyze_task_complexity(
    task_id: str = Path(..., title="The ID of the task to analyze"),
    include_subtasks: bool = Query(True, title="Include subtasks in analysis"),
    controller: TaskController = Depends(get_task_controller)
):
    """Analyze task complexity using AI."""
    from metis.core.mcp.tools import analyze_task_complexity as mcp_analyze_complexity
    
    result = await mcp_analyze_complexity(
        task_id=task_id,
        include_subtasks=include_subtasks
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Complexity analysis failed")
        )
    
    return result


@router.post(
    "/tasks/suggest-order",
    response_model=Dict[str, Any],
    summary="Suggest optimal task execution order",
    description="Get AI-powered suggestions for task execution order",
    tags=["AI Features"]
)
async def suggest_task_order(
    task_ids: Optional[List[str]] = Body(None, title="List of task IDs to order"),
    status_filter: Optional[str] = Query(None, title="Filter by status", enum=["pending", "in_progress", "completed", "blocked"]),
    controller: TaskController = Depends(get_task_controller)
):
    """Suggest optimal task execution order using AI."""
    from metis.core.mcp.tools import suggest_task_order as mcp_suggest_order
    
    result = await mcp_suggest_order(
        task_ids=task_ids,
        status_filter=status_filter
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Task ordering failed")
        )
    
    return result