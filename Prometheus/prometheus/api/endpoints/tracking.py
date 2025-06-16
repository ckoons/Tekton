"""
Tracking Endpoints

This module defines the API endpoints for project tracking in the Prometheus/Epimethius Planning System.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.shared import (
    TrackingUpdate, TrackingRequest,
    BurndownRequest, TrackingMetricsRequest
)
from ..models.shared import StandardResponse, PaginatedResponse


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.tracking")

# Create router
router = APIRouter(prefix="/tracking", tags=["tracking"])


# Endpoints
@router.get("/{plan_id}", response_model=StandardResponse)
async def get_tracking_data(
    plan_id: str = Path(..., description="ID of the plan"),
    include_tasks: bool = Query(True, description="Whether to include tasks"),
    include_milestones: bool = Query(True, description="Whether to include milestones"),
    include_issues: bool = Query(True, description="Whether to include issues"),
    include_history: bool = Query(False, description="Whether to include history")
):
    """
    Get tracking data for a plan.
    
    Args:
        plan_id: ID of the plan
        include_tasks: Whether to include tasks
        include_milestones: Whether to include milestones
        include_issues: Whether to include issues
        include_history: Whether to include history
        
    Returns:
        Tracking data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Get plan
    plan = plans_db[plan_id]
    
    # Get execution records for the plan
    from .history import execution_records_db
    plan_records = [r for r in execution_records_db.values() if r["plan_id"] == plan_id]
    plan_record = plan_records[-1] if plan_records else None
    
    # Build tracking data
    tracking_data = {
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "start_date": plan["start_date"],
        "end_date": plan["end_date"],
        "methodology": plan["methodology"],
        "overall_progress": 0.0,
        "status": "not_started"
    }
    
    # Include tasks if requested
    if include_tasks:
        tracking_data["tasks"] = {}
        
        # Calculate task progress
        total_progress = 0.0
        task_count = 0
        completed_count = 0
        
        for task_id, task in plan["tasks"].items():
            task_progress = task.get("progress", 0.0)
            task_status = task.get("status", "not_started")
            
            # Update from execution record if available
            if plan_record and "task_records" in plan_record and task_id in plan_record["task_records"]:
                task_record = plan_record["task_records"][task_id]
                task_progress = task_record.get("progress", task_progress)
                task_status = task_record.get("status", task_status)
            
            # Add task to tracking data
            tracking_data["tasks"][task_id] = {
                "name": task["name"],
                "status": task_status,
                "progress": task_progress,
                "priority": task.get("priority", "medium"),
                "start_date": task.get("start_date"),
                "end_date": task.get("end_date"),
                "assigned_resources": task.get("assigned_resources", [])
            }
            
            # Update progress calculation
            total_progress += task_progress
            task_count += 1
            if task_status == "completed":
                completed_count += 1
        
        # Calculate overall progress
        if task_count > 0:
            tracking_data["overall_progress"] = total_progress / task_count
            
            # Determine overall status
            if completed_count == task_count:
                tracking_data["status"] = "completed"
            elif completed_count > 0 or total_progress > 0:
                tracking_data["status"] = "in_progress"
            else:
                tracking_data["status"] = "not_started"
    
    # Include milestones if requested
    if include_milestones:
        tracking_data["milestones"] = {}
        
        for milestone in plan["milestones"]:
            milestone_id = milestone["milestone_id"]
            milestone_status = milestone.get("status", "not_started")
            
            # Update from execution record if available
            if plan_record and "milestone_records" in plan_record and milestone_id in plan_record["milestone_records"]:
                milestone_record = plan_record["milestone_records"][milestone_id]
                milestone_status = milestone_record.get("status", milestone_status)
            
            # Add milestone to tracking data
            tracking_data["milestones"][milestone_id] = {
                "name": milestone["name"],
                "status": milestone_status,
                "target_date": milestone.get("target_date"),
                "actual_date": milestone_record.get("actual_date") if plan_record and "milestone_records" in plan_record and milestone_id in plan_record["milestone_records"] else None,
                "criteria": milestone.get("criteria", [])
            }
    
    # Include issues if requested
    if include_issues:
        tracking_data["issues"] = []
        
        # Get issues from execution records
        for record in plan_records:
            for issue in record.get("issues_encountered", []):
                tracking_data["issues"].append({
                    "issue_id": issue["issue_id"],
                    "title": issue["title"],
                    "severity": issue["severity"],
                    "status": issue["status"],
                    "reported_date": issue["reported_date"],
                    "related_task_ids": issue.get("related_task_ids", [])
                })
    
    # Include history if requested
    if include_history:
        tracking_data["history"] = []
        
        # Add history entries from execution records
        for record in plan_records:
            tracking_data["history"].append({
                "record_id": record["record_id"],
                "record_date": record["record_date"],
                "overall_progress": sum(task.get("progress", 0.0) for task in record.get("task_records", {}).values()) / len(record.get("task_records", {})) if record.get("task_records") else 0.0,
                "completed_tasks": sum(1 for task in record.get("task_records", {}).values() if task.get("status") == "completed"),
                "total_tasks": len(record.get("task_records", {})),
                "issues_count": len(record.get("issues_encountered", []))
            })
    
    return {
        "status": "success",
        "message": "Tracking data retrieved successfully",
        "data": tracking_data
    }


@router.post("/{plan_id}/update", response_model=StandardResponse)
async def update_tracking(
    update: TrackingUpdate,
    plan_id: str = Path(..., description="ID of the plan")
):
    """
    Update tracking data for a plan.
    
    Args:
        plan_id: ID of the plan
        update: Tracking update data
        
    Returns:
        Updated tracking data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Check if plan_id matches
    if update.plan_id != plan_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Plan ID in path ({plan_id}) does not match plan ID in body ({update.plan_id})"
        )
    
    # Check if execution record exists or create a new one
    from .history import execution_records_db
    import uuid
    from datetime import datetime
    
    # Get timestamp
    timestamp = update.timestamp.isoformat() if update.timestamp else datetime.now().isoformat()
    
    # Find or create record for this update
    plan_records = [r for r in execution_records_db.values() if r["plan_id"] == plan_id]
    record = None
    
    if plan_records:
        # Use the latest record
        record = plan_records[-1]
    else:
        # Create a new record
        record_id = f"record-{uuid.uuid4()}"
        record = {
            "record_id": record_id,
            "plan_id": plan_id,
            "record_date": timestamp,
            "task_records": {},
            "milestone_records": {},
            "issues_encountered": [],
            "metadata": {},
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        }
        execution_records_db[record_id] = record
    
    # Process task updates
    if update.task_updates:
        for task_id, progress in update.task_updates.items():
            # Check if task exists
            if task_id not in plans_db[plan_id]["tasks"]:
                continue
                
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
            
            # Update progress
            task_record = record["task_records"][task_id]
            task_record["progress"] = progress
            
            # Update status based on progress
            if progress == 0.0:
                task_record["status"] = "not_started"
            elif progress == 1.0:
                task_record["status"] = "completed"
                if not task_record["actual_end_date"]:
                    task_record["actual_end_date"] = timestamp
            else:
                task_record["status"] = "in_progress"
                if not task_record["actual_start_date"]:
                    task_record["actual_start_date"] = timestamp
            
            # Add to status history
            task_record["status_history"].append({
                "status": task_record["status"],
                "timestamp": datetime.now().timestamp(),
                "progress": progress
            })
            
            task_record["updated_at"] = datetime.now().timestamp()
    
    # Process milestone updates
    if update.milestone_updates:
        for milestone_id, status in update.milestone_updates.items():
            # Find the milestone
            milestone_found = False
            for milestone in plans_db[plan_id]["milestones"]:
                if milestone["milestone_id"] == milestone_id:
                    milestone_found = True
                    break
                    
            if not milestone_found:
                continue
                
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
            
            # Update status
            milestone_record = record["milestone_records"][milestone_id]
            milestone_record["status"] = status
            
            # Set actual date if completed
            if status == "completed" and not milestone_record["actual_date"]:
                milestone_record["actual_date"] = timestamp
            
            # Add to status history
            milestone_record["status_history"].append({
                "status": status,
                "timestamp": datetime.now().timestamp()
            })
            
            milestone_record["updated_at"] = datetime.now().timestamp()
    
    # Process issues
    if update.issues:
        for issue_data in update.issues:
            issue_id = f"issue-{uuid.uuid4()}"
            
            record["issues_encountered"].append({
                "issue_id": issue_id,
                "title": issue_data.get("title", "Untitled Issue"),
                "description": issue_data.get("description", ""),
                "severity": issue_data.get("severity", "medium"),
                "related_task_ids": issue_data.get("related_task_ids", []),
                "status": "open",
                "resolution": None,
                "reported_by": issue_data.get("reported_by"),
                "reported_date": timestamp,
                "resolved_date": None,
                "metadata": issue_data.get("metadata", {}),
                "created_at": datetime.now().timestamp(),
                "updated_at": datetime.now().timestamp()
            })
    
    # Update notes
    if update.notes:
        record["notes"] = update.notes
    
    # Update metadata
    if update.metadata:
        record["metadata"].update(update.metadata)
    
    # Update record timestamp
    record["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated tracking data for plan {plan_id}")
    
    return {
        "status": "success",
        "message": "Tracking data updated successfully",
        "data": {
            "plan_id": plan_id,
            "record_id": record["record_id"],
            "record_date": record["record_date"]
        }
    }


@router.get("/{plan_id}/burndown", response_model=StandardResponse)
async def get_burndown_chart(
    plan_id: str = Path(..., description="ID of the plan"),
    chart_type: str = Query("burndown", description="Type of chart", 
                         pattern="^(burndown|burnup)$"),
    scope: str = Query("all", description="Scope of the chart", 
                     pattern="^(all|tasks|effort)$"),
    time_scale: str = Query("daily", description="Time scale for the chart", 
                         pattern="^(daily|weekly|monthly)$"),
    include_ideal: bool = Query(True, description="Whether to include ideal line"),
    include_forecast: bool = Query(False, description="Whether to include forecast")
):
    """
    Get burndown chart data for a plan.
    
    Args:
        plan_id: ID of the plan
        chart_type: Type of chart (burndown or burnup)
        scope: Scope of the chart
        time_scale: Time scale for the chart
        include_ideal: Whether to include ideal line
        include_forecast: Whether to include forecast
        
    Returns:
        Burndown chart data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Get plan
    plan = plans_db[plan_id]
    
    # Get execution records for the plan
    from .history import execution_records_db
    plan_records = [r for r in execution_records_db.values() if r["plan_id"] == plan_id]
    
    # Generate dates array
    import datetime
    
    start_date = datetime.datetime.fromisoformat(plan["start_date"].replace("Z", "+00:00"))
    end_date = datetime.datetime.fromisoformat(plan["end_date"].replace("Z", "+00:00"))
    
    # Generate date points based on time_scale
    date_points = []
    current_date = start_date
    
    if time_scale == "daily":
        while current_date <= end_date:
            date_points.append(current_date)
            current_date += datetime.timedelta(days=1)
    elif time_scale == "weekly":
        while current_date <= end_date:
            date_points.append(current_date)
            current_date += datetime.timedelta(weeks=1)
    elif time_scale == "monthly":
        while current_date <= end_date:
            # Advance by roughly a month
            month = current_date.month + 1
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            current_date = current_date.replace(year=year, month=month, day=1)
            date_points.append(current_date)
    
    # Calculate total scope values based on scope parameter
    total_scope = 0
    if scope == "all" or scope == "tasks":
        total_scope = len(plan["tasks"])
    elif scope == "effort":
        total_scope = sum(task.get("estimated_effort", 0) for task in plan["tasks"].values())
    
    # Generate ideal line
    ideal_line = []
    if include_ideal:
        total_days = (end_date - start_date).days
        if total_days > 0:
            for i, date in enumerate(date_points):
                days_passed = (date - start_date).days
                progress_ratio = days_passed / total_days
                
                if chart_type == "burndown":
                    remaining = total_scope * (1 - progress_ratio)
                else:  # burnup
                    remaining = total_scope * progress_ratio
                    
                ideal_line.append({
                    "date": date.isoformat(),
                    "value": max(0, remaining)
                })
    
    # Generate actual line from execution records
    actual_line = []
    current_value = total_scope if chart_type == "burndown" else 0
    
    for date in date_points:
        # Find records before or on this date
        relevant_records = [r for r in plan_records if datetime.datetime.fromisoformat(r["record_date"].replace("Z", "+00:00")) <= date]
        
        if relevant_records:
            # Use the latest record
            latest_record = sorted(relevant_records, key=lambda r: r["record_date"])[-1]
            
            if scope == "all" or scope == "tasks":
                completed_tasks = sum(1 for task in latest_record.get("task_records", {}).values() 
                                    if task.get("status") == "completed")
                
                if chart_type == "burndown":
                    current_value = total_scope - completed_tasks
                else:  # burnup
                    current_value = completed_tasks
            elif scope == "effort":
                remaining_effort = 0
                for task_id, task in plan["tasks"].items():
                    estimated_effort = task.get("estimated_effort", 0)
                    
                    if task_id in latest_record.get("task_records", {}):
                        task_record = latest_record["task_records"][task_id]
                        progress = task_record.get("progress", 0)
                        
                        if chart_type == "burndown":
                            remaining_effort += estimated_effort * (1 - progress)
                        else:  # burnup
                            remaining_effort += estimated_effort * progress
                    else:
                        # Task not started
                        if chart_type == "burndown":
                            remaining_effort += estimated_effort
                
                current_value = remaining_effort
        
        actual_line.append({
            "date": date.isoformat(),
            "value": current_value
        })
    
    # Generate forecast line
    forecast_line = []
    if include_forecast and actual_line:
        # Simple linear regression for forecasting
        # This is a very simplified approach; a real implementation would use more sophisticated methods
        
        # Get the last few data points
        last_points = actual_line[-min(len(actual_line), 5):]
        
        if len(last_points) >= 2:
            # Calculate average daily change
            first_point = last_points[0]
            last_point = last_points[-1]
            
            first_date = datetime.datetime.fromisoformat(first_point["date"].replace("Z", "+00:00"))
            last_date = datetime.datetime.fromisoformat(last_point["date"].replace("Z", "+00:00"))
            
            days_diff = max(1, (last_date - first_date).days)
            value_diff = last_point["value"] - first_point["value"]
            daily_change = value_diff / days_diff
            
            # Add forecast points
            current_date = last_date
            current_value = last_point["value"]
            
            # Generate forecast for at most 30 days
            for _ in range(30):
                if chart_type == "burndown" and current_value <= 0:
                    break
                if chart_type == "burnup" and current_value >= total_scope:
                    break
                    
                current_date += datetime.timedelta(days=1)
                if time_scale == "daily":
                    current_value += daily_change
                    forecast_line.append({
                        "date": current_date.isoformat(),
                        "value": max(0, min(total_scope, current_value))
                    })
                elif time_scale == "weekly" and current_date.weekday() == last_date.weekday():
                    current_value += daily_change * 7
                    forecast_line.append({
                        "date": current_date.isoformat(),
                        "value": max(0, min(total_scope, current_value))
                    })
                elif time_scale == "monthly" and current_date.day == last_date.day:
                    # Roughly a month's worth of daily change
                    current_value += daily_change * 30
                    forecast_line.append({
                        "date": current_date.isoformat(),
                        "value": max(0, min(total_scope, current_value))
                    })
    
    # Build chart data
    chart_data = {
        "plan_id": plan_id,
        "chart_type": chart_type,
        "scope": scope,
        "time_scale": time_scale,
        "total_scope": total_scope,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "ideal_line": ideal_line if include_ideal else None,
        "actual_line": actual_line,
        "forecast_line": forecast_line if include_forecast else None
    }
    
    return {
        "status": "success",
        "message": f"{chart_type.capitalize()} chart data retrieved successfully",
        "data": chart_data
    }


@router.get("/{plan_id}/metrics", response_model=StandardResponse)
async def get_tracking_metrics(
    plan_id: str = Path(..., description="ID of the plan"),
    metrics: List[str] = Query(..., description="Metrics to include"),
    start_date: Optional[str] = Query(None, description="Start date for metrics (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date for metrics (ISO format)"),
    group_by: Optional[str] = Query(None, description="Group by dimension")
):
    """
    Get tracking metrics for a plan.
    
    Args:
        plan_id: ID of the plan
        metrics: List of metrics to include
        start_date: Optional start date for metrics (ISO format)
        end_date: Optional end date for metrics (ISO format)
        group_by: Optional dimension to group by
        
    Returns:
        Tracking metrics data
    """
    # Check if plan exists
    from .planning import plans_db
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    # Get plan
    plan = plans_db[plan_id]
    
    # Get execution records for the plan
    from .history import execution_records_db
    plan_records = [r for r in execution_records_db.values() if r["plan_id"] == plan_id]
    
    # Apply time range filter if specified
    if start_date or end_date:
        from datetime import datetime
        
        # Convert dates from ISO format
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            try:
                start_timestamp = datetime.fromisoformat(start_date).timestamp()
            except ValueError:
                # Handle invalid date format
                pass
                
        if end_date:
            try:
                end_timestamp = datetime.fromisoformat(end_date).timestamp()
            except ValueError:
                # Handle invalid date format
                pass
        
        # Time range filtering will be implemented in future PRs
    
    # Calculate metrics
    metrics_data = {}
    
    for metric in metrics:
        if metric == "completion_rate":
            # Calculate overall completion rate
            if not plan_records:
                metrics_data[metric] = 0.0
            else:
                latest_record = sorted(plan_records, key=lambda r: r["record_date"])[-1]
                task_records = latest_record.get("task_records", {})
                
                if not task_records:
                    metrics_data[metric] = 0.0
                else:
                    completed_tasks = sum(1 for task in task_records.values() if task.get("status") == "completed")
                    metrics_data[metric] = completed_tasks / len(task_records)
                    
        elif metric == "progress_over_time":
            # Calculate progress over time
            progress_points = []
            
            for record in sorted(plan_records, key=lambda r: r["record_date"]):
                task_records = record.get("task_records", {})
                
                if task_records:
                    avg_progress = sum(task.get("progress", 0.0) for task in task_records.values()) / len(task_records)
                    progress_points.append({
                        "date": record["record_date"],
                        "value": avg_progress
                    })
                    
            metrics_data[metric] = progress_points
            
        elif metric == "velocity":
            # Calculate velocity (tasks completed per day)
            if len(plan_records) >= 2:
                sorted_records = sorted(plan_records, key=lambda r: r["record_date"])
                first_record = sorted_records[0]
                last_record = sorted_records[-1]
                
                import datetime
                first_date = datetime.datetime.fromisoformat(first_record["record_date"].replace("Z", "+00:00"))
                last_date = datetime.datetime.fromisoformat(last_record["record_date"].replace("Z", "+00:00"))
                
                first_completed = sum(1 for task in first_record.get("task_records", {}).values() 
                                    if task.get("status") == "completed")
                last_completed = sum(1 for task in last_record.get("task_records", {}).values() 
                                   if task.get("status") == "completed")
                
                days_diff = max(1, (last_date - first_date).days)
                tasks_completed = last_completed - first_completed
                
                metrics_data[metric] = tasks_completed / days_diff
            else:
                metrics_data[metric] = 0.0
                
        elif metric == "effort_variance":
            # Calculate effort variance
            if not plan_records:
                metrics_data[metric] = 0.0
            else:
                latest_record = sorted(plan_records, key=lambda r: r["record_date"])[-1]
                
                total_variance = 0.0
                task_count = 0
                
                for task_id, task in plan["tasks"].items():
                    estimated_effort = task.get("estimated_effort", 0.0)
                    
                    if "task_records" in latest_record and task_id in latest_record["task_records"]:
                        task_record = latest_record["task_records"][task_id]
                        
                        if task_record.get("actual_effort") is not None:
                            actual_effort = task_record["actual_effort"]
                            variance = actual_effort - estimated_effort
                            total_variance += variance
                            task_count += 1
                
                metrics_data[metric] = total_variance / task_count if task_count > 0 else 0.0
                
        elif metric == "milestone_achievement":
            # Calculate milestone achievement rate
            milestone_metrics = {
                "total": len(plan["milestones"]),
                "completed": 0,
                "missed": 0,
                "on_time": 0,
                "late": 0
            }
            
            if plan_records:
                latest_record = sorted(plan_records, key=lambda r: r["record_date"])[-1]
                
                for milestone in plan["milestones"]:
                    milestone_id = milestone["milestone_id"]
                    
                    if "milestone_records" in latest_record and milestone_id in latest_record["milestone_records"]:
                        milestone_record = latest_record["milestone_records"][milestone_id]
                        
                        if milestone_record["status"] == "completed":
                            milestone_metrics["completed"] += 1
                            
                            # Check if completed on time
                            import datetime
                            target_date = datetime.datetime.fromisoformat(milestone["target_date"].replace("Z", "+00:00"))
                            actual_date = datetime.datetime.fromisoformat(milestone_record["actual_date"].replace("Z", "+00:00"))
                            
                            if actual_date <= target_date:
                                milestone_metrics["on_time"] += 1
                            else:
                                milestone_metrics["late"] += 1
                                
                        elif milestone_record["status"] == "missed":
                            milestone_metrics["missed"] += 1
            
            metrics_data[metric] = milestone_metrics
    
    # Apply grouping if requested
    if group_by:
        grouped_metrics = {}
        
        if group_by == "task":
            # Group by task
            for task_id, task in plan["tasks"].items():
                task_metrics = {}
                
                for metric in metrics:
                    # Calculate task-specific metrics
                    pass
                    
                grouped_metrics[task_id] = task_metrics
                
        elif group_by == "resource":
            # Group by resource
            resources = set()
            for task in plan["tasks"].values():
                resources.update(task.get("assigned_resources", []))
                
            for resource_id in resources:
                resource_metrics = {}
                
                for metric in metrics:
                    # Calculate resource-specific metrics
                    pass
                    
                grouped_metrics[resource_id] = resource_metrics
                
        elif group_by == "milestone":
            # Group by milestone
            for milestone in plan["milestones"]:
                milestone_id = milestone["milestone_id"]
                milestone_metrics = {}
                
                for metric in metrics:
                    # Calculate milestone-specific metrics
                    pass
                    
                grouped_metrics[milestone_id] = milestone_metrics
        
        # Add grouped metrics to the response
        metrics_data["grouped_by"] = group_by
        metrics_data["groups"] = grouped_metrics
    
    return {
        "status": "success",
        "message": "Tracking metrics retrieved successfully",
        "data": metrics_data
    }