"""
Sprint management endpoints for Prometheus UI.
Handles Development Sprint operations including listing, status updates, and file management.
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from shared.utils.logging_setup import get_logger
from shared.env import TektonEnviron

logger = get_logger(__name__)

# Router for sprint endpoints
router = APIRouter(prefix="/sprints", tags=["sprints"])

# Get MetaData path from environment
METADATA_PATH = Path(TektonEnviron.get("TEKTON_ROOT", "/Users/cskoons/projects/github/Coder-C")) / "MetaData" / "DevelopmentSprints"


class SprintStatus(BaseModel):
    """Sprint status model"""
    status: str = Field(..., description="Sprint status (Planning, Ready, Building, Complete, Superceded)")
    updated_by: str = Field(default="prometheus", description="Component that updated the status")
    notes: Optional[str] = Field(None, description="Optional notes about the status change")


class SprintMove(BaseModel):
    """Sprint move request model"""
    destination: str = Field(..., description="Destination folder (Superceded, Complete)")
    reason: Optional[str] = Field(None, description="Reason for moving the sprint")


class SprintDetails(BaseModel):
    """Sprint details model"""
    name: str
    status: str
    created: str
    modified: str
    description: Optional[str] = None
    phases: Optional[List[Dict]] = None
    requirements: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None
    coder_assignment: Optional[str] = None


class ResourceInfo(BaseModel):
    """Coder resource information"""
    name: str
    capacity: int = 3
    active: List[str] = []
    queue: List[str] = []


def read_daily_log(sprint_path: Path) -> Dict[str, Any]:
    """Read and parse DAILY_LOG.md file"""
    daily_log_path = sprint_path / "DAILY_LOG.md"
    if not daily_log_path.exists():
        return {"status": "Planning", "updated": datetime.now().isoformat()}
    
    try:
        content = daily_log_path.read_text()
        lines = content.strip().split('\n')
        
        status = "Planning"
        updated = datetime.now().isoformat()
        updated_by = "unknown"
        
        for line in lines:
            if line.startswith("## Sprint Status:"):
                status = line.replace("## Sprint Status:", "").strip()
            elif line.startswith("**Updated**:"):
                updated = line.replace("**Updated**:", "").strip()
            elif line.startswith("**Updated By**:"):
                updated_by = line.replace("**Updated By**:", "").strip()
        
        return {
            "status": status,
            "updated": updated,
            "updated_by": updated_by
        }
    except Exception as e:
        logger.error(f"Error reading DAILY_LOG.md: {e}")
        return {"status": "Unknown", "updated": datetime.now().isoformat()}


def write_daily_log(sprint_path: Path, status: str, updated_by: str = "prometheus", notes: str = ""):
    """Write status to DAILY_LOG.md file"""
    daily_log_path = sprint_path / "DAILY_LOG.md"
    
    # Read existing content to preserve history
    existing_content = ""
    if daily_log_path.exists():
        existing_content = daily_log_path.read_text()
    
    # Create new status entry
    timestamp = datetime.now().isoformat()
    new_entry = f"""## Sprint Status: {status}
**Updated**: {timestamp}
**Updated By**: {updated_by}

{notes}

---

"""
    
    # Prepend new entry to existing content
    updated_content = new_entry + existing_content
    
    # Write back to file
    daily_log_path.write_text(updated_content)
    logger.info(f"Updated DAILY_LOG.md for sprint at {sprint_path}")


def read_sprint_plan(sprint_path: Path) -> Dict[str, Any]:
    """Read and parse SPRINT_PLAN.md file"""
    sprint_plan_path = sprint_path / "SPRINT_PLAN.md"
    if not sprint_plan_path.exists():
        return {}
    
    try:
        content = sprint_plan_path.read_text()
        # Basic parsing - can be enhanced
        return {
            "content": content,
            "has_plan": True
        }
    except Exception as e:
        logger.error(f"Error reading SPRINT_PLAN.md: {e}")
        return {"has_plan": False}


def read_proposal_json(sprint_path: Path) -> Dict[str, Any]:
    """Read proposal.json file if it exists"""
    proposal_path = sprint_path / "proposal.json"
    if not proposal_path.exists():
        return {}
    
    try:
        with open(proposal_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading proposal.json: {e}")
        return {}


@router.get("/list", response_model=List[Dict[str, Any]])
async def list_sprints():
    """List all Development Sprint directories with their status"""
    try:
        sprints = []
        
        # Ensure the DevelopmentSprints directory exists
        if not METADATA_PATH.exists():
            logger.warning(f"DevelopmentSprints directory not found at {METADATA_PATH}")
            return []
        
        # Find all directories ending with _Sprint
        for item in METADATA_PATH.iterdir():
            if item.is_dir() and item.name.endswith("_Sprint"):
                # Read sprint information
                daily_log = read_daily_log(item)
                proposal = read_proposal_json(item)
                
                # Strip _Sprint suffix for display
                display_name = item.name.replace("_Sprint", "")
                
                sprint_info = {
                    "name": item.name,
                    "display_name": display_name,
                    "status": daily_log.get("status", "Planning"),
                    "updated": daily_log.get("updated"),
                    "updated_by": daily_log.get("updated_by", "unknown"),
                    "path": str(item),
                    "description": proposal.get("description", ""),
                    "purpose": proposal.get("purpose", ""),
                    "created": proposal.get("created", ""),
                    "coder_assignment": None  # Will be populated from resources
                }
                
                sprints.append(sprint_info)
        
        # Sort by status priority and then by name
        status_order = ["Building", "Ready", "Planning", "Complete", "Superceded"]
        sprints.sort(key=lambda x: (status_order.index(x["status"]) if x["status"] in status_order else 99, x["name"]))
        
        return sprints
    except Exception as e:
        logger.error(f"Error listing sprints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sprint_name}/status")
async def get_sprint_status(sprint_name: str):
    """Get the current status of a sprint"""
    try:
        sprint_path = METADATA_PATH / sprint_name
        if not sprint_path.exists():
            raise HTTPException(status_code=404, detail=f"Sprint {sprint_name} not found")
        
        daily_log = read_daily_log(sprint_path)
        return daily_log
    except Exception as e:
        logger.error(f"Error getting sprint status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{sprint_name}/status")
async def update_sprint_status(sprint_name: str, status_update: SprintStatus):
    """Update the status of a sprint in DAILY_LOG.md"""
    try:
        sprint_path = METADATA_PATH / sprint_name
        if not sprint_path.exists():
            raise HTTPException(status_code=404, detail=f"Sprint {sprint_name} not found")
        
        # Write new status to DAILY_LOG.md
        write_daily_log(
            sprint_path,
            status_update.status,
            status_update.updated_by,
            status_update.notes or ""
        )
        
        return {"message": f"Sprint {sprint_name} status updated to {status_update.status}"}
    except Exception as e:
        logger.error(f"Error updating sprint status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{sprint_name}/move")
async def move_sprint(sprint_name: str, move_request: SprintMove):
    """Move a sprint to Superceded or Complete folder"""
    try:
        sprint_path = METADATA_PATH / sprint_name
        if not sprint_path.exists():
            raise HTTPException(status_code=404, detail=f"Sprint {sprint_name} not found")
        
        # Create destination folder if it doesn't exist
        dest_folder = METADATA_PATH / move_request.destination
        dest_folder.mkdir(exist_ok=True)
        
        # Move the sprint directory
        dest_path = dest_folder / sprint_name
        if dest_path.exists():
            raise HTTPException(status_code=409, detail=f"Sprint already exists in {move_request.destination}")
        
        # Update status before moving
        write_daily_log(
            sprint_path,
            move_request.destination,
            "prometheus",
            f"Moved to {move_request.destination}: {move_request.reason or 'No reason provided'}"
        )
        
        # Move the directory
        shutil.move(str(sprint_path), str(dest_path))
        
        return {"message": f"Sprint {sprint_name} moved to {move_request.destination}"}
    except Exception as e:
        logger.error(f"Error moving sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sprint_name}/details", response_model=SprintDetails)
async def get_sprint_details(sprint_name: str):
    """Get detailed information about a sprint"""
    try:
        sprint_path = METADATA_PATH / sprint_name
        if not sprint_path.exists():
            raise HTTPException(status_code=404, detail=f"Sprint {sprint_name} not found")
        
        # Read all available information
        daily_log = read_daily_log(sprint_path)
        proposal = read_proposal_json(sprint_path)
        sprint_plan = read_sprint_plan(sprint_path)
        
        # Combine information
        details = SprintDetails(
            name=sprint_name,
            status=daily_log.get("status", "Planning"),
            created=proposal.get("created", ""),
            modified=proposal.get("modified", daily_log.get("updated", "")),
            description=proposal.get("description", ""),
            phases=proposal.get("phases", []),
            requirements=proposal.get("requirements", []),
            success_criteria=proposal.get("successCriteria", []),
            coder_assignment=None  # Will be populated from resources
        )
        
        return details
    except Exception as e:
        logger.error(f"Error getting sprint details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{sprint_name}/edit")
async def edit_sprint(sprint_name: str, updates: Dict[str, Any] = Body(...)):
    """Edit sprint proposal.json file"""
    try:
        sprint_path = METADATA_PATH / sprint_name
        if not sprint_path.exists():
            raise HTTPException(status_code=404, detail=f"Sprint {sprint_name} not found")
        
        proposal_path = sprint_path / "proposal.json"
        
        # Read existing proposal
        if proposal_path.exists():
            with open(proposal_path, 'r') as f:
                proposal = json.load(f)
        else:
            proposal = {}
        
        # Update fields
        proposal.update(updates)
        proposal["modified"] = datetime.now().isoformat()
        
        # Write back
        with open(proposal_path, 'w') as f:
            json.dump(proposal, f, indent=2)
        
        # Update DAILY_LOG with edit note
        current_log = read_daily_log(sprint_path)
        write_daily_log(
            sprint_path,
            current_log.get("status", "Planning"),
            "prometheus",
            f"Sprint details edited"
        )
        
        return {"message": f"Sprint {sprint_name} updated successfully"}
    except Exception as e:
        logger.error(f"Error editing sprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))