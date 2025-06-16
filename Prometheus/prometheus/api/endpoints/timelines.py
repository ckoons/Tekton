"""
Timeline Endpoints

This module defines the API endpoints for timelines in the Prometheus/Epimethius Planning System.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.planning import TimelineCreate, TimelineUpdate, TimelineEntry
from ..models.shared import StandardResponse, PaginatedResponse


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.timelines")

# Create router
router = APIRouter(prefix="/plans/{plan_id}/timeline", tags=["timelines"])


# Placeholder for timeline storage (will be replaced with proper storage in future PRs)
timelines_db = {}


# Endpoints
@router.get("/", response_model=StandardResponse)
async def get_timeline(plan_id: str = Path(..., description="ID of the plan")):
    """
    Get the timeline for a plan.
    
    Args:
        plan_id: ID of the plan
        
    Returns:
        Timeline data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if timeline exists
    if plan_id not in timelines_db:
        # Create a new timeline if it doesn't exist
        from datetime import datetime
        import uuid
        
        timeline_id = f"timeline-{uuid.uuid4()}"
        timelines_db[plan_id] = {
            "timeline_id": timeline_id,
            "plan_id": plan_id,
            "entries": {},
            "critical_path": [],
            "metadata": {},
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp(),
            "version": 1
        }
    
    return {
        "status": "success",
        "message": "Timeline retrieved successfully",
        "data": timelines_db[plan_id]
    }


@router.post("/", response_model=StandardResponse)
async def create_timeline(
    timeline: TimelineCreate,
    plan_id: str = Path(..., description="ID of the plan")
):
    """
    Create a timeline for a plan.
    
    Args:
        plan_id: ID of the plan
        timeline: Timeline creation data
        
    Returns:
        Created timeline
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if plan_id matches
    if timeline.plan_id != plan_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Plan ID in path ({plan_id}) does not match plan ID in body ({timeline.plan_id})"
        )
    
    # Check if timeline already exists
    if plan_id in timelines_db:
        raise HTTPException(
            status_code=400, 
            detail=f"Timeline for plan {plan_id} already exists"
        )
    
    # Generate timeline_id
    from datetime import datetime
    import uuid
    
    timeline_id = f"timeline-{uuid.uuid4()}"
    
    # Process entries
    entries = {}
    for entry_data in timeline.entries:
        entry_id = f"entry-{uuid.uuid4()}"
        entries[entry_id] = {
            "entry_id": entry_id,
            "entity_id": entry_data.entity_id,
            "entity_type": entry_data.entity_type,
            "start_date": entry_data.start_date.isoformat(),
            "end_date": entry_data.end_date.isoformat(),
            "status": entry_data.status,
            "dependencies": entry_data.dependencies or [],
            "metadata": entry_data.metadata or {},
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        }
    
    # Create the timeline (will be replaced with proper storage in future PRs)
    new_timeline = {
        "timeline_id": timeline_id,
        "plan_id": plan_id,
        "entries": entries,
        "critical_path": [],  # Will be calculated
        "metadata": timeline.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp(),
        "version": 1
    }
    
    timelines_db[plan_id] = new_timeline
    
    # Update plan to reference the timeline
    plans_db[plan_id]["timeline_id"] = timeline_id
    plans_db[plan_id]["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Created timeline {timeline_id} for plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Timeline created successfully",
        "data": new_timeline
    }


@router.put("/", response_model=StandardResponse)
async def update_timeline(
    timeline: TimelineUpdate,
    plan_id: str = Path(..., description="ID of the plan")
):
    """
    Update the timeline for a plan.
    
    Args:
        plan_id: ID of the plan
        timeline: Timeline update data
        
    Returns:
        Updated timeline
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if timeline exists
    if plan_id not in timelines_db:
        raise HTTPException(status_code=404, detail=f"Timeline for plan {plan_id} not found")
    
    # Update timeline (will be replaced with proper storage in future PRs)
    existing_timeline = timelines_db[plan_id]
    
    # Process updates
    from datetime import datetime
    
    # Update entries if provided
    if timeline.entries is not None:
        # Dictionary to map entity IDs to existing entry IDs
        entity_to_entry = {
            f"{entry['entity_type']}:{entry['entity_id']}": entry_id
            for entry_id, entry in existing_timeline["entries"].items()
        }
        
        for entry_data in timeline.entries:
            # Check if an entry for this entity already exists
            entity_key = f"{entry_data.entity_type}:{entry_data.entity_id}"
            if entity_key in entity_to_entry:
                # Update existing entry
                entry_id = entity_to_entry[entity_key]
                existing_timeline["entries"][entry_id].update({
                    "start_date": entry_data.start_date.isoformat(),
                    "end_date": entry_data.end_date.isoformat(),
                    "status": entry_data.status,
                    "dependencies": entry_data.dependencies or [],
                    "metadata": entry_data.metadata or {},
                    "updated_at": datetime.now().timestamp()
                })
            else:
                # Create new entry
                entry_id = f"entry-{uuid.uuid4()}"
                existing_timeline["entries"][entry_id] = {
                    "entry_id": entry_id,
                    "entity_id": entry_data.entity_id,
                    "entity_type": entry_data.entity_type,
                    "start_date": entry_data.start_date.isoformat(),
                    "end_date": entry_data.end_date.isoformat(),
                    "status": entry_data.status,
                    "dependencies": entry_data.dependencies or [],
                    "metadata": entry_data.metadata or {},
                    "created_at": datetime.now().timestamp(),
                    "updated_at": datetime.now().timestamp()
                }
    
    # Remove entries if specified
    if timeline.entries_to_remove is not None:
        for entry_id in timeline.entries_to_remove:
            if entry_id in existing_timeline["entries"]:
                del existing_timeline["entries"][entry_id]
    
    # Add new entries if specified
    if timeline.entries_to_add is not None:
        for entry_data in timeline.entries_to_add:
            entry_id = f"entry-{uuid.uuid4()}"
            existing_timeline["entries"][entry_id] = {
                "entry_id": entry_id,
                "entity_id": entry_data.entity_id,
                "entity_type": entry_data.entity_type,
                "start_date": entry_data.start_date.isoformat(),
                "end_date": entry_data.end_date.isoformat(),
                "status": entry_data.status,
                "dependencies": entry_data.dependencies or [],
                "metadata": entry_data.metadata or {},
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            }
    
    # Update metadata if provided
    if timeline.metadata is not None:
        existing_timeline["metadata"] = timeline.metadata
    
    # Update version and timestamp
    existing_timeline["version"] += 1
    existing_timeline["updated_at"] = datetime.now().timestamp()
    
    # Update critical path (placeholder implementation)
    existing_timeline["critical_path"] = []
    
    logger.info(f"Updated timeline for plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Timeline updated successfully",
        "data": existing_timeline
    }


@router.get("/gantt", response_model=StandardResponse)
async def get_gantt_chart(
    plan_id: str = Path(..., description="ID of the plan"),
    include_resources: bool = Query(False, description="Include resource assignments"),
    include_dependencies: bool = Query(True, description="Include task dependencies"),
    highlight_critical_path: bool = Query(True, description="Highlight critical path")
):
    """
    Get Gantt chart data for a plan.
    
    Args:
        plan_id: ID of the plan
        include_resources: Whether to include resource assignments
        include_dependencies: Whether to include task dependencies
        highlight_critical_path: Whether to highlight the critical path
        
    Returns:
        Gantt chart data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if timeline exists
    if plan_id not in timelines_db:
        raise HTTPException(status_code=404, detail=f"Timeline for plan {plan_id} not found")
    
    # Get timeline
    timeline = timelines_db[plan_id]
    
    # Get plan
    plan = plans_db[plan_id]
    
    # Build Gantt chart data
    gantt_data = {
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "start_date": plan["start_date"],
        "end_date": plan["end_date"],
        "tasks": [],
        "milestones": [],
        "dependencies": [] if include_dependencies else None,
        "critical_path": timeline["critical_path"] if highlight_critical_path else None
    }
    
    # Process timeline entries
    for entry_id, entry in timeline["entries"].items():
        # Add task or milestone to Gantt chart
        if entry["entity_type"] == "task":
            task_id = entry["entity_id"]
            if task_id in plan["tasks"]:
                task = plan["tasks"][task_id]
                gantt_task = {
                    "id": task_id,
                    "name": task["name"],
                    "start_date": entry["start_date"],
                    "end_date": entry["end_date"],
                    "progress": task["progress"],
                    "status": task["status"],
                    "priority": task["priority"],
                    "is_critical": entry_id in timeline["critical_path"]
                }
                
                if include_resources:
                    gantt_task["resources"] = task["assigned_resources"]
                    
                gantt_data["tasks"].append(gantt_task)
                
                # Add dependencies
                if include_dependencies:
                    for dep_id in task.get("dependencies", []):
                        gantt_data["dependencies"].append({
                            "predecessor_id": dep_id,
                            "successor_id": task_id,
                            "type": "finish_to_start"
                        })
        elif entry["entity_type"] == "milestone":
            milestone_id = entry["entity_id"]
            for milestone in plan["milestones"]:
                if milestone["milestone_id"] == milestone_id:
                    gantt_data["milestones"].append({
                        "id": milestone_id,
                        "name": milestone["name"],
                        "date": entry["start_date"],  # Milestones have same start and end date
                        "status": milestone["status"],
                        "is_critical": entry_id in timeline["critical_path"]
                    })
                    break
    
    return {
        "status": "success",
        "message": "Gantt chart data retrieved successfully",
        "data": gantt_data
    }