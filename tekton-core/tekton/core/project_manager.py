"""
TektonCore Project Management System

Manages project lifecycle, state, and coordination for multi-AI development workflows.
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("tekton_core.project_manager")


class ProjectState(str, Enum):
    """Project lifecycle states"""
    DEV_SPRINT = "dev_sprint"          # Initial idea documented
    QUEUED = "queued"                  # Approved for project queue
    PLANNING = "planning"              # Active planning phase
    APPROVED = "approved"              # Ready for development
    ACTIVE = "active"                  # Development in progress
    COMPLETE = "complete"              # All objectives achieved
    ARCHIVED = "archived"              # Completed and archived


class TaskState(str, Enum):
    """Task states"""
    PENDING = "pending"                # Not yet assigned
    ASSIGNED = "assigned"              # Assigned to AI worker
    IN_PROGRESS = "in_progress"        # Actively being worked on
    READY_FOR_MERGE = "ready_for_merge"  # Ready for merge coordination
    COMPLETED = "completed"            # Successfully merged
    BLOCKED = "blocked"                # Blocked by dependencies


@dataclass
class Task:
    """Individual task within a project"""
    id: str
    title: str
    description: str
    state: TaskState
    assigned_ai: Optional[str] = None
    branch: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    estimated_hours: Optional[int] = None
    dependencies: List[str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class Project:
    """Project data model"""
    id: str
    name: str
    description: str
    state: ProjectState
    repo_url: Optional[str] = None
    working_dir: Optional[str] = None
    upstream_repo: Optional[str] = None
    companion_ai: Optional[str] = None
    tasks: List[Task] = None
    created_at: str = None
    updated_at: str = None
    last_activity: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.last_activity is None:
            self.last_activity = self.created_at
        if self.metadata is None:
            self.metadata = {}


class ProjectRegistry:
    """JSON-based project storage system"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize project registry"""
        if storage_path is None:
            # Default to ~/.tekton/projects/
            home = Path.home()
            storage_path = home / ".tekton" / "projects"
        
        self.storage_path = Path(storage_path)
        self.registry_file = self.storage_path / "registry.json"
        self.projects_dir = self.storage_path / "projects"
        self.tasks_dir = self.storage_path / "tasks"
        
        # Ensure directories exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)
        self.tasks_dir.mkdir(exist_ok=True)
        
        # Initialize registry if it doesn't exist
        if not self.registry_file.exists():
            self._create_empty_registry()
            
        logger.info(f"Project registry initialized at {self.storage_path}")
    
    def _create_empty_registry(self):
        """Create empty registry file"""
        registry_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "projects": {},
            "metadata": {
                "total_projects": 0,
                "active_projects": 0,
                "completed_projects": 0
            }
        }
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file"""
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            self._create_empty_registry()
            return self._load_registry()
    
    def _save_registry(self, registry_data: Dict[str, Any]):
        """Save registry to file"""
        registry_data["updated_at"] = datetime.now().isoformat()
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
    
    def _load_project_file(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load individual project file"""
        project_file = self.projects_dir / f"{project_id}.json"
        
        if not project_file.exists():
            return None
            
        try:
            with open(project_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load project {project_id}: {e}")
            return None
    
    def _save_project_file(self, project: Project):
        """Save individual project file"""
        project_file = self.projects_dir / f"{project.id}.json"
        project.updated_at = datetime.now().isoformat()
        
        # Convert project to dict, handling dataclasses
        project_data = asdict(project)
        
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
    
    def create_project(self, name: str, description: str, **kwargs) -> Project:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        
        project = Project(
            id=project_id,
            name=name,
            description=description,
            state=ProjectState.DEV_SPRINT,
            **kwargs
        )
        
        # Save project file
        self._save_project_file(project)
        
        # Update registry
        registry_data = self._load_registry()
        registry_data["projects"][project_id] = {
            "name": name,
            "state": project.state.value,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        registry_data["metadata"]["total_projects"] += 1
        self._save_registry(registry_data)
        
        logger.info(f"Created project: {name} ({project_id})")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        project_data = self._load_project_file(project_id)
        
        if not project_data:
            return None
        
        # Convert back to Project object
        # Handle tasks conversion
        tasks = []
        for task_data in project_data.get("tasks", []):
            task = Task(**task_data)
            tasks.append(task)
        
        project_data["tasks"] = tasks
        project_data["state"] = ProjectState(project_data["state"])
        
        return Project(**project_data)
    
    def update_project(self, project: Project):
        """Update existing project"""
        project.updated_at = datetime.now().isoformat()
        project.last_activity = project.updated_at
        
        # Save project file
        self._save_project_file(project)
        
        # Update registry
        registry_data = self._load_registry()
        if project.id in registry_data["projects"]:
            registry_data["projects"][project.id].update({
                "name": project.name,
                "state": project.state.value,
                "updated_at": project.updated_at
            })
            self._save_registry(registry_data)
        
        logger.info(f"Updated project: {project.name} ({project.id})")
    
    def list_projects(self, state: Optional[ProjectState] = None) -> List[Project]:
        """List all projects, optionally filtered by state"""
        registry_data = self._load_registry()
        projects = []
        
        for project_id in registry_data["projects"]:
            project = self.get_project(project_id)
            if project and (state is None or project.state == state):
                projects.append(project)
        
        # Sort by last activity (most recent first)
        projects.sort(key=lambda p: p.last_activity, reverse=True)
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        project_file = self.projects_dir / f"{project_id}.json"
        
        if not project_file.exists():
            return False
        
        # Remove project file
        project_file.unlink()
        
        # Update registry
        registry_data = self._load_registry()
        if project_id in registry_data["projects"]:
            del registry_data["projects"][project_id]
            registry_data["metadata"]["total_projects"] -= 1
            self._save_registry(registry_data)
        
        logger.info(f"Deleted project: {project_id}")
        return True


class ProjectManager:
    """High-level project management interface"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize project manager"""
        self.registry = ProjectRegistry(storage_path)
        logger.info("Project manager initialized")
    
    async def create_project_from_sprint(self, sprint_path: str) -> Project:
        """Create project from development sprint documentation"""
        sprint_file = Path(sprint_path)
        
        if not sprint_file.exists():
            raise ValueError(f"Sprint file not found: {sprint_path}")
        
        # Extract project name from sprint directory
        sprint_name = sprint_file.parent.name
        project_name = sprint_name.replace("_", " ").title()
        
        # Read sprint documentation (basic implementation)
        description = f"Project created from sprint: {sprint_name}"
        
        project = self.registry.create_project(
            name=project_name,
            description=description,
            metadata={
                "sprint_path": str(sprint_path),
                "sprint_name": sprint_name
            }
        )
        
        logger.info(f"Created project from sprint: {project_name}")
        return project
    
    async def transition_project_state(self, project_id: str, new_state: ProjectState, reason: str = None):
        """Transition project to new state"""
        project = self.registry.get_project(project_id)
        
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        old_state = project.state
        project.state = new_state
        
        if reason:
            if "state_transitions" not in project.metadata:
                project.metadata["state_transitions"] = []
            
            project.metadata["state_transitions"].append({
                "from_state": old_state.value,
                "to_state": new_state.value,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
        
        self.registry.update_project(project)
        
        logger.info(f"Project {project.name} transitioned from {old_state.value} to {new_state.value}")
        return project
    
    async def add_task(self, project_id: str, title: str, description: str, **kwargs) -> Task:
        """Add task to project"""
        project = self.registry.get_project(project_id)
        
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            state=TaskState.PENDING,
            **kwargs
        )
        
        project.tasks.append(task)
        self.registry.update_project(project)
        
        logger.info(f"Added task '{title}' to project {project.name}")
        return task
    
    async def update_task_state(self, project_id: str, task_id: str, new_state: TaskState, **kwargs):
        """Update task state"""
        project = self.registry.get_project(project_id)
        
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        task = None
        for t in project.tasks:
            if t.id == task_id:
                task = t
                break
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.state = new_state
        task.updated_at = datetime.now().isoformat()
        
        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.registry.update_project(project)
        
        logger.info(f"Task '{task.title}' state updated to {new_state.value}")
        return task
    
    async def assign_task(self, project_id: str, task_id: str, ai_name: str, branch: str = None):
        """Assign task to AI worker"""
        if not branch:
            # Generate branch name
            project = self.registry.get_project(project_id)
            branch = f"sprint/{ai_name.lower()}-{task_id[:8]}"
        
        await self.update_task_state(
            project_id, 
            task_id, 
            TaskState.ASSIGNED,
            assigned_ai=ai_name,
            branch=branch
        )
        
        logger.info(f"Assigned task {task_id} to {ai_name} on branch {branch}")
        return branch
    
    async def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project summary"""
        project = self.registry.get_project(project_id)
        
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Calculate task statistics
        task_stats = {
            "total": len(project.tasks),
            "pending": len([t for t in project.tasks if t.state == TaskState.PENDING]),
            "assigned": len([t for t in project.tasks if t.state == TaskState.ASSIGNED]),
            "in_progress": len([t for t in project.tasks if t.state == TaskState.IN_PROGRESS]),
            "ready_for_merge": len([t for t in project.tasks if t.state == TaskState.READY_FOR_MERGE]),
            "completed": len([t for t in project.tasks if t.state == TaskState.COMPLETED]),
            "blocked": len([t for t in project.tasks if t.state == TaskState.BLOCKED])
        }
        
        # Calculate progress percentage
        if task_stats["total"] > 0:
            progress = (task_stats["completed"] / task_stats["total"]) * 100
        else:
            progress = 0
        
        return {
            "project": asdict(project),
            "task_stats": task_stats,
            "progress": round(progress, 1),
            "active_tasks": [asdict(t) for t in project.tasks if t.state in [TaskState.ASSIGNED, TaskState.IN_PROGRESS]],
            "ready_tasks": [asdict(t) for t in project.tasks if t.state == TaskState.READY_FOR_MERGE]
        }
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide project overview"""
        all_projects = self.registry.list_projects()
        
        state_counts = {}
        for state in ProjectState:
            state_counts[state.value] = len([p for p in all_projects if p.state == state])
        
        # Get active projects with task summaries
        active_projects = []
        for project in all_projects:
            if project.state in [ProjectState.ACTIVE, ProjectState.APPROVED, ProjectState.PLANNING]:
                summary = await self.get_project_summary(project.id)
                active_projects.append(summary)
        
        return {
            "total_projects": len(all_projects),
            "state_counts": state_counts,
            "active_projects": active_projects,
            "recent_activity": [asdict(p) for p in all_projects[:5]]  # 5 most recent
        }