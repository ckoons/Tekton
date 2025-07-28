"""
Resource Endpoints

This module defines the API endpoints for resources in the Prometheus/Epimethius Planning System.
Enhanced to support Coder resource management for Development Sprints.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path as PathLib
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.planning import ResourceCreate, ResourceUpdate, ResourceAllocation
from ..models.shared import StandardResponse, PaginatedResponse
from shared.env import TektonEnviron


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.resources")

# Create router
router = APIRouter(prefix="/resources", tags=["resources"])

# Get paths
METADATA_PATH = PathLib(TektonEnviron.get("TEKTON_ROOT", "/Users/cskoons/projects/github/Coder-C")) / "MetaData" / "DevelopmentSprints"
RESOURCES_FILE = METADATA_PATH / "coder_resources.json"

# Placeholder for resource storage (will be replaced with proper storage in future PRs)
resources_db = {}


def load_coder_resources() -> Dict[str, Any]:
    """Load coder resources from file"""
    if not RESOURCES_FILE.exists():
        # Initialize with default structure
        default_resources = {
            "coders": {
                "Tekton": {
                    "capacity": 3,
                    "active": [],
                    "queue": []
                },
                "Coder-A": {
                    "capacity": 3,
                    "active": [],
                    "queue": []
                },
                "Coder-B": {
                    "capacity": 3,
                    "active": [],
                    "queue": []
                },
                "Coder-C": {
                    "capacity": 3,
                    "active": [],
                    "queue": []
                }
            }
        }
        save_coder_resources(default_resources)
        return default_resources
    
    try:
        with open(RESOURCES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading coder resources: {e}")
        return {"coders": {}}


def save_coder_resources(resources: Dict[str, Any]):
    """Save coder resources to file"""
    try:
        RESOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(RESOURCES_FILE, 'w') as f:
            json.dump(resources, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving coder resources: {e}")


# Endpoints
@router.get("/", response_model=PaginatedResponse)
async def list_resources(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order")
):
    """
    List all resources with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        resource_type: Filter by resource type
        skill: Filter by skill
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Paginated list of resources
    """
    # Get all resources (will be replaced with proper storage in future PRs)
    all_resources = list(resources_db.values())
    
    # Apply filters
    if resource_type:
        all_resources = [r for r in all_resources if r.get("resource_type") == resource_type]
    if skill:
        all_resources = [r for r in all_resources if skill in r.get("skills", [])]
    
    # Calculate pagination
    total_items = len(all_resources)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Sort resources
    if sort_by:
        reverse = sort_order.lower() == "desc"
        all_resources.sort(key=lambda r: r.get(sort_by, ""), reverse=reverse)
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    paginated_resources = all_resources[start_idx:end_idx]
    
    return {
        "status": "success",
        "message": f"Retrieved {len(paginated_resources)} resources",
        "data": paginated_resources,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }


@router.post("/", response_model=StandardResponse)
async def create_resource(resource: ResourceCreate):
    """
    Create a new resource.
    
    Args:
        resource: Resource creation data
        
    Returns:
        Created resource
    """
    # Generate resource_id
    from datetime import datetime
    import uuid
    
    resource_id = f"resource-{uuid.uuid4()}"
    
    # Create the resource (will be replaced with proper storage in future PRs)
    new_resource = {
        "resource_id": resource_id,
        "name": resource.name,
        "resource_type": resource.resource_type,
        "capacity": resource.capacity,
        "skills": resource.skills or [],
        "availability": resource.availability or {},
        "cost_rate": resource.cost_rate,
        "metadata": resource.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp()
    }
    
    resources_db[resource_id] = new_resource
    
    logger.info(f"Created resource {resource_id}: {resource.name}")
    
    return {
        "status": "success",
        "message": "Resource created successfully",
        "data": new_resource
    }


@router.get("/{resource_id}", response_model=StandardResponse)
async def get_resource(resource_id: str = Path(..., description="ID of the resource")):
    """
    Get a specific resource.
    
    Args:
        resource_id: ID of the resource
        
    Returns:
        Resource data
    """
    # Check if resource exists
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    
    return {
        "status": "success",
        "message": "Resource retrieved successfully",
        "data": resources_db[resource_id]
    }


@router.put("/{resource_id}", response_model=StandardResponse)
async def update_resource(
    resource: ResourceUpdate,
    resource_id: str = Path(..., description="ID of the resource")
):
    """
    Update a resource.
    
    Args:
        resource_id: ID of the resource
        resource: Resource update data
        
    Returns:
        Updated resource
    """
    # Check if resource exists
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    
    # Update resource (will be replaced with proper storage in future PRs)
    existing_resource = resources_db[resource_id]
    
    # Apply updates
    if resource.name is not None:
        existing_resource["name"] = resource.name
    if resource.resource_type is not None:
        existing_resource["resource_type"] = resource.resource_type
    if resource.capacity is not None:
        existing_resource["capacity"] = resource.capacity
    if resource.skills is not None:
        existing_resource["skills"] = resource.skills
    if resource.availability is not None:
        existing_resource["availability"] = resource.availability
    if resource.cost_rate is not None:
        existing_resource["cost_rate"] = resource.cost_rate
    if resource.metadata is not None:
        existing_resource["metadata"] = resource.metadata
    
    # Update timestamp
    from datetime import datetime
    existing_resource["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated resource {resource_id}")
    
    return {
        "status": "success",
        "message": "Resource updated successfully",
        "data": existing_resource
    }


@router.delete("/{resource_id}", response_model=StandardResponse)
async def delete_resource(resource_id: str = Path(..., description="ID of the resource")):
    """
    Delete a resource.
    
    Args:
        resource_id: ID of the resource
        
    Returns:
        Deletion confirmation
    """
    # Check if resource exists
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    
    # Check if resource is assigned to any tasks
    from .planning import plans_db
    
    is_assigned = False
    for plan in plans_db.values():
        for task in plan["tasks"].values():
            if resource_id in task.get("assigned_resources", []):
                is_assigned = True
                plan_id = plan["plan_id"]
                task_id = task["task_id"]
                break
        if is_assigned:
            break
    
    if is_assigned:
        raise HTTPException(
            status_code=400, 
            detail=f"Resource {resource_id} is assigned to task {task_id} in plan {plan_id}"
        )
    
    # Delete resource (will be replaced with proper storage in future PRs)
    deleted_resource = resources_db.pop(resource_id)
    
    logger.info(f"Deleted resource {resource_id}")
    
    return {
        "status": "success",
        "message": "Resource deleted successfully",
        "data": {"resource_id": resource_id}
    }


@router.get("/skills/list", response_model=StandardResponse)
async def list_skills():
    """
    List all skills across resources.
    
    Returns:
        List of skills
    """
    # Get all skills (will be replaced with proper storage in future PRs)
    skills = set()
    for resource in resources_db.values():
        skills.update(resource.get("skills", []))
    
    return {
        "status": "success",
        "message": "Skills retrieved successfully",
        "data": list(skills)
    }


@router.put("/plans/{plan_id}/allocation", response_model=StandardResponse)
async def allocate_resources(
    allocation: ResourceAllocation,
    plan_id: str = Path(..., description="ID of the plan")
):
    """
    Allocate resources to tasks in a plan.
    
    Args:
        plan_id: ID of the plan
        allocation: Resource allocation data
        
    Returns:
        Updated allocation
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if plan_id matches
    if allocation.plan_id != plan_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Plan ID in path ({plan_id}) does not match plan ID in body ({allocation.plan_id})"
        )
    
    # Validate resources exist
    for resource_id in allocation.allocations.keys():
        if resource_id not in resources_db:
            raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")
    
    # Process allocation (will be replaced with proper implementation in future PRs)
    plan = plans_db[plan_id]
    
    # Update tasks with assigned resources
    for resource_id, task_allocations in allocation.allocations.items():
        for task_allocation in task_allocations:
            task_id = task_allocation.get("task_id")
            if not task_id or task_id not in plan["tasks"]:
                continue
                
            # Update task's assigned resources
            if resource_id not in plan["tasks"][task_id]["assigned_resources"]:
                plan["tasks"][task_id]["assigned_resources"].append(resource_id)
    
    # Update plan version and timestamp
    from datetime import datetime
    plan["version"] += 1
    plan["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated resource allocation for plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Resource allocation updated successfully",
        "data": {
            "plan_id": plan_id,
            "allocations": allocation.allocations
        }
    }


@router.get("/plans/{plan_id}/allocation", response_model=StandardResponse)
async def get_resource_allocation(plan_id: str = Path(..., description="ID of the plan")):
    """
    Get resource allocation for a plan.
    
    Args:
        plan_id: ID of the plan
        
    Returns:
        Current resource allocation
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Get resource allocation (will be replaced with proper implementation in future PRs)
    plan = plans_db[plan_id]
    
    # Build allocation object
    allocation = {"plan_id": plan_id, "allocations": {}}
    
    # Group by resource
    for task_id, task in plan["tasks"].items():
        for resource_id in task.get("assigned_resources", []):
            if resource_id not in allocation["allocations"]:
                allocation["allocations"][resource_id] = []
                
            allocation["allocations"][resource_id].append({
                "task_id": task_id,
                "start_date": task.get("start_date"),
                "end_date": task.get("end_date"),
                "effort": task.get("estimated_effort")
            })
    
    return {
        "status": "success",
        "message": "Resource allocation retrieved successfully",
        "data": allocation
    }


# ===== Coder Resource Management Endpoints =====

@router.get("/coders", response_model=StandardResponse)
async def get_coders():
    """Get all Coder resources and their assignments"""
    try:
        resources = load_coder_resources()
        return {
            "status": "success",
            "message": "Coder resources retrieved successfully",
            "data": resources["coders"]
        }
    except Exception as e:
        logger.error(f"Error getting coder resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coders/{coder_name}", response_model=StandardResponse)
async def get_coder_details(coder_name: str):
    """Get details for a specific coder"""
    try:
        resources = load_coder_resources()
        if coder_name not in resources["coders"]:
            raise HTTPException(status_code=404, detail=f"Coder {coder_name} not found")
        
        return {
            "status": "success",
            "message": f"Coder {coder_name} details retrieved",
            "data": resources["coders"][coder_name]
        }
    except Exception as e:
        logger.error(f"Error getting coder details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/coders/{coder_name}/assign", response_model=StandardResponse)
async def assign_sprint_to_coder(
    coder_name: str,
    assignment: Dict[str, str] = Body(..., example={"sprint_name": "Planning_Team_UI_Sprint", "project": "TektonCore"})
):
    """Assign a sprint to a coder"""
    try:
        resources = load_coder_resources()
        if coder_name not in resources["coders"]:
            raise HTTPException(status_code=404, detail=f"Coder {coder_name} not found")
        
        coder = resources["coders"][coder_name]
        sprint_name = assignment["sprint_name"]
        project = assignment.get("project", "Unknown")
        
        # Check capacity
        if len(coder["active"]) >= coder["capacity"]:
            # Add to queue instead
            if sprint_name not in coder["queue"]:
                coder["queue"].append(sprint_name)
            message = f"Sprint {sprint_name} added to {coder_name}'s queue (at capacity)"
        else:
            # Add to active
            if sprint_name not in coder["active"]:
                coder["active"].append(sprint_name)
            message = f"Sprint {sprint_name} assigned to {coder_name} as active"
        
        save_coder_resources(resources)
        
        return {
            "status": "success",
            "message": message,
            "data": coder
        }
    except Exception as e:
        logger.error(f"Error assigning sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/coders/{coder_name}/complete", response_model=StandardResponse)
async def complete_coder_sprint(
    coder_name: str,
    completion: Dict[str, str] = Body(..., example={"sprint_name": "Planning_Team_UI_Sprint"})
):
    """Mark a sprint as complete and assign next from queue"""
    try:
        resources = load_coder_resources()
        if coder_name not in resources["coders"]:
            raise HTTPException(status_code=404, detail=f"Coder {coder_name} not found")
        
        coder = resources["coders"][coder_name]
        sprint_name = completion["sprint_name"]
        
        # Remove from active
        if sprint_name in coder["active"]:
            coder["active"].remove(sprint_name)
        
        # Assign next from queue if available
        next_sprint = None
        if coder["queue"] and len(coder["active"]) < coder["capacity"]:
            next_sprint = coder["queue"].pop(0)
            coder["active"].append(next_sprint)
        
        save_coder_resources(resources)
        
        message = f"Sprint {sprint_name} completed for {coder_name}"
        if next_sprint:
            message += f", assigned {next_sprint} from queue"
        
        return {
            "status": "success",
            "message": message,
            "data": {
                "coder": coder,
                "next_sprint": next_sprint
            }
        }
    except Exception as e:
        logger.error(f"Error completing sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capacity", response_model=StandardResponse)
async def get_capacity_overview():
    """Get capacity overview for all coders"""
    try:
        resources = load_coder_resources()
        overview = {}
        
        for coder_name, coder_data in resources["coders"].items():
            overview[coder_name] = {
                "capacity": coder_data["capacity"],
                "active_count": len(coder_data["active"]),
                "queue_count": len(coder_data["queue"]),
                "utilization": len(coder_data["active"]) / coder_data["capacity"] * 100 if coder_data["capacity"] > 0 else 0,
                "available_slots": max(0, coder_data["capacity"] - len(coder_data["active"]))
            }
        
        return {
            "status": "success",
            "message": "Capacity overview retrieved",
            "data": overview
        }
    except Exception as e:
        logger.error(f"Error getting capacity overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))