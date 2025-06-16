"""
Task Endpoints

This module defines the API endpoints for tasks in the Prometheus/Epimethius Planning System.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.planning import TaskCreate, TaskUpdate
from ..models.shared import StandardResponse, PaginatedResponse


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.tasks")

# Create router
router = APIRouter(prefix="/plans/{plan_id}/tasks", tags=["tasks"])


# Endpoints
@router.get("/", response_model=PaginatedResponse)
async def list_tasks(
    plan_id: str = Path(..., description="ID of the plan"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order")
):
    """
    List tasks for a plan with pagination and filtering.
    
    Args:
        plan_id: ID of the plan
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Filter by status
        priority: Filter by priority
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Paginated list of tasks
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Get all tasks for the plan
    all_tasks = list(plans_db[plan_id]["tasks"].values())
    
    # Apply filters
    if status:
        all_tasks = [task for task in all_tasks if task.get("status") == status]
    if priority:
        all_tasks = [task for task in all_tasks if task.get("priority") == priority]
    
    # Calculate pagination
    total_items = len(all_tasks)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Sort tasks
    if sort_by:
        reverse = sort_order.lower() == "desc"
        all_tasks.sort(key=lambda t: t.get(sort_by, ""), reverse=reverse)
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    paginated_tasks = all_tasks[start_idx:end_idx]
    
    return {
        "status": "success",
        "message": f"Retrieved {len(paginated_tasks)} tasks",
        "data": paginated_tasks,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }


@router.post("/", response_model=StandardResponse)
async def create_task(
    task: TaskCreate,
    plan_id: str = Path(..., description="ID of the plan")
):
    """
    Create a new task for a plan.
    
    Args:
        plan_id: ID of the plan
        task: Task creation data
        
    Returns:
        Created task
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Generate task_id
    from datetime import datetime
    import uuid
    
    task_id = f"task-{uuid.uuid4()}"
    
    # Create the task (will be replaced with proper storage in future PRs)
    new_task = {
        "task_id": task_id,
        "name": task.name,
        "description": task.description,
        "status": "not_started",
        "priority": task.priority,
        "estimated_effort": task.estimated_effort,
        "actual_effort": 0.0,
        "progress": 0.0,
        "assigned_resources": task.assigned_resources or [],
        "dependencies": task.dependencies or [],
        "requirements": task.requirements or [],
        "start_date": task.start_date.isoformat() if task.start_date else None,
        "end_date": task.end_date.isoformat() if task.end_date else None,
        "metadata": task.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp()
    }
    
    # Add task to plan
    plans_db[plan_id]["tasks"][task_id] = new_task
    
    # Update plan version and timestamp
    plans_db[plan_id]["version"] += 1
    plans_db[plan_id]["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Created task {task_id} for plan {plan_id}: {task.name}")
    
    return {
        "status": "success",
        "message": "Task created successfully",
        "data": new_task
    }


@router.get("/{task_id}", response_model=StandardResponse)
async def get_task(
    plan_id: str = Path(..., description="ID of the plan"),
    task_id: str = Path(..., description="ID of the task")
):
    """
    Get a specific task.
    
    Args:
        plan_id: ID of the plan
        task_id: ID of the task
        
    Returns:
        Task data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if task exists
    if task_id not in plans_db[plan_id]["tasks"]:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Task retrieved successfully",
        "data": plans_db[plan_id]["tasks"][task_id]
    }


@router.put("/{task_id}", response_model=StandardResponse)
async def update_task(
    task: TaskUpdate,
    plan_id: str = Path(..., description="ID of the plan"),
    task_id: str = Path(..., description="ID of the task")
):
    """
    Update a task.
    
    Args:
        plan_id: ID of the plan
        task_id: ID of the task
        task: Task update data
        
    Returns:
        Updated task
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if task exists
    if task_id not in plans_db[plan_id]["tasks"]:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in plan {plan_id}")
    
    # Update task (will be replaced with proper storage in future PRs)
    existing_task = plans_db[plan_id]["tasks"][task_id]
    
    # Apply updates
    if task.name is not None:
        existing_task["name"] = task.name
    if task.description is not None:
        existing_task["description"] = task.description
    if task.status is not None:
        existing_task["status"] = task.status
    if task.priority is not None:
        existing_task["priority"] = task.priority
    if task.estimated_effort is not None:
        existing_task["estimated_effort"] = task.estimated_effort
    if task.actual_effort is not None:
        existing_task["actual_effort"] = task.actual_effort
    if task.assigned_resources is not None:
        existing_task["assigned_resources"] = task.assigned_resources
    if task.dependencies is not None:
        existing_task["dependencies"] = task.dependencies
    if task.requirements is not None:
        existing_task["requirements"] = task.requirements
    if task.start_date is not None:
        existing_task["start_date"] = task.start_date.isoformat()
    if task.end_date is not None:
        existing_task["end_date"] = task.end_date.isoformat()
    if task.progress is not None:
        existing_task["progress"] = task.progress
    if task.metadata is not None:
        existing_task["metadata"] = task.metadata
    
    # Update timestamp
    from datetime import datetime
    existing_task["updated_at"] = datetime.now().timestamp()
    
    # Update plan version and timestamp
    plans_db[plan_id]["version"] += 1
    plans_db[plan_id]["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated task {task_id} in plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Task updated successfully",
        "data": existing_task
    }


@router.delete("/{task_id}", response_model=StandardResponse)
async def delete_task(
    plan_id: str = Path(..., description="ID of the plan"),
    task_id: str = Path(..., description="ID of the task")
):
    """
    Delete a task.
    
    Args:
        plan_id: ID of the plan
        task_id: ID of the task
        
    Returns:
        Deletion confirmation
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if task exists
    if task_id not in plans_db[plan_id]["tasks"]:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found in plan {plan_id}")
    
    # Delete task (will be replaced with proper storage in future PRs)
    deleted_task = plans_db[plan_id]["tasks"].pop(task_id)
    
    # Update plan version and timestamp
    from datetime import datetime
    plans_db[plan_id]["version"] += 1
    plans_db[plan_id]["updated_at"] = datetime.now().timestamp()
    
    # Remove task from dependencies of other tasks
    for other_task in plans_db[plan_id]["tasks"].values():
        if task_id in other_task.get("dependencies", []):
            other_task["dependencies"].remove(task_id)
    
    logger.info(f"Deleted task {task_id} from plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Task deleted successfully",
        "data": {"task_id": task_id, "plan_id": plan_id}
    }