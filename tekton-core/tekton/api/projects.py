"""
TektonCore Projects API

API endpoints for project management with GitHub integration.
"""

import os
import socket
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from tekton.core.project_manager import ProjectManager, ProjectState
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
    companion_intelligence: str = Field("gpt-oss:20b", description="AI model selection")
    description: Optional[str] = Field("", description="Project description")


class ImportProjectRequest(BaseModel):
    """Request model for importing existing project"""
    local_directory: str = Field(..., description="Local git repository path")
    companion_intelligence: str = Field("gpt-oss:20b", description="AI model selection")


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
    is_active: bool = True  # Whether the working directory exists
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
        
        # Ensure project CIs are running when projects are listed
        # This happens when the UI loads the project cards
        await project_manager.ensure_project_cis_running(projects)
        
        project_responses = []
        for p in projects:
            # Check if working directory exists
            is_active = True
            if p.local_directory:
                is_active = os.path.exists(p.local_directory)
                if not is_active:
                    logger.warning(f"Project {p.name} directory not found: {p.local_directory}")
            
            project_responses.append(
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
                    is_active=is_active,
                    metadata=p.metadata
                )
            )
        
        return ProjectListResponse(
            projects=project_responses,
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
        
        # Launch the project CI immediately after creation
        await project_manager.launch_project_ci(project)
        
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


@router.post("/check-git")
async def check_git_repository(request: Dict[str, Any]):
    """Check if a path is a git repository and get its status"""
    import subprocess
    
    try:
        path = request.get("path")
        if not path:
            raise HTTPException(status_code=400, detail="Path is required")
        
        # Expand the path
        expanded_path = os.path.expanduser(path)
        
        # Check if path exists
        if not os.path.exists(expanded_path):
            return {
                "is_git": False,
                "exists": False,
                "message": "Path does not exist"
            }
        
        # Check if it's a git repository
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=expanded_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            is_git = result.returncode == 0
        except Exception:
            is_git = False
        
        if not is_git:
            return {
                "is_git": False,
                "exists": True,
                "message": "Not a git repository"
            }
        
        # Get git remote info
        remotes = {}
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=expanded_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            remote_url = parts[1]
                            if remote_name not in remotes:
                                remotes[remote_name] = remote_url
        except Exception:
            pass
        
        # Get current branch
        current_branch = None
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=expanded_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                current_branch = result.stdout.strip()
        except Exception:
            pass
        
        return {
            "is_git": True,
            "exists": True,
            "remotes": remotes,
            "current_branch": current_branch,
            "has_origin": "origin" in remotes,
            "has_upstream": "upstream" in remotes,
            "origin_url": remotes.get("origin"),
            "upstream_url": remotes.get("upstream")
        }
        
    except Exception as e:
        logger.error(f"Error checking git repository: {e}")
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


# Projects Chat Models
class ProjectsChatRequest(BaseModel):
    """Request model for projects chat"""
    project_name: str = Field(..., description="Name of the project")
    message: str = Field(..., description="Message to send to project CI")
    ci_socket: Optional[str] = Field(None, description="CI socket identifier")


class ProjectsChatResponse(BaseModel):
    """Response model for projects chat"""
    response: str = Field(..., description="Response from project CI")
    project_name: str = Field(..., description="Name of the project")
    ci_socket: str = Field(..., description="CI socket identifier")


# Socket Communication Helper
async def send_to_project_ci_socket(port: int, message: str) -> str:
    """Send message to project CI via socket"""
    try:
        # Use same pattern as aish MessageHandler
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20)  # 20 second timeout
        
        # Connect to CI socket
        await asyncio.get_event_loop().run_in_executor(
            None, sock.connect, ('localhost', port)
        )
        
        # Send message
        message_data = json.dumps({'content': message}) + '\n'
        await asyncio.get_event_loop().run_in_executor(
            None, sock.send, message_data.encode()
        )
        
        # Receive response
        response_data = await asyncio.get_event_loop().run_in_executor(
            None, sock.recv, 4096
        )
        
        sock.close()
        
        # Parse response
        response = json.loads(response_data.decode())
        return response.get('content', '')
        
    except Exception as e:
        logger.error(f"Socket communication failed: {e}")
        return f"Error: Unable to reach CI on port {port}"


def get_project_ci_port(project_name: str) -> int:
    """Get socket port for project CI"""
    if project_name.lower() == "tekton":
        return 42016  # numa-ai port
    
    # For other projects, use base port + hash
    # This is simplified - real implementation would use project registry
    project_hash = abs(hash(project_name)) % 1000
    return 42100 + project_hash


@api_contract(
    title="Projects Chat API",
    endpoint="/api/projects/chat",
    method="POST",
    request_schema={"project_name": "str", "message": "str", "ci_socket": "Optional[str]"},
    response_schema={"response": "str", "project_name": "str", "ci_socket": "str"},
    description="Send message to project CI via socket communication"
)
@router.post("/chat", response_model=ProjectsChatResponse)
async def projects_chat(request: ProjectsChatRequest):
    """Send message to project CI"""
    project_name = request.project_name
    message = request.message
    ci_socket = request.ci_socket
    
    if not all([project_name, message]):
        raise HTTPException(400, "Missing required fields: project_name, message")
    
    logger.info(f"Projects chat: {project_name} -> {message[:50]}...")
    
    # Get project CI port
    project_ci_port = get_project_ci_port(project_name)
    
    # Send to CI using socket pattern
    try:
        response = await send_to_project_ci_socket(
            project_ci_port, 
            f"[Project: {project_name}] {message}"
        )
        
        logger.info(f"Projects chat response: {response[:100]}...")
        
        return ProjectsChatResponse(
            response=response,
            project_name=project_name,
            ci_socket=ci_socket or f"project-{project_name.lower()}-ai"
        )
        
    except Exception as e:
        logger.error(f"Projects chat failed: {e}")
        raise HTTPException(500, f"CI communication failed: {str(e)}")