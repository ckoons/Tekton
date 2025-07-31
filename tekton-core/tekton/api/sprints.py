"""
TektonCore Sprint Management API

REST API endpoints for development sprint coordination:
- Sprint status monitoring
- Coder assignment management  
- Branch and merge coordination
- Conflict resolution workflow
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

from shared.utils.logging_setup import setup_component_logging

# Import landmarks for API documentation
try:
    from landmarks import (
        api_contract,
        integration_point
    )
except ImportError:
    # Landmarks not available, define no-op decorators
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = setup_component_logging("tekton_core.api.sprints")

# Global sprint coordinator instance (will be set by main app)
sprint_coordinator = None

def set_sprint_coordinator(coordinator):
    """Set the sprint coordinator instance"""
    global sprint_coordinator
    sprint_coordinator = coordinator

# Pydantic models for API requests/responses
class SprintAssignmentRequest(BaseModel):
    """Request to manually assign sprint to Coder"""
    sprint_name: str = Field(..., description="Name of the development sprint")
    coder_id: str = Field(..., description="Coder identifier (A, B, or C)")

class MergeConflictResolution(BaseModel):
    """Request to resolve merge conflict"""
    merge_id: str = Field(..., description="Merge request identifier")
    action: str = Field(..., description="Resolution action: approve, reject, or reset")
    reason: Optional[str] = Field(None, description="Reason for the resolution")

class CreateTestSprintRequest(BaseModel):
    """Request to create test sprint"""
    sprint_name: str = Field(..., description="Test sprint name")
    coder_id: str = Field(..., description="Coder to assign (A, B, or C)")

class DryRunMergeRequest(BaseModel):
    """Request to perform dry-run merge"""
    merge_id: str = Field(..., description="Merge identifier")
    merge_name: str = Field(..., description="Sprint name being merged")

class FixMergeRequest(BaseModel):
    """Request to fix merge conflicts with AI"""
    merge_id: str = Field(..., description="Merge identifier")
    merge_name: str = Field(..., description="Sprint name being merged")
    conflict_data: Dict[str, Any] = Field(..., description="Conflict information")

class ConsultCoderRequest(BaseModel):
    """Request to consult original Coder"""
    merge_id: str = Field(..., description="Merge identifier")
    merge_name: str = Field(..., description="Sprint name being merged")
    conflict_data: Dict[str, Any] = Field(..., description="Conflict information")

class RedoSprintRequest(BaseModel):
    """Request to redo sprint with new Coder"""
    merge_id: str = Field(..., description="Merge identifier")
    merge_name: str = Field(..., description="Sprint name to redo")
    new_coder: Optional[str] = Field(None, description="New Coder assignment (A, B, or C)")

# Create router
router = APIRouter(prefix="/api/v1/sprints", tags=["Sprint Management"])

@api_contract(
    title="Sprint Status API",
    endpoint="/sprints/status",
    method="GET",
    request_schema={"sprint_name": "Optional[str]"},
    response_schema={"sprints": "List[Dict]", "summary": "Dict"},
    description="Get status of all development sprints or specific sprint"
)
@router.get("/status")
async def get_sprint_status(sprint_name: Optional[str] = None):
    """Get development sprint status"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        status_data = sprint_coordinator.get_sprint_status(sprint_name)
        
        if "error" in status_data:
            raise HTTPException(status_code=404, detail=status_data["error"])
        
        return {
            "success": True,
            "data": status_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sprint status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Sprint Assignment API",
    endpoint="/sprints/assign",
    method="POST", 
    request_schema={"sprint_name": "str", "coder_id": "str"},
    response_schema={"success": "bool", "message": "str"},
    description="Manually assign development sprint to specific Coder"
)
@router.post("/assign")
async def assign_sprint(request: SprintAssignmentRequest):
    """Manually assign sprint to Coder"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        success = await sprint_coordinator.assign_sprint_to_coder(
            sprint_name=request.sprint_name,
            coder_id=request.coder_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Sprint {request.sprint_name} assigned to Coder-{request.coder_id}",
                "sprint_name": request.sprint_name,
                "coder_id": request.coder_id
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to assign sprint {request.sprint_name} to Coder-{request.coder_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Coder Status API",
    endpoint="/sprints/coders",
    method="GET",
    request_schema={},
    response_schema={"coders": "Dict", "assignment_queue": "List[str]"},
    description="Get status and availability of all Coders"
)
@router.get("/coders")
async def get_coder_status():
    """Get Coder status and assignments"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        coder_data = sprint_coordinator.get_coder_status()
        
        return {
            "success": True,
            "data": coder_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get coder status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Merge Status API", 
    endpoint="/sprints/merges",
    method="GET",
    request_schema={},
    response_schema={"merge_queue": "Dict", "statistics": "Dict"},
    description="Get merge coordination status and statistics"
)
@router.get("/debug")
async def debug_sprint_coordinator():
    """Debug endpoint to check sprint coordinator status"""
    return {
        "sprint_coordinator_is_none": sprint_coordinator is None,
        "sprint_coordinator_type": str(type(sprint_coordinator)) if sprint_coordinator else "None",
        "sprint_coordinator_id": id(sprint_coordinator) if sprint_coordinator else "None"
    }

@router.get("/merges")
async def get_merge_status():
    """Get merge coordination status"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        merge_data = sprint_coordinator.get_merge_status()
        
        return {
            "success": True,
            "data": merge_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get merge status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Merge Conflict Resolution API",
    endpoint="/sprints/resolve-conflict",
    method="POST",
    request_schema={"merge_id": "str", "action": "str", "reason": "Optional[str]"},
    response_schema={"success": "bool", "message": "str"},
    description="Resolve merge conflict with human decision (approve/reject/reset)"
)
@router.post("/resolve-conflict")
async def resolve_merge_conflict(request: MergeConflictResolution):
    """Resolve merge conflict with human decision"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    if request.action not in ["approve", "reject", "reset"]:
        raise HTTPException(
            status_code=400, 
            detail="Action must be one of: approve, reject, reset"
        )
    
    try:
        success = await sprint_coordinator.resolve_merge_conflict(
            merge_id=request.merge_id,
            action=request.action,
            reason=request.reason or ""
        )
        
        if success:
            return {
                "success": True,
                "message": f"Merge conflict {request.merge_id} resolved with action: {request.action}",
                "merge_id": request.merge_id,
                "action": request.action
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Merge request {request.merge_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve merge conflict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Merge Retry API",
    endpoint="/sprints/retry-merge/{merge_id}",
    method="POST",
    request_schema={"merge_id": "str"},
    response_schema={"success": "bool", "message": "str"},
    description="Retry a failed merge request"
)
@router.post("/retry-merge/{merge_id}")
async def retry_merge(merge_id: str):
    """Retry a failed merge request"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        success = await sprint_coordinator.retry_failed_merge(merge_id)
        
        if success:
            return {
                "success": True,
                "message": f"Merge request {merge_id} queued for retry",
                "merge_id": merge_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Merge request {merge_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retry merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="System Status API",
    endpoint="/sprints/system",
    method="GET",
    request_schema={},
    response_schema={"coordinator": "Dict", "components": "Dict"},
    description="Get comprehensive sprint coordination system status"
)
@router.get("/system")
async def get_system_status():
    """Get comprehensive sprint system status"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        system_data = sprint_coordinator.get_system_status()
        
        return {
            "success": True,
            "data": system_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Development and testing endpoints

@router.post("/test/create-sprint")
async def create_test_sprint(request: CreateTestSprintRequest):
    """Create test sprint for development/testing"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        success = await sprint_coordinator.create_test_sprint(
            sprint_name=request.sprint_name,
            coder_id=request.coder_id
        )
        
        if success:
            return {
                "success": True,
                "message": f"Test sprint {request.sprint_name} created and assigned to Coder-{request.coder_id}",
                "sprint_name": request.sprint_name,
                "coder_id": request.coder_id
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create test sprint {request.sprint_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create test sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug")
async def get_debug_info():
    """Get detailed debug information (development only)"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        debug_data = sprint_coordinator.get_debug_info()
        
        return {
            "success": True,
            "data": debug_data,
            "timestamp": datetime.now().isoformat(),
            "warning": "This endpoint contains sensitive debug information"
        }
        
    except Exception as e:
        logger.error(f"Failed to get debug info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@integration_point(
    title="Sprint Status Monitoring Integration",
    target_component="dev_sprint_monitor",
    protocol="background_tasks",
    data_flow="API → background task → DAILY_LOG.md monitoring",
    description="Provides real-time sprint status updates via background monitoring"
)
@router.get("/status/stream")
async def stream_sprint_status(background_tasks: BackgroundTasks):
    """Stream real-time sprint status updates (for future WebSocket implementation)"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    # For now, return current status
    # TODO: Implement WebSocket streaming for real-time updates
    try:
        status_data = sprint_coordinator.get_sprint_status()
        
        return {
            "success": True,
            "data": status_data,
            "streaming": False,
            "message": "Real-time streaming not yet implemented - use polling",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get streaming status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New merge workflow endpoints

@api_contract(
    title="Dry-Run Merge API",
    endpoint="/sprints/merge/dry-run",
    method="POST",
    request_schema={"merge_id": "str", "merge_name": "str"},
    response_schema={"success": "bool", "conflicts": "List[Dict]", "can_merge": "bool"},
    description="Perform dry-run merge to check for conflicts"
)
@router.post("/merge/dry-run")
async def dry_run_merge(request: DryRunMergeRequest):
    """Perform dry-run merge to check for conflicts"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        # Simulate dry-run merge
        await asyncio.sleep(1)  # Simulate processing
        
        # For now, return mock data
        # TODO: Implement actual git merge --no-commit logic
        return {
            "success": True,
            "merge_id": request.merge_id,
            "merge_name": request.merge_name,
            "can_merge": False,
            "conflicts": [
                {
                    "file": "src/main.py",
                    "line": 42,
                    "type": "content",
                    "description": "Both branches modified this function"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to perform dry-run merge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Fix Merge Conflicts API",
    endpoint="/sprints/merge/fix",
    method="POST",
    request_schema={"merge_id": "str", "merge_name": "str", "conflict_data": "Dict"},
    response_schema={"success": "bool", "resolution": "Dict", "message": "str"},
    description="Use AI to fix merge conflicts"
)
@router.post("/merge/fix")
async def fix_merge_conflicts(request: FixMergeRequest):
    """Use AI to fix merge conflicts"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        # Simulate AI conflict resolution
        await asyncio.sleep(2)  # Simulate AI processing
        
        # TODO: Implement actual AI-powered conflict resolution
        return {
            "success": True,
            "merge_id": request.merge_id,
            "merge_name": request.merge_name,
            "resolution": {
                "files_fixed": 1,
                "strategy": "AI-powered resolution",
                "confidence": 0.95
            },
            "message": "Conflicts resolved using AI assistance",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to fix merge conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Consult Coder API",
    endpoint="/sprints/merge/consult",
    method="POST",
    request_schema={"merge_id": "str", "merge_name": "str", "conflict_data": "Dict"},
    response_schema={"success": "bool", "consultation": "Dict", "message": "str"},
    description="Consult original Coder for conflict resolution"
)
@router.post("/merge/consult")
async def consult_coder(request: ConsultCoderRequest):
    """Consult original Coder for conflict resolution"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        # Simulate Coder consultation
        await asyncio.sleep(1.5)  # Simulate consultation
        
        # TODO: Implement actual Coder consultation logic
        return {
            "success": True,
            "merge_id": request.merge_id,
            "merge_name": request.merge_name,
            "consultation": {
                "coder": "Coder-A",
                "response": "Recommend accepting incoming changes for function X",
                "confidence": "high"
            },
            "message": "Coder consultation completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to consult Coder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_contract(
    title="Redo Sprint API",
    endpoint="/sprints/merge/redo",
    method="POST",
    request_schema={"merge_id": "str", "merge_name": "str", "new_coder": "Optional[str]"},
    response_schema={"success": "bool", "new_sprint": "Dict", "message": "str"},
    description="Redo sprint with new Coder assignment"
)
@router.post("/merge/redo")
async def redo_sprint(request: RedoSprintRequest):
    """Redo sprint with new Coder assignment"""
    
    if not sprint_coordinator:
        raise HTTPException(status_code=503, detail="Sprint coordinator not initialized")
    
    try:
        # Simulate sprint redo
        await asyncio.sleep(2)  # Simulate processing
        
        new_coder = request.new_coder or "B"  # Default to Coder-B if not specified
        
        # TODO: Implement actual sprint redo logic
        return {
            "success": True,
            "merge_id": request.merge_id,
            "new_sprint": {
                "name": f"{request.merge_name}_REDO",
                "coder": f"Coder-{new_coder}",
                "status": "Assigned",
                "created": datetime.now().isoformat()
            },
            "message": f"Sprint reassigned to Coder-{new_coder} for redo",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to redo sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))