"""
Storage implementations for Metis data

This module provides the storage implementations for Metis data,
including in-memory storage and database-backed storage.
"""

import os
from typing import Dict, List, Optional, Any, Tuple, Set
from uuid import uuid4
from datetime import datetime
import json
import threading

from metis.models.task import Task
from metis.models.dependency import Dependency
from metis.models.subtask import Subtask
from metis.models.requirement import RequirementRef
from metis.models.complexity import ComplexityScore


class InMemoryStorage:
    """
    In-memory storage implementation for Metis.
    
    This class provides an in-memory storage solution for tasks and their
    related data. It's useful for development, testing, and deployments
    that don't require persistent storage.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._tasks: Dict[str, Task] = {}
        self._dependencies: Dict[str, Dependency] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
    
    # Task operations
    
    def create_task(self, task: Task) -> Task:
        """
        Create a new task in storage.
        
        Args:
            task: Task to create
            
        Returns:
            Task: Created task with ID assigned
        """
        with self._lock:
            # Ensure task has an ID
            if not task.id:
                task.id = str(uuid4())
            
            # Validate task dependencies
            for dep_id in task.dependencies:
                if dep_id not in self._tasks:
                    raise ValueError(f"Dependency task not found: {dep_id}")
            
            # Store the task
            self._tasks[task.id] = task
            return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """
        Update a task by ID.
        
        Args:
            task_id: ID of the task to update
            updates: Dictionary of field updates
            
        Returns:
            Optional[Task]: Updated task if found, None otherwise
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            
            # Validate dependency updates
            if "dependencies" in updates:
                for dep_id in updates["dependencies"]:
                    if dep_id not in self._tasks:
                        raise ValueError(f"Dependency task not found: {dep_id}")
            
            # Apply updates
            task.update(updates)
            
            # Store updated task
            self._tasks[task_id] = task
            return task
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            bool: True if task was found and deleted, False otherwise
        """
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            # Check if any tasks depend on this one
            for t in self._tasks.values():
                if task_id in t.dependencies:
                    raise ValueError(f"Cannot delete task {task_id} as other tasks depend on it")
            
            # Delete related dependencies
            deps_to_delete = []
            for dep_id, dep in self._dependencies.items():
                if dep.source_task_id == task_id or dep.target_task_id == task_id:
                    deps_to_delete.append(dep_id)
            
            for dep_id in deps_to_delete:
                del self._dependencies[dep_id]
            
            # Delete the task
            del self._tasks[task_id]
            return True
    
    def list_tasks(
        self, 
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Task], int]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            assignee: Filter by assignee
            tag: Filter by tag
            search: Search term for title/description
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Tuple[List[Task], int]: List of tasks and total count
        """
        with self._lock:
            # Start with all tasks
            tasks = list(self._tasks.values())
            
            # Apply filters
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            if priority:
                tasks = [t for t in tasks if t.priority == priority]
            
            if assignee:
                tasks = [t for t in tasks if t.assignee == assignee]
            
            if tag:
                tasks = [t for t in tasks if tag in t.tags]
            
            if search:
                search = search.lower()
                tasks = [
                    t for t in tasks 
                    if search in t.title.lower() or 
                       search in t.description.lower() or
                       (t.details and search in t.details.lower())
                ]
            
            # Get total count
            total = len(tasks)
            
            # Sort by updated_at (newest first)
            tasks.sort(key=lambda t: t.updated_at, reverse=True)
            
            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size
            
            # Return paginated results
            return tasks[start:end], total
    
    # Dependency operations
    
    def create_dependency(self, dependency: Dependency) -> Dependency:
        """
        Create a new dependency in storage.
        
        Args:
            dependency: Dependency to create
            
        Returns:
            Dependency: Created dependency with ID assigned
        """
        with self._lock:
            # Ensure dependency has an ID
            if not dependency.id:
                dependency.id = str(uuid4())
            
            # Validate source and target tasks exist
            if dependency.source_task_id not in self._tasks:
                raise ValueError(f"Source task not found: {dependency.source_task_id}")
            
            if dependency.target_task_id not in self._tasks:
                raise ValueError(f"Target task not found: {dependency.target_task_id}")
            
            # Validate no circular dependencies
            from metis.models.dependency import DependencyManager
            all_deps = list(self._dependencies.values())
            
            if not DependencyManager.validate_new_dependency(
                all_deps, dependency.source_task_id, dependency.target_task_id
            ):
                raise ValueError("This dependency would create a circular reference")
            
            # Store the dependency
            self._dependencies[dependency.id] = dependency
            
            # Update the target task's dependencies
            target_task = self._tasks[dependency.target_task_id]
            if dependency.source_task_id not in target_task.dependencies:
                target_task.dependencies.append(dependency.source_task_id)
                target_task.updated_at = datetime.utcnow()
            
            return dependency
    
    def get_dependency(self, dependency_id: str) -> Optional[Dependency]:
        """
        Get a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to retrieve
            
        Returns:
            Optional[Dependency]: Dependency if found, None otherwise
        """
        with self._lock:
            return self._dependencies.get(dependency_id)
    
    def update_dependency(self, dependency_id: str, updates: Dict[str, Any]) -> Optional[Dependency]:
        """
        Update a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to update
            updates: Dictionary of field updates
            
        Returns:
            Optional[Dependency]: Updated dependency if found, None otherwise
        """
        with self._lock:
            dependency = self._dependencies.get(dependency_id)
            if not dependency:
                return None
            
            # Disallow changing source/target tasks
            if "source_task_id" in updates or "target_task_id" in updates:
                raise ValueError("Cannot change source_task_id or target_task_id of an existing dependency")
            
            # Apply updates
            dependency.update(updates)
            
            # Store updated dependency
            self._dependencies[dependency_id] = dependency
            return dependency
    
    def delete_dependency(self, dependency_id: str) -> bool:
        """
        Delete a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to delete
            
        Returns:
            bool: True if dependency was found and deleted, False otherwise
        """
        with self._lock:
            dependency = self._dependencies.get(dependency_id)
            if not dependency:
                return False
            
            # Remove dependency from target task
            target_task = self._tasks.get(dependency.target_task_id)
            if target_task and dependency.source_task_id in target_task.dependencies:
                target_task.dependencies.remove(dependency.source_task_id)
                target_task.updated_at = datetime.utcnow()
            
            # Delete the dependency
            del self._dependencies[dependency_id]
            return True
    
    def list_dependencies(
        self,
        task_id: Optional[str] = None,
        dependency_type: Optional[str] = None
    ) -> List[Dependency]:
        """
        List dependencies with optional filtering.
        
        Args:
            task_id: Filter by source or target task ID
            dependency_type: Filter by dependency type
            
        Returns:
            List[Dependency]: List of matching dependencies
        """
        with self._lock:
            # Start with all dependencies
            dependencies = list(self._dependencies.values())
            
            # Apply filters
            if task_id:
                dependencies = [
                    d for d in dependencies
                    if d.source_task_id == task_id or d.target_task_id == task_id
                ]
            
            if dependency_type:
                dependencies = [d for d in dependencies if d.dependency_type == dependency_type]
            
            # Sort by updated_at (newest first)
            dependencies.sort(key=lambda d: d.updated_at, reverse=True)
            
            return dependencies
    
    def list_blocking_tasks(self, task_id: str) -> List[Task]:
        """
        List tasks that block a given task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            List[Task]: List of tasks that block the specified task
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return []
            
            return [self._tasks[dep_id] for dep_id in task.dependencies if dep_id in self._tasks]
    
    def list_dependent_tasks(self, task_id: str) -> List[Task]:
        """
        List tasks that depend on a given task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            List[Task]: List of tasks that depend on the specified task
        """
        with self._lock:
            dependent_tasks = []
            
            for task in self._tasks.values():
                if task_id in task.dependencies:
                    dependent_tasks.append(task)
            
            return dependent_tasks
    
    # Persistence operations (for in-memory storage backup/restore)
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save the current state to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                # Convert to JSON-serializable format
                data = {
                    "tasks": {task_id: task.dict() for task_id, task in self._tasks.items()},
                    "dependencies": {dep_id: dep.dict() for dep_id, dep in self._dependencies.items()}
                }
                
                # Write to file
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                return True
            except Exception as e:
                print(f"Error saving to file: {e}")
                return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load state from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._lock:
            try:
                if not os.path.exists(filepath):
                    return False
                
                # Read from file
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Clear current state
                self._tasks.clear()
                self._dependencies.clear()
                
                # Recreate tasks
                for task_id, task_data in data.get("tasks", {}).items():
                    self._tasks[task_id] = Task(**task_data)
                
                # Recreate dependencies
                for dep_id, dep_data in data.get("dependencies", {}).items():
                    self._dependencies[dep_id] = Dependency(**dep_data)
                
                return True
            except Exception as e:
                print(f"Error loading from file: {e}")
                return False