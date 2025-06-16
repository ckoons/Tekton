"""
Task manager for Metis

This module defines the TaskManager class, which provides the core business
logic for managing tasks in the Metis system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from uuid import uuid4
import asyncio
import os

from metis.models.task import Task
from metis.models.enums import TaskStatus, Priority
from metis.models.dependency import Dependency, DependencyManager
from metis.models.subtask import Subtask
from metis.models.complexity import ComplexityScore
from metis.models.requirement import RequirementRef
from metis.core.storage import InMemoryStorage

# Import these modules lazily to avoid circular imports
# They'll be imported when the methods that use them are called
# from metis.core.telos_integration import telos_client


class TaskManager:
    """
    Task Manager for Metis.
    
    This class provides the core business logic for managing tasks in Metis,
    including CRUD operations, dependency management, and task querying.
    """
    
    def __init__(self, storage: Optional[Any] = None):
        """
        Initialize the TaskManager.
        
        Args:
            storage: Optional storage implementation (defaults to InMemoryStorage)
        """
        self.storage = storage or InMemoryStorage()
        self._event_handlers = {}
        
        # Load from backup file if exists
        backup_path = os.environ.get("METIS_BACKUP_PATH", "metis_data.json")
        if os.path.exists(backup_path):
            self.storage.load_from_file(backup_path)
    
    # Task operations
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Create a new task.
        
        Args:
            task_data: Dictionary of task data
            
        Returns:
            Task: Created task
            
        Raises:
            ValueError: If task data is invalid
        """
        # Create Task instance
        task = Task(**task_data)
        
        # Save to storage
        created_task = self.storage.create_task(task)
        
        # Fire event
        await self._fire_event("task_created", created_task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return created_task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        return self.storage.get_task(task_id)
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """
        Update a task by ID.
        
        Args:
            task_id: ID of the task to update
            updates: Dictionary of field updates
            
        Returns:
            Optional[Task]: Updated task if found, None otherwise
            
        Raises:
            ValueError: If updates are invalid
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Apply updates
        updated_task = self.storage.update_task(task_id, updates)
        
        # Fire event
        await self._fire_event("task_updated", updated_task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return updated_task
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by ID.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            bool: True if task was deleted, False if not found
            
        Raises:
            ValueError: If task cannot be deleted due to dependencies
        """
        task = await self.get_task(task_id)
        if not task:
            return False
        
        # Delete from storage
        deleted = self.storage.delete_task(task_id)
        
        if deleted:
            # Fire event
            await self._fire_event("task_deleted", {"id": task_id})
            
            # Auto-save if backup path is set
            await self._auto_save()
        
        return deleted
    
    async def list_tasks(
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
        return self.storage.list_tasks(
            status=status,
            priority=priority,
            assignee=assignee,
            tag=tag,
            search=search,
            page=page,
            page_size=page_size
        )
    
    # Subtask operations
    
    async def add_subtask(self, task_id: str, subtask_data: Dict[str, Any]) -> Optional[Subtask]:
        """
        Add a subtask to a task.
        
        Args:
            task_id: ID of the parent task
            subtask_data: Dictionary of subtask data
            
        Returns:
            Optional[Subtask]: Created subtask if parent task exists, None otherwise
            
        Raises:
            ValueError: If subtask data is invalid
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Create subtask
        subtask = Subtask(**subtask_data)
        
        # Add to task
        task.add_subtask(subtask)
        
        # Update in storage
        self.storage.update_task(task_id, {"subtasks": task.subtasks})
        
        # Fire event
        await self._fire_event("task_updated", task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return subtask
    
    async def update_subtask(
        self, task_id: str, subtask_id: str, updates: Dict[str, Any]
    ) -> Optional[Subtask]:
        """
        Update a subtask.
        
        Args:
            task_id: ID of the parent task
            subtask_id: ID of the subtask to update
            updates: Dictionary of field updates
            
        Returns:
            Optional[Subtask]: Updated subtask if found, None otherwise
            
        Raises:
            ValueError: If updates are invalid
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Update subtask
        success = task.update_subtask(subtask_id, updates)
        if not success:
            return None
        
        # Find the updated subtask
        subtask = next((s for s in task.subtasks if s.id == subtask_id), None)
        
        # Update in storage
        self.storage.update_task(task_id, {"subtasks": task.subtasks})
        
        # Fire event
        await self._fire_event("task_updated", task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return subtask
    
    async def remove_subtask(self, task_id: str, subtask_id: str) -> bool:
        """
        Remove a subtask from a task.
        
        Args:
            task_id: ID of the parent task
            subtask_id: ID of the subtask to remove
            
        Returns:
            bool: True if subtask was removed, False if not found
        """
        task = await self.get_task(task_id)
        if not task:
            return False
        
        # Remove subtask
        success = task.remove_subtask(subtask_id)
        if not success:
            return False
        
        # Update in storage
        self.storage.update_task(task_id, {"subtasks": task.subtasks})
        
        # Fire event
        await self._fire_event("task_updated", task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return True
    
    # Requirement reference operations
    
    async def add_requirement_ref(
        self, task_id: str, req_ref_data: Dict[str, Any]
    ) -> Optional[RequirementRef]:
        """
        Add a requirement reference to a task.
        
        Args:
            task_id: ID of the task
            req_ref_data: Dictionary of requirement reference data
            
        Returns:
            Optional[RequirementRef]: Created reference if task exists, None otherwise
            
        Raises:
            ValueError: If reference data is invalid
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Create requirement reference
        req_ref = RequirementRef(**req_ref_data)
        
        # Add to task
        task.add_requirement_ref(req_ref)
        
        # Update in storage
        self.storage.update_task(task_id, {"requirement_refs": task.requirement_refs})
        
        # Fire event
        await self._fire_event("task_updated", task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return req_ref
    
    async def update_requirement_ref(
        self, task_id: str, ref_id: str, updates: Dict[str, Any]
    ) -> Optional[RequirementRef]:
        """
        Update a requirement reference.
        
        Args:
            task_id: ID of the task
            ref_id: ID of the requirement reference to update
            updates: Dictionary of field updates
            
        Returns:
            Optional[RequirementRef]: Updated reference if found, None otherwise
            
        Raises:
            ValueError: If updates are invalid
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Update requirement reference
        success = task.update_requirement_ref(ref_id, updates)
        if not success:
            return None
        
        # Find the updated reference
        ref = next((r for r in task.requirement_refs if r.id == ref_id), None)
        
        # Update in storage
        self.storage.update_task(task_id, {"requirement_refs": task.requirement_refs})
        
        # Fire event
        await self._fire_event("task_updated", task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return ref
    
    async def remove_requirement_ref(self, task_id: str, ref_id: str) -> bool:
        """
        Remove a requirement reference from a task.
        
        Args:
            task_id: ID of the task
            ref_id: ID of the requirement reference to remove
            
        Returns:
            bool: True if reference was removed, False if not found
        """
        task = await self.get_task(task_id)
        if not task:
            return False
        
        # Remove requirement reference
        success = task.remove_requirement_ref(ref_id)
        if not success:
            return False
        
        # Update in storage
        self.storage.update_task(task_id, {"requirement_refs": task.requirement_refs})
        
        # Fire event
        await self._fire_event("task_updated", task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return True
    
    # Dependency operations
    
    async def create_dependency(self, dependency_data: Dict[str, Any]) -> Dependency:
        """
        Create a new dependency between tasks.
        
        Args:
            dependency_data: Dictionary of dependency data
            
        Returns:
            Dependency: Created dependency
            
        Raises:
            ValueError: If dependency data is invalid or would create a cycle
        """
        # Create Dependency instance
        dependency = Dependency(**dependency_data)
        
        # Save to storage
        created_dependency = self.storage.create_dependency(dependency)
        
        # Fire event for both tasks
        source_task = await self.get_task(dependency.source_task_id)
        target_task = await self.get_task(dependency.target_task_id)
        
        if source_task:
            await self._fire_event("task_updated", source_task)
        
        if target_task:
            await self._fire_event("task_updated", target_task)
        
        # Auto-save if backup path is set
        await self._auto_save()
        
        return created_dependency
    
    async def get_dependency(self, dependency_id: str) -> Optional[Dependency]:
        """
        Get a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to retrieve
            
        Returns:
            Optional[Dependency]: Dependency if found, None otherwise
        """
        return self.storage.get_dependency(dependency_id)
    
    async def update_dependency(
        self, dependency_id: str, updates: Dict[str, Any]
    ) -> Optional[Dependency]:
        """
        Update a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to update
            updates: Dictionary of field updates
            
        Returns:
            Optional[Dependency]: Updated dependency if found, None otherwise
            
        Raises:
            ValueError: If updates are invalid
        """
        # Update in storage
        updated_dependency = self.storage.update_dependency(dependency_id, updates)
        
        if updated_dependency:
            # Fire event for both tasks
            source_task = await self.get_task(updated_dependency.source_task_id)
            target_task = await self.get_task(updated_dependency.target_task_id)
            
            if source_task:
                await self._fire_event("task_updated", source_task)
            
            if target_task:
                await self._fire_event("task_updated", target_task)
            
            # Auto-save if backup path is set
            await self._auto_save()
        
        return updated_dependency
    
    async def delete_dependency(self, dependency_id: str) -> bool:
        """
        Delete a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to delete
            
        Returns:
            bool: True if dependency was deleted, False if not found
        """
        # Get dependency before deletion for event firing
        dependency = await self.get_dependency(dependency_id)
        if not dependency:
            return False
        
        # Delete from storage
        deleted = self.storage.delete_dependency(dependency_id)
        
        if deleted:
            # Fire event for both tasks
            source_task = await self.get_task(dependency.source_task_id)
            target_task = await self.get_task(dependency.target_task_id)
            
            if source_task:
                await self._fire_event("task_updated", source_task)
            
            if target_task:
                await self._fire_event("task_updated", target_task)
            
            # Auto-save if backup path is set
            await self._auto_save()
        
        return deleted
    
    async def list_dependencies(
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
        return self.storage.list_dependencies(
            task_id=task_id,
            dependency_type=dependency_type
        )
    
    async def list_blocking_tasks(self, task_id: str) -> List[Task]:
        """
        List tasks that block a given task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            List[Task]: List of tasks that block the specified task
        """
        return self.storage.list_blocking_tasks(task_id)
    
    async def list_dependent_tasks(self, task_id: str) -> List[Task]:
        """
        List tasks that depend on a given task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            List[Task]: List of tasks that depend on the specified task
        """
        return self.storage.list_dependent_tasks(task_id)
    
    # Bulk operations
    
    async def bulk_create_tasks(self, tasks_data: List[Dict[str, Any]]) -> List[Task]:
        """
        Create multiple tasks in a batch.
        
        Args:
            tasks_data: List of task data dictionaries
            
        Returns:
            List[Task]: List of created tasks
            
        Raises:
            ValueError: If any task data is invalid
        """
        created_tasks = []
        
        for task_data in tasks_data:
            task = await self.create_task(task_data)
            created_tasks.append(task)
        
        return created_tasks
    
    async def bulk_update_tasks(
        self, updates_map: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Optional[Task]]:
        """
        Update multiple tasks in a batch.
        
        Args:
            updates_map: Dictionary mapping task IDs to update dictionaries
            
        Returns:
            Dict[str, Optional[Task]]: Dictionary mapping task IDs to updated tasks
            
        Raises:
            ValueError: If any updates are invalid
        """
        results = {}
        
        for task_id, updates in updates_map.items():
            task = await self.update_task(task_id, updates)
            results[task_id] = task
        
        return results
    
    # Event handling
    
    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Callback function to handle the event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
    
    def unregister_event_handler(self, event_type: str, handler: callable) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler to unregister
            
        Returns:
            bool: True if handler was found and removed, False otherwise
        """
        if event_type not in self._event_handlers:
            return False
        
        try:
            self._event_handlers[event_type].remove(handler)
            return True
        except ValueError:
            return False
    
    async def _fire_event(self, event_type: str, data: Any) -> None:
        """
        Fire an event to all registered handlers.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type not in self._event_handlers:
            return
        
        # Call all handlers
        for handler in self._event_handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, data)
                else:
                    handler(event_type, data)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    # Persistence
    
    async def save(self, filepath: str) -> bool:
        """
        Save the current state to a file.
        
        Args:
            filepath: Path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.storage.save_to_file(filepath)
    
    async def load(self, filepath: str) -> bool:
        """
        Load state from a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.storage.load_from_file(filepath)
    
    async def _auto_save(self) -> None:
        """Auto-save if backup path is set."""
        backup_path = os.environ.get("METIS_BACKUP_PATH")
        if backup_path:
            self.storage.save_to_file(backup_path)
    
    # Telos integration
    
    async def import_requirement(self, requirement_id: str, task_id: Optional[str] = None) -> Tuple[Optional[RequirementRef], Optional[Task]]:
        """
        Import a requirement from Telos as a requirement reference.
        
        Args:
            requirement_id: ID of the requirement to import
            task_id: Optional task ID to add the reference to
            
        Returns:
            Tuple[Optional[RequirementRef], Optional[Task]]: 
                Created reference and task if successful, None otherwise
        """
        from metis.core.telos_integration import telos_client
        
        # Get requirement reference from Telos
        req_ref = await telos_client.create_requirement_reference(requirement_id)
        if not req_ref:
            return None, None
        
        # If task_id provided, add reference to task
        if task_id:
            task = await self.get_task(task_id)
            if not task:
                return req_ref, None
            
            # Add reference to task
            await self.add_requirement_ref(task_id, req_ref.dict())
            
            # Get updated task
            task = await self.get_task(task_id)
            return req_ref, task
        
        return req_ref, None
    
    async def import_requirement_as_task(self, requirement_id: str) -> Optional[Task]:
        """
        Import a requirement from Telos as a new task.
        
        Args:
            requirement_id: ID of the requirement to import
            
        Returns:
            Optional[Task]: Created task if successful, None otherwise
        """
        from metis.core.telos_integration import telos_client
        
        # Get requirement data from Telos
        requirement = await telos_client.get_requirement(requirement_id)
        if not requirement:
            return None
        
        # Create task from requirement
        task_data = {
            "title": requirement.get("title", "Untitled Requirement"),
            "description": requirement.get("description", ""),
            "status": TaskStatus.PENDING.value,
            "priority": Priority.MEDIUM.value,
            "tags": ["telos", "requirement", requirement.get("type", "unknown")]
        }
        
        # Create task
        task = await self.create_task(task_data)
        
        # Create and add requirement reference
        req_ref = await telos_client.create_requirement_reference(requirement_id)
        if req_ref:
            await self.add_requirement_ref(task.id, req_ref.dict())
            
            # Get updated task
            task = await self.get_task(task.id)
        
        return task
    
    async def search_telos_requirements(
        self, 
        query: str = None, 
        status: str = None,
        category: str = None,
        page: int = 1, 
        page_size: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search for requirements in Telos.
        
        Args:
            query: Search query
            status: Filter by status
            category: Filter by category
            page: Page number
            page_size: Page size
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: List of requirements and total count
        """
        from metis.core.telos_integration import telos_client
        
        return await telos_client.search_requirements(
            query=query,
            status=status,
            category=category,
            page=page,
            page_size=page_size
        )