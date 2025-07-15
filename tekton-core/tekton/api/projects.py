"""
TektonCore Projects API

API endpoints for project management with GitHub integration.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from tekton.core.project_manager_v2 import ProjectManager, ProjectState
from shared.utils.logging_setup import setup_component_logging
from shared.urls import tekton_url

logger = setup_component_logging("tekton_core.api.projects")

# Import landmarks for API documentation
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint
    )
except ImportError:
    # Landmarks not available, define no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Initialize router
router = APIRouter(prefix="/api/projects", tags=["projects"])

# Initialize project manager - use shared instance for consistency
from tekton.core.shared_instances import get_project_manager
project_manager = get_project_manager()


# Simple test endpoint
@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify routing"""
    logger.info("[API] Test endpoint called")
    return {"message": "Projects API is working", "endpoint": "/api/projects/test"}




# Pydantic models for API
class CreateProjectRequest(BaseModel):
    """Request model for creating a new project"""
    github_url: str = Field(..., description="Primary GitHub URL")
    local_directory: str = Field(..., description="Local working directory path")
    forked_repository: Optional[str] = Field(None, description="Fork repository URL")
    upstream_repository: Optional[str] = Field(None, description="Upstream repository URL")
    companion_intelligence: str = Field("llama3.3:70b", description="AI model selection")
    description: Optional[str] = Field("", description="Project description")


class ImportProjectRequest(BaseModel):
    """Request model for importing existing project"""
    local_directory: str = Field(..., description="Local git repository path")
    companion_intelligence: str = Field("llama3.3:70b", description="AI model selection")


class ProjectResponse(BaseModel):
    """Response model for project data"""
    id: str
    name: str
    description: str
    state: str
    github_url: Optional[str]
    local_directory: Optional[str]
    forked_repository: Optional[str]
    upstream_repository: Optional[str]
    companion_intelligence: Optional[str]
    added_date: str
    is_tekton_self: bool
    metadata: Dict[str, Any]


class ProjectWithStatusResponse(BaseModel):
    """Response model for project with git status"""
    project: ProjectResponse
    git_status: Dict[str, Any]


class ProjectListResponse(BaseModel):
    """Response model for project list"""
    projects: List[ProjectResponse]
    total: int


@api_contract(
    title="List Projects API",
    endpoint="/api/projects",
    method="GET",
    request_schema={"state": "Optional[str]"},
    response_schema={"projects": "List[ProjectResponse]", "total": "int"},
    description="Lists all projects with optional state filtering"
)
@router.get("", response_model=ProjectListResponse)
async def list_projects(state: Optional[str] = Query(None, description="Filter by project state")):
    """List all projects, optionally filtered by state"""
    try:
        filter_state = ProjectState(state) if state else None
        projects = project_manager.registry.list_projects(filter_state)
        
        return ProjectListResponse(
            projects=[
                ProjectResponse(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    state=p.state.value,
                    github_url=p.github_url,
                    local_directory=p.local_directory,
                    forked_repository=p.forked_repository,
                    upstream_repository=p.upstream_repository,
                    companion_intelligence=p.companion_intelligence,
                    added_date=p.added_date,
                    is_tekton_self=p.is_tekton_self,
                    metadata=p.metadata
                )
                for p in projects
            ],
            total=len(projects)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_contract(
    title="Create Project API",
    endpoint="/api/projects",
    method="POST",
    request_schema={"request": "CreateProjectRequest"},
    response_schema={"project": "ProjectResponse"},
    description="Creates new project from GitHub URL with automatic git remote detection"
)
@integration_point(
    title="Frontend to Backend Project Creation",
    target_component="project_manager_v2",
    protocol="HTTP POST",
    data_flow="Frontend form → API endpoint → ProjectManager → ProjectRegistry",
    description="Main integration point for project creation from UI"
)
@router.post("", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """Create a new project from GitHub"""
    logger.info(f"[API] Create project request received: {request.github_url}")
    try:
        project = await project_manager.create_project_from_github(
            github_url=request.github_url,
            local_directory=request.local_directory,
            forked_repository=request.forked_repository,
            upstream_repository=request.upstream_repository,
            companion_intelligence=request.companion_intelligence,
            description=request.description
        )
        
        response = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            state=project.state.value,
            github_url=project.github_url,
            local_directory=project.local_directory,
            forked_repository=project.forked_repository,
            upstream_repository=project.upstream_repository,
            companion_intelligence=project.companion_intelligence,
            added_date=project.added_date,
            is_tekton_self=project.is_tekton_self,
            metadata=project.metadata
        )
        logger.info(f"[API] Project created successfully: {project.name} ({project.id})")
        return response
    except Exception as e:
        logger.error(f"[API] Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=ProjectResponse)
async def import_project(request: ImportProjectRequest):
    """Import an existing git project"""
    try:
        project = await project_manager.import_existing_project(
            local_directory=request.local_directory,
            companion_intelligence=request.companion_intelligence
        )
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            state=project.state.value,
            github_url=project.github_url,
            local_directory=project.local_directory,
            forked_repository=project.forked_repository,
            upstream_repository=project.upstream_repository,
            companion_intelligence=project.companion_intelligence,
            added_date=project.added_date,
            is_tekton_self=project.is_tekton_self,
            metadata=project.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectWithStatusResponse)
async def get_project(project_id: str):
    """Get project details with git status"""
    try:
        result = await project_manager.get_project_with_status(project_id)
        
        project_data = result["project"]
        return ProjectWithStatusResponse(
            project=ProjectResponse(
                id=project_data["id"],
                name=project_data["name"],
                description=project_data["description"],
                state=project_data["state"],
                github_url=project_data["github_url"],
                local_directory=project_data["local_directory"],
                forked_repository=project_data["forked_repository"],
                upstream_repository=project_data["upstream_repository"],
                companion_intelligence=project_data["companion_intelligence"],
                added_date=project_data["added_date"],
                is_tekton_self=project_data["is_tekton_self"],
                metadata=project_data["metadata"]
            ),
            git_status=result["git_status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}/refresh-remotes", response_model=ProjectResponse)
async def refresh_project_remotes(project_id: str):
    """Refresh project's git remote information"""
    try:
        project = await project_manager.update_project_remotes(project_id)
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            state=project.state.value,
            github_url=project.github_url,
            local_directory=project.local_directory,
            forked_repository=project.forked_repository,
            upstream_repository=project.upstream_repository,
            companion_intelligence=project.companion_intelligence,
            added_date=project.added_date,
            is_tekton_self=project.is_tekton_self,
            metadata=project.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def remove_project(project_id: str):
    """Remove project from dashboard (does not delete repository)"""
    try:
        success = project_manager.registry.remove_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "message": "Project removed from dashboard",
            "project_id": project_id,
            "note": "Repository files remain untouched"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/location")
async def get_config_location():
    """Get the configuration file location for debugging"""
    return {
        "config_path": str(project_manager.registry.storage_path),
        "projects_file": str(project_manager.registry.projects_file),
        "exists": project_manager.registry.projects_file.exists()
    }


# Git action endpoints (for UI buttons)
@router.post("/{project_id}/git/status")
async def git_status(project_id: str):
    """Get git status for a project"""
    try:
        project = project_manager.registry.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not project.local_directory:
            raise HTTPException(status_code=400, detail="Project has no local directory")
        
        # Run git status command
        import subprocess
        result = subprocess.run(
            ["git", "-C", project.local_directory, "status", "--short"],
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "status": result.stdout,
            "return_code": result.returncode,
            "error": result.stderr if result.returncode != 0 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/git/pull")
async def git_pull(project_id: str, remote: str = Query(..., description="Remote to pull from (fork/upstream)")):
    """Pull from git remote"""
    try:
        project = project_manager.registry.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not project.local_directory:
            raise HTTPException(status_code=400, detail="Project has no local directory")
        
        # Determine remote URL
        if remote == "fork" and project.forked_repository:
            remote_name = "origin"
        elif remote == "upstream" and project.upstream_repository:
            remote_name = "upstream"
        else:
            raise HTTPException(status_code=400, detail=f"No {remote} repository configured")
        
        # Run git pull command
        import subprocess
        result = subprocess.run(
            ["git", "-C", project.local_directory, "pull", remote_name],
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "remote": remote,
            "output": result.stdout,
            "return_code": result.returncode,
            "error": result.stderr if result.returncode != 0 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/git/push")
async def git_push(project_id: str):
    """Push to fork repository"""
    try:
        project = project_manager.registry.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not project.local_directory:
            raise HTTPException(status_code=400, detail="Project has no local directory")
        
        if not project.forked_repository:
            raise HTTPException(status_code=400, detail="No fork repository configured")
        
        # Run git push command
        import subprocess
        result = subprocess.run(
            ["git", "-C", project.local_directory, "push", "origin"],
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "output": result.stdout,
            "return_code": result.returncode,
            "error": result.stderr if result.returncode != 0 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))