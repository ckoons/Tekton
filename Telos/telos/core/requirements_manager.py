"""Requirements management for Telos.

This module provides tools for managing user requirements and projects.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any

from telos.core.requirement import Requirement
from telos.core.project import Project

logger = logging.getLogger(__name__)


class RequirementsManager:
    """Manager for projects and requirements."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the requirements manager.
        
        Args:
            storage_dir: Optional directory for storing projects
        """
        self.projects: Dict[str, Project] = {}
        self.storage_dir = storage_dir
        
        # Load projects if storage directory is provided
        if storage_dir:
            self.load_projects()
    
    def create_project(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new project.
        
        Args:
            name: Project name
            description: Project description
            metadata: Additional metadata
            
        Returns:
            The project ID
        """
        project = Project(name=name, description=description, metadata=metadata)
        self.projects[project.project_id] = project
        
        # Save the project if storage directory is set
        if self.storage_dir:
            self._save_project(project)
        
        return project.project_id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID.
        
        Args:
            project_id: The project ID
            
        Returns:
            The project or None if not found
        """
        return self.projects.get(project_id)
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects.
        
        Returns:
            List of all projects
        """
        return list(self.projects.values())
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            Success status
        """
        if project_id in self.projects:
            # Delete project file if storage directory is set
            if self.storage_dir:
                self._delete_project_file(project_id)
            
            # Remove from memory
            del self.projects[project_id]
            return True
        
        return False
    
    def add_requirement(
        self,
        project_id: str,
        title: str,
        description: str,
        **kwargs
    ) -> Optional[str]:
        """Add a requirement to a project.
        
        Args:
            project_id: The project ID
            title: Requirement title
            description: Requirement description
            **kwargs: Additional requirement attributes
            
        Returns:
            The requirement ID or None if the project doesn't exist
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        requirement = Requirement(title=title, description=description, **kwargs)
        req_id = project.add_requirement(requirement)
        
        # Save the project if storage directory is set
        if self.storage_dir:
            self._save_project(project)
        
        return req_id
    
    def get_requirement(
        self,
        project_id: str,
        requirement_id: str
    ) -> Optional[Requirement]:
        """Get a requirement from a project.
        
        Args:
            project_id: The project ID
            requirement_id: The requirement ID
            
        Returns:
            The requirement or None if not found
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.get_requirement(requirement_id)
    
    def update_requirement(
        self,
        project_id: str,
        requirement_id: str,
        **kwargs
    ) -> bool:
        """Update a requirement.
        
        Args:
            project_id: The project ID
            requirement_id: The requirement ID
            **kwargs: Attributes to update
            
        Returns:
            Success status
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        success = project.update_requirement(requirement_id, **kwargs)
        
        # Save the project if storage directory is set and update was successful
        if success and self.storage_dir:
            self._save_project(project)
        
        return success
    
    def _save_project(self, project: Project) -> None:
        """Save a project to disk.
        
        Args:
            project: The project to save
        """
        if not self.storage_dir:
            return
        
        os.makedirs(self.storage_dir, exist_ok=True)
        file_path = os.path.join(self.storage_dir, f"{project.project_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(project.to_dict(), f, indent=2)
    
    def _delete_project_file(self, project_id: str) -> None:
        """Delete a project file.
        
        Args:
            project_id: The project ID
        """
        if not self.storage_dir:
            return
        
        file_path = os.path.join(self.storage_dir, f"{project_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def load_projects(self) -> None:
        """Load all projects from the storage directory."""
        if not self.storage_dir or not os.path.exists(self.storage_dir):
            logger.warning(f"Storage directory {self.storage_dir} does not exist")
            return
        
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.storage_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                project = Project.from_dict(data)
                self.projects[project.project_id] = project
                logger.info(f"Loaded project {project.project_id}: {project.name}")
            except Exception as e:
                logger.error(f"Error loading project from {file_path}: {e}")
    
    async def register_with_hermes(self, service_registry=None) -> bool:
        """Register the requirements manager with the Hermes service registry.
        
        Args:
            service_registry: Optional service registry instance
            
        Returns:
            Success status
        """
        try:
            # Try to import the service registry if not provided
            if service_registry is None:
                try:
                    from hermes.core.service_discovery import ServiceRegistry
                    service_registry = ServiceRegistry()
                    await service_registry.start()
                except ImportError:
                    logger.error("Could not import Hermes ServiceRegistry")
                    return False
            
            # Register the requirements service
            success = await service_registry.register(
                service_id="telos-requirements",
                name="Telos Requirements Manager",
                version="0.1.0",
                capabilities=["requirements_management", "project_management"],
                metadata={
                    "projects": len(self.projects),
                    "requirements": sum(len(p.requirements) for p in self.projects.values())
                }
            )
            
            if success:
                logger.info("Registered requirements manager with Hermes")
            else:
                logger.warning("Failed to register requirements manager")
            
            return success
        
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False