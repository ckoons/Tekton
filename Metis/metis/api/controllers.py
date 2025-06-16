"""
API controllers for Metis

This module provides the controller layer for the Metis API, handling
the business logic between API routes and the task manager.
"""

from typing import Dict, List, Optional, Any, Tuple, Set, Union
from fastapi import HTTPException, Depends, Query, Path, Body, status

from metis.core.task_manager import TaskManager
from metis.models.task import Task
from metis.models.dependency import Dependency
from metis.models.subtask import Subtask
from metis.models.requirement import RequirementRef
from metis.api.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskDetailResponse, DependencyCreate, DependencyUpdate,
    DependencyResponse, DependencyListResponse, SubtaskCreate,
    SubtaskUpdate, RequirementRefCreate, RequirementRefUpdate,
    ApiResponse
)


class TaskController:
    """
    Controller for task-related API endpoints.
    
    This class provides methods for handling task-related API requests,
    translating between API schemas and core models, and delegating to
    the TaskManager for business logic.
    """
    
    def __init__(self, task_manager: TaskManager):
        """
        Initialize the TaskController.
        
        Args:
            task_manager: TaskManager instance for business logic
        """
        self.task_manager = task_manager
    
    # Task endpoints
    
    async def create_task(self, task_create: TaskCreate) -> TaskResponse:
        """
        Create a new task.
        
        Args:
            task_create: Task creation schema
            
        Returns:
            TaskResponse: Created task
            
        Raises:
            HTTPException: If task creation fails
        """
        try:
            # Convert to Task model
            task_data = task_create.dict()
            
            # Create task
            task = await self.task_manager.create_task(task_data)
            
            # Convert to response schema
            return self._task_to_response(task)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create task: {str(e)}"
            )
    
    async def get_task(self, task_id: str) -> TaskDetailResponse:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            TaskDetailResponse: Task detail response
            
        Raises:
            HTTPException: If task is not found
        """
        task = await self.task_manager.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task not found: {task_id}"
            )
        
        # Convert to response schema
        return TaskDetailResponse(
            success=True,
            task=self._task_to_response(task)
        )
    
    async def update_task(self, task_id: str, task_update: TaskUpdate) -> TaskResponse:
        """
        Update a task by ID.
        
        Args:
            task_id: ID of the task to update
            task_update: Task update schema
            
        Returns:
            TaskResponse: Updated task
            
        Raises:
            HTTPException: If task is not found or update fails
        """
        try:
            # Convert to dictionary, excluding None values
            update_data = {k: v for k, v in task_update.dict().items() if v is not None}
            
            # Update task
            task = await self.task_manager.update_task(task_id, update_data)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task not found: {task_id}"
                )
            
            # Convert to response schema
            return self._task_to_response(task)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update task: {str(e)}"
            )
    
    async def delete_task(self, task_id: str) -> ApiResponse:
        """
        Delete a task by ID.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            ApiResponse: Success response
            
        Raises:
            HTTPException: If task is not found or delete fails
        """
        try:
            deleted = await self.task_manager.delete_task(task_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task not found: {task_id}"
                )
            
            return ApiResponse(
                success=True,
                message=f"Task {task_id} deleted successfully"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete task: {str(e)}"
            )
    
    async def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> TaskListResponse:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            assignee: Filter by assignee
            tag: Filter by tag
            search: Search term for title/description
            page: Page number
            page_size: Page size
            
        Returns:
            TaskListResponse: List of tasks and metadata
        """
        try:
            # Get tasks from manager
            tasks, total = await self.task_manager.list_tasks(
                status=status,
                priority=priority,
                assignee=assignee,
                tag=tag,
                search=search,
                page=page,
                page_size=page_size
            )
            
            # Convert to response schema
            task_responses = [self._task_to_response(task) for task in tasks]
            
            return TaskListResponse(
                success=True,
                tasks=task_responses,
                total=total,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list tasks: {str(e)}"
            )
    
    # Subtask endpoints
    
    async def add_subtask(self, task_id: str, subtask_create: SubtaskCreate) -> TaskResponse:
        """
        Add a subtask to a task.
        
        Args:
            task_id: ID of the parent task
            subtask_create: Subtask creation schema
            
        Returns:
            TaskResponse: Updated task with new subtask
            
        Raises:
            HTTPException: If task is not found or subtask creation fails
        """
        try:
            # Convert to dictionary
            subtask_data = subtask_create.dict()
            
            # Add subtask
            subtask = await self.task_manager.add_subtask(task_id, subtask_data)
            if not subtask:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task not found: {task_id}"
                )
            
            # Get updated task
            task = await self.task_manager.get_task(task_id)
            
            # Convert to response schema
            return self._task_to_response(task)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add subtask: {str(e)}"
            )
    
    async def update_subtask(
        self, task_id: str, subtask_id: str, subtask_update: SubtaskUpdate
    ) -> TaskResponse:
        """
        Update a subtask.
        
        Args:
            task_id: ID of the parent task
            subtask_id: ID of the subtask to update
            subtask_update: Subtask update schema
            
        Returns:
            TaskResponse: Updated task
            
        Raises:
            HTTPException: If task or subtask is not found or update fails
        """
        try:
            # Convert to dictionary, excluding None values
            update_data = {k: v for k, v in subtask_update.dict().items() if v is not None}
            
            # Update subtask
            subtask = await self.task_manager.update_subtask(task_id, subtask_id, update_data)
            if not subtask:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Subtask not found: {subtask_id}"
                )
            
            # Get updated task
            task = await self.task_manager.get_task(task_id)
            
            # Convert to response schema
            return self._task_to_response(task)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update subtask: {str(e)}"
            )
    
    async def remove_subtask(self, task_id: str, subtask_id: str) -> TaskResponse:
        """
        Remove a subtask from a task.
        
        Args:
            task_id: ID of the parent task
            subtask_id: ID of the subtask to remove
            
        Returns:
            TaskResponse: Updated task
            
        Raises:
            HTTPException: If task or subtask is not found or removal fails
        """
        try:
            # Remove subtask
            removed = await self.task_manager.remove_subtask(task_id, subtask_id)
            if not removed:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Subtask not found: {subtask_id}"
                )
            
            # Get updated task
            task = await self.task_manager.get_task(task_id)
            
            # Convert to response schema
            return self._task_to_response(task)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove subtask: {str(e)}"
            )
    
    # Requirement reference endpoints
    
    async def add_requirement_ref(
        self, task_id: str, req_ref_create: RequirementRefCreate
    ) -> TaskResponse:
        """
        Add a requirement reference to a task.
        
        Args:
            task_id: ID of the task
            req_ref_create: Requirement reference creation schema
            
        Returns:
            TaskResponse: Updated task with new requirement reference
            
        Raises:
            HTTPException: If task is not found or reference creation fails
        """
        try:
            # Convert to dictionary
            req_ref_data = req_ref_create.dict()
            
            # Add requirement reference
            req_ref = await self.task_manager.add_requirement_ref(task_id, req_ref_data)
            if not req_ref:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task not found: {task_id}"
                )
            
            # Get updated task
            task = await self.task_manager.get_task(task_id)
            
            # Convert to response schema
            return self._task_to_response(task)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add requirement reference: {str(e)}"
            )
    
    async def update_requirement_ref(
        self, task_id: str, ref_id: str, req_ref_update: RequirementRefUpdate
    ) -> TaskResponse:
        """
        Update a requirement reference.
        
        Args:
            task_id: ID of the task
            ref_id: ID of the requirement reference to update
            req_ref_update: Requirement reference update schema
            
        Returns:
            TaskResponse: Updated task
            
        Raises:
            HTTPException: If task or reference is not found or update fails
        """
        try:
            # Convert to dictionary, excluding None values
            update_data = {k: v for k, v in req_ref_update.dict().items() if v is not None}
            
            # Update requirement reference
            req_ref = await self.task_manager.update_requirement_ref(task_id, ref_id, update_data)
            if not req_ref:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Requirement reference not found: {ref_id}"
                )
            
            # Get updated task
            task = await self.task_manager.get_task(task_id)
            
            # Convert to response schema
            return self._task_to_response(task)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update requirement reference: {str(e)}"
            )
    
    async def remove_requirement_ref(self, task_id: str, ref_id: str) -> TaskResponse:
        """
        Remove a requirement reference from a task.
        
        Args:
            task_id: ID of the task
            ref_id: ID of the requirement reference to remove
            
        Returns:
            TaskResponse: Updated task
            
        Raises:
            HTTPException: If task or reference is not found or removal fails
        """
        try:
            # Remove requirement reference
            removed = await self.task_manager.remove_requirement_ref(task_id, ref_id)
            if not removed:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Requirement reference not found: {ref_id}"
                )
            
            # Get updated task
            task = await self.task_manager.get_task(task_id)
            
            # Convert to response schema
            return self._task_to_response(task)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove requirement reference: {str(e)}"
            )
    
    # Dependency endpoints
    
    async def create_dependency(self, dependency_create: DependencyCreate) -> DependencyResponse:
        """
        Create a new dependency between tasks.
        
        Args:
            dependency_create: Dependency creation schema
            
        Returns:
            DependencyResponse: Created dependency
            
        Raises:
            HTTPException: If dependency creation fails
        """
        try:
            # Convert to dictionary
            dependency_data = dependency_create.dict()
            
            # Create dependency
            dependency = await self.task_manager.create_dependency(dependency_data)
            
            # Convert to response schema
            return self._dependency_to_response(dependency)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create dependency: {str(e)}"
            )
    
    async def get_dependency(self, dependency_id: str) -> DependencyResponse:
        """
        Get a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to retrieve
            
        Returns:
            DependencyResponse: Dependency response
            
        Raises:
            HTTPException: If dependency is not found
        """
        dependency = await self.task_manager.get_dependency(dependency_id)
        if not dependency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dependency not found: {dependency_id}"
            )
        
        # Convert to response schema
        return self._dependency_to_response(dependency)
    
    async def update_dependency(
        self, dependency_id: str, dependency_update: DependencyUpdate
    ) -> DependencyResponse:
        """
        Update a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to update
            dependency_update: Dependency update schema
            
        Returns:
            DependencyResponse: Updated dependency
            
        Raises:
            HTTPException: If dependency is not found or update fails
        """
        try:
            # Convert to dictionary, excluding None values
            update_data = {k: v for k, v in dependency_update.dict().items() if v is not None}
            
            # Update dependency
            dependency = await self.task_manager.update_dependency(dependency_id, update_data)
            if not dependency:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dependency not found: {dependency_id}"
                )
            
            # Convert to response schema
            return self._dependency_to_response(dependency)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update dependency: {str(e)}"
            )
    
    async def delete_dependency(self, dependency_id: str) -> ApiResponse:
        """
        Delete a dependency by ID.
        
        Args:
            dependency_id: ID of the dependency to delete
            
        Returns:
            ApiResponse: Success response
            
        Raises:
            HTTPException: If dependency is not found or delete fails
        """
        try:
            deleted = await self.task_manager.delete_dependency(dependency_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dependency not found: {dependency_id}"
                )
            
            return ApiResponse(
                success=True,
                message=f"Dependency {dependency_id} deleted successfully"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete dependency: {str(e)}"
            )
    
    async def list_dependencies(
        self,
        task_id: Optional[str] = None,
        dependency_type: Optional[str] = None
    ) -> DependencyListResponse:
        """
        List dependencies with optional filtering.
        
        Args:
            task_id: Filter by source or target task ID
            dependency_type: Filter by dependency type
            
        Returns:
            DependencyListResponse: List of dependencies
        """
        try:
            # Get dependencies from manager
            dependencies = await self.task_manager.list_dependencies(
                task_id=task_id,
                dependency_type=dependency_type
            )
            
            # Convert to response schema
            dependency_responses = [
                self._dependency_to_response(dependency) 
                for dependency in dependencies
            ]
            
            return DependencyListResponse(
                success=True,
                dependencies=dependency_responses
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list dependencies: {str(e)}"
            )
    
    # Conversion methods
    
    def _task_to_response(self, task: Task) -> TaskResponse:
        """
        Convert a Task model to a TaskResponse schema.
        
        Args:
            task: Task model
            
        Returns:
            TaskResponse: Task response schema
        """
        # Handle nested objects
        from metis.api.schemas import SubtaskResponse, RequirementRefResponse, ComplexityScoreResponse
        
        # Convert subtasks
        subtask_responses = []
        for subtask in task.subtasks:
            subtask_responses.append(SubtaskResponse(
                id=subtask.id,
                title=subtask.title,
                description=subtask.description,
                status=subtask.status,
                order=subtask.order,
                created_at=subtask.created_at,
                updated_at=subtask.updated_at
            ))
        
        # Convert requirement references
        req_ref_responses = []
        for req_ref in task.requirement_refs:
            req_ref_responses.append(RequirementRefResponse(
                id=req_ref.id,
                requirement_id=req_ref.requirement_id,
                source=req_ref.source,
                requirement_type=req_ref.requirement_type,
                title=req_ref.title,
                relationship=req_ref.relationship,
                description=req_ref.description,
                created_at=req_ref.created_at,
                updated_at=req_ref.updated_at
            ))
        
        # Convert complexity if present
        complexity_response = None
        if task.complexity:
            from metis.api.schemas import ComplexityFactorResponse
            
            # Convert complexity factors
            factor_responses = []
            for factor in task.complexity.factors:
                factor_responses.append(ComplexityFactorResponse(
                    id=factor.id,
                    name=factor.name,
                    description=factor.description,
                    weight=factor.weight,
                    score=factor.score,
                    notes=factor.notes
                ))
            
            complexity_response = ComplexityScoreResponse(
                id=task.complexity.id,
                factors=factor_responses,
                overall_score=task.complexity.overall_score,
                level=task.complexity.level,
                created_at=task.complexity.created_at,
                updated_at=task.complexity.updated_at
            )
        
        # Calculate progress
        progress = task.get_progress()
        
        # Create response
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            details=task.details,
            test_strategy=task.test_strategy,
            dependencies=task.dependencies,
            tags=task.tags,
            assignee=task.assignee,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            subtasks=subtask_responses,
            requirement_refs=req_ref_responses,
            complexity=complexity_response,
            progress=progress
        )
    
    def _dependency_to_response(self, dependency: Dependency) -> DependencyResponse:
        """
        Convert a Dependency model to a DependencyResponse schema.
        
        Args:
            dependency: Dependency model
            
        Returns:
            DependencyResponse: Dependency response schema
        """
        return DependencyResponse(
            id=dependency.id,
            source_task_id=dependency.source_task_id,
            target_task_id=dependency.target_task_id,
            dependency_type=dependency.dependency_type,
            description=dependency.description,
            created_at=dependency.created_at,
            updated_at=dependency.updated_at
        )