"""
History Endpoints

This module defines the API endpoints for execution history in the Prometheus/Epimethius Planning System.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.retrospective import (
    ExecutionRecordCreate, ExecutionRecordUpdate,
    TaskExecutionUpdate, MilestoneExecutionUpdate, 
    ExecutionIssueCreate, ExecutionIssueUpdate,
    VarianceAnalysisRequest
)
from ..models.shared import StandardResponse, PaginatedResponse


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.history")

# Create router
router = APIRouter(prefix="/history", tags=["history"])


# Placeholder for execution record storage (will be replaced with proper storage in future PRs)
execution_records_db = {}


# Endpoints
@router.get("/", response_model=PaginatedResponse)
async def list_execution_records(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    plan_id: Optional[str] = Query(None, description="Filter by plan ID"),
    sort_by: Optional[str] = Query("record_date", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """
    List all execution records with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        plan_id: Filter by plan ID
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Paginated list of execution records
    """
    # Get all execution records (will be replaced with proper storage in future PRs)
    all_records = list(execution_records_db.values())
    
    # Apply filters
    if plan_id:
        all_records = [r for r in all_records if r.get("plan_id") == plan_id]
    
    # Calculate pagination
    total_items = len(all_records)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Sort records
    if sort_by:
        reverse = sort_order.lower() == "desc"
        all_records.sort(key=lambda r: r.get(sort_by, ""), reverse=reverse)
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    paginated_records = all_records[start_idx:end_idx]
    
    return {
        "status": "success",
        "message": f"Retrieved {len(paginated_records)} execution records",
        "data": paginated_records,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }


@router.post("/{plan_id}", response_model=StandardResponse)
async def create_execution_record(
    record: ExecutionRecordCreate,
    plan_id: str = Path(..., description="ID of the plan")
):
    """
    Create a new execution record for a plan.
    
    Args:
        plan_id: ID of the plan
        record: Execution record creation data
        
    Returns:
        Created execution record
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if plan_id matches
    if record.plan_id != plan_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Plan ID in path ({plan_id}) does not match plan ID in body ({record.plan_id})"
        )
    
    # Generate record_id
    from datetime import datetime
    import uuid
    
    record_id = f"record-{uuid.uuid4()}"
    
    # Process issues
    issues_encountered = []
    if record.issues_encountered:
        for issue_data in record.issues_encountered:
            issue_id = f"issue-{uuid.uuid4()}"
            issues_encountered.append({
                "issue_id": issue_id,
                "title": issue_data.title,
                "description": issue_data.description,
                "severity": issue_data.severity,
                "related_task_ids": issue_data.related_task_ids or [],
                "status": "open",
                "resolution": None,
                "reported_by": issue_data.reported_by,
                "reported_date": issue_data.reported_date.isoformat() if issue_data.reported_date else datetime.now().isoformat(),
                "resolved_date": None,
                "metadata": issue_data.metadata or {},
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
    
    # Create the execution record (will be replaced with proper storage in future PRs)
    new_record = {
        "record_id": record_id,
        "plan_id": plan_id,
        "record_date": record.record_date.isoformat() if record.record_date else datetime.now().isoformat(),
        "task_records": record.task_records or {},
        "milestone_records": record.milestone_records or {},
        "issues_encountered": issues_encountered,
        "metadata": record.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp()
    }
    
    execution_records_db[record_id] = new_record
    
    logger.info(f"Created execution record {record_id} for plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Execution record created successfully",
        "data": new_record
    }


@router.get("/{record_id}", response_model=StandardResponse)
async def get_execution_record(record_id: str = Path(..., description="ID of the execution record")):
    """
    Get a specific execution record.
    
    Args:
        record_id: ID of the execution record
        
    Returns:
        Execution record data
    """
    # Check if execution record exists
    if record_id not in execution_records_db:
        raise HTTPException(status_code=404, detail=f"Execution record {record_id} not found")
    
    return {
        "status": "success",
        "message": "Execution record retrieved successfully",
        "data": execution_records_db[record_id]
    }


@router.post("/{record_id}/update", response_model=StandardResponse)
async def update_execution_record(
    update: ExecutionRecordUpdate,
    record_id: str = Path(..., description="ID of the execution record")
):
    """
    Update an execution record.
    
    Args:
        record_id: ID of the execution record
        update: Execution record update data
        
    Returns:
        Updated execution record
    """
    # Check if execution record exists
    if record_id not in execution_records_db:
        raise HTTPException(status_code=404, detail=f"Execution record {record_id} not found")
    
    # Update execution record (will be replaced with proper storage in future PRs)
    record = execution_records_db[record_id]
    from datetime import datetime
    
    # Process task updates
    if update.task_updates:
        for task_update in update.task_updates:
            task_id = task_update.task_id
            
            # Create task record if it doesn't exist
            if "task_records" not in record:
                record["task_records"] = {}
                
            if task_id not in record["task_records"]:
                record["task_records"][task_id] = {
                    "task_id": task_id,
                    "status": "not_started",
                    "progress": 0.0,
                    "actual_start_date": None,
                    "actual_end_date": None,
                    "actual_effort": None,
                    "assigned_resources": [],
                    "blockers": [],
                    "notes": None,
                    "created_at": datetime.now().timestamp(),
                    "updated_at": datetime.now().timestamp(),
                    "status_history": [{
                        "status": "not_started",
                        "timestamp": datetime.now().timestamp(),
                        "progress": 0.0
                    }]
                }
            
            # Update task record
            task_record = record["task_records"][task_id]
            
            if task_update.status is not None:
                task_record["status"] = task_update.status
                # Add to status history
                task_record["status_history"].append({
                    "status": task_update.status,
                    "timestamp": datetime.now().timestamp(),
                    "progress": task_update.progress if task_update.progress is not None else task_record.get("progress", 0.0)
                })
                
            if task_update.progress is not None:
                task_record["progress"] = task_update.progress
                
            if task_update.actual_start_date is not None:
                task_record["actual_start_date"] = task_update.actual_start_date.isoformat()
                
            if task_update.actual_end_date is not None:
                task_record["actual_end_date"] = task_update.actual_end_date.isoformat()
                
            if task_update.actual_effort is not None:
                task_record["actual_effort"] = task_update.actual_effort
                
            if task_update.assigned_resources is not None:
                task_record["assigned_resources"] = task_update.assigned_resources
                
            if task_update.blockers is not None:
                task_record["blockers"] = task_update.blockers
                
            if task_update.notes is not None:
                task_record["notes"] = task_update.notes
                
            if task_update.metadata is not None:
                task_record["metadata"] = task_update.metadata
                
            task_record["updated_at"] = datetime.now().timestamp()
    
    # Process milestone updates
    if update.milestone_updates:
        for milestone_update in update.milestone_updates:
            milestone_id = milestone_update.milestone_id
            
            # Create milestone record if it doesn't exist
            if "milestone_records" not in record:
                record["milestone_records"] = {}
                
            if milestone_id not in record["milestone_records"]:
                record["milestone_records"][milestone_id] = {
                    "milestone_id": milestone_id,
                    "status": "not_started",
                    "actual_date": None,
                    "notes": None,
                    "created_at": datetime.now().timestamp(),
                    "updated_at": datetime.now().timestamp(),
                    "status_history": [{
                        "status": "not_started",
                        "timestamp": datetime.now().timestamp()
                    }]
                }
            
            # Update milestone record
            milestone_record = record["milestone_records"][milestone_id]
            
            if milestone_update.status is not None:
                milestone_record["status"] = milestone_update.status
                # Add to status history
                milestone_record["status_history"].append({
                    "status": milestone_update.status,
                    "timestamp": datetime.now().timestamp()
                })
                
            if milestone_update.actual_date is not None:
                milestone_record["actual_date"] = milestone_update.actual_date.isoformat()
                
            if milestone_update.notes is not None:
                milestone_record["notes"] = milestone_update.notes
                
            if milestone_update.metadata is not None:
                milestone_record["metadata"] = milestone_update.metadata
                
            milestone_record["updated_at"] = datetime.now().timestamp()
    
    # Process new issues
    if update.new_issues:
        if "issues_encountered" not in record:
            record["issues_encountered"] = []
            
        for issue_data in update.new_issues:
            issue_id = f"issue-{uuid.uuid4()}"
            record["issues_encountered"].append({
                "issue_id": issue_id,
                "title": issue_data.title,
                "description": issue_data.description,
                "severity": issue_data.severity,
                "related_task_ids": issue_data.related_task_ids or [],
                "status": "open",
                "resolution": None,
                "reported_by": issue_data.reported_by,
                "reported_date": issue_data.reported_date.isoformat() if issue_data.reported_date else datetime.now().isoformat(),
                "resolved_date": None,
                "metadata": issue_data.metadata or {},
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
    
    # Process issue updates
    if update.issue_updates:
        if "issues_encountered" not in record:
            record["issues_encountered"] = []
            
        for issue_update in update.issue_updates:
            # Find the issue
            issue_index = None
            for i, issue in enumerate(record["issues_encountered"]):
                if issue["issue_id"] == issue_update.issue_id:
                    issue_index = i
                    break
                    
            if issue_index is not None:
                issue = record["issues_encountered"][issue_index]
                
                if issue_update.title is not None:
                    issue["title"] = issue_update.title
                    
                if issue_update.description is not None:
                    issue["description"] = issue_update.description
                    
                if issue_update.severity is not None:
                    issue["severity"] = issue_update.severity
                    
                if issue_update.status is not None:
                    issue["status"] = issue_update.status
                    
                if issue_update.resolution is not None:
                    issue["resolution"] = issue_update.resolution
                    
                if issue_update.related_task_ids is not None:
                    issue["related_task_ids"] = issue_update.related_task_ids
                    
                if issue_update.resolved_date is not None:
                    issue["resolved_date"] = issue_update.resolved_date.isoformat()
                    
                if issue_update.metadata is not None:
                    issue["metadata"] = issue_update.metadata
                    
                issue["updated_at"] = datetime.now().timestamp()
    
    # Update metadata if provided
    if update.metadata is not None:
        record["metadata"] = update.metadata
    
    # Update timestamp
    record["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated execution record {record_id}")
    
    return {
        "status": "success",
        "message": "Execution record updated successfully",
        "data": record
    }


@router.get("/{plan_id}/variance", response_model=StandardResponse)
async def get_variance_analysis(
    plan_id: str = Path(..., description="ID of the plan"),
    record_id: Optional[str] = Query(None, description="ID of the execution record"),
    metrics: Optional[List[str]] = Query(None, description="Metrics to include"),
    analysis_level: Optional[str] = Query("detailed", description="Level of analysis", 
                                       pattern="^(summary|detailed|comprehensive)$")
):
    """
    Get variance analysis between plan and actual execution.
    
    Args:
        plan_id: ID of the plan
        record_id: Optional ID of a specific execution record
        metrics: Optional list of metrics to include
        analysis_level: Level of analysis detail
        
    Returns:
        Variance analysis
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Get plan
    plan = plans_db[plan_id]
    
    # Get execution records for the plan
    plan_records = [r for r in execution_records_db.values() if r["plan_id"] == plan_id]
    
    if record_id:
        if record_id not in execution_records_db:
            raise HTTPException(status_code=404, detail=f"Execution record {record_id} not found")
        if execution_records_db[record_id]["plan_id"] != plan_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Execution record {record_id} is not for plan {plan_id}"
            )
        plan_records = [execution_records_db[record_id]]
    
    if not plan_records:
        return {
            "status": "success",
            "message": "No execution records found for variance analysis",
            "data": {
                "plan_id": plan_id,
                "analysis_level": analysis_level,
                "metrics": metrics,
                "variance": {}
            }
        }
    
    # Select the record to use (in a real implementation, we might use multiple records or the latest one)
    record = plan_records[-1]  # Using the latest record
    
    # Calculate variance (placeholder implementation)
    variance = {
        "plan_id": plan_id,
        "record_id": record["record_id"],
        "record_date": record["record_date"],
        "overall_completion": 0.0,
        "task_completion": {},
        "milestone_achievement": {},
        "effort_variance": {},
        "schedule_variance": {}
    }
    
    # Calculate task completion variance
    total_progress = 0.0
    task_count = 0
    
    for task_id, task in plan["tasks"].items():
        if "task_records" in record and task_id in record["task_records"]:
            task_record = record["task_records"][task_id]
            
            # Add task variance
            variance["task_completion"][task_id] = {
                "name": task["name"],
                "planned_status": task.get("status", "not_started"),
                "actual_status": task_record["status"],
                "planned_progress": task.get("progress", 0.0),
                "actual_progress": task_record["progress"],
                "variance": task_record["progress"] - task.get("progress", 0.0)
            }
            
            # Add to overall completion
            total_progress += task_record["progress"]
            task_count += 1
            
            # Add effort variance if available
            if "actual_effort" in task_record and task_record["actual_effort"] is not None:
                effort_variance = task_record["actual_effort"] - task.get("estimated_effort", 0.0)
                variance["effort_variance"][task_id] = {
                    "name": task["name"],
                    "planned_effort": task.get("estimated_effort", 0.0),
                    "actual_effort": task_record["actual_effort"],
                    "variance": effort_variance,
                    "variance_percentage": (effort_variance / task.get("estimated_effort", 1.0)) * 100 if task.get("estimated_effort", 0.0) > 0 else 0.0
                }
                
            # Add schedule variance if dates are available
            if task.get("start_date") and task_record.get("actual_start_date"):
                import datetime
                
                # Parse dates
                planned_start = datetime.datetime.fromisoformat(task["start_date"].replace("Z", "+00:00"))
                actual_start = datetime.datetime.fromisoformat(task_record["actual_start_date"].replace("Z", "+00:00"))
                
                start_variance_days = (actual_start - planned_start).days
                
                # Check end dates too
                end_variance_days = None
                if task.get("end_date") and task_record.get("actual_end_date"):
                    planned_end = datetime.datetime.fromisoformat(task["end_date"].replace("Z", "+00:00"))
                    actual_end = datetime.datetime.fromisoformat(task_record["actual_end_date"].replace("Z", "+00:00"))
                    end_variance_days = (actual_end - planned_end).days
                
                variance["schedule_variance"][task_id] = {
                    "name": task["name"],
                    "planned_start": task.get("start_date"),
                    "actual_start": task_record.get("actual_start_date"),
                    "start_variance_days": start_variance_days,
                    "planned_end": task.get("end_date"),
                    "actual_end": task_record.get("actual_end_date"),
                    "end_variance_days": end_variance_days
                }
    
    # Calculate overall completion
    if task_count > 0:
        variance["overall_completion"] = total_progress / task_count
    
    # Calculate milestone achievement variance
    for milestone in plan["milestones"]:
        milestone_id = milestone["milestone_id"]
        if "milestone_records" in record and milestone_id in record["milestone_records"]:
            milestone_record = record["milestone_records"][milestone_id]
            
            # Add milestone variance
            variance["milestone_achievement"][milestone_id] = {
                "name": milestone["name"],
                "planned_date": milestone.get("target_date"),
                "actual_date": milestone_record.get("actual_date"),
                "planned_status": milestone.get("status", "not_started"),
                "actual_status": milestone_record["status"]
            }
            
            # Add date variance if dates are available
            if milestone.get("target_date") and milestone_record.get("actual_date"):
                import datetime
                
                # Parse dates
                planned_date = datetime.datetime.fromisoformat(milestone["target_date"].replace("Z", "+00:00"))
                actual_date = datetime.datetime.fromisoformat(milestone_record["actual_date"].replace("Z", "+00:00"))
                
                variance["milestone_achievement"][milestone_id]["date_variance_days"] = (actual_date - planned_date).days
    
    # Filter metrics if specified
    if metrics:
        filtered_variance = {"plan_id": plan_id, "record_id": record["record_id"], "overall_completion": variance["overall_completion"]}
        for metric in metrics:
            if metric in variance:
                filtered_variance[metric] = variance[metric]
        variance = filtered_variance
    
    # Adjust level of detail based on analysis_level
    if analysis_level == "summary":
        # Provide just summary information
        summary_variance = {
            "plan_id": plan_id,
            "record_id": record["record_id"],
            "record_date": record["record_date"],
            "overall_completion": variance["overall_completion"],
            "task_count": task_count,
            "completed_tasks": sum(1 for task in variance["task_completion"].values() if task["actual_status"] == "completed"),
            "average_progress": variance["overall_completion"] * 100,
            "milestones_completed": sum(1 for m in variance["milestone_achievement"].values() if m["actual_status"] == "completed"),
            "milestones_total": len(variance["milestone_achievement"]),
            "average_effort_variance": sum(e["variance_percentage"] for e in variance["effort_variance"].values()) / len(variance["effort_variance"]) if variance["effort_variance"] else 0
        }
        variance = summary_variance
    
    return {
        "status": "success",
        "message": "Variance analysis retrieved successfully",
        "data": {
            "plan_id": plan_id,
            "analysis_level": analysis_level,
            "metrics": metrics,
            "variance": variance
        }
    }