"""
Retrospective Endpoints

This module defines the API endpoints for retrospectives in the Prometheus/Epimethius Planning System.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.retrospective import (
    RetrospectiveCreate, RetrospectiveUpdate, 
    RetroItemCreate, RetroItemUpdate,
    ActionItemCreate, ActionItemUpdate
)
from ..models.shared import StandardResponse, PaginatedResponse

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        integration_point,
        state_checkpoint
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
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.retrospective")

# Create router
router = APIRouter(prefix="/retrospectives", tags=["retrospectives"])


# Placeholder for retrospective storage (will be replaced with proper storage in future PRs)
retrospectives_db = {}


# Endpoints
@router.get("/", response_model=PaginatedResponse)
async def list_retrospectives(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    plan_id: Optional[str] = Query(None, description="Filter by plan ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: Optional[str] = Query("date", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """
    List all retrospectives with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        plan_id: Filter by plan ID
        status: Filter by status
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Paginated list of retrospectives
    """
    # Get all retrospectives (will be replaced with proper storage in future PRs)
    all_retros = list(retrospectives_db.values())
    
    # Apply filters
    if plan_id:
        all_retros = [r for r in all_retros if r.get("plan_id") == plan_id]
    if status:
        all_retros = [r for r in all_retros if r.get("status") == status]
    
    # Calculate pagination
    total_items = len(all_retros)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Sort retrospectives
    if sort_by:
        reverse = sort_order.lower() == "desc"
        all_retros.sort(key=lambda r: r.get(sort_by, ""), reverse=reverse)
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    paginated_retros = all_retros[start_idx:end_idx]
    
    return {
        "status": "success",
        "message": f"Retrieved {len(paginated_retros)} retrospectives",
        "data": paginated_retros,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }


@router.post("/", response_model=StandardResponse)
async def create_retrospective(retro: RetrospectiveCreate):
    """
    Create a new retrospective.
    
    Args:
        retro: Retrospective creation data
        
    Returns:
        Created retrospective
    """
    # Check if plan exists
    from .planning import plans_db
    if retro.plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {retro.plan_id} not found")
    
    # Generate retro_id
    from datetime import datetime
    import uuid
    
    retro_id = f"retro-{uuid.uuid4()}"
    
    # Create the retrospective (will be replaced with proper storage in future PRs)
    new_retro = {
        "retro_id": retro_id,
        "plan_id": retro.plan_id,
        "name": retro.name,
        "date": retro.date.isoformat() if retro.date else datetime.now().isoformat(),
        "format": retro.format,
        "facilitator": retro.facilitator,
        "participants": retro.participants or [],
        "items": [],
        "action_items": [],
        "status": "draft",
        "metadata": retro.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp()
    }
    
    retrospectives_db[retro_id] = new_retro
    
    logger.info(f"Created retrospective {retro_id}: {retro.name}")
    
    return {
        "status": "success",
        "message": "Retrospective created successfully",
        "data": new_retro
    }


@router.get("/{retro_id}", response_model=StandardResponse)
async def get_retrospective(retro_id: str = Path(..., description="ID of the retrospective")):
    """
    Get a specific retrospective.
    
    Args:
        retro_id: ID of the retrospective
        
    Returns:
        Retrospective data
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    return {
        "status": "success",
        "message": "Retrospective retrieved successfully",
        "data": retrospectives_db[retro_id]
    }


@router.put("/{retro_id}", response_model=StandardResponse)
async def update_retrospective(
    retro: RetrospectiveUpdate,
    retro_id: str = Path(..., description="ID of the retrospective")
):
    """
    Update a retrospective.
    
    Args:
        retro_id: ID of the retrospective
        retro: Retrospective update data
        
    Returns:
        Updated retrospective
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    # Update retrospective (will be replaced with proper storage in future PRs)
    existing_retro = retrospectives_db[retro_id]
    
    # Apply updates
    if retro.name is not None:
        existing_retro["name"] = retro.name
    if retro.format is not None:
        existing_retro["format"] = retro.format
    if retro.facilitator is not None:
        existing_retro["facilitator"] = retro.facilitator
    if retro.date is not None:
        existing_retro["date"] = retro.date.isoformat()
    if retro.participants is not None:
        existing_retro["participants"] = retro.participants
    if retro.status is not None:
        existing_retro["status"] = retro.status
    if retro.metadata is not None:
        existing_retro["metadata"] = retro.metadata
    
    # Update timestamp
    from datetime import datetime
    existing_retro["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated retrospective {retro_id}")
    
    return {
        "status": "success",
        "message": "Retrospective updated successfully",
        "data": existing_retro
    }


@router.delete("/{retro_id}", response_model=StandardResponse)
async def delete_retrospective(retro_id: str = Path(..., description="ID of the retrospective")):
    """
    Delete a retrospective.
    
    Args:
        retro_id: ID of the retrospective
        
    Returns:
        Deletion confirmation
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    # Check if retrospective can be deleted
    if retrospectives_db[retro_id]["status"] == "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete completed retrospective {retro_id}"
        )
    
    # Delete retrospective (will be replaced with proper storage in future PRs)
    deleted_retro = retrospectives_db.pop(retro_id)
    
    logger.info(f"Deleted retrospective {retro_id}")
    
    return {
        "status": "success",
        "message": "Retrospective deleted successfully",
        "data": {"retro_id": retro_id}
    }


@router.post("/{retro_id}/items", response_model=StandardResponse)
async def add_retro_item(
    item: RetroItemCreate,
    retro_id: str = Path(..., description="ID of the retrospective")
):
    """
    Add an item to a retrospective.
    
    Args:
        retro_id: ID of the retrospective
        item: Retrospective item creation data
        
    Returns:
        Created retrospective item
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    # Check if retrospective is in draft or in progress
    if retrospectives_db[retro_id]["status"] == "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot add items to completed retrospective {retro_id}"
        )
    
    # Generate item_id
    from datetime import datetime
    import uuid
    
    item_id = f"item-{uuid.uuid4()}"
    
    # Create the retrospective item (will be replaced with proper storage in future PRs)
    new_item = {
        "item_id": item_id,
        "content": item.content,
        "category": item.category,
        "votes": 0,
        "author": item.author,
        "related_task_ids": item.related_task_ids or [],
        "metadata": item.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp()
    }
    
    # Add item to retrospective
    retrospectives_db[retro_id]["items"].append(new_item)
    
    # Update retrospective timestamp
    retrospectives_db[retro_id]["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Added item {item_id} to retrospective {retro_id}")
    
    return {
        "status": "success",
        "message": "Retrospective item added successfully",
        "data": new_item
    }


@router.post("/{retro_id}/action-items", response_model=StandardResponse)
async def add_action_item(
    action: ActionItemCreate,
    retro_id: str = Path(..., description="ID of the retrospective")
):
    """
    Add an action item to a retrospective.
    
    Args:
        retro_id: ID of the retrospective
        action: Action item creation data
        
    Returns:
        Created action item
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    # Generate action_id
    from datetime import datetime
    import uuid
    
    action_id = f"action-{uuid.uuid4()}"
    
    # Create the action item (will be replaced with proper storage in future PRs)
    new_action = {
        "action_id": action_id,
        "title": action.title,
        "description": action.description,
        "assignees": action.assignees or [],
        "due_date": action.due_date.isoformat() if action.due_date else None,
        "status": "open",
        "priority": action.priority,
        "related_retro_items": action.related_retro_items or [],
        "metadata": action.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp(),
        "completed_at": None,
        "status_history": [{
            "status": "open",
            "timestamp": datetime.now().timestamp()
        }]
    }
    
    # Add action item to retrospective
    retrospectives_db[retro_id]["action_items"].append(new_action)
    
    # Update retrospective timestamp
    retrospectives_db[retro_id]["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Added action item {action_id} to retrospective {retro_id}")
    
    return {
        "status": "success",
        "message": "Action item added successfully",
        "data": new_action
    }


@router.put("/{retro_id}/items/{item_id}", response_model=StandardResponse)
async def update_retro_item(
    item: RetroItemUpdate,
    retro_id: str = Path(..., description="ID of the retrospective"),
    item_id: str = Path(..., description="ID of the retrospective item")
):
    """
    Update a retrospective item.
    
    Args:
        retro_id: ID of the retrospective
        item_id: ID of the retrospective item
        item: Retrospective item update data
        
    Returns:
        Updated retrospective item
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    # Find the item
    retro = retrospectives_db[retro_id]
    item_index = None
    for i, existing_item in enumerate(retro["items"]):
        if existing_item["item_id"] == item_id:
            item_index = i
            break
    
    if item_index is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found in retrospective {retro_id}")
    
    # Check if retrospective is in draft or in progress
    if retro["status"] == "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot update items in completed retrospective {retro_id}"
        )
    
    # Update item (will be replaced with proper storage in future PRs)
    existing_item = retro["items"][item_index]
    
    # Apply updates
    if item.content is not None:
        existing_item["content"] = item.content
    if item.category is not None:
        existing_item["category"] = item.category
    if item.votes is not None:
        existing_item["votes"] = item.votes
    if item.related_task_ids is not None:
        existing_item["related_task_ids"] = item.related_task_ids
    if item.metadata is not None:
        existing_item["metadata"] = item.metadata
    
    # Update timestamp
    from datetime import datetime
    existing_item["updated_at"] = datetime.now().timestamp()
    
    # Update retrospective timestamp
    retro["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated item {item_id} in retrospective {retro_id}")
    
    return {
        "status": "success",
        "message": "Retrospective item updated successfully",
        "data": existing_item
    }


@router.post("/{retro_id}/finalize", response_model=StandardResponse)
async def finalize_retrospective(retro_id: str = Path(..., description="ID of the retrospective")):
    """
    Finalize a retrospective.
    
    Args:
        retro_id: ID of the retrospective
        
    Returns:
        Finalized retrospective
    """
    # Check if retrospective exists
    if retro_id not in retrospectives_db:
        raise HTTPException(status_code=404, detail=f"Retrospective {retro_id} not found")
    
    # Check if retrospective is already completed
    if retrospectives_db[retro_id]["status"] == "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Retrospective {retro_id} is already completed"
        )
    
    # Finalize retrospective (will be replaced with proper storage in future PRs)
    retro = retrospectives_db[retro_id]
    retro["status"] = "completed"
    
    # Update timestamp
    from datetime import datetime
    retro["updated_at"] = datetime.now().timestamp()
    
    # Also, in a real implementation, we might:
    # 1. Create improvement tickets
    # 2. Link to execution records
    # 3. Generate performance analysis
    
    logger.info(f"Finalized retrospective {retro_id}")
    
    return {
        "status": "success",
        "message": "Retrospective finalized successfully",
        "data": retro
    }


# ===== Enhanced Retrospective Management for Sprints =====

import json
from pathlib import Path as PathLib
from shared.env import TektonEnviron

# Get paths
METADATA_PATH = PathLib(TektonEnviron.get("TEKTON_ROOT", "/Users/cskoons/projects/github/Coder-C")) / "MetaData" / "DevelopmentSprints"
RETROSPECTIVES_PATH = METADATA_PATH / "Retrospectives"


@architecture_decision(
    title="Epimetheus Retrospective System",
    description="Dual-nature planning with Prometheus (forward) and Epimetheus (retrospective)",
    rationale="Learn from past sprints to improve future planning through structured retrospectives",
    alternatives_considered=["Separate retrospective component", "Post-mortem only approach", "No retrospectives"],
    impacts=["continuous_improvement", "team_learning", "sprint_quality"],
    decided_by="Casey",
    decision_date="2025-01-26"
)
class _RetrospectiveArchitecture:
    """Marker class for retrospective architecture decision"""
    pass


def create_retrospective_template(sprint_name: str, completed_date: str = None) -> Dict[str, Any]:
    """Create a retrospective template for a sprint"""
    if completed_date is None:
        completed_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "sprintName": sprint_name,
        "completedDate": completed_date,
        "teamMembers": {
            "prometheus": {
                "feedback": "",
                "recommendations": []
            },
            "metis": {
                "feedback": "",
                "recommendations": []
            },
            "harmonia": {
                "feedback": "",
                "recommendations": []
            },
            "synthesis": {
                "feedback": "",
                "recommendations": []
            },
            "tektonCore": {
                "feedback": "",
                "recommendations": []
            }
        },
        "whatWentWell": [],
        "whatCouldImprove": [],
        "actionItems": [],
        "followUpSprintNeeded": False,
        "teamChatTranscript": ""
    }


@router.post("/sprints/{sprint_name}/create", response_model=StandardResponse)
@api_contract(
    title="Create Sprint Retrospective",
    description="Creates retrospective document for completed sprints",
    endpoint="/api/v1/retrospectives/sprints/{sprint_name}/create",
    method="POST",
    request_schema={"teamMembers": "object", "whatWentWell": "array", "actionItems": "array"},
    response_schema={"status": "string", "data": "object"},
    performance_requirements="<300ms file creation"
)
@integration_point(
    title="Sprint Retrospective Creation",
    description="Creates retrospective JSON files linked to completed sprints",
    target_component="File System",
    protocol="file_io",
    data_flow="Sprint completion → Create retrospective template → Save to Retrospectives folder",
    integration_date="2025-07-28"
)
async def create_sprint_retrospective(
    sprint_name: str,
    retrospective_data: Optional[Dict[str, Any]] = Body(None)
):
    """Create a retrospective for a completed sprint"""
    try:
        # Ensure retrospectives directory exists
        RETROSPECTIVES_PATH.mkdir(parents=True, exist_ok=True)
        
        # Create retrospective file path
        retro_file = RETROSPECTIVES_PATH / f"{sprint_name}_retrospective.json"
        
        # Check if retrospective already exists
        if retro_file.exists() and retrospective_data is None:
            raise HTTPException(status_code=409, detail=f"Retrospective for {sprint_name} already exists")
        
        # Create retrospective data
        if retrospective_data is None:
            retrospective_data = create_retrospective_template(sprint_name)
        else:
            # Merge with template to ensure all fields exist
            template = create_retrospective_template(sprint_name)
            template.update(retrospective_data)
            retrospective_data = template
        
        # Save retrospective
        with open(retro_file, 'w') as f:
            json.dump(retrospective_data, f, indent=2)
        
        logger.info(f"Created retrospective for sprint {sprint_name}")
        
        return {
            "status": "success",
            "message": f"Retrospective created for sprint {sprint_name}",
            "data": retrospective_data
        }
    except Exception as e:
        logger.error(f"Error creating retrospective: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sprints/{sprint_name}/retrospective", response_model=StandardResponse)
async def get_sprint_retrospective(sprint_name: str):
    """Get retrospective for a sprint"""
    try:
        retro_file = RETROSPECTIVES_PATH / f"{sprint_name}_retrospective.json"
        
        if not retro_file.exists():
            raise HTTPException(status_code=404, detail=f"No retrospective found for sprint {sprint_name}")
        
        with open(retro_file, 'r') as f:
            retrospective_data = json.load(f)
        
        return {
            "status": "success",
            "message": f"Retrospective retrieved for sprint {sprint_name}",
            "data": retrospective_data
        }
    except Exception as e:
        logger.error(f"Error getting retrospective: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sprints/{sprint_name}/retrospective", response_model=StandardResponse)
async def update_sprint_retrospective(
    sprint_name: str,
    updates: Dict[str, Any] = Body(...)
):
    """Update retrospective for a sprint"""
    try:
        retro_file = RETROSPECTIVES_PATH / f"{sprint_name}_retrospective.json"
        
        if not retro_file.exists():
            raise HTTPException(status_code=404, detail=f"No retrospective found for sprint {sprint_name}")
        
        # Load existing retrospective
        with open(retro_file, 'r') as f:
            retrospective_data = json.load(f)
        
        # Update fields
        retrospective_data.update(updates)
        retrospective_data["lastUpdated"] = datetime.now().isoformat()
        
        # Save updated retrospective
        with open(retro_file, 'w') as f:
            json.dump(retrospective_data, f, indent=2)
        
        logger.info(f"Updated retrospective for sprint {sprint_name}")
        
        return {
            "status": "success",
            "message": f"Retrospective updated for sprint {sprint_name}",
            "data": retrospective_data
        }
    except Exception as e:
        logger.error(f"Error updating retrospective: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sprints/{sprint_name}/retrospective/capture-chat", response_model=StandardResponse)
async def capture_team_chat(
    sprint_name: str,
    chat_data: Dict[str, str] = Body(..., example={"transcript": "Team chat conversation..."})
):
    """Capture Team Chat transcript for retrospective"""
    try:
        retro_file = RETROSPECTIVES_PATH / f"{sprint_name}_retrospective.json"
        
        if not retro_file.exists():
            # Create retrospective if it doesn't exist
            retrospective_data = create_retrospective_template(sprint_name)
        else:
            with open(retro_file, 'r') as f:
                retrospective_data = json.load(f)
        
        # Update team chat transcript
        retrospective_data["teamChatTranscript"] = chat_data.get("transcript", "")
        retrospective_data["chatCapturedAt"] = datetime.now().isoformat()
        
        # Save updated retrospective
        with open(retro_file, 'w') as f:
            json.dump(retrospective_data, f, indent=2)
        
        logger.info(f"Captured team chat for sprint {sprint_name} retrospective")
        
        return {
            "status": "success",
            "message": f"Team chat captured for sprint {sprint_name}",
            "data": {"chatLength": len(chat_data.get("transcript", ""))}
        }
    except Exception as e:
        logger.error(f"Error capturing team chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sprints/list-retrospectives", response_model=StandardResponse)
async def list_sprint_retrospectives():
    """List all sprint retrospectives"""
    try:
        retrospectives = []
        
        if RETROSPECTIVES_PATH.exists():
            for retro_file in RETROSPECTIVES_PATH.glob("*_retrospective.json"):
                try:
                    with open(retro_file, 'r') as f:
                        retro_data = json.load(f)
                        retrospectives.append({
                            "sprintName": retro_data.get("sprintName", retro_file.stem.replace("_retrospective", "")),
                            "completedDate": retro_data.get("completedDate", ""),
                            "hasTeamChat": bool(retro_data.get("teamChatTranscript", "")),
                            "actionItemCount": len(retro_data.get("actionItems", [])),
                            "filePath": str(retro_file)
                        })
                except Exception as e:
                    logger.error(f"Error reading retrospective file {retro_file}: {e}")
        
        # Sort by completed date descending
        retrospectives.sort(key=lambda x: x["completedDate"], reverse=True)
        
        return {
            "status": "success",
            "message": f"Found {len(retrospectives)} retrospectives",
            "data": retrospectives
        }
    except Exception as e:
        logger.error(f"Error listing retrospectives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-manual", response_model=StandardResponse)
@api_contract(
    title="Create Manual Retrospective",
    description="Creates ad-hoc retrospectives outside of sprint completion flow",
    endpoint="/api/v1/retrospectives/create-manual",
    method="POST",
    request_schema={"purpose": "string", "participants": ["string"], "scope": "string"},
    response_schema={"status": "string", "data": "object"},
    performance_requirements="<200ms file creation"
)
@state_checkpoint(
    title="Manual Retrospective State",
    description="Tracks non-sprint retrospectives for process improvements",
    state_type="file",
    persistence=True,
    consistency_requirements="Unique naming prevents conflicts",
    recovery_strategy="Scan Retrospectives folder for manual_* files"
)
async def create_manual_retrospective(
    retrospective_request: Dict[str, Any] = Body(..., example={
        "purpose": "Mid-sprint checkpoint",
        "participants": ["prometheus", "metis"],
        "scope": "Planning Team Process Improvement"
    })
):
    """Create a manual retrospective for any purpose"""
    try:
        # Generate unique name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        purpose_slug = retrospective_request.get("purpose", "manual").lower().replace(" ", "_")[:30]
        retro_name = f"manual_{purpose_slug}_{timestamp}"
        
        # Create retrospective data
        retrospective_data = {
            "name": retro_name,
            "purpose": retrospective_request.get("purpose", "Manual Retrospective"),
            "type": "manual",
            "createdDate": datetime.now().isoformat(),
            "participants": retrospective_request.get("participants", []),
            "scope": retrospective_request.get("scope", ""),
            "discussion": {
                "topics": [],
                "insights": [],
                "actionItems": []
            },
            "teamChatTranscript": ""
        }
        
        # Save retrospective
        RETROSPECTIVES_PATH.mkdir(parents=True, exist_ok=True)
        retro_file = RETROSPECTIVES_PATH / f"{retro_name}.json"
        
        with open(retro_file, 'w') as f:
            json.dump(retrospective_data, f, indent=2)
        
        logger.info(f"Created manual retrospective: {retro_name}")
        
        return {
            "status": "success",
            "message": "Manual retrospective created",
            "data": retrospective_data
        }
    except Exception as e:
        logger.error(f"Error creating manual retrospective: {e}")
        raise HTTPException(status_code=500, detail=str(e))