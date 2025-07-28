"""
Sprint Management Routes for Planning Team Workflow UI

This module provides endpoints for managing development sprints,
specifically for the Metis UI component in the planning workflow.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status, Request
from metis.api.controllers import TaskController
from landmarks import api_contract, integration_point
import os
import json
from datetime import datetime
import re
import uuid


# Create router for sprint management
sprint_router = APIRouter(prefix="/api/v1", tags=["Sprint Management"])


# Dependency for getting the controller
def get_task_controller(request: Request) -> TaskController:
    """Get the TaskController instance from the component."""
    component = request.app.state.component
    if not component or not component.task_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Component not initialized"
        )
    return TaskController(component.task_manager)


@sprint_router.get(
    "/sprints",
    response_model=Dict[str, Any],
    summary="List Development Sprints",
    description="List all development sprints with optional status filter"
)
@api_contract(
    title="Sprint List API",
    endpoint="/api/v1/sprints",
    method="GET",
    request_schema={"status": "string (optional)"}
)
async def list_sprints(
    status: Optional[str] = Query(None, title="Filter by status (e.g., 'Ready-1:Metis')"),
    controller: TaskController = Depends(get_task_controller)
):
    """List development sprints from filesystem."""
    try:
        sprints_path = "/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints"
        sprints = []
        
        # Scan sprint directories
        for item in os.listdir(sprints_path):
            if item.endswith("_Sprint") and os.path.isdir(os.path.join(sprints_path, item)):
                sprint_dir = os.path.join(sprints_path, item)
                daily_log_path = os.path.join(sprint_dir, "DAILY_LOG.md")
                
                # Read sprint status from DAILY_LOG.md
                sprint_status = "Unknown"
                description = ""
                created_date = ""
                priority = "Medium"
                
                if os.path.exists(daily_log_path):
                    with open(daily_log_path, 'r') as f:
                        content = f.read()
                        # Extract status from "## Sprint Status: XXX" line
                        status_match = re.search(r'## Sprint Status: (.+)', content)
                        if status_match:
                            sprint_status = status_match.group(1).strip()
                        
                        # Extract first paragraph as description
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.strip() and not line.startswith('#') and not line.startswith('**'):
                                description = line.strip()
                                break
                        
                        # Extract date
                        date_match = re.search(r'\*\*Updated\*\*: (.+)', content)
                        if date_match:
                            created_date = date_match.group(1).strip()
                
                # Apply status filter if provided
                if status and sprint_status != status:
                    continue
                
                sprint_name = item.replace("_Sprint", "")
                
                sprints.append({
                    "id": item,
                    "name": sprint_name,
                    "status": sprint_status,
                    "description": description or f"Development sprint for {sprint_name}",
                    "created_date": created_date or datetime.now().isoformat(),
                    "priority": priority,
                    "path": sprint_dir
                })
        
        return {
            "success": True,
            "sprints": sprints,
            "total": len(sprints)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sprints: {str(e)}"
        )


@sprint_router.get(
    "/sprints/{sprint_id}",
    response_model=Dict[str, Any],
    summary="Get Sprint Details",
    description="Get detailed information about a specific sprint"
)
async def get_sprint(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    controller: TaskController = Depends(get_task_controller)
):
    """Get sprint details including tasks."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        
        if not os.path.exists(sprint_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sprint not found: {sprint_id}"
            )
        
        # Read sprint tasks if exists
        tasks_file = os.path.join(sprint_path, "tasks.json")
        tasks = []
        
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        return {
            "success": True,
            "sprint_id": sprint_id,
            "tasks": tasks
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sprint: {str(e)}"
        )


@sprint_router.post(
    "/sprints/{sprint_id}/tasks",
    response_model=Dict[str, Any],
    summary="Create Task for Sprint",
    description="Create a new task within a sprint"
)
@api_contract(
    title="Sprint Task Creation API",
    endpoint="/api/v1/sprints/{sprint_id}/tasks",
    method="POST",
    request_schema={"name": "string", "description": "string", "complexity": "int", "estimated_hours": "float", "phase": "string"}
)
async def create_sprint_task(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    task_data: Dict[str, Any] = Body(...),
    controller: TaskController = Depends(get_task_controller)
):
    """Create a task for a sprint."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        
        if not os.path.exists(sprint_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sprint not found: {sprint_id}"
            )
        
        # Load existing tasks
        tasks_file = os.path.join(sprint_path, "tasks.json")
        tasks = []
        
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        # Create new task
        new_task = {
            "id": str(uuid.uuid4()),
            "sprint_id": sprint_id,
            "name": task_data.get("name", ""),
            "description": task_data.get("description", ""),
            "complexity": task_data.get("complexity", 3),
            "estimated_hours": task_data.get("estimated_hours", 0),
            "phase": task_data.get("phase", ""),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "dependencies": []
        }
        
        tasks.append(new_task)
        
        # Save tasks
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return {
            "success": True,
            "task": new_task,
            "message": "Task created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@sprint_router.put(
    "/sprints/{sprint_id}/tasks/{task_id}",
    response_model=Dict[str, Any],
    summary="Update Sprint Task",
    description="Update a task within a sprint"
)
async def update_sprint_task(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    task_id: str = Path(..., title="The ID of the task"),
    task_data: Dict[str, Any] = Body(...),
    controller: TaskController = Depends(get_task_controller)
):
    """Update a sprint task."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        tasks_file = os.path.join(sprint_path, "tasks.json")
        
        if not os.path.exists(tasks_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tasks found for sprint: {sprint_id}"
            )
        
        # Load tasks
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        # Find and update task
        task_found = False
        for i, task in enumerate(tasks):
            if task.get("id") == task_id:
                tasks[i].update(task_data)
                tasks[i]["updated_at"] = datetime.now().isoformat()
                task_found = True
                break
        
        if not task_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}"
            )
        
        # Save tasks
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return {
            "success": True,
            "message": "Task updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@sprint_router.delete(
    "/sprints/{sprint_id}/tasks/{task_id}",
    response_model=Dict[str, Any],
    summary="Delete Sprint Task",
    description="Delete a task from a sprint"
)
async def delete_sprint_task(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    task_id: str = Path(..., title="The ID of the task"),
    controller: TaskController = Depends(get_task_controller)
):
    """Delete a sprint task."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        tasks_file = os.path.join(sprint_path, "tasks.json")
        
        if not os.path.exists(tasks_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tasks found for sprint: {sprint_id}"
            )
        
        # Load tasks
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        # Remove task
        original_count = len(tasks)
        tasks = [t for t in tasks if t.get("id") != task_id]
        
        if len(tasks) == original_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}"
            )
        
        # Save tasks
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return {
            "success": True,
            "message": "Task deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


@sprint_router.get(
    "/sprints/{sprint_id}/dependencies",
    response_model=Dict[str, Any],
    summary="List Task Dependencies",
    description="List all dependencies for tasks in a sprint"
)
async def list_sprint_dependencies(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    controller: TaskController = Depends(get_task_controller)
):
    """List dependencies for sprint tasks."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        tasks_file = os.path.join(sprint_path, "tasks.json")
        
        if not os.path.exists(tasks_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tasks found for sprint: {sprint_id}"
            )
        
        # Load tasks
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        # Build dependency list
        dependencies = []
        task_map = {t["id"]: t["name"] for t in tasks}
        
        for task in tasks:
            if task.get("dependencies"):
                for dep_id in task["dependencies"]:
                    dependencies.append({
                        "task_id": task["id"],
                        "task_name": task["name"],
                        "depends_on_id": dep_id,
                        "depends_on_name": task_map.get(dep_id, "Unknown Task")
                    })
        
        return {
            "success": True,
            "dependencies": dependencies,
            "total": len(dependencies)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list dependencies: {str(e)}"
        )


@sprint_router.post(
    "/sprints/{sprint_id}/dependencies",
    response_model=Dict[str, Any],
    summary="Create Task Dependency",
    description="Create a dependency between tasks in a sprint"
)
async def create_sprint_dependency(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    dependency_data: Dict[str, Any] = Body(...),
    controller: TaskController = Depends(get_task_controller)
):
    """Create a dependency between sprint tasks."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        tasks_file = os.path.join(sprint_path, "tasks.json")
        
        if not os.path.exists(tasks_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tasks found for sprint: {sprint_id}"
            )
        
        # Load tasks
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        task_id = dependency_data.get("task_id")
        depends_on_id = dependency_data.get("depends_on_id")
        
        # Find task and add dependency
        task_found = False
        for task in tasks:
            if task.get("id") == task_id:
                if "dependencies" not in task:
                    task["dependencies"] = []
                if depends_on_id not in task["dependencies"]:
                    task["dependencies"].append(depends_on_id)
                task_found = True
                break
        
        if not task_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}"
            )
        
        # Save tasks
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return {
            "success": True,
            "message": "Dependency created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dependency: {str(e)}"
        )


@sprint_router.delete(
    "/sprints/{sprint_id}/dependencies",
    response_model=Dict[str, Any],
    summary="Remove Task Dependency",
    description="Remove a dependency between tasks in a sprint"
)
async def remove_sprint_dependency(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    dependency_data: Dict[str, Any] = Body(...),
    controller: TaskController = Depends(get_task_controller)
):
    """Remove a dependency between sprint tasks."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        tasks_file = os.path.join(sprint_path, "tasks.json")
        
        if not os.path.exists(tasks_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tasks found for sprint: {sprint_id}"
            )
        
        # Load tasks
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        task_id = dependency_data.get("task_id")
        depends_on_id = dependency_data.get("depends_on_id")
        
        # Find task and remove dependency
        task_found = False
        for task in tasks:
            if task.get("id") == task_id:
                if "dependencies" in task and depends_on_id in task["dependencies"]:
                    task["dependencies"].remove(depends_on_id)
                    task_found = True
                break
        
        if not task_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task or dependency not found"
            )
        
        # Save tasks
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return {
            "success": True,
            "message": "Dependency removed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove dependency: {str(e)}"
        )


@sprint_router.post(
    "/sprints/{sprint_id}/export",
    response_model=Dict[str, Any],
    summary="Export Sprint to Harmonia",
    description="Export sprint tasks to Harmonia for resource allocation"
)
@integration_point(
    title="Harmonia Export Integration",
    target_component="Harmonia",
    protocol="File-based handoff",
    data_flow="Metis Tasks -> Export File -> Harmonia Import"
)
async def export_to_harmonia(
    sprint_id: str = Path(..., title="The ID of the sprint"),
    controller: TaskController = Depends(get_task_controller)
):
    """Export sprint tasks to Harmonia."""
    try:
        sprint_path = f"/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/{sprint_id}"
        tasks_file = os.path.join(sprint_path, "tasks.json")
        
        if not os.path.exists(tasks_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No tasks found for sprint: {sprint_id}"
            )
        
        # Load tasks
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        # Prepare export data
        export_data = {
            "sprint_id": sprint_id,
            "exported_at": datetime.now().isoformat(),
            "exported_by": "Metis",
            "status": "Ready-2:Harmonia",
            "tasks": tasks,
            "summary": {
                "total_tasks": len(tasks),
                "total_hours": sum(t.get("estimated_hours", 0) for t in tasks),
                "average_complexity": sum(t.get("complexity", 0) for t in tasks) / len(tasks) if tasks else 0
            }
        }
        
        # Save export file
        export_file = os.path.join(sprint_path, "harmonia_export.json")
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Update DAILY_LOG.md status
        daily_log_path = os.path.join(sprint_path, "DAILY_LOG.md")
        if os.path.exists(daily_log_path):
            with open(daily_log_path, 'r') as f:
                content = f.read()
            
            # Update status line
            content = re.sub(
                r'## Sprint Status: .+',
                '## Sprint Status: Ready-2:Harmonia',
                content
            )
            
            # Add export note
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            export_note = f"\n### Export to Harmonia - {timestamp}\n- Exported {len(tasks)} tasks\n- Total estimated hours: {export_data['summary']['total_hours']}\n- Average complexity: {export_data['summary']['average_complexity']:.1f}\n"
            
            # Insert after status line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('## Sprint Status:'):
                    lines.insert(i + 1, export_note)
                    break
            
            content = '\n'.join(lines)
            
            with open(daily_log_path, 'w') as f:
                f.write(content)
        
        return {
            "success": True,
            "message": f"Sprint exported to Harmonia successfully",
            "export_file": export_file,
            "summary": export_data["summary"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export to Harmonia: {str(e)}"
        )


@sprint_router.post(
    "/workflow",
    response_model=Dict[str, Any],
    summary="Workflow Check",
    description="Check for sprints ready for Metis processing"
)
async def check_workflow(
    workflow_data: Dict[str, Any] = Body(...),
    controller: TaskController = Depends(get_task_controller)
):
    """Check for sprints with Ready-1:Metis status."""
    try:
        purpose = workflow_data.get("purpose", {})
        
        if purpose.get("metis") == "check_for_sprints":
            # List all Ready-1:Metis sprints
            sprints_path = "/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints"
            ready_sprints = []
            
            for item in os.listdir(sprints_path):
                if item.endswith("_Sprint") and os.path.isdir(os.path.join(sprints_path, item)):
                    sprint_dir = os.path.join(sprints_path, item)
                    daily_log_path = os.path.join(sprint_dir, "DAILY_LOG.md")
                    
                    if os.path.exists(daily_log_path):
                        with open(daily_log_path, 'r') as f:
                            content = f.read()
                            status_match = re.search(r'## Sprint Status: (.+)', content)
                            if status_match and status_match.group(1).strip() == "Ready-1:Metis":
                                ready_sprints.append({
                                    "id": item,
                                    "name": item.replace("_Sprint", ""),
                                    "path": sprint_dir
                                })
            
            return {
                "success": True,
                "ready_sprints": ready_sprints,
                "count": len(ready_sprints),
                "message": f"Found {len(ready_sprints)} sprints ready for task breakdown"
            }
        
        return {
            "success": True,
            "message": "Workflow check completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow check failed: {str(e)}"
        )