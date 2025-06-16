"""
Improvement Endpoints

This module defines the API endpoints for improvements in the Prometheus/Epimethius Planning System.
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from ..models.improvement import (
    ImprovementCreate, ImprovementUpdate, ImprovementStatusUpdate,
    ImprovementPatternCreate, ImprovementPatternUpdate,
    ImprovementSuggestionRequest, ImprovementProgressRequest,
    LLMImprovementSuggestion, LLMRootCauseAnalysis
)
from ..models.shared import StandardResponse, PaginatedResponse


# Configure logging
logger = logging.getLogger("prometheus.api.endpoints.improvement")

# Create router
router = APIRouter(prefix="/improvements", tags=["improvements"])


# Placeholder for improvement storage (will be replaced with proper storage in future PRs)
improvements_db = {}
patterns_db = {}


# Endpoints
@router.get("/", response_model=PaginatedResponse)
async def list_improvements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    source: Optional[str] = Query(None, description="Filter by source"),
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """
    List all improvements with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Filter by status
        priority: Filter by priority
        source: Filter by source
        source_id: Filter by source ID
        tag: Filter by tag
        assignee: Filter by assignee
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Paginated list of improvements
    """
    # Get all improvements (will be replaced with proper storage in future PRs)
    all_improvements = list(improvements_db.values())
    
    # Apply filters
    if status:
        all_improvements = [i for i in all_improvements if i.get("status") == status]
    if priority:
        all_improvements = [i for i in all_improvements if i.get("priority") == priority]
    if source:
        all_improvements = [i for i in all_improvements if i.get("source") == source]
    if source_id:
        all_improvements = [i for i in all_improvements if i.get("source_id") == source_id]
    if tag:
        all_improvements = [i for i in all_improvements if tag in i.get("tags", [])]
    if assignee:
        all_improvements = [i for i in all_improvements if assignee in i.get("assignees", [])]
    
    # Calculate pagination
    total_items = len(all_improvements)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Sort improvements
    if sort_by:
        reverse = sort_order.lower() == "desc"
        all_improvements.sort(key=lambda i: i.get(sort_by, ""), reverse=reverse)
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    paginated_improvements = all_improvements[start_idx:end_idx]
    
    return {
        "status": "success",
        "message": f"Retrieved {len(paginated_improvements)} improvements",
        "data": paginated_improvements,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }


@router.post("/", response_model=StandardResponse)
async def create_improvement(improvement: ImprovementCreate):
    """
    Create a new improvement.
    
    Args:
        improvement: Improvement creation data
        
    Returns:
        Created improvement
    """
    # Generate improvement_id
    from datetime import datetime
    import uuid
    
    improvement_id = f"improvement-{uuid.uuid4()}"
    
    # Create the improvement (will be replaced with proper storage in future PRs)
    new_improvement = {
        "improvement_id": improvement_id,
        "title": improvement.title,
        "description": improvement.description,
        "source": improvement.source,
        "source_id": improvement.source_id,
        "priority": improvement.priority,
        "status": "open",
        "assignees": improvement.assignees or [],
        "due_date": improvement.due_date.isoformat() if improvement.due_date else None,
        "implementation_plan": improvement.implementation_plan,
        "verification_criteria": improvement.verification_criteria,
        "tags": improvement.tags or [],
        "metadata": improvement.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp(),
        "implemented_at": None,
        "verified_at": None,
        "status_history": [
            {
                "status": "open",
                "timestamp": datetime.now().timestamp(),
                "comment": "Initial status"
            }
        ]
    }
    
    improvements_db[improvement_id] = new_improvement
    
    logger.info(f"Created improvement {improvement_id}: {improvement.title}")
    
    return {
        "status": "success",
        "message": "Improvement created successfully",
        "data": new_improvement
    }


@router.get("/{improvement_id}", response_model=StandardResponse)
async def get_improvement(improvement_id: str = Path(..., description="ID of the improvement")):
    """
    Get a specific improvement.
    
    Args:
        improvement_id: ID of the improvement
        
    Returns:
        Improvement data
    """
    # Check if improvement exists
    if improvement_id not in improvements_db:
        raise HTTPException(status_code=404, detail=f"Improvement {improvement_id} not found")
    
    return {
        "status": "success",
        "message": "Improvement retrieved successfully",
        "data": improvements_db[improvement_id]
    }


@router.put("/{improvement_id}", response_model=StandardResponse)
async def update_improvement(
    improvement: ImprovementUpdate,
    improvement_id: str = Path(..., description="ID of the improvement")
):
    """
    Update an improvement.
    
    Args:
        improvement_id: ID of the improvement
        improvement: Improvement update data
        
    Returns:
        Updated improvement
    """
    # Check if improvement exists
    if improvement_id not in improvements_db:
        raise HTTPException(status_code=404, detail=f"Improvement {improvement_id} not found")
    
    # Update improvement (will be replaced with proper storage in future PRs)
    existing_improvement = improvements_db[improvement_id]
    
    # Apply updates
    if improvement.title is not None:
        existing_improvement["title"] = improvement.title
    if improvement.description is not None:
        existing_improvement["description"] = improvement.description
    if improvement.priority is not None:
        existing_improvement["priority"] = improvement.priority
    if improvement.status is not None:
        old_status = existing_improvement["status"]
        existing_improvement["status"] = improvement.status
        
        # Add to status history
        from datetime import datetime
        existing_improvement["status_history"].append({
            "status": improvement.status,
            "timestamp": datetime.now().timestamp(),
            "comment": "Status updated"
        })
        
        # Update implemented_at and verified_at
        if improvement.status == "implemented" and old_status != "implemented":
            existing_improvement["implemented_at"] = datetime.now().timestamp()
        if improvement.status == "verified" and old_status != "verified":
            existing_improvement["verified_at"] = datetime.now().timestamp()
            
    if improvement.assignees is not None:
        existing_improvement["assignees"] = improvement.assignees
    if improvement.due_date is not None:
        existing_improvement["due_date"] = improvement.due_date.isoformat()
    if improvement.implementation_plan is not None:
        existing_improvement["implementation_plan"] = improvement.implementation_plan
    if improvement.verification_criteria is not None:
        existing_improvement["verification_criteria"] = improvement.verification_criteria
    if improvement.tags is not None:
        existing_improvement["tags"] = improvement.tags
    if improvement.metadata is not None:
        existing_improvement["metadata"] = improvement.metadata
    
    # Update timestamp
    from datetime import datetime
    existing_improvement["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated improvement {improvement_id}")
    
    return {
        "status": "success",
        "message": "Improvement updated successfully",
        "data": existing_improvement
    }


@router.put("/{improvement_id}/status", response_model=StandardResponse)
async def update_improvement_status(
    status_update: ImprovementStatusUpdate,
    improvement_id: str = Path(..., description="ID of the improvement")
):
    """
    Update the status of an improvement.
    
    Args:
        improvement_id: ID of the improvement
        status_update: Status update data
        
    Returns:
        Updated improvement
    """
    # Check if improvement exists
    if improvement_id not in improvements_db:
        raise HTTPException(status_code=404, detail=f"Improvement {improvement_id} not found")
    
    # Update improvement status (will be replaced with proper storage in future PRs)
    existing_improvement = improvements_db[improvement_id]
    
    # Get old status
    old_status = existing_improvement["status"]
    
    # Update status
    existing_improvement["status"] = status_update.status
    
    # Add to status history
    from datetime import datetime
    existing_improvement["status_history"].append({
        "status": status_update.status,
        "timestamp": datetime.now().timestamp(),
        "comment": status_update.comment or f"Status updated to {status_update.status}"
    })
    
    # Update implemented_at and verified_at
    if status_update.status == "implemented" and old_status != "implemented":
        existing_improvement["implemented_at"] = datetime.now().timestamp()
    if status_update.status == "verified" and old_status != "verified":
        existing_improvement["verified_at"] = datetime.now().timestamp()
    
    # Update timestamp
    existing_improvement["updated_at"] = datetime.now().timestamp()
    
    logger.info(f"Updated status of improvement {improvement_id} to {status_update.status}")
    
    return {
        "status": "success",
        "message": "Improvement status updated successfully",
        "data": existing_improvement
    }


@router.delete("/{improvement_id}", response_model=StandardResponse)
async def delete_improvement(improvement_id: str = Path(..., description="ID of the improvement")):
    """
    Delete an improvement.
    
    Args:
        improvement_id: ID of the improvement
        
    Returns:
        Deletion confirmation
    """
    # Check if improvement exists
    if improvement_id not in improvements_db:
        raise HTTPException(status_code=404, detail=f"Improvement {improvement_id} not found")
    
    # Delete improvement (will be replaced with proper storage in future PRs)
    deleted_improvement = improvements_db.pop(improvement_id)
    
    logger.info(f"Deleted improvement {improvement_id}")
    
    return {
        "status": "success",
        "message": "Improvement deleted successfully",
        "data": {"improvement_id": improvement_id}
    }


@router.get("/patterns", response_model=PaginatedResponse)
async def list_improvement_patterns(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    min_frequency: Optional[int] = Query(None, description="Filter by minimum frequency"),
    sort_by: Optional[str] = Query("frequency", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """
    List all improvement patterns with pagination and filtering.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        category: Filter by category
        tag: Filter by tag
        min_frequency: Filter by minimum frequency
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Paginated list of improvement patterns
    """
    # Get all patterns (will be replaced with proper storage in future PRs)
    all_patterns = list(patterns_db.values())
    
    # Apply filters
    if category:
        all_patterns = [p for p in all_patterns if p.get("category") == category]
    if tag:
        all_patterns = [p for p in all_patterns if tag in p.get("tags", [])]
    if min_frequency:
        all_patterns = [p for p in all_patterns if p.get("frequency", 0) >= min_frequency]
    
    # Calculate pagination
    total_items = len(all_patterns)
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 1
    
    # Sort patterns
    if sort_by:
        reverse = sort_order.lower() == "desc"
        all_patterns.sort(key=lambda p: p.get(sort_by, ""), reverse=reverse)
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    paginated_patterns = all_patterns[start_idx:end_idx]
    
    return {
        "status": "success",
        "message": f"Retrieved {len(paginated_patterns)} improvement patterns",
        "data": paginated_patterns,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages
    }


@router.post("/patterns", response_model=StandardResponse)
async def create_improvement_pattern(pattern: ImprovementPatternCreate):
    """
    Create a new improvement pattern.
    
    Args:
        pattern: Improvement pattern creation data
        
    Returns:
        Created improvement pattern
    """
    # Generate pattern_id
    from datetime import datetime
    import uuid
    
    pattern_id = f"pattern-{uuid.uuid4()}"
    
    # Create the improvement pattern (will be replaced with proper storage in future PRs)
    new_pattern = {
        "pattern_id": pattern_id,
        "name": pattern.name,
        "description": pattern.description,
        "category": pattern.category,
        "frequency": 1,
        "related_improvements": pattern.related_improvements or [],
        "suggested_actions": pattern.suggested_actions or [],
        "tags": pattern.tags or [],
        "metadata": pattern.metadata or {},
        "created_at": datetime.now().timestamp(),
        "updated_at": datetime.now().timestamp()
    }
    
    patterns_db[pattern_id] = new_pattern
    
    logger.info(f"Created improvement pattern {pattern_id}: {pattern.name}")
    
    return {
        "status": "success",
        "message": "Improvement pattern created successfully",
        "data": new_pattern
    }


@router.get("/suggestions", response_model=StandardResponse)
async def get_improvement_suggestions(
    source_type: str = Query(..., description="Type of source for suggestions"),
    source_id: Optional[str] = Query(None, description="ID of the source"),
    limit: int = Query(5, ge=1, description="Maximum number of suggestions")
):
    """
    Get improvement suggestions.
    
    Args:
        source_type: Type of source for suggestions
        source_id: Optional ID of the source
        limit: Maximum number of suggestions
        
    Returns:
        List of improvement suggestions
    """
    # Get source data
    source_data = None
    
    if source_type == "retrospective":
        # Check if retrospective exists
        from .retrospective import retrospectives_db
        if not source_id or source_id not in retrospectives_db:
            raise HTTPException(status_code=404, detail=f"Retrospective {source_id} not found")
        source_data = retrospectives_db[source_id]
        
    elif source_type == "performance":
        # This would check performance data (placeholder)
        pass
        
    elif source_type == "pattern":
        # Check if pattern exists
        if not source_id or source_id not in patterns_db:
            raise HTTPException(status_code=404, detail=f"Improvement pattern {source_id} not found")
        source_data = patterns_db[source_id]
        
    elif source_type == "history":
        # Check if execution record exists
        from .history import execution_records_db
        if not source_id or source_id not in execution_records_db:
            raise HTTPException(status_code=404, detail=f"Execution record {source_id} not found")
        source_data = execution_records_db[source_id]
    
    # Generate suggestions (placeholder implementation)
    suggestions = []
    
    # For retrospectives, generate suggestions from action items
    if source_type == "retrospective" and source_data:
        for i, action_item in enumerate(source_data.get("action_items", [])):
            if i >= limit:
                break
                
            suggestions.append({
                "title": f"Implement: {action_item['title']}",
                "description": action_item['description'],
                "source": "retrospective",
                "source_id": source_id,
                "priority": action_item.get("priority", "medium"),
                "suggested_assignees": action_item.get("assignees", []),
                "implementation_plan": None,
                "verification_criteria": None,
                "confidence": 0.9,
                "metadata": {
                    "action_item_id": action_item.get("action_id")
                }
            })
    
    # For patterns, generate suggestions from the pattern
    elif source_type == "pattern" and source_data:
        for i, action in enumerate(source_data.get("suggested_actions", [])):
            if i >= limit:
                break
                
            suggestions.append({
                "title": f"Apply pattern: {action}",
                "description": f"Implement the action from pattern '{source_data['name']}': {action}",
                "source": "pattern",
                "source_id": source_id,
                "priority": "medium",
                "suggested_assignees": [],
                "implementation_plan": None,
                "verification_criteria": None,
                "confidence": 0.8,
                "metadata": {
                    "pattern_id": source_id,
                    "pattern_name": source_data.get("name"),
                    "pattern_category": source_data.get("category")
                }
            })
    
    # Add some placeholder suggestions if we don't have enough
    while len(suggestions) < limit:
        suggestions.append({
            "title": f"Generic improvement {len(suggestions) + 1}",
            "description": "This is a placeholder improvement suggestion",
            "source": source_type,
            "source_id": source_id,
            "priority": "medium",
            "suggested_assignees": [],
            "implementation_plan": "Implement this improvement",
            "verification_criteria": "Verify this improvement",
            "confidence": 0.5,
            "metadata": {}
        })
    
    return {
        "status": "success",
        "message": f"Retrieved {len(suggestions)} improvement suggestions",
        "data": suggestions
    }


@router.get("/progress", response_model=StandardResponse)
async def get_improvement_progress(
    source_type: Optional[str] = Query(None, description="Type of source for improvements"),
    source_id: Optional[str] = Query(None, description="ID of the source"),
    status: Optional[List[str]] = Query(None, description="Statuses to include"),
    start_date: Optional[str] = Query(None, description="Start date for the progress (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date for the progress (ISO format)"),
    group_by: Optional[str] = Query(None, description="Group by dimension")
):
    """
    Get improvement progress.
    
    Args:
        source_type: Optional type of source for improvements
        source_id: Optional ID of the source
        status: Optional list of statuses to include
        start_date: Optional start date for the progress (ISO format)
        end_date: Optional end date for the progress (ISO format)
        group_by: Optional dimension to group by
        
    Returns:
        Improvement progress data
    """
    # Get improvements (will be replaced with proper storage in future PRs)
    all_improvements = list(improvements_db.values())
    
    # Apply filters
    if source_type:
        all_improvements = [i for i in all_improvements if i.get("source") == source_type]
    if source_id:
        all_improvements = [i for i in all_improvements if i.get("source_id") == source_id]
    if status:
        all_improvements = [i for i in all_improvements if i.get("status") in status]
    # Apply time range filter if provided
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
        
        # Filter by date range
        if start_timestamp:
            all_improvements = [
                i for i in all_improvements 
                if i.get("created_at", 0) >= start_timestamp
            ]
            
        if end_timestamp:
            all_improvements = [
                i for i in all_improvements 
                if i.get("created_at", 0) <= end_timestamp
            ]
    
    # Calculate progress metrics
    total_count = len(all_improvements)
    status_counts = {}
    for imp in all_improvements:
        status = imp.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate grouping if requested
    grouped_data = {}
    if group_by:
        if group_by == "status":
            for imp in all_improvements:
                status = imp.get("status", "unknown")
                if status not in grouped_data:
                    grouped_data[status] = []
                grouped_data[status].append(imp)
                
        elif group_by == "priority":
            for imp in all_improvements:
                priority = imp.get("priority", "unknown")
                if priority not in grouped_data:
                    grouped_data[priority] = []
                grouped_data[priority].append(imp)
                
        elif group_by == "source":
            for imp in all_improvements:
                source = imp.get("source", "unknown")
                if source not in grouped_data:
                    grouped_data[source] = []
                grouped_data[source].append(imp)
                
        elif group_by == "assignee":
            for imp in all_improvements:
                if not imp.get("assignees"):
                    assignee = "unassigned"
                    if assignee not in grouped_data:
                        grouped_data[assignee] = []
                    grouped_data[assignee].append(imp)
                else:
                    for assignee in imp.get("assignees", []):
                        if assignee not in grouped_data:
                            grouped_data[assignee] = []
                        grouped_data[assignee].append(imp)
                        
        elif group_by == "tag":
            for imp in all_improvements:
                if not imp.get("tags"):
                    tag = "untagged"
                    if tag not in grouped_data:
                        grouped_data[tag] = []
                    grouped_data[tag].append(imp)
                else:
                    for tag in imp.get("tags", []):
                        if tag not in grouped_data:
                            grouped_data[tag] = []
                        grouped_data[tag].append(imp)
    
    # Calculate completion rate
    completed_count = status_counts.get("verified", 0) + status_counts.get("implemented", 0)
    completion_rate = (completed_count / total_count) if total_count > 0 else 0
    
    # Create progress data
    progress_data = {
        "total_count": total_count,
        "status_counts": status_counts,
        "completion_rate": completion_rate,
        "grouped_data": {
            group: {
                "count": len(items),
                "status_counts": {
                    status: sum(1 for i in items if i.get("status") == status)
                    for status in set(i.get("status", "unknown") for i in items)
                },
                "completion_rate": (
                    sum(1 for i in items if i.get("status") in ["verified", "implemented"]) / len(items)
                ) if len(items) > 0 else 0
            }
            for group, items in grouped_data.items()
        } if group_by else None
    }
    
    return {
        "status": "success",
        "message": "Improvement progress retrieved successfully",
        "data": progress_data
    }