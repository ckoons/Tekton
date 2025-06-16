"""Command implementations for the Telos CLI.

This module provides the implementation of commands for the Telos CLI.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable

from telos.core.requirements import RequirementsManager, Requirement, Project
from telos.ui.cli_helpers import (
    format_timestamp, get_status_symbol, get_priority_symbol,
    visualize_hierarchy, visualize_graph
)

logger = logging.getLogger(__name__)


# Project commands
def create_project(requirements_manager: RequirementsManager, name: str, description: str = "") -> None:
    """Create a project.
    
    Args:
        requirements_manager: Requirements manager
        name: Project name
        description: Project description
    """
    project_id = requirements_manager.create_project(name, description)
    print(f"Created project {project_id}: {name}")


def list_projects(requirements_manager: RequirementsManager) -> None:
    """List all projects.
    
    Args:
        requirements_manager: Requirements manager
    """
    projects = requirements_manager.get_all_projects()
    
    if not projects:
        print("No projects found")
        return
    
    print("Projects:")
    for project in projects:
        req_count = len(project.requirements)
        print(f"  {project.project_id}: {project.name} ({req_count} requirements)")


def show_project(requirements_manager: RequirementsManager, project_id: str) -> None:
    """Show project details.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
    """
    project = requirements_manager.get_project(project_id)
    
    if not project:
        print(f"Project {project_id} not found")
        return
    
    print(f"Project: {project.name} ({project.project_id})")
    print(f"Description: {project.description}")
    print(f"Created: {format_timestamp(project.created_at)}")
    print(f"Updated: {format_timestamp(project.updated_at)}")
    print(f"Requirements: {len(project.requirements)}")
    
    if project.requirements:
        print("\nRequirements:")
        for req_id, requirement in project.requirements.items():
            status_symbol = get_status_symbol(requirement.status)
            priority_symbol = get_priority_symbol(requirement.priority)
            print(f"  {status_symbol} {priority_symbol} {req_id}: {requirement.title}")


def delete_project(requirements_manager: RequirementsManager, project_id: str) -> None:
    """Delete a project.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
    """
    success = requirements_manager.delete_project(project_id)
    
    if success:
        print(f"Deleted project {project_id}")
    else:
        print(f"Project {project_id} not found")


# Requirement commands
def add_requirement(
    requirements_manager: RequirementsManager,
    project_id: str,
    title: str,
    description: str = "",
    requirement_type: str = "functional",
    priority: str = "medium",
    tags: Optional[str] = None,
    parent_id: Optional[str] = None,
    interactive: bool = False
) -> None:
    """Add a requirement to a project.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
        title: Requirement title
        description: Requirement description
        requirement_type: Requirement type
        priority: Priority level
        tags: Comma-separated tags
        parent_id: Parent requirement ID
        interactive: Whether to start interactive refinement after adding
    """
    # Parse tags
    tag_list = tags.split(",") if tags else []
    
    # Add the requirement
    req_id = requirements_manager.add_requirement(
        project_id=project_id,
        title=title,
        description=description,
        requirement_type=requirement_type,
        priority=priority,
        tags=tag_list,
        parent_id=parent_id
    )
    
    if req_id:
        print(f"Added requirement {req_id} to project {project_id}")
        
        # Start interactive refinement if requested
        if interactive:
            from telos.ui.interactive_refine import refine_requirement_cmd
            refine_requirement_cmd(requirements_manager, project_id, req_id)
    else:
        print(f"Project {project_id} not found")


def list_requirements(
    requirements_manager: RequirementsManager,
    project_id: str,
    status: Optional[str] = None,
    requirement_type: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None
) -> None:
    """List requirements in a project.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
        status: Filter by status
        requirement_type: Filter by type
        priority: Filter by priority
        tag: Filter by tag
    """
    project = requirements_manager.get_project(project_id)
    
    if not project:
        print(f"Project {project_id} not found")
        return
    
    requirements = project.get_all_requirements(
        status=status,
        requirement_type=requirement_type,
        priority=priority,
        tag=tag
    )
    
    if not requirements:
        print("No requirements found matching the criteria")
        return
    
    print(f"Requirements for project {project.name} ({project_id}):")
    for requirement in requirements:
        status_symbol = get_status_symbol(requirement.status)
        priority_symbol = get_priority_symbol(requirement.priority)
        print(f"  {status_symbol} {priority_symbol} {requirement.requirement_id}: {requirement.title}")
        
        # Show additional details for each requirement
        if requirement.tags:
            tags_str = ", ".join(requirement.tags)
            print(f"    Tags: {tags_str}")
        
        if requirement.parent_id:
            print(f"    Parent: {requirement.parent_id}")
        
        print(f"    Type: {requirement.requirement_type}")


def show_requirement(requirements_manager: RequirementsManager, project_id: str, requirement_id: str) -> None:
    """Show requirement details.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
        requirement_id: Requirement ID
    """
    requirement = requirements_manager.get_requirement(project_id, requirement_id)
    
    if not requirement:
        print(f"Requirement {requirement_id} not found in project {project_id}")
        return
    
    print(f"Requirement: {requirement.title} ({requirement_id})")
    print(f"Project: {project_id}")
    print(f"Description: {requirement.description}")
    print(f"Type: {requirement.requirement_type}")
    print(f"Priority: {requirement.priority}")
    print(f"Status: {requirement.status}")
    
    if requirement.tags:
        tags_str = ", ".join(requirement.tags)
        print(f"Tags: {tags_str}")
    
    if requirement.parent_id:
        print(f"Parent: {requirement.parent_id}")
    
    if requirement.dependencies:
        deps_str = ", ".join(requirement.dependencies)
        print(f"Dependencies: {deps_str}")
    
    print(f"Created: {format_timestamp(requirement.created_at)}")
    print(f"Updated: {format_timestamp(requirement.updated_at)}")
    
    if requirement.history:
        print("\nHistory:")
        for entry in requirement.history:
            timestamp = format_timestamp(entry["timestamp"])
            print(f"  {timestamp} - {entry['action']}: {entry['description']}")


def update_requirement(
    requirements_manager: RequirementsManager,
    project_id: str,
    requirement_id: str,
    **kwargs
) -> None:
    """Update a requirement.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
        requirement_id: Requirement ID
        **kwargs: Attributes to update
    """
    # Parse tags if provided
    if "tags" in kwargs and kwargs["tags"]:
        kwargs["tags"] = kwargs["tags"].split(",")
    
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    if not kwargs:
        print("No updates specified")
        return
    
    success = requirements_manager.update_requirement(
        project_id=project_id,
        requirement_id=requirement_id,
        **kwargs
    )
    
    if success:
        print(f"Updated requirement {requirement_id}")
    else:
        print(f"Requirement {requirement_id} not found in project {project_id}")


def delete_requirement(requirements_manager: RequirementsManager, project_id: str, requirement_id: str) -> None:
    """Delete a requirement.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
        requirement_id: Requirement ID
    """
    project = requirements_manager.get_project(project_id)
    
    if not project:
        print(f"Project {project_id} not found")
        return
    
    success = project.delete_requirement(requirement_id)
    
    if success:
        print(f"Deleted requirement {requirement_id}")
        
        # Save the project
        requirements_manager._save_project(project)
    else:
        print(f"Requirement {requirement_id} not found")


# Visualization commands
def visualize_requirements(
    requirements_manager: RequirementsManager,
    project_id: str,
    format: str = "hierarchy",
    output: Optional[str] = None
) -> None:
    """Visualize requirements.
    
    Args:
        requirements_manager: Requirements manager
        project_id: Project ID
        format: Visualization format
        output: Output file
    """
    project = requirements_manager.get_project(project_id)
    
    if not project:
        print(f"Project {project_id} not found")
        return
    
    if format == "hierarchy":
        visualize_hierarchy(project, output)
    elif format == "graph":
        visualize_graph(project, output)
    else:
        print(f"Unknown format: {format}")


# Hermes commands
async def register_with_hermes(requirements_manager: RequirementsManager) -> None:
    """Register with the Hermes service registry.
    
    Args:
        requirements_manager: Requirements manager
    """
    try:
        result = await requirements_manager.register_with_hermes()
        
        if result:
            print("Successfully registered with Hermes service registry")
        else:
            print("Failed to register with Hermes service registry")
    except Exception as e:
        print(f"Error registering with Hermes: {e}")
